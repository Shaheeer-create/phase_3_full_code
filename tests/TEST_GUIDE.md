# Phase V Testing Guide

Complete guide for running and understanding Phase V tests.

---

## Overview

Phase V includes comprehensive testing across multiple layers:

1. **Integration Tests** - API endpoints with database
2. **Event Flow Tests** - Kafka event publishing and consumption
3. **E2E Tests** - Complete user workflows with Playwright
4. **Performance Tests** - Load testing with Locust

---

## Prerequisites

### Required Software
- Python 3.12+
- Node.js 20+ (for Playwright)
- Access to deployed system (Minikube or cloud)

### Environment Variables
```bash
# Required
export DATABASE_URL="postgresql://user:pass@host/db"
export API_URL="http://todo.local"
export BASE_URL="http://todo.local"

# Optional (for authenticated tests)
export TEST_USER_EMAIL="test@example.com"
export TEST_USER_PASSWORD="testpass123"
```

---

## Quick Start

### Install Dependencies
```bash
cd tests
pip install -r requirements.txt
playwright install chromium
```

### Run All Tests
```bash
# Linux/Mac
chmod +x run_all_tests.sh
./run_all_tests.sh

# Windows
run_all_tests.bat
```

---

## Test Suites

### 1. Integration Tests

**What it tests:**
- All Phase V API endpoints
- Database integration
- Input validation
- Error handling

**Run:**
```bash
pytest tests/integration/test_api_phase5.py -v
```

**Test Coverage:**
- ✅ Task creation with priority, tags, due dates
- ✅ Advanced search with multiple filters
- ✅ Tag management
- ✅ Reminder creation
- ✅ Recurring task patterns
- ✅ Task completion
- ✅ Data validation

**Expected Results:**
- All tests should pass
- Response times < 200ms
- No database errors

---

### 2. Event Flow Tests

**What it tests:**
- Kafka event publishing
- Microservice event consumption
- Audit logging
- Recurring task generation
- Event processing latency

**Run:**
```bash
pytest tests/event-flow/test_event_flow.py -v
```

**Test Coverage:**
- ✅ Task created event → Audit log
- ✅ Task updated event → Audit log
- ✅ Task completed event → Audit log
- ✅ Task deleted event → Audit log
- ✅ Recurring task completion → Instance generation
- ✅ Reminder creation → Database entry
- ✅ Event processing latency < 5 seconds

**Expected Results:**
- All events published to Kafka
- Audit service logs all operations
- Recurring service generates instances
- Event processing < 5 seconds

**Note:** These tests require:
- Dapr running
- Kafka/Redpanda accessible
- All microservices deployed

---

### 3. E2E Tests

**What it tests:**
- Complete user workflows
- Frontend functionality
- UI interactions
- Responsive design

**Run:**
```bash
pytest tests/e2e/test_user_workflows.py -v
```

**Test Coverage:**
- ✅ Task creation (basic, with priority, with tags, with due date)
- ✅ Task completion/uncompletion
- ✅ Task filtering by status
- ✅ Task search
- ✅ Task deletion
- ✅ Advanced filtering by priority
- ✅ Mobile responsive layout

**Expected Results:**
- All UI interactions work
- No JavaScript errors
- Responsive on mobile devices

**Note:** Tests run in headless mode by default. To see browser:
```bash
pytest tests/e2e/test_user_workflows.py -v --headed
```

---

### 4. Performance Tests

**What it tests:**
- API response times under load
- Concurrent user handling
- Database performance
- System throughput

**Run:**
```bash
locust -f tests/performance/locustfile.py \
  --host=http://todo.local \
  --users=100 \
  --spawn-rate=10 \
  --run-time=5m \
  --headless
```

**Test Scenarios:**
- List tasks (10 weight)
- Create task (5 weight)
- Search tasks (3 weight)
- Complete task (4 weight)
- Update task (2 weight)
- Add tags (2 weight)
- Create reminder (1 weight)
- Delete task (1 weight)

**Performance Targets:**
- Average response time: < 200ms
- 95th percentile: < 500ms
- Failure rate: < 1%
- Throughput: > 100 req/sec

**Expected Results:**
- System handles 100 concurrent users
- No significant performance degradation
- All endpoints meet response time targets

---

## Running Individual Test Suites

### Integration Tests Only
```bash
pytest tests/integration/test_api_phase5.py -v --tb=short
```

### Event Flow Tests Only
```bash
pytest tests/event-flow/test_event_flow.py -v --tb=short
```

### E2E Tests Only
```bash
pytest tests/e2e/test_user_workflows.py -v --tb=short
```

### Performance Tests Only
```bash
locust -f tests/performance/locustfile.py \
  --host=http://todo.local \
  --users=50 \
  --spawn-rate=5 \
  --run-time=3m
```

---

## Test Reports

### Generate HTML Reports
```bash
# Integration tests with coverage
pytest tests/integration/test_api_phase5.py \
  --html=test-reports/integration.html \
  --self-contained-html \
  --cov=backend \
  --cov-report=html:test-reports/coverage

# E2E tests
pytest tests/e2e/test_user_workflows.py \
  --html=test-reports/e2e.html \
  --self-contained-html

# Performance tests
locust -f tests/performance/locustfile.py \
  --host=http://todo.local \
  --users=50 \
  --spawn-rate=5 \
  --run-time=5m \
  --headless \
  --html=test-reports/performance.html
```

### View Reports
```bash
# Open in browser
open test-reports/integration.html
open test-reports/e2e.html
open test-reports/performance.html
open test-reports/coverage/index.html
```

---

## Troubleshooting

### Integration Tests Failing

**Issue:** `Authentication failed: 401`
**Solution:**
- Verify test user exists in database
- Check JWT_SECRET is correct
- Ensure Better Auth is configured

**Issue:** `Connection refused`
**Solution:**
- Verify API is running: `curl http://todo.local/api/health`
- Check ingress is configured
- Verify DNS: `ping todo.local`

**Issue:** `Database connection failed`
**Solution:**
- Verify DATABASE_URL is correct
- Check database is accessible
- Ensure migrations have run

---

### Event Flow Tests Failing

**Issue:** `Audit log entry not found`
**Solution:**
- Verify Dapr is running: `dapr status -k`
- Check Kafka connection: `kubectl logs -l app=backend -c daprd`
- Verify audit service is running: `kubectl get pods -l app=audit-service`
- Increase wait time in tests (event processing may be slow)

**Issue:** `Recurring instance not generated`
**Solution:**
- Verify recurring service is running
- Check recurring service logs: `kubectl logs -l app=recurring-service`
- Verify Kafka topic exists: Check Redpanda Console
- This is expected if recurring service is not deployed

---

### E2E Tests Failing

**Issue:** `Timeout waiting for element`
**Solution:**
- Increase timeout in tests
- Check frontend is accessible: `curl http://todo.local`
- Verify JavaScript is loading (check browser console)
- Run with `--headed` to see what's happening

**Issue:** `Playwright browser not found`
**Solution:**
```bash
playwright install chromium
```

---

### Performance Tests Failing

**Issue:** `High response times`
**Solution:**
- Check system resources: `kubectl top pods`
- Verify database performance
- Check Kafka consumer lag
- Reduce concurrent users

**Issue:** `High failure rate`
**Solution:**
- Check backend logs for errors
- Verify database connections not exhausted
- Check rate limiting settings
- Reduce spawn rate

---

## Test Data Management

### Create Test User
```bash
# Via API
curl -X POST http://todo.local/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpass123",
    "name": "Test User"
  }'
```

### Clean Up Test Data
```bash
# Delete all tasks for test user
# (Run this between test runs if needed)
psql $DATABASE_URL -c "DELETE FROM tasks WHERE user_id = 'test-user-id';"
psql $DATABASE_URL -c "DELETE FROM audit_log WHERE user_id = 'test-user-id';"
```

---

## Continuous Integration

### GitHub Actions Example
```yaml
name: Run Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'

      - name: Install dependencies
        run: |
          pip install -r tests/requirements.txt
          playwright install chromium

      - name: Run integration tests
        env:
          DATABASE_URL: ${{ secrets.DATABASE_URL }}
          API_URL: http://localhost:8000
        run: pytest tests/integration/ -v

      - name: Run E2E tests
        env:
          BASE_URL: http://localhost:3000
        run: pytest tests/e2e/ -v
```

---

## Performance Benchmarks

### Baseline Performance (Expected)

**API Endpoints:**
- GET /api/tasks: 50-100ms
- POST /api/tasks: 100-150ms
- GET /api/tasks/search: 100-200ms
- PATCH /api/tasks/{id}/complete: 80-120ms

**Event Processing:**
- Task created → Audit log: 1-3 seconds
- Task completed → Recurring instance: 2-5 seconds

**Concurrent Users:**
- 50 users: < 200ms avg response time
- 100 users: < 300ms avg response time
- 200 users: < 500ms avg response time

---

## Test Coverage Goals

### Current Coverage
- Backend API: 85%+ (target)
- Event flow: 70%+ (target)
- Frontend: 60%+ (target)

### Coverage Report
```bash
pytest tests/integration/ --cov=backend --cov-report=term-missing
```

---

## Best Practices

### Writing Tests
1. **Isolation** - Each test should be independent
2. **Cleanup** - Clean up test data after tests
3. **Assertions** - Use clear, specific assertions
4. **Timeouts** - Set reasonable timeouts for async operations
5. **Logging** - Log important test steps for debugging

### Running Tests
1. **Local First** - Run tests locally before CI
2. **Incremental** - Run affected tests first
3. **Parallel** - Use pytest-xdist for parallel execution
4. **Reports** - Always generate HTML reports for review

---

## Next Steps

After all tests pass:

1. ✅ Review test reports
2. ✅ Check code coverage
3. ✅ Fix any warnings
4. ✅ Document any known issues
5. ✅ Proceed to Phase 5.7 (Cloud deployment)

---

## Support

### Common Commands
```bash
# Run specific test
pytest tests/integration/test_api_phase5.py::TestTaskCRUD::test_create_task_with_priority -v

# Run tests matching pattern
pytest tests/ -k "priority" -v

# Run tests with verbose output
pytest tests/ -vv

# Run tests and stop on first failure
pytest tests/ -x

# Run tests in parallel
pytest tests/ -n auto

# Generate coverage report
pytest tests/ --cov=backend --cov-report=html
```

---

**Last Updated:** 2026-02-07
**Test Suite Version:** 1.0.0
**Phase:** 5.6 - Local Deployment & Testing
