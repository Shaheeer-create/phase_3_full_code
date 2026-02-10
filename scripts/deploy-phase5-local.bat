@echo off
REM Deploy Phase V to Minikube (Windows)
REM This script deploys the complete Phase V system with Dapr + Redpanda Cloud

echo ==========================================
echo Phase V - Local Deployment to Minikube
echo ==========================================
echo.

REM Configuration
set NAMESPACE=default

REM Step 1: Verify prerequisites
echo Step 1: Verifying prerequisites...

where kubectl >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: kubectl not found. Please install kubectl.
    exit /b 1
)

where helm >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: helm not found. Please install Helm 3.
    exit /b 1
)

where minikube >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: minikube not found. Please install Minikube.
    exit /b 1
)

where dapr >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: dapr CLI not found. Please install Dapr CLI.
    echo Visit: https://docs.dapr.io/getting-started/install-dapr-cli/
    exit /b 1
)

echo All prerequisites installed
echo.

REM Step 2: Start Minikube if not running
echo Step 2: Checking Minikube status...

minikube status >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Starting Minikube...
    minikube start --cpus=4 --memory=8192 --driver=docker
) else (
    echo Minikube is running
)

REM Enable ingress addon
minikube addons enable ingress

echo.

REM Step 3: Setup hosts file entry
echo Step 3: Setting up hosts file entry...

for /f "tokens=*" %%i in ('minikube ip') do set MINIKUBE_IP=%%i

findstr /C:"todo.local" %WINDIR%\System32\drivers\etc\hosts >nul
if %ERRORLEVEL% NEQ 0 (
    echo Adding todo.local to hosts file (requires admin)...
    echo %MINIKUBE_IP% todo.local >> %WINDIR%\System32\drivers\etc\hosts
    echo NOTE: If this fails, manually add this line to C:\Windows\System32\drivers\etc\hosts:
    echo %MINIKUBE_IP% todo.local
) else (
    echo todo.local already in hosts file
)

echo.

REM Step 4: Load environment variables
echo Step 4: Loading environment variables...

if not exist .env (
    echo ERROR: .env file not found. Please create .env from .env.example
    echo Copy .env.example to .env and fill in your values.
    exit /b 1
)

REM Load .env file (simple version for Windows)
for /f "usebackq tokens=1,* delims==" %%a in (".env") do (
    set %%a=%%b
)

echo Environment variables loaded
echo.

REM Step 5: Create secrets
echo Step 5: Creating Kubernetes secrets...

kubectl create secret generic todo-secrets ^
  --from-literal=database-url="%DATABASE_URL%" ^
  --from-literal=jwt-secret="%JWT_SECRET%" ^
  --from-literal=gemini-api-key="%GEMINI_API_KEY%" ^
  --from-literal=smtp-user="%SMTP_USER%" ^
  --from-literal=smtp-password="%SMTP_PASSWORD%" ^
  --namespace %NAMESPACE% ^
  --dry-run=client -o yaml | kubectl apply -f -

kubectl create secret generic kafka-secrets ^
  --from-literal=username="%REDPANDA_CLIENT_ID%" ^
  --from-literal=password="%REDPANDA_CLIENT_SECRET%" ^
  --from-literal=bootstrap-server="%REDPANDA_BOOTSTRAP_SERVER%" ^
  --namespace %NAMESPACE% ^
  --dry-run=client -o yaml | kubectl apply -f -

echo Secrets created
echo.

REM Step 6: Run database migrations
echo Step 6: Running database migrations...

cd backend
python migrations\run_migration.py
cd ..

echo Database migrations complete
echo.

REM Step 7: Install Dapr
echo Step 7: Installing Dapr...

dapr status -k >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Installing Dapr to Kubernetes...
    dapr init -k --wait --timeout 300
) else (
    echo Dapr already installed
)

REM Wait for Dapr to be ready
kubectl wait --for=condition=ready pod -l app=dapr-operator -n dapr-system --timeout=300s
kubectl wait --for=condition=ready pod -l app=dapr-sidecar-injector -n dapr-system --timeout=300s
kubectl wait --for=condition=ready pod -l app=dapr-sentry -n dapr-system --timeout=300s

echo Dapr is ready
echo.

REM Step 8: Configure Dapr components
echo Step 8: Configuring Dapr components...

REM Update pubsub.yaml with actual bootstrap server (Windows version)
powershell -Command "(Get-Content k8s\dapr\pubsub.yaml) -replace 'seed-abc123.cloud.redpanda.com:9092', '%REDPANDA_BOOTSTRAP_SERVER%' | Set-Content k8s\dapr\pubsub.yaml"

REM Apply Dapr components
kubectl apply -f k8s\dapr\ --namespace %NAMESPACE%

echo Dapr components configured
echo.

REM Step 9: Build Docker images
echo Step 9: Building Docker images...

REM Point Docker to Minikube's Docker daemon
@echo off
for /f "tokens=*" %%i in ('minikube docker-env --shell cmd') do %%i

REM Build backend
echo Building backend...
docker build -t todo-backend:latest .\backend

REM Build frontend
echo Building frontend...
docker build -t todo-frontend:latest .\frontend

REM Build notification service
echo Building notification service...
docker build -t notification-service:latest .\services\notification-service

REM Build recurring service
echo Building recurring service...
docker build -t recurring-service:latest .\services\recurring-service

REM Build audit service
echo Building audit service...
docker build -t audit-service:latest .\services\audit-service

echo Docker images built
echo.

REM Step 10: Deploy with Helm
echo Step 10: Deploying application with Helm...

helm upgrade --install todo-app .\helm-chart ^
  --namespace %NAMESPACE% ^
  --set frontend.image.repository=todo-frontend ^
  --set frontend.image.tag=latest ^
  --set frontend.image.pullPolicy=Never ^
  --set backend.image.repository=todo-backend ^
  --set backend.image.tag=latest ^
  --set backend.image.pullPolicy=Never ^
  --set notificationService.image.repository=notification-service ^
  --set notificationService.image.tag=latest ^
  --set notificationService.image.pullPolicy=Never ^
  --set recurringService.image.repository=recurring-service ^
  --set recurringService.image.tag=latest ^
  --set recurringService.image.pullPolicy=Never ^
  --set auditService.image.repository=audit-service ^
  --set auditService.image.tag=latest ^
  --set auditService.image.pullPolicy=Never ^
  --set dapr.enabled=true ^
  --wait --timeout 10m

echo Application deployed
echo.

REM Step 11: Wait for deployments
echo Step 11: Waiting for deployments to be ready...

kubectl wait --for=condition=available deployment/frontend --timeout=300s --namespace %NAMESPACE%
kubectl wait --for=condition=available deployment/backend --timeout=300s --namespace %NAMESPACE%
kubectl wait --for=condition=available deployment/notification-service --timeout=300s --namespace %NAMESPACE%
kubectl wait --for=condition=available deployment/recurring-service --timeout=300s --namespace %NAMESPACE%
kubectl wait --for=condition=available deployment/audit-service --timeout=300s --namespace %NAMESPACE%

echo All deployments ready
echo.

REM Step 12: Display access information
echo ==========================================
echo Deployment Complete!
echo ==========================================
echo.
echo Access URLs:
echo   Frontend: http://todo.local
echo   Backend API: http://todo.local/api
echo   Health Check: http://todo.local/api/health
echo.
echo Verify deployment:
echo   kubectl get pods -n %NAMESPACE%
echo   kubectl get svc -n %NAMESPACE%
echo   kubectl get ingress -n %NAMESPACE%
echo.
echo View logs:
echo   kubectl logs -f deployment/backend -n %NAMESPACE%
echo   kubectl logs -f deployment/frontend -n %NAMESPACE%
echo   kubectl logs -f deployment/notification-service -n %NAMESPACE%
echo.
echo Run tests:
echo   cd tests
echo   run_all_tests.bat
echo.
echo ==========================================
