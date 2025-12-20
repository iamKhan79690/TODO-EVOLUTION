# 📝 TODO-EVOLUTION

[![Python](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![TypeScript](https://img.shields.io/badge/typescript-5.x-blue.svg)](https://www.typescriptlang.org/)
[![Next.js](https://img.shields.io/badge/next.js-16.0.7-black.svg)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/fastapi-0.121.2-green.svg)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/postgresql-15+-blue.svg)](https://www.postgresql.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

A sophisticated AI-powered task management application evolving from console to full-stack web application with an intelligent chatbot assistant.

---

## 📖 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [Tech Stack](#-tech-stack)
- [Architecture](#-architecture)
- [Quick Start](#-quick-start)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Running the Application](#running-the-application)
  - [Access Points](#access-points)
- [Environment Configuration](#-environment-configuration)
- [MCP Server (Optional)](#-mcp-server-optional)
- [API Documentation](#-api-documentation)
- [Testing](#-testing)
- [Deployment](#-deployment)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🎯 Overview

**TODO-Evolution** is a modern task management platform that demonstrates the evolution from a console application to a full-stack web solution. The application features:

- **Phase I**: Console-based task management (completed)
- **Phase II**: Full-stack web application with authentication (completed)
- **Phase III**: AI-powered chat assistant with natural language task management (✅ **PRODUCTION READY**)

The AI Chat Assistant allows users to manage tasks through natural language conversations, with real-time processing and mobile optimization.

---

## 🌟 Key Features

### 🔐 User Authentication
- JWT-based authentication with bcrypt password hashing
- Access and refresh token pattern with automatic token blacklisting
- Protected routes requiring authentication
- Secure sign-out with token revocation

### 📋 Advanced Task Management
- **CRUD Operations**: Create, read, update, and delete tasks seamlessly
- **Priority Levels**: High, medium, low, and urgent priority classification
- **Task Status**: Mark tasks as complete/incomplete with visual indicators
- **Smart Filtering**: Filter tasks by priority, completion status, and more
- **User Isolation**: Multi-tenant architecture (each user sees only their own tasks)

### 🤖 AI Chat Assistant
- **Natural Language Processing**: Manage tasks using conversational commands
- **Context-Aware**: Intelligent task recommendations based on patterns
- **Real-time Processing**: Instant message processing and response
- **Smart Task Analysis**: Productivity pattern recognition and insights
- **MCP Integration**: Optional Model Context Protocol server for extended AI capabilities

### 🎨 Modern Web Interface
- **Responsive Design**: Mobile-first approach that works on all devices
- **Touch-First Design**: Optimized for mobile interactions and gestures
- **Voice Input Support**: Touch-optimized mobile voice commands
- **Real-time Updates**: Instant task synchronization
- **Accessibility**: Built with accessibility best practices

---

## 🏗️ Tech Stack

### Frontend
| Technology | Version | Purpose |
|------------|---------|---------|
| Next.js | 16.0.7 | React framework with App Router |
| TypeScript | 5.x | Type safety |
| Tailwind CSS | 4.x | Styling |
| React Query | 5.x | State management |
| Lucide React | 0.400+ | Icons |

### Backend
| Technology | Version | Purpose |
|------------|---------|---------|
| FastAPI | 0.121.2 | REST API framework |
| Python | 3.13+ | Backend language |
| PostgreSQL | 15+ | Database (Neon cloud recommended) |
| SQLModel | 0.0.27 | ORM with SQLAlchemy 2.0 |
| OpenAI SDK | 2.8+ | AI agent integration |

### Optional Components
| Technology | Purpose |
|------------|---------|
| MCP Server | Extended AI tools (FastMCP 0.4.1) |
| Redis | Token blacklisting (optional) |

---

## 🏛️ Architecture

```
TODO-Evolution/
├── frontend/                 # Next.js 16 frontend application
│   ├── src/
│   │   ├── app/             # Next.js App Router pages
│   │   ├── components/      # Reusable React components
│   │   ├── hooks/           # Custom React hooks
│   │   ├── lib/             # Utility libraries
│   │   └── types/           # TypeScript type definitions
│   └── package.json
│
├── backend/                  # FastAPI backend application
│   ├── src/
│   │   ├── api/             # API route handlers
│   │   ├── auth/            # Authentication logic
│   │   ├── core/            # Core configuration
│   │   ├── dependencies/    # FastAPI dependencies
│   │   ├── models/          # SQLModel database models
│   │   ├── schemas/         # Pydantic data schemas
│   │   └── services/        # Business logic (AI agent, etc.)
│   ├── main.py              # Application entry point
│   └── requirements.txt
│
├── mcp_server/              # Optional MCP server for extended AI tools
│   ├── tools/               # MCP tool implementations
│   ├── services/            # FastAPI client for backend integration
│   ├── config/              # JWT and database configuration
│   ├── main.py              # MCP server entry point
│   └── server.py            # HTTP server alternative
│
└── package.json             # Root workspace configuration
```

---

## 🚀 Quick Start

### Prerequisites

| Requirement | Version | Notes |
|-------------|---------|-------|
| **Node.js** | 18.0+ | Required for frontend |
| **Python** | 3.11+ | 3.13 recommended |
| **Git** | Latest | For cloning |
| **PostgreSQL** | 15+ | Neon account recommended for cloud database |

### Installation

#### 1. Clone the Repository

```bash
git clone https://github.com/iamKhan79690/TODO-EVOLUTION.git
cd TODO-Evolution
```

#### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### 3. Frontend Setup

```bash
# Navigate to frontend directory (from project root)
cd frontend

# Install dependencies
npm install
```

#### 4. Environment Configuration

**Backend** - Create `backend/.env`:

```bash
# Database Configuration (Required)
DATABASE_URL=postgresql://user:password@ep-xyz.us-east-2.aws.neon.tech/todoapp

# Authentication (Required)
JWT_SECRET=your-secure-jwt-secret-key-change-in-production

# Server Settings
HOST=0.0.0.0
PORT=8000
DEBUG=true

# AI Services (Optional - enables AI chat features)
OPENAI_API_KEY=your-openai-api-key
# OR
GEMINI_API_KEY=your-gemini-api-key

# CORS (adjust for your frontend URL)
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# MCP Server (Required for AI Chat)
USE_MCP_TOOLS=true
MCP_SERVER_URL=http://localhost:8001

# Redis (Optional - for token blacklisting)
REDIS_ENABLED=false
REDIS_URL=redis://localhost:6379
```

**Frontend** - Create `frontend/.env.local`:

```bash
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_URL=http://localhost:3000

# WebSocket (if using WebSocket features)
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

### Running the Application

#### Option 1: Run Separately (Recommended for Development)

Open **three terminal windows**:

**Terminal 1 - Backend:**
```bash
cd backend
venv\Scripts\activate      # Windows
# source venv/bin/activate # macOS/Linux
python main.py
```

**Terminal 2 - MCP Server:**
```bash
cd mcp_server
pip install -r requirements.txt  # First time only
python server.py
```

**Terminal 3 - Frontend:**
```bash
cd frontend
npm run dev
```

#### Option 2: Run with npm scripts (from root)

```bash
# Install concurrently first
npm install

# Run both frontend and backend
npm run dev
```

> ⚠️ **Note**: The concurrent script is Windows-specific. For macOS/Linux, use Option 1 or modify the script.

### Access Points

Once running, access the application at:

| Service | URL | Description |
|---------|-----|-------------|
| 🎨 **Frontend** | http://localhost:3000 | Main web application |
| 🔧 **Backend API** | http://localhost:8000 | FastAPI REST API |
| 🤖 **MCP Server** | http://localhost:8001 | AI Tools Server |
| 📚 **API Docs** | http://localhost:8000/docs | Interactive Swagger UI |
| 📕 **ReDoc** | http://localhost:8000/redoc | Alternative API docs |
| 💚 **Health Check** | http://localhost:8000/api/v1/health | API health status |

---

## ⚙️ Environment Configuration

### Backend Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | ✅ Yes | - | PostgreSQL connection string |
| `JWT_SECRET` | ✅ Yes | - | Secret key for JWT tokens |
| `HOST` | No | `0.0.0.0` | Server host |
| `PORT` | No | `8000` | Server port |
| `DEBUG` | No | `true` | Enable debug mode |
| `OPENAI_API_KEY` | No | - | OpenAI API key for AI features |
| `GEMINI_API_KEY` | No | - | Google Gemini API key (alternative) |
| `CORS_ORIGINS` | No | `localhost:3000` | Allowed CORS origins |
| `USE_MCP_TOOLS` | No | `false` | Enable MCP server integration |
| `REDIS_ENABLED` | No | `false` | Enable Redis for token blacklisting |

### Frontend Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `NEXT_PUBLIC_API_URL` | ✅ Yes | - | Backend API URL |
| `NEXT_PUBLIC_APP_URL` | No | - | Frontend application URL |
| `NEXT_PUBLIC_WS_URL` | No | - | WebSocket URL (if enabled) |

---

## 🔌 MCP Server (Required)

The **MCP (Model Context Protocol) Server** provides AI capabilities for the chat assistant through task management tools. It runs as a **separate service** on port 8001 and is **required** for the AI chat functionality to work properly.

### What MCP Server Provides

- AI-powered task management tools (add, list, complete, delete, update tasks)
- JWT authentication integration with the backend
- Structured logging and performance monitoring
- FastAPI client for seamless backend communication

### Running MCP Server

**1. Install dependencies:**
```bash
cd mcp_server
pip install -r requirements.txt
```

**2. Configure environment:**

Create `mcp_server/.env`:
```bash
DATABASE_URL=postgresql://user:password@localhost:5432/todoapp
JWT_SECRET=same-as-backend-jwt-secret
MCP_SERVER_PORT=8001
FASTAPI_BACKEND_URL=http://localhost:8000
```

**3. Run the server:**
```bash
# Option A: FastMCP server (stdio transport)
python main.py

# Option B: HTTP server (for REST clients)
python server.py
```

> **Note**: The MCP server communicates with the backend API on port 8000, so ensure the backend is running before starting the MCP server.

### MCP Server Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/tools/add_task` | POST | Add a new task |
| `/tools/list_tasks` | POST | List user tasks |
| `/tools/complete_task` | POST | Mark task complete |
| `/tools/delete_task` | POST | Delete a task |
| `/tools/update_task` | POST | Update a task |

---

## 📚 API Documentation

### Interactive Documentation

Visit **http://localhost:8000/docs** for interactive Swagger UI documentation.

### Key Endpoints

#### Authentication
```http
POST /api/v1/auth/sign-up    # User registration
POST /api/v1/auth/sign-in    # User login
POST /api/v1/auth/sign-out   # User logout
GET  /api/v1/auth/me         # Get current user info
GET  /api/v1/auth/verify     # Verify token validity
```

#### Task Management
```http
GET    /api/tasks              # List user tasks (with filtering)
POST   /api/tasks              # Create new task
GET    /api/tasks/{id}         # Get specific task
PUT    /api/tasks/{id}         # Update task
PATCH  /api/tasks/{id}         # Partial update task
DELETE /api/tasks/{id}         # Delete task
PATCH  /api/tasks/{id}/complete # Toggle task completion
```

#### AI Chat
```http
POST   /api/{user_id}/chat     # Send message to AI assistant
GET    /api/conversations      # List user conversations
POST   /api/conversations      # Create new conversation
GET    /api/conversations/{id}/messages # Get conversation messages
```

### Authentication

All protected endpoints require:
```http
Authorization: Bearer <your-jwt-token>
```

---

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest --cov=src --cov-report=term-missing
```

### Frontend Tests
```bash
cd frontend
npm run lint        # ESLint check
npm run test        # Jest unit tests
npm run test:e2e    # Playwright E2E tests
```

---

## 🚀 Deployment

### Production Environment

| Component | Recommended Platform |
|-----------|---------------------|
| Frontend | Vercel, Netlify, AWS Amplify |
| Backend | Railway, Render, AWS ECS |
| Database | Neon PostgreSQL, AWS RDS |
| MCP Server | Same as backend (if used) |

### Production Configuration

1. Set `DEBUG=false` in backend
2. Use secure `JWT_SECRET` values
3. Configure proper `CORS_ORIGINS`
4. Use production database URLs
5. Enable HTTPS for all services

---

## 🤖 AI Chat Assistant Usage

### Getting Started
1. **Sign in** to your account
2. **Click the chat button** in the bottom-right corner
3. **Start chatting** with the AI assistant

### Supported Commands

| Command | Example |
|---------|---------|
| Add task | "Add task: Buy groceries" |
| Complete task | "Complete my homework task" |
| List tasks | "Show me my high priority tasks" |
| Get suggestions | "What should I work on today?" |
| Update priority | "Set task X to high priority" |
| Delete task | "Delete the meeting task" |

### Mobile Features
- **Voice Input**: Tap the microphone button to dictate
- **Touch Optimization**: All buttons sized for mobile
- **Keyboard Awareness**: Interface adapts to virtual keyboard

---

## 🤝 Contributing

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Make** changes with proper testing
4. **Commit** with descriptive messages
5. **Push** to your feature branch
6. **Open** a Pull Request

### Development Standards
- TypeScript strict mode with full type coverage
- Python type hints required for all functions
- Write tests for new features
- Follow PEP 8 (Python) and ESLint rules (TypeScript)

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<p align="center">
  <strong>Built with ❤️ using Next.js, FastAPI, PostgreSQL, and AI</strong><br>
  © 2025 TODO-EVOLUTION • AI-Powered Productivity Platform
</p>