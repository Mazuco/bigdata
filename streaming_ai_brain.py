#streaming_ai_brain.py
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, DoubleType, StringType
from pyspark.sql.functions import from_json, col
import mlflow.spark
import mlflow

# Aponta o Spark para o servidor central do MLflow
# (Se o contêiner do MLflow estiver na mesma rede Docker do Spark, você pode usar o nome do contêiner)
mlflow.set_tracking_uri("http://mlflow:5000")

# --- 1. Initialization ---
spark = SparkSession.builder \
    .appName("Kafka_MLflow_RealTime_Inference") \
    .getOrCreate()
spark.sparkContext.setLogLevel("WARN")

# --- 2. Load the Pre-Trained Model from MLflow ---
print("[INFO] Loading MLflow Model into memory...")
# IMPORTANT: Replace the 'YOUR_RUN_ID_HERE' with the actual Run ID from the MLflow UI
run_id = "YOUR_RUN_ID_HERE" 
model_uri = f"runs:/{run_id}/spark-model"

# Load the entire pipeline (Assembler + Decision Tree)
ai_model = mlflow.spark.load_model(model_uri)

# --- 3. Kafka Source Setup ---
print("[INFO] Connecting to Kafka Stream...")
kafka_topic = "ecommerce_clickstream"
kafka_bootstrap_servers = "192.168.15.115:9092"

raw_stream_df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", kafka_bootstrap_servers) \
    .option("subscribe", kafka_topic) \
    .option("startingOffsets", "latest") \
    .load()

# --- 4. Parsing the incoming JSON ---
# We expect Kafka messages to look like: {"session_duration": 4.5, "pages_visited": 3.0}
json_schema = StructType([
    StructField("session_duration", DoubleType(), True),
    StructField("pages_visited", DoubleType(), True)
])

# Convert the Kafka 'value' (binary) to String, then parse JSON into actual columns
parsed_stream_df = raw_stream_df.selectExpr("CAST(value AS STRING)") \
    .select(from_json(col("value"), json_schema).alias("data")) \
    .select("data.*")

# --- 5. Real-Time Inference (The Brain) ---
print("[INFO] Applying AI Model to the Stream...")
# The model.transform() method works seamlessly on Streaming DataFrames!
predictions_stream_df = ai_model.transform(parsed_stream_df)

# We just want to see the original data and the AI's prediction
final_output_df = predictions_stream_df.select(
    "session_duration", 
    "pages_visited", 
    "prediction" 
)

# --- 6. Output Sink (Console for testing) ---
print("[INFO] Starting the Streaming Query. Waiting for events...")
query = final_output_df.writeStream \
    .outputMode("append") \
    .format("console") \
    .option("truncate", "false") \
    .trigger(processingTime="2 seconds") \
    .start()

query.awaitTermination()
