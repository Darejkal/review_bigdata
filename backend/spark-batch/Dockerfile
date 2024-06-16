FROM apache/airflow:2.9.2
RUN pip install apache-airflow-providers-apache-spark==4.8.1

USER root
RUN apt-get update 
RUN apt-get install -y openjdk-17-jdk
RUN java -version $$ \
    javac -version

RUN apt-get install -y wget
# Setup JAVA_HOME 
ENV JAVA_HOME /usr/lib/jvm/java-1.17.0-openjdk-amd64
RUN export JAVA_HOME

## Finished JAVA installation

## SPARK files and variables

ENV SPARK_HOME /usr/local/spark

# Spark submit binaries and jars (Spark binaries must be the same version of spark cluster)
RUN cd "/tmp" && \
        wget --no-verbose "https://archive.apache.org/dist/spark/spark-${SPARK_VERSION}/spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz" && \
        tar -xvzf "spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz" && \
        mkdir -p "${SPARK_HOME}/bin" && \
        mkdir -p "${SPARK_HOME}/assembly/target/scala-2.12/jars" && \
        cp -a "spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}/bin/." "${SPARK_HOME}/bin/" && \
        cp -a "spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}/jars/." "${SPARK_HOME}/assembly/target/scala-2.12/jars/" && \
        rm "spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz"

# Create SPARK_HOME env var
RUN export SPARK_HOME
ENV PATH $PATH:/usr/local/spark/bin
USER ${AIRFLOW_UID}