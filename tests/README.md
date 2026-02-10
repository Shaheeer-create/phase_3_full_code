# Phase V Test Scripts - Complete

**Status:** ✅ All test scripts created and ready to use
**Date:** 2026-02-07

---

## 📦 What's Included

### Test Suites (4 types)
1. **Integration Tests** - `tests/integration/test_api_phase5.py`
   - 30+ test cases covering all Phase V API endpoints
   - Tests: CRUD, search, tags, reminders, recurring tasks
   - Database integration validation

2. **Event Flow Tests** - `tests/event-flow/test_event_flow.py`
   - 15+ test cases for Kafka event publishing
   - Tests: Audit logging, recurring generation, event latency
   - Microservice integration validation

3. **E2E Tests** - `tests/e2e/test_user_workflows.py`
   - 20+ test cases for complete user workflows
   - Tests: UI interactions, filtering, search, responsive design
   - Browser automation with Playwright

4. **Performance Tests** - `tests/performance/locustfile.py`
   - Load testing with 8 different scenarios
   - Tests: Concurrent users, response times, throughput
   - Performance benchmarking

### Automation Scripts
- `run_all_tests.sh` - Linux/Mac test runner
- `run_all_tests.bat` - Windows test runner
- `requirements.txt` - Python dependencies
- `TEST_GUIDE.md` - Comprehensive testing guide

---

## 🚀 Quick Start

### 1. Install Dependencies (5 minutes)
```bash
cd tests
pip install -r requirements.txt
playwright install chromium
```

### 2. Set Environment Variables
```bash
export DATABASE_URL="postgresql://user:pass@host/db"
export API_URL="http://todo.local"
export BASE_URL="http://todo.local"
```

### 3. Run All Tests (15-20 minutes)
```bash
# Linux/Mac
chmod +x run_all_tests.sh
./run_all_tests.sh

# Windows
run_all_tests.bat
```

---

## 📊 Test Coverage

### Integration Tests
- ✅ Task CRUD with Phase V fields (priority, tags, due dates)
- ✅ Advanced search (text, priority, tags, date range)
- ✅ Tag management (add, display, remove)
- ✅ Reminder creation (notification, email)
- ✅ Recurring patterns (daily, weekly, monthly, yearly)
- ✅ Task completion with event publishing
- ✅ Input validation and error handling

### Event Flow Tests
- ✅ Task created → Audit log entry
- ✅ Task updated → Audit log entry
- ✅ Task completed → Audit log entry
- ✅ Task deleted → Audit log entry
- ✅ Recurring task completion → Instance generation
- ✅ Reminder creation → Database entry
- ✅ Event processing latency measurement

### E2E Tests
- ✅ Create task (basic, with priority, with tags, with due date)
- ✅ Complete/uncomplete tasks
- ✅ Filter by status (all, pending, completed)
- ✅ Search tasks by text
- ✅ Delete tasks
- ✅ Advanced filtering by priority
- ✅ Mobile responsive layout

### Performance Tests
- ✅ List tasks (10x weight)
- ✅ Create task (5x weight)
- ✅ Search tasks (3x weight)
- ✅ Complete task (4x weight)
- ✅ Update task (2x weight)
- ✅ Add tags (2x weight)
- ✅ Create reminder (1x weight)
- ✅ Delete task (1x weight)

---

## 📈 Expected Results

### Integration Tests
- **Pass Rate:** 100%
- **Duration:** 2-3 minutes
- **Coverage:** 85%+ backend code

### Event Flow Tests
- **Pass Rate:** 90%+ (some tests may fail if microservices not deployed)
- **Duration:** 3-5 minutes
- **Event Latency:** < 5 seconds

### E2E Tests
- **Pass Rate:** 100%
- **Duration:** 5-7 minutes
- **Browser:** Chromium headless

### Performance Tests
- **Concurrent Users:** 50-100
- **Duration:** 5 minutes
- **Avg Response Time:** < 200ms
- **Failure Rate:** < 1%

---

## 🎯 Success Criteria

Phase 5.6 testing is successful when:

- ✅ All integration tests pass (100%)
- ✅ Event flow tests pass (90%+)
- ✅ E2E tests pass (100%)
- ✅ Performance tests meet targets:
  - Average response time < 200ms
  - 95th percentile < 500ms
  - Failure rate < 1%
  - Throughput > 100 req/sec

---

## 🐛 Known Issues

### Event Flow Tests
- **Issue:** Some tests may fail if microservices are not deployed
- **Impact:** Tests for recurring instance generation and audit logging
- **Workaround:** Deploy all microservices before running event flow tests
- **Status:** Expected behavior

### Performance Tests
- **Issue:** High response times on first run (cold start)
- **Impact:** Initial requests may exceed 200ms target
- **Workaround:** Run warm-up period before measuring
- **Status:** Normal behavior

---

## 📝 Test Reports

After running tests, reports are generated in `test-reports/`:

```
test-reports/
├── integration-report.html       # Integration test results
├── event-flow-report.html        # Event flow test results
├── e2e-report.html               # E2E test results
├── performance-report.html       # Performance test results
└── coverage-integration/         # Code coverage report
    └── index.html
```

**View Reports:**
```bash
open test-reports/integration-report.html
open test-reports/coverage-integration/index.html
```

---

## 🔧 Troubleshooting

### Tests Won't Run
```bash
# Check Python version
python --version  # Should be 3.12+

# Reinstall dependencies
pip install -r tests/requirements.txt --force-reinstall

# Install Playwright browsers
playwright install chromium
```

### Authentication Errors
```bash
# Create test user
curl -X POST http://todo.local/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpass123","name":"Test User"}'
```

### Database Connection Errors
```bash
# Verify DATABASE_URL
echo $DATABASE_URL

# Test connection
psql $DATABASE_URL -c "SELECT 1"
```

### Event Flow Tests Failing
```bash
# Check Dapr status
dapr status -k

# Check microservices
kubectl get pods -l app=audit-service
kubectl get pods -l app=recurring-service
kubectl get pods -l app=notification-service

# Check Kafka connection
kubectl logs -l app=backend -c daprd | grep kafka
```

---

## 📚 Documentation

- **TEST_GUIDE.md** - Comprehensive testing guide
- **DEPLOYMENT_GUIDE.md** - Deployment instructions
- **REDPANDA_SETUP_GUIDE.md** - Kafka setup guide

---

## ✅ Next Steps

After all tests pass:

1. **Review Test Reports**
   - Check all test results
   - Review code coverage
   - Identify any failures

2. **Fix Any Issues**
   - Address failing tests
   - Improve code coverage
   - Optimize performance

3. **Document Results**
   - Save test reports
   - Document any known issues
   - Update test documentation

4. **Proceed to Phase 5.7**
   - Set up Oracle OKE cluster
   - Deploy to cloud
   - Run tests in cloud environment

---

## 📞 Support

### Common Commands

```bash
# Run specific test file
pytest tests/integration/test_api_phase5.py -v

# Run specific test class
pytest tests/integration/test_api_phase5.py::TestTaskCRUD -v

# Run specific test
pytest tests/integration/test_api_phase5.py::TestTaskCRUD::test_create_task_with_priority -v

# Run tests matching pattern
pytest tests/ -k "priority" -v

# Run with coverage
pytest tests/integration/ --cov=backend --cov-report=html

# Run in parallel
pytest tests/ -n auto

# Generate HTML report
pytest tests/ --html=report.html --self-contained-html
```

### Performance Testing

```bash
# Quick test (1 minute, 10 users)
locust -f tests/performance/locustfile.py --host=http://todo.local --users=10 --spawn-rate=2 --run-time=1m --headless

# Standard test (5 minutes, 50 users)
locust -f tests/performance/locustfile.py --host=http://todo.local --users=50 --spawn-rate=5 --run-time=5m --headless

# Stress test (10 minutes, 200 users)
locust -f tests/performance/locustfile.py --host=http://todo.local --users=200 --spawn-rate=10 --run-time=10m --headless

# Interactive mode (with web UI)
locust -f tests/performance/locustfile.py --host=http://todo.local
# Then open http://localhost:8089
```

---

## 🎉 Summary

**Test Scripts Status:** ✅ COMPLETE

All test scripts have been created and are ready to use. The test suite provides comprehensive coverage of:
- Backend API functionality
- Event-driven architecture
- Frontend user workflows
- System performance

**Total Test Cases:** 65+
**Total Lines of Test Code:** ~2,500
**Estimated Test Duration:** 15-20 minutes (all suites)

---

**Created:** 2026-02-07
**Phase:** 5.6 - Local Deployment & Testing
**Status:** Ready for execution
