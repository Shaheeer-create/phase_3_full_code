# Todo Chatbot - Kubernetes Deployment Guide

**Complete guide to deploy and run the Todo Chatbot application on local Kubernetes using Minikube.**

---

## 📍 Quick Navigation

- **First time deploying?** → Start with [Prerequisites](#prerequisites)
- **Already deployed?** → Jump to [Daily Usage](#daily-usage-quick-start)
- **Having issues?** → Check [Troubleshooting](#troubleshooting)

---

## 🚀 What is This Project?

**Todo Chatbot** is a full-stack web application combining task management with AI-powered assistance:

### Tech Stack
- **Frontend:** Next.js 16 (App Router), TypeScript, Tailwind CSS
- **Backend:** Python FastAPI with SQLModel ORM
- **Database:** Neon Serverless PostgreSQL (cloud-hosted)
- **AI:** Google Gemini 2.5 Flash for intelligent task management
- **Auth:** Better Auth with JWT tokens
- **Deployment:** Kubernetes (Minikube) with Helm charts

### Key Features
- ✅ User authentication (signup/login)
- ✅ Task CRUD operations (create, read, update, delete)
- ✅ AI chatbot that creates tasks via natural language
- ✅ Real-time streaming AI responses
- ✅ Multi-user support with data isolation
- ✅ Persistent storage in PostgreSQL

---

## 📁 Project Location

```
E:\quarter4\hacakthon-2\phase_3_copy
```

**All commands in this guide should be run from this directory unless otherwise specified.**

---

## Daily Usage (Quick Start)

### If You've Already Deployed

**1. Start Minikube Cluster**
```powershell
cd E:\quarter4\hacakthon-2\phase_3_copy
minikube start -p todo-cluster
```

**2. Verify Pods are Running**
```powershell
kubectl get pods
```

**Expected Output:**
```
NAME                        READY   STATUS    RESTARTS   AGE
backend-745f578dd7-mxxm7    1/1     Running   0          5m
backend-745f578dd7-rl4d8    1/1     Running   0          5m
frontend-696bd654f9-fqlbj   1/1     Running   0          5m
frontend-696bd654f9-rl2wl   1/1     Running   0          5m
```

**3. Start Minikube Tunnel (Administrator PowerShell)**
```powershell
minikube tunnel -p todo-cluster
```

**Expected Output:**
```
* Tunnel successfully started
* NOTE: Please do not close this terminal as this process must stay alive for the tunnel to be accessible ...
* Starting tunnel for service todo-chatbot-api.
* Starting tunnel for service todo-chatbot-auth.
* Starting tunnel for service todo-chatbot-frontend.
```

**⚠️ Keep this terminal window open!**

**4. Access the Application**

Open browser: **http://todo.local**

---

## Prerequisites

### Required Software

1. **Docker Desktop** (v24.0.0+)
   - Download: https://www.docker.com/products/docker-desktop/
   - Verify: `docker --version`

2. **Minikube** (v1.32.0+)
   ```powershell
   choco install minikube
   ```
   - Verify: `minikube version`

3. **kubectl** (v1.28.0+)
   ```powershell
   choco install kubernetes-cli
   ```
   - Verify: `kubectl version --client`

4. **Helm** (v3.13.0+)
   ```powershell
   choco install kubernetes-helm
   ```
   - Verify: `helm version`

### Required Credentials

You need these three secrets (already configured in the project):

1. **DATABASE_URL** - Neon PostgreSQL connection string
2. **GEMINI_API_KEY** - Google Gemini API key
3. **BETTER_AUTH_SECRET** - Authentication secret (32+ characters)

These are stored in `backend/.env` for reference but will be created as Kubernetes secrets during deployment.

---

## First Time Deployment

### Step 1: Start Minikube Cluster

```powershell
cd E:\quarter4\hacakthon-2\phase_3_copy
minikube start --driver=docker --cpus=2 --memory=3072 -p todo-cluster
```

**Expected Output:**
```
😄  [todo-cluster] minikube v1.38.0 on Microsoft Windows 10 Pro 22H2
✨  Using the docker driver based on user configuration
📌  Using Docker Desktop driver with root privileges
👍  Starting "todo-cluster" primary control-plane node in "todo-cluster" cluster
🚜  Pulling base image v0.0.49 ...
🔗  Configuring bridge CNI (Container Networking Interface) ...
🔎  Verifying Kubernetes components...
🌟  Enabled addons: default-storageclass, storage-provisioner
🏄  Done! kubectl is now configured to use "todo-cluster" cluster and "default" namespace by default
```

**Verify cluster is running:**
```powershell
kubectl get nodes
```

**Expected Output:**
```
NAME           STATUS   ROLES           AGE   VERSION
todo-cluster   Ready    control-plane   99s   v1.35.0
```

---

### Step 2: Enable Ingress Controller

```powershell
minikube addons enable ingress -p todo-cluster
```

**Expected Output:**
```
💡  ingress is an addon maintained by Kubernetes. For any concerns contact minikube on GitHub.
    ▪ Using image registry.k8s.io/ingress-nginx/controller:v1.14.1
    ▪ Using image registry.k8s.io/ingress-nginx/kube-webhook-certgen:v1.6.5
🔎  Verifying ingress addon...
🌟  The 'ingress' addon is enabled
```

---

### Step 3: Build Docker Images

**Set Docker environment to use Minikube's Docker daemon:**
```powershell
minikube -p todo-cluster docker-env --shell powershell | Invoke-Expression
```

**Build Backend Image:**
```powershell
cd backend
docker build -t todo-backend:latest .
```

**Expected Output:**
```
#13 exporting to image
#13 exporting layers 1.2s done
#13 writing image sha256:7993bc0a3252748a110f707058731610b115fb4908bb26f4c7f1492850ab4163 done
#13 naming to docker.io/library/todo-backend:latest 0.0s done
```

**Build Frontend Image:**
```powershell
cd ../frontend
docker build -t todo-frontend:v3.0 .
```

**Expected Output:**
```
#18 exporting to image
#18 exporting layers 4.0s done
#18 writing image sha256:a037d3330b1d0ee9016b819250bd423cec95304f51e1b503a07e6f0affbb1484 done
#18 naming to docker.io/library/todo-frontend:v3.0 0.0s done
```

**Verify images:**
```powershell
cd ..
docker images | findstr todo
```

**Expected Output:**
```
todo-frontend   v3.0     a037d3330b1d   2 minutes ago   450MB
todo-backend    latest   7993bc0a3252   5 minutes ago   380MB
```

---

### Step 4: Create Kubernetes Secrets

```powershell
kubectl create secret generic todo-secrets `
  --from-literal=database-url='postgresql://neondb_owner:npg_HRljDCgkn36r@ep-tiny-unit-ah26hi7v-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require' `
  --from-literal=better-auth-secret='zRfivV__JY648KCDbRYbkK5TN7Jzb23YiAOx2dvYmWE' `
  --from-literal=gemini-api-key='AIzaSyDj_avs25ROuIHpGMN_zy2hQZX-VXt5qWM'
```

**Expected Output:**
```
secret/todo-secrets created
```

**Verify secret:**
```powershell
kubectl get secret todo-secrets
```

**Expected Output:**
```
NAME           TYPE     DATA   AGE
todo-secrets   Opaque   3      10s
```

---

### Step 5: Deploy with Helm

```powershell
helm install todo-chatbot ./helm-chart
```

**Expected Output:**
```
NAME: todo-chatbot
LAST DEPLOYED: Wed Feb  4 14:49:54 2026
NAMESPACE: default
STATUS: deployed
REVISION: 1
DESCRIPTION: Install complete
TEST SUITE: None
```

**Verify deployment:**
```powershell
kubectl get pods
```

**Expected Output (wait 1-2 minutes for all pods to be Running):**
```
NAME                        READY   STATUS    RESTARTS   AGE
backend-745f578dd7-mxxm7    1/1     Running   0          2m
backend-745f578dd7-rl4d8    1/1     Running   0          2m
frontend-696bd654f9-fqlbj   1/1     Running   0          2m
frontend-696bd654f9-rl2wl   1/1     Running   0          2m
```

**Check services:**
```powershell
kubectl get services
```

**Expected Output:**
```
NAME         TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)    AGE
backend      ClusterIP   10.102.16.129   <none>        8001/TCP   2m
frontend     ClusterIP   10.107.189.88   <none>        3000/TCP   2m
kubernetes   ClusterIP   10.96.0.1       <none>        443/TCP    10m
```

**Check ingress:**
```powershell
kubectl get ingress
```

**Expected Output:**
```
NAME                    CLASS   HOSTS        ADDRESS        PORTS   AGE
todo-chatbot-api        nginx   todo.local   192.168.58.2   80      2m
todo-chatbot-auth       nginx   todo.local   192.168.58.2   80      2m
todo-chatbot-frontend   nginx   todo.local   192.168.58.2   80      2m
```

---

### Step 6: Configure Local Access

**Update Hosts File (Run as Administrator):**

```powershell
Add-Content -Path C:\Windows\System32\drivers\etc\hosts -Value "`n127.0.0.1 todo.local"
```

**Or manually edit:** `C:\Windows\System32\drivers\etc\hosts`

Add this line:
```
127.0.0.1 todo.local
```

---

### Step 7: Start Minikube Tunnel

**Open a NEW PowerShell window as Administrator:**

```powershell
minikube tunnel -p todo-cluster
```

**Expected Output:**
```
* Tunnel successfully started

* NOTE: Please do not close this terminal as this process must stay alive for the tunnel to be accessible ...

* Starting tunnel for service todo-chatbot-api.
* Starting tunnel for service todo-chatbot-auth.
* Starting tunnel for service todo-chatbot-frontend.
```

**⚠️ CRITICAL: Keep this terminal window open while using the application!**

---

### Step 8: Test the Application

**Open browser and navigate to:**
```
http://todo.local
```

**Expected:** Todo App homepage loads with "Sign Up" and "Login" buttons

**Test Signup:**
1. Click "Sign Up"
2. Enter email: `your-email@example.com`
3. Enter password: `YourPassword123!`
4. Enter name: `Your Name`
5. Click "Sign Up"

**Expected:** Redirected to tasks page (http://todo.local/tasks)

**Test Task Creation:**
1. Click "Add Task" or "+" button
2. Enter title: "Test Kubernetes Deployment"
3. Enter description (optional)
4. Click "Save"

**Expected:** Task appears in the list

**Test AI Chatbot:**
1. Navigate to "Chat" page
2. Click "New Conversation"
3. Send message: "Create a task to test AI integration"

**Expected:**
- AI responds with streaming text
- Task is created and visible in Tasks page
- No 404 or 500 errors

---

## Troubleshooting

### Issue 1: Pods in CrashLoopBackOff or Error State

**Check pod logs:**
```powershell
kubectl logs <pod-name>
```

**Common causes:**

**A. Database Connection Errors**
```
asyncpg.exceptions._base.InterfaceError: connection is closed
```

**Solution:** The database configuration already includes connection pooling. If you still see this error, restart the backend:
```powershell
kubectl rollout restart deployment backend
```

**B. Missing Secrets**
```
Error: environment variable not found
```

**Solution:** Recreate secrets:
```powershell
kubectl delete secret todo-secrets
kubectl create secret generic todo-secrets --from-literal=database-url='...' --from-literal=better-auth-secret='...' --from-literal=gemini-api-key='...'
kubectl rollout restart deployment backend
kubectl rollout restart deployment frontend
```

---

### Issue 2: 404 Not Found on /api/tasks

**Symptom:** Frontend loads but API calls return 404

**Check ingress configuration:**
```powershell
kubectl get ingress todo-chatbot-api -o yaml | findstr "path"
```

**Expected:**
```
path: /api
pathType: Prefix
```

**If you see `rewrite-target` annotation, the ingress is misconfigured.**

**Solution:** The ingress should NOT rewrite paths. Verify `helm-chart/templates/ingress.yaml` has:
```yaml
# Backend API Ingress without rewriting
spec:
  rules:
  - host: todo.local
    http:
      paths:
      - path: /api
        pathType: Prefix
```

**Apply fix:**
```powershell
helm upgrade todo-chatbot ./helm-chart
```

---

### Issue 3: "This site can't be reached" (ERR_CONNECTION_REFUSED)

**Check:**
1. Is minikube tunnel running?
2. Is hosts file configured?
3. Are pods running?

**Solution:**
```powershell
# 1. Verify tunnel is running (in Administrator PowerShell)
minikube tunnel -p todo-cluster

# 2. Verify hosts file
ping todo.local
# Should reply from 127.0.0.1

# 3. Verify pods
kubectl get pods
# All should be Running
```

---

### Issue 4: Docker Desktop Performance Issues

**Symptom:** Commands hang or timeout (TLS handshake timeout)

**Solution:**
```powershell
# Restart Docker Desktop
Stop-Process -Name "Docker Desktop" -Force
Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe"

# Wait 20 seconds, then verify
docker ps
```

---

### Issue 5: Minikube Won't Start

**Error:** `Docker machine "minikube" does not exist`

**Solution:** Use a fresh profile name:
```powershell
minikube delete -p todo-cluster
minikube start --driver=docker --cpus=2 --memory=3072 -p todo-cluster
```

---

## Useful Commands

### View Logs
```powershell
# Backend logs (live)
kubectl logs -l app.kubernetes.io/name=todo-chatbot -l app.kubernetes.io/component=backend --tail=50 -f

# Frontend logs (live)
kubectl logs -l app.kubernetes.io/name=todo-chatbot -l app.kubernetes.io/component=frontend --tail=50 -f

# Specific pod
kubectl logs <pod-name> --tail=100
```

### Restart Deployments
```powershell
kubectl rollout restart deployment backend
kubectl rollout restart deployment frontend
```

### Check Resource Usage
```powershell
kubectl top pods
kubectl top nodes
```

### Access Pod Shell
```powershell
# Backend
kubectl exec -it deployment/backend -- /bin/bash

# Frontend
kubectl exec -it deployment/frontend -- /bin/sh
```

### Update Application Code

**After making code changes:**

```powershell
# 1. Set Docker environment
minikube -p todo-cluster docker-env --shell powershell | Invoke-Expression

# 2. Rebuild image
cd backend  # or frontend
docker build -t todo-backend:latest .  # or todo-frontend:v3.0

# 3. Restart deployment
kubectl rollout restart deployment backend  # or frontend

# 4. Watch rollout
kubectl rollout status deployment backend
```

### Clean Up Everything
```powershell
# Uninstall application
helm uninstall todo-chatbot

# Delete secrets
kubectl delete secret todo-secrets

# Stop minikube
minikube stop -p todo-cluster

# Delete cluster (removes all data)
minikube delete -p todo-cluster
```

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        Browser                               │
│                   http://todo.local                          │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   Minikube Tunnel                            │
│                   (127.0.0.1:80)                             │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  Nginx Ingress Controller                    │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  /auth/*  → backend:8001  (Authentication)           │   │
│  │  /api/*   → backend:8001  (API endpoints)            │   │
│  │  /*       → frontend:3000 (Next.js pages)            │   │
│  └──────────────────────────────────────────────────────┘   │
└────────────┬────────────────────────────┬───────────────────┘
             │                            │
             ▼                            ▼
┌────────────────────────┐   ┌───────────────────────────────┐
│   Frontend Service     │   │    Backend Service            │
│   (ClusterIP:3000)     │   │    (ClusterIP:8001)           │
│   ┌────────────────┐   │   │   ┌────────────────────────┐  │
│   │ Pod 1 (Next.js)│   │   │   │ Pod 1 (FastAPI)        │  │
│   │ Pod 2 (Next.js)│   │   │   │ Pod 2 (FastAPI)        │  │
│   └────────────────┘   │   │   └────────────────────────┘  │
└────────────────────────┘   └───────────┬───────────────────┘
                                         │
                                         ▼
                         ┌───────────────────────────────────┐
                         │   Neon PostgreSQL (External)      │
                         │   Serverless, Auto-scaling        │
                         │   Connection Pooling Enabled      │
                         └───────────────────────────────────┘
```

---

## Configuration Summary

| Component | Port | Replicas | Image | Health Check |
|-----------|------|----------|-------|--------------|
| Frontend  | 3000 | 2        | todo-frontend:v3.0 | GET / |
| Backend   | 8001 | 2        | todo-backend:latest | GET /health |

| Environment Variable | Value | Location |
|---------------------|-------|----------|
| NEXT_PUBLIC_API_URL | http://todo.local | Frontend |
| DATABASE_URL | postgresql://... | Backend (Secret) |
| BETTER_AUTH_SECRET | zRfivV__... | Both (Secret) |
| GEMINI_API_KEY | AIzaSy... | Backend (Secret) |
| GEMINI_MODEL | gemini-2.5-flash | Backend |

---

## Success Checklist

- [ ] Minikube cluster running (`todo-cluster` profile)
- [ ] Nginx ingress enabled
- [ ] Docker images built (backend + frontend)
- [ ] Kubernetes secrets created
- [ ] Helm chart deployed
- [ ] All 4 pods running (2 frontend + 2 backend)
- [ ] Hosts file configured (127.0.0.1 todo.local)
- [ ] Minikube tunnel running (Administrator PowerShell)
- [ ] Frontend accessible at http://todo.local
- [ ] Backend health check returns `{"status":"healthy"}`
- [ ] Signup works without 500 errors
- [ ] Login works
- [ ] Task CRUD operations work (no 404 errors)
- [ ] AI chatbot responds without errors
- [ ] Tasks persist after pod restart

---

## Important Notes

### Database Connection Pooling

The backend includes connection pooling configuration to handle Neon's serverless PostgreSQL:

```python
# backend/database.py
engine = create_async_engine(
    DATABASE_URL,
    pool_pre_ping=True,      # Verify connections before use
    pool_recycle=300,        # Recycle connections every 5 minutes
    pool_size=5,             # Maximum connections in pool
    max_overflow=10,         # Maximum overflow connections
)
```

This prevents "connection is closed" errors.

### Ingress Path Routing

The ingress does NOT rewrite paths. Requests to `/api/tasks` are passed directly to the backend at `/api/tasks`.

**Correct configuration:**
```yaml
- path: /api
  pathType: Prefix
  backend:
    service:
      name: backend
      port:
        number: 8001
```

**Incorrect (DO NOT USE):**
```yaml
annotations:
  nginx.ingress.kubernetes.io/rewrite-target: /$2  # ❌ Causes 404 errors
```

---

## Next Steps

Once deployment is successful:

1. **Test all features thoroughly**
2. **Monitor logs:** `kubectl logs -l app.kubernetes.io/name=todo-chatbot --tail=100`
3. **Check resource usage:** `kubectl top pods`
4. **Scale if needed:** `kubectl scale deployment/backend --replicas=3`
5. **Update code:** Rebuild images and restart deployments

---

## Support

If you encounter issues not covered in this guide:

1. Check pod logs: `kubectl logs <pod-name>`
2. Describe pod: `kubectl describe pod <pod-name>`
3. Check ingress: `kubectl describe ingress`
4. Verify secrets: `kubectl get secret todo-secrets`
5. Review minikube status: `minikube status -p todo-cluster`

---

**Last Updated:** February 4, 2026
**Version:** 2.0.0
**Tested On:** Windows 10 Pro, Minikube v1.38.0, Kubernetes v1.35.0, Docker Desktop 29.1.3
