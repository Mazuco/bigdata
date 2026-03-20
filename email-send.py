# email-send.py

from datetime import datetime
from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator
from airflow.operators.email import EmailOperator

smtp_user = 'smtp.mail.yahoo.com'

def print_hello():
    return 'Hello World!'

default_args = {
    'owner': 'Vitor',
    'start_date':datetime(2025,8,18),
}

with DAG(
    dag_id = 'email_alert_example',
    schedule = None,
    default_args = default_args,
) as dag:

    email = EmailOperator(
        task_id = 'email_alert',
        to = 'vitor.mazuco@yahoo.com.br',
        subject = 'Email Alert',
        html_content = """ <h3>Email Test by Airflow</h3>""",
        dag=dag
    )

    empty_operator = EmptyOperator(
        task_id = 'dummy_task',
        retries = 3,
        dag = dag
    )

    hello_operator = PythonOperator(
        task_id = 'hello_task',
        python_callable = print_hello,
        dag = dag
    )

    email >> empty_operator >> hello_operator
