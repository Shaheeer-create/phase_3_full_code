# Phase 5.6 Quick Start Guide

**Complete deployment and testing guide for Phase V on Minikube**

---

## 📋 Prerequisites

Before starting, ensure you have:

- ✅ **Minikube** installed and running
- ✅ **kubectl** installed
- ✅ **Helm 3** installed
- ✅ **Docker** installed
- ✅ **Python 3.12+** installed
- ✅ **Node.js 20+** installed
- ✅ **Dapr CLI** installed
- ✅ **Redpanda Cloud account** (you have this ✓)
- ✅ **Neon PostgreSQL database** (you have this ✓)
- ✅ **Google Gemini API key** (you have this ✓)

### Install Missing Tools

**Windows:**
```powershell
# Install Chocolatey first (if not installed)
# Then install tools:
choco install minikube kubernetes-cli kubernetes-helm docker-desktop

# Install Dapr CLI
powershell -Command "iwr -useb https://raw.githubusercontent.com/dapr/cli/master/install/install.ps1 | iex"
```

**Linux/Mac:**
```bash
# Install Minikube
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube

# Install kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

# Install Helm
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# Install Dapr CLI
wget -q https://raw.githubusercontent.com/dapr/cli/master/install/install.sh -O - | /bin/bash
```

---

## 🚀 Step-by-Step Deployment

### Step 1: Complete Redpanda Cloud Setup (5 minutes)

You already have:
- ✅ Redpanda Cloud account
- ✅ Cluster created
- ✅ Topic: `task-events` created
- ✅ Credentials: Client ID and Secret

**Now create 2 more topics:**

1. Go to [Redpanda Console](https://cloud.redpanda.com/)
2. Navigate to your cluster → **Topics**
3. Click **Create Topic**

**Topic 2: reminder-events**
- Name: `reminder-events`
- Partitions: `3`
- Retention: `604800000` ms (7 days)
- Cleanup policy: `delete`
- Click **Create**

**Topic 3: recurring-events**
- Name: `recurring-events`
- Partitions: `3`
- Retention: `604800000` ms (7 days)
- Cleanup policy: `delete`
- Click **Create**

4. Get your **Bootstrap Server URL**:
   - Go to **Cluster Settings** → **Connection**
   - Copy the bootstrap server URL (e.g., `seed-abc123.cloud.redpanda.com:9092`)

**You should now have:**
- ✅ 3 topics: task-events, reminder-events, recurring-events
- ✅ Bootstrap server URL
- ✅ Client ID: `WII4vQ2cFUwWoJbcuydvOjH097QL90C8`
- ✅ Client Secret: `sxOloXPgn1S24C3fVk0l854IVRmD8TmUJaxQo3iK4PV3FjgMWmb8rjlUakLiMqf_`

---

### Step 2: Configure Environment Variables (2 minutes)

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Edit `.env` and fill in your values:

```bash
# Database (your Neon PostgreSQL URL)
DATABASE_URL=postgresql://user:password@host.neon.tech/dbname?sslmode=require

# Authentication (generate with: openssl rand -base64 32)
JWT_SECRET=your-generated-secret-here

# AI (your Google Gemini API key)
GEMINI_API_KEY=your-gemini-api-key-here

# Redpanda Cloud (use your actual values)
REDPANDA_BOOTSTRAP_SERVER=seed-xxxxx.cloud.redpanda.com:9092
REDPANDA_CLIENT_ID=WII4vQ2cFUwWoJbcuydvOjH097QL90C8
REDPANDA_CLIENT_SECRET=sxOloXPgn1S24C3fVk0l854IVRmD8TmUJaxQo3iK4PV3FjgMWmb8rjlUakLiMqf_

# Email (optional - for notification service)
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

**Generate JWT Secret:**
```bash
# Linux/Mac
openssl rand -base64 32

# Windows (PowerShell)
[Convert]::ToBase64String((1..32 | ForEach-Object { Get-Random -Maximum 256 }))
```

---

### Step 3: Start Minikube (2 minutes)

```bash
# Start Minikube with sufficient resources
minikube start --cpus=4 --memory=8192 --driver=docker

# Enable ingress addon
minikube addons enable ingress

# Verify Minikube is running
minikube status
```

---

### Step 4: Deploy Phase V (10-15 minutes)

**Windows:**
```bash
cd E:\quarter4\hacakthon-2\phase_3_copy
scripts\deploy-phase5-local.bat
```

**Linux/Mac:**
```bash
cd /path/to/phase_3_copy
chmod +x scripts/deploy-phase5-local.sh
./scripts/deploy-phase5-local.sh
```

**What this script does:**
1. ✅ Verifies all prerequisites
2. ✅ Creates Kubernetes secrets
3. ✅ Runs database migrations
4. ✅ Installs Dapr to Kubernetes
5. ✅ Configures Dapr components (Kafka Pub/Sub)
6. ✅ Builds Docker images (5 services)
7. ✅ Deploys with Helm
8. ✅ Waits for all pods to be ready

**Expected output:**
```
==========================================
Deployment Complete!
==========================================

Access URLs:
  Frontend: http://todo.local
  Backend API: http://todo.local/api
  Health Check: http://todo.local/api/health
```

---

### Step 5: Verify Deployment (2 minutes)

```bash
# Check all pods are running
kubectl get pods

# Expected output:
# NAME                                    READY   STATUS    RESTARTS   AGE
# backend-xxxxxxxxxx-xxxxx                2/2     Running   0          2m
# frontend-xxxxxxxxxx-xxxxx               2/2     Running   0          2m
# notification-service-xxxxxxxxxx-xxxxx   2/2     Running   0          2m
# recurring-service-xxxxxxxxxx-xxxxx      2/2     Running   0          2m
# audit-service-xxxxxxxxxx-xxxxx          2/2     Running   0          2m

# Check services
kubectl get svc

# Check ingress
kubectl get ingress

# Test health endpoint
curl http://todo.local/api/health
# Expected: {"status":"healthy"}
```

**Verify Dapr sidecars:**
```bash
# Each pod should have 2 containers (app + daprd)
kubectl get pods -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.spec.containers[*].name}{"\n"}{end}'
```

---

### Step 6: Run Tests (15-20 minutes)

```bash
cd tests

# Install test dependencies
pip install -r requirements.txt
playwright install chromium

# Set environment variables
export DATABASE_URL="your-neon-postgres-url"
export API_URL="http://todo.local"
export BASE_URL="http://todo.local"
```

**Run all tests:**

**Windows:**
```bash
run_all_tests.bat
```

**Linux/Mac:**
```bash
chmod +x run_all_tests.sh
./run_all_tests.sh
```

**Or run individual test suites:**

```bash
# Integration tests (2-3 minutes)
pytest tests/integration/test_api_phase5.py -v

# Event flow tests (3-5 minutes)
pytest tests/event-flow/test_event_flow.py -v

# E2E tests (5-7 minutes)
pytest tests/e2e/test_user_workflows.py -v

# Performance tests (5 minutes)
locust -f tests/performance/locustfile.py \
  --host=http://todo.local \
  --users=50 \
  --spawn-rate=5 \
  --run-time=5m \
  --headless
```

**Expected results:**
- ✅ Integration tests: 30+ tests passed
- ✅ Event flow tests: 15+ tests passed (90%+ pass rate)
- ✅ E2E tests: 20+ tests passed
- ✅ Performance tests: Avg response time < 200ms

---

## 📊 View Test Reports

After running tests, reports are generated in `test-reports/`:

```bash
# Open reports in browser
# Windows
start test-reports\integration-report.html
start test-reports\e2e-report.html
start test-reports\performance-report.html
start test-reports\coverage-integration\index.html

# Linux/Mac
open test-reports/integration-report.html
open test-reports/e2e-report.html
open test-reports/performance-report.html
open test-reports/coverage-integration/index.html
```

---

## 🔍 Troubleshooting

### Issue: Pods not starting

```bash
# Check pod status
kubectl get pods

# View pod logs
kubectl logs -f deployment/backend
kubectl logs -f deployment/backend -c daprd  # Dapr sidecar logs

# Describe pod for events
kubectl describe pod <pod-name>
```

### Issue: Can't access http://todo.local

**Windows:**
1. Check hosts file: `C:\Windows\System32\drivers\etc\hosts`
2. Should contain: `<minikube-ip> todo.local`
3. Get Minikube IP: `minikube ip`
4. Add manually if missing (requires admin)

**Linux/Mac:**
1. Check hosts file: `/etc/hosts`
2. Should contain: `<minikube-ip> todo.local`
3. Add manually: `echo "$(minikube ip) todo.local" | sudo tee -a /etc/hosts`

### Issue: Database connection failed

```bash
# Verify DATABASE_URL is correct
echo $DATABASE_URL

# Test connection
psql $DATABASE_URL -c "SELECT 1"

# Check if migrations ran
psql $DATABASE_URL -c "\dt"
# Should show: tasks, task_tags, recurring_patterns, task_reminders, audit_log
```

### Issue: Kafka connection failed

```bash
# Check Dapr pubsub component
kubectl get component kafka-pubsub -o yaml

# Check if bootstrap server is correct
kubectl get secret kafka-secrets -o jsonpath='{.data.bootstrap-server}' | base64 -d

# View Dapr sidecar logs
kubectl logs -f deployment/backend -c daprd | grep kafka
```

### Issue: Event flow tests failing

This is expected if microservices are not fully deployed or Kafka is not accessible.

**Check microservices:**
```bash
kubectl get pods -l app=notification-service
kubectl get pods -l app=recurring-service
kubectl get pods -l app=audit-service

# View logs
kubectl logs -f deployment/notification-service
kubectl logs -f deployment/recurring-service
kubectl logs -f deployment/audit-service
```

**Check Kafka topics in Redpanda Console:**
- Go to your cluster → Topics
- Verify all 3 topics exist: task-events, reminder-events, recurring-events
- Check if messages are being published (should see message count increasing)

---

## 🎯 Success Criteria

Phase 5.6 is successful when:

- ✅ All 5 services deployed and running (2/2 containers each)
- ✅ Dapr sidecars injected into all pods
- ✅ Frontend accessible at http://todo.local
- ✅ Backend API responding at http://todo.local/api
- ✅ Integration tests: 100% pass rate
- ✅ Event flow tests: 90%+ pass rate
- ✅ E2E tests: 100% pass rate
- ✅ Performance tests: p95 < 200ms, failure rate < 1%
- ✅ Kafka topics receiving events (check Redpanda Console)
- ✅ Audit log entries created in database
- ✅ Recurring task instances generated

---

## 📝 Next Steps

After Phase 5.6 is complete:

1. **Review test reports** - Check for any failures or warnings
2. **Fix any issues** - Address failing tests or performance problems
3. **Document results** - Save test reports and metrics
4. **Proceed to Phase 5.7** - Set up Oracle OKE cloud infrastructure

---

## 🆘 Getting Help

If you encounter issues:

1. **Check logs:**
   ```bash
   kubectl logs -f deployment/backend
   kubectl logs -f deployment/backend -c daprd
   ```

2. **Check Dapr status:**
   ```bash
   dapr status -k
   ```

3. **Check Redpanda Console:**
   - Verify topics exist
   - Check message counts
   - View consumer groups

4. **Run individual tests:**
   ```bash
   pytest tests/integration/test_api_phase5.py::TestTaskCRUD::test_create_task_with_priority -v
   ```

5. **Refer to detailed guides:**
   - `DEPLOYMENT_GUIDE.md` - Full deployment documentation
   - `REDPANDA_SETUP_GUIDE.md` - Redpanda Cloud setup
   - `tests/TEST_GUIDE.md` - Comprehensive testing guide

---

## ⏱️ Estimated Time

- **Redpanda setup:** 5 minutes
- **Environment configuration:** 2 minutes
- **Minikube start:** 2 minutes
- **Deployment:** 10-15 minutes
- **Verification:** 2 minutes
- **Testing:** 15-20 minutes

**Total:** ~35-45 minutes

---

**Last Updated:** 2026-02-07
**Phase:** 5.6 - Local Deployment & Testing
**Status:** Ready to execute
