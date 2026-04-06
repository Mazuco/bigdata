# first_ml_pipeline.py
from pyspark.sql import SparkSession
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.regression import LinearRegression
from pyspark.ml import Pipeline

# --- 1. Initialization ---
spark = SparkSession.builder \
    .appName("ML_Estimators_Pipelines") \
    .getOrCreate()
spark.sparkContext.setLogLevel("WARN")

# --- 2. Mock Data (Simulating a real property dataset) ---
data = [
    (1.0, 1.0, 170.0), (2.0, 1.0, 235.0), (1.0, 4.0, 65.0), 
    (1.0, 4.0, 65.0), (2.0, 1.5, 785.0), (3.0, 2.0, 450.0), 
    (1.0, 1.0, 150.0), (4.0, 3.0, 900.0), (2.0, 2.0, 300.0), 
    (1.0, 1.5, 180.0), (3.0, 3.0, 700.0), (5.0, 4.0, 1200.0)
]
airbnbDF = spark.createDataFrame(data, ["bedrooms", "bathrooms", "price"])

print("[INFO] Splitting Dataset (80% Train, 20% Test)...")
trainDF, testDF = airbnbDF.randomSplit([0.8, 0.2], seed=42)

# --- 3. Define the Stages of our Machine Learning Pipeline ---

# Stage 1: The Transformer
# Merges the input variables into a single mathematical vector
vecAssembler = VectorAssembler(
    inputCols=["bedrooms", "bathrooms"], 
    outputCol="features"
)

# Stage 2: The Estimator (The Algorithm)
# We tell the algorithm where the input vector is, and what it needs to predict (label)
lr = LinearRegression(featuresCol="features", labelCol="price")

# Create the Pipeline connecting Stage 1 and Stage 2
print("[INFO] Building and Fitting the ML Pipeline...")
pipeline = Pipeline(stages=[vecAssembler, lr])

# --- 4. Training (The .fit() phase) ---
# This single command applies the assembler and trains the model!
# It returns a PipelineModel (which acts as a Transformer)
pipelineModel = pipeline.fit(trainDF)

# (Optional Curiosity: Let's extract the mathematical formula the model learned)
# We need to access the second stage [1] of the pipeline to get the LinearRegression model
lr_trained_model = pipelineModel.stages[1]
print(f"\n[MODEL MATH] Formula Learned: Price = ({round(lr_trained_model.coefficients[0],2)} * bedrooms) + ({round(lr_trained_model.coefficients[1],2)} * bathrooms) + {round(lr_trained_model.intercept,2)}\n")

# --- 5. Predicting (The .transform() phase) ---
print("[INFO] Applying the trained model to the unseen Test Data...")
# We use .transform() on the PipelineModel, and it automatically applies 
# the VectorAssembler AND the predictions to the Test Set!
predictionsDF = pipelineModel.transform(testDF)

# Let's see the magic: The real price vs the model's prediction
predictionsDF.select("bedrooms", "bathrooms", "features", "price", "prediction").show(truncate=False)

spark.stop()
