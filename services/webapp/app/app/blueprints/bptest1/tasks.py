# -*- encoding: utf-8 -*-

from . import bptest1
from flask_socketio import SocketIO
from app import create_celery_app, socketio

celery = create_celery_app()

@celery.task(bind=True)
# def test_tally_celery(self):
#     print('IN CELERY BACKGROUND TASK')
#     sio = SocketIO(logger=True, engineio_logger=True, message_queue='redis://:TCPYkerxvKQu@redis:6379/0', async_mode='threading')
#     #from app.app import socketio as sio
#     message = None
#     self.update_state(state='PROGRESS',
#                           meta={'current': 'working'})
#     #sio.emit('local_request',{'data': message }, namespace='/test_local', broadcast=True)
#     #sio.sleep(1)
#     sio.emit('web_response1', {'data': 'SENT MESSAGE THROUGH CELERY BPTEST1'}, broadcast=True, namespace='/test_web2')
#     sio.sleep(1)
#     print('TRIED EMIT FROM CELERY BPTEST1')
#     return('tried to print')


@celery.task
def create_stream(phrase, queue):
    """
    Celery task that connects to the twitter stream and runs a loop, periodically
    emitting tweet information to all connected clients.
    """
    print('IN CELERY BACKGROUND TASK')
    sio = SocketIO(logger=True, engineio_logger=True, message_queue='redis://:TCPYkerxvKQu@redis:6379/0', async_mode='threading')
    message = None
    self.update_state(state='PROGRESS',
                          meta={'current': 'working'})
    #sio.emit('local_request',{'data': message }, namespace='/test_local', broadcast=True)
    #sio.sleep(1)
    sio.emit('web_response1', {'data': 'SENT MESSAGE THROUGH CELERY BPTEST1'}, broadcast=True, namespace='/test_web2')
    sio.sleep(1)
    print('TRIED EMIT FROM CELERY BPTEST1')
    return('tried to print')
    # local = SocketIO(message_queue=queue)
    #
    # # stream = Twitter().stream(phrase, timeout=30)
    #
    # for i in range(60):
    #     print("I'm working")
    #     # stream.update()
    #     # for tweet in reversed(stream):
    #     #     sentiment = classify_tweet(tweet)
    #     #     x, y = vectorize_tweet(tweet)
    #     #     local.emit('tweet', {'id': str(i),
    #     #                          'text': str(tweet.text.encode('ascii', 'ignore')),
    #     #                          'sentiment': sentiment,
    #     #                          'x': x,
    #     #                          'y': y})
    #     # stream.clear()
    #     time.sleep(1)
    #
    # return queue


@celery.task
def send_complete_message(queue):
    """
    Celery task that notifies the client that the twitter loop has completed executing.
    """
    local = SocketIO(message_queue=queue)
    local.emit('complete', {'data': 'Operation complete!'})
