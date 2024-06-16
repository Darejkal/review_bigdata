from pyspark.sql import SparkSession
from pyspark.ml.feature import Tokenizer
from pyspark.ml.feature import StopWordsRemover
from pyspark.ml.feature import HashingTF, IDF
from pyspark.ml import Pipeline
from pyspark.sql.functions import col
import os
from datetime import datetime
TODAY=datetime.today().strftime('%Y-%m-%d')
# SPARK_MASTER_ADDRESS=os.environ["SPARK_ADDR"]

spark:SparkSession = SparkSession.builder.appName("MLApp").getOrCreate()
spark.sparkContext.setCheckpointDir("hdfs://namenode:8020/checkpoints")
df = spark.read.parquet("hdfs://namenode:8020/data/"+TODAY)

df.printSchema()

df_select = df.select(
    df.rating.cast("int").alias("rating"),
    df.content
)
df_filterd=df_select.filter("content!=''").na.drop()

tokenizer = Tokenizer(inputCol = "content", outputCol = "review_words")
wordsDF = tokenizer.transform(df_filterd)

# remover = StopWordsRemover(inputCol = "review_words", outputCol = "filtered")
# wordsDF2 = remover.transform(wordsDF)

hashingTF = HashingTF(inputCol = "review_words", outputCol = "TF", numFeatures = 10000)
wordsDF3 = hashingTF.transform(wordsDF)

idf = IDF(inputCol="TF", outputCol="features", minDocFreq = 5)   # minDocFreq: remove sparse terms
idfModel = idf.fit(wordsDF3)
# wordsDF4 = idfModel.transform(wordsDF3)

(training, test) = df_filterd.randomSplit([0.7, 0.3], seed = 100)


minor = training.where(col("rating") < 3)
countMinor = minor.groupBy("rating").count()

major = training.where(col("rating") >=3)
countMajor = major.groupBy("rating").count()

underSampling = major.sample(withReplacement = False, fraction = 0.33, seed = 100)
countUnderS = underSampling.groupBy("rating").count()
df_concat = minor.union(underSampling)
train = df_concat.withColumnRenamed("rating", "label")
countLabel = train.groupBy("label").count()

# LogisticRegression

from pyspark.ml.classification import LogisticRegression
from pyspark.ml.evaluation import BinaryClassificationEvaluator
from pyspark.ml.tuning import CrossValidator, ParamGridBuilder

lr = LogisticRegression(maxIter=20)

pipeline = Pipeline(stages=[tokenizer, hashingTF, idfModel, lr])

paramGrid = ParamGridBuilder() \
    .addGrid(hashingTF.numFeatures, [10, 50]) \
    .addGrid(lr.regParam, [0.1, 0.01]) \
    .build()

crossval = CrossValidator(estimator=pipeline,
                          estimatorParamMaps=paramGrid,
                          evaluator=BinaryClassificationEvaluator(),
                          numFolds=4) 

cvModel = crossval.fit(train)

prediction = cvModel.transform(test)
selected = prediction.select("content", "rating", "probability", "prediction").take(5)
for row in selected:
    print(row)

evaluator = BinaryClassificationEvaluator(
    labelCol="rating")
Accuracy = evaluator.evaluate(prediction)
print("Accuracy for Logistic Repression: " + str(Accuracy))
cvModel.save("hdfs://namenode:8020/data/logistics/"+TODAY)

from pyspark.ml import Pipeline
from pyspark.ml.classification import RandomForestClassifier
from pyspark.ml.feature import IndexToString, StringIndexer, VectorIndexer
from pyspark.ml.evaluation import BinaryClassificationEvaluator
from pyspark.ml.evaluation import MulticlassClassificationEvaluator
from pyspark.ml.tuning import CrossValidator, ParamGridBuilder

rf = RandomForestClassifier(numTrees=15)

pipeline = Pipeline(stages=[tokenizer, hashingTF, idfModel, rf])

paramGrid = ParamGridBuilder() \
    .addGrid(hashingTF.numFeatures, [10, 50]) \
    .addGrid(rf.maxDepth, [5, 15]) \
    .build()

# Random Forest

crossval = CrossValidator(estimator = pipeline,
                          estimatorParamMaps = paramGrid,
                          evaluator = BinaryClassificationEvaluator(),
                          numFolds = 5)

cvModel = crossval.fit(train)

prediction = cvModel.transform(test)
selected = prediction.select("content", "rating", "probability", "prediction").take(5)

for row in selected:
    print(row)

evaluator = BinaryClassificationEvaluator(
    labelCol="rating")
Accuracy_RF = evaluator.evaluate(prediction)

print("Accuracy for Random Forest: " + str(Accuracy_RF))

cvModel.save("hdfs://namenode:8020/data/randomforests/"+TODAY)

# Gradient-boosted tree classifier

from pyspark.ml import Pipeline
from pyspark.ml.classification import GBTClassifier

gbt = GBTClassifier(maxIter=10)
pipeline = Pipeline(stages=[tokenizer, hashingTF, idfModel, gbt])

paramGrid = ParamGridBuilder() \
    .addGrid(hashingTF.numFeatures, [10, 50]) \
    .build()

crossval = CrossValidator(estimator = pipeline,
                          estimatorParamMaps = paramGrid,
                          evaluator = BinaryClassificationEvaluator(),
                          numFolds = 3)


cvModel = crossval.fit(train)

predictions = cvModel.transform(test)

selected_GBT = predictions.select("content", "rating", "probability", "prediction").take(5)

for row in selected_GBT:
    print(row)

evaluator_GBT = BinaryClassificationEvaluator(
    labelCol="rating")
Accuracy_GBT = evaluator_GBT.evaluate(predictions)
print("Accuracy for Gradient-boosted tree classifier: " + str(Accuracy_GBT))

cvModel.save("hdfs://namenode:8020/data/gradientboosted/"+TODAY)