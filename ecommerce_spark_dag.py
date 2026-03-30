# ecommerce_spark_dag.py
from airflow import DAG
from airflow.providers.ssh.operators.ssh import SSHOperator
from datetime import datetime, timedelta

# 1. Default arguments for the DAG
default_args = {
    'owner': 'data_engineering_team',
    'depends_on_past': False,
    'start_date': datetime(2026, 3, 29), # Adjust to your current date
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# 2. DAG Definition
with DAG(
    'spark_ecommerce_etl_job',
    default_args=default_args,
    description='Triggers a remote PySpark ETL job via SSH',
    schedule_interval='@daily', # Runs once a day at midnight
    catchup=False,
    tags=['spark', 'ecommerce', 'etl']
) as dag:

    # The exact command we would type in the terminal of the Spark server
    submit_command = "spark-submit /home/jovyan/work/processamento_ecommerce.py"

    # 3. The SSH Task (Acts as our remote Spark Submit)
    trigger_spark_job = SSHOperator(
        task_id='run_spark_submit',
        ssh_conn_id='spark_ssh_conn', # Matches the Connection ID created in the UI
        command=submit_command,
        cmd_timeout=600 # Wait up to 10 minutes for the Spark job to finish
    )

    # Define the execution flow (just one task for now)
    trigger_spark_job
