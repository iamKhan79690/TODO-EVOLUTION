/**
 * TypeScript type definitions for the Todo Evolution application
 */

// =============================================================================
// User Types
// =============================================================================

export interface User {
  id: number;
  email: string;
  name: string;
  createdAt: string;
  updatedAt: string;
}

export interface UserCreate {
  email: string;
  name: string;
  password: string;
  confirmPassword?: string;
}

export interface UserUpdate {
  name?: string;
  email?: string;
}

// =============================================================================
// Authentication Types
// =============================================================================

export interface AuthToken {
  accessToken: string;
  refreshToken: string;
  tokenType: string;
  expiresIn: number;
}

export interface AuthResponse {
  user: User;
  token: AuthToken;
  message: string;
}

export interface SignInRequest {
  email: string;
  password: string;
}

export interface SignUpRequest {
  email: string;
  password: string;
  confirmPassword: string;
  name: string;
}

export interface SignOutRequest {
  refreshToken: string;
}

export interface RefreshTokenRequest {
  refresh_token: string;
}

export interface AuthError {
  error: string;
  message: string;
  details?: Record<string, any>;
}

// =============================================================================
// Session Types
// =============================================================================

export interface Session {
  user: User;
  accessToken: string;
  refreshToken: string;
  expiresAt: Date;
  createdAt: Date;
}

export interface SessionInfo {
  sessionId: string;
  createdAt: string;
  lastAccessed: string;
  expiresAt: string;
  ipAddress?: string;
  userAgent?: string;
  isActive: boolean;
}

// =============================================================================
// Form Validation Types
// =============================================================================

export interface FormFieldError {
  field: string;
  message: string;
}

export interface FormErrors {
  [fieldName: string]: string | undefined;
}

export interface FormState<T> {
  data: T;
  errors: FormErrors;
  isSubmitting: boolean;
  isDirty: boolean;
  isValid: boolean;
}

// =============================================================================
// API Response Types
// =============================================================================

export interface ApiResponse<T = any> {
  data: T;
  message?: string;
  success: boolean;
}

export interface PaginatedResponse<T = any> {
  data: T[];
  pagination: {
    page: number;
    limit: number;
    total: number;
    totalPages: number;
    hasNext: boolean;
    hasPrev: boolean;
  };
}

export interface ApiError {
  error: string;
  message: string;
  details?: Record<string, any>;
  statusCode?: number;
}

// =============================================================================
// Task Types (for reference)
// =============================================================================

export enum Priority {
  LOW = 'low',
  MEDIUM = 'medium',
  HIGH = 'high',
  URGENT = 'urgent',
}

export enum RecurrencePattern {
  NONE = 'none',
  DAILY = 'daily',
  WEEKLY = 'weekly',
  MONTHLY = 'monthly',
  YEARLY = 'yearly',
}

export interface TaskBase {
  title: string;
  description?: string;
  priority: Priority;
  dueDate?: string;
  recurrencePattern: RecurrencePattern;
}

export interface Task extends TaskBase {
  id: number;
  isCompleted: boolean;
  createdAt: string;
  updatedAt: string;
  userId: number;
}

export interface TaskCreate extends TaskBase {}
export interface TaskUpdate extends Partial<TaskBase> {}

// =============================================================================
// Component Props Types
// =============================================================================

export interface BaseButtonProps {
  children: React.ReactNode;
  type?: 'button' | 'submit' | 'reset';
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'destructive';
  size?: 'sm' | 'md' | 'lg';
  disabled?: boolean;
  loading?: boolean;
  className?: string;
  onClick?: () => void;
}

export interface BaseInputProps {
  name: string;
  type?: string;
  label?: string;
  placeholder?: string;
  value?: string;
  defaultValue?: string;
  required?: boolean;
  disabled?: boolean;
  error?: string;
  className?: string;
  onChange?: (value: string) => void;
  onBlur?: () => void;
}

export interface FormProps {
  onSubmit: (data: any) => void;
  children: React.ReactNode;
  className?: string;
}

// =============================================================================
// Context and Provider Types
// =============================================================================

export interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  signIn: (email: string, password: string) => Promise<void>;
  signUp: (email: string, password: string, name: string) => Promise<void>;
  signOut: () => Promise<void>;
  refresh: () => Promise<void>;
}

// =============================================================================
// Route Protection Types
// =============================================================================

export interface ProtectedRouteProps {
  children: React.ReactNode;
  fallback?: React.ReactNode;
  redirectTo?: string;
}

export interface PublicRouteProps {
  children: React.ReactNode;
  fallback?: React.ReactNode;
  redirectTo?: string;
}

// =============================================================================
// Loading and Error Types
// =============================================================================

export interface LoadingState {
  isLoading: boolean;
  message?: string;
}

export interface ErrorState {
  hasError: boolean;
  error?: Error | string;
  message?: string;
}

export interface AsyncState<T> extends LoadingState, ErrorState {
  data?: T;
}

// =============================================================================
// Utility Types
// =============================================================================

export type Optional<T, K extends keyof T> = Omit<T, K> & Partial<Pick<T, K>>;

export type RequiredBy<T, K extends keyof T> = T & Required<Pick<T, K>>;

export type DeepPartial<T> = {
  [P in keyof T]?: T[P] extends object ? DeepPartial<T[P]> : T[P];
};

export type ID = string | number;

export type Timestamp = string;

// =============================================================================
// Environment Types
// =============================================================================

export interface EnvConfig {
  NEXT_PUBLIC_API_URL: string;
  NEXT_PUBLIC_API_V1_PREFIX: string;
  NEXT_PUBLIC_BETTER_AUTH_URL: string;
  NEXT_PUBLIC_SITE_URL: string;
  BETTER_AUTH_SECRET: string;
  BETTER_AUTH_SIGN_IN_URL: string;
  BETTER_AUTH_SIGN_OUT_URL: string;
  BETTER_AUTH_SIGN_UP_URL: string;
  BETTER_AUTH_APP_NAME: string;
  BETTER_AUTH_TRUSTED_ORIGINS: string;
  NODE_ENV: 'development' | 'production' | 'test';
}