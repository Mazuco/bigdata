# tuned_consumer.py
from confluent_kafka import Consumer, KafkaException, KafkaError
import sys
import signal
import time

running = True

def signal_handler(sig, frame):
    """Graceful shutdown signal handler."""
    global running
    print("\n[INFO] Graceful shutdown initiated...")
    running = False

signal.signal(signal.SIGINT, signal_handler)

# ==========================================
# Architecting the Tuned Configuration
# ==========================================
conf = {
    'bootstrap.servers': 'localhost:9092,localhost:9093,localhost:9094',
    'group.id': 'heavy-etl-group',
    'client.id': 'tuned-python-consumer-01',
    
    # 1. Behavior when no valid offset is found
    'auto.offset.reset': 'earliest',
    
    # 2. Disable Auto-Commit for Zero Data Loss (from previous lesson)
    'enable.auto.commit': False,
    
    # 3. Network & Throughput Tuning
    'fetch.min.bytes': 1048576,        # Request at least 1MB of data...
    'fetch.wait.max.ms': 500,          # ...or wait a maximum of 500ms before returning what's available
    
    # 4. Stability Tuning for Heavy Processing
    'max.poll.interval.ms': 300000,    # Allow up to 5 minutes to process a batch before assuming the app is dead
    'session.timeout.ms': 10000,       # Broker connection timeout (10 seconds)
    'heartbeat.interval.ms': 3000,     # Send network heartbeat every 3 seconds
    
    # 5. Cooperative Rebalancing (Modern standard for high availability)
    'partition.assignment.strategy': 'cooperative-sticky'
}

consumer = Consumer(conf)
topic = 'cluster-topic'
consumer.subscribe([topic])

print(f"[INFO] Tuned Consumer started. Polling topic '{topic}'...")

try:
    while running:
        # We increase the poll timeout slightly since we are waiting for larger batches
        msg = consumer.poll(timeout=2.0)
        
        if msg is None:
            continue
            
        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                continue
            else:
                raise KafkaException(msg.error())
        
        # --- Heavy Data Processing Simulation ---
        key = msg.key().decode('utf-8') if msg.key() else 'NULL'
        value = msg.value().decode('utf-8')
        
        print(f"Processing -> Partition: {msg.partition()} | Offset: {msg.offset()} | Value: {value}")
        
        # Simulating a heavy ETL task (e.g., writing to a Data Lake)
        # Because we configured max.poll.interval.ms to 5 minutes, this sleep is perfectly safe.
        time.sleep(0.1) 
        
        # Async commit for maximum throughput during the loop
        try:
            consumer.commit(message=msg, asynchronous=True)
        except Exception as e:
            pass # Ignore async errors, next commit will override

except KeyboardInterrupt:
    pass
except Exception as e:
    print(f"[ERROR] Critical failure: {e}")

finally:
    print("[INFO] Performing final synchronous commit to secure state...")
    try:
        consumer.commit(asynchronous=False)
    except Exception as e:
        print(f"[ERROR] Sync commit failed during shutdown: {e}")
    finally:
        consumer.close()
        print("[INFO] Consumer safely closed.")
