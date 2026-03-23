# etl_ecommerce.py

import json
import os
from datetime import datetime
from airflow import DAG
from airflow.providers.mongo.hooks.mongo import MongoHook
from airflow.operators.python import PythonOperator
from hdfs import InsecureClient 

# Variables
FILE_PATH = '/opt/airflow/dags/data/clickstream_extract.json'
HADOOP_URL = 'http://192.168.15.187:9870' # Ex: http://192.168.1.100:9870
HADOOP_USER = 'root'
HDFS_DESTINATION_DIR = '/datalake/raw/ecommerce'
HDFS_DESTINATION_FILE = f'{HDFS_DESTINATION_DIR}/clickstream_extract.json'

def extract_ecommerce_logs():
    os.makedirs(os.path.dirname(FILE_PATH), exist_ok=True)
    
    hook = MongoHook(mongo_conn_id='mongo_default')
    client = hook.get_conn()
    collection = client.ecommerce_db.web_traffic_logs
    
    print("Starting batch extraction from MongoDB...")
    documents = list(collection.find().limit(50000))
    
    for doc in documents:
        doc['_id'] = str(doc['_id'])
        doc['timestamp'] = doc['timestamp'].isoformat()
        
    with open(FILE_PATH, 'w') as f:
        json.dump(documents, f, indent=4)
        
    print(f"✅ {len(documents)} web traffic records saved to {FILE_PATH} (Staging)")

def load_to_hadoop():
    print(f"Connecting to remote Hadoop via WebHDFS at {HADOOP_URL}...")
    
    # InsecureClient é usado quando o Hadoop não tem Kerberos (autenticação de segurança corporativa)
    client = InsecureClient(HADOOP_URL, user=HADOOP_USER)
    
    # Cria a pasta no HDFS se ela não existir
    client.makedirs(HDFS_DESTINATION_DIR)
    
    # Faz o upload do arquivo da nossa Staging Area para o servidor remoto
    print(f"Uploading file to HDFS: {HDFS_DESTINATION_FILE}")
    client.upload(HDFS_DESTINATION_DIR, FILE_PATH, overwrite=True)
    
    print("✅ Load finished! Data successfully transferred to remote Apache Hadoop.")

with DAG(
    dag_id='etl_ecommerce_mongo_hadoop',
    start_date=datetime(2024, 1, 1),
    schedule='@daily',
    catchup=False,
    tags=['BigData', 'MongoDB', 'Hadoop']
) as dag:

    extract_task = PythonOperator(
        task_id='extract_mongo_data',
        python_callable=extract_ecommerce_logs
    )

    load_task = PythonOperator(
        task_id='load_to_remote_hdfs',
        python_callable=load_to_hadoop
    )

    # Execution order
    extract_task >> load_task


