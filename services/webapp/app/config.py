import os
basedir = os.path.abspath(os.path.dirname(__file__))


class BaseConfig:
    SQLALCHEMY_DATABASE_URI = os.environ.get('SHARED_DB_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ['SECRET_KEY']
    CELERY_BROKER_URL = 'redis://localhost:6379/0'
    CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
    SOCKETIO_REDIS_URL = 'redis://localhost:6379/0'
    BROKER_TRANSPORT = 'redis'
    CELERY_ACCEPT_CONTENT = ['pickle']
