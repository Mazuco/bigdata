# mllib_data_prep.py
from pyspark.sql import SparkSession
from pyspark.ml.feature import VectorAssembler

# --- 1. Initialize Spark Session ---
spark = SparkSession.builder \
    .appName("MLlib_DataPreparation") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

# --- 2. Create Mock Data (Simulating the Airbnb Dataset) ---
print("[INFO] Loading mock dataset...")
data = [
    (1.0, 1.0, 170.0),
    (2.0, 1.0, 235.0),
    (1.0, 4.0, 65.0),
    (1.0, 4.0, 65.0),
    (2.0, 1.5, 785.0),
    (3.0, 2.0, 450.0),
    (1.0, 1.0, 150.0),
    (4.0, 3.0, 900.0),
    (2.0, 2.0, 300.0),
    (1.0, 1.5, 180.0)
]
columns = ["bedrooms", "bathrooms", "price"]
airbnbDF = spark.createDataFrame(data, columns)

print("\n--- Original DataFrame ---")
airbnbDF.show(5)

# --- 3. Split the Data (Train / Test) ---
# We use seed=42 to ensure reproducibility. Every time you run this, 
# the same rows will go to the training set.
print("[INFO] Splitting data into Training and Testing sets...")
trainDF, testDF = airbnbDF.randomSplit([0.8, 0.2], seed=42)

print(f"Total rows in Training Set: {trainDF.count()}")
print(f"Total rows in Testing Set: {testDF.count()}")

# --- 4. The Transformer: VectorAssembler ---
# We need to combine 'bedrooms' and 'bathrooms' into a single 'features' vector
print("\n[INFO] Applying VectorAssembler...")
vecAssembler = VectorAssembler(
    inputCols=["bedrooms", "bathrooms"], 
    outputCol="features"
)

# Apply the transformation to our training data
vecTrainDF = vecAssembler.transform(trainDF)

print("\n--- Transformed DataFrame (Ready for ML) ---")
# Select only the features and the target label (price) to verify
vecTrainDF.select("features", "price").show(truncate=False)

spark.stop()
