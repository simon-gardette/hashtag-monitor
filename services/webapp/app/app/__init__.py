#!/usr/bin/env python
import eventlet
eventlet.monkey_patch(socket=True)
from flask import Flask, render_template, session, request, jsonify, url_for
from flask_socketio import SocketIO, emit, join_room, leave_room, \
    close_room, rooms, disconnect

from celery import Celery

#from app.blueprints.bptest2 import bptest2
#from app.blueprints.bptest2 import tasks

socketio = SocketIO()


CELERY_TASK_LIST = [
    'app.blueprints.bptest1.tasks',
    'app.blueprints.bptest2.tasks',
]


def register_extensions(app):
    from app.extensions import db
    from app.extensions import login
    from app.extensions import migrate

    db.init_app(app)
    login.init_app(app)
    login.login_view = 'main.login'
    migrate.init_app(app, db)


def register_blueprints(app):
    # from app.webapp import server_bp
    # app.register_blueprint(server_bp)
    # from app.blueprints.bptest2 import bptest2
    # app.register_blueprint(bptest2)
    from app.blueprints.bptest1 import bptest1
    app.register_blueprint(bptest1)


def create_celery_app(app=None):
    """
    Create a new Celery object and tie together the Celery config to the app's
    config. Wrap all tasks in the context of the application.

    :param app: Flask app
    :return: Celery app
    """
    app = app or create_app()

    celery = Celery(app.import_name, broker='redis://:TCPYkerxvKQu@redis:6379/0',
                    include=CELERY_TASK_LIST)
    celery.conf.update(app.config)
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTask
    return celery

def create_app(main=True, debug=False):
    """Create an application."""
    app = Flask(__name__)
    #app.config.from_object(config[config_name])
    #config[config_name].init_app(app)
    #app.debug = debug

    async_mode = None

    #register_dashapps(app)
    register_extensions(app)
    register_blueprints(app)

    app.config['SECRET_KEY'] = 'secret!'

    # for socketio
    #socketio = SocketIO(app, logger=True, engineio_logger=True, message_queue=app.config['CELERY_BROKER_URL'])

    #socketio = SocketIO()
    #   socketio = SocketIO(None, logger=True, engineio_logger=True, message_queue=app.config['CELERY_BROKER_URL'], async_mode='threading')
    # # Initialize Celery


    #socketio.init_app(app, logger=True, engineio_logger=True, async_mode=async_mode, message_queue='redis://:devpassword@redis:6379/0')

    #######PUT THIS AFTER REGISTERING THE BLUEPRINT
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

    @app.route('/')
    def index():
        return render_template('index.html', async_mode=socketio.async_mode)


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
