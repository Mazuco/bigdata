# stream_to_hdfs.py
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json
from pyspark.sql.types import StructType, StructField, StringType

# --- 1. Initialize Spark Session ---
spark = SparkSession.builder \
    .appName("KafkaToHdfsDataLake") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

# --- 2. Define Schema ---
json_schema = StructType([
    StructField("event_id", StringType(), True),
    StructField("source", StringType(), True),
    StructField("timestamp", StringType(), True)
])

# --- 3. Read Stream from Kafka ---
kafka_df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "192.168.15.115:9092,192.168.15.115:9093,192.168.15.115:9094") \
    .option("subscribe", "cluster-topic") \
    .option("startingOffsets", "earliest") \
    .load()

# --- 4. Transform Data ---
parsed_df = kafka_df.selectExpr("CAST(value AS STRING) as json_string") \
    .select(from_json(col("json_string"), json_schema).alias("data")) \
    .select("data.*")

# --- 5. Output Stream to Hadoop (HDFS) ---
print("[INFO] Starting stream to HDFS Data Lake...")

# Define the HDFS paths
HDFS_TARGET_DIR = "/datalake/silver/web_events"
HDFS_CHECKPOINT_DIR = "/datalake/silver/web_events/_checkpoints"

query = parsed_df.writeStream \
    .format("parquet") \
    .outputMode("append") \
    .option("path", HDFS_TARGET_DIR) \
    .option("checkpointLocation", HDFS_CHECKPOINT_DIR) \
    .start()

query.awaitTermination()
