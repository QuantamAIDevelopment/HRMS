# HRMS Kubernetes Deployment

## Overview
This directory contains Kubernetes manifests for deploying the HRMS application to a Kubernetes cluster using Azure DevOps CI/CD pipeline.

## Files
- `secrets.yaml` - Kubernetes secrets and ConfigMap for application configuration
- `deployment.yaml` - Application deployment with environment variables and health checks
- `service.yaml` - Service and Ingress for external access
- `azure-pipeline-deploy.yaml` - Azure DevOps pipeline configuration

## Prerequisites
1. Azure Container Registry (ACR)
2. Azure Kubernetes Service (AKS) or any Kubernetes cluster
3. Azure DevOps project with service connections
4. PostgreSQL database (can be Azure Database for PostgreSQL)

## Environment Variables Required in Azure DevOps
Set these as pipeline variables or variable groups:

### Secrets (mark as secret in Azure DevOps):
- `DATABASE_URL` - PostgreSQL connection string (e.g., `postgresql://user:password@host:5432/dbname`)
- `SECRET_KEY` - JWT secret key for authentication
- `SMTP_USERNAME` - Email service username
- `SMTP_PASSWORD` - Email service password
- `FROM_EMAIL` - Sender email address

### Configuration:
- `dockerRegistryServiceConnection` - Azure Container Registry service connection name
- `kubernetesServiceConnection` - Kubernetes cluster service connection name
- `containerRegistry` - Your ACR URL (e.g., `yourregistry.azurecr.io`)

## Deployment Steps

### 1. Setup Azure Resources
```bash
# Create resource group
az group create --name hrms-rg --location eastus

# Create ACR
az acr create --resource-group hrms-rg --name yourregistry --sku Basic

# Create AKS cluster
az aks create --resource-group hrms-rg --name hrms-aks --node-count 2 --enable-addons monitoring --generate-ssh-keys
```

### 2. Configure Azure DevOps
1. Create service connections for ACR and AKS
2. Set up pipeline variables with your secrets
3. Update the pipeline YAML with your connection names

### 3. Deploy
1. Push code to your repository
2. Pipeline will automatically build and deploy
3. Or manually run the pipeline

### 4. Access Application
```bash
# Get external IP (if using LoadBalancer service)
kubectl get services

# Or setup Ingress controller for domain access
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.1/deploy/static/provider/cloud/deploy.yaml
```

## Manual Deployment (Alternative)
If not using Azure DevOps:

```bash
# Build and push image
docker build -t yourregistry.azurecr.io/hrms-service:latest .
docker push yourregistry.azurecr.io/hrms-service:latest

# Create secrets manually
kubectl create secret generic hrms-secrets \
  --from-literal=database-url="your-db-url" \
  --from-literal=db-username="your-db-username" \
  --from-literal=db-password="your-db-password" \
  --from-literal=secret-key="your-secret-key" \
  --from-literal=smtp-server="smtp.gmail.com" \
  --from-literal=smtp-port="587" \
  --from-literal=smtp-username="your-smtp-user" \
  --from-literal=smtp-password="your-smtp-pass" \
  --from-literal=from-email="your-email"

# Deploy
kubectl apply -f k8s/secrets.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
```

## Monitoring
```bash
# Check deployment status
kubectl get deployments
kubectl get pods
kubectl get services

# View logs
kubectl logs -f deployment/hrms-service

# Check health
kubectl port-forward service/hrms-service 8080:80
curl http://localhost:8080/health
```

## Scaling
```bash
# Scale replicas
kubectl scale deployment hrms-service --replicas=3

# Auto-scaling (optional)
kubectl autoscale deployment hrms-service --cpu-percent=70 --min=2 --max=10
```