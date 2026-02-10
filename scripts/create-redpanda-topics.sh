#!/bin/bash
# Create Redpanda Cloud Topics
# This script creates the required topics for Phase V

# Redpanda Cloud connection details
BOOTSTRAP_SERVER="your-cluster-url.cloud.redpanda.com:9092"
CLIENT_ID="WII4vQ2cFUwWoJbcuydvOjH097QL90C8"
CLIENT_SECRET="sxOloXPgn1S24C3fVk0l854IVRmD8TmUJaxQo3iK4PV3FjgMWmb8rjlUakLiMqf_"

echo "Creating Redpanda Cloud topics..."

# Note: You need to create topics via Redpanda Console UI
# Navigate to: https://cloud.redpanda.com/clusters/<your-cluster>/topics

echo "Please create the following topics in Redpanda Console:"
echo ""
echo "1. Topic: reminder-events"
echo "   - Partitions: 3"
echo "   - Retention: 7 days (604800000 ms)"
echo "   - Cleanup policy: delete"
echo ""
echo "2. Topic: recurring-events"
echo "   - Partitions: 3"
echo "   - Retention: 7 days (604800000 ms)"
echo "   - Cleanup policy: delete"
echo ""
echo "You already have: task-events ✓"
echo ""
echo "After creating topics, run: ./scripts/verify-redpanda-connection.sh"
