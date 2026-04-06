# ecommerce_classification.py
from pyspark.sql import SparkSession
from pyspark.ml import Pipeline
from pyspark.ml.feature import StringIndexer, VectorAssembler
from pyspark.ml.classification import DecisionTreeClassifier

# --- 1. Initialization ---
spark = SparkSession.builder \
    .appName("Ecommerce_Purchase_Prediction") \
    .getOrCreate()
spark.sparkContext.setLogLevel("WARN")

# --- 2. Mock E-commerce Clickstream Data ---
# Columns: [Session Duration (mins), Pages Visited, Action (Label)]
data = [
    (12.0, 6.0, "Purchase"), (15.0, 8.0, "Purchase"),
    (2.0,  1.0, "Abandon"),  (3.0,  2.0, "Abandon"),
    (25.0, 12.0,"Purchase"), (1.5,  1.0, "Abandon"),
    (10.0, 5.0, "Purchase"), (4.0,  3.0, "Abandon"),
    (20.0, 9.0, "Purchase"), (5.0,  1.0, "Abandon")
]
columns = ["session_duration", "pages_visited", "action"]
clickstreamDF = spark.createDataFrame(data, columns)

print("[INFO] Dataset Preview (Clickstream Data):")
clickstreamDF.show()

# --- 3. Building the Pipeline Stages ---

# Stage 1: Convert text label "action" to a numeric index
labelIndexer = StringIndexer(inputCol="action", outputCol="label")

# Stage 2: Assemble features (duration and pages) into a mathematical vector
assembler = VectorAssembler(
    inputCols=["session_duration", "pages_visited"], 
    outputCol="features"
)

# Stage 3: The Classifier (Decision Tree)
dt = DecisionTreeClassifier(labelCol="label", featuresCol="features")

# --- 4. Creating and Training the Pipeline ---
pipeline = Pipeline(stages=[labelIndexer, assembler, dt])

print("[INFO] Splitting data and training model...")
trainDF, testDF = clickstreamDF.randomSplit([0.7, 0.3], seed=42)

model = pipeline.fit(trainDF)

# --- 5. Predictions ---
print("[INFO] Making predictions on unseen test data...")
predictions = model.transform(testDF)

# Display results
# Note: "label" is the numeric mapping of "action". "prediction" is the model's guess.
predictions.select("session_duration", "pages_visited", "action", "label", "prediction").show()

# --- 6. Exporting the Tree Rules ---
treeModel = model.stages[2]
print("\n[LOGIC] Decision Tree Rules Extracted by the Algorithm:")
print(treeModel.toDebugString)

spark.stop()
