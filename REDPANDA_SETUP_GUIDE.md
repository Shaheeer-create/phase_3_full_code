# Redpanda Cloud Setup Guide - Complete Walkthrough

**Time Required:** 10-15 minutes
**Cost:** FREE (Serverless tier)

---

## Step 1: Sign Up and Create Cluster ✅ (You've Done This)

You mentioned you've already:
- ✅ Signed up at https://redpanda.com/cloud
- ✅ Created a cluster

**Important:** You only need **ONE cluster** for all 3 topics. Don't create multiple clusters.

---

## Step 2: Create Topics (3 Topics in Your Existing Cluster)

### Navigate to Topics
1. **Log in** to Redpanda Cloud Console: https://cloud.redpanda.com
2. **Click on your cluster** (the one you created)
3. In the left sidebar, click **"Topics"**

### Create Topic 1: task-events

1. Click the **"Create Topic"** button (top right)
2. Fill in the form:
   ```
   Topic Name: task-events
   Partitions: 3
   Replication Factor: 3 (default, don't change)
   Retention Time: 7 days (168 hours)
   Retention Size: Unlimited
   Cleanup Policy: Delete
   ```
3. Click **"Create"**

### Create Topic 2: reminder-events

1. Click **"Create Topic"** again
2. Fill in the form:
   ```
   Topic Name: reminder-events
   Partitions: 3
   Replication Factor: 3
   Retention Time: 7 days (168 hours)
   Retention Size: Unlimited
   Cleanup Policy: Delete
   ```
3. Click **"Create"**

### Create Topic 3: recurring-events

1. Click **"Create Topic"** again
2. Fill in the form:
   ```
   Topic Name: recurring-events
   Partitions: 3
   Replication Factor: 3
   Retention Time: 7 days (168 hours)
   Retention Size: Unlimited
   Cleanup Policy: Delete
   ```
3. Click **"Create"**

### Verify Topics Created
You should now see 3 topics in the Topics list:
- ✅ task-events
- ✅ reminder-events
- ✅ recurring-events

---

## Step 3: Get Connection Credentials

### Method 1: From Cluster Overview (Recommended)

1. **Go back to your cluster** (click cluster name in top breadcrumb)
2. You should see the **"Overview"** tab
3. Look for a section called **"Bootstrap Server"** or **"Connection Details"**
4. You'll see something like:
   ```
   Bootstrap servers: seed-abc123.cloud.redpanda.com:9092
   ```
5. **Copy this URL** - you'll need it later

### Method 2: From "How to Connect" Section

1. In your cluster, look for **"How to Connect"** or **"Connect"** tab
2. Click on it
3. You'll see connection details including:
   - **Bootstrap servers** (the Kafka broker URL)
   - **SASL mechanism** (usually SCRAM-SHA-256)
   - Instructions for creating credentials

---

## Step 4: Create SASL Credentials (Authentication)

### Navigate to Security/Users

1. In your cluster, find the **"Security"** tab in the left sidebar
   - OR look for **"Users"** or **"ACLs"**
2. Click on **"Users"** or **"Create User"**

### Create a New User

1. Click **"Create User"** or **"Add User"**
2. Fill in:
   ```
   Username: todo-app-user
   Password: [Generate a strong password or let Redpanda generate one]
   Mechanism: SCRAM-SHA-256
   ```
3. Click **"Create"**

### Set Permissions (ACLs)

After creating the user, you need to grant permissions:

1. Still in the **Security/Users** section
2. Click on your user (**todo-app-user**)
3. Click **"Add ACL"** or **"Permissions"**
4. Grant the following permissions:

   **For topic: task-events**
   ```
   Resource Type: Topic
   Resource Name: task-events
   Pattern Type: Literal
   Operations: Read, Write, Describe
   ```

   **For topic: reminder-events**
   ```
   Resource Type: Topic
   Resource Name: reminder-events
   Pattern Type: Literal
   Operations: Read, Write, Describe
   ```

   **For topic: recurring-events**
   ```
   Resource Type: Topic
   Resource Name: recurring-events
   Pattern Type: Literal
   Operations: Read, Write, Describe
   ```

   **For consumer group**
   ```
   Resource Type: Group
   Resource Name: todo-app
   Pattern Type: Literal
   Operations: Read
   ```

5. Click **"Save"** or **"Add"** for each ACL

---

## Step 5: Collect All Credentials

You should now have:

1. **Bootstrap Server URL**
   ```
   Example: seed-abc123.cloud.redpanda.com:9092
   ```

2. **SASL Username**
   ```
   Example: todo-app-user
   ```

3. **SASL Password**
   ```
   Example: your-generated-password
   ```

4. **SASL Mechanism**
   ```
   SCRAM-SHA-256
   ```

**IMPORTANT:** Save these credentials securely! You'll need them in the next step.

---

## Step 6: Update Your Configuration Files

### Update Dapr Pub/Sub Component

1. Open the file: `k8s/dapr/pubsub.yaml`

2. Find this section:
   ```yaml
   metadata:
   - name: brokers
     value: "seed-abc123.cloud.redpanda.com:9092"  # REPLACE THIS
   ```

3. Replace with **YOUR** bootstrap server URL:
   ```yaml
   metadata:
   - name: brokers
     value: "YOUR_BOOTSTRAP_SERVER_URL:9092"
   ```

   Example:
   ```yaml
   metadata:
   - name: brokers
     value: "seed-f8a2b1c3.cloud.redpanda.com:9092"
   ```

### Create Kubernetes Secret with Credentials

Run this command (replace with your actual credentials):

```bash
kubectl create secret generic kafka-secrets \
  --from-literal=username='todo-app-user' \
  --from-literal=password='YOUR_ACTUAL_PASSWORD' \
  --namespace default
```

Example:
```bash
kubectl create secret generic kafka-secrets \
  --from-literal=username='todo-app-user' \
  --from-literal=password='xK9mP2nQ5rT8wY3zA6bC' \
  --namespace default
```

---

## Step 7: Verify Configuration

### Test Connection (Optional but Recommended)

You can test the connection using `kcat` (formerly `kafkacat`):

```bash
# Install kcat (macOS)
brew install kcat

# Test connection
kcat -b YOUR_BOOTSTRAP_SERVER:9092 \
  -X security.protocol=SASL_SSL \
  -X sasl.mechanism=SCRAM-SHA-256 \
  -X sasl.username=todo-app-user \
  -X sasl.password=YOUR_PASSWORD \
  -L
```

If successful, you'll see a list of topics including your 3 topics.

---

## Common Issues and Solutions

### Issue 1: "Can't find Bootstrap Server"
**Solution:**
- Go to Cluster → Overview
- Look for "Connection Details" or "Bootstrap Server"
- It should be in format: `seed-xxxxx.cloud.redpanda.com:9092`

### Issue 2: "Authentication Failed"
**Solution:**
- Verify username and password are correct
- Check that SASL mechanism is SCRAM-SHA-256
- Verify ACLs are set correctly for the user

### Issue 3: "Topic Not Found"
**Solution:**
- Go to Topics tab
- Verify all 3 topics exist: task-events, reminder-events, recurring-events
- Check spelling matches exactly

### Issue 4: "Permission Denied"
**Solution:**
- Go to Security → Users → Your User
- Verify ACLs are set for all 3 topics
- Ensure Read, Write, Describe permissions are granted

---

## Quick Reference Card

Save this for later:

```
REDPANDA CLOUD CREDENTIALS
==========================

Cluster Name: [Your cluster name]
Bootstrap Server: [seed-xxxxx.cloud.redpanda.com:9092]
SASL Username: [todo-app-user]
SASL Password: [your-password]
SASL Mechanism: SCRAM-SHA-256

Topics Created:
✓ task-events (3 partitions)
✓ reminder-events (3 partitions)
✓ recurring-events (3 partitions)

Consumer Group: todo-app
```

---

## Next Steps

After completing this setup:

1. ✅ Update `k8s/dapr/pubsub.yaml` with your bootstrap server
2. ✅ Create Kubernetes secret with your credentials
3. ✅ Continue with deployment guide (Step 6: Run Migrations)

---

## Visual Navigation Guide

Here's where to find everything in Redpanda Console:

```
Redpanda Cloud Console
├── Clusters (left sidebar)
│   └── [Your Cluster]
│       ├── Overview (Bootstrap Server here)
│       ├── Topics (Create topics here)
│       │   ├── task-events
│       │   ├── reminder-events
│       │   └── recurring-events
│       ├── Security / Users (Create user here)
│       │   └── todo-app-user
│       │       └── ACLs (Set permissions here)
│       └── How to Connect (Connection details)
```

---

## Troubleshooting Checklist

Before proceeding, verify:

- [ ] Cluster is running (status: Active)
- [ ] 3 topics created with correct names
- [ ] User created with SCRAM-SHA-256
- [ ] ACLs set for all 3 topics
- [ ] ACL set for consumer group
- [ ] Bootstrap server URL copied
- [ ] Username and password saved
- [ ] `k8s/dapr/pubsub.yaml` updated
- [ ] Kubernetes secret created

---

## Need Help?

If you're stuck:

1. **Check Redpanda Documentation:** https://docs.redpanda.com/docs/get-started/quick-start-cloud/
2. **Redpanda Community:** https://redpanda.com/slack
3. **Common issue:** If you can't find "Security" or "Users" tab, try:
   - Look for "Access Control"
   - Look for "SASL"
   - Check under cluster settings

---

**Last Updated:** 2026-02-07
**Next:** Continue with DEPLOYMENT_GUIDE.md Step 6
