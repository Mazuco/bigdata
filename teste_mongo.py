from airflow import DAG
from airflow.providers.mongo.hooks.mongo import MongoHook
from airflow.operators.python import PythonOperator
from datetime import datetime

def ping_mongodb():
    print("Starting connection test with the Remote MongoDB...")
    
    # Chama a conexão que criamos na interface web
    hook = MongoHook(mongo_conn_id='mongo_default')
    client = hook.get_conn()
    
    # O comando server_info() força um 'ping' real no banco
    info = client.server_info()
    print(f"✅ Successfully connected! Remote MongoDB version {info.get('version')}")
    
    # Lista os bancos para provar que a permissão de leitura está funcionando
    bancos = client.list_database_names()
    print(f"✅ Databases visible to this user: {bancos}")
    
    return "Test completed successfully."

with DAG(
    dag_id='teste_conexao_mongodb',
    start_date=datetime(2024, 1, 1),
    schedule=None, # Rodará apenas quando você der o Play
    catchup=False,
    tags=['Teste', 'MongoDB']
) as dag:

    tarefa_teste = PythonOperator(
        task_id='verificar_comunicacao',
        python_callable=ping_mongodb
    )


