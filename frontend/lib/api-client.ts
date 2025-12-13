"use client";

import { betterAuthClient } from './auth';

// API base URL from environment variables
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const API_V1_PREFIX = process.env.NEXT_PUBLIC_API_V1_PREFIX || '/api/v1';

/**
 * Type definition for API request options
 */
interface ApiRequestOptions extends RequestInit {
  // Custom options can be added here if needed
}

/**
 * Enhanced fetch function with authentication headers
 */
async function apiRequest<T = any>(
  endpoint: string,
  options: ApiRequestOptions = {}
): Promise<T> {
  const url = `${API_BASE_URL}${API_V1_PREFIX}${endpoint}`;

  // Get authentication headers from Better Auth
  const authHeaders = await getAuthHeaders();

  // Prepare default headers
  const defaultHeaders: Record<string, string> = {
    'Content-Type': 'application/json',
    ...authHeaders,
  };

  // Merge with provided headers
  const headers = {
    ...defaultHeaders,
    ...options.headers,
  };

  try {
    const response = await fetch(url, {
      ...options,
      headers,
    });

    // Handle non-OK responses
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({
        error: 'Unknown error',
        message: `HTTP ${response.status}: ${response.statusText}`,
      }));

      // Handle authentication errors specifically
      if (response.status === 401) {
        // Clear auth state and redirect to sign in
        await betterAuthClient.signOut();
        window.location.href = '/sign-in';
        throw new Error('Authentication expired. Please sign in again.');
      }

      throw new Error(errorData.message || `HTTP ${response.status}: ${response.statusText}`);
    }

    // Return parsed JSON response
    return await response.json();
  } catch (error) {
    // Log error for debugging
    console.error(`API request failed: ${endpoint}`, error);
    throw error;
  }
}

/**
 * Get authentication headers from Better Auth client
 */
async function getAuthHeaders(): Promise<Record<string, string>> {
  try {
    // Get session from Better Auth
    const session = await betterAuthClient.getSession();

    if (session?.user && session.accessToken) {
      return {
        'Authorization': `Bearer ${session.accessToken}`,
      };
    }

    return {};
  } catch (error) {
    console.warn('Error getting auth headers:', error);
    return {};
  }
}

/**
 * API client methods for common HTTP operations
 */
export const apiClient = {
  // GET request
  get: <T = any>(endpoint: string, options: ApiRequestOptions = {}) =>
    apiRequest<T>(endpoint, { ...options, method: 'GET' }),

  // POST request
  post: <T = any>(endpoint: string, data?: any, options: ApiRequestOptions = {}) =>
    apiRequest<T>(endpoint, {
      ...options,
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined,
    }),

  // PUT request
  put: <T = any>(endpoint: string, data?: any, options: ApiRequestOptions = {}) =>
    apiRequest<T>(endpoint, {
      ...options,
      method: 'PUT',
      body: data ? JSON.stringify(data) : undefined,
    }),

  // PATCH request
  patch: <T = any>(endpoint: string, data?: any, options: ApiRequestOptions = {}) =>
    apiRequest<T>(endpoint, {
      ...options,
      method: 'PATCH',
      body: data ? JSON.stringify(data) : undefined,
    }),

  // DELETE request
  delete: <T = any>(endpoint: string, options: ApiRequestOptions = {}) =>
    apiRequest<T>(endpoint, { ...options, method: 'DELETE' }),

  // File upload (for multipart/form-data)
  upload: <T = any>(endpoint: string, formData: FormData, options: ApiRequestOptions = {}) => {
    // Remove Content-Type header to let browser set it with boundary
    const { headers, ...restOptions } = options;

    return apiRequest<T>(endpoint, {
      ...restOptions,
      method: 'POST',
      body: formData,
    });
  },
};

/**
 * Type definitions for API responses
 */
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

/**
 * Hook for API operations with error handling
 */
export function useApi() {
  return {
    ...apiClient,

    // Wrapper for API calls with loading states
    request: async <T = any>(
      requestFn: () => Promise<T>,
      options: {
        onSuccess?: (data: T) => void;
        onError?: (error: Error) => void;
      } = {}
    ): Promise<T> => {
      try {
        const result = await requestFn();
        options.onSuccess?.(result);
        return result;
      } catch (error) {
        const errorMessage = error instanceof Error ? error : new Error('Unknown error');
        options.onError?.(errorMessage);
        throw errorMessage;
      }
    },
  };
}

/**
 * Example usage:
 *
 * // GET request
 * const users = await apiClient.get<User[]>('/users');
 *
 * // POST request
 * const newUser = await apiClient.post<User>('/users', {
 *   name: 'John Doe',
 *   email: 'john@example.com'
 * });
 *
 * // With useApi hook
 * const { request } = useApi();
 * const result = await request(
 *   () => apiClient.get<Task[]>('/tasks'),
 *   {
 *     onSuccess: (data) => console.log('Tasks loaded:', data),
 *     onError: (error) => console.error('Failed to load tasks:', error),
 *   }
 * );
 */