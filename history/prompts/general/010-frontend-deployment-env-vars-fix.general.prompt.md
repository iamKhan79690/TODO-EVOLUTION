---
id: 010
title: Frontend deployment environment variables fix
stage: general
date: 2025-12-25
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: 1-phase-iv-kubernetes-aiops
user: iamkhan7969@gmail.com
command: debugging session
labels: ["kubernetes","deployment","frontend","environment-variables","nextjs"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - frontend/Dockerfile
  - helm-chart/values.yaml
tests:
  - Frontend health endpoint check
  - API proxy sign-in test
  - Environment variable verification in running pods
  - Pod image version verification
---

## Prompt

User reported that sign-in functionality from the frontend was not working with error: "Unable to connect to server. Please check if the backend is running."

The user was accessing the application at `http://127.0.0.1:43321/auth/signin` with credentials:
- Email: iamkhan7969@gmail.com
- Password: Anaskhan@321

After multiple fix attempts (CORS configuration, route params fix), the user asked: "same error occur again why?"

## Response snapshot

**Root Cause Identified:**
The frontend pods were running with old image (v1.0.1) that had incorrect `NEXT_PUBLIC_*` environment variables. Next.js requires these variables to be set at **BUILD TIME** (during `npm run build`), not just at runtime in Kubernetes.

**Fixes Applied:**
1. Updated `frontend/Dockerfile` to set `NEXT_PUBLIC_*` environment variables before the build step:
   ```dockerfile
   ENV NEXT_PUBLIC_API_URL=/api/proxy \
       NEXT_PUBLIC_FASTAPI_URL=/api/proxy \
       NEXT_PUBLIC_CHAT_API_URL=/api/proxy \
       NEXT_PUBLIC_AUTH_URL=/api/proxy \
       NEXT_PUBLIC_APP_URL=http://127.0.0.1:43321
   ```

2. Rebuilt frontend image with tag 1.0.3 in Minikube Docker context

3. Patched Kubernetes deployment to force new image rollout:
   ```bash
   kubectl patch deployment todo-evolution-frontend -p '{"spec":{"template":{"spec":{"containers":[{"name":"frontend","image":"todo-frontend:1.0.3"}]}}}}'
   ```

**Verification:**
- ✅ Pods restarted with new image 1.0.3
- ✅ Environment variables confirmed correct in running pods
- ✅ Frontend health check: Working (200 OK)
- ✅ API proxy sign-in: Working (JWT tokens generated)
- ✅ User confirmed: "thankuuuu it worked"

## Outcome

- ✅ Impact: Resolved critical production issue preventing user authentication
- 🧪 Tests: Frontend health endpoint, API proxy authentication, pod environment verification
- 📁 Files: Modified `frontend/Dockerfile` (build-time env vars), updated `helm-chart/values.yaml` (image tag to 1.0.3)
- 🔁 Next prompts: None - issue fully resolved
- 🧠 Reflection: Key learning - Next.js `NEXT_PUBLIC_*` variables are baked into JavaScript bundle at build time, cannot be changed at runtime in Kubernetes. This is a common source of confusion in containerized deployments.

## Evaluation notes (flywheel)

- Failure modes observed: Kubernetes deployment not picking up new image automatically, build-time vs runtime env vars confusion
- Graders run and results (PASS/FAIL): Manual testing - PASS
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Consider adding build-time environment variable validation to CI/CD pipeline to catch this issue earlier
