# read_kafka_stream.py
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json
from pyspark.sql.types import StructType, StructField, StringType

# --- 1. Initialize Spark Session ---
# This creates the engine that will distribute our workload
spark = SparkSession.builder \
    .appName("KafkaToConsoleStream") \
    .getOrCreate()

# Suppress overly verbose Spark logs (keep only WARN and ERROR)
spark.sparkContext.setLogLevel("WARN")

print("[INFO] Spark Session Initialized.")

# --- 2. Define the Expected Schema ---
# We must tell Spark the format of the JSON the Airflow producer is sending
json_schema = StructType([
    StructField("event_id", StringType(), True),
    StructField("source", StringType(), True),
    StructField("timestamp", StringType(), True)
])

# --- 3. Read the Stream from the Remote Kafka Cluster ---
print("[INFO] Connecting to Kafka cluster at 192.168.15.115...")

kafka_df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "192.168.15.115:9092,192.168.15.115:9093,192.168.15.115:9094") \
    .option("subscribe", "cluster-topic") \
    .option("startingOffsets", "earliest") \
    .load()

# --- 4. Transform the Data ---
# Kafka stores values as raw binary. We need to cast it to a String, 
# and then use the from_json function to parse it into distinct columns.
parsed_df = kafka_df.selectExpr("CAST(value AS STRING) as json_string") \
    .select(from_json(col("json_string"), json_schema).alias("data")) \
    .select("data.*") # Unpack the JSON properties into actual DataFrame columns

# --- 5. Output the Stream to the Console ---
print("[INFO] Starting the streaming query...")

query = parsed_df.writeStream \
    .outputMode("append") \
    .format("console") \
    .option("truncate", False) \
    .start()

# Keep the application running indefinitely to wait for new data
query.awaitTermination()
