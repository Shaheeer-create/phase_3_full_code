#!/bin/bash
# Verify Redpanda Cloud Connection
# This script tests connectivity to Redpanda Cloud and lists topics

set -e

echo "=== Verifying Redpanda Cloud Connection ==="
echo ""

# Check if kafkacat/kcat is installed
if ! command -v kcat &> /dev/null && ! command -v kafkacat &> /dev/null; then
    echo "❌ kcat/kafkacat not found. Installing..."
    echo "Run: brew install kcat (Mac) or apt-get install kafkacat (Linux)"
    exit 1
fi

# Use kcat if available, otherwise kafkacat
KAFKA_CMD="kcat"
if ! command -v kcat &> /dev/null; then
    KAFKA_CMD="kafkacat"
fi

# Redpanda Cloud connection details
BOOTSTRAP_SERVER="${REDPANDA_BOOTSTRAP_SERVER}"
CLIENT_ID="${REDPANDA_CLIENT_ID}"
CLIENT_SECRET="${REDPANDA_CLIENT_SECRET}"

if [ -z "$BOOTSTRAP_SERVER" ] || [ -z "$CLIENT_ID" ] || [ -z "$CLIENT_SECRET" ]; then
    echo "❌ Missing environment variables. Please set:"
    echo "   export REDPANDA_BOOTSTRAP_SERVER='your-cluster.cloud.redpanda.com:9092'"
    echo "   export REDPANDA_CLIENT_ID='WII4vQ2cFUwWoJbcuydvOjH097QL90C8'"
    echo "   export REDPANDA_CLIENT_SECRET='sxOloXPgn1S24C3fVk0l854IVRmD8TmUJaxQo3iK4PV3FjgMWmb8rjlUakLiMqf_'"
    exit 1
fi

echo "Testing connection to: $BOOTSTRAP_SERVER"
echo ""

# List topics
echo "Listing topics..."
$KAFKA_CMD -b "$BOOTSTRAP_SERVER" \
    -X security.protocol=SASL_SSL \
    -X sasl.mechanisms=SCRAM-SHA-256 \
    -X sasl.username="$CLIENT_ID" \
    -X sasl.password="$CLIENT_SECRET" \
    -L

echo ""
echo "=== Connection Test Complete ==="
echo ""
echo "Expected topics:"
echo "  ✓ task-events"
echo "  ✓ reminder-events"
echo "  ✓ recurring-events"
echo ""
echo "If all 3 topics are listed above, you're ready to deploy!"
