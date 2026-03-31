# async_producer.py
from confluent_kafka import Producer
import time

# 1. Define the Callback Function
def delivery_report(err, msg):
    """
    Called once for each message produced to indicate delivery result.
    Triggered by poll() or flush().
    """
    if err is not None:
        print(f"Message delivery failed: {err}")
        # In production, we would log this to an error file or Dead Letter Queue
    else:
        print(f"Message delivered to {msg.topic()} [Partition: {msg.partition()}] at Offset: {msg.offset()}")


# 2. Producer Configuration
conf = {
    'bootstrap.servers': 'localhost:9092,localhost:9093,localhost:9094',
    'client.id': 'async-producer'
}

producer = Producer(conf)
topic = 'cluster-topic'

print("Starting asynchronous send...")
start_time = time.time()

# Sending 10 messages asynchronously
for i in range(10):
    message = f"Asynchronous message {i}"
    
    # 3. Produce and attach the callback
    producer.produce(
        topic, 
        message.encode('utf-8'), 
        callback=delivery_report
    )
    
    # 4. Trigger callbacks for events (success/failures) from previous produce() calls
    # poll(0) is non-blocking and highly efficient
    producer.poll(0)

# 5. Wait for any outstanding messages to be delivered and delivery reports to be received
print("Waiting for final deliveries...")
producer.flush()

end_time = time.time()
print(f"Total time taken: {end_time - start_time:.4f} seconds")

