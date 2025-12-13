@echo off
REM =============================================================================
REM EVOLUTION-OF-TODO - Phase II Setup Script (Windows)
REM =============================================================================
REM This script sets up the complete development environment for Phase II
REM =============================================================================

echo 🚀 Setting up Evolution of Todo - Phase II Development Environment
echo ==================================================================

REM Check prerequisites
echo 📋 Checking prerequisites...

REM Check Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js is not installed. Please install Node.js 18+ first.
    pause
    exit /b 1
)

for /f "tokens=1 delims=v" %%i in ('node --version') do set NODE_VERSION=%%i
for /f "tokens=1 delims=." %%i in ("%NODE_VERSION%") do set NODE_MAJOR=%%i
if %NODE_MAJOR% lss 18 (
    echo ❌ Node.js version 18+ is required. Current version: %NODE_VERSION%
    pause
    exit /b 1
)
echo ✅ Node.js %NODE_VERSION% detected

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python 3.11+ is not installed. Please install Python first.
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo ✅ Python %PYTHON_VERSION% detected

REM Check if .env.local exists
if not exist ".env.local" (
    echo 📝 Creating .env.local from template...
    copy .env.local.example .env.local >nul
    echo ⚠️  Please update .env.local with your database configuration and secrets
    echo    See DATABASE_SETUP.md for detailed instructions
) else (
    echo ✅ .env.local already exists
)

REM Setup Frontend
echo.
echo 🎨 Setting up Frontend (Next.js)...

if not exist "frontend" mkdir frontend

cd frontend

if not exist "package.json" (
    echo 📦 Creating Next.js project...
    npx create-next-app@latest . --typescript --tailwind --eslint --app --src-dir --import-alias "@/*" --no-git
) else (
    echo 📦 Installing frontend dependencies...
    call npm install
)

echo ✅ Frontend setup complete
cd ..

REM Setup Backend
echo.
echo 🐍 Setting up Backend (FastAPI)...

if not exist "backend" mkdir backend

cd backend

REM Create Python virtual environment if it doesn't exist
if not exist "venv" (
    echo 🐍 Creating Python virtual environment...
    python -m venv venv
)

REM Activate virtual environment and install dependencies
echo 📦 Installing backend dependencies...
call venv\Scripts\activate.bat

REM Create requirements.txt if it doesn't exist
if not exist "requirements.txt" (
    echo fastapi^>=0.104.0 > requirements.txt
    echo uvicorn[standard]^>=0.24.0 >> requirements.txt
    echo sqlmodel^>=0.0.14 >> requirements.txt
    echo asyncpg^>=0.29.0 >> requirements.txt
    echo python-jose[cryptography]^>=3.3.0 >> requirements.txt
    echo python-multipart^>=0.0.6 >> requirements.txt
    echo better-auth^>=0.8.0 >> requirements.txt
    echo pytest^>=7.4.0 >> requirements.txt
    echo httpx^>=0.25.0 >> requirements.txt
    echo pytest-asyncio^>=0.21.0 >> requirements.txt
    echo testcontainers^>=3.7.0 >> requirements.txt
)

pip install -r requirements.txt

echo ✅ Backend setup complete
cd ..

REM Install root dependencies
echo.
echo 📦 Installing root dependencies...
call npm install

echo.
echo 🎉 Setup complete!
echo ==================================================================
echo Next steps:
echo 1. Update .env.local with your database configuration
echo 2. Run: npm run dev
echo.
echo Development servers will be available at:
echo - Frontend: http://localhost:3000
echo - Backend API: http://localhost:8000
echo - API Docs: http://localhost:8000/docs
echo.
pause