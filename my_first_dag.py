# my_first_dag.py

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from datetime import datetime

# 1. Funções Python que as tarefas vão executar
def personalized_greeting():
    print("Hi! This is your first Python assignment on Airflow.")

# 2. Definição da DAG
with DAG(
    dag_id='intro_class_vitor',
    start_date=datetime(2024, 1, 1),
    schedule='@daily',
    catchup=False
) as dag:

    # 3. Definindo as tarefas (Tasks)
    task_1 = BashOperator(
        task_id='comando_bash_ola',
        bash_command='echo "Starting the data pipeline..." '
    )

    task_2 = PythonOperator(
        task_id='python_greeting_function',
        python_callable=personalized_greeting
    )

    task_3 = BashOperator(
        task_id='end_of_flow',
        bash_command='echo "Pipeline completed successfully!"'
    )

    # 4. Definindo a ordem (Dependências)
    # A tarefa 1 roda primeiro, depois a 2, depois a 3.
    task_1 >> task_2 >> task_3
