# streaming_final_integration.py
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, DoubleType, StringType
from pyspark.sql.functions import from_json, col, current_timestamp
import mlflow.spark

# --- 1. Initialization ---
spark = SparkSession.builder \
    .appName("RealTime_Inference_Dual_Sink") \
    .config("spark.mongodb.output.uri", "mongodb://192.168.15.121:27017/ecommerce.predictions") \
    .getOrCreate()
spark.sparkContext.setLogLevel("WARN")

# --- 2. Load Model ---
run_id = "YOUR_RUN_ID_HERE" # Replace with your actual Run ID
model_uri = f"runs:/{run_id}/spark-model"
ai_model = mlflow.spark.load_model(model_uri)

# --- 3. Kafka Source ---
json_schema = StructType([
    StructField("session_duration", DoubleType(), True),
    StructField("pages_visited", DoubleType(), True)
])

raw_stream_df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "192.168.15.115:9092") \
    .option("subscribe", "ecommerce_clickstream") \
    .load()

parsed_stream_df = raw_stream_df.selectExpr("CAST(value AS STRING)") \
    .select(from_json(col("value"), json_schema).alias("data")) \
    .select("data.*") \
    .withColumn("processed_at", current_timestamp())

# Apply AI Inference
predictions_df = ai_model.transform(parsed_stream_df)

# --- 4. Function for Dual Sink (foreachBatch) ---
def save_to_dual_destination(batch_df, batch_id):
    if batch_df.count() > 0:
        print(f"[BATCH {batch_id}] Processing {batch_df.count()} records...")
        
        # A. Save to HDFS (Parquet)
        # Using append mode to build history
        batch_df.write \
            .format("parquet") \
            .mode("append") \
            .save("hdfs://namenode:9000/datalake/ecommerce_history/")
            
        # B. Save to MongoDB (JSON)
        # Stored in database 'ecommerce', collection 'predictions'
        batch_df.write \
            .format("mongodb") \
            .mode("append") \
            .save()

# --- 5. Start Streaming ---
print("[INFO] Dual-Sink Pipeline active. Listening to Kafka...")
query = predictions_df.writeStream \
    .foreachBatch(save_to_dual_destination) \
    .start()

query.awaitTermination()

