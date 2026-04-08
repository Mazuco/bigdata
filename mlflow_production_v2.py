import mlflow
import mlflow.spark
from pyspark.sql import SparkSession
from pyspark.ml import Pipeline
from pyspark.ml.feature import StringIndexer, VectorAssembler
from pyspark.ml.classification import DecisionTreeClassifier
from pyspark.ml.evaluation import MulticlassClassificationEvaluator

# --- 1. Initialization ---
spark = SparkSession.builder \
    .appName("MLflow_Production_Pipeline") \
    .getOrCreate()
spark.sparkContext.setLogLevel("WARN")

mlflow.set_tracking_uri("http://192.168.15.72:5000")

# --- 2. Mock Data (E-commerce Clickstream) ---
data = [
    (12.0, 6.0, "Purchase"), (15.0, 8.0, "Purchase"), (2.0, 1.0, "Abandon"),
    (3.0, 2.0, "Abandon"), (25.0, 12.0, "Purchase"), (1.5, 1.0, "Abandon"),
    (10.0, 5.0, "Purchase"), (4.0, 3.0, "Abandon"), (20.0, 9.0, "Purchase"),
    (5.0, 1.0, "Abandon"), (11.0, 4.0, "Purchase"), (6.0, 2.0, "Abandon")
]
clickstreamDF = spark.createDataFrame(data, ["session_duration", "pages_visited", "action"])
trainDF, testDF = clickstreamDF.randomSplit([0.8, 0.2], seed=42)

# --- 3. Pipeline Setup ---
labelIndexer = StringIndexer(inputCol="action", outputCol="label")
assembler = VectorAssembler(inputCols=["session_duration", "pages_visited"], outputCol="features")

# Let's say we already know depth=2 is the best from our previous tuning class
chosen_depth = 2
dt = DecisionTreeClassifier(labelCol="label", featuresCol="features", maxDepth=chosen_depth, seed=42)

pipeline = Pipeline(stages=[labelIndexer, assembler, dt])

evaluator = MulticlassClassificationEvaluator(labelCol="label", predictionCol="prediction", metricName="accuracy")

# ==========================================
# 4. THE MLFLOW TRACKING BLOCK
# ==========================================
print("[INFO] Starting MLflow Tracking Run...")

# Set an experiment name to group our runs
mlflow.set_experiment("Ecommerce_Purchase_Predictor")

with mlflow.start_run(run_name="DecisionTree_V1"):
    
    # A. Log Parameters (The settings we chose)
    print(" -> Logging parameters...")
    mlflow.log_param("max_depth", chosen_depth)
    mlflow.log_param("algorithm", "DecisionTree")
    mlflow.log_param("dataset_size", clickstreamDF.count())

    # B. Train the Model
    print(" -> Training the model...")
    pipelineModel = pipeline.fit(trainDF)

    # C. Evaluate and Log Metrics (The test scores)
    print(" -> Evaluating model...")
    predictions = pipelineModel.transform(testDF)
    accuracy = evaluator.evaluate(predictions)
    
    mlflow.log_metric("test_accuracy", accuracy)
    print(f"    * Accuracy Score: {accuracy * 100:.2f}%")

    # D. SAVE THE MODEL
    # This is the most important part. It exports the Pipeline to the MLflow format.
    print(" -> Saving model artifacts to disk...")
    mlflow.spark.log_model(pipelineModel, "spark-model")

print("\n[SUCCESS] Run completed and logged to MLflow locally in the 'mlruns' folder.")

spark.stop()
