# partition_producer.py
from confluent_kafka import Producer
import time

def delivery_report(err, msg):
    """Callback to confirm delivery and show the assigned partition."""
    if err is not None:
        print(f"FAILED delivery: {err}")
    else:
        # Check if key exists to decode it safely
        key = msg.key().decode('utf-8') if msg.key() else 'NULL'
        print(f"Key: {key:<10} | Partition: {msg.partition()} | Offset: {msg.offset()}")

# Connect to the 3-node cluster
conf = {'bootstrap.servers': 'localhost:9092,localhost:9093,localhost:9094'}
producer = Producer(conf)
topic = 'cluster-topic'
TOTAL_PARTITIONS = 3 # We created cluster-topic with 3 partitions earlier

print("--- 1. Sending Messages WITHOUT Keys (Round-Robin) ---")
for i in range(3):
    producer.produce(topic, value=f"Random event {i}".encode('utf-8'), callback=delivery_report)

producer.flush()
time.sleep(1)


print("\n--- 2. Sending Messages WITH Keys (Consistent Hashing) ---")
# customer_A events will ALWAYS go to one partition, customer_B to another.
events = [
    {"key": "customer_A", "action": "login"},
    {"key": "customer_B", "action": "login"},
    {"key": "customer_A", "action": "click"},
    {"key": "customer_B", "action": "purchase"}
]

for event in events:
    producer.produce(
        topic, 
        key=event["key"].encode('utf-8'), 
        value=event["action"].encode('utf-8'), 
        callback=delivery_report
    )

producer.flush()
time.sleep(1)

print("\n--- 3. Custom Partitioner (The Banana Problem) ---")
def banana_partitioner(customer_key):
    """
    Custom logic: 'Banana' always goes to the last partition (Partition 2).
    Everyone else gets hashed into Partition 0 or 1.
    """
    if customer_key == "Banana":
        return TOTAL_PARTITIONS - 1
    else:
        # Simple hash simulation for the remaining partitions
        return hash(customer_key) % (TOTAL_PARTITIONS - 1)

business_events = ["Apple", "Banana", "Orange", "Banana", "Grape"]

for customer in business_events:
    chosen_partition = banana_partitioner(customer)
    
    producer.produce(
        topic, 
        key=customer.encode('utf-8'), 
        value=f"Transaction from {customer}".encode('utf-8'), 
        partition=chosen_partition, # Explicitly forcing the partition
        callback=delivery_report
    )

producer.flush()
