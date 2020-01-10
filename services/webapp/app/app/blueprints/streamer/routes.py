# # -*- encoding: utf-8 -*-
from app.blueprints.streamer import blueprint

from app import socketio, create_app

from celery import Celery

from flask_socketio import emit, join_room, leave_room, \
    close_room, rooms, disconnect

@blueprint.route('/streamer/minecraft', methods=['GET','POST'])
def send_room_message_without_socketio():
        from app.blueprints.streamer.tasks import test_tally_celery
        task = test_tally_celery.delay()
        print ('SENDING TO CELERY. Please wait..')
        return('Processing from BPTEST2.. please wait..')

@socketio.on('connect', namespace='/collector')
def test_connect():
    print('WEB CONNECTED ON OPEN AUTO')
    emit('web_response', {'data': 'Connected', 'count': 0})


@socketio.on('web_event', namespace='/collector')
def test_message(message):
    emit('web_response', {'data': message['data']})

@socketio.on('disconnect_request', namespace='/collector')
def local_disconnect_request():
    emit('lweb_response',
         {'data': 'Disconnected!'})
    socketio.sleep(0)
    print('WEB DISCONNECTED ON CLOSE/REFRESH')
    disconnect()



# from app.blueprints.streamer import blueprint
# from flask import render_template, redirect, url_for
# from flask_login import login_required, current_user
# from app.extensions import login_manager, db
#
# from .tasks import create_stream, send_complete_message
#
# from app.blueprints.interface.forms import AddBrand, AddKeyword
# from app.blueprints.interface.models import Brands, Keywords
# from celery import chain
#
#
# @blueprint.route('/collector/<keyword>', methods=['GET','POST'])
# def twitter(keyword):
#     """
#     Route that accepts a twitter search phrase and queues a task to initiate
#     a connection to twitter.
#     """
#     queue = 'redis://:TCPYkerxvKQu@redis:6379/0'
#     # create_stream.apply_async(args=[phrase, queue])
#     chain(create_stream.s(keyword, queue), send_complete_message.s()).apply_async()
#     return 'Establishing connection...'
#
# @blueprint.route('/collector-twitter', methods=['GET'])
# def index():
#     """
#     Route that maps to the main index page.
#     """
#     return render_template('collector.html')
