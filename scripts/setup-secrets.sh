#!/bin/bash
# Setup Kubernetes Secrets for Phase V
# This script creates all required secrets for the Todo App deployment

set -e

echo "=== Setting up Kubernetes Secrets for Phase V ==="
echo ""

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    echo "❌ kubectl not found. Please install kubectl first."
    exit 1
fi

# Check if we're connected to a cluster
if ! kubectl cluster-info &> /dev/null; then
    echo "❌ Not connected to a Kubernetes cluster."
    echo "Please start Minikube: minikube start"
    exit 1
fi

echo "✓ Connected to Kubernetes cluster"
echo ""

# Prompt for required environment variables if not set
if [ -z "$DATABASE_URL" ]; then
    echo "Enter your Neon PostgreSQL DATABASE_URL:"
    read -r DATABASE_URL
fi

if [ -z "$JWT_SECRET" ]; then
    echo "Enter your JWT_SECRET (or press Enter to generate one):"
    read -r JWT_SECRET
    if [ -z "$JWT_SECRET" ]; then
        JWT_SECRET=$(openssl rand -base64 32)
        echo "Generated JWT_SECRET: $JWT_SECRET"
    fi
fi

if [ -z "$GEMINI_API_KEY" ]; then
    echo "Enter your Google Gemini API key:"
    read -r GEMINI_API_KEY
fi

if [ -z "$REDPANDA_BOOTSTRAP_SERVER" ]; then
    echo "Enter your Redpanda Cloud bootstrap server (e.g., seed-abc123.cloud.redpanda.com:9092):"
    read -r REDPANDA_BOOTSTRAP_SERVER
fi

# Redpanda credentials (provided by user)
REDPANDA_CLIENT_ID="${REDPANDA_CLIENT_ID:-WII4vQ2cFUwWoJbcuydvOjH097QL90C8}"
REDPANDA_CLIENT_SECRET="${REDPANDA_CLIENT_SECRET:-sxOloXPgn1S24C3fVk0l854IVRmD8TmUJaxQo3iK4PV3FjgMWmb8rjlUakLiMqf_}"

# Optional: SMTP credentials for email notifications
SMTP_USER="${SMTP_USER:-}"
SMTP_PASSWORD="${SMTP_PASSWORD:-}"

echo ""
echo "Creating Kubernetes secrets..."
echo ""

# Create namespace if it doesn't exist
kubectl create namespace default --dry-run=client -o yaml | kubectl apply -f -

# Create todo-secrets (main application secrets)
kubectl create secret generic todo-secrets \
  --from-literal=database-url="$DATABASE_URL" \
  --from-literal=jwt-secret="$JWT_SECRET" \
  --from-literal=gemini-api-key="$GEMINI_API_KEY" \
  --from-literal=smtp-user="$SMTP_USER" \
  --from-literal=smtp-password="$SMTP_PASSWORD" \
  --namespace default \
  --dry-run=client -o yaml | kubectl apply -f -

echo "✓ Created secret: todo-secrets"

# Create kafka-secrets (Redpanda Cloud credentials)
kubectl create secret generic kafka-secrets \
  --from-literal=username="$REDPANDA_CLIENT_ID" \
  --from-literal=password="$REDPANDA_CLIENT_SECRET" \
  --from-literal=bootstrap-server="$REDPANDA_BOOTSTRAP_SERVER" \
  --namespace default \
  --dry-run=client -o yaml | kubectl apply -f -

echo "✓ Created secret: kafka-secrets"

echo ""
echo "=== Secrets Setup Complete ==="
echo ""
echo "Secrets created:"
echo "  ✓ todo-secrets (database, jwt, gemini, smtp)"
echo "  ✓ kafka-secrets (redpanda credentials)"
echo ""
echo "Next step: Update k8s/dapr/pubsub.yaml with your Redpanda bootstrap server"
echo "Then run: ./scripts/deploy-phase5-local.sh"
