@echo off
REM Run All Tests for Phase V (Windows)
REM This script runs integration, event flow, E2E, and performance tests

echo ==========================================
echo Phase V - Running All Tests
echo ==========================================
echo.

REM Configuration
if "%API_URL%"=="" set API_URL=http://todo.local
if "%BASE_URL%"=="" set BASE_URL=http://todo.local

REM Check if DATABASE_URL is set
if "%DATABASE_URL%"=="" (
    echo ERROR: DATABASE_URL not set
    echo Please set DATABASE_URL environment variable
    exit /b 1
)

REM Install dependencies
echo Installing test dependencies...
pip install -r tests\requirements.txt

REM Install Playwright browsers
echo Installing Playwright browsers...
playwright install chromium

echo.
echo ==========================================
echo 1. Running Integration Tests
echo ==========================================
pytest tests\integration\test_api_phase5.py -v --tb=short --html=test-reports\integration-report.html --self-contained-html --cov=backend --cov-report=html:test-reports\coverage-integration

if %ERRORLEVEL% NEQ 0 (
    echo Integration tests failed
    exit /b 1
)
echo Integration tests passed

echo.
echo ==========================================
echo 2. Running Event Flow Tests
echo ==========================================
pytest tests\event-flow\test_event_flow.py -v --tb=short --html=test-reports\event-flow-report.html --self-contained-html

if %ERRORLEVEL% NEQ 0 (
    echo Event flow tests failed
    exit /b 1
)
echo Event flow tests passed

echo.
echo ==========================================
echo 3. Running E2E Tests
echo ==========================================
pytest tests\e2e\test_user_workflows.py -v --tb=short --html=test-reports\e2e-report.html --self-contained-html

if %ERRORLEVEL% NEQ 0 (
    echo E2E tests failed
    exit /b 1
)
echo E2E tests passed

echo.
echo ==========================================
echo 4. Running Performance Tests
echo ==========================================
echo Starting Locust performance test (5 minutes)...
locust -f tests\performance\locustfile.py --host=%API_URL% --users=50 --spawn-rate=5 --run-time=5m --headless --html=test-reports\performance-report.html

if %ERRORLEVEL% NEQ 0 (
    echo Performance tests failed
    exit /b 1
)
echo Performance tests completed

echo.
echo ==========================================
echo Test Summary
echo ==========================================
echo All tests passed!
echo.
echo Test reports generated in test-reports\:
echo   - integration-report.html
echo   - event-flow-report.html
echo   - e2e-report.html
echo   - performance-report.html
echo   - coverage-integration\ (code coverage)
echo.
echo ==========================================
