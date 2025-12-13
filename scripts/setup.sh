#!/bin/bash

# =============================================================================
# EVOLUTION-OF-TODO - Phase II Setup Script
# =============================================================================
# This script sets up the complete development environment for Phase II
# =============================================================================

set -e  # Exit on any error

echo "🚀 Setting up Evolution of Todo - Phase II Development Environment"
echo "=================================================================="

# Check prerequisites
echo "📋 Checking prerequisites..."

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18+ first."
    exit 1
fi

NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
    echo "❌ Node.js version 18+ is required. Current version: $(node -v)"
    exit 1
fi
echo "✅ Node.js $(node -v) detected"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3.11+ is not installed. Please install Python first."
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "✅ Python $PYTHON_VERSION detected"

# Check if .env.local exists
if [ ! -f ".env.local" ]; then
    echo "📝 Creating .env.local from template..."
    cp .env.local.example .env.local
    echo "⚠️  Please update .env.local with your database configuration and secrets"
    echo "   See DATABASE_SETUP.md for detailed instructions"
else
    echo "✅ .env.local already exists"
fi

# Setup Frontend
echo ""
echo "🎨 Setting up Frontend (Next.js)..."

if [ ! -d "frontend" ]; then
    mkdir -p frontend
fi

cd frontend

if [ ! -f "package.json" ]; then
    echo "📦 Creating Next.js project..."
    npx create-next-app@latest . --typescript --tailwind --eslint --app --src-dir --import-alias "@/*" --no-git
else
    echo "📦 Installing frontend dependencies..."
    npm install
fi

echo "✅ Frontend setup complete"
cd ..

# Setup Backend
echo ""
echo "🐍 Setting up Backend (FastAPI)..."

if [ ! -d "backend" ]; then
    mkdir -p backend
fi

cd backend

# Create Python virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "🐍 Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment and install dependencies
echo "📦 Installing backend dependencies..."
source venv/bin/activate

# Create requirements.txt if it doesn't exist
if [ ! -f "requirements.txt" ]; then
    echo "fastapi>=0.104.0
uvicorn[standard]>=0.24.0
sqlmodel>=0.0.14
asyncpg>=0.29.0
python-jose[cryptography]>=3.3.0
python-multipart>=0.0.6
better-auth>=0.8.0
pytest>=7.4.0
httpx>=0.25.0
pytest-asyncio>=0.21.0
testcontainers>=3.7.0" > requirements.txt
fi

pip install -r requirements.txt

echo "✅ Backend setup complete"
cd ..

# Install root dependencies
echo ""
echo "📦 Installing root dependencies..."
npm install

echo ""
echo "🎉 Setup complete!"
echo "=================================================================="
echo "Next steps:"
echo "1. Update .env.local with your database configuration"
echo "2. Run: npm run dev"
echo ""
echo "Development servers will be available at:"
echo "- Frontend: http://localhost:3000"
echo "- Backend API: http://localhost:8000"
echo "- API Docs: http://localhost:8000/docs"