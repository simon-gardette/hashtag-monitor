# -*- encoding: utf-8 -*-

import eventlet
eventlet.monkey_patch(socket=True)
from flask import Flask
from flask_socketio import SocketIO, emit, join_room, leave_room, \
    close_room, rooms, disconnect
from importlib import import_module
from flask_login import LoginManager
from celery import Celery
from logging import basicConfig, DEBUG, getLogger, StreamHandler
from datetime import datetime

socketio = SocketIO()





def register_extensions(app):
    from app.extensions import db
    from app.extensions import login_manager
    from app.extensions import migrate

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'main.login'

    migrate.init_app(app, db)


def register_blueprints(app):
    for module_name in ('base', 'home', 'interface'):
        module = import_module('app.blueprints.{}.routes'.format(module_name))
        app.register_blueprint(module.blueprint)


def create_celery_app(app=None):
    """
    Create a new Celery object and tie together the Celery config to the app's
    config. Wrap all tasks in the context of the application.

    :param app: Flask app
    :return: Celery app
    """
    app = app or create_app()

    celery = Celery(app.import_name,
                    broker='redis://:TCPYkerxvKQu@redis:6379/0'
                    )
    celery.conf.update(app.config)

    return celery


def configure_database(app):

    @app.before_first_request
    def initialize_database():
        db.drop_all() # delete on production. should insert a condition here
        db.create_all()




    @app.teardown_request
    def shutdown_session(exception=None):
        db.session.remove()


def configure_logs(app):
    # soft logging
    try:
        basicConfig(filename='error.log', level=DEBUG)
        logger = getLogger()
        logger.addHandler(StreamHandler())
    except:
        pass


def create_app(main=True, debug=False):
    """Create an application."""
    app = Flask(__name__, static_folder='blueprints/base/static')
    # Need to make taht a var to accept debug etc.
    app.config.from_object('app.config.ProductionConfig')

    async_mode = None

    register_extensions(app)

    # configure_database(app)

    register_blueprints(app)

    #register_dashapps(app) #Dashapp are a separated core to render infos

    configure_logs(app)

    # fo unit tests (will probably not be implemented in 1st version)
    # if selenium:
    #     app.config['LOGIN_DISABLED'] = True

    # This always need to be after BluePrint
    if main:
        # Initialize socketio server and attach it to the message queue, so
        # that everything works even when there are multiple servers or
        # additional processes such as Celery workers wanting to access
        # Socket.IO
        socketio.init_app(app, logger=True, engineio_logger=True,
                          message_queue='redis://:TCPYkerxvKQu@redis:6379/0')
        #socketio = SocketIO(app, logger=True, engineio_logger=True, message_queue=app.config['CELERY_BROKER_URL'])
    else:
        # Initialize socketio to emit events through through the message queue
        # Note that since Celery does not use eventlet, we have to be explicit
        # in setting the async mode to not use it.
        socketio.init_app(None, logger=True, engineio_logger=True,
                          message_queue='redis://:TCPYkerxvKQu@redis:6379/0',
                          async_mode='threading')

    return app


def register_dashapps(app):
    from app.blueprints.dashapp1.layout import layout
    from app.blueprints.dashapp1.callbacks import register_callbacks

    # Meta tags for viewport responsiveness
    meta_viewport = {"name": "viewport", "content": "width=device-width, initial-scale=1, shrink-to-fit=no"}

    dashapp1 = dash.Dash(__name__,
                         app=app,
                         url_base_pathname='/dashboard/',
                         assets_folder=get_root_path(__name__) + '/dashboard/assets/',
                         meta_tags=[meta_viewport])

    with app.app_context():
        dashapp1.title = 'Dashapp 1'
        dashapp1.layout = layout
        register_callbacks(dashapp1)

    _protect_dashviews(dashapp1)


def _protect_dashviews(dashapp):
    for view_func in dashapp.app.view_functions:
        if view_func.startswith(dashapp.config.url_base_pathname):
            dashapp.app.view_functions[view_func] = login_required(dashapp.app.view_functions[view_func])
