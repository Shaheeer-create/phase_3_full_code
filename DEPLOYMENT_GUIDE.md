# Phase V: Local Deployment Guide

This guide walks you through deploying the complete Phase V system to Minikube for local testing.

---

## Prerequisites

### Required Software
- ✅ **Minikube** (v1.30+)
- ✅ **kubectl** (v1.28+)
- ✅ **Helm** (v3.12+)
- ✅ **Docker** (v24+)
- ✅ **Dapr CLI** (v1.12+)
- ✅ **Node.js** (v20+)
- ✅ **Python** (v3.12+)

### Check Prerequisites
```bash
# Check Minikube
minikube version

# Check kubectl
kubectl version --client

# Check Helm
helm version

# Check Docker
docker --version

# Check Dapr CLI
dapr version

# Check Node.js
node --version

# Check Python
python --version
```

---

## Step 1: Start Minikube

```bash
# Start Minikube with sufficient resources
minikube start --cpus=4 --memory=8192 --disk-size=20g

# Enable ingress addon
minikube addons enable ingress

# Verify Minikube is running
minikube status
```

---

## Step 2: Install Dapr on Minikube

```bash
# Initialize Dapr on Kubernetes
dapr init -k

# Verify Dapr installation
dapr status -k

# Expected output:
# NAME                   NAMESPACE    HEALTHY  STATUS   REPLICAS  VERSION  AGE
# dapr-sidecar-injector  dapr-system  True     Running  1         1.12.0   1m
# dapr-sentry            dapr-system  True     Running  1         1.12.0   1m
# dapr-operator          dapr-system  True     Running  1         1.12.0   1m
# dapr-placement         dapr-system  True     Running  1         1.12.0   1m
```

---

## Step 3: Set Up Redpanda Cloud

### Create Redpanda Cloud Account
1. Go to https://redpanda.com/cloud
2. Sign up for free serverless tier
3. Create a new cluster

### Create Kafka Topics
In Redpanda Console, create 3 topics:

1. **task-events**
   - Partitions: 3
   - Retention: 7 days

2. **reminder-events**
   - Partitions: 3
   - Retention: 7 days

3. **recurring-events**
   - Partitions: 3
   - Retention: 7 days

### Get Connection Details
From Redpanda Console → Cluster Settings, copy:
- Bootstrap servers URL (e.g., `seed-abc123.cloud.redpanda.com:9092`)
- SASL username
- SASL password

### Update Dapr Pub/Sub Component
Edit `k8s/dapr/pubsub.yaml` and replace the broker URL:
```yaml
metadata:
  - name: brokers
    value: "YOUR_REDPANDA_URL:9092"  # Replace with your URL
```

---

## Step 4: Create Kubernetes Secrets

```bash
# Create todo-secrets
kubectl create secret generic todo-secrets \
  --from-literal=database-url='YOUR_NEON_DATABASE_URL' \
  --from-literal=better-auth-secret='YOUR_AUTH_SECRET' \
  --from-literal=gemini-api-key='YOUR_GEMINI_API_KEY' \
  --from-literal=smtp-user='YOUR_SMTP_USER' \
  --from-literal=smtp-password='YOUR_SMTP_PASSWORD' \
  --namespace default

# Create kafka-secrets
kubectl create secret generic kafka-secrets \
  --from-literal=username='YOUR_REDPANDA_USERNAME' \
  --from-literal=password='YOUR_REDPANDA_PASSWORD' \
  --namespace default

# Verify secrets
kubectl get secrets
```

---

## Step 5: Apply Dapr Components

```bash
# Apply all Dapr components
kubectl apply -f k8s/dapr/ --namespace default

# Verify components
kubectl get components

# Expected output:
# NAME              AGE
# kafka-pubsub      1m
# statestore        1m
# secretstore       1m
# reminder-cron     1m
```

---

## Step 6: Run Database Migrations

```bash
# Navigate to migrations directory
cd backend/migrations

# Install dependencies
pip install asyncpg python-dotenv

# Run migration
python run_migration.py up

# Expected output:
# ✓ Connected to database
# ✓ Migration up completed successfully
# ✓ New tables created:
#   - audit_log
#   - recurring_patterns
#   - task_reminders
#   - task_tags
# ✓ New columns added to tasks table:
#   - due_date
#   - is_recurring
#   - parent_task_id
#   - priority
#   - recurrence_instance_date
```

---

## Step 7: Build Docker Images

```bash
# Set Docker environment to use Minikube's Docker daemon
eval $(minikube docker-env)

# Build backend image
cd backend
docker build -t todo-backend:latest .

# Build frontend image
cd ../frontend
docker build -t todo-frontend:v3.0 .

# Build notification service
cd ../services/notification-service
docker build -t todo-notification-service:latest .

# Build recurring service
cd ../services/recurring-service
docker build -t todo-recurring-service:latest .

# Build audit service
cd ../services/audit-service
docker build -t todo-audit-service:latest .

# Verify images
docker images | grep todo
```

---

## Step 8: Deploy with Helm

```bash
# Navigate to project root
cd ../..

# Install/upgrade Helm chart
helm upgrade --install todo-app ./helm-chart \
  --namespace default \
  --wait \
  --timeout 10m

# Verify deployment
kubectl get pods

# Expected output:
# NAME                                    READY   STATUS    RESTARTS   AGE
# backend-xxxxxxxxxx-xxxxx                2/2     Running   0          2m
# backend-xxxxxxxxxx-xxxxx                2/2     Running   0          2m
# frontend-xxxxxxxxxx-xxxxx               1/1     Running   0          2m
# frontend-xxxxxxxxxx-xxxxx               1/1     Running   0          2m
# notification-service-xxxxxxxxxx-xxxxx   2/2     Running   0          2m
# recurring-service-xxxxxxxxxx-xxxxx      2/2     Running   0          2m
# audit-service-xxxxxxxxxx-xxxxx          2/2     Running   0          2m

# Note: Pods with Dapr enabled will show 2/2 (app + daprd sidecar)
```

---

## Step 9: Configure Local DNS

```bash
# Get Minikube IP
minikube ip

# Add to /etc/hosts (Linux/Mac) or C:\Windows\System32\drivers\etc\hosts (Windows)
# Replace <MINIKUBE_IP> with the actual IP
echo "<MINIKUBE_IP> todo.local" | sudo tee -a /etc/hosts

# Verify
ping todo.local
```

---

## Step 10: Verify Deployment

### Check All Services
```bash
# Check all pods are running
kubectl get pods

# Check all services
kubectl get services

# Check ingress
kubectl get ingress

# Check Dapr components
kubectl get components
```

### Test Health Endpoints
```bash
# Test backend health
curl http://todo.local/api/health

# Test notification service health
kubectl port-forward svc/notification-service 8002:8002 &
curl http://localhost:8002/health

# Test recurring service health
kubectl port-forward svc/recurring-service 8003:8003 &
curl http://localhost:8003/health

# Test audit service health
kubectl port-forward svc/audit-service 8004:8004 &
curl http://localhost:8004/health
```

### Test Frontend
```bash
# Open in browser
open http://todo.local

# Or use curl
curl -I http://todo.local
```

---

## Step 11: Test Event Flow

### Test Task Creation Event
```bash
# Create a task via API (replace with valid JWT token)
curl -X POST http://todo.local/api/tasks \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Task",
    "description": "Testing event flow",
    "priority": "high",
    "tags": ["test"]
  }'

# Check audit service logs
kubectl logs -l app=audit-service -c audit-service --tail=50

# Should see: "Processing task event: task.created for task X"
```

### Test WebSocket Connection
```bash
# Port forward notification service
kubectl port-forward svc/notification-service 8002:8002

# Connect with wscat (install: npm install -g wscat)
wscat -c ws://localhost:8002/ws/test-user-id

# Should see: Connected
```

---

## Step 12: View Logs

### View All Logs
```bash
# Backend logs
kubectl logs -l app=backend -c backend --tail=100 -f

# Frontend logs
kubectl logs -l app=frontend --tail=100 -f

# Notification service logs
kubectl logs -l app=notification-service -c notification-service --tail=100 -f

# Recurring service logs
kubectl logs -l app=recurring-service -c recurring-service --tail=100 -f

# Audit service logs
kubectl logs -l app=audit-service -c audit-service --tail=100 -f

# Dapr sidecar logs
kubectl logs -l app=backend -c daprd --tail=100 -f
```

---

## Troubleshooting

### Pods Not Starting
```bash
# Describe pod to see events
kubectl describe pod <pod-name>

# Check pod logs
kubectl logs <pod-name> -c <container-name>

# Check Dapr sidecar logs
kubectl logs <pod-name> -c daprd
```

### Dapr Components Not Loading
```bash
# Check component status
kubectl describe component kafka-pubsub

# Check Dapr operator logs
kubectl logs -l app=dapr-operator -n dapr-system
```

### Kafka Connection Issues
```bash
# Test Kafka connectivity from a pod
kubectl exec -it <backend-pod> -c backend -- curl -v telnet://YOUR_REDPANDA_URL:9092

# Check Dapr pub/sub logs
kubectl logs <backend-pod> -c daprd | grep pubsub
```

### Database Connection Issues
```bash
# Test database connection
kubectl exec -it <backend-pod> -c backend -- python -c "
import asyncpg
import asyncio
import os
async def test():
    conn = await asyncpg.connect(os.getenv('DATABASE_URL'))
    print('Connected!')
    await conn.close()
asyncio.run(test())
"
```

---

## Cleanup

### Remove Deployment
```bash
# Uninstall Helm release
helm uninstall todo-app

# Delete Dapr components
kubectl delete -f k8s/dapr/

# Delete secrets
kubectl delete secret todo-secrets kafka-secrets

# Uninstall Dapr from Kubernetes
dapr uninstall -k
```

### Stop Minikube
```bash
minikube stop
```

### Delete Minikube Cluster
```bash
minikube delete
```

---

## Next Steps

After successful local deployment:

1. **Run Integration Tests** (Phase 5.6 continued)
   - Test all API endpoints
   - Test event flow
   - Test WebSocket connections

2. **Run E2E Tests** (Phase 5.6 continued)
   - Test complete user workflows
   - Test recurring task generation
   - Test reminder notifications

3. **Performance Testing** (Phase 5.6 continued)
   - Load test with Locust
   - Measure API response times
   - Test Kafka throughput

4. **Move to Cloud** (Phase 5.7)
   - Provision Oracle OKE cluster
   - Deploy to production

---

## Useful Commands

```bash
# Watch all pods
kubectl get pods -w

# Get all resources
kubectl get all

# Port forward to a service
kubectl port-forward svc/<service-name> <local-port>:<service-port>

# Execute command in pod
kubectl exec -it <pod-name> -c <container-name> -- /bin/bash

# View Dapr dashboard
dapr dashboard -k

# Restart a deployment
kubectl rollout restart deployment/<deployment-name>

# Scale a deployment
kubectl scale deployment/<deployment-name> --replicas=3
```

---

**Last Updated:** 2026-02-07
**Next:** Run integration and E2E tests
