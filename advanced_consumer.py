# advanced_consumer.py
from confluent_kafka import Consumer, KafkaException, KafkaError
import sys
import signal

running = True

def signal_handler(sig, frame):
    """Captures Ctrl+C to stop the loop gracefully."""
    global running
    print("\n[INFO] Stop signal received. Finishing current batch...")
    running = False

signal.signal(signal.SIGINT, signal_handler)

# --- 1. Consumer Configuration (Manual Commit Enabled) ---
conf = {
    'bootstrap.servers': 'localhost:9092,localhost:9093,localhost:9094',
    'group.id': 'robust-etl-pipeline',
    'auto.offset.reset': 'earliest',
    'enable.auto.commit': False  # CRITICAL: Disabling auto-commit
}

consumer = Consumer(conf)
topic = 'cluster-topic'
consumer.subscribe([topic])

print(f"[INFO] Consumer started. Auto-commit is OFF.")
print("[INFO] Using ASYNC commits during the loop, and SYNC commit on exit.")

try:
    while running:
        # Fetching a single message (in a real scenario, we might use consume() for batches)
        msg = consumer.poll(timeout=1.0)
        
        if msg is None:
            continue
            
        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                continue
            else:
                raise KafkaException(msg.error())
        
        # --- 2. Business Logic Execution ---
        # Imagine this is where we transform the data and save it to Hadoop/Database
        key = msg.key().decode('utf-8') if msg.key() else 'NULL'
        value = msg.value().decode('utf-8')
        print(f"Processing Record -> Partition: {msg.partition()} | Offset: {msg.offset()} | Value: {value}")
        
        # --- 3. Asynchronous Commit ---
        # Once the data is safely processed/stored, we commit asynchronously for high throughput.
        # This will not block the next iteration of the loop.
        try:
            consumer.commit(message=msg, asynchronous=True)
        except Exception as e:
            # We log the async error, but we don't crash. The next async commit will overwrite it.
            print(f"[WARNING] Async commit failed for offset {msg.offset()}: {e}")

except KeyboardInterrupt:
    pass
except Exception as e:
    print(f"[ERROR] Pipeline crashed: {e}")

finally:
    # --- 4. Synchronous Commit & Cleanup ---
    print("[INFO] Exiting loop. Performing final SYNCHRONOUS commit...")
    try:
        # Without asynchronous=True, this blocks until the broker acknowledges the commit.
        # This guarantees our very last processed message is marked as read before we die.
        consumer.commit(asynchronous=False)
        print("[INFO] Final commit successful.")
    except Exception as e:
        print(f"[ERROR] Final sync commit failed: {e}")
    finally:
        print("[INFO] Closing connection to the cluster.")
        consumer.close()
