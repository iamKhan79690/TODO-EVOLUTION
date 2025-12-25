# 🔐 Credentials and Secrets Guide

**Date:** December 25, 2025
**Purpose:** Complete overview of all credentials and secrets in the project

---

## 📁 Credentials Files Locations

### **1. Backend Credentials**

**File:** `/backend/.env`
```bash
DATABASE_URL=postgresql://neondb_owner:npg_6XJMDV8OidrG@ep-soft-wave-a4c4579s-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require
DATABASE_URL_ASYNC=postgresql+asyncpg://neondb_owner:npg_6XJMDV8OidrG@ep-soft-wave-a4c4579s-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require
JWT_SECRET=mHcvjk-NHb8wkRW_LJPpbuiH2ISXCOJ3B-CLIovVOX8
BETTER_AUTH_SECRET=nrnxH2ibdCh1fFNNm8war_j0OPB01KiBfVSPLZ1adi0
OPENAI_API_KEY=sk-proj-PLACEHOLDER
GEMINI_API_KEY=AIzaSyDVETwgQ4crz6QPwGC1g9zRig8xKN44A88
```

**Status:** ✅ **Contains REAL credentials** (Neon database, OpenAI, Gemini)

---

### **2. MCP Server Credentials**

**File:** `/mcp_server/.env`
```bash
JWT_SECRET=mHcvjk-NHb8wkRW_LJPpbuiH2ISXCOJ3B-CLIovVOX8
DATABASE_URL=postgresql://neondb_owner:npg_6XJMDV8OidrG@ep-soft-wave-a4c4579s-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require
FASTAPI_BASE_URL=http://localhost:8000
MCP_SERVER_PORT=8001
```

**Status:** ✅ **Contains REAL credentials**

---

### **3. Frontend Credentials**

**File:** `/frontend/.env.local`
```bash
NEXT_PUBLIC_FASTAPI_URL=http://localhost:8000
NEXT_PUBLIC_CHAT_API_URL=http://localhost:8000/api
NEXT_PUBLIC_AUTH_URL=http://localhost:3000/api/auth
NEXT_PUBLIC_APP_URL=http://localhost:3000
```

**Status:** ✅ **Local development URLs (no sensitive data)**

---

### **4. Kubernetes Secrets (Currently Deployed)**

**Name:** `todo-secrets`

**Current Values (PLACEHOLDERS):**
```yaml
DATABASE_URL: postgresql+asyncpg://todo_user:change_me_in_production@localhost:5432/todo
JWT_SECRET: change-this-to-a-secure-random-string-min-32-chars
OPENAI_API_KEY: sk-your-openai-api-key-here
```

**Status:** ⚠️ **Using PLACEHOLDER values** - Needs to be updated!

---

## 🔧 **IMPORTANT: Update Kubernetes Secrets!**

Your Kubernetes deployment is using **placeholder secrets**. You need to update them with your **real credentials** from the `.env` files.

### **Steps to Update Kubernetes Secrets:**

```bash
# 1. Delete the existing placeholder secrets
kubectl delete secret todo-secrets

# 2. Create new secrets with REAL credentials from your .env files
kubectl create secret generic todo-secrets \
  --from-literal=DATABASE_URL='postgresql+asyncpg://neondb_owner:npg_6XJMDV8OidrG@ep-soft-wave-a4c4579s-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require' \
  --from-literal=JWT_SECRET='mHcvjk-NHb8wkRW_LJPpbuiH2ISXCOJ3B-CLIovVOX8' \
  --from-literal=OPENAI_API_KEY='sk-proj-PLACEHOLDER'

# 3. Restart the deployments to pick up new secrets
kubectl rollout restart deployment todo-evolution-backend
kubectl rollout restart deployment todo-evolution-mcp-server

# 4. Wait for pods to restart
kubectl get pods -w
```

---

## 📋 All Environment Files Summary

| File | Location | Contains | Status |
|------|----------|----------|--------|
| `.env` | `/backend/` | Real credentials (DB, OpenAI, JWT) | ✅ Actual |
| `.env` | `/mcp_server/` | Real credentials (DB, JWT) | ✅ Actual |
| `.env.local` | `/frontend/` | Local URLs | ✅ Dev config |
| `.env.example` | Project root | Template | 📝 Template |
| `todo-secrets` | Kubernetes | Placeholder values | ⚠️ **Needs update** |

---

## 🔐 Security Notes

### ⚠️ **CRITICAL WARNING:**

Your `.env` files contain **REAL, ACTIVE credentials:**

1. **Neon PostgreSQL Database** - Production database with owner access
2. **OpenAI API Key** - Active key with access to OpenAI services
3. **Gemini API Key** - Active Google AI key
4. **JWT Secrets** - Authentication secrets

**These files should NEVER be:**
- ❌ Committed to git (if they are, remove from git history immediately)
- ❌ Shared publicly
- ❌ Stored in plain text in production

**Recommended Actions:**
1. **Rotate these keys** after deployment if they were exposed
2. **Add `.env` to `.gitignore`** (if not already there)
3. **Use environment-specific .env files** for development vs production

---

## 🛠️ Quick Command to Update Secrets

Here's a quick copy-paste command to update your Kubernetes secrets:

```bash
cd /mnt/d/Hackathon/TODO-Evolution

# Read credentials from backend/.env and create Kubernetes secret
kubectl delete secret todo-secrets

kubectl create secret generic todo-secrets \
  --from-literal=DATABASE_URL='postgresql+asyncpg://neondb_owner:npg_6XJMDV8OidrG@ep-soft-wave-a4c4579s-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require' \
  --from-literal=JWT_SECRET='mHcvjk-NHb8wkRW_LJPpbuiH2ISXCOJ3B-CLIovVOX8' \
  --from-literal=OPENAI_API_KEY='sk-proj-PLACEHOLDER'

# Restart deployments
kubectl rollout restart deployment todo-evolution-backend
kubectl rollout restart deployment todo-evolution-mcp-server

# Wait and verify
kubectl get pods
kubectl logs -l component=backend --tail=10
```

---

## ✅ Verification

After updating secrets, verify they're correctly configured:

```bash
# Check secret exists
kubectl get secret todo-secrets

# Check backend logs for successful database connection
kubectl logs -l component=backend --tail=20 | grep -E "database|Database|connected"

# Test backend health endpoint
curl http://127.0.0.1:38937/api/proxy/health/

# Expected output should show:
# {"status":"healthy","database":"connected",...}
```

---

## 📚 Related Documentation

- **Helm Chart Secrets:** `helm-chart/values.yaml` (lines 207-214)
- **Secrets Template:** `helm-chart/templates/secrets.yaml`
- **Deployment Guide:** `minikube-deployment-fix-guide.md`
- **Success Report:** `DEPLOYMENT-SUCCESS.md`

---

**Generated:** December 25, 2025
**Purpose:** Help locate and update all credentials and secrets
