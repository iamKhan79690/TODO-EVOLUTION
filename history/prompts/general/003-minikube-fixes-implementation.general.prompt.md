---
id: 003
title: Minikube Backend Connection Fixes Implementation
stage: general
date: 2025-12-24
surface: agent
model: claude-sonnet-4-5
feature: none
branch: 1-phase-iv-kubernetes-aiops
user: iamkhan7969
command: n/a
labels: ["kubernetes","minikube","implementation","api-proxy","fixes"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
 - helm-chart/values.yaml
 - helm-chart/templates/backend/deployment.yaml
 - helm-chart/templates/frontend/deployment.yaml
 - frontend/src/app/api/proxy/[...path]/route.ts
 - minikube-deployment-fix-guide.md
tests:
 - N/A (implementation session, manual testing required)
---

## Prompt

yes sure

## Response snapshot

Implemented comprehensive fixes for Minikube backend connectivity issues:

### Changes Made:

1. **Fixed Environment Variables in helm-chart/values.yaml**:
   - Added `BACKEND_URL: "http://todo-evolution-backend:8000"` for server-side API proxy
   - Changed `NEXT_PUBLIC_API_URL: "/api/proxy"` for client-side calls
   - Added `CORS_ORIGINS: "http://localhost:3000,http://localhost,http://192.168.49.2"` to backend env

2. **Updated Helm Templates**:
   - `helm-chart/templates/backend/deployment.yaml`: Added CORS_ORIGINS environment variable
   - `helm-chart/templates/frontend/deployment.yaml`: Added BACKEND_URL environment variable

3. **Created Next.js API Proxy**:
   - New file: `frontend/src/app/api/proxy/[...path]/route.ts`
   - Catches all `/api/proxy/*` requests and forwards them to backend server-side
   - Handles all HTTP methods (GET, POST, PUT, PATCH, DELETE)
   - Automatically forwards Authorization headers from cookies
   - Solves browser-to-Kubernetes connectivity issue

4. **Created Deployment Guide**:
   - Comprehensive guide at `minikube-deployment-fix-guide.md`
   - Step-by-step deployment instructions
   - Testing procedures
   - Troubleshooting section
   - Architecture diagram

### Architecture Solution:

The key insight is that browsers run outside the Kubernetes cluster and cannot access internal service DNS names. The solution uses a Next.js API proxy:

```
Browser → Frontend Service → API Proxy (server-side) → Backend Service (internal DNS)
```

The API proxy runs server-side in Next.js, so it can access internal Kubernetes services like `todo-evolution-backend`.

## Outcome

- ✅ Impact: High - Fixes root cause of "backend not running" error
- 🧪 Tests: Manual testing required (user needs to rebuild images and redeploy)
- 📁 Files: Modified 3 files, created 2 new files
- 🔁 Next prompts: Rebuild Docker images, redeploy with Helm, test in browser
- 🧠 Reflection: This is a production-ready solution that uses Next.js API routes to proxy backend requests. More secure than exposing backend externally. Follows Kubernetes best practices by keeping backend service as ClusterIP/internal.

## Evaluation notes (flywheel)

- Failure modes observed: N/A
- Graders run and results (PASS/FAIL): N/A - Requires manual deployment and testing
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): User should rebuild frontend Docker image with new API proxy route, then redeploy with `helm upgrade todo-evolution ./helm-chart` and test sign-in functionality.

---

## Related Files:
- Previous analysis: `history/prompts/general/002-minikube-deployment-debugging.general.prompt.md`
- Constitution: `.specify/memory/constitution.md`
