import os
import papermill as pm
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python_operator import PythonOperator

def execute_python_notebook_task(**context):
    notebook_path = context['notebook_path']
    out_path = context['out_path']
    out_dir = os.path.dirname(out_path)
    statement_parameters = context['statement_parameters'] if 'statement_parameters' in context else None

    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    if callable(statement_parameters):
        statement_parameters = statement_parameters(context)

    pm.execute_notebook(
        notebook_path,
        out_path,
        parameters=statement_parameters
    )

seven_days_ago = datetime.combine(
    datetime.today() - timedelta(7),
    datetime.min.time()
)

default_args = {
    'owner': 'airflow',
    'start_date': seven_days_ago,
    'provide_context': True,
}

dag_name = 'runnin_notebooks_yo'
schedule_interval = '@daily'

with DAG(dag_name, default_args=default_args, schedule_interval=schedule_interval) as dag:
    run_some_notebook_task = PythonOperator(
        task_id='run_some_notebook_task',
        python_callable=execute_python_notebook_task,
        op_kwargs={
            'notebook_path': '/usr/local/airflow/notebooks/twitter.ipynb',
            'out_path': '/usr/local/airflow/notebooks/out-twitter-{{ execution_date }}.ipynb',
            'statement_parameters': {
                'parameter_1': 'some_value'
            }
        }
    )