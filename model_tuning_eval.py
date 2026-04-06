# model_tuning_eval.py
from pyspark.sql import SparkSession
from pyspark.ml import Pipeline
from pyspark.ml.feature import StringIndexer, VectorAssembler
from pyspark.ml.classification import DecisionTreeClassifier
from pyspark.ml.evaluation import MulticlassClassificationEvaluator
from pyspark.ml.tuning import ParamGridBuilder, CrossValidator

# --- 1. Initialization ---
spark = SparkSession.builder \
    .appName("ML_Tuning_Evaluation") \
    .getOrCreate()
spark.sparkContext.setLogLevel("WARN")

# --- 2. Mock Data (E-commerce Clickstream) ---
print("[INFO] Generating mock clickstream data...")
data = [
    (12.0, 6.0, "Purchase"), (15.0, 8.0, "Purchase"), (2.0, 1.0, "Abandon"),
    (3.0, 2.0, "Abandon"), (25.0, 12.0, "Purchase"), (1.5, 1.0, "Abandon"),
    (10.0, 5.0, "Purchase"), (4.0, 3.0, "Abandon"), (20.0, 9.0, "Purchase"),
    (5.0, 1.0, "Abandon"), (11.0, 4.0, "Purchase"), (6.0, 2.0, "Abandon"),
    (18.0, 7.0, "Purchase"), (2.5, 1.0, "Abandon"), (22.0, 10.0, "Purchase"),
    (3.5, 1.0, "Abandon"), (14.0, 5.0, "Purchase"), (1.0, 1.0, "Abandon")
]
clickstreamDF = spark.createDataFrame(data, ["session_duration", "pages_visited", "action"])

# Split into Train (for tuning) and Test (for the absolute final evaluation)
trainDF, testDF = clickstreamDF.randomSplit([0.8, 0.2], seed=42)

# --- 3. Base Pipeline Stages ---
labelIndexer = StringIndexer(inputCol="action", outputCol="label")
assembler = VectorAssembler(inputCols=["session_duration", "pages_visited"], outputCol="features")

# The Classifier (We do NOT set maxDepth here, we will tune it)
dt = DecisionTreeClassifier(labelCol="label", featuresCol="features", seed=42)

# --- 4. The Evaluator ---
# We tell Spark how to score the models. We will use 'accuracy' (percentage of correct guesses).
evaluator = MulticlassClassificationEvaluator(
    labelCol="label", 
    predictionCol="prediction", 
    metricName="accuracy"
)

# --- 5. The Grid Search (Hyperparameter Tuning) ---
# We tell Spark to test 3 different max depths for the tree
print("[INFO] Building Parameter Grid...")
paramGrid = ParamGridBuilder() \
    .addGrid(dt.maxDepth, [2, 4, 6]) \
    .build()

# --- 6. The Cross-Validator ---
# This is the "robot". It takes the algorithm, the evaluator, and the grid,
# and performs the K-Fold rotation (numFolds=3) to find the absolute best setting.
cv = CrossValidator(
    estimator=dt,
    evaluator=evaluator,
    estimatorParamMaps=paramGrid,
    numFolds=3,
    parallelism=2 # Speed up training by running models in parallel
)

# --- 7. The Ultimate Pipeline ---
# BEST PRACTICE from the book: Put the CrossValidator INSIDE the pipeline.
# This prevents the StringIndexer from running 9 times pointlessly.
pipeline = Pipeline(stages=[labelIndexer, assembler, cv])

print("[INFO] Training multiple models via Cross-Validation (This may take a moment)...")
# This single .fit() will train 9 different trees behind the scenes!
pipelineModel = pipeline.fit(trainDF)

# --- 8. Final Evaluation ---
print("[INFO] Best model selected automatically. Making predictions on Final Test Data...")
predictions = pipelineModel.transform(testDF)

# Get the final score using our evaluator
accuracy = evaluator.evaluate(predictions)
print(f"\n======================================")
print(f" FINAL MODEL ACCURACY: {accuracy * 100:.2f}%")
print(f"======================================\n")

# To satisfy our curiosity, what was the best maxDepth it found?
# We extract the CV model (stage 2), then get its bestModel
best_tree_model = pipelineModel.stages[2].bestModel
print(f"[TUNING RESULT] The best Tree Depth found by the CrossValidator was: {best_tree_model.getMaxDepth()}")

spark.stop()

