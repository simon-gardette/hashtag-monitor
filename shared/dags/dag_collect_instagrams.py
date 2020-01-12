from __future__ import print_function
from builtins import range
from airflow.operators.python_operator import PythonOperator
from airflow.operators.dummy_operator import DummyOperator
from airflow.models import DAG
from datetime import datetime, timedelta
import time

from random import choice
from datetime import datetime
import json
import requests
from bs4 import BeautifulSoup
import IPython.display
import os
from sqlalchemy import create_engine, MetaData, Table, exc
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session

import logging


log = logging.getLogger(__name__)

yesterday = datetime.combine(
    datetime.today() - timedelta(1),
    datetime.min.time()
)

USER_AGENTS = ['Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36']

args = {
    'owner': 'airflow',
    'start_date': yesterday,
}

dag = DAG(dag_id='stream_instagram_datas',
          default_args=args,
          schedule_interval='*/5 * * * *',
          catchup=False
)

def get_keywords():
    Base = automap_base()

    # engine, suppose it has two tables 'user' and 'address' set up
    engine = create_engine(os.environ['SHARED_DB_URI'])

    # reflect the tables
    Base.prepare(engine, reflect=True)

    # mapped classes are now created with names by default
    # matching that of the table name.

    keywords = Base.classes.keywords

    session = Session(engine)

    keywords = session.query(keywords).all()

    session.close()
    engine.dispose()

    return keywords


def collect_grams(ds, **kwargs):
    hashtag = kwargs.get("keyword_name")
    keyword_id = kwargs.get("keyword_id")
    brand_id = kwargs.get("brand_id")
    # Define the URL for the profile page.

    url = 'https://www.instagram.com/explore/tags/'+hashtag+'/'

    # Initiate a scraper object and call one of the methods.
    instagram = InstagramScraper(url, keyword_id=keyword_id, brand_id=brand_id)
    results = instagram.hashtag_posts()
    return results

join = DummyOperator(
    task_id='join',
    trigger_rule='one_success',
    dag=dag
)

keywords = get_keywords()

for keyword in keywords:
    run_this = PythonOperator(
        task_id='stream_instagrams_'+ keyword.keyword_name,
        provide_context=True,
        python_callable=collect_grams,
        execution_timeout=None,
        op_kwargs={'keyword_id': keyword.id,
                   'keyword_name': keyword.keyword_name,
                   'brand_id': keyword.brand_id},
        dag=dag)
    run_this >> join

class InstagramScraper:
    def __init__(self, url, user_agents=None, **kwargs):
        self.url = url
        self.user_agents = user_agents
        self.database = os.environ['SHARED_DB_URI']
        self.keyword_id = kwargs.get("keyword_id")
        self.brand_id = kwargs.get("brand_id")

    def __random_agent(self):
        if self.user_agents and isinstance(self.user_agents, list):
            return choice(self.user_agents)
        return choice(USER_AGENTS)

    def __request_url(self):
        try:
            response = requests.get(
                        self.url,
                        headers={'User-Agent': self.__random_agent()})
            response.raise_for_status()
        except requests.HTTPError:
            raise requests.HTTPError('Received non-200 status code.')
        except requests.RequestException:
            raise requests.RequestException
        else:
            return response.text
    @staticmethod
    def extract_json(html):
        soup = BeautifulSoup(html, 'html.parser')
        body = soup.find('body')
        script_tag = body.find('script')
        raw_string = script_tag.text.strip().replace('window._sharedData =', '').replace(';', '')
        return json.loads(raw_string)

    def raw_response(self):
        results = {}
        try:
            response = self.__request_url()
            json_data = self.extract_json(response)
            return json_data
        except Exception as e:
            raise e

    def hashtag_posts(self):
        results = []
        try:
            response = self.__request_url()
            json_data = self.extract_json(response)
            infos = json_data['entry_data']['TagPage'][0]['graphql']['hashtag']['edge_hashtag_to_media']['edges']
        except Exception as e:
            raise e
        else:
            for node in infos:
                node = node.get('node')
                if node and isinstance(node,dict):
                    results.append(node)
                    self.populate_table(node, node['id'])
        return results

    def populate_table(self, raw_data, api_id):
        """
        Populate a given table witht he Twitter collected data
        Args:raw_data (json) : storing raw data for further usage
        """

        Base = automap_base()

        # engine, suppose it has two tables 'user' and 'address' set up
        engine = create_engine(os.environ['SHARED_DB_URI'])

        # reflect the tables
        Base.prepare(engine, reflect=True)

        # mapped classes are now created with names by default
        # matching that of the table name.

        Raws = Base.classes.raws

        session = Session(engine)

        add_raws = Raws(brand_id=self.brand_id,
                   keyword_id=self.keyword_id,
                   platform_id=2,
                   api_id=api_id,
                   raw_data=raw_data,
                   created_at=datetime.now())
        session.add(add_raws)
        try:
            session.commit()

        except exc.SQLAlchemyError as e:
            print(e)
            log.error(e)
            session.rollback()
            pass

        # Close connection
        session.close()
        engine.dispose()
        log.info(f"Instagram collected")
        return
