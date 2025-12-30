<div align="center">

# 📝 TODO EVOLUTION

### AI-Powered Task Management Platform

[![Python](https://img.shields.io/badge/Python-3.13+-blue.svg?style=flat-square&logo=python)](https://www.python.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.x-blue.svg?style=flat-square&logo=typescript)](https://www.typescriptlang.org/)
[![Next.js](https://img.shields.io/badge/Next.js-16.0.7-black.svg?style=flat-square&logo=next.js)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.121.2-green.svg?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-blue.svg?style=flat-square&logo=postgresql)](https://www.postgresql.org/)
[![Kubernetes](https://img.shields.io/badge/Kubernetes-1.28+-326ce5.svg?style=flat-square&logo=kubernetes)](https://kubernetes.io/)
[![Helm](https://img.shields.io/badge/Helm-3.19+-0fd69e.svg?style=flat-square&logo=helm)](https://helm.sh/)
[![License](https://img.shields.io/badge/License-MIT-green.svg?style=flat-square)](LICENSE)

**A modern, full-stack task management application that evolves from console to cloud**

[Features](#-features) • [Quick Start](#-quick-start) • [Architecture](#-architecture) • [Deployment](#-deployment) • [API Docs](#-api-documentation) • [Contributing](#-contributing)

</div>

---

## 📖 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Architecture](#-architecture)
- [Quick Start](#-quick-start)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Configuration](#configuration)
  - [Running Locally](#running-locally)
- [Kubernetes Deployment](#-kubernetes-deployment)
  - [Minikube Quick Start](#minikube-quick-start)
  - [Automated Deployment](#automated-deployment)
  - [Monitoring & Scaling](#monitoring--scaling)
- [Environment Variables](#-environment-variables)
- [API Documentation](#-api-documentation)
- [Development](#-development)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🎯 Overview

**TODO Evolution** is a sophisticated task management platform that demonstrates modern full-stack development with AI capabilities. The project showcases an evolutionary journey from a simple console application to a production-ready, cloud-native solution.

### Project Evolution

| Phase | Description | Status |
|-------|-------------|--------|
| **Phase I** | Console-based task management with Python | ✅ Complete |
| **Phase II** | Full-stack web application with authentication | ✅ Complete |
| **Phase III** | AI-powered chat assistant with natural language processing | ✅ Production Ready |
| **Phase IV** | Kubernetes deployment with Helm charts | ✅ Production Ready |

### Key Highlights

- 🤖 **AI Chat Assistant** - Manage tasks through natural conversations
- 🔐 **JWT Authentication** - Secure user authentication with refresh tokens
- 📱 **Mobile-First Design** - Responsive UI optimized for all devices
- 🎨 **Modern Tech Stack** - Next.js 16, FastAPI, PostgreSQL
- ☸️ **Cloud-Native** - Kubernetes-ready with Helm charts
- 🐳 **Containerized** - Multi-stage Docker builds with security hardening
- 🔄 **Real-Time Updates** - Instant task synchronization
- 🌍 **Multi-Tenant** - User-isolated data architecture

---

## ✨ Features

### 🔐 User Authentication

- Secure JWT-based authentication with bcrypt password hashing
- Access and refresh token pattern with automatic token rotation
- Token blacklisting for enhanced security
- Protected routes with role-based access control
- Seamless sign-in/sign-out experience

### 📋 Intelligent Task Management

| Feature | Description |
|---------|-------------|
| **CRUD Operations** | Create, read, update, and delete tasks with ease |
| **Priority Levels** | High, medium, low, and urgent task classification |
| **Smart Filtering** | Filter tasks by priority, status, and date |
| **Quick Actions** | Mark tasks complete/incomplete with one click |
| **User Isolation** | Each user sees only their own tasks (multi-tenant) |

### 🤖 AI Chat Assistant

> **"Add a task to buy groceries tomorrow"**
> ✅ *Task created successfully*

- **Natural Language Processing** - Conversational task management
- **Context-Aware** - Intelligent recommendations based on patterns
- **Real-Time Processing** - Instant responses and updates
- **Voice Input** - Touch-optimized mobile voice commands
- **Productivity Insights** - Task completion analytics and suggestions

### 🎨 Modern Web Interface

- **Responsive Design** - Flawless experience on mobile, tablet, and desktop
- **Touch-First** - Optimized for mobile interactions and gestures
- **Dark/Light Mode** - Eye-friendly theme switching
- **Accessibility** - WCAG compliant with keyboard navigation
- **Real-Time Sync** - Live updates across devices

### ☸️ Production-Ready Deployment

- **Kubernetes Support** - Deploy to any Kubernetes cluster
- **Helm Charts** - One-command deployment with Helm
- **Docker Images** - Multi-stage builds with security best practices
- **Health Monitoring** - Built-in liveness and readiness probes
- **Resource Management** - CPU/memory limits and requests
- **Rolling Updates** - Zero-downtime deployments

---

## 🛠️ Tech Stack

### Frontend

| Technology | Version | Purpose |
|:-----------|:--------:|:--------|
| ![Next.js](https://img.shields.io/badge/Next.js-16.0.7-black?style=flat-square&logo=next.js) | 16.0.7 | React framework with App Router |
| ![TypeScript](https://img.shields.io/badge/TypeScript-5.x-blue?style=flat-square&logo=typescript) | 5.x | Type-safe development |
| ![Tailwind CSS](https://img.shields.io/badge/Tailwind-4.x-38bdf8?style=flat-square&logo=tailwindcss) | 4.x | Utility-first styling |
| ![React Query](https://img.shields.io/badge/React_Query-5.x-ff4154?style=flat-square) | 5.x | Server state management |
| ![Lucide](https://img.shields.io/badge/Lucide-0.400+-2f2f2f?style=flat-square) | 0.400+ | Beautiful icon set |

### Backend

| Technology | Version | Purpose |
|:-----------|:--------:|:--------|
| ![FastAPI](https://img.shields.io/badge/FastAPI-0.121.2-green?style=flat-square&logo=fastapi) | 0.121.2 | High-performance REST API |
| ![Python](https://img.shields.io/badge/Python-3.13+-blue?style=flat-square&logo=python) | 3.13+ | Backend language |
| ![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-blue?style=flat-square&logo=postgresql) | 15+ | Relational database |
| ![SQLModel](https://img.shields.io/badge/SQLModel-0.0.27-9b59b6?style=flat-square) | 0.0.27 | ORM with Pydantic |
| ![OpenAI](https://img.shields.io/badge/OpenAI-2.8+-412991?style=flat-square&logo=openai) | 2.8+ | AI integration |

### DevOps & Orchestration

| Technology | Version | Purpose |
|:-----------|:--------:|:--------|
| ![Kubernetes](https://img.shields.io/badge/Kubernetes-1.28+-326ce5?style=flat-square&logo=kubernetes) | 1.28+ | Container orchestration |
| ![Helm](https://img.shields.io/badge/Helm-3.19+-0fd69e?style=flat-square&logo=helm) | 3.19+ | Package manager |
| ![Minikube](https://img.shields.io/badge/Minikube-Latest-39afd0?style=flat-square&logo=minikube) | Latest | Local Kubernetes |
| ![Docker](https://img.shields.io/badge/Docker-Latest-2496ed?style=flat-square&logo=docker) | Latest | Container runtime |

---

## 🏗️ Architecture

### System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                          │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │           Next.js 16 Frontend (Port 3000)                │  │
│  │  • TypeScript • Tailwind CSS • React Query               │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────────┘
                              │ HTTP/REST API
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                         API GATEWAY                             │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │           FastAPI Backend (Port 8000)                    │  │
│  │  • JWT Auth • CORS • Rate Limiting                       │  │
│  └──────────────────────────────────────────────────────────┘  │
└──────────────┬───────────────────────────┬──────────────────────┘
               │                           │
               ▼                           ▼
┌──────────────────────┐    ┌──────────────────────────────────┐
│  POSTgreSQL DATABASE │    │      MCP SERVER (Port 8001)       │
│  • User Data         │    │  • Task Management Tools         │
│  • Task Data         │    │  • AI Agent Integration          │
│  • Conversations     │    │  • JWT Authentication            │
└──────────────────────┘    └──────────────────────────────────┘
```

### Kubernetes Deployment Architecture

```
Minikube/Kubernetes Cluster
│
├── Namespace: default
│
├── Frontend Deployment
│   ├── Replicas: 2
│   ├── Image: todo-frontend:1.0.5
│   ├── Service: LoadBalancer
│   └── Resources: CPU 100m-500m, Memory 128Mi-512Mi
│
├── Backend Deployment
│   ├── Replicas: 2
│   ├── Image: todo-backend:2.0.2
│   ├── Service: NodePort
│   └── Resources: CPU 100m-500m, Memory 128Mi-512Mi
│
└── MCP Server Deployment
    ├── Replicas: 1
    ├── Image: todo-mcp-server:1.0.2
    ├── Service: ClusterIP (internal)
    └── Resources: CPU 100m-500m, Memory 128Mi-512Mi
```

---

## 🚀 Quick Start

Get the application running locally in under 5 minutes!

### Prerequisites

| Requirement | Minimum Version | Installation |
|:------------|:---------------:|:-------------|
| ![Node.js](https://img.shields.io/badge/Node.js-18.0+-green?style=flat-square&logo=node.js) | 18.0+ | [nodejs.org](https://nodejs.org/) |
| ![Python](https://img.shields.io/badge/Python-3.11+-blue?style=flat-square&logo=python) | 3.11+ (3.13 recommended) | [python.org](https://www.python.org/) |
| ![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-blue?style=flat-square&logo=postgresql) | 15+ | [postgresql.org](https://www.postgresql.org/) or use [Neon](https://neon.tech/) |
| ![Git](https://img.shields.io/badge/Git-Latest-orange?style=flat-square&logo=git) | Latest | [git-scm.com](https://git-scm.com/) |

> **💡 Tip:** Use [Neon PostgreSQL](https://neon.tech/) for a free, managed PostgreSQL database.

### Installation

#### 1. Clone the Repository

```bash
git clone https://github.com/iamKhan79690/TODO-EVOLUTION.git
cd TODO-EVOLUTION
```

#### 2. Backend Setup

```bash
# Navigate to backend
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
# Navigate to frontend (from project root)
cd frontend

# Install dependencies
npm install
```

### Configuration

Create environment files with your configuration:

#### Backend Environment (`backend/.env`)

```bash
# Database (Required)
DATABASE_URL=postgresql+asyncpg://user:password@ep-xyz.region.aws.neon.tech/neondb?ssl=require

# Authentication (Required)
JWT_SECRET=your-secure-jwt-secret-min-32-characters

# Server Configuration
HOST=0.0.0.0
PORT=8000
LOG_LEVEL=INFO

# AI Services (Optional - enables AI chat)
OPENAI_API_KEY=sk-your-openai-api-key
# OR
GEMINI_API_KEY=AIzaSy-your-gemini-api-key

# MCP Server (Required for AI Chat)
USE_MCP_TOOLS=true
MCP_SERVER_URL=http://localhost:8001

# CORS
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

#### Frontend Environment (`frontend/.env.local`)

```bash
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_URL=http://localhost:3000
```

### Running Locally

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

### Access the Application

| Service | URL | Description |
|:--------|:----|:-----------|
| 🎨 **Frontend** | http://localhost:3000 | Main web application |
| 🔧 **Backend API** | http://localhost:8000 | REST API |
| 🤖 **MCP Server** | http://localhost:8001 | AI Tools Server |
| 📚 **API Docs** | http://localhost:8000/docs | Interactive Swagger UI |
| 💚 **Health Check** | http://localhost:8000/health/ | API health status |

---

## ☸️ Kubernetes Deployment

Deploy the entire application stack to Kubernetes with Helm charts.

### Prerequisites for Kubernetes

| Requirement | Minimum Version | Installation |
|:------------|:---------------:|:-------------|
| ![Minikube](https://img.shields.io/badge/Minikube-Latest-39afd0?style=flat-square&logo=minikube) | Latest | [Install Guide](https://minikube.sigs.k8s.io/docs/start/) |
| ![Docker](https://img.shields.io/badge/Docker-Latest-2496ed?style=flat-square&logo=docker) | Latest | [Docker Desktop](https://www.docker.com/products/docker-desktop) |
| ![kubectl](https://img.shields.io/badge/kubectl-1.28+-326ce5?style=flat-square&logo=kubernetes) | 1.28+ | [Install Guide](https://kubernetes.io/docs/tasks/tools/) |
| ![Helm](https://img.shields.io/badge/Helm-3.19+-0fd69e?style=flat-square&logo=helm) | 3.19+ | [Install Guide](https://helm.sh/docs/intro/install/) |
| **System Resources** | 2 CPUs, 6GB RAM | Adjust based on your system |

### Minikube Quick Start

#### Step 1: Start Minikube

```bash
# Start Minikube with Docker driver
minikube start --cpus=2 --memory=6144 --disk-size=20g --driver=docker

# Enable required addons
minikube addons enable ingress
minikube addons enable metrics-server

# Verify status
minikube status
```

#### Step 2: Configure Docker Environment

```bash
# Point Docker CLI to Minikube daemon
eval $(minikube docker-env)  # Linux/macOS
# minikube docker-env | Invoke-Expression  # Windows PowerShell

# Verify
docker ps
```

#### Step 3: Build Docker Images

```bash
# Build all three images (parallel in separate terminals for speed)
docker build -t todo-frontend:1.0.5 ./frontend
docker build -t todo-backend:2.0.2 ./backend
docker build -t todo-mcp-server:1.0.2 ./mcp_server

# Verify
docker images | grep todo
```

#### Step 4: Load Images into Minikube

```bash
minikube image load todo-frontend:1.0.5
minikube image load todo-backend:2.0.2
minikube image load todo-mcp-server:1.0.2
```

#### Step 5: Configure Helm Secrets

Edit `helm-chart/values.yaml`:

```yaml
secrets:
  databaseURL: "postgresql+asyncpg://user:pass@ep-xyz.region.aws.neon.tech/neondb?ssl=require"
  jwtSecret: "your-secure-jwt-secret-min-32-characters"
  openaiAPIKey: "sk-your-openai-key"
  geminiAPIKey: "AIzaSy-your-gemini-key"
```

#### Step 6: Deploy with Helm

```bash
# Lint chart first
helm lint ./helm-chart

# Install application
helm install todo-evolution ./helm-chart

# Or upgrade existing deployment
helm upgrade todo-evolution ./helm-chart

# Monitor pods
kubectl get pods -w
```

#### Step 7: Access Deployed Application

```bash
# Get frontend URL
minikube service todo-evolution-frontend --url
# Output: http://127.0.0.1:53223

# Get backend URL
minikube service todo-evolution-backend --url
# Output: http://127.0.0.1:53263

# Open in browser
minikube service todo-evolution-frontend
```

### Automated Deployment

Use the provided scripts for automated deployment:

**Linux/macOS:**
```bash
chmod +x rebuild-and-redeploy.sh
./rebuild-and-redeploy.sh
```

**Windows:**
```powershell
.\rebuild-and-redeploy.bat
```

### Monitoring & Scaling

#### Check Pod Status

```bash
# List all pods
kubectl get pods

# Describe pod for details
kubectl describe pod <pod-name>

# View logs
kubectl logs <pod-name> --tail=50 -f
```

#### Scale Applications

```bash
# Scale frontend to 3 replicas
kubectl scale deployment/todo-evolution-frontend --replicas=3

# Scale backend to 4 replicas
kubectl scale deployment/todo-evolution-backend --replicas=4
```

#### Update Application

```bash
# Build new image
docker build -t todo-backend:2.0.3 ./backend
minikube image load todo-backend:2.0.3

# Update values.yaml tag to 2.0.3
# Then upgrade
helm upgrade todo-evolution ./helm-chart

# Monitor rolling update
kubectl rollout status deployment/todo-evolution-backend
```

#### Rollback

```bash
# View history
helm history todo-evolution

# Rollback to previous version
helm rollback todo-evolution
```

### Cleanup

```bash
# Uninstall Helm release
helm uninstall todo-evolution

# Stop Minikube
minikube stop

# Delete cluster (clean slate)
minikube delete
```

---

## 🔧 Environment Variables

### Backend Environment Variables

| Variable | Required | Default | Description |
|:---------|:--------:|:-------:|:------------|
| `DATABASE_URL` | ✅ | - | PostgreSQL connection string with asyncpg driver |
| `JWT_SECRET` | ✅ | - | Secret key for JWT tokens (min 32 characters) |
| `HOST` | ❌ | `0.0.0.0` | Server host address |
| `PORT` | ❌ | `8000` | Server port |
| `LOG_LEVEL` | ❌ | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `OPENAI_API_KEY` | ❌ | - | OpenAI API key for AI features |
| `GEMINI_API_KEY` | ❌ | - | Google Gemini API key (alternative to OpenAI) |
| `CORS_ORIGINS` | ❌ | `localhost:3000` | Allowed CORS origins (comma-separated) |
| `USE_MCP_TOOLS` | ❌ | `false` | Enable MCP server integration |
| `MCP_SERVER_URL` | ❌ | `http://localhost:8001` | MCP server URL |
| `REDIS_ENABLED` | ❌ | `false` | Enable Redis for token blacklisting |

### Frontend Environment Variables

| Variable | Required | Default | Description |
|:---------|:--------:|:-------:|:------------|
| `NEXT_PUBLIC_API_URL` | ✅ | - | Backend API URL |
| `NEXT_PUBLIC_APP_URL` | ❌ | - | Frontend application URL |
| `NEXT_PUBLIC_WS_URL` | ❌ | - | WebSocket URL (if enabled) |

---

## 📚 API Documentation

### Interactive Documentation

Once the backend is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

#### Authentication

```http
POST /api/v1/auth/sign-up    # User registration
POST /api/v1/auth/sign-in    # User login
POST /api/v1/auth/sign-out   # User logout
GET  /api/v1/auth/me         # Get current user
GET  /api/v1/auth/verify     # Verify token
```

#### Task Management

```http
GET    /api/tasks              # List tasks (with filtering)
POST   /api/tasks              # Create task
GET    /api/tasks/{id}         # Get task details
PUT    /api/tasks/{id}         # Update task
DELETE /api/tasks/{id}         # Delete task
PATCH  /api/tasks/{id}/complete # Toggle completion
```

#### AI Chat

```http
POST   /api/{user_id}/chat     # Send message to AI assistant
GET    /api/conversations      # List conversations
POST   /api/conversations      # Create conversation
GET    /api/conversations/{id}/messages # Get messages
```

### Authentication

All protected endpoints require a JWT token:

```http
Authorization: Bearer <your-jwt-token>
```

---

## 💻 Development

### Backend Development

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Run with hot reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Run tests
pytest --cov=src --cov-report=term-missing

# Format code
black .
isort .

# Lint
flake8
mypy src/
```

### Frontend Development

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev

# Run type checking
npm run type-check

# Lint code
npm run lint
npm run lint:fix

# Run tests
npm run test
npm run test:e2e
```

### Code Style

- **Python**: PEP 8, Black formatter, isort imports
- **TypeScript**: ESLint, Prettier
- **Commit Messages**: Conventional Commits specification

---

## 🤝 Contributing

We welcome contributions! Please follow these guidelines:

### How to Contribute

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Make** changes with proper tests
4. **Commit** with conventional commits (`feat: add user profile`)
5. **Push** to your branch (`git push origin feature/amazing-feature`)
6. **Open** a Pull Request

### Development Standards

- [x] TypeScript strict mode with full type coverage
- [x] Python type hints for all functions
- [x] Write tests for new features (pytest for backend, Jest for frontend)
- [x] Update documentation for API changes
- [x] Follow code style guidelines (PEP 8 for Python, ESLint for TypeScript)

### Reporting Issues

Found a bug? Have a feature request?

1. Check existing [issues](https://github.com/iamKhan79690/TODO-EVOLUTION/issues)
2. Create a new issue with:
   - Clear title and description
   - Steps to reproduce (for bugs)
   - Expected vs actual behavior
   - Environment details (OS, Python/Node versions)

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2025 TODO-EVOLUTION

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction...
```

---

## 🙏 Acknowledgments

- **Next.js Team** - For the amazing React framework
- **FastAPI Team** - For the modern, fast Python web framework
- **OpenAI** - For GPT models powering the AI assistant
- **Neon** - For the excellent PostgreSQL hosting
- **Kubernetes & Helm Teams** - For container orchestration tools

---

## 📞 Support & Contact

- 📧 Email: support@todo-evolution.com
- 🐦 Twitter: [@todoevolution](https://twitter.com/todoevolution)
- 💬 Discord: [Join our community](https://discord.gg/todoevolution)
- 📖 Documentation: [docs.todo-evolution.com](https://docs.todo-evolution.com)

---

<div align="center">

### 🌟 Star this project on GitHub!

**Built with ❤️ using Next.js, FastAPI, PostgreSQL, Kubernetes, and AI**

© 2025 TODO-EVOLUTION • AI-Powered Productivity Platform

[⬆ Back to Top](#-todo-evolution)

</div>
