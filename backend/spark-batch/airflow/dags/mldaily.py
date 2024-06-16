from airflow import DAG
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from datetime import datetime
with DAG("ml_run_daily",
    start_date=datetime(2024,6,16),
    schedule="@daily") as dag:
    submit_job=SparkSubmitOperator(
        task_id='submit_job',
        application="/opt/airflow/include/spark-batch.py",
        conn_id="http://spark-master:7077",
        total_executor_cores="1",
    )