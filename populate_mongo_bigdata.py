# populate_mongo_bigdata.py
import random
import uuid
from datetime import datetime, timedelta
from pymongo import MongoClient

# Connect to local MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["ecommerce_db"]
collection = db["web_traffic_logs"]

# Clear existing data for a fresh start (optional, remove if you want to keep appending)
print("Clearing old data...")
collection.delete_many({})

# Configuration for data generation
TOTAL_RECORDS = 10000000  # Change to 10000000 (10 million) to reach ~2GB of data
BATCH_SIZE = 100000       # Inserts 10,000 records at a time for performance

event_types = ["page_view", "add_to_cart", "remove_from_cart", "checkout", "purchase", "login"]
device_types = ["mobile_ios", "mobile_android", "desktop_windows", "desktop_mac", "tablet"]
categories = ["electronics", "clothing", "home_appliances", "books", "toys"]

print(f"Starting to generate {TOTAL_RECORDS} records. This might take a while...")

logs_batch = []
records_inserted = 0

for i in range(TOTAL_RECORDS):
    # Generate random timestamp within the last 30 days
    random_days_ago = random.randint(0, 30)
    random_minutes_ago = random.randint(0, 1440)
    event_time = datetime.now() - timedelta(days=random_days_ago, minutes=random_minutes_ago)
    
    log_entry = {
        "event_id": str(uuid.uuid4()),
        "timestamp": event_time,
        "user_id": random.randint(1000, 99999),
        "session_id": str(uuid.uuid4())[:8],
        "event_type": random.choice(event_types),
        "device": random.choice(device_types),
        "product_category": random.choice(categories),
        "processing_time_ms": random.randint(10, 500)
    }
    
    logs_batch.append(log_entry)
    
    # Insert batch into MongoDB and clear the list
    if len(logs_batch) == BATCH_SIZE:
        collection.insert_many(logs_batch)
        records_inserted += BATCH_SIZE
        logs_batch = []
        
        # Print progress
        if records_inserted % 100000 == 0:
            print(f"Progress: {records_inserted} / {TOTAL_RECORDS} records inserted...")

# Insert any remaining records
if logs_batch:
    collection.insert_many(logs_batch)
    print(f"Final progress: {TOTAL_RECORDS} / {TOTAL_RECORDS} records inserted.")

print("Data generation complete!")
