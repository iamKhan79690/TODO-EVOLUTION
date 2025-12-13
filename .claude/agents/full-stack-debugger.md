# Full-Stack Application Debugger Agent

## Purpose
This agent systematically debugs the entire Todo Evolution application stack, identifying and fixing all connectivity, authentication, and configuration issues in one comprehensive pass.

## Prerequisites
- Backend must be running on port 8001
- Frontend must be running on port 3001
- Neon PostgreSQL database must be accessible

---

## Phase 1: Environment Configuration Audit

### Step 1.1: Check Backend .env
```bash
cat backend/.env
```
**Verify these keys exist and have values:**
- `DATABASE_URL` - Must contain Neon PostgreSQL connection string
- `DATABASE_URL_ASYNC` - Must use `postgresql+asyncpg://` prefix and `ssl=require`
- `BETTER_AUTH_SECRET` - Used for JWT signing
- `JWT_SECRET` - Alternative JWT secret (check which is actually used)
- `CORS_ORIGINS` - Must include `http://localhost:3001`

### Step 1.2: Check Frontend .env.local
```bash
cat frontend/.env.local
```
**Verify:**
- `NEXT_PUBLIC_FASTAPI_URL=http://localhost:8001`

### Step 1.3: Verify Secret Consistency
The JWT signing and verification MUST use the same secret. Check:
- `backend/src/auth/better_auth_config.py` - Uses `settings.BETTER_AUTH_SECRET`
- `backend/src/dependencies/auth.py` - Uses `settings.BETTER_AUTH_SECRET`

**If they use different secrets, fix them to use the same one.**

---

## Phase 2: Backend API Health Check

### Step 2.1: Test Health Endpoint
```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8001/api/v1/health" -Method GET
```
**Expected:** `status: "healthy"`, `database: "connected"`

### Step 2.2: Test Auth Signup
```powershell
$body = '{"email":"debug@test.com","password":"debug123","name":"Debug User"}'
Invoke-RestMethod -Uri "http://127.0.0.1:8001/api/v1/auth/sign-up" -Method POST -Body $body -ContentType "application/json"
```
**Expected:** Returns user object with `access_token` and `refresh_token`

### Step 2.3: Test Tasks API with Token
```powershell
$token = "<token_from_step_2.2>"
Invoke-RestMethod -Uri "http://127.0.0.1:8001/api/tasks" -Method GET -Headers @{Authorization="Bearer $token"}
```
**Expected:** Returns `{ tasks: [], count: 0, user_id: X }`

### Step 2.4: Test Task Creation
```powershell
$token = "<token_from_step_2.2>"
$body = '{"title":"Test Task","priority":"medium"}'
Invoke-RestMethod -Uri "http://127.0.0.1:8001/api/tasks" -Method POST -Body $body -ContentType "application/json" -Headers @{Authorization="Bearer $token"}
```
**Expected:** Returns created task object

---

## Phase 3: Route Alignment Verification

### Step 3.1: Backend Routes (main.py)
Check `backend/main.py` for router prefixes:
- `health_router` → `/api/v1`
- `tasks_router` → `/api`  
- `auth_router` → `/api/v1`

**Resulting endpoints:**
- Auth: `/api/v1/auth/sign-up`, `/api/v1/auth/sign-in`, etc.
- Tasks: `/api/tasks`, `/api/tasks/{id}`
- Health: `/api/v1/health`

### Step 3.2: Frontend API Calls
Check `frontend/src/lib/api.ts`:
- `baseURL` should be `http://localhost:8001`
- Task endpoints should use `/api/tasks` (NOT `/api/v1/tasks`)

Check `frontend/src/lib/auth-client.ts`:
- `baseURL` should be `http://localhost:8001`  
- Auth endpoints should use `/api/v1/auth/*`

---

## Phase 4: Database Schema Verification

### Step 4.1: Check User Model
`backend/src/models/models.py` - User must have:
- `id: int`
- `email: str`
- `name: str`
- `hashed_password: str` ← **CRITICAL: This field must exist!**
- `created_at: datetime`
- `updated_at: datetime`

### Step 4.2: Check Task Model
Same file - Task must have:
- `id: int`
- `title: str`
- `description: Optional[str]`
- `priority: Priority enum`
- `is_completed: bool`
- `user_id: int` (foreign key to user)
- `created_at: datetime`
- `updated_at: datetime`

### Step 4.3: Verify Database Tables in Neon
Run in Neon SQL Editor:
```sql
SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'user';
SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'task';
```
**Ensure `hashed_password` column exists in `user` table.**

---

## Phase 5: Authentication Flow Debug

### Step 5.1: JWT Token Structure
Decode a token at jwt.io to verify:
- `sub`: User ID (integer)
- `email`: User email  
- `exp`: Expiration timestamp
- `type`: "access" or "refresh"

### Step 5.2: Token Verification Path
`backend/src/dependencies/auth.py` - `get_current_user()`:
1. Extracts token from `Authorization: Bearer <token>` header
2. Checks if token is blacklisted (Redis)
3. Decodes JWT with `settings.BETTER_AUTH_SECRET`
4. Extracts `sub` (user_id) and `email` from payload
5. Looks up user in database by user_id
6. Returns user object

**Common issues:**
- Token blacklist check failing (Redis not available) → Set `REDIS_ENABLED=False`
- Wrong secret used for verification
- User not found in database (wrong user_id)

### Step 5.3: Session.execute vs Session.exec
All async database queries must use:
```python
result = await session.execute(statement)
user = result.scalars().first()
```
NOT:
```python
result = await session.exec(statement)  # WRONG for AsyncSession
```

---

## Phase 6: Common Fixes

### Fix 6.1: Missing hashed_password Column
```sql
ALTER TABLE "user" ADD COLUMN hashed_password VARCHAR(255);
```

### Fix 6.2: Session.exec to Session.execute
Replace all occurrences in:
- `backend/src/api/auth.py`
- `backend/src/dependencies/auth.py`
- `backend/src/services/task_service.py`

### Fix 6.3: CORS Issues
Ensure `backend/src/core/config.py` includes:
```python
CORS_ORIGINS = ["http://localhost:3000", "http://localhost:3001"]
```

### Fix 6.4: Redis Disabled
In `backend/.env`:
```
REDIS_ENABLED=False
```

### Fix 6.5: Password Validation Too Strict
In `backend/src/schemas/auth.py`, reduce password requirements:
```python
password: str = Field(..., min_length=1, max_length=128)
```

---

## Phase 7: Verification Tests

After all fixes, run these commands in sequence:

```powershell
# 1. Health check
Invoke-RestMethod -Uri "http://127.0.0.1:8001/api/v1/health"

# 2. Sign up
$signup = Invoke-RestMethod -Uri "http://127.0.0.1:8001/api/v1/auth/sign-up" -Method POST -Body '{"email":"final@test.com","password":"test123","name":"Final Test"}' -ContentType "application/json"
$token = $signup.token.access_token

# 3. Get tasks (should be empty)
Invoke-RestMethod -Uri "http://127.0.0.1:8001/api/tasks" -Headers @{Authorization="Bearer $token"}

# 4. Create task
Invoke-RestMethod -Uri "http://127.0.0.1:8001/api/tasks" -Method POST -Body '{"title":"My First Task","priority":"high"}' -ContentType "application/json" -Headers @{Authorization="Bearer $token"}

# 5. Get tasks (should have 1 task)
Invoke-RestMethod -Uri "http://127.0.0.1:8001/api/tasks" -Headers @{Authorization="Bearer $token"}
```

**All 5 commands must succeed for the application to be fully functional.**

---

## Troubleshooting Decision Tree

```
Is health endpoint working?
├─ No → Check if backend is running, check port 8001
└─ Yes → Is database "connected"?
    ├─ No → Check DATABASE_URL_ASYNC in .env, verify Neon access
    └─ Yes → Is signup working?
        ├─ No → Check password validation, hashed_password column
        └─ Yes → Is tasks API working with token?
            ├─ No → Check JWT secret consistency, session.execute usage
            └─ Yes → ✅ Application is functional!
```
