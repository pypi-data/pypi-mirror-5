# coding: utf-8
#
# Copyright (c) Alexandr Emelin. BSD license.
# All rights reserved.
#
import os
import sys
import json
import logging
import functools
import tornado
import tornado.web
import tornado.httpserver
import tornado.ioloop
import tornado.options
from tornado.options import define, options
from sockjs.tornado import SockJSRouter

from centrifuge import utils

import centrifuge.rpc
import centrifuge.handlers
import centrifuge.web.handlers

from centrifuge.handlers import RpcHandler
from centrifuge.handlers import SockjsConnection
from centrifuge.handlers import WebsocketConnection

from centrifuge.web.handlers import MainHandler
from centrifuge.web.handlers import AuthHandler
from centrifuge.web.handlers import GoogleAuthHandler
from centrifuge.web.handlers import LogoutHandler
from centrifuge.web.handlers import AdminSocketHandler
from centrifuge.web.handlers import Http404Handler
from centrifuge.web.handlers import ProjectCreateHandler
from centrifuge.web.handlers import ProjectSettingsHandler

from centrifuge.rpc import create_control_channel_name
from centrifuge.rpc import handle_control_message

import zmq
from zmq.eventloop import ioloop
from zmq.eventloop.zmqstream import ZMQStream


# Install ZMQ ioloop instead of a tornado ioloop
# http://zeromq.github.com/pyzmq/eventloop.html
ioloop.install()


define(
    "port", default=8000, help="app port", type=int
)

define(
    "zmq_pub_listen", default="127.0.0.1", help="zmq pub listen", type=str
)

define(
    "zmq_pub_port", default=7000, help="zmq pub port", type=int
)

define(
    "zmq_pub_port_shift", default=None, type=int,
    help="zmq port shift with respect to tornado port (useful "
         "when deploying with supervisor on one machine)"
)

define(
    "zmq_sub_address", default=["tcp://localhost:7000"], type=str, multiple=True,
    help="comma-separated list of all ZeroMQ PUB socket addresses"
)

define(
    "zmq_pub_sub_proxy", default=False, type=bool, help="use XPUB/XSUB proxy"
)

define(
    "zmq_xsub", default="tcp://localhost:6000", type=str,
    help="XSUB socket address"
)

define(
    "zmq_xpub", default="tcp://localhost:6001", type=str,
    help="XPUB socket address"
)

define(
    "config", default='config.json', help="JSON config file", type=str
)


def stop_running(msg):
    """
    Called only during initialization when critical error occurred.
    """
    logging.error(msg)
    sys.exit(1)


class Application(tornado.web.Application):

    def __init__(self, settings):

        handlers = [
            tornado.web.url(
                r'/', MainHandler, name="main"
            ),
            tornado.web.url(
                r'/connection/websocket',
                WebsocketConnection,
                name="connection_websocket"
            ),
            tornado.web.url(
                r'/project/create$',
                ProjectCreateHandler,
                name="project_create"
            ),
            tornado.web.url(
                r'/project/([^/]+)/settings/([^/]+)$',
                ProjectSettingsHandler,
                name="project_settings"
            ),
            tornado.web.url(
                r'/rpc/([^/]+)$', RpcHandler, name="store"
            ),
            tornado.web.url(
                r'/auth$', AuthHandler, name="auth"
            ),
            tornado.web.url(
                r'/auth/google$', GoogleAuthHandler, name="auth_google"
            ),
            tornado.web.url(
                r'/logout$', LogoutHandler, name="logout"
            ),
            tornado.web.url(
                r'.*', Http404Handler, name='http404'
            )
        ]

        AdminSocketRouter = SockJSRouter(AdminSocketHandler, '/socket')
        handlers = AdminSocketRouter.urls + handlers

        SockjsConnectionRouter = SockJSRouter(
            SockjsConnection, '/connection/sockjs'
        )
        handlers = SockjsConnectionRouter.urls + handlers

        AdminSocketHandler.application = self
        SockjsConnection.application = self

        tornado.web.Application.__init__(
            self,
            handlers,
            **settings
        )


def main():

    tornado.options.parse_command_line()

    try:
        custom_settings = json.load(open(options.config, 'r'))
    except IOError:
        custom_settings = {}

    database_settings = custom_settings.get('database', {})

    # detect and apply database api module
    api_backend = utils.import_module(
        database_settings.get('api', 'centrifuge.api')
    )
    centrifuge.handlers.api = api_backend
    centrifuge.web.handlers.api = api_backend
    centrifuge.rpc.api = api_backend

    try:
        backend_db = api_backend.prepare_db_backend(
            database_settings.get('settings', {})
        )
    except Exception as e:
        return stop_running(str(e))

    settings = dict(
        cookie_secret=custom_settings.get("cookie_secret", "bad secret"),
        login_url="/auth",
        template_path=os.path.join(
            os.path.dirname(__file__),
            os.path.join("web/frontend", "templates")
        ),
        static_path=os.path.join(
            os.path.dirname(__file__),
            os.path.join("web/frontend", "static")
        ),
        xsrf_cookies=True,
        autoescape="xhtml_escape",
        debug=custom_settings.get('debug', False),
        db=backend_db,
        options=custom_settings
    )

    try:
        app = Application(settings)
        server = tornado.httpserver.HTTPServer(app)
        server.listen(options.port)
        ioloop_instance = tornado.ioloop.IOLoop.instance()
    except Exception as e:
        return stop_running(str(e))

    app.zmq_pub_sub_proxy = options.zmq_pub_sub_proxy

    context = zmq.Context()

    # create PUB socket to publish instance events into it
    publish_socket = context.socket(zmq.PUB)

    if app.zmq_pub_sub_proxy:
        # application started with XPUB/XSUB proxy
        app.zmq_xsub = options.zmq_xsub
        publish_socket.connect(app.zmq_xsub)
    else:
        # application started without XPUB/XSUB proxy
        if options.zmq_pub_port_shift:
            # calculate zmq pub port number
            zmq_pub_port = options.port + options.zmq_pub_port_shift
        else:
            zmq_pub_port = options.zmq_pub_port

        app.zmq_pub_port = zmq_pub_port

        publish_socket.bind(
            "tcp://%s:%s" % (options.zmq_pub_listen, str(app.zmq_pub_port))
        )

    # wrap pub socket into ZeroMQ stream
    app.pub_stream = ZMQStream(publish_socket)

    # create SUB socket listening to all events from all app instances
    subscribe_socket = context.socket(zmq.SUB)

    if app.zmq_pub_sub_proxy:
        # application started with XPUB/XSUB proxy
        app.zmq_xpub = options.zmq_xpub
        subscribe_socket.connect(app.zmq_xpub)
    else:
        # application started without XPUB/XSUB proxy
        app.zmq_sub_address = options.zmq_sub_address
        for address in app.zmq_sub_address:
            subscribe_socket.connect(address)

    subscribe_socket.setsockopt(
        zmq.SUBSCRIBE,
        create_control_channel_name()
    )

    def listen_control_channel():
        # wrap sub socket into ZeroMQ stream and set its on_recv callback
        app.sub_stream = ZMQStream(subscribe_socket)
        handle = functools.partial(handle_control_message, app)
        app.sub_stream.on_recv(handle)

    ioloop_instance.add_callback(listen_control_channel)

    app.event_callbacks = []
    callbacks = custom_settings.get('event_callbacks', [])

    for callback in callbacks:
        event_callback = utils.namedAny(callback)
        app.event_callbacks.append(event_callback)

    if not hasattr(app, 'admin_connections'):
        # initialize dict to keep admin connections
        app.admin_connections = {}

    if not hasattr(app, 'connections'):
        # initialize dict to keep client's connections
        app.connections = {}

    if app.zmq_pub_sub_proxy:
        logging.info(
            "Started: Tornado - {0}, ZeroMQ XPUB: {1}, XSUB: {2}".format(
                options.port, app.zmq_xpub, app.zmq_xsub
            )
        )
    else:
        logging.info(
            "Started: Tornado - {0}, ZeroMQ PUB - {1}; subscribed to {2}".format(
                options.port, app.zmq_pub_port, app.zmq_sub_address
            )
        )

    # finally, let's go
    try:
        ioloop_instance.start()
    except KeyboardInterrupt:
        logging.info('interrupted')
    finally:
        # clean
        if hasattr(app, 'pub_stream'):
            app.pub_stream.close()
        if hasattr(app, 'sub_stream'):
            app.sub_stream.on_recv(None)
            app.sub_stream.close()


if __name__ == '__main__':
    main()
