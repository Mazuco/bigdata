# simple_producer.py
from confluent_kafka import Producer

# Settings pointing to the 3 nodes of our local cluster.
configuracao = {
    'bootstrap.servers': 'localhost:9092,localhost:9093,localhost:9094',
    'client.id': 'meu-primeiro-produtor'
}

# Instantiating the Producer
producer = Producer(configuracao)

topico = 'cluster-topic'
mensagem = 'Starting data ingestion into Big Data!'

# Sending to buffer
producer.produce(topic=topico, value=mensagem.encode('utf-8'))

# Forcing the shipment to Kafka
producer.flush()

print("Message sent successfully!")


