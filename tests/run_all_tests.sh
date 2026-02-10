#!/bin/bash
# Run All Tests for Phase V
# This script runs integration, event flow, E2E, and performance tests

set -e  # Exit on error

echo "=========================================="
echo "Phase V - Running All Tests"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
API_URL=${API_URL:-"http://todo.local"}
DATABASE_URL=${DATABASE_URL:-""}
BASE_URL=${BASE_URL:-"http://todo.local"}

# Check if required environment variables are set
if [ -z "$DATABASE_URL" ]; then
    echo -e "${RED}ERROR: DATABASE_URL not set${NC}"
    echo "Please set DATABASE_URL environment variable"
    exit 1
fi

# Install dependencies
echo -e "${YELLOW}Installing test dependencies...${NC}"
pip install -r tests/requirements.txt

# Install Playwright browsers (for E2E tests)
echo -e "${YELLOW}Installing Playwright browsers...${NC}"
playwright install chromium

echo ""
echo "=========================================="
echo "1. Running Integration Tests"
echo "=========================================="
pytest tests/integration/test_api_phase5.py \
    -v \
    --tb=short \
    --html=test-reports/integration-report.html \
    --self-contained-html \
    --cov=backend \
    --cov-report=html:test-reports/coverage-integration

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Integration tests passed${NC}"
else
    echo -e "${RED}✗ Integration tests failed${NC}"
    exit 1
fi

echo ""
echo "=========================================="
echo "2. Running Event Flow Tests"
echo "=========================================="
pytest tests/event-flow/test_event_flow.py \
    -v \
    --tb=short \
    --html=test-reports/event-flow-report.html \
    --self-contained-html

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Event flow tests passed${NC}"
else
    echo -e "${RED}✗ Event flow tests failed${NC}"
    exit 1
fi

echo ""
echo "=========================================="
echo "3. Running E2E Tests"
echo "=========================================="
pytest tests/e2e/test_user_workflows.py \
    -v \
    --tb=short \
    --html=test-reports/e2e-report.html \
    --self-contained-html

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ E2E tests passed${NC}"
else
    echo -e "${RED}✗ E2E tests failed${NC}"
    exit 1
fi

echo ""
echo "=========================================="
echo "4. Running Performance Tests"
echo "=========================================="
echo -e "${YELLOW}Starting Locust performance test (5 minutes)...${NC}"
locust -f tests/performance/locustfile.py \
    --host=$API_URL \
    --users=50 \
    --spawn-rate=5 \
    --run-time=5m \
    --headless \
    --html=test-reports/performance-report.html

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Performance tests completed${NC}"
else
    echo -e "${RED}✗ Performance tests failed${NC}"
    exit 1
fi

echo ""
echo "=========================================="
echo "Test Summary"
echo "=========================================="
echo -e "${GREEN}✓ All tests passed!${NC}"
echo ""
echo "Test reports generated in test-reports/:"
echo "  - integration-report.html"
echo "  - event-flow-report.html"
echo "  - e2e-report.html"
echo "  - performance-report.html"
echo "  - coverage-integration/ (code coverage)"
echo ""
echo "=========================================="
