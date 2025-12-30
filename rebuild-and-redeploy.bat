@echo off
REM Complete rebuild and redeploy script for TODO Evolution with Gemini API fix
REM This script fixes the invalid gemini-2.5-flash model name issue

echo 🔧 TODO Evolution - Rebuild and Redeploy Script
echo ==============================================
echo.

REM Step 1: Start Minikube
echo 📦 Step 1: Starting Minikube...
minikube start --cpus=4 --memory=8192 --disk-size=20g
echo ✅ Minikube started
echo.

REM Step 2: Point Docker to Minikube daemon
echo 🐳 Step 2: Pointing Docker to Minikube...
FOR /f "tokens=*" %i IN ('minikube docker-env') DO %i
echo ✅ Docker now using Minikube daemon
echo.

REM Step 3: Build backend image (with Gemini fix)
echo 🔨 Step 3: Building backend Docker image...
cd backend
docker build -t todo-backend:2.0.1 .
cd ..
echo ✅ Backend image built: todo-backend:2.0.1
echo.

REM Step 4: Update Helm chart values
echo 📝 Step 4: Updating Helm chart values...
powershell -Command "(Get-Content helm-chart\values.yaml) -replace 'tag: \"1.0.0\"', 'tag: \"2.0.1\"' | Set-Content helm-chart\values.yaml"
echo ✅ Helm values updated to use todo-backend:2.0.1
echo.

REM Step 5: Deploy with Helm
echo 🚀 Step 5: Deploying to Minikube with Helm...
helm upgrade --install todo-evolution .\helm-chart --set backend.image.tag=2.0.1 --namespace default --wait --timeout 5m
echo ✅ Deployment complete
echo.

REM Step 6: Verify deployment
echo 🔍 Step 6: Verifying deployment...
kubectl get pods -l app=todo-evolution
echo.
echo 📊 Services:
kubectl get svc -l app=todo-evolution
echo.

REM Step 7: Get frontend URL
echo 🌐 Step 7: Getting service URLs...
echo Frontend URL:
minikube service todo-evolution-frontend --url
echo.
echo Backend API health check:
for /f %%i in ('minikube service todo-evolution-backend --url') do curl %%i/health/
echo.

echo ✅🎉 All done! Your application should now be working.
echo.
echo 📝 What was fixed:
echo   - Changed gemini-2.5-flash → gemini-1.5-flash (simple_chat.py)
echo   - Changed gemini-2.5-flash → gemini-2.0-flash-exp (ai_agent.py)
echo.
echo 🧪 To test the AI chat:
echo   1. Open the frontend URL in your browser
echo   2. Sign in to your account
echo   3. Click the chat button
echo   4. Type: 'hi' or 'add task: buy groceries'
echo.
echo 📋 To check backend logs:
kubectl logs -l app.kubernetes.io/name=backend --tail=50 -f

pause
