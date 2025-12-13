/**
 * Core task entity representing a single todo item
 */
export interface Task {
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

/**
 * Enumeration of possible task statuses
 */
export type TaskStatus =
  | 'pending'      // Task created but not started
  | 'in_progress'  // Task actively being worked on
  | 'completed'    // Task finished successfully
  | 'cancelled'    // Task cancelled before completion
  | 'blocked';     // Task blocked by dependencies

/**
 * Enumeration of task priority levels
 */
export type TaskPriority =
  | 'low'      // Low priority tasks
  | 'medium'   // Default priority level
  | 'high'     // High priority tasks
  | 'urgent';  // Time-sensitive critical tasks

/**
 * User profile information
 */
export interface User {
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

/**
 * User-specific application preferences
 */
export interface UserPreferences {
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

/**
 * Data transfer object for creating new tasks
 */
export interface CreateTaskDTO {
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

/**
 * Data transfer object for updating existing tasks
 */
export interface UpdateTaskDTO {
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

/**
 * Query parameters for task listing and filtering
 */
export interface TaskQueryParams {
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

/**
 * Available fields for task sorting
 */
export type TaskSortField =
  | 'title'
  | 'status'
  | 'priority'
  | 'dueDate'
  | 'createdAt'
  | 'updatedAt'
  | 'completedAt';

/**
 * Standard API response wrapper
 */
export interface ApiResponse<T> {
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

/**
 * Paginated API response for list endpoints
 */
export interface PaginatedResponse<T> extends ApiResponse<T[]> {
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

/**
 * Task statistics aggregation response
 */
export interface TaskStatsResponse {
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

/**
 * Form state for task creation/editing
 */
export interface TaskFormState {
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

/**
 * Validation error messages for task form
 */
export interface TaskFormErrors {
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

/**
 * Search form state
 */
export interface SearchFormState {
  /** Search query */
  query: string;

  /** Active filters */
  filters: TaskFilters;

  /** Sort configuration */
  sort: SortConfiguration;

  /** View mode */
  viewMode: 'list' | 'grid' | 'kanban';
}

/**
 * Active task filters configuration
 */
export interface TaskFilters {
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

/**
 * Sort configuration for task lists
 */
export interface SortConfiguration {
  /** Field to sort by */
  field: TaskSortField;

  /** Sort direction */
  direction: 'asc' | 'desc';
}

/**
 * Global application state structure
 */
export interface AppState {
  /** Authentication state */
  auth: AuthState;

  /** Tasks state */
  tasks: TasksState;

  /** UI state */
  ui: UIState;

  /** User preferences */
  preferences: UserPreferences;
}

/**
 * Authentication state management
 */
export interface AuthState {
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

/**
 * Tasks management state
 */
export interface TasksState {
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

/**
 * UI-specific state management
 */
export interface UIState {
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

/**
 * Notification system state
 */
export interface Notification {
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

/**
 * Return type for useTasks hook
 */
export interface UseTasksReturn {
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

/**
 * Return type for useAuth hook
 */
export interface UseAuthReturn {
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