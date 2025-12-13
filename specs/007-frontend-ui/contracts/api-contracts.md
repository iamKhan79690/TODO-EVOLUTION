# API Contracts: Frontend Task Management UI

**Feature**: Frontend Task Management UI
**Version**: 1.0
**Created**: 2025-12-07
**Status**: Final

## API Contract Overview

This document defines the complete API contracts between the frontend React application and the FastAPI backend. All contracts include request/response formats, error handling, authentication requirements, and validation rules.

## Authentication Contracts

### Authentication Headers
```
Authorization: Bearer <jwt_token>
Content-Type: application/json
X-Request-ID: <unique_request_identifier>
```

### Sign In Contract
```typescript
// Request
interface SignInRequest {
  email: string;
  password: string;
  rememberMe?: boolean;
}

// Response
interface SignInResponse {
  success: boolean;
  message: string;
  data: {
    user: {
      id: string;
      email: string;
      name: string;
      avatar?: string;
    };
    accessToken: string;
    refreshToken: string;
    expiresIn: number;
  };
}

// Error Response
interface SignInError {
  success: false;
  message: string;
  errors: {
    email?: string;
    password?: string;
    general?: string;
  };
}
```

### Sign Up Contract
```typescript
// Request
interface SignUpRequest {
  email: string;
  password: string;
  name: string;
  confirmPassword: string;
}

// Response
interface SignUpResponse {
  success: boolean;
  message: string;
  data: {
    user: {
      id: string;
      email: string;
      name: string;
    };
    accessToken: string;
    refreshToken: string;
    expiresIn: number;
  };
}
```

### Token Refresh Contract
```typescript
// Request
interface RefreshTokenRequest {
  refreshToken: string;
}

// Response
interface RefreshTokenResponse {
  success: boolean;
  message: string;
  data: {
    accessToken: string;
    refreshToken: string;
    expiresIn: number;
  };
}
```

## Task Management Contracts

### Get Tasks Contract
```typescript
// Endpoint: GET /api/tasks
// Query Parameters
interface GetTasksQuery {
  page?: number;        // Default: 1
  limit?: number;       // Default: 20, Max: 100
  search?: string;      // Search in title and description
  status?: TaskStatus;
  priority?: TaskPriority;
  assignedTo?: string;
  tag?: string;
  dueDateFrom?: string; // ISO date string
  dueDateTo?: string;   // ISO date string
  sortBy?: TaskSortField;
  sortOrder?: 'asc' | 'desc';
}

// Response
interface GetTasksResponse {
  success: boolean;
  message: string;
  data: Task[];
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

### Create Task Contract
```typescript
// Endpoint: POST /api/tasks
// Request
interface CreateTaskRequest {
  title: string;             // Required, min: 1, max: 200
  description?: string;      // Optional, max: 2000
  priority?: TaskPriority;   // Default: 'medium'
  dueDate?: string;          // ISO date string
  tags?: string[];           // Array of tag strings
  assignedTo?: string;       // User ID
  estimatedTime?: number;    // Minutes
}

// Response
interface CreateTaskResponse {
  success: boolean;
  message: string;
  data: Task;
}

// Error Response
interface CreateTaskError {
  success: false;
  message: string;
  errors: {
    title?: string;
    description?: string;
    dueDate?: string;
    estimatedTime?: string;
    general?: string[];
  };
}
```

### Update Task Contract
```typescript
// Endpoint: PATCH /api/tasks/{taskId}
// Request
interface UpdateTaskRequest {
  title?: string;
  description?: string;
  status?: TaskStatus;
  priority?: TaskPriority;
  dueDate?: string;
  tags?: string[];
  assignedTo?: string;
  estimatedTime?: number;
  actualTime?: number;
}

// Response
interface UpdateTaskResponse {
  success: boolean;
  message: string;
  data: Task;
}

// Error Response
interface UpdateTaskError {
  success: false;
  message: string;
  errors: {
    title?: string;
    description?: string;
    dueDate?: string;
    status?: string;
    actualTime?: string;
    general?: string[];
  };
}
```

### Delete Task Contract
```typescript
// Endpoint: DELETE /api/tasks/{taskId}
// Response
interface DeleteTaskResponse {
  success: boolean;
  message: string;
  data: null;
}

// Error Response
interface DeleteTaskError {
  success: false;
  message: string;
  errors: {
    taskId?: string;
    general?: string[];
  };
}
```

### Bulk Operations Contract
```typescript
// Endpoint: PATCH /api/tasks/bulk
// Request
interface BulkUpdateRequest {
  taskIds: string[];           // Array of task IDs
  updates: UpdateTaskRequest;  // Updates to apply to all tasks
}

// Response
interface BulkUpdateResponse {
  success: boolean;
  message: string;
  data: {
    updatedTasks: Task[];
    failedUpdates: Array<{
      taskId: string;
      error: string;
    }>;
  };
}

// Endpoint: DELETE /api/tasks/bulk
// Request
interface BulkDeleteRequest {
  taskIds: string[];
}

// Response
interface BulkDeleteResponse {
  success: boolean;
  message: string;
  data: {
    deletedTaskIds: string[];
    failedDeletes: Array<{
      taskId: string;
      error: string;
    }>;
  };
}
```

## Task Statistics Contracts

### Get Task Statistics Contract
```typescript
// Endpoint: GET /api/tasks/stats
// Query Parameters
interface GetStatsQuery {
  dateRange?: {
    from: string;  // ISO date string
    to: string;    // ISO date string
  };
  userId?: string; // For admin/manager views
}

// Response
interface GetStatsResponse {
  success: boolean;
  message: string;
  data: {
    totalTasks: number;
    tasksByStatus: {
      pending: number;
      inProgress: number;
      completed: number;
      cancelled: number;
      blocked: number;
    };
    tasksByPriority: {
      low: number;
      medium: number;
      high: number;
      urgent: number;
    };
    overdueTasks: number;
    dueToday: number;
    dueThisWeek: number;
    avgCompletionTime: number;
    productivity: {
      tasksCompletedToday: number;
      tasksCompletedThisWeek: number;
      completionRate: number;
    };
    trends: {
      daily: Array<{
        date: string;        // ISO date string
        completed: number;
        created: number;
      }>;
      weekly: Array<{
        week: string;        // Week identifier
        completed: number;
        created: number;
      }>;
    };
  };
}
```

## User Profile Contracts

### Get User Profile Contract
```typescript
// Endpoint: GET /api/users/profile
// Response
interface GetUserProfileResponse {
  success: boolean;
  message: string;
  data: {
    user: {
      id: string;
      email: string;
      name: string;
      avatar?: string;
      createdAt: string;
      lastLogin?: string;
    };
    preferences: UserPreferences;
  };
}
```

### Update User Profile Contract
```typescript
// Endpoint: PATCH /api/users/profile
// Request
interface UpdateUserProfileRequest {
  name?: string;
  avatar?: string;
  preferences?: Partial<UserPreferences>;
}

// Response
interface UpdateUserProfileResponse {
  success: boolean;
  message: string;
  data: {
    user: User;
    preferences: UserPreferences;
  };
}
```

### Change Password Contract
```typescript
// Endpoint: POST /api/users/change-password
// Request
interface ChangePasswordRequest {
  currentPassword: string;
  newPassword: string;
  confirmPassword: string;
}

// Response
interface ChangePasswordResponse {
  success: boolean;
  message: string;
  data: null;
}

// Error Response
interface ChangePasswordError {
  success: false;
  message: string;
  errors: {
    currentPassword?: string;
    newPassword?: string;
    confirmPassword?: string;
    general?: string;
  };
}
```

## File Upload Contracts

### Upload Task Attachment Contract
```typescript
// Endpoint: POST /api/tasks/{taskId}/attachments
// Request: multipart/form-data
interface UploadAttachmentRequest {
  file: File;                 // File to upload
  description?: string;       // Optional file description
}

// Response
interface UploadAttachmentResponse {
  success: boolean;
  message: string;
  data: {
    attachment: {
      id: string;
      filename: string;
      originalName: string;
      size: number;
      mimeType: string;
      url: string;
      uploadedAt: string;
    };
  };
}

// Error Response
interface UploadAttachmentError {
  success: false;
  message: string;
  errors: {
    file?: string;
    description?: string;
    general?: string;
  };
}
```

### Delete Task Attachment Contract
```typescript
// Endpoint: DELETE /api/tasks/{taskId}/attachments/{attachmentId}
// Response
interface DeleteAttachmentResponse {
  success: boolean;
  message: string;
  data: null;
}
```

## Search and Filtering Contracts

### Advanced Search Contract
```typescript
// Endpoint: POST /api/tasks/search
// Request
interface AdvancedSearchRequest {
  query: {
    text?: string;            // Full-text search
    filters: {
      status?: TaskStatus[];
      priority?: TaskPriority[];
      assignedTo?: string[];
      tags?: string[];
      dateRange?: {
        field: 'createdAt' | 'updatedAt' | 'dueDate' | 'completedAt';
        from: string;
        to: string;
      };
    };
  };
  sort: Array<{
    field: TaskSortField;
    direction: 'asc' | 'desc';
  }>;
  pagination: {
    page: number;
    limit: number;
  };
}

// Response
interface AdvancedSearchResponse {
  success: boolean;
  message: string;
  data: {
    tasks: Task[];
    pagination: {
      currentPage: number;
      totalPages: number;
      totalItems: number;
      itemsPerPage: number;
      hasNextPage: boolean;
      hasPreviousPage: boolean;
    };
    facets: {
      statuses: Array<{
        status: TaskStatus;
        count: number;
      }>;
      priorities: Array<{
        priority: TaskPriority;
        count: number;
      }>;
      tags: Array<{
        tag: string;
        count: number;
      }>;
      assignees: Array<{
        userId: string;
        name: string;
        count: number;
      }>;
    };
  };
}
```

## Real-time Updates Contracts

### WebSocket Message Contracts
```typescript
// WebSocket Connection URL
const WS_URL = 'ws://localhost:8000/ws/tasks';

// Authentication Message
interface WSAuthMessage {
  type: 'auth';
  token: string;
}

// Task Update Messages
interface WSTaskCreatedMessage {
  type: 'task_created';
  data: Task;
  userId: string;
}

interface WSTaskUpdatedMessage {
  type: 'task_updated';
  data: Task;
  userId: string;
  changes: Partial<Task>;
}

interface WSTaskDeletedMessage {
  type: 'task_deleted';
  data: {
    taskId: string;
    userId: string;
  };
}

// Connection Status Messages
interface WSConnectedMessage {
  type: 'connected';
  data: {
    userId: string;
    timestamp: string;
  };
}

interface WSDisconnectedMessage {
  type: 'disconnected';
  data: {
    reason: string;
    timestamp: string;
  };
}

interface WSErrorMessage {
  type: 'error';
  data: {
    code: string;
    message: string;
    timestamp: string;
  };
}
```

## Error Handling Contracts

### Standard Error Response
```typescript
interface StandardErrorResponse {
  success: false;
  message: string;
  errors: {
    [field: string]: string | string[];
  };
  meta: {
    timestamp: string;
    requestId: string;
    path: string;
    method: string;
  };
}
```

### HTTP Status Code Mapping
```
200: Success
201: Created
204: No Content
400: Bad Request
401: Unauthorized
403: Forbidden
404: Not Found
409: Conflict
422: Validation Error
429: Rate Limited
500: Internal Server Error
502: Bad Gateway
503: Service Unavailable
504: Gateway Timeout
```

### Error Code Definitions
```typescript
// Validation Errors
VALIDATION_ERROR = 'VALIDATION_ERROR'
REQUIRED_FIELD_MISSING = 'REQUIRED_FIELD_MISSING'
INVALID_FORMAT = 'INVALID_FORMAT'
INVALID_VALUE = 'INVALID_VALUE'

// Authentication Errors
UNAUTHORIZED = 'UNAUTHORIZED'
INVALID_CREDENTIALS = 'INVALID_CREDENTIALS'
TOKEN_EXPIRED = 'TOKEN_EXPIRED'
TOKEN_INVALID = 'TOKEN_INVALID'

// Authorization Errors
FORBIDDEN = 'FORBIDDEN'
INSUFFICIENT_PERMISSIONS = 'INSUFFICIENT_PERMISSIONS'

// Resource Errors
NOT_FOUND = 'NOT_FOUND'
ALREADY_EXISTS = 'ALREADY_EXISTS'
RESOURCE_LOCKED = 'RESOURCE_LOCKED'

// System Errors
INTERNAL_SERVER_ERROR = 'INTERNAL_SERVER_ERROR'
DATABASE_ERROR = 'DATABASE_ERROR'
EXTERNAL_SERVICE_ERROR = 'EXTERNAL_SERVICE_ERROR'
RATE_LIMIT_EXCEEDED = 'RATE_LIMIT_EXCEEDED'

// Business Logic Errors
TASK_NOT_DELETABLE = 'TASK_NOT_DELETABLE'
INVALID_STATUS_TRANSITION = 'INVALID_STATUS_TRANSITION'
ASSIGNMENT_NOT_ALLOWED = 'ASSIGNMENT_NOT_ALLOWED'
```

## Rate Limiting Contracts

### Rate Limit Headers
```typescript
interface RateLimitHeaders {
  'X-RateLimit-Limit': string;      // Requests allowed per window
  'X-RateLimit-Remaining': string;  // Requests remaining in window
  'X-RateLimit-Reset': string;      // Unix timestamp when window resets
  'Retry-After': string;            // Seconds to wait before retrying
}
```

### Rate Limit Response
```typescript
interface RateLimitResponse {
  success: false;
  message: string;
  errors: {
    general: string;
  };
  meta: {
    limit: number;
    remaining: number;
    resetAt: number;
    retryAfter: number;
  };
}
```

## Pagination Contracts

### Standard Pagination Format
```typescript
interface PaginationMeta {
  currentPage: number;      // 1-based page number
  totalPages: number;       // Total number of pages
  totalItems: number;       // Total number of items
  itemsPerPage: number;     // Items per page
  hasNextPage: boolean;     // Whether next page exists
  hasPreviousPage: boolean; // Whether previous page exists
}
```

### Pagination Query Parameters
```typescript
interface PaginationQuery {
  page?: number;     // Default: 1, Min: 1
  limit?: number;    // Default: 20, Min: 1, Max: 100
  offset?: number;   // Alternative to page, 0-based
}
```

## Caching Contracts

### Cache Control Headers
```typescript
interface CacheControlHeaders {
  'Cache-Control': string;       // Cache directives
  'ETag': string;               // Entity tag for validation
  'Last-Modified': string;      // Last modification timestamp
  'X-Cache-Status': string;     // Cache hit/miss status
}
```

### Conditional Request Headers
```typescript
interface ConditionalRequestHeaders {
  'If-None-Match': string;       // ETag validation
  'If-Modified-Since': string;   // Timestamp validation
}
```

## Internationalization Contracts

### Language Negotiation
```typescript
// Accept-Language Header
Accept-Language: 'en-US,en;q=0.9,es;q=0.8'

// Response Language Header
Content-Language: 'en-US'

// Localized Response Structure
interface LocalizedResponse<T> {
  success: boolean;
  message: string;
  data: T;
  localization: {
    language: string;
    region: string;
    currency?: string;
    timezone: string;
  };
}
```

These API contracts provide a comprehensive foundation for implementing robust type-safe communication between the React frontend and FastAPI backend, ensuring consistency, reliability, and maintainability across the entire application.