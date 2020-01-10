from __future__ import print_function
from builtins import range
from airflow.operators.python_operator import PythonOperator
from airflow.models import DAG
from datetime import datetime, timedelta
import time

from InstagramAPI import InstagramAPI

from pprint import pprint

#set up our main class using tweepy.StreamListener
class InstagramCollector():

    def __init__(self):
        self.database = os.environ['SHARED_DB_URI']


    def collect ():
        pass

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

        ins = raw_tweet.insert().values(rawtweet=raw_data)

        #actual content of request
        conn.execute(ins)

        try:
            trans.commit()

        except mysql.Error as e:
            print(e)
            trans.rollback()

        # Close connection
        conn.close()
        print(f"Tweet colleted")
        return

today = datetime.today()

args = {
    'owner': 'airflow',
    'start_date': today,
}

dag = DAG(dag_id='stream_twitter_data',
          default_args=args,
          schedule_interval=None
)


def collect_grams(ds, **kwargs):
    collect_grams = InstagramCollector()

    return collect_grams

run_this = PythonOperator(
    task_id='stream_tweets',
    provide_context=True,
    python_callable=stream_tweets,
    execution_timeout=None,
    dag=dag)

# for i in range(10):
#     '''
#     Generating 10 sleeping task, sleeping from 0 to 9 seconds
#     respectively
#     '''
#     task = PythonOperator(
#         task_id='sleep_for_'+str(i),
#         python_callable=my_sleeping_function,
#         op_kwargs={'random_base': float(i)/10},
#         dag=dag)
#
#     task.set_upstream(run_this)
