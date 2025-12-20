import {
  Conversation,
  Message,
  UserPreferences,
  CreateConversationRequest,
  SendMessageRequest,
  RealtimeUpdate,
  ApiResponse
} from './types';

/**
 * Centralized Chat API client for chat operations
 * Handles all HTTP requests to the chat backend with proper error handling and authentication
 */
export class ChatAPI {
  private baseURL: string;
  private defaultHeaders: Record<string, string>;

  constructor(baseURL?: string) {
    this.baseURL = baseURL || process.env.NEXT_PUBLIC_CHAT_API_URL || 'http://localhost:8000/api';
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
      // Get token from localStorage or auth client
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

        // Handle 401 unauthorized - token might be expired
        if (response.status === 401) {
          // Clear invalid token and redirect to auth
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          localStorage.removeItem('user_data');

          if (typeof window !== 'undefined') {
            window.location.href = '/auth/signin';
          }
        }

        throw new Error(
          errorData.detail ||
          errorData.message ||
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

  // Conversation endpoints

  /**
   * Get all conversations for the authenticated user
   */
  async getConversations(): Promise<Conversation[]> {
    return this.request<Conversation[]>('/conversations');
  }

  /**
   * Get a specific conversation by ID
   */
  async getConversation(conversationId: string): Promise<Conversation> {
    return this.request<Conversation>(`/conversations/${conversationId}`);
  }

  /**
   * Create a new conversation
   */
  async createConversation(title?: string): Promise<Conversation> {
    return this.request<Conversation>('/conversations', {
      method: 'POST',
      body: JSON.stringify(title ? { title } : {}),
    });
  }

  /**
   * Update conversation metadata
   */
  async updateConversation(
    conversationId: string,
    updates: { title?: string; isArchived?: boolean }
  ): Promise<Conversation> {
    return this.request<Conversation>(`/conversations/${conversationId}`, {
      method: 'PUT',
      body: JSON.stringify(updates),
    });
  }

  /**
   * Delete a conversation and all its messages
   */
  async deleteConversation(conversationId: string): Promise<void> {
    return this.request<void>(`/conversations/${conversationId}`, {
      method: 'DELETE',
    });
  }

  // Message endpoints

  /**
   * Get all messages for a conversation
   */
  async getMessages(
    conversationId: string,
    limit: number = 50,
    offset: number = 0
  ): Promise<Message[]> {
    const queryParams = new URLSearchParams({
      limit: limit.toString(),
      offset: offset.toString(),
    });

    return this.request<Message[]>(
      `/conversations/${conversationId}/messages?${queryParams.toString()}`
    );
  }

  /**
   * Send a message to a conversation
   */
  async sendMessage(
    conversationId: string,
    content: string
  ): Promise<Message> {
    return this.request<Message>(`/conversations/${conversationId}/messages`, {
      method: 'POST',
      body: JSON.stringify({ content }),
    });
  }

  /**
   * Delete a specific message
   */
  async deleteMessage(conversationId: string, messageId: string): Promise<void> {
    return this.request<void>(
      `/conversations/${conversationId}/messages/${messageId}`,
      {
        method: 'DELETE',
      }
    );
  }

  // Real-time endpoints

  /**
   * Get real-time updates for a conversation
   */
  async getUpdates(
    conversationId: string,
    lastMessageId?: string,
    limit: number = 10
  ): Promise<RealtimeUpdate> {
    const queryParams = new URLSearchParams({
      limit: limit.toString(),
    });

    if (lastMessageId) {
      queryParams.set('lastMessageId', lastMessageId);
    }

    return this.request<RealtimeUpdate>(
      `/conversations/${conversationId}/updates?${queryParams.toString()}`
    );
  }

  // User preferences endpoints

  /**
   * Get user preferences
   */
  async getUserPreferences(): Promise<UserPreferences> {
    return this.request<UserPreferences>('/user/preferences');
  }

  /**
   * Update user preferences
   */
  async updateUserPreferences(
    preferences: Partial<UserPreferences>
  ): Promise<UserPreferences> {
    return this.request<UserPreferences>('/user/preferences', {
      method: 'PUT',
      body: JSON.stringify(preferences),
    });
  }

  // Utility methods

  /**
   * Check API health status
   */
  async healthCheck(): Promise<{ status: string; timestamp: string }> {
    return this.request<{ status: string; timestamp: string }>('/health');
  }

  /**
   * Test connectivity to the API
   */
  async testConnection(): Promise<boolean> {
    try {
      await this.healthCheck();
      return true;
    } catch (error) {
      console.error('API connection test failed:', error);
      return false;
    }
  }
}

// Create a singleton instance for the application
export const chatAPI = new ChatAPI();

// Export a default instance for easier importing
export default chatAPI;