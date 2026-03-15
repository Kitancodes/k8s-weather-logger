# k8s-weather-logger

A real-time weather logging service built with Python, containerized with Docker, and deployed on AWS EKS using Kubernetes and Terraform. Every 30 minutes, the service fetches live weather data for Lagos, Abuja, Tokyo, and London from the OpenWeatherMap API and persists each reading into a PostgreSQL database running inside the cluster. This is a backend service with no UI. The evidence is in the data.

## What It Does

A Kubernetes CronJob triggers the weather fetcher every 30 minutes. The Python app connects to the OpenWeatherMap API, collects temperature, humidity, and wind speed for all four cities, then inserts a timestamped row per city into a PostgreSQL database. The database runs as a pod inside the same Kubernetes namespace.

## Why I Built This

I built this project to get hands-on with Kubernetes concepts that show up in real production environments. Specifically, I wanted to work with Kubernetes Secrets and ConfigMaps in a meaningful context, and I mean with a real API key, real database credentials, and real configuration that the app actually depends on. Everything in this project has a reason to exist.

## Tech Stack

- Python 3.11
- PostgreSQL 15
- Docker
- Kubernetes (AWS EKS)
- Terraform
- OpenWeatherMap API

## How Secrets and ConfigMaps Are Used

This is the core of the project. The weather app never hardcodes credentials. All sensitive values — the OpenWeatherMap API key, database username, password, and database name — are stored in a Kubernetes Secret and injected into the pod as environment variables at runtime. Non-sensitive configuration, including the list of cities, database host, and port, lives in a ConfigMap.

Locally, the app reads from a `.env` file. Inside the cluster, Kubernetes handles the injection transparently. The app code itself does not change between environments.

## Kubernetes Resources

The following resources are deployed in the `weather-logger` namespace:

- `Namespace` — isolates all project resources
- `Secret` — stores the API key and database credentials
- `ConfigMap` — stores cities, database host, and port
- `CronJob` — triggers the weather fetch every 30 minutes
- `Deployment` — runs the PostgreSQL database pod
- `Service` (ClusterIP) — exposes PostgreSQL internally within the cluster
- `Deployment` — runs the weather app
- `PersistentVolumeClaim` — defined for durable PostgreSQL storage (see note below)

## A Note on the PersistentVolumeClaim

The `pvc.yaml` manifest is included and reflects how PostgreSQL storage would be configured in production. During deployment on EKS, the EBS CSI driver encountered an IAM permissions issue caused by missing IRSA (IAM Roles for Service Accounts) configuration, which prevented dynamic volume provisioning. But instead of shifting focus away from the core learning objective, the decision was made to proceed without it.

## Infrastructure

All AWS infrastructure is provisioned with Terraform using two modules: VPC and EKS. 

The VPC module provisions public and private subnets across two availability zones, an internet gateway, NAT gateways, and route tables. 

The EKS module provisions the control plane, IAM roles, a node group, and the necessary policy attachments.

`terraform destroy` was run immediately after verifying the deployment. The project can be fully reproduced at any time with `terraform apply`.

## Deployment

You will need the AWS CLI configured, Terraform installed, kubectl installed, and a Docker Hub account.

Provision the infrastructure:
```
cd terraform
terraform init
terraform apply
```

Connect kubectl to the cluster:
```
aws eks update-kubeconfig --region us-east-1 --name weather-logger-cluster
```

Base64 encode your credentials and replace placeholders in `manifests/secret.yaml`:
```
echo -n "your_api_key" | base64
echo -n "your_db_password" | base64
```

Apply manifests in order:
```
kubectl apply -f manifests/namespace.yaml
kubectl apply -f manifests/secret.yaml
kubectl apply -f manifests/configmap.yaml
kubectl apply -f manifests/postgres/deployment.yaml
kubectl apply -f manifests/postgres/service.yaml
kubectl apply -f manifests/deployment.yaml
kubectl apply -f manifests/cronjob.yaml
```

Verify everything is running:
```
kubectl get all -n weather-logger
```

Tear down when done:
```
cd terraform
terraform destroy
```

## Evidence

![PostgreSQL weather_log table showing logged data for Lagos, Abuja, Tokyo and London](./evidence/postgres-pager.png)

