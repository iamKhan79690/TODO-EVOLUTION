import {
  Task,
  CreateTaskDTO,
  UpdateTaskDTO,
  TaskQueryParams,
  ApiResponse,
  PaginatedResponse,
  TaskStatsResponse
} from './types';

/**
 * Centralized API client for task management operations
 * Handles all HTTP requests to the backend with proper error handling and JWT authentication
 */
export class TaskAPI {
  private baseURL: string;
  private defaultHeaders: Record<string, string>;

  constructor(baseURL: string = process.env.NEXT_PUBLIC_FASTAPI_URL || 'http://localhost:8001') {
    this.baseURL = baseURL;
    this.defaultHeaders = {
      'Content-Type': 'application/json',
    };
  }

  /**
   * Get authentication headers for requests
   */
  private async getAuthHeaders(): Promise<Record<string, string>> {
    if (typeof window === 'undefined') {
      return {};
    }

    try {
      // Get token from localStorage or any other storage method
      const token = localStorage.getItem('access_token');
      if (token) {
        return {
          ...this.defaultHeaders,
          'Authorization': `Bearer ${token}`,
        };
      }
    } catch (error) {
      console.warn('Failed to get auth token:', error);
    }

    return this.defaultHeaders;
  }

  /**
   * Make an HTTP request with proper error handling
   */
  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;
    const headers = await this.getAuthHeaders();

    try {
      const response = await fetch(url, {
        ...options,
        headers: {
          ...headers,
          ...options.headers,
        },
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(
          errorData.message ||
          errorData.detail ||
          `HTTP ${response.status}: ${response.statusText}`
        );
      }

      return await response.json();
    } catch (error) {
      if (error instanceof Error) {
        throw error;
      }
      throw new Error('Network request failed');
    }
  }

  /**
   * Fetch tasks with pagination and filtering
   */
  async getTasks(params?: TaskQueryParams): Promise<PaginatedResponse<Task>> {
    const queryParams = new URLSearchParams();

    if (params?.page) queryParams.set('page', params.page.toString());
    if (params?.limit) queryParams.set('limit', params.limit.toString());
    if (params?.search) queryParams.set('search', params.search);
    if (params?.status) queryParams.set('status', params.status);
    if (params?.priority) queryParams.set('priority', params.priority);
    if (params?.assignedTo) queryParams.set('assignedTo', params.assignedTo);
    if (params?.tag) queryParams.set('tag', params.tag);
    if (params?.sortBy) queryParams.set('sortBy', params.sortBy);
    if (params?.sortOrder) queryParams.set('sortOrder', params.sortOrder);

    if (params?.dueDate?.from) queryParams.set('dueDateFrom', params.dueDate.from);
    if (params?.dueDate?.to) queryParams.set('dueDateTo', params.dueDate.to);

    const queryString = queryParams.toString();
    const endpoint = `/api/tasks${queryString ? `?${queryString}` : ''}`;

    return this.request<PaginatedResponse<Task>>(endpoint);
  }

  /**
   * Fetch a single task by ID
   */
  async getTask(id: string): Promise<ApiResponse<Task>> {
    return this.request<ApiResponse<Task>>(`/api/tasks/${id}`);
  }

  /**
   * Create a new task
   */
  async createTask(taskData: CreateTaskDTO): Promise<ApiResponse<Task>> {
    return this.request<ApiResponse<Task>>('/api/tasks', {
      method: 'POST',
      body: JSON.stringify(taskData),
    });
  }

  /**
   * Update an existing task
   */
  async updateTask(id: string, updates: UpdateTaskDTO): Promise<ApiResponse<Task>> {
    return this.request<ApiResponse<Task>>(`/api/tasks/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(updates),
    });
  }

  /**
   * Delete a task
   */
  async deleteTask(id: string): Promise<ApiResponse<void>> {
    return this.request<ApiResponse<void>>(`/api/tasks/${id}`, {
      method: 'DELETE',
    });
  }

  /**
   * Bulk update multiple tasks
   */
  async bulkUpdate(taskIds: string[], updates: UpdateTaskDTO): Promise<ApiResponse<Task[]>> {
    return this.request<ApiResponse<Task[]>>('/api/tasks/bulk', {
      method: 'PATCH',
      body: JSON.stringify({
        taskIds,
        updates,
      }),
    });
  }

  /**
   * Bulk delete multiple tasks
   */
  async bulkDelete(taskIds: string[]): Promise<ApiResponse<void>> {
    return this.request<ApiResponse<void>>('/api/tasks/bulk', {
      method: 'DELETE',
      body: JSON.stringify({
        taskIds,
      }),
    });
  }

  /**
   * Get task statistics
   */
  async getTaskStats(params?: {
    dateRange?: {
      from: string;
      to: string;
    };
  }): Promise<ApiResponse<TaskStatsResponse>> {
    const queryParams = new URLSearchParams();

    if (params?.dateRange?.from) queryParams.set('from', params.dateRange.from);
    if (params?.dateRange?.to) queryParams.set('to', params.dateRange.to);

    const queryString = queryParams.toString();
    const endpoint = `/api/tasks/stats${queryString ? `?${queryString}` : ''}`;

    return this.request<ApiResponse<TaskStatsResponse>>(endpoint);
  }

  /**
   * Search tasks with advanced filtering
   */
  async searchTasks(searchData: {
    query: {
      text?: string;
      filters: {
        status?: string[];
        priority?: string[];
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
      field: string;
      direction: 'asc' | 'desc';
    }>;
    pagination: {
      page: number;
      limit: number;
    };
  }): Promise<ApiResponse<{
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
        status: string;
        count: number;
      }>;
      priorities: Array<{
        priority: string;
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
  }>> {
    return this.request('/api/tasks/search', {
      method: 'POST',
      body: JSON.stringify(searchData),
    });
  }

  /**
   * Upload file attachment for a task
   */
  async uploadTaskAttachment(
    taskId: string,
    file: File,
    description?: string
  ): Promise<ApiResponse<{
    attachment: {
      id: string;
      filename: string;
      originalName: string;
      size: number;
      mimeType: string;
      url: string;
      uploadedAt: string;
    };
  }>> {
    const formData = new FormData();
    formData.append('file', file);
    if (description) {
      formData.append('description', description);
    }

    const headers = await this.getAuthHeaders();
    // Remove Content-Type header to let browser set it with boundary for multipart/form-data
    delete headers['Content-Type'];

    const response = await fetch(`${this.baseURL}/api/tasks/${taskId}/attachments`, {
      method: 'POST',
      headers,
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(
        errorData.message ||
        errorData.detail ||
        `HTTP ${response.status}: ${response.statusText}`
      );
    }

    return response.json();
  }

  /**
   * Delete task attachment
   */
  async deleteTaskAttachment(taskId: string, attachmentId: string): Promise<ApiResponse<void>> {
    return this.request<ApiResponse<void>>(`/api/tasks/${taskId}/attachments/${attachmentId}`, {
      method: 'DELETE',
    });
  }

  /**
   * Check API health status
   */
  async healthCheck(): Promise<ApiResponse<{ status: string; timestamp: string }>> {
    return this.request<ApiResponse<{ status: string; timestamp: string }>>('/api/health');
  }
}

// Create a singleton instance for the application
export const taskAPI = new TaskAPI();

// Export a default instance for easier importing
export default taskAPI;