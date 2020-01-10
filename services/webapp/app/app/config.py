# -*- encoding: utf-8 -*-
import os

# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SQLALCHEMY_DATABASE_URI = os.environ.get('SHARED_DB_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ['SECRET_KEY']
    CELERY_BROKER_URL = 'redis://:TCPYkerxvKQu@redis:6379/0'
    CELERY_RESULT_BACKEND = 'redis://:TCPYkerxvKQu@redis:6379/0'
    SOCKETIO_REDIS_URL = 'redis://:TCPYkerxvKQu@redis:6379/0'
    BROKER_TRANSPORT = 'redis'
    CELERY_ACCEPT_CONTENT = ['pickle']


class ProductionConfig(Config):
    DEBUG = False

    # Security
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_DURATION = 3600

    # PostgreSQL database

class DebugConfig(Config):
    DEBUG = True
