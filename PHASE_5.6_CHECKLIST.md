# Phase 5.6 Deployment Checklist

Use this checklist to track your progress through the Phase 5.6 deployment.

---

## 📋 Pre-Deployment Checklist

### Prerequisites Verification
- [ ] Minikube installed (`minikube version`)
- [ ] kubectl installed (`kubectl version --client`)
- [ ] Helm 3 installed (`helm version`)
- [ ] Docker installed (`docker --version`)
- [ ] Python 3.12+ installed (`python --version`)
- [ ] Node.js 20+ installed (`node --version`)
- [ ] Dapr CLI installed (`dapr --version`)

### Accounts & Credentials
- [x] Redpanda Cloud account created ✓
- [x] Redpanda cluster created ✓
- [x] Redpanda credentials obtained ✓
  - Client ID: `WII4vQ2cFUwWoJbcuydvOjH097QL90C8`
  - Client Secret: `sxOloXPgn1S24C3fVk0l854IVRmD8TmUJaxQo3iK4PV3FjgMWmb8rjlUakLiMqf_`
- [ ] Neon PostgreSQL database URL ready
- [ ] Google Gemini API key ready

---

## 🔧 Redpanda Cloud Setup

### Topics Creation
- [x] Topic 1: `task-events` created ✓
- [ ] Topic 2: `reminder-events` created
  - Partitions: 3
  - Retention: 7 days (604800000 ms)
  - Cleanup policy: delete
- [ ] Topic 3: `recurring-events` created
  - Partitions: 3
  - Retention: 7 days (604800000 ms)
  - Cleanup policy: delete

### Connection Details
- [ ] Bootstrap server URL copied from Redpanda Console
  - Format: `seed-xxxxx.cloud.redpanda.com:9092`
- [ ] Verified all 3 topics are visible in Redpanda Console

---

## ⚙️ Environment Configuration

### .env File Setup
- [ ] Copied `.env.example` to `.env`
- [ ] Filled in `DATABASE_URL` (Neon PostgreSQL)
- [ ] Generated and filled in `JWT_SECRET`
  - Command: `openssl rand -base64 32`
- [ ] Filled in `GEMINI_API_KEY`
- [ ] Filled in `REDPANDA_BOOTSTRAP_SERVER`
- [ ] Filled in `REDPANDA_CLIENT_ID`
- [ ] Filled in `REDPANDA_CLIENT_SECRET`
- [ ] (Optional) Filled in SMTP credentials for email notifications

### Verify .env File
- [ ] All required variables are set (no empty values)
- [ ] DATABASE_URL includes `?sslmode=require`
- [ ] JWT_SECRET is at least 32 characters
- [ ] REDPANDA_BOOTSTRAP_SERVER includes port `:9092`

---

## 🚀 Minikube Setup

### Start Minikube
- [ ] Started Minikube: `minikube start --cpus=4 --memory=8192 --driver=docker`
- [ ] Enabled ingress addon: `minikube addons enable ingress`
- [ ] Verified Minikube status: `minikube status`
- [ ] Got Minikube IP: `minikube ip`

### Hosts File Configuration
- [ ] Added `<minikube-ip> todo.local` to hosts file
  - Windows: `C:\Windows\System32\drivers\etc\hosts`
  - Linux/Mac: `/etc/hosts`
- [ ] Verified: `ping todo.local` responds

---

## 📦 Deployment Execution

### Run Deployment Script
- [ ] Navigated to project directory
- [ ] Executed deployment script:
  - Windows: `scripts\deploy-phase5-local.bat`
  - Linux/Mac: `./scripts/deploy-phase5-local.sh`

### Deployment Steps (automated by script)
- [ ] Prerequisites verified
- [ ] Kubernetes secrets created
- [ ] Database migrations executed
- [ ] Dapr installed to Kubernetes
- [ ] Dapr components configured
- [ ] Docker images built (5 services)
- [ ] Helm chart deployed
- [ ] All pods ready (2/2 containers each)

### Verify Deployment
- [ ] All pods running: `kubectl get pods`
  - [ ] backend (2/2 Running)
  - [ ] frontend (2/2 Running)
  - [ ] notification-service (2/2 Running)
  - [ ] recurring-service (2/2 Running)
  - [ ] audit-service (2/2 Running)
- [ ] Services created: `kubectl get svc`
- [ ] Ingress configured: `kubectl get ingress`
- [ ] Health check responds: `curl http://todo.local/api/health`

---

## 🧪 Testing Execution

### Test Environment Setup
- [ ] Navigated to `tests/` directory
- [ ] Installed test dependencies: `pip install -r requirements.txt`
- [ ] Installed Playwright browsers: `playwright install chromium`
- [ ] Set test environment variables:
  - [ ] `DATABASE_URL`
  - [ ] `API_URL=http://todo.local`
  - [ ] `BASE_URL=http://todo.local`

### Run Test Suites
- [ ] **Integration Tests** (2-3 minutes)
  - Command: `pytest tests/integration/test_api_phase5.py -v`
  - Expected: 30+ tests passed
  - Result: _____ tests passed / _____ total

- [ ] **Event Flow Tests** (3-5 minutes)
  - Command: `pytest tests/event-flow/test_event_flow.py -v`
  - Expected: 15+ tests passed (90%+ pass rate)
  - Result: _____ tests passed / _____ total

- [ ] **E2E Tests** (5-7 minutes)
  - Command: `pytest tests/e2e/test_user_workflows.py -v`
  - Expected: 20+ tests passed
  - Result: _____ tests passed / _____ total

- [ ] **Performance Tests** (5 minutes)
  - Command: `locust -f tests/performance/locustfile.py --host=http://todo.local --users=50 --spawn-rate=5 --run-time=5m --headless`
  - Expected: Avg response time < 200ms, failure rate < 1%
  - Result: Avg _____ ms, p95 _____ ms, failure rate _____ %

### Test Reports
- [ ] Opened integration test report: `test-reports/integration-report.html`
- [ ] Opened E2E test report: `test-reports/e2e-report.html`
- [ ] Opened performance test report: `test-reports/performance-report.html`
- [ ] Opened coverage report: `test-reports/coverage-integration/index.html`

---

## ✅ Validation Checklist

### Functional Validation
- [ ] Can access frontend at http://todo.local
- [ ] Can register new user
- [ ] Can login with credentials
- [ ] Can create task with priority
- [ ] Can add tags to task
- [ ] Can set due date
- [ ] Can create recurring task
- [ ] Can set reminder
- [ ] Can search tasks with filters
- [ ] Can complete task
- [ ] Can delete task

### Event-Driven Validation
- [ ] Task creation publishes event to Kafka
  - Check Redpanda Console: `task-events` topic has messages
- [ ] Audit log entry created in database
  - Query: `SELECT * FROM audit_log ORDER BY created_at DESC LIMIT 10;`
- [ ] Recurring task completion generates next instance
  - Complete a recurring task and verify new instance created
- [ ] Reminder notification sent
  - Check notification service logs: `kubectl logs -f deployment/notification-service`

### Performance Validation
- [ ] API response times acceptable (p95 < 200ms)
- [ ] No errors in backend logs
- [ ] No errors in microservice logs
- [ ] Kafka consumer lag < 100 messages
- [ ] Database queries performing well

---

## 🐛 Troubleshooting (if needed)

### Common Issues Encountered
- [ ] Issue: _________________________________
  - Solution: _________________________________
  - Status: [ ] Resolved [ ] Pending

- [ ] Issue: _________________________________
  - Solution: _________________________________
  - Status: [ ] Resolved [ ] Pending

### Logs Collected
- [ ] Backend logs: `kubectl logs deployment/backend > logs/backend.log`
- [ ] Frontend logs: `kubectl logs deployment/frontend > logs/frontend.log`
- [ ] Notification service logs: `kubectl logs deployment/notification-service > logs/notification.log`
- [ ] Recurring service logs: `kubectl logs deployment/recurring-service > logs/recurring.log`
- [ ] Audit service logs: `kubectl logs deployment/audit-service > logs/audit.log`
- [ ] Dapr sidecar logs: `kubectl logs deployment/backend -c daprd > logs/backend-daprd.log`

---

## 📊 Results Summary

### Test Results
- Integration Tests: _____ / _____ passed (_____ %)
- Event Flow Tests: _____ / _____ passed (_____ %)
- E2E Tests: _____ / _____ passed (_____ %)
- Performance Tests: Avg _____ ms, p95 _____ ms, failure rate _____ %

### Code Coverage
- Backend Coverage: _____ %
- Target: 85%+

### Performance Metrics
- Average Response Time: _____ ms (target: < 200ms)
- 95th Percentile: _____ ms (target: < 500ms)
- Throughput: _____ req/sec (target: > 100 req/sec)
- Failure Rate: _____ % (target: < 1%)

### Event Processing
- Kafka Consumer Lag: _____ messages (target: < 100)
- Event Processing Latency: _____ seconds (target: < 5s)
- Audit Log Entries: _____ (should match task operations)

---

## ✅ Phase 5.6 Completion Criteria

Phase 5.6 is **COMPLETE** when all of the following are true:

- [ ] All 5 services deployed and running (2/2 containers each)
- [ ] Dapr sidecars injected into all pods
- [ ] Frontend accessible at http://todo.local
- [ ] Backend API responding at http://todo.local/api
- [ ] Integration tests: 100% pass rate
- [ ] Event flow tests: 90%+ pass rate
- [ ] E2E tests: 100% pass rate
- [ ] Performance tests meet targets (p95 < 200ms, failure < 1%)
- [ ] Kafka topics receiving events (verified in Redpanda Console)
- [ ] Audit log entries created in database
- [ ] Recurring task instances generated correctly
- [ ] All test reports reviewed and saved

---

## 📝 Sign-Off

**Deployment Date:** _______________

**Deployed By:** _______________

**Test Results:** [ ] Pass [ ] Fail (with issues documented)

**Ready for Phase 5.7:** [ ] Yes [ ] No

**Notes:**
_________________________________________________________________
_________________________________________________________________
_________________________________________________________________

---

**Last Updated:** 2026-02-07
**Phase:** 5.6 - Local Deployment & Testing
**Status:** Ready to execute
