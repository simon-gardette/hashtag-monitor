from __future__ import print_function
from builtins import range
from airflow.operators.python_operator import PythonOperator
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
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.dialects.postgresql import insert


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

dag = DAG(dag_id='stream_instagram_data',
          default_args=args,
          schedule_interval='*/5 * * * *'
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


def collect_grams(ds, **kwargs):
    hashtag = kwargs.get("keyword_name")
    keyword_id = kwargs.get("keyword_id")
    brand_id = kwargs.get("brand_id")
    # Define the URL for the profile page.

    url = 'https://www.instagram.com/explore/tags/'+hashtag+'/'

    # Initiate a scraper object and call one of the methods.
    instagram = InstagramScraper(url, keyword_id=keyword_id, brand_id=brand_id)
    posts = instagram.raw_response()
    IPython.display.JSON(posts)
    return results

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

    def page_metrics(self):
        results = {}
        try:
            response = self.__request_url()
            json_data = self.extract_json(response)
            metrics = json_data['entry_data']['ProfilePage'][0]['graphql']['user']
        except Exception as e:
            raise e
        else:
            for key, value in metrics.items():
                if key != 'edge_owner_to_timeline_media':
                    if value and isinstance(value, dict):
                        value = value['count']
                        results[key] = value
        return results
    def hashtag_posts(self):
        results = []
        try:
            response = self.__request_url()
            json_data = self.extract_json(response)
            infos = posts['entry_data']['TagPage'][0]['graphql']['hashtag']['edge_hashtag_to_media']['edges']
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

        ins = insert(raw_tweet).values(brand_id=self.brand_id,
                                    	keyword_id=self.keyword_id,
                                    	platform_id=2,
                                    	api_id=api_id,
                                    	raw_data=raw_data,
                                    	created_at=datetime.now()
                                        )


        do_update_ins = ins.on_conflict_do_update(
            constraint='api_id',
            set_=dict(brand_id=self.brand_id,
                      keyword_id=self.keyword_id,
                      platform_id=2,
                      api_id=api_id,
                      raw_data=raw_data,
                      created_at=datetime.now())
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
