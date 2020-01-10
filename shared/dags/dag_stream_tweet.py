from __future__ import print_function
from builtins import range
from airflow.operators.python_operator import PythonOperator
from airflow.operators.dummy_operator import DummyOperator
from airflow.models import DAG
from datetime import datetime, timedelta
import time

import tweepy
import os
import json
import logging
import parser
import traceback
import sys
import sqlalchemy
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy import exc

from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine

from pprint import pprint

log = logging.getLogger(__name__)



seven_days_ago = datetime.combine(
    datetime.today() - timedelta(7),
    datetime.min.time()
)

args = {
    'owner': 'airflow',
    'start_date': seven_days_ago,
}

dag = DAG(dag_id='stream_twitter_data',
          default_args=args,
          schedule_interval=None
)

def get_keywords():
    Base = automap_base()

    # engine, suppose it has two tables 'user' and 'address' set up
    engine = create_engine(os.environ['SHARED_DB_URI'])

    # reflect the tables
    Base.prepare(engine, reflect=True)

    # mapped classes are now created with names by default
    # matching that of the table name.

    raws = Base.classes.raws
    keywords = Base.classes.keywords

    session = Session(engine)

    keywords = session.query(keywords).all()

    session.close()
    engine.dispose()

    return keywords


def stream_tweets(ds, **kwargs):
    keyword_name = kwargs.get("keyword_name")
    keyword_id = kwargs.get("keyword_id")
    brand_id = kwargs.get("brand_id")
    log.info("something happened")
    pprint('hello')
    consumer_key = os.environ['TWITTER_API_KEY']
    consumer_secret = os.environ['TWITTER_API_SECRET']
    key = os.environ['TWITTER_ACCESS_TOKEN']
    secret = os.environ['TWITTER_ACCESS_SECRET']

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(key, secret)
    api = tweepy.API(auth)

    tweepy_listener = TwitterListener(keyword_id=keyword_id, brand_id=brand_id)
    tweepy_stream = tweepy.Stream(auth = api.auth, listener=tweepy_listener)
    while True:  # a while loop to achieve what I want to do
        log.info("something happened")
        results = tweepy_stream.filter(track=[keyword_name])
        log.info(results)
        print(results)
        time.sleep(3600)

    return results

join = DummyOperator(
    task_id='join',
    trigger_rule='one_success',
    dag=dag,
)

keywords = get_keywords()

for keyword in keywords:
    run_this = PythonOperator(
        task_id='stream_tweets_'+ keyword.keyword_name,
        provide_context=True,
        python_callable=stream_tweets,
        execution_timeout=None,
        op_kwargs={'keyword_id': keyword.id,
                   'keyword_name': keyword.keyword_name,
                   'brand_id': keyword.brand_id},
        dag=dag)

#
# run_this >> join



#set up our main class using tweepy.StreamListener
class TwitterListener(tweepy.StreamListener):

    def __init__(self, **kwargs):
        self.database = os.environ['SHARED_DB_URI']
        self.keyword_id = kwargs.get("keyword_id")
        self.brand_id = kwargs.get("brand_id")

    def on_error(self, status_code):
        if status_code == 420:
            # returning False in on_data disconnects the stream
            return False

    def on_status(self, status):
        print(status.text)
        return True

    def on_data(self, data):
        """
        Automatic detection of the kind of data collected from Twitter
        This method reads in tweet data as JSON and extracts the data we want.
        """
        try:
            # parse as json
            raw_data = json.loads(data)
            print(raw_data)
            #insert data just collected into MySQL my_database
            self.populate_table(raw_data)

        except Exception as e:
            logging.error(traceback.format_exc())
            # Logs the error appropriately.


    # todo : create the tables on init
    def populate_table(self, raw_data):
        """Populate a given table witht he Twitter collected data

        Args:
            raw_data (json) : storing raw data for further usage
        """
        engine = create_engine(self.database)

        # Create connection
        conn = engine.connect()
        meta = MetaData()

        #get table
        raw_tweet = Table('raws', meta, autoload=True, autoload_with=engine)

        # Begin transaction
        trans = conn.begin()

        ins = raw_tweet.insert().values(brand_id=self.brand_id,
                                    	keyword_id=self.keyword_id,
                                    	platform_id=1,
                                    	api_id='none',
                                    	raw_data=raw_data,
                                    	created_at=datetime.now()
                                        )

        #actual content of request
        conn.execute(ins)

        try:
            trans.commit()

        except exc.SQLAlchemyError as e:
            print(e)
            log.error(e)
            trans.rollback()

        # Close connection
        conn.close()
        engine.dispose()
        print(f"Tweet colleted")
        return
