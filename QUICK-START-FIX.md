# 🚀 Quick Start: Apply the Gemini API Fix

## ⚡ Fastest Way to Fix (3 Steps)

### 1️⃣ Run the Script (Windows)
```batch
rebuild-and-redeploy.bat
```

**OR** (Linux/Mac/WSL)
```bash
./rebuild-and-redeploy.sh
```

### 2️⃣ Open Your Browser
```
minikube service todo-evolution-frontend --url
```

### 3️⃣ Test the AI Chat
- Sign in
- Click chat button
- Type: **"hi"**
- ✅ Should get a friendly response!

---

## 📝 What Changed?

| File | Change | Why |
|------|--------|-----|
| `simple_chat.py` | `gemini-2.5-flash` → `gemini-1.5-flash` | Model name was invalid |
| `ai_agent.py` | `gemini-2.5-flash` → `gemini-2.0-flash-exp` | Model name was invalid |

---

## 🔍 Verify It Works

```bash
# Check backend logs
kubectl logs -l app.kubernetes.io/name=backend --tail=50

# Look for successful Gemini API calls
kubectl logs -l app.kubernetes.io/name=backend | grep -i "gemini\|model"
```

**You should see:**
- ✅ `gemini-1.5-flash` or `gemini-2.0-flash-exp` in logs
- ✅ No "model not found" errors
- ✅ AI responding to messages

---

## ❓ Still Not Working?

### Check API Key
```bash
kubectl get secret todo-secrets -o yaml | findstr GEMINI
```

### Check Backend Pod
```bash
kubectl get pods -l app.kubernetes.io/name=backend
kubectl describe pod <backend-pod-name>
```

### Check Environment Variables
```bash
kubectl exec <backend-pod-name> -- env | findstr GEMINI
```

---

## 📚 Full Documentation

See `GEMINI-FIX.md` for detailed troubleshooting and explanation.

---

**Need Help? Check the logs!**
```bash
kubectl logs -l app.kubernetes.io/name=backend -f
```
