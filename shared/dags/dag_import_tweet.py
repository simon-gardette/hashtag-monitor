# -*- coding: utf-8 -*-
"""
This DAG will use Papermill to run the notebook "twitter", based on the execution date
it will create an output notebook "out-<date>". All fields, including the keys in the parameters, are
templated.
"""

from datetime import timedelta

import airflow
from airflow.models import DAG
from airflow.operators.papermill_operator import PapermillOperator

default_args = {
    'owner': 'airflow',
    'start_date': airflow.utils.dates.days_ago(2)
}

with DAG(
    dag_id='example_papermill_operator',
    default_args=default_args,
    schedule_interval='0 0 * * *',
    dagrun_timeout=timedelta(minutes=60)
) as dag:
    # [START howto_operator_papermill]
    run_this = PapermillOperator(
        task_id="run_example_notebook",
        input_nb="/usr/local/airflow/notebooks/twitter.ipynb",
        output_nb="/usr/local/airflow/notebooks/out-twitter-{{ execution_date }}.ipynb",
        parameters={"msgs": "Ran from Airflow at {{ execution_date }}!"}
    )
    # [END howto_operator_papermill]