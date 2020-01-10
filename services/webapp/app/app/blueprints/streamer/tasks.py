from flask_socketio import SocketIO

from app import create_celery_app, socketio

celery = create_celery_app()

@celery.task(bind=True)
def test_tally_celery(self):
    print('IN CELERY BACKGROUND TASK')
    sio = SocketIO(logger=True, engineio_logger=True, message_queue='redis://:TCPYkerxvKQu@redis:6379/0', async_mode='threading')
    #from app.app import socketio as sio
    message = None
    self.update_state(state='PROGRESS',
                          meta={'current': 'working'})
    #sio.emit('local_request',{'data': message }, namespace='/test_local', broadcast=True)
    #sio.sleep(1)
    sio.emit('web_response2', {'data': 'SENT MESSAGE FROM CELERY TASK - BPTEST2'}, broadcast=True, namespace='/test_web2')
    sio.sleep(1)
    print('TRIED EMIT FROM CELERY BPTEST2')
    return('tried to print')



# from flask_socketio import SocketIO
# from app import create_celery_app
#
# import time
# import numpy as np
# from flask import *
# from flask_socketio import *
# from pattern.web import Twitter
#
# celery = create_celery_app()
#
#
# @celery.task
# def create_stream(phrase, queue):
#     """
#     Celery task that connects to the twitter stream and runs a loop, periodically
#     emitting tweet information to all connected clients.
#     """
#     # local = SocketIO(message_queue=queue)
#     # stream = Twitter().stream(phrase, timeout=30)
#     # local.emit('starting', {'data': 'Operation complete!'}, namespace='/twitter')
#     # for i in range(60):
#     #     print('hey ho')
#     #     local.emit('complete', {'data': 'Operation complete!'}, namespace='/twitter')
#     #
#     #     stream.update()
#     #     for tweet in reversed(stream):
#     #         local.emit('tweet')
#     #     stream.clear()
#     #     time.sleep(1)
#     #
#     # return queue
#     print('IN CELERY BACKGROUND TASK')
#     sio = SocketIO(logger=True, engineio_logger=True, message_queue='redis://:TCPYkerxvKQu@redis:6379/0', async_mode='threading')
#     message = None
#     self.update_state(state='PROGRESS',
#                       meta={'current': 'working'})
#     #sio.emit('local_request',{'data': message }, namespace='/test_local', broadcast=True)
#     #sio.sleep(1)
#     sio.emit('web_response1', {'data': 'SENT MESSAGE THROUGH CELERY BPTEST1'}, broadcast=True, namespace='/test_web2')
#     sio.sleep(1)
#     print('TRIED EMIT FROM CELERY BPTEST1')
#     return('tried to print')
#
# #
# # class TwitterListener(tweepy.StreamListener):
# #
# #     def __init__(self):
# #         self.database = os.environ['SHARED_DB_URI']
# #
# #     def on_error(self, status_code):
# #         if status_code == 420:
# #             # returning False in on_data disconnects the stream
# #             return False
# #
# #     def on_status(self, status):
# #         print(status.text)
# #         return True
# #
# #     def on_data(self, data):
# #         """
# #         Automatic detection of the kind of data collected from Twitter
# #         This method reads in tweet data as JSON and extracts the data we want.
# #         """
# #         try:
# #             # parse as json
# #             raw_data = json.loads(data)
# #
# #             # extract the relevant data
# #             if "text" in raw_data:
# #                 user = raw_data["user"]["screen_name"]
# #                 created_at = raw_data["created_at"]
# #                 tweet = raw_data["text"]
# #                 retweet_count = raw_data["retweet_count"]
# #                 id_str = raw_data["id_str"]
# #
# #             #insert data just collected into MySQL my_database
# #             #populate_table(user, created_at, tweet, retweet_count, id_str)
# #             print(f"Tweet colleted at: {created_at}")
# #
# #         except Exception as e:
# #             logging.error(traceback.format_exc())
# #             # Logs the error appropriately.
# #
# #
# # # todo : create the tables on init
# #     def populate_table(
# #         self, user, created_at, tweet, retweet_count, id_str, raw_data
# #     ):
# #         """Populate a given table witht he Twitter collected data
# #
# #         Args:
# #             user (str): username from the status
# #             created_at (datetime): when the tweet was created
# #             tweet (str): text
# #             retweet_count (int): number of retweets
# #             id_str (int): unique id for the tweet
# #             raw_data (json) : storing raw data for further usage
# #         """
# #
# #         dbconnect = connect_db(self.database)
# #
# #         cursor = dbconnect.cursor()
# #         cursor.execute("USE airflowdb")
# #
# #         # add content here
# #
# #         try:
# #             # what is missing?
# #             commit()
# #             print("commited")
# #
# #         except mysql.Error as e:
# #             print(e)
# #             dbconnect.rollback()
# #
# #         cursor.close()
# #         dbconnect.close()
# #
# #         return
# #
# #
# # @celery.task
# # def create_stream(keyword, queue):
# #
# #     logger = get_task_logger(__name__)
# #     """
# #     Celery task that connects to the twitter stream and runs a loop, periodically
# #     emitting tweet information to all connected clients.
# #     """
# #
# #     consumer_key = os.environ['TWITTER_API_KEY']
# #     consumer_secret = os.environ['TWITTER_API_SECRET']
# #     key = os.environ['TWITTER_ACCESS_TOKEN']
# #     secret = os.environ['TWITTER_ACCESS_SECRET']
# #
# #     auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
# #     auth.set_access_token(key, secret)
# #     api = tweepy.API(auth)
# #     #
# #     tweepy_listener = TwitterListener()
# #     tweepy_stream = tweepy.Stream(auth = api.auth, listener=tweepy_listener)
# #
# #     local = SocketIO(message_queue=queue)
# #     #
# #     stream = tweepy_stream.filter(track=['minecraft'])
# #     local.emit('stream')
# #     #
# #     for i in range(60):
# #         print("I'm working")
# #         # stream.update()
# #         for tweet in reversed(stream):
# #             print("I'm working")
# #
# #         # stream.clear()
# #         time.sleep(1)
# #     #
# #     return queue
# #
# #
# @celery.task
# def send_complete_message(queue):
#     """
#     Celery task that notifies the client that the twitter loop has completed executing.
#     """
#     local = SocketIO(message_queue=queue)
#     local.emit('complete', {'data': 'Operation complete!'})
