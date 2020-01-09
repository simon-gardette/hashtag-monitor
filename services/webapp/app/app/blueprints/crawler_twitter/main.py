import os
import sys
import time
import numpy as np
from flask import *
from flask_socketio import SocketIO
from celery import Celery, chain

from pattern.web import Twitter

from flask import Blueprint, render_template, abort
from jinja2 import TemplateNotFound

from app.extensions import db
from app.app_celery import celery, socketio

from config import BaseConfig


crawler_twitter = Blueprint('crawler_twitter', __name__)

@celery.task
def create_stream(phrase, queue):
    """
    Celery task that connects to the twitter stream and runs a loop, periodically
    emitting tweet information to all connected clients.
    """
    local = SocketIO(message_queue=queue)
    stream = Twitter().stream(phrase, timeout=30)

    for i in range(60):
        stream.update()
        for tweet in reversed(stream):
            sentiment = classify_tweet(tweet)
            x, y = vectorize_tweet(tweet)
            local.emit('tweet', {'id': str(i),
                                 'text': str(tweet.text.encode('ascii', 'ignore')),
                                 'sentiment': sentiment,
                                 'x': x,
                                 'y': y})
        stream.clear()
        time.sleep(1)

    return queue


@celery.task
def send_complete_message(queue):
    """
    Celery task that notifies the client that the twitter loop has completed executing.
    """
    local = SocketIO(message_queue=queue)
    local.emit('complete', {'data': 'Operation complete!'})

@crawler_twitter.route('/crawler-twitter/<phrase>', methods=['POST'])
def twitter(phrase):
    """
    Route that accepts a twitter search phrase and queues a task to initiate
    a connection to twitter.
    """
    queue = app.config['SOCKETIO_REDIS_URL']
    # create_stream.apply_async(args=[phrase, queue])
    chain(create_stream.s(phrase, queue), send_complete_message.s()).apply_async()
    return 'Establishing connection...'
