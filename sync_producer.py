# sync_producer.py
from confluent_kafka import Producer
import time

conf = {
    'bootstrap.servers': 'localhost:9092,localhost:9093,localhost:9094',
    'client.id': 'sync-producer'
}

producer = Producer(conf)
topic = 'cluster-topic'

print("Starting synchronous send...")
start_time = time.time()

# Sending 10 messages synchronously
for i in range(10):
    message = f"Synchronous message {i}"
    
    # 1. Produce the message to the buffer
    producer.produce(topic, message.encode('utf-8'))
    
    # 2. Immediately wait for this specific message to be delivered
    # The flush() blocks until the message is sent and acknowledged
    producer.flush()
    print(f"Delivered: {message}")

end_time = time.time()
print(f"Total time taken: {end_time - start_time:.4f} seconds")

