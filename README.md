# LAKEHOUSE

## IT ALL BEGINS WITH...
Let's start to build a lakehouse, containing:
a. Apache Spark
b. Apache Airflow
c. Minio


### Apache Spark

We will use Spark to process the parquet files inside medal folders of the lake.

#### First way:

Using Dockerfile to start a container with Spark (/spark/docker-compose-way). To build the Docker, run this command:
```
docker build -t my-apache-spark:3.5.1 .
```

After building the image, start the docker compose:
```
docker compose up
```

Access your master container and submit a spark job:
```
docker exec -i -t [CONTAINER ID] /bin/bash

cd /opt/spark/bin

./spark-submit --master spark://0.0.0.0:7077 --name spark-pi --class org.apache.spark.examples.SparkPi  local:///opt/spark/examples/jars/spark-examples_2.12-3.5.1.jar 100

```


### Apache Airflow

Airflow will orchestrate the steps of our ELT.


#Minio

It will be the bucket of our parquet files.