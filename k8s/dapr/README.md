# Dapr Components Configuration

This directory contains Dapr component configurations for Phase V event-driven architecture.

## Components

### 1. Kafka Pub/Sub (`pubsub.yaml`)
**Type:** `pubsub.kafka`

Connects to Redpanda Cloud (managed Kafka) for event streaming.

**Topics:**
- `task-events` - Task lifecycle events (created, updated, deleted, completed)
- `reminder-events` - Reminder notifications
- `recurring-events` - Recurring task generation events

**Configuration:**
- Broker: Redpanda Cloud serverless endpoint
- Authentication: SASL/SCRAM-SHA-256
- Consumer Group: `todo-app`

**Secrets Required:**
```bash
kubectl create secret generic kafka-secrets \
  --from-literal=username='<redpanda-username>' \
  --from-literal=password='<redpanda-password>'
```

### 2. State Store (`statestore.yaml`)
**Type:** `state.postgresql`

Uses Neon PostgreSQL for Dapr state management.

**Configuration:**
- Table: `dapr_state`
- Metadata Table: `dapr_metadata`
- Cleanup Interval: 3600 seconds (1 hour)

**Secrets Required:**
```bash
kubectl create secret generic todo-secrets \
  --from-literal=database-url='postgresql://...'
```

### 3. Secret Store (`secrets.yaml`)
**Type:** `secretstores.kubernetes`

Uses Kubernetes native secrets for secure credential management.

### 4. Cron Binding (`bindings-cron.yaml`)
**Type:** `bindings.cron`

Triggers reminder checks every minute.

**Schedule:** `@every 1m`

## Prerequisites

### 1. Install Dapr CLI
```bash
# Linux/macOS
wget -q https://raw.githubusercontent.com/dapr/cli/master/install/install.sh -O - | /bin/bash

# Windows (PowerShell)
powershell -Command "iwr -useb https://raw.githubusercontent.com/dapr/cli/master/install/install.ps1 | iex"
```

### 2. Initialize Dapr on Kubernetes
```bash
# For Minikube
dapr init -k

# Verify installation
dapr status -k
```

Expected output:
```
NAME                   NAMESPACE    HEALTHY  STATUS   REPLICAS  VERSION  AGE  CREATED
dapr-sidecar-injector  dapr-system  True     Running  1         1.12.0   1m   2024-02-07 12:00:00
dapr-sentry            dapr-system  True     Running  1         1.12.0   1m   2024-02-07 12:00:00
dapr-operator          dapr-system  True     Running  1         1.12.0   1m   2024-02-07 12:00:00
dapr-placement         dapr-system  True     Running  1         1.12.0   1m   2024-02-07 12:00:00
```

### 3. Set Up Redpanda Cloud

1. Sign up at https://redpanda.com/cloud
2. Create a serverless cluster
3. Create topics:
   - `task-events` (3 partitions, 7 days retention)
   - `reminder-events` (3 partitions, 7 days retention)
   - `recurring-events` (3 partitions, 7 days retention)
4. Get connection details (bootstrap servers, username, password)
5. Update `pubsub.yaml` with your broker URL

## Deployment

### Step 1: Create Secrets
```bash
# Kafka credentials
kubectl create secret generic kafka-secrets \
  --from-literal=username='<redpanda-username>' \
  --from-literal=password='<redpanda-password>' \
  --namespace default

# Application secrets (if not already created)
kubectl create secret generic todo-secrets \
  --from-literal=database-url='<neon-postgres-url>' \
  --from-literal=jwt-secret='<jwt-secret>' \
  --from-literal=gemini-api-key='<gemini-key>' \
  --namespace default
```

### Step 2: Apply Dapr Components
```bash
kubectl apply -f k8s/dapr/ --namespace default
```

### Step 3: Verify Components
```bash
kubectl get components --namespace default
```

Expected output:
```
NAME              AGE
kafka-pubsub      1m
statestore        1m
secretstore       1m
reminder-cron     1m
```

### Step 4: Enable Dapr for Deployments

Add Dapr annotations to your deployment manifests:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
spec:
  template:
    metadata:
      annotations:
        dapr.io/enabled: "true"
        dapr.io/app-id: "backend"
        dapr.io/app-port: "8000"
        dapr.io/log-level: "info"
    spec:
      containers:
      - name: backend
        image: backend:latest
        # ... rest of container spec
```

## Testing Dapr Components

### Test Pub/Sub
```bash
# Publish a test event
kubectl exec -it <backend-pod> -- curl -X POST \
  http://localhost:3500/v1.0/publish/kafka-pubsub/task-events \
  -H "Content-Type: application/json" \
  -d '{"event_type":"task.created","task_id":1,"user_id":"test"}'

# Check Redpanda Console to verify message was published
```

### Test State Store
```bash
# Save state
kubectl exec -it <backend-pod> -- curl -X POST \
  http://localhost:3500/v1.0/state/statestore \
  -H "Content-Type: application/json" \
  -d '[{"key":"test-key","value":"test-value"}]'

# Retrieve state
kubectl exec -it <backend-pod> -- curl \
  http://localhost:3500/v1.0/state/statestore/test-key
```

### Test Secrets
```bash
# Get secret
kubectl exec -it <backend-pod> -- curl \
  http://localhost:3500/v1.0/secrets/secretstore/todo-secrets
```

## Monitoring

### View Dapr Logs
```bash
# Sidecar logs
kubectl logs <pod-name> -c daprd

# Application logs
kubectl logs <pod-name> -c <container-name>
```

### Dapr Dashboard
```bash
# Install dashboard
dapr dashboard -k

# Access at http://localhost:8080
```

## Troubleshooting

### Component Not Loading
```bash
# Check component status
kubectl describe component kafka-pubsub

# Check Dapr operator logs
kubectl logs -l app=dapr-operator -n dapr-system
```

### Connection Issues
```bash
# Test Kafka connectivity from pod
kubectl exec -it <backend-pod> -- curl -v telnet://seed-abc123.cloud.redpanda.com:9092

# Check secret values
kubectl get secret kafka-secrets -o jsonpath='{.data.username}' | base64 -d
```

### Pub/Sub Not Working
1. Verify topics exist in Redpanda Console
2. Check consumer group is active
3. Verify SASL credentials are correct
4. Check Dapr sidecar logs for errors

## Uninstall

```bash
# Remove components
kubectl delete -f k8s/dapr/

# Uninstall Dapr from Kubernetes
dapr uninstall -k

# Remove secrets
kubectl delete secret kafka-secrets
kubectl delete secret todo-secrets
```

## References

- [Dapr Documentation](https://docs.dapr.io/)
- [Dapr Kafka Pub/Sub](https://docs.dapr.io/reference/components-reference/supported-pubsub/setup-apache-kafka/)
- [Dapr PostgreSQL State Store](https://docs.dapr.io/reference/components-reference/supported-state-stores/setup-postgresql/)
- [Redpanda Cloud Documentation](https://docs.redpanda.com/docs/get-started/quick-start-cloud/)
