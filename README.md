# LAKEHOUSE

## IT ALL BEGINS WITH...
Let's start to build a lakehouse, containing:

a. Apache Spark 

b. Apache Airflow

c. Minio


### Apache Spark

We will use Spark to process the parquet files inside medal folders of the lake. To configure the spark, I'm following the tutorial from Safouane Ennasser:

https://medium.com/@SaphE/testing-apache-spark-locally-docker-compose-and-kubernetes-deployment-94d35a54f222

https://medium.com/@SaphE/deploying-apache-spark-on-a-local-kubernetes-cluster-a-comprehensive-guide-d4a59c6b1204

https://medium.com/@SaphE/deploying-apache-spark-on-kubernetes-using-helm-charts-simplified-cluster-management-and-ee5e4f2264fd

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

#### Second way:

Using a local kubernetes cluster, we need to:

Install KIND and Kubectl:
```

https://github.com/kubernetes-sigs/kind/releases
https://kubernetes.io/docs/tasks/tools/#kubectl

```

Create a cluster:
```

kind create cluster

```

Download Spark and extract file to destination folder:
```

https://spark.apache.org/downloads.html

```

Build a image using this command in SPARK_HOME directory:
```

./bin/docker-image-tool.sh -t our-own-apache-spark-kb8 build

```

Using kind, push the new docker image to make it accessible within the cluster:
```

kind load docker-image spark:our-own-apache-spark-kb8

```

To execute spark jobs by spark-submit, we need to create a service account in Kubernetes using kubectl and estabilish a cluster-level role for the service account, granting permissions within the default namespace:
```

kubectl create serviceaccount spark

kubectl create clusterrolebinding spark-role --clusterrole=edit --serviceaccount=default:spark --namespace=default

```

Now, we can run the app using spark-submit:
```

./bin/spark-submit --master k8s://https://127.0.0.1:49407 --deploy-mode cluster --name spark-pi --class org.apache.spark.examples.SparkPi --conf spark.executor.instances=2 --conf spark.kubernetes.container.image=spark:my-apache-spark-kb8 --conf spark.kubernetes.container.image.pullPolicy=IfNotPresent --conf spark.kubernetes.authenticate.driver.serviceAccountName=spark local:///opt/spark/examples/jars/spark-examples_2.13-3.5.1.jar 100

```

Remind to check your kubernetes control plane URL using this command:
```

kubectl cluster-info

```

To monitor application, follow this steps:
```

kubectl get pods

kubectl port-forward <driver-pod-name> 4040:4040

```

Then we can access Spark UI via "localhost:4040" while the job is still running!


### Third way

We will install Spark using helm and helm charts. After installing helm in the computer, let's install Spark Operator by downloading it from the repository and installing it in your cluster:

```

helm repo add spark-operator https://kubeflow.github.io/spark-operator

helm install my-spark-operator spark-operator/spark-operator --namespace spark-operator --create-namespace --set webhook.enable=true

```

To check your installation, use this command:
```

helm status --namespace spark-operator my-spark-operator

```

Let's apply the yaml:
```

kubectl apply -f spark-pi.yaml

```

To check the application, use this command:
```

kubectl describe sparkapplication --namespace=spark-operator

```

### Fourth way

This was my way to start a spark pod in k8s, following these steps after installing helm and kubectl:

First, to install a spark pod with one master and two workers, use this helm commands:
```

helm install spark-with-ui oci://registry-1.docker.io/bitnamicharts/spark

helm upgrade --install spark-with-ui --set worker.replicaCount=2 oci://registry-1.docker.io/bitnamicharts/spark --create-namespace --namespace=lakehouse

```

To execute a test, run a spark-submit in the master pod:
```

kubectl exec -it -n lakehouse spark-with-ui-master-0 -- ./bin/spark-submit \
 --class org.apache.spark.examples.SparkPi \
 --master spark://spark-with-ui-master-0:7077 \
 ./examples/jars/spark-examples_2.12-3.5.1.jar 1000

```

To access the spark-ui, we need to make a port-foward to its http port:
```

kubectl port-forward svc/spark-with-ui-master-svc 80:80 --namespace lakehouse

```


### Apache Airflow

Airflow will orchestrate the steps of our ELT.

```

helm repo add apache-airflow https://airflow.apache.org

```

To install an airflow instance, run this helm command (you need a values.yaml file with the manifest of the installation):
```

helm upgrade --install airflow apache-airflow/airflow --namespace lakehouse -f values.yaml --version 2.8.4

````

To enter in the Airflow webserver, we need to make a port-forward in kubectl to the webserver port:
```

kubectl port-forward svc/airflow-webserver 8080:8080 --namespace lakehouse

```


### Minio

It will be the bucket of our parquet files.




kubectl config set-context --current --namespace lakehouse

helm show values apache-airflow/airflow > values.yaml
helm upgrade --install airflow apache-airflow/airflow --namespace lakehouse --create-namespace --values values.yaml


kubectl create namespace lakehouse && kubectl config set-context --current --namespace=lakehouse




