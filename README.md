# LAKEHOUSE

## IT ALL BEGINS WITH...
Let's start to build a lakehouse, containing:

a. Apache Spark 

b. Apache Airflow

c. Minio


### Apache Spark

We will use Spark to process the parquet files inside medal folders of the lake. To configure all our lakehouse, I'll use helm charts and minikube to start a k8s cluster in docker. I'm with a Macbook, sou I've already installed brew and use this commands to install minikube and helm:

```

brew install helm

brew install minikube

```

After that and having a Docker Desktop installed, start a cluster with this command:
```

minikube start --memory 9000 --cpus 3

```

Then, to install SPARK, let's run this helm commands:
```

helm install spark oci://registry-1.docker.io/bitnamicharts/spark --version 9.2.5 --create-namespace --namespace=lakehouse --set worker.replicaCount=3 --set worker.resources.memory=2g --set service.type=NodePort

```

To execute a test, run a spark-submit in the master pod:
```

kubectl exec -it -n lakehouse spark-master-0 -- ./bin/spark-submit \
 --class org.apache.spark.examples.SparkPi \
 --master spark://spark-master-0:7077 \
 ./examples/jars/spark-examples_2.12-3.5.1.jar 1000

```

With minikube, we can expose the ports of spark master service to access the application and the UI locally:
```

minikube service spark-master-svc --url -n lakehouse

```

Just copy the URLs and access it from your browser or use it as a spark master at your local application!


### Apache Airflow

Airflow will orchestrate the steps of our ELT.

```

helm repo add apache-airflow https://airflow.apache.org

```

To install an airflow instance, run this helm command (you need a values.yaml file with the manifest of the installation):
```

helm install airflow apache-airflow/airflow --namespace lakehouse -f values.yaml --version 1.13.1

````

To enter in the Airflow webserver, we need to make a port-forward in kubectl to the webserver port:
```

kubectl port-forward svc/airflow-webserver 8080:8080 --namespace airflow

```


### Minio

The parquet files of our lakehouse will be stored in buckets inside minio. To install minio in k8s, start downloading the repo:

```

helm repo add minio-operator https://operator.min.io

```

Then, install the operator:
```

helm install --namespace lakehouse operator minio-operator/operator --version 5.0.10

```

To grant access to the console, we need to use a JWT secret:
```

kubectl get secret/console-sa-secret -n lakehouse -o json | jq -r ".data.token" | base64 -d

```

Let's access the console of minio:
```

kubectl port-forward svc/console -n lakehouse 9090:9090

```

Use the jwt to login and create a tenant via UI, then it's ready to work!

When editing the new tenant, I needed to change the CPU capacity of it to "250m" in the YAML file, and in Security tab I needed to disable TLS option.


### Jupyter

To develop and test yours python scripts, you can deploy a Jupyterhub service that can connect to the other services. To install it, we can begin with:
```

helm repo add jupyterhub https://hub.jupyter.org/helm-chart/

```

Then install via helm (the config.yaml file is in jupyter folder):
```

helm install jupyter jupyterhub/jupyterhub --namespace lakehouse --values config.yaml

```

After installed, run a port-forward to get access to the hub:
```

kubectl --namespace=lakehouse port-forward service/proxy-public 54345:80

```


Some commands that help me in the Devops tasks:

- To list the pods:
```
kubectl get pods -n lakehouse
```

- To check if the port is available:
```
kubectl exec -it -n lakehouse spark-master-0 -- netstat -nltp|grep 7077
```
OR
```
kubectl get pod spark-worker-0 --template='{{(index (index .spec.containers 0).ports 0).containerPort}}{{"\n"}}' -n lakehouse
```


kubectl cp tmp/data.json lakehouse/spark-master-0:/tmp/

kubectl -n lakehouse exec --stdin --tty spark-master-0 -- /bin/bash 

kubectl -n lakehouse exec --stdin --tty proxy-public -- /bin/bash

apt-get install openjdk-8-jdk-headless -qq    
