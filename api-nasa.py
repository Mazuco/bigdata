# api-nasa.py

import json
import pathlib
import requests
from datetime import date, datetime, timedelta 
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

dag_owner = 'Vitor'

def _get_pictures():
    # Salvando na pasta mapeada dags/images para você ver o arquivo no seu Linux
    save_dir = "/opt/airflow/dags/images"
    pathlib.Path(save_dir).mkdir(parents=True, exist_ok=True)
    
    api_key = 'dfvdvdfvdfvdffvvdvdvdfdvdfdfvdfv'
    url = f'https://api.nasa.gov/planetary/apod?api_key={api_key}'
    
    response = requests.get(url).json()
    today_image = response.get('hdurl')
    
    if today_image:
        # Apontando o caminho completo na hora de salvar
        file_path = f'{save_dir}/todays_image_{date.today()}.png'
        
        with open(file_path, 'wb') as f:
            f.write(requests.get(today_image).content)
            
        print(f"Sucesso! Imagem salva em: {file_path}")
    else:
        print("A API da NASA não retornou imagem hoje (pode ser um vídeo).")

default_args = {
    'owner': dag_owner,
    'depends_on_past': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5)
}	

with DAG(
    dag_id='download_ASOD_image',
    default_args=default_args,
    description='Download NASA image and notify',
    start_date=datetime(2023, 1, 1),
    schedule='@daily',
    catchup=False, # Configurado para False para não rodar milhares de vezes
    tags=['NASA']
) as dag:
 
    get_pictures = PythonOperator(
        task_id="get_pictures",
        python_callable=_get_pictures,
    )
 
    # Usando a variável nativa {{ ds }} do Airflow para pegar a data atual no Bash
    notify = BashOperator(
        task_id="notify",
        bash_command='echo "Images for {{ ds }} have been added!"',
    )
 
    get_pictures >> notify
 
