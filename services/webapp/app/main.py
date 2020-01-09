# -*- encoding: utf-8 -*-
from app import create_app, create_celery_app
from flask_socketio import SocketIO

app = create_app()
celery = create_celery_app()
socketio = SocketIO()
