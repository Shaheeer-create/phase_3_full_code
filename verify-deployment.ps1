#!/usr/bin/env pwsh
# Phase 4 Deployment Verification Script

Write-Host "=== Todo Chatbot Deployment Verification ===" -ForegroundColor Cyan
Write-Host ""

# Check Minikube status
Write-Host "1. Checking Minikube status..." -ForegroundColor Yellow
$minikubeStatus = minikube status
Write-Host $minikubeStatus
Write-Host ""

# Check pods
Write-Host "2. Checking pod status..." -ForegroundColor Yellow
kubectl get pods
Write-Host ""

# Check services
Write-Host "3. Checking services..." -ForegroundColor Yellow
kubectl get svc
Write-Host ""

# Check ingress
Write-Host "4. Checking ingress..." -ForegroundColor Yellow
kubectl get ingress
Write-Host ""

# Check if hosts file has entry
Write-Host "5. Checking hosts file..." -ForegroundColor Yellow
$hostsContent = Get-Content C:\Windows\System32\drivers\etc\hosts
if ($hostsContent -match "todo.local") {
    Write-Host "✅ Hosts file entry found" -ForegroundColor Green
} else {
    Write-Host "❌ Hosts file entry NOT found" -ForegroundColor Red
    Write-Host "   Run as Admin: Add-Content -Path C:\Windows\System32\drivers\etc\hosts -Value '`n192.168.49.2 todo.local'" -ForegroundColor Yellow
}
Write-Host ""

# Test connectivity
Write-Host "6. Testing connectivity..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://192.168.49.2" -TimeoutSec 5 -UseBasicParsing
    Write-Host "✅ Minikube IP accessible (Status: $($response.StatusCode))" -ForegroundColor Green
} catch {
    Write-Host "❌ Cannot reach Minikube IP" -ForegroundColor Red
    Write-Host "   Make sure 'minikube tunnel' is running in Admin PowerShell" -ForegroundColor Yellow
}
Write-Host ""

# Check backend health
Write-Host "7. Testing backend health endpoint..." -ForegroundColor Yellow
try {
    $backendHealth = Invoke-WebRequest -Uri "http://192.168.49.2/api/health" -TimeoutSec 5 -UseBasicParsing
    Write-Host "✅ Backend health check passed (Status: $($backendHealth.StatusCode))" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Backend health check failed: $($_.Exception.Message)" -ForegroundColor Yellow
}
Write-Host ""

# Summary
Write-Host "=== Summary ===" -ForegroundColor Cyan
Write-Host "Application URL: http://todo.local" -ForegroundColor White
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Ensure hosts file has: 192.168.49.2 todo.local"
Write-Host "2. Run 'minikube tunnel' in Admin PowerShell (keep it running)"
Write-Host "3. Open http://todo.local in your browser"
Write-Host ""
