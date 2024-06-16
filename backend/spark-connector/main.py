import os
from pyspark.sql import SparkSession, Row,DataFrame
import pyspark.sql.functions as F
from pyspark.sql.types import StructType,StructField,StringType,ArrayType,DoubleType,TimestampType,IntegerType
from pyspark.sql.window import Window
from sentence_transformers import SentenceTransformer
import sklearn
from pyspark.ml.feature import Tokenizer, StopWordsRemover
import pandas as pd
import numpy as np
from datetime import datetime,timezone,timedelta
KAFKA_ADDRESS=os.environ['REDPANDA_ADDR']
SPARK_MASTER_ADDRESS=os.environ["SPARK_ADDR"]

spark:SparkSession = SparkSession.builder.master("spark://"+SPARK_MASTER_ADDRESS).getOrCreate()
spark.conf.set("spark.sql.session.timeZone", "UTC")
spark.sparkContext.setCheckpointDir("hdfs://namenode:8020/checkpoints")
preprocessed_df=spark.readStream.format("kafka")\
    .option("kafka.bootstrap.servers",KAFKA_ADDRESS)\
    .option("subscribe", "committed-raw-input")\
    .option("checkpointLocation", "hdfs://namenode:8020/checkpoints")\
    .load()
preprocessed_df.printSchema()
fields={
    "content":StringType(),
    "rating":IntegerType(),
    "timeline":StructType([StructField(
       "review_created_date",StringType()
    )])
}
schema=StructType([StructField(k,v) for k,v in fields.items()])
@F.udf(returnType=StringType())
def formatDate(x):
    return x.strftime('%Y-%m-%d')
@F.udf(returnType=TimestampType())
def stringToDate(x):
    if(x):
        dt_utc = datetime.strptime(x, "%Y-%m-%d %H:%M:%S")
        hanoi_tz = timezone(timedelta(hours=7))
        dt_hanoi = dt_utc.astimezone(hanoi_tz)
        return dt_hanoi
    return None
df=preprocessed_df\
    .select(F.from_json(F.col("value").cast("string"),schema).alias("parsed_value"),F.col("timestamp"))\
    .select(F.col("parsed_value.*"),formatDate("timestamp").alias("time"),F.col("timestamp"))\
    .select(F.col("timeline.*"),"content","rating",formatDate("timestamp").alias("time"),F.col("timestamp"))
df=df.withColumn("review_created_date",stringToDate("review_created_date"))
df.writeStream.format("console")\
            .outputMode("append")\
            .start()

newdf=df.filter("content!=''").na.drop()
newdf.withColumn("value",F.struct(F.col("rating"),F.col("content"),F.col("time")))\
    .writeStream.outputMode("append")\
    .format("parquet")\
    .option("checkpointLocation", "hdfs://namenode:8020/checkpoints")\
    .partitionBy("time")\
    .start("hdfs://namenode:8020/data/total")
tokenizer = Tokenizer(inputCol='content', outputCol='words_token')
df_words_token = tokenizer.transform(newdf)
df_final_words = df_words_token.where(F.size('words_token')>=3)
finaldf=df_final_words
finaldf.select(F.to_json(F.struct(F.col("words_token"), F.col("content"),F.col("time"),F.col("timestamp"))).alias("value"))\
    .writeStream\
    .outputMode("append").format("kafka")\
    .option("kafka.bootstrap.servers",KAFKA_ADDRESS)\
    .option("topic", "spark-output")\
    .option("checkpointLocation", "hdfs://namenode:8020/checkpoints")\
    .start()
print("All set")

while len(spark.streams.active) > 0:
  spark.streams.resetTerminated()
  spark.streams.awaitAnyTermination()
