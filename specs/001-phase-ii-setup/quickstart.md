# Phase II Development Setup Quickstart

**Purpose**: Quick setup guide for developers joining Phase II of the Todo application
**Timeline**: ~15 minutes for complete development environment setup
**Prerequisites**: Node.js 18+, Python 3.11+, Git

## System Requirements

### Development Environment
- **Node.js**: 18.0.0 or higher (for Next.js frontend)
- **Python**: 3.11.0 or higher (for FastAPI backend)
- **Git**: Latest version for version control
- **IDE**: VS Code or similar with TypeScript/Python support

### Optional Tools
- **Docker**: For database testing (testcontainers)
- **PostgreSQL Client**: pgAdmin, DBeaver, or similar for database management

## Setup Instructions

### 1. Repository Setup

```bash
# Clone the repository (if not already done)
git clone <repository-url>
cd "The Evolution of Todo"

# Switch to Phase II feature branch
git checkout 001-phase-ii-setup
```

### 2. Frontend Setup (Next.js)

```bash
# Navigate to frontend directory
cd frontend

# Create Next.js project with TypeScript and Tailwind
npx create-next-app@latest . --typescript --tailwind --eslint --app --src-dir --import-alias "@/*"

# Install additional dependencies
npm install better-auth @auth/prisma-adapter

# Install development dependencies
npm install -D @types/node

# Copy environment template
cp .env.example .env.local
```

**Frontend Environment Variables (.env.local)**:
```env
# Better Auth Configuration
NEXT_PUBLIC_BETTER_AUTH_URL=http://localhost:3000
BETTER_AUTH_SECRET=your-super-secret-key-change-this-in-production
BETTER_AUTH_SIGN_IN_URL="/sign-in"
BETTER_AUTH_SIGN_OUT_URL="/"

# Database (for Better Auth)
DATABASE_URL="postgresql://user:password@localhost:5432/todoapp?schema=public"

# Development
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 3. Backend Setup (FastAPI)

```bash
# Navigate to backend directory
cd ../backend

# Create Python virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install Python dependencies
pip install fastapi uvicorn sqlmodel "asyncpg>=0.21" python-jose[cryptography] better-auth

# Install development dependencies
pip install -d pytest httpx pytest-asyncio testcontainers

# Create requirements.txt for reproducibility
pip freeze > requirements.txt
```

**Backend Environment Variables (.env)**:
```env
# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/todoapp

# Better Auth Configuration (same as frontend)
BETTER_AUTH_SECRET=your-super-secret-key-change-this-in-production

# Development
DEBUG=true
CORS_ORIGINS=["http://localhost:3000"]
```

### 4. Database Setup (Neon PostgreSQL)

1. **Create Neon Account**: Visit [https://neon.tech](https://neon.tech) and create an account
2. **Create Database**: Create a new PostgreSQL project
3. **Get Connection String**: Copy the connection string from Neon dashboard
4. **Update Environment**: Replace `DATABASE_URL` in both frontend and backend `.env` files

**Database Connection String Format**:
```
postgresql://username:password@ep-xyz.us-east-2.aws.neon.tech/dbname?sslmode=require
```

### 5. Development Server Startup

**Start Frontend**:
```bash
cd frontend
npm run dev
# Frontend will be available at http://localhost:3000
```

**Start Backend**:
```bash
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate
uvicorn main:app --reload --port 8000
# Backend API will be available at http://localhost:8000
# API docs at http://localhost:8000/docs
```

## Verification Steps

### 1. Frontend Verification
1. Open http://localhost:3000 in browser
2. Should see Next.js welcome page
3. Check browser console for no errors
4. TypeScript compilation should succeed

### 2. Backend Verification
1. Open http://localhost:8000 in browser
2. Should see `{"message": "Hello World"}` or similar
3. Open http://localhost:8000/docs for API documentation
4. Verify OpenAPI documentation loads correctly

### 3. Database Verification
1. Test database connection from backend
2. Verify tables are created (users, tasks)
3. Check that Better Auth can connect to database

### 4. Integration Verification
1. Test CORS configuration between frontend and backend
2. Verify API calls from frontend work
3. Test health check endpoints

## Common Issues & Solutions

### Frontend Issues

**Issue**: `npm create-next-app` fails
```bash
# Solution: Clear npm cache
npm cache clean --force
npx create-next-app@latest . --typescript --tailwind --eslint --app --src-dir --import-alias "@/*"
```

**Issue**: TypeScript compilation errors
```bash
# Solution: Check Node.js version
node --version  # Should be 18+
npm --version   # Should be 9+
```

### Backend Issues

**Issue**: Virtual environment activation fails (Windows)
```powershell
# Solution: Use PowerShell execution policy
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
venv\Scripts\Activate.ps1
```

**Issue**: Package installation fails
```bash
# Solution: Upgrade pip and use wheel
pip install --upgrade pip setuptools wheel
pip install fastapi uvicorn sqlmodel "asyncpg>=0.21"
```

### Database Issues

**Issue**: Connection refused to PostgreSQL
```bash
# Solution: Check connection string format
# Ensure SSL is enabled for Neon connections
DATABASE_URL="postgresql://user:pass@host/dbname?sslmode=require"
```

## Development Workflow

### 1. Daily Development
```bash
# Start both servers in separate terminals
# Terminal 1: Frontend
cd frontend && npm run dev

# Terminal 2: Backend
cd backend && source venv/bin/activate && uvicorn main:app --reload
```

### 2. Testing
```bash
# Frontend tests
cd frontend && npm test

# Backend tests
cd backend && source venv/bin/activate && pytest
```

### 3. Code Quality
```bash
# Frontend linting
cd frontend && npm run lint

# Backend linting (if configured)
cd backend && source venv/bin/activate && flake8 .
```

## Project Structure Overview

```
The Evolution of Todo/
├── frontend/                    # Next.js application
│   ├── src/
│   │   ├── app/                # App Router pages
│   │   ├── components/         # Reusable components
│   │   └── lib/               # Utilities and configuration
│   ├── public/                 # Static assets
│   ├── package.json
│   └── .env.local             # Frontend environment variables
├── backend/                    # FastAPI application
│   ├── app/
│   │   ├── api/               # API routes
│   │   ├── core/              # Core configuration
│   │   ├── models/            # SQLModel models
│   │   └── services/          # Business logic
│   ├── main.py                # FastAPI application entry
│   ├── requirements.txt
│   └── .env                   # Backend environment variables
├── specs/                      # Project specifications
│   └── 001-phase-ii-setup/
└── .specify/                   # Spec-Kit Plus configuration
```

## Next Steps

1. **Verify Setup**: Complete all verification steps above
2. **Review Documentation**: Read `data-model.md` and `contracts/openapi.yaml`
3. **Start Development**: Begin implementing features according to `tasks.md`
4. **Join Team Communication**: Connect with the development team

## Support

- **Documentation**: Check `/specs/001-phase-ii-setup/` for detailed specifications
- **API Documentation**: http://localhost:8000/docs (once backend is running)
- **Issues**: Create GitHub issues for setup problems
- **Team Contact**: Reach out to the development team for assistance

---

**Setup Status**: ✅ Ready for development
**Time to Complete**: ~15 minutes
**Support Available**: Documentation + team communication channels