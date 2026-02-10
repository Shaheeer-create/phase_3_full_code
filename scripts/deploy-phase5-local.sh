#!/bin/bash
# Deploy Phase V to Minikube (Local Development)
# This script deploys the complete Phase V system with Dapr + Redpanda Cloud

set -e

echo "=========================================="
echo "Phase V - Local Deployment to Minikube"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
NAMESPACE="default"

# Step 1: Verify prerequisites
echo -e "${YELLOW}Step 1: Verifying prerequisites...${NC}"

if ! command -v kubectl &> /dev/null; then
    echo -e "${RED}❌ kubectl not found. Please install kubectl.${NC}"
    exit 1
fi

if ! command -v helm &> /dev/null; then
    echo -e "${RED}❌ helm not found. Please install Helm 3.${NC}"
    exit 1
fi

if ! command -v minikube &> /dev/null; then
    echo -e "${RED}❌ minikube not found. Please install Minikube.${NC}"
    exit 1
fi

if ! command -v dapr &> /dev/null; then
    echo -e "${RED}❌ dapr CLI not found. Installing Dapr CLI...${NC}"
    wget -q https://raw.githubusercontent.com/dapr/cli/master/install/install.sh -O - | /bin/bash
fi

echo -e "${GREEN}✓ All prerequisites installed${NC}"
echo ""

# Step 2: Start Minikube if not running
echo -e "${YELLOW}Step 2: Checking Minikube status...${NC}"

if ! minikube status &> /dev/null; then
    echo "Starting Minikube..."
    minikube start --cpus=4 --memory=8192 --driver=docker
else
    echo -e "${GREEN}✓ Minikube is running${NC}"
fi

# Enable ingress addon
minikube addons enable ingress

echo ""

# Step 3: Setup /etc/hosts entry
echo -e "${YELLOW}Step 3: Setting up /etc/hosts entry...${NC}"

MINIKUBE_IP=$(minikube ip)
if ! grep -q "todo.local" /etc/hosts; then
    echo "Adding todo.local to /etc/hosts (requires sudo)..."
    echo "$MINIKUBE_IP todo.local" | sudo tee -a /etc/hosts
else
    echo -e "${GREEN}✓ todo.local already in /etc/hosts${NC}"
fi

echo ""

# Step 4: Create secrets
echo -e "${YELLOW}Step 4: Creating Kubernetes secrets...${NC}"

if [ ! -f ".env" ]; then
    echo -e "${RED}❌ .env file not found. Please create .env with required variables.${NC}"
    echo "Required variables:"
    echo "  DATABASE_URL=postgresql://..."
    echo "  JWT_SECRET=your-secret"
    echo "  GEMINI_API_KEY=your-key"
    echo "  REDPANDA_BOOTSTRAP_SERVER=seed-xxx.cloud.redpanda.com:9092"
    echo "  REDPANDA_CLIENT_ID=your-client-id"
    echo "  REDPANDA_CLIENT_SECRET=your-client-secret"
    exit 1
fi

# Load environment variables
export $(cat .env | xargs)

# Create secrets
kubectl create secret generic todo-secrets \
  --from-literal=database-url="$DATABASE_URL" \
  --from-literal=jwt-secret="$JWT_SECRET" \
  --from-literal=gemini-api-key="$GEMINI_API_KEY" \
  --from-literal=smtp-user="${SMTP_USER:-}" \
  --from-literal=smtp-password="${SMTP_PASSWORD:-}" \
  --namespace "$NAMESPACE" \
  --dry-run=client -o yaml | kubectl apply -f -

kubectl create secret generic kafka-secrets \
  --from-literal=username="$REDPANDA_CLIENT_ID" \
  --from-literal=password="$REDPANDA_CLIENT_SECRET" \
  --from-literal=bootstrap-server="$REDPANDA_BOOTSTRAP_SERVER" \
  --namespace "$NAMESPACE" \
  --dry-run=client -o yaml | kubectl apply -f -

echo -e "${GREEN}✓ Secrets created${NC}"
echo ""

# Step 5: Run database migrations
echo -e "${YELLOW}Step 5: Running database migrations...${NC}"

cd backend
python migrations/run_migration.py
cd ..

echo -e "${GREEN}✓ Database migrations complete${NC}"
echo ""

# Step 6: Install Dapr
echo -e "${YELLOW}Step 6: Installing Dapr...${NC}"

if ! dapr status -k &> /dev/null; then
    echo "Installing Dapr to Kubernetes..."
    dapr init -k --wait --timeout 300
else
    echo -e "${GREEN}✓ Dapr already installed${NC}"
fi

# Wait for Dapr to be ready
kubectl wait --for=condition=ready pod -l app=dapr-operator -n dapr-system --timeout=300s
kubectl wait --for=condition=ready pod -l app=dapr-sidecar-injector -n dapr-system --timeout=300s
kubectl wait --for=condition=ready pod -l app=dapr-sentry -n dapr-system --timeout=300s

echo -e "${GREEN}✓ Dapr is ready${NC}"
echo ""

# Step 7: Update Dapr pubsub component with actual bootstrap server
echo -e "${YELLOW}Step 7: Configuring Dapr components...${NC}"

# Update pubsub.yaml with actual bootstrap server
sed -i.bak "s|seed-abc123.cloud.redpanda.com:9092|$REDPANDA_BOOTSTRAP_SERVER|g" k8s/dapr/pubsub.yaml

# Apply Dapr components
kubectl apply -f k8s/dapr/ --namespace "$NAMESPACE"

echo -e "${GREEN}✓ Dapr components configured${NC}"
echo ""

# Step 8: Build Docker images
echo -e "${YELLOW}Step 8: Building Docker images...${NC}"

# Point Docker to Minikube's Docker daemon
eval $(minikube docker-env)

# Build backend
echo "Building backend..."
docker build -t todo-backend:latest ./backend

# Build frontend
echo "Building frontend..."
docker build -t todo-frontend:latest ./frontend

# Build notification service
echo "Building notification service..."
docker build -t notification-service:latest ./services/notification-service

# Build recurring service
echo "Building recurring service..."
docker build -t recurring-service:latest ./services/recurring-service

# Build audit service
echo "Building audit service..."
docker build -t audit-service:latest ./services/audit-service

echo -e "${GREEN}✓ Docker images built${NC}"
echo ""

# Step 9: Deploy with Helm
echo -e "${YELLOW}Step 9: Deploying application with Helm...${NC}"

helm upgrade --install todo-app ./helm-chart \
  --namespace "$NAMESPACE" \
  --set frontend.image.repository=todo-frontend \
  --set frontend.image.tag=latest \
  --set frontend.image.pullPolicy=Never \
  --set backend.image.repository=todo-backend \
  --set backend.image.tag=latest \
  --set backend.image.pullPolicy=Never \
  --set notificationService.image.repository=notification-service \
  --set notificationService.image.tag=latest \
  --set notificationService.image.pullPolicy=Never \
  --set recurringService.image.repository=recurring-service \
  --set recurringService.image.tag=latest \
  --set recurringService.image.pullPolicy=Never \
  --set auditService.image.repository=audit-service \
  --set auditService.image.tag=latest \
  --set auditService.image.pullPolicy=Never \
  --set dapr.enabled=true \
  --wait --timeout 10m

echo -e "${GREEN}✓ Application deployed${NC}"
echo ""

# Step 10: Wait for deployments
echo -e "${YELLOW}Step 10: Waiting for deployments to be ready...${NC}"

kubectl wait --for=condition=available deployment/frontend --timeout=300s --namespace "$NAMESPACE"
kubectl wait --for=condition=available deployment/backend --timeout=300s --namespace "$NAMESPACE"
kubectl wait --for=condition=available deployment/notification-service --timeout=300s --namespace "$NAMESPACE"
kubectl wait --for=condition=available deployment/recurring-service --timeout=300s --namespace "$NAMESPACE"
kubectl wait --for=condition=available deployment/audit-service --timeout=300s --namespace "$NAMESPACE"

echo -e "${GREEN}✓ All deployments ready${NC}"
echo ""

# Step 11: Display access information
echo "=========================================="
echo "Deployment Complete!"
echo "=========================================="
echo ""
echo "Access URLs:"
echo "  Frontend: http://todo.local"
echo "  Backend API: http://todo.local/api"
echo "  Health Check: http://todo.local/api/health"
echo ""
echo "Verify deployment:"
echo "  kubectl get pods -n $NAMESPACE"
echo "  kubectl get svc -n $NAMESPACE"
echo "  kubectl get ingress -n $NAMESPACE"
echo ""
echo "View logs:"
echo "  kubectl logs -f deployment/backend -n $NAMESPACE"
echo "  kubectl logs -f deployment/frontend -n $NAMESPACE"
echo "  kubectl logs -f deployment/notification-service -n $NAMESPACE"
echo ""
echo "Run tests:"
echo "  cd tests"
echo "  ./run_all_tests.sh"
echo ""
echo "=========================================="
