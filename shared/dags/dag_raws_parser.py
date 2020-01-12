from __future__ import print_function
from builtins import range
from airflow.operators.python_operator import PythonOperator
from airflow.operators.dummy_operator import DummyOperator
from airflow.models import DAG
from datetime import datetime, timedelta
import time

import os
import json
import logging
import traceback
from sqlalchemy import create_engine
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy import exc
from datetime import datetime
import pandas as pd
from textblob import TextBlob
from textblob_fr import PatternTagger, PatternAnalyzer
import pycld2 as cld2

log = logging.getLogger(__name__)

yesterday = datetime.combine(
    datetime.today() - timedelta(1),
    datetime.min.time()
)

args = {
    'owner': 'airflow',
    'start_date': yesterday,
}

dag = DAG(dag_id='raws_parser',
          default_args=args,
          schedule_interval='*/1 * * * *',
          catchup=False,
)

def parser(ds, **kwargs):
    parser = RawsParser()
    posts = parser.parser_raw_data()
    return posts

run_this = PythonOperator(
    task_id='raws_parser',
    provide_context=True,
    python_callable=parser,
    execution_timeout=None,
    dag=dag)

class RawsParser():
    def __init__(self):
        self.database = os.environ['SHARED_DB_URI']
        self.Base = automap_base()
        self.engine = create_engine(self.database)
        self.Base.prepare(self.engine, reflect=True)
        self.Platforms = self.Base.classes.platforms
        self.Raws = self.Base.classes.raws

    def get_platforms(self):
        # reflect the tables
        session = Session(self.engine)

        platforms = session.query(self.Platforms, self.Platforms.id).all()

        session.close()

        return platforms

    def get_raws(self, platform):
        session = Session(self.engine)
        try:
            query = session.query(self.Raws).filter_by(platform_id=platform.id,status=None).limit(1000).statement
            df = pd.read_sql(query, self.engine)
            session.close()

        except exc.SQLAlchemyError as e:
            print(e)
            session.close()
            log.error(e)
        return df

    def parser_raw_data(self):
        platforms = self.get_platforms()
        print(platforms)

        for platform in platforms:
            log.info(platform)
            print(platform)
            df_raws = self.get_raws(platform)
            df_raws = df_raws.drop(['created_at'], axis=1)
            df = pd.DataFrame()
            if platform.id == 1 and df_raws.empty is False:
                log.info('Parsing twitter')
                df = self.twitter_data(df_raws)
            elif platform.id == 2 and df_raws.empty is False:
                log.info('Parsing instagram')
                df = self.instagram_data(df_raws)
            else:
                log.error('There\'s an unmanaged platform here, do something.')
        return df
        self.engine.dispose()

    def twitter_data(self, df_raws):
        df_update= pd.DataFrame(columns=['id','status'])
        df_update['id']=df_raws['id']
        df_raws = df_raws.rename(columns={"api_id": "twitter_id", "id": "raw_id"})
        df_raws["twitter_id"] = pd.to_numeric(df_raws["twitter_id"])
        df_flattened = df_raws.raw_data.apply(lambda x: self.parse_json_twitter(x))
        df_flattened["twitter_id"] = pd.to_numeric(df_flattened["twitter_id"])
        df_result = pd.merge(df_raws, df_flattened, on=['twitter_id'])
        df_result = df_result.drop(['raw_data','status','platform_id'], axis=1)
        print(list(df_result.columns))
        df_result.to_sql('tweets',con=self.engine, if_exists='append', index=False)
        self.update_raw_status(df_update)
        return df_result

    def parse_json_twitter(self, df):
        twitter_id = df['id']
        twitter_user_id = df['user']['id']
        twitter_text = df['text']
        twitter_user_name = df['user']['name']
        twitter_followers_count = df['user']['followers_count']
        twitter_url  =  df['id']

        try:
            isReliable, textBytesFound, details = cld2.detect(twitter_text)
            twitter_lang = details[0][1]
        except Exception as e:
            logging.error(traceback.format_exc())

        twitter_sentiment = self.detect_sentiment(twitter_text, twitter_lang)
        twitter_topics  = None

        created_at = df['created_at']
        return pd.Series([twitter_id,
                          twitter_user_id,
                          twitter_text,
                          twitter_user_name,
                          twitter_followers_count,
                          twitter_lang,
                          twitter_sentiment,
                          twitter_topics,
                          twitter_url,
                          created_at],
                         index=['twitter_id',
                                'twitter_user_id',
                                'twitter_text',
                                'twitter_user_name',
                                'twitter_followers_count',
                                'twitter_lang',
                                'twitter_sentiment',
                                'twitter_topics',
                                'twitter_url',
                                'created_at'])

    def instagram_data(self, df_raws):
        df_update= pd.DataFrame(columns = ['id','status'])
        df_update['id']=df_raws['id']
        df_raws = df_raws.rename(columns={"api_id": "instagram_id", "id": "raw_id"})
        df_raws["instagram_id"] = pd.to_numeric(df_raws["instagram_id"])
        df_flattened = df_raws.raw_data.apply(lambda x: self.parse_json_instagram(x))
        df_flattened["instagram_id"] = pd.to_numeric(df_flattened["instagram_id"])
        df_result = pd.merge(df_raws, df_flattened, on=['instagram_id'])
        df_result = df_result.drop(['raw_data','status','platform_id'], axis=1)
        df_result.to_sql('instagrams',con=self.engine, if_exists='append', index=False)
        self.update_raw_status(df_update)

        return df_result

    def parse_json_instagram(self, df):
        instagram_id = df['id']
        instagram_user_id = df['owner']['id']
        instagram_user_name = None
        instagram_followers_count = None
        instagram_media_url = df['display_url']

        instagram_text  = df['edge_media_to_caption']['edges'][0]['node']['text']
        try:
            isReliable, textBytesFound, details = cld2.detect(instagram_text)
            instagram_lang = details[0][1]
        except Exception as e:
            logging.error(traceback.format_exc())

        instagram_sentiment = self.detect_sentiment(instagram_text, instagram_lang)


        instagram_topics  = None
        instagram_url  = df['shortcode']
        created_at = datetime.fromtimestamp(df['taken_at_timestamp'])

        return pd.Series([instagram_id,
                         instagram_user_id,
                         instagram_user_name,
                         instagram_followers_count,
                         instagram_media_url,
                         instagram_sentiment,
                         instagram_text ,
                         instagram_lang ,
                         instagram_topics ,
                         instagram_url ,
                         created_at],
                         index=['instagram_id',
                                'instagram_user_id',
                                'instagram_user_name',
                                'instagram_followers_count',
                                'instagram_media_url',
                                'instagram_sentiment',
                                'instagram_text',
                                'instagram_lang',
                                'instagram_topics',
                                'instagram_url',
                                'created_at'])
    @staticmethod
    def detect_sentiment(text, lang):
        if lang == 'fr':
            sentiment = TextBlob(text, pos_tagger=PatternTagger(), analyzer=PatternAnalyzer()).sentiment
            polarity = sentiment[0]
        else:
            sentiment = TextBlob(text).sentiment
            polarity = sentiment.polarity
        if polarity > 0.3:
            text_sentiment = 'Positive'
        elif polarity < -0.3:
            text_sentiment = 'Negative'
        else:
            text_sentiment = 'Neutral or Undefined'
        return text_sentiment

    def update_raw_status(self, df_update):
        df_update['status'] = 'Parsed'
        print(df_update.to_dict(orient='records'))
        session = Session(self.engine)
        try:
            session.bulk_update_mappings(
              self.Raws,
              df_update.to_dict(orient='records')
            )
            session.commit()
            session.close()

        except exc.SQLAlchemyError as e:
            session.rollback()
            print(e)
            session.close()
            log.error(e)
        pass
