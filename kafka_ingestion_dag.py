# kafka_ingestion_dag.py
from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
from datetime import datetime, timedelta
from confluent_kafka import Producer
import json
import time

# --- 1. The Core Logic (Our Producer) ---
def run_kafka_producer():
    """
    Function executed by the Airflow Worker (IP: 192.168.15.97).
    Connects to the remote Kafka cluster to ingest data.
    """
    conf = {
        # Updated to point to your specific Kafka host IP
        'bootstrap.servers': '192.168.15.115:9092,192.168.15.115:9093,192.168.15.115:9094',
        'client.id': 'airflow-ingestion-worker',
        'acks': 'all',
        'enable.idempotence': True
    }
    
    producer = Producer(conf)
    topic = 'cluster-topic'
    
    try:
        for i in range(10):
            payload = {
                "event_id": f"airflow_{int(time.time())}_{i}",
                "source": "airflow_scheduler",
                "timestamp": str(datetime.now())
            }
            producer.produce(topic, json.dumps(payload).encode('utf-8'))
        
        producer.flush()
        print("Batch successfully ingested into remote Kafka cluster.")
        
    except Exception as e:
        print(f"Failed to produce messages: {e}")
        raise e 

# --- 2. DAG Definition ---
default_args = {
    'owner': 'vitor_data_eng',
    'depends_on_past': False,
    'start_date': datetime(2026, 3, 1), 
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 2,                       
    'retry_delay': timedelta(minutes=5) 
}

with DAG(
    'kafka_ingestion_pipeline_v1',
    default_args=default_args,
    description='Automated hourly ingestion into Kafka at 192.168.15.115',
    schedule=timedelta(hours=1), 
    catchup=False,                        
    tags=['ingestion', 'kafka']
) as dag:

    # --- 3. The Task ---
    ingest_task = PythonOperator(
        task_id='produce_web_events_to_kafka',
        python_callable=run_kafka_producer
    )

    ingest_task
