# 📝 EVOLUTION-OF-TODO

A sophisticated task management application evolving from console to full-stack web application with intelligent features.

[![Python](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![TypeScript](https://img.shields.io/badge/typescript-5.x-blue.svg)](https://www.typescriptlang.org/)
[![Next.js](https://img.shields.io/badge/next.js-16+-black.svg)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/fastapi-0.121+-green.svg)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/postgresql-15+-blue.svg)](https://www.postgresql.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Test Status](https://img.shields.io/badge/tests-22%2F22%20passing-brightgreen.svg)](test_report.md)

## 🎯 Project Overview

Todo Evolution is a modern task management platform that demonstrates the evolution from a console application to a full-stack web solution. Built with cutting-edge technology and best practices, it provides a robust foundation for productivity applications.

### 🚀 Phase II: Production-Ready Full-Stack Application ✅

**Status**: ✅ **PRODUCTION READY** - Comprehensive testing completed (22/22 tests passing)

A modern web application with real-time capabilities, user authentication, and advanced task management features.

## 🌟 Key Features

### 🔐 User Authentication
- **Secure Registration & Login**: JWT-based authentication with bcrypt password hashing
- **Token Management**: Access and refresh token pattern with automatic token blacklisting
- **Protected Routes**: All sensitive operations require authentication
- **Session Management**: Secure sign-out with token revocation

### 📋 Advanced Task Management
- **CRUD Operations**: Create, read, update, and delete tasks seamlessly
- **Priority Levels**: High, medium, and low priority classification
- **Task Status**: Mark tasks as complete/incomplete with visual indicators
- **Smart Filtering**: Filter tasks by priority, completion status, and more
- **User Isolation**: Each user sees only their own tasks (multi-tenant architecture)

### 🎨 Modern Web Interface
- **Responsive Design**: Mobile-first approach that works on all devices
- **Real-time Updates**: Instant task synchronization across devices
- **Intuitive UI**: Clean, modern interface built with Tailwind CSS
- **Loading States**: Proper loading indicators and error handling
- **Accessibility**: Built with accessibility best practices

### 🛠️ Developer Experience
- **Hot Reloading**: Instant development feedback
- **TypeScript**: Full type safety across frontend and backend
- **API Documentation**: Interactive OpenAPI/Swagger documentation
- **Database Migrations**: Automated schema management
- **Environment Configuration**: Flexible environment variable setup

## 🏗️ Tech Stack

### Frontend
- **Framework**: Next.js 16.0.7 with App Router
- **Language**: TypeScript 5.x
- **Styling**: Tailwind CSS 4.x
- **UI Components**: Lucide React Icons
- **State Management**: React Query (TanStack Query)
- **Form Handling**: React Hook Form with Zod validation
- **Authentication**: Better Auth client library

### Backend
- **Framework**: FastAPI 0.121.2
- **Language**: Python 3.13+
- **Database**: PostgreSQL (Neon)
- **ORM**: SQLModel 2.0.44 with SQLAlchemy 2.0
- **Authentication**: JWT with Better Auth
- **Password Hashing**: Bcrypt
- **Validation**: Pydantic 2.12.5
- **API Documentation**: OpenAPI/Swagger

### Development Tools
- **Package Management**: UV (Python) + npm (Node.js)
- **Code Quality**: Ruff (Python) + ESLint (TypeScript)
- **Testing**: Comprehensive integration testing
- **Documentation**: Auto-generated API docs

## 🚀 Quick Setup

### Prerequisites
- **Node.js**: 18.0+
- **Python**: 3.11+
- **Git**: Latest version
- **PostgreSQL**: Neon account (for cloud database)

### ⚡ Fast Setup (5 minutes)

1. **Clone the repository**
```bash
git clone https://github.com/iamKhan79690/EVOLUTION-OF-TODO.git
cd "The Evolution of Todo"
```

2. **Environment Setup**
```bash
# Backend environment
cd backend
python -m venv venv

# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
```

3. **Configure Environment Variables**
```bash
# Create backend/.env file
cp .env.example .env

# Edit .env with your configuration
```

4. **Start Development Servers**
```bash
# Terminal 1: Start backend
cd backend
python main.py

# Terminal 2: Start frontend
cd frontend
npm install
npm run dev
```

### 🌐 Access Points

Once running, access the application at:

- **🎨 Frontend Application**: http://localhost:3000
- **🔧 Backend API**: http://localhost:8000
- **📚 API Documentation**: http://localhost:8000/docs
- **💚 Health Check**: http://localhost:8000/api/v1/health

## 🔧 Environment Configuration

### Backend Environment Variables (.env)

Create `backend/.env` with the following:

```bash
# Database Configuration
DATABASE_URL=postgresql://user:password@ep-xyz.us-east-2.aws.neon.tech/dbname

# Authentication Secrets
BETTER_AUTH_SECRET=your-32-character-secret-key-here
JWT_SECRET=your-jwt-secret-key-here

# JWT Settings
JWT_EXPIRE_MINUTES=30

# Development Settings
DEBUG=true
HOST=0.0.0.0
PORT=8000

# CORS Origins (comma-separated)
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

### Frontend Environment Variables (.env.local)

Create `frontend/.env.local` with:

```bash
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_URL=http://localhost:3000

# Authentication
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=your-nextauth-secret-here
```

## 📚 API Documentation

### Interactive Documentation
Visit **http://localhost:8000/docs** for interactive API documentation powered by Swagger UI.

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

#### System
```http
GET /api/v1/health            # Health check endpoint
GET /                        # API root information
```

### Authentication Headers
All protected endpoints require:
```http
Authorization: Bearer <your-jwt-token>
```

## 🧪 Testing & Quality Assurance

### Comprehensive Test Suite
- ✅ **22/22 tests passing** (100% success rate)
- ✅ Authentication system testing
- ✅ CRUD operations validation
- ✅ Security and authorization testing
- ✅ API endpoint functionality

### View Test Results
Detailed test reports are available in [**test_report.md**](test_report.md)

### Running Tests
```bash
# Backend tests
cd backend
pytest --cov=src --cov-report=term-missing

# Frontend linting
cd frontend
npm run lint
```

### Code Quality
- **TypeScript**: Full type safety
- **Python**: Type hints and mypy checking
- **Linting**: Ruff (Python) + ESLint (TypeScript)
- **Formatting**: Auto-formatting with Black and Prettier

## 🏗️ Architecture Overview

### Backend Architecture (FastAPI)
```
backend/
├── src/
│   ├── api/          # API route handlers
│   ├── auth/         # Authentication logic
│   ├── core/         # Core configuration
│   ├── dependencies/ # FastAPI dependencies
│   ├── models/       # SQLModel database models
│   ├── schemas/      # Pydantic data schemas
│   └── services/     # Business logic services
├── main.py           # Application entry point
└── requirements.txt  # Python dependencies
```

### Frontend Architecture (Next.js)
```
frontend/
├── src/
│   ├── app/          # Next.js App Router pages
│   ├── components/   # Reusable React components
│   ├── hooks/        # Custom React hooks
│   ├── lib/          # Utility libraries
│   └── types/        # TypeScript type definitions
├── public/           # Static assets
└── package.json      # Node.js dependencies
```

### Database Schema
- **Users Table**: Authentication and user data
- **Tasks Table**: Task information with user relationships
- **Token Blacklist**: Revoked authentication tokens

## 🔒 Security Features

### Authentication & Authorization
- **JWT Tokens**: Secure access and refresh token pattern
- **Password Hashing**: Bcrypt with salt rounds
- **Token Blacklisting**: Secure logout functionality
- **Route Protection**: All sensitive endpoints require authentication

### Data Security
- **User Isolation**: Multi-tenant architecture
- **Input Validation**: Comprehensive input sanitization
- **SQL Injection Prevention**: SQLAlchemy ORM protection
- **CORS Configuration**: Proper cross-origin resource sharing

## 🚀 Deployment

### Development Environment
- **Frontend**: http://localhost:3000 (Next.js dev server)
- **Backend**: http://localhost:8000 (FastAPI dev server)

### Production Deployment (Recommended)
- **Frontend**: Vercel, Netlify, or AWS Amplify
- **Backend**: Railway, Render, or AWS ECS
- **Database**: Neon PostgreSQL (cloud) or AWS RDS
- **Environment**: Configure production environment variables

## 🤝 Contributing

We welcome contributions! Please follow these guidelines:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Make** your changes with proper testing
4. **Follow** coding standards and type hints
5. **Test** thoroughly (ensure all tests pass)
6. **Commit** with descriptive messages
7. **Push** to your feature branch
8. **Open** a Pull Request

### Development Standards
- **TypeScript**: Strict mode with full type coverage
- **Python**: Type hints required for all functions
- **Testing**: Write tests for new features
- **Documentation**: Update README and API docs
- **Code Style**: Follow PEP 8 (Python) and ESLint rules (TypeScript)

## 📈 Project Status

### ✅ Completed Features
- [x] User authentication system
- [x] Task CRUD operations
- [x] Priority levels and filtering
- [x] User data isolation
- [x] JWT token management
- [x] API documentation
- [x] Responsive web interface
- [x] Database integration
- [x] Security best practices

### 🚧 In Progress
- [ ] Advanced search functionality
- [ ] Task categories and tags
- [ ] Due dates and reminders
- [ ] Email notifications
- [ ] Team collaboration features

### 📋 Planned Features
- [ ] Mobile app (React Native)
- [ ] Real-time collaboration
- [ ] Advanced analytics dashboard
- [ ] Third-party integrations
- [ ] API rate limiting
- [ ] Comprehensive audit logging

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **[Next.js](https://nextjs.org/)** - React framework
- **[FastAPI](https://fastapi.tiangolo.com/)** - Modern Python web framework
- **[SQLModel](https://sqlmodel.tiangolo.com/)** - SQL database in Python
- **[Tailwind CSS](https://tailwindcss.com/)** - Utility-first CSS framework
- **[Better Auth](https://better-auth.com/)** - Authentication solution

---

<p align="center">
  <strong>Built with ❤️ using Next.js, FastAPI, and PostgreSQL</strong><br>
  © 2025 EVOLUTION-OF-TODO • Production Ready ✅
</p>