# Quickstart Guide: Frontend Task Management UI

**Feature**: Frontend Task Management UI
**Target Audience**: Developers
**Estimated Setup Time**: 15-20 minutes
**Created**: 2025-12-07

## Prerequisites

### Required Software
- **Node.js**: 18.0+ (LTS version recommended)
- **npm**: 9.0+ or **yarn**: 1.22+
- **Git**: Latest stable version
- **VS Code** or equivalent code editor with TypeScript support

### Recommended Extensions
```json
{
  "recommendations": [
    "ms-vscode.vscode-typescript-next",
    "bradlc.vscode-tailwindcss",
    "esbenp.prettier-vscode",
    "ms-vscode.vscode-eslint",
    "ms-vscode.vscode-json",
    "formulahendry.auto-rename-tag",
    "christian-kohler.path-intellisense"
  ]
}
```

### Environment Requirements
- **Backend API**: FastAPI server running on `http://localhost:8000`
- **Database**: PostgreSQL (Neon or local)
- **Authentication**: Better Auth configured and running
- **Redis**: For session management (required by Better Auth)

## Project Setup

### 1. Clone Repository and Install Dependencies
```bash
# Clone the repository
git clone <repository-url>
cd "The Evolution of Todo"

# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# or with yarn
yarn install
```

### 2. Environment Configuration
Create `.env.local` file in the `frontend` directory:

```env
# Next.js Configuration
NEXT_PUBLIC_APP_URL=http://localhost:3000
NEXT_PUBLIC_FASTAPI_URL=http://localhost:8000

# Better Auth Configuration
BETTER_AUTH_SECRET=your-super-secret-key-here-change-in-production
BETTER_AUTH_URL=http://localhost:3000/api/auth
NEXT_PUBLIC_BETTER_AUTH_URL=http://localhost:3000/api/auth

# Database Configuration (for Better Auth)
DATABASE_URL=postgresql://username:password@localhost:5432/task_manager

# OAuth Providers (Optional)
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# Application Configuration
NEXT_PUBLIC_APP_NAME=Todo Evolution
NEXT_PUBLIC_APP_VERSION=1.0.0
NEXT_PUBLIC_SUPPORT_EMAIL=support@todoevolution.com
```

### 3. Database Setup
Ensure your PostgreSQL database is running and accessible:

```bash
# Using Docker for PostgreSQL
docker run --name postgres-todo \
  -e POSTGRES_DB=task_manager \
  -e POSTGRES_USER=todo_user \
  -e POSTGRES_PASSWORD=your_secure_password \
  -p 5432:5432 \
  -d postgres:15

# Or use Neon Serverless PostgreSQL
# Update DATABASE_URL in .env.local with your Neon connection string
```

### 4. Backend Services Setup
Ensure the following services are running:

```bash
# Start FastAPI Backend (from root directory)
cd backend
.\venv\Scripts\Activate.ps1  # Windows
# source venv/bin/activate   # Linux/Mac
python main.py

# Start Redis for Better Auth (from root directory)
docker run --name redis-todo -p 6379:6379 -d redis:7
# or install Redis locally
```

## Development Workflow

### 1. Start Development Server
```bash
# In frontend directory
npm run dev

# Application will be available at:
# http://localhost:3000
```

### 2. Verify Services Running
Open these URLs to verify all services are operational:

```bash
# Frontend Application
http://localhost:3000

# Backend API Health Check
http://localhost:8000/health

# Better Auth Status
http://localhost:3000/api/auth/session

# Redis Connection Test
redis-cli ping  # Should return "PONG"
```

### 3. Initial User Registration
1. Navigate to `http://localhost:3000/signup`
2. Create your first account
3. Verify email (if configured)
4. Sign in to access the dashboard

## Project Structure Overview

```
frontend/
├── src/
│   ├── app/                    # Next.js App Router
│   │   ├── (auth)/            # Authentication routes
│   │   │   ├── signin/
│   │   │   └── signup/
│   │   ├── (dashboard)/       # Protected dashboard routes
│   │   │   ├── layout.tsx
│   │   │   ├── page.tsx
│   │   │   └── tasks/
│   │   ├── api/               # API routes (proxies)
│   │   ├── globals.css        # Global styles
│   │   ├── layout.tsx         # Root layout
│   │   └── page.tsx           # Landing page
│   ├── components/            # React components
│   │   ├── task/              # Task management components
│   │   ├── auth/              # Authentication components
│   │   ├── layout/            # Layout components
│   │   └── ui/                # Reusable UI components
│   ├── lib/                   # Utilities and configurations
│   │   ├── api/               # API client
│   │   ├── auth/              # Better Auth configuration
│   │   └── utils/             # Helper functions
│   ├── hooks/                 # Custom React hooks
│   ├── types/                 # TypeScript type definitions
│   └── styles/                # Additional styles
├── public/                    # Static assets
├── .env.local                 # Environment variables
├── next.config.js             # Next.js configuration
├── tailwind.config.js         # Tailwind CSS configuration
├── tsconfig.json              # TypeScript configuration
└── package.json               # Dependencies and scripts
```

## Key Development Commands

```bash
# Development
npm run dev                 # Start development server
npm run build              # Build for production
npm run start              # Start production server

# Code Quality
npm run lint               # Run ESLint
npm run lint:fix           # Fix ESLint issues
npm run type-check         # Run TypeScript compiler

# Testing
npm run test               # Run tests
npm run test:watch         # Run tests in watch mode
npm run test:coverage      # Run tests with coverage

# Utilities
npm run clean              # Clean build artifacts
npm run analyze            # Analyze bundle size
```

## Core Components Usage

### TaskList Component
```typescript
import TaskList from '@/components/task/TaskList';

function Dashboard() {
  return (
    <div className="container mx-auto p-4">
      <TaskList
        filters={{ status: 'pending' }}
        sortBy="dueDate"
        sortOrder="asc"
      />
    </div>
  );
}
```

### TaskForm Component
```typescript
import TaskForm from '@/components/task/TaskForm';

function CreateTaskModal({ isOpen, onClose }) {
  const handleCreateTask = async (taskData) => {
    // API call to create task
    await createTask(taskData);
    onClose();
  };

  return (
    <TaskForm
      mode="create"
      onSubmit={handleCreateTask}
      onCancel={onClose}
    />
  );
}
```

### Authentication Components
```typescript
import { SignInForm, SignUpForm } from '@/components/auth';

function AuthPage() {
  return (
    <div className="min-h-screen flex items-center justify-center">
      <SignInForm onSuccess={() => router.push('/dashboard')} />
      <SignUpForm onSuccess={() => router.push('/dashboard')} />
    </div>
  );
}
```

## API Client Usage

### Basic API Operations
```typescript
import { apiClient } from '@/lib/api/client';

// Get tasks with filtering
const tasks = await apiClient.getTasks({
  page: 1,
  limit: 20,
  status: 'pending',
  priority: 'high'
});

// Create new task
const newTask = await apiClient.createTask({
  title: 'Complete project documentation',
  description: 'Write comprehensive docs for the new feature',
  priority: 'high',
  dueDate: '2025-12-15T10:00:00Z'
});

// Update task
const updatedTask = await apiClient.updateTask('task-id', {
  status: 'completed',
  actualTime: 120
});

// Delete task
await apiClient.deleteTask('task-id');
```

### Real-time Updates
```typescript
import { useRealtimeTasks } from '@/hooks/useRealtimeTasks';

function TaskDashboard() {
  const { tasks, isConnected, error } = useRealtimeTasks();

  if (error) {
    return <div>Connection error: {error.message}</div>;
  }

  return (
    <div>
      <div className="mb-4">
        Status: {isConnected ? 'Connected' : 'Disconnected'}
      </div>
      <TaskList tasks={tasks} />
    </div>
  );
}
```

## Custom Hooks Usage

### useTasks Hook
```typescript
import { useTasks } from '@/hooks/useTasks';

function TaskManager() {
  const {
    tasks,
    isLoading,
    error,
    createTask,
    updateTask,
    deleteTask,
    refetch
  } = useTasks({
    filters: { status: 'pending' },
    sortBy: 'priority',
    sortOrder: 'desc'
  });

  const handleCompleteTask = async (taskId: string) => {
    await updateTask(taskId, { status: 'completed' });
  };

  if (isLoading) return <div>Loading tasks...</div>;
  if (error) return <div>Error: {error.message}</div>;

  return (
    <div>
      {tasks.map(task => (
        <TaskItem
          key={task.id}
          task={task}
          onComplete={() => handleCompleteTask(task.id)}
        />
      ))}
    </div>
  );
}
```

### useAuth Hook
```typescript
import { useAuth } from '@/hooks/useAuth';

function AuthenticatedApp() {
  const { user, login, logout, isLoading } = useAuth();

  if (isLoading) return <div>Loading...</div>;

  if (!user) {
    return <SignInForm onSignIn={login} />;
  }

  return (
    <div>
      <header>
        Welcome, {user.name}!
        <button onClick={logout}>Sign Out</button>
      </header>
      <Dashboard />
    </div>
  );
}
```

## Styling Guide

### Tailwind CSS Usage
```typescript
// Component with Tailwind classes
export default function TaskCard({ task }) {
  return (
    <div className="bg-white rounded-lg shadow-md p-6 border border-gray-200 hover:shadow-lg transition-shadow">
      <h3 className="text-lg font-semibold text-gray-900 mb-2">
        {task.title}
      </h3>
      <p className="text-gray-600 text-sm mb-4">
        {task.description}
      </p>
      <div className="flex items-center justify-between">
        <span className={`px-2 py-1 text-xs font-medium rounded-full ${
          task.priority === 'high' ? 'bg-red-100 text-red-800' :
          task.priority === 'medium' ? 'bg-yellow-100 text-yellow-800' :
          'bg-green-100 text-green-800'
        }`}>
          {task.priority}
        </span>
        <button className="text-blue-600 hover:text-blue-800 text-sm font-medium">
          Edit
        </button>
      </div>
    </div>
  );
}
```

### Responsive Design
```typescript
// Mobile-first responsive component
export default function ResponsiveTaskList({ tasks }) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {tasks.map(task => (
        <TaskItem
          key={task.id}
          task={task}
          className="w-full" // Ensures proper mobile layout
        />
      ))}
    </div>
  );
}
```

## Testing Guidelines

### Component Testing
```typescript
// __tests__/TaskItem.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import TaskItem from '@/components/task/TaskItem';

const mockTask = {
  id: '1',
  title: 'Test Task',
  status: 'pending',
  priority: 'medium'
};

describe('TaskItem', () => {
  it('renders task title correctly', () => {
    render(<TaskItem task={mockTask} />);
    expect(screen.getByText('Test Task')).toBeInTheDocument();
  });

  it('calls onComplete when complete button clicked', () => {
    const onComplete = jest.fn();
    render(<TaskItem task={mockTask} onComplete={onComplete} />);

    fireEvent.click(screen.getByText('Complete'));
    expect(onComplete).toHaveBeenCalledWith('1');
  });
});
```

### Hook Testing
```typescript
// __tests__/useTasks.test.tsx
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useTasks } from '@/hooks/useTasks';

const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false }
    }
  });

  return ({ children }) => (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );
};

describe('useTasks', () => {
  it('loads tasks successfully', async () => {
    const { result } = renderHook(() => useTasks(), {
      wrapper: createWrapper()
    });

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });
  });
});
```

## Deployment Guide

### Production Build
```bash
# Build for production
npm run build

# Start production server
npm run start
```

### Environment Variables for Production
Create `.env.production.local`:

```env
# Production URLs
NEXT_PUBLIC_APP_URL=https://yourdomain.com
NEXT_PUBLIC_FASTAPI_URL=https://api.yourdomain.com

# Production Auth Configuration
BETTER_AUTH_SECRET=production-super-secret-key
BETTER_AUTH_URL=https://yourdomain.com/api/auth
NEXT_PUBLIC_BETTER_AUTH_URL=https://yourdomain.com/api/auth

# Production Database
DATABASE_URL=postgresql://user:pass@host:5432/prod_db

# Production OAuth
GOOGLE_CLIENT_ID=production-google-client-id
GOOGLE_CLIENT_SECRET=production-google-client-secret
```

### Vercel Deployment
```bash
# Install Vercel CLI
npm install -g vercel

# Deploy to Vercel
vercel --prod

# Set environment variables in Vercel dashboard
# Configure custom domain
# Set up redirects if needed
```

## Troubleshooting

### Common Issues and Solutions

#### 1. Authentication Not Working
```bash
# Check Better Auth configuration
npm run build
# Look for auth-related errors

# Verify environment variables
echo $BETTER_AUTH_SECRET
echo $DATABASE_URL

# Check Redis connection
redis-cli ping
```

#### 2. API Connection Issues
```bash
# Verify backend is running
curl http://localhost:8000/health

# Check CORS configuration
curl -H "Origin: http://localhost:3000" \
     -H "Access-Control-Request-Method: GET" \
     -H "Access-Control-Request-Headers: X-Requested-With" \
     -X OPTIONS http://localhost:8000/api/tasks
```

#### 3. Build Errors
```bash
# Clear Next.js cache
rm -rf .next

# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install

# Check TypeScript compilation
npm run type-check
```

#### 4. Performance Issues
```bash
# Analyze bundle size
npm run analyze

# Check for memory leaks in dev tools
# Monitor network requests in browser dev tools
```

## Development Best Practices

### 1. Code Organization
- Keep components focused and single-purpose
- Use custom hooks for shared logic
- Maintain consistent file naming conventions
- Separate business logic from presentation

### 2. State Management
- Use React Query for server state
- Use local state for UI-only state
- Implement proper error boundaries
- Optimize re-renders with memoization

### 3. Performance Optimization
- Implement code splitting for large components
- Use dynamic imports for non-critical features
- Optimize images and assets
- Implement virtual scrolling for large lists

### 4. Accessibility
- Use semantic HTML elements
- Implement proper ARIA labels
- Ensure keyboard navigation
- Test with screen readers

### 5. Security
- Validate all user inputs
- Use HTTPS in production
- Implement proper authentication
- Sanitize user-generated content

## Resources and Documentation

### Official Documentation
- [Next.js 16 Documentation](https://nextjs.org/docs)
- [React 18 Documentation](https://react.dev)
- [Better Auth Documentation](https://better-auth.com/docs)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [React Query Documentation](https://tanstack.com/query/latest)

### Community Resources
- [Next.js GitHub Repository](https://github.com/vercel/next.js)
- [React Discord Community](https://discord.gg/react)
- [Stack Overflow Tag: next.js](https://stackoverflow.com/questions/tagged/next.js)

This quickstart guide provides everything needed to get started with the frontend task management UI, from initial setup to deployment and troubleshooting.