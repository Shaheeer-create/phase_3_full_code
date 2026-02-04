# Phase 4 - Kubernetes Deployment Guide

## Deployment Status: ✅ COMPLETE

All components have been successfully deployed to Minikube!

---

## 🎯 Quick Access

**Application URL:** http://todo.local

---

## 📋 Final Configuration Steps

### Step 1: Add Hosts Entry (Required)

You need to add `todo.local` to your Windows hosts file with **Administrator privileges**.

**Option A: Using Notepad (Recommended)**
1. Open Notepad as Administrator:
   - Press `Win + S`, type "Notepad"
   - Right-click → "Run as administrator"
2. Open file: `C:\Windows\System32\drivers\etc\hosts`
3. Add this line at the end:
   ```
   192.168.49.2 todo.local
   ```
4. Save and close

**Option B: Using PowerShell (Admin)**
```powershell
Add-Content -Path C:\Windows\System32\drivers\etc\hosts -Value "`n192.168.49.2 todo.local"
```

### Step 2: Start Minikube Tunnel

Open a **new PowerShell window as Administrator** and run:
```powershell
minikube tunnel
```

**Important:** Keep this window open while using the application. The tunnel routes traffic from your localhost to the Minikube cluster.

---

## 🚀 Accessing the Application

Once the hosts file is updated and tunnel is running:

1. **Frontend:** http://todo.local
2. **Backend API:** http://todo.local/api
3. **Health Check:** http://todo.local/api/health

---

## 📊 Deployment Details

### Cluster Information
- **Minikube IP:** 192.168.49.2
- **Kubernetes Version:** Latest
- **Driver:** Docker
- **Resources:** 2 CPUs, 3GB RAM

### Deployed Components

#### Frontend (Next.js 16)
- **Replicas:** 2
- **Image:** todo-frontend:latest
- **Port:** 3000
- **Resources:** 256Mi-512Mi memory, 250m-500m CPU

#### Backend (FastAPI)
- **Replicas:** 2
- **Image:** todo-backend:latest
- **Port:** 8000
- **Resources:** 512Mi-1Gi memory, 500m-1000m CPU

#### Ingress (Nginx)
- **Host:** todo.local
- **Routes:**
  - `/` → Frontend service
  - `/api` → Backend service

### Secrets Configured
- `BETTER_AUTH_SECRET` - Authentication secret
- `DATABASE_URL` - Neon PostgreSQL connection
- `GEMINI_API_KEY` - Google Gemini AI API key

---

## 🔍 Verification Commands

Check deployment status:
```powershell
# View all pods
kubectl get pods

# View services
kubectl get services

# View ingress
kubectl get ingress

# Check pod logs
kubectl logs <pod-name>

# Describe pod
kubectl describe pod <pod-name>
```

---

## 🛠️ Troubleshooting

### Pods Not Running
```powershell
kubectl get pods
kubectl logs <pod-name>
kubectl describe pod <pod-name>
```

### Cannot Access Application
1. Verify hosts file entry: `192.168.49.2 todo.local`
2. Ensure minikube tunnel is running (Admin PowerShell)
3. Check ingress status: `kubectl get ingress`
4. Verify pods are running: `kubectl get pods`

### Restart Deployment
```powershell
# Restart frontend
kubectl rollout restart deployment frontend

# Restart backend
kubectl rollout restart deployment backend

# Check rollout status
kubectl rollout status deployment frontend
kubectl rollout status deployment backend
```

### View Logs
```powershell
# Frontend logs
kubectl logs -l app.kubernetes.io/component=frontend --tail=50

# Backend logs
kubectl logs -l app.kubernetes.io/component=backend --tail=50

# Follow logs in real-time
kubectl logs -f <pod-name>
```

---

## 🔄 Update Deployment

If you make code changes:

1. **Rebuild Docker images:**
   ```powershell
   # Configure Docker to use Minikube
   & minikube -p minikube docker-env --shell powershell | Invoke-Expression

   # Rebuild frontend
   cd frontend
   docker build -t todo-frontend:latest .

   # Rebuild backend
   cd ../backend
   docker build -t todo-backend:latest .
   ```

2. **Restart deployments:**
   ```powershell
   kubectl rollout restart deployment frontend
   kubectl rollout restart deployment backend
   ```

---

## 🗑️ Cleanup

To remove the deployment:
```powershell
# Uninstall Helm release
helm uninstall todo-chatbot

# Delete secrets
kubectl delete secret todo-secrets

# Stop Minikube
minikube stop

# Delete Minikube cluster (optional)
minikube delete
```

---

## 📁 Project Structure

```
phase_3_copy/
├── frontend/
│   ├── Dockerfile              # Multi-stage Next.js build
│   ├── .dockerignore
│   └── next.config.ts          # Standalone output enabled
├── backend/
│   ├── Dockerfile              # Multi-stage Python build
│   ├── .dockerignore
│   └── requirements.txt        # Updated with email-validator
├── helm-chart/
│   ├── Chart.yaml              # Helm chart metadata
│   ├── values.yaml             # Configuration values
│   └── templates/
│       ├── _helpers.tpl        # Template helpers
│       ├── frontend-deployment.yaml
│       ├── frontend-service.yaml
│       ├── backend-deployment.yaml
│       ├── backend-service.yaml
│       └── ingress.yaml
└── DEPLOYMENT.md               # This file
```

---

## ✅ Success Criteria

- [x] Minikube cluster running
- [x] Docker images built
- [x] Kubernetes secrets created
- [x] Helm chart deployed
- [x] All pods running (2 frontend + 2 backend)
- [x] Services created
- [x] Ingress configured
- [ ] Hosts file updated (manual step)
- [ ] Minikube tunnel running (manual step)
- [ ] Application accessible at http://todo.local

---

## 🎉 Next Steps

1. Complete the manual configuration steps above
2. Access the application at http://todo.local
3. Test authentication (signup/login)
4. Test task CRUD operations
5. Test AI chatbot functionality

---

**Deployment completed successfully!** 🚀
