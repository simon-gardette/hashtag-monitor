# -*- encoding: utf-8 -*-
from . import bptest1
from .tasks import create_stream, send_complete_message
from app import socketio
from celery import chain

# @bptest1.route('/SendTallyFunc/', methods=['GET','POST'])
# def send_room_message_without_socketio():
#         from .tasks import test_tally_celery
#         print('SENDING TO CELERY')
#         tasks = test_tally_celery.delay()
#         return ('Processing.. please wait..')

@bptest1.route('/crawler-twitter/<phrase>', methods=['GET','POST'])
def twitter(phrase):
    """
    Route that accepts a twitter search phrase and queues a task to initiate
    a connection to twitter.
    """
    queue = 'redis://:TCPYkerxvKQu@redis:6379/0'
    # create_stream.apply_async(args=[phrase, queue])
    chain(create_stream.s(phrase, queue), send_complete_message.s()).apply_async()
    return 'Establishing connection...'


# @socketio.on('connect', namespace='/test_web2')
# def test_connect():
#     print('WEB CONNECTED ON OPEN AUTO')
#     emit('web_response', {'data': 'Connected', 'count': 0})


# @socketio.on('web_event', namespace='/test_web2')
# def test_message(message):
#     session['receive_count'] = session.get('receive_count', 0) + 1
#     emit('web_response',
#          {'data': message['data'], 'count': session['receive_count']})

# @socketio.on('disconnect_request', namespace='/test_web2')
# def local_disconnect_request():
#     session['receive_count'] = session.get('receive_count', 0) + 1
#     #print('in disconnect_request')
#     emit('web_response',
#          {'data': 'Disconnected!', 'count': session['receive_count']})
#     socketio.sleep(0)
#     print('WEB DISCONNECTED ON CLOSE/REFRESH')
#     disconnect()
