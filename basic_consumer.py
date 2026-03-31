# basic_consumer.py
from confluent_kafka import Consumer, KafkaException, KafkaError
import sys
import signal

# --- 1. Signal Handler for Graceful Shutdown ---
# This ensures we exit cleanly when pressing Ctrl+C
running = True

def signal_handler(sig, frame):
    global running
    print("\n[INFO] Termination signal received. Initiating graceful shutdown...")
    running = False

signal.signal(signal.SIGINT, signal_handler)

# --- 2. Consumer Configuration ---
conf = {
    'bootstrap.servers': 'localhost:9092,localhost:9093,localhost:9094',
    'group.id': 'bigdata-analytics-group',
    'auto.offset.reset': 'earliest' # If no previous offset exists, start from the beginning
}

# --- 3. Instantiating and Subscribing ---
consumer = Consumer(conf)
topic = 'cluster-topic'

consumer.subscribe([topic])
print(f"[INFO] Consumer started. Subscribed to topic: {topic}")
print("[INFO] Waiting for messages... (Press Ctrl+C to stop)")

# --- 4. The Poll Loop ---
try:
    while running:
        # poll(1.0) waits up to 1 second for data. If nothing arrives, it returns None.
        msg = consumer.poll(timeout=1.0)
        
        if msg is None:
            continue
            
        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                # End of partition event (not an actual error, just info)
                print(f"[INFO] Reached end of partition {msg.partition()}")
            else:
                raise KafkaException(msg.error())
        else:
            # --- Business Logic goes here ---
            key = msg.key().decode('utf-8') if msg.key() else 'NULL'
            value = msg.value().decode('utf-8')
            partition = msg.partition()
            offset = msg.offset()
            
            print(f"Consumed -> Partition: {partition} | Offset: {offset} | Key: {key:<10} | Value: {value}")

except Exception as e:
    print(f"[ERROR] Consumer loop crashed: {e}")

finally:
    # --- 5. Graceful Cleanup ---
    print("[INFO] Closing consumer connection to the cluster...")
    consumer.close()
    print("[INFO] Shutdown complete.")
