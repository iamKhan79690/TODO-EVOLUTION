# Data Model: Frontend Task Management UI

**Feature**: Frontend Task Management UI
**Version**: 1.0
**Created**: 2025-12-07
**Status**: Final

## Overview

This document defines the comprehensive data model for the frontend task management interface, including all TypeScript interfaces, API contracts, and state management structures required for implementing a modern, type-safe task management application.

## Core Data Types

### Task Entity
```typescript
/**
 * Core task entity representing a single todo item
 */
interface Task {
  /** Unique identifier for the task */
  id: string;

  /** Task title - required field */
  title: string;

  /** Detailed task description */
  description?: string;

  /** Current task status */
  status: TaskStatus;

  /** Task priority level */
  priority: TaskPriority;

  /** Optional due date for task completion */
  dueDate?: Date;

  /** Task creation timestamp */
  createdAt: Date;

  /** Last modification timestamp */
  updatedAt: Date;

  /** Task completion timestamp */
  completedAt?: Date;

  /** User-assigned tags for categorization */
  tags?: string[];

  /** Task assignee for collaborative features */
  assignedTo?: string;

  /** Estimated completion time in minutes */
  estimatedTime?: number;

  /** Actual time spent in minutes */
  actualTime?: number;
}
```

### Task Status Enumeration
```typescript
/**
 * Enumeration of possible task statuses
 */
type TaskStatus =
  | 'pending'      // Task created but not started
  | 'in_progress'  // Task actively being worked on
  | 'completed'    // Task finished successfully
  | 'cancelled'    // Task cancelled before completion
  | 'blocked';     // Task blocked by dependencies
```

### Task Priority Enumeration
```typescript
/**
 * Enumeration of task priority levels
 */
type TaskPriority =
  | 'low'      // Low priority tasks
  | 'medium'   // Default priority level
  | 'high'     // High priority tasks
  | 'urgent';  // Time-sensitive critical tasks
```

### User Entity
```typescript
/**
 * User profile information
 */
interface User {
  /** Unique user identifier */
  id: string;

  /** User email address */
  email: string;

  /** User display name */
  name: string;

  /** User avatar URL */
  avatar?: string;

  /** Account creation timestamp */
  createdAt: Date;

  /** Last login timestamp */
  lastLogin?: Date;

  /** User preferences and settings */
  preferences: UserPreferences;
}
```

### User Preferences
```typescript
/**
 * User-specific application preferences
 */
interface UserPreferences {
  /** Theme preference */
  theme: 'light' | 'dark' | 'system';

  /** Default task priority */
  defaultPriority: TaskPriority;

  /** Email notification settings */
  emailNotifications: {
    taskAssigned: boolean;
    taskCompleted: boolean;
    taskDue: boolean;
    taskOverdue: boolean;
  };

  /** UI display preferences */
  display: {
    itemsPerPage: number;
    defaultSort: TaskSortField;
    defaultView: 'list' | 'grid' | 'kanban';
    showCompleted: boolean;
  };

  /** Time zone for date calculations */
  timezone: string;
}
```

## API Data Transfer Objects

### Task Creation DTO
```typescript
/**
 * Data transfer object for creating new tasks
 */
interface CreateTaskDTO {
  /** Task title - required */
  title: string;

  /** Optional task description */
  description?: string;

  /** Initial task priority */
  priority?: TaskPriority;

  /** Optional due date */
  dueDate?: string; // ISO string format

  /** Optional task tags */
  tags?: string[];

  /** Optional assignee */
  assignedTo?: string;

  /** Optional estimated time */
  estimatedTime?: number;
}
```

### Task Update DTO
```typescript
/**
 * Data transfer object for updating existing tasks
 */
interface UpdateTaskDTO {
  /** Updated task title */
  title?: string;

  /** Updated task description */
  description?: string;

  /** Updated task status */
  status?: TaskStatus;

  /** Updated task priority */
  priority?: TaskPriority;

  /** Updated due date */
  dueDate?: string; // ISO string format

  /** Updated task tags */
  tags?: string[];

  /** Updated assignee */
  assignedTo?: string;

  /** Updated estimated time */
  estimatedTime?: number;

  /** Updated actual time */
  actualTime?: number;
}
```

### Task Query Parameters
```typescript
/**
 * Query parameters for task listing and filtering
 */
interface TaskQueryParams {
  /** Pagination page number */
  page?: number;

  /** Number of items per page */
  limit?: number;

  /** Search term for title/description */
  search?: string;

  /** Status filter */
  status?: TaskStatus;

  /** Priority filter */
  priority?: TaskPriority;

  /** Assignee filter */
  assignedTo?: string;

  /** Tag filter */
  tag?: string;

  /** Due date range filter */
  dueDate?: {
    from?: string; // ISO string
    to?: string;   // ISO string
  };

  /** Sort field */
  sortBy?: TaskSortField;

  /** Sort direction */
  sortOrder?: 'asc' | 'desc';
}
```

### Sort Field Enumeration
```typescript
/**
 * Available fields for task sorting
 */
type TaskSortField =
  | 'title'
  | 'status'
  | 'priority'
  | 'dueDate'
  | 'createdAt'
  | 'updatedAt'
  | 'completedAt';
```

## API Response Types

### Standard API Response
```typescript
/**
 * Standard API response wrapper
 */
interface ApiResponse<T> {
  /** Response data payload */
  data: T;

  /** Success status indicator */
  success: boolean;

  /** Response message */
  message: string;

  /** Optional error details */
  errors?: string[];

  /** Response metadata */
  meta?: {
    timestamp: string;
    requestId: string;
  };
}
```

### Paginated Response
```typescript
/**
 * Paginated API response for list endpoints
 */
interface PaginatedResponse<T> extends ApiResponse<T[]> {
  /** Pagination metadata */
  pagination: {
    currentPage: number;
    totalPages: number;
    totalItems: number;
    itemsPerPage: number;
    hasNextPage: boolean;
    hasPreviousPage: boolean;
  };
}
```

### Task Statistics Response
```typescript
/**
 * Task statistics aggregation response
 */
interface TaskStatsResponse {
  /** Total number of tasks */
  totalTasks: number;

  /** Tasks by status */
  tasksByStatus: {
    pending: number;
    inProgress: number;
    completed: number;
    cancelled: number;
    blocked: number;
  };

  /** Tasks by priority */
  tasksByPriority: {
    low: number;
    medium: number;
    high: number;
    urgent: number;
  };

  /** Overdue tasks count */
  overdueTasks: number;

  /** Tasks due today */
  dueToday: number;

  /** Tasks due this week */
  dueThisWeek: number;

  /** Average completion time */
  avgCompletionTime: number; // in hours

  /** Productivity metrics */
  productivity: {
    tasksCompletedToday: number;
    tasksCompletedThisWeek: number;
    completionRate: number; // percentage
  };
}
```

## Form Data Types

### Task Form State
```typescript
/**
 * Form state for task creation/editing
 */
interface TaskFormState {
  /** Current form data */
  data: CreateTaskDTO | UpdateTaskDTO;

  /** Form validation errors */
  errors: TaskFormErrors;

  /** Form submission state */
  isSubmitting: boolean;

  /** Form dirty state (has unsaved changes) */
  isDirty: boolean;

  /** Form validity state */
  isValid: boolean;
}
```

### Form Validation Errors
```typescript
/**
 * Validation error messages for task form
 */
interface TaskFormErrors {
  /** Title field error */
  title?: string;

  /** Description field error */
  description?: string;

  /** Due date field error */
  dueDate?: string;

  /** Estimated time field error */
  estimatedTime?: string;

  /** General form errors */
  general?: string[];
}
```

### Search Form State
```typescript
/**
 * Form state for task search and filtering
 */
interface SearchFormState {
  /** Search query */
  query: string;

  /** Active filters */
  filters: TaskFilters;

  /** Sort configuration */
  sort: SortConfiguration;

  /** View mode */
  viewMode: 'list' | 'grid' | 'kanban';
}
```

### Task Filters
```typescript
/**
 * Active task filters configuration
 */
interface TaskFilters {
  /** Status filter */
  status?: TaskStatus;

  /** Priority filter */
  priority?: TaskPriority;

  /** Assignee filter */
  assignee?: string;

  /** Tag filter */
  tags?: string[];

  /** Due date range filter */
  dueDateRange?: {
    from: Date;
    to: Date;
  };

  /** Created date range filter */
  createdDateRange?: {
    from: Date;
    to: Date;
  };
}
```

### Sort Configuration
```typescript
/**
 * Sort configuration for task lists
 */
interface SortConfiguration {
  /** Field to sort by */
  field: TaskSortField;

  /** Sort direction */
  direction: 'asc' | 'desc';
}
```

## State Management Types

### Global Application State
```typescript
/**
 * Global application state structure
 */
interface AppState {
  /** Authentication state */
  auth: AuthState;

  /** Tasks state */
  tasks: TasksState;

  /** UI state */
  ui: UIState;

  /** User preferences */
  preferences: UserPreferences;
}
```

### Authentication State
```typescript
/**
 * Authentication state management
 */
interface AuthState {
  /** Current authenticated user */
  user: User | null;

  /** Authentication status */
  status: 'idle' | 'loading' | 'authenticated' | 'unauthenticated' | 'error';

  /** Authentication error message */
  error: string | null;

  /** Session expiration timestamp */
  expiresAt?: number;

  /** JWT access token */
  accessToken?: string;

  /** JWT refresh token */
  refreshToken?: string;
}
```

### Tasks State
```typescript
/**
 * Tasks management state
 */
interface TasksState {
  /** Current list of tasks */
  tasks: Task[];

  /** Loading state */
  isLoading: boolean;

  /** Error state */
  error: string | null;

  /** Current filters */
  filters: TaskFilters;

  /** Current sort configuration */
  sort: SortConfiguration;

  /** Pagination state */
  pagination: {
    currentPage: number;
    totalPages: number;
    totalItems: number;
    hasMore: boolean;
  };

  /** Selected task IDs */
  selectedTasks: string[];

  /** Search query */
  searchQuery: string;

  /** View mode */
  viewMode: 'list' | 'grid' | 'kanban';

  /** Last update timestamp */
  lastUpdated: number;
}
```

### UI State
```typescript
/**
 * UI-specific state management
 */
interface UIState {
  /** Theme configuration */
  theme: 'light' | 'dark' | 'system';

  /** Sidebar state */
  sidebar: {
    isOpen: boolean;
    isCollapsed: boolean;
  };

  /** Modal states */
  modals: {
    taskForm: boolean;
    deleteConfirm: boolean;
    filters: boolean;
    settings: boolean;
  };

  /** Loading states */
  loading: {
    tasks: boolean;
    createTask: boolean;
    updateTask: boolean;
    deleteTask: boolean;
  };

  /** Notification state */
  notifications: Notification[];

  /** Screen size breakpoint */
  screenSize: 'mobile' | 'tablet' | 'desktop';
}
```

### Notification State
```typescript
/**
 * Notification system state
 */
interface Notification {
  /** Unique notification identifier */
  id: string;

  /** Notification type */
  type: 'success' | 'error' | 'warning' | 'info';

  /** Notification message */
  message: string;

  /** Optional notification title */
  title?: string;

  /** Auto-dismiss timeout in milliseconds */
  timeout?: number;

  /** Creation timestamp */
  createdAt: Date;

  /** Whether notification is visible */
  isVisible: boolean;
}
```

## Hook Return Types

### Tasks Hook Return Type
```typescript
/**
 * Return type for useTasks hook
 */
interface UseTasksReturn {
  /** Current tasks list */
  tasks: Task[];

  /** Loading state */
  isLoading: boolean;

  /** Error state */
  error: string | null;

  /** Refetch function */
  refetch: () => Promise<void>;

  /** Create task function */
  createTask: (data: CreateTaskDTO) => Promise<void>;

  /** Update task function */
  updateTask: (id: string, data: UpdateTaskDTO) => Promise<void>;

  /** Delete task function */
  deleteTask: (id: string) => Promise<void>;

  /** Bulk update function */
  bulkUpdate: (ids: string[], data: UpdateTaskDTO) => Promise<void>;

  /** Bulk delete function */
  bulkDelete: (ids: string[]) => Promise<void>;
}
```

### Authentication Hook Return Type
```typescript
/**
 * Return type for useAuth hook
 */
interface UseAuthReturn {
  /** Current user */
  user: User | null;

  /** Authentication status */
  status: AuthState['status'];

  /** Login function */
  login: (email: string, password: string) => Promise<void>;

  /** Register function */
  register: (email: string, password: string, name: string) => Promise<void>;

  /** Logout function */
  logout: () => Promise<void>;

  /** Refresh token function */
  refreshToken: () => Promise<void>;

  /** Update user profile */
  updateProfile: (data: Partial<User>) => Promise<void>;
}
```

## Configuration Types

### Application Configuration
```typescript
/**
 * Application configuration object
 */
interface AppConfig {
  /** API base URL */
  apiBaseUrl: string;

  /** WebSocket URL for real-time updates */
  wsUrl: string;

  /** Application version */
  version: string;

  /** Feature flags */
  features: {
    realTimeUpdates: boolean;
    collaborativeTasks: boolean;
    fileAttachments: boolean;
    advancedReporting: boolean;
  };

  /** Performance configuration */
  performance: {
    maxTasksPerPage: number;
    debounceTime: number; // for search
    refreshInterval: number; // for real-time updates
  };

  ** UI configuration */
  ui: {
    defaultTheme: 'light' | 'dark' | 'system';
    defaultPageSize: number;
    maxUploadSize: number; // in bytes
  };
}
```

## Validation Schemas

### Task Validation Schema (Zod)
```typescript
import { z } from 'zod';

/**
 * Zod schema for task validation
 */
export const taskSchema = z.object({
  title: z.string()
    .min(1, 'Title is required')
    .max(200, 'Title must be less than 200 characters'),

  description: z.string()
    .optional()
    .max(2000, 'Description must be less than 2000 characters'),

  priority: z.enum(['low', 'medium', 'high', 'urgent'])
    .default('medium'),

  dueDate: z.string()
    .optional()
    .refine((date) => !date || !isNaN(Date.parse(date)), {
      message: 'Invalid due date format',
    }),

  tags: z.array(z.string())
    .optional(),

  assignedTo: z.string()
    .optional(),

  estimatedTime: z.number()
    .min(0, 'Estimated time must be positive')
    .optional(),
});

/**
 * Type inference from task schema
 */
export type TaskFormData = z.infer<typeof taskSchema>;
```

## Integration Points

### Backend Integration
```typescript
/**
 * Backend API client interface
 */
interface TaskAPIClient {
  /** Fetch tasks with pagination and filtering */
  getTasks(params?: TaskQueryParams): Promise<PaginatedResponse<Task>>;

  /** Fetch single task by ID */
  getTask(id: string): Promise<ApiResponse<Task>>;

  /** Create new task */
  createTask(data: CreateTaskDTO): Promise<ApiResponse<Task>>;

  /** Update existing task */
  updateTask(id: string, data: UpdateTaskDTO): Promise<ApiResponse<Task>>;

  /** Delete task */
  deleteTask(id: string): Promise<ApiResponse<void>>;

  /** Bulk operations */
  bulkUpdate(ids: string[], data: UpdateTaskDTO): Promise<ApiResponse<Task[]>>;
  bulkDelete(ids: string[]): Promise<ApiResponse<void>>;

  /** Task statistics */
  getStats(): Promise<ApiResponse<TaskStatsResponse>>;
}
```

### Storage Integration
```typescript
/**
 * Local storage interface for caching and offline support
 */
interface TaskStorage {
  /** Cache tasks locally */
  cacheTasks(tasks: Task[]): Promise<void>;

  /** Retrieve cached tasks */
  getCachedTasks(): Promise<Task[] | null>;

  /** Clear task cache */
  clearCache(): Promise<void>;

  /** Store user preferences */
  storePreferences(preferences: UserPreferences): Promise<void>;

  /** Retrieve user preferences */
  getPreferences(): Promise<UserPreferences | null>;
}
```

This comprehensive data model provides the foundation for implementing a type-safe, scalable, and maintainable task management frontend application with full CRUD operations, real-time updates, and robust state management.