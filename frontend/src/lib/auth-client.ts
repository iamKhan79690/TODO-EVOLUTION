'use client';

import { User, AuthState, UseAuthReturn } from '@/lib/types';

/**
 * Authentication client utilities for Better Auth integration
 * Handles token management, session persistence, and auth state
 */

export class AuthClient {
  private static instance: AuthClient;
  private storage: Storage;
  private tokenRefreshTimer: NodeJS.Timeout | null = null;
  private baseURL: string;

  private constructor() {
    this.storage = typeof window !== 'undefined' ? localStorage : ({} as Storage);
    this.baseURL = process.env.NEXT_PUBLIC_FASTAPI_URL || 'http://localhost:8001';
  }

  public static getInstance(): AuthClient {
    if (!AuthClient.instance) {
      AuthClient.instance = new AuthClient();
    }
    return AuthClient.instance;
  }

  /**
   * Get current access token
   */
  public getAccessToken(): string | null {
    try {
      return this.storage.getItem('access_token');
    } catch {
      return null;
    }
  }

  /**
   * Get current refresh token
   */
  public getRefreshToken(): string | null {
    try {
      return this.storage.getItem('refresh_token');
    } catch {
      return null;
    }
  }

  /**
   * Store authentication tokens
   */
  public setTokens(accessToken: string, refreshToken: string): void {
    try {
      this.storage.setItem('access_token', accessToken);
      this.storage.setItem('refresh_token', refreshToken);
    } catch (error) {
      console.warn('Failed to store tokens:', error);
    }
  }

  /**
   * Clear authentication tokens
   */
  public clearTokens(): void {
    try {
      this.storage.removeItem('access_token');
      this.storage.removeItem('refresh_token');
      this.storage.removeItem('user_data');
    } catch (error) {
      console.warn('Failed to clear tokens:', error);
    }

    // Clear token refresh timer
    if (this.tokenRefreshTimer) {
      clearTimeout(this.tokenRefreshTimer);
      this.tokenRefreshTimer = null;
    }
  }

  /**
   * Store user data
   */
  public setUser(user: User): void {
    try {
      this.storage.setItem('user_data', JSON.stringify(user));
    } catch (error) {
      console.warn('Failed to store user data:', error);
    }
  }

  /**
   * Get stored user data
   */
  public getUser(): User | null {
    try {
      const userData = this.storage.getItem('user_data');
      return userData ? JSON.parse(userData) : null;
    } catch {
      return null;
    }
  }

  /**
   * Check if user is authenticated
   */
  public isAuthenticated(): boolean {
    return !!(this.getAccessToken() && this.getUser());
  }

  /**
   * Refresh access token
   */
  public async refreshToken(): Promise<boolean> {
    const refreshToken = this.getRefreshToken();
    if (!refreshToken) {
      return false;
    }

    try {
      const response = await fetch(`${this.baseURL}/api/v1/auth/refresh`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ refreshToken }),
      });

      if (!response.ok) {
        throw new Error('Token refresh failed');
      }

      const data = await response.json();

      if (data.access_token && data.refresh_token) {
        this.setTokens(data.access_token, data.refresh_token);
        return true;
      }

      return false;
    } catch (error) {
      console.error('Token refresh error:', error);
      this.clearTokens();
      return false;
    }
  }

  /**
   * Setup automatic token refresh
   */
  public setupTokenRefresh(): void {
    // Clear any existing timer
    if (this.tokenRefreshTimer) {
      clearTimeout(this.tokenRefreshTimer);
    }

    // Setup new timer (refresh token 5 minutes before it expires)
    this.tokenRefreshTimer = setTimeout(async () => {
      const success = await this.refreshToken();
      if (success) {
        this.setupTokenRefresh(); // Setup next refresh
      }
    }, 50 * 60 * 1000); // 50 minutes
  }

  /**
   * Sign in with email and password
   */
  public async signIn(email: string, password: string): Promise<{ user: User; accessToken: string; refreshToken: string }> {
    let response: Response;

    try {
      response = await fetch(`${this.baseURL}/api/v1/auth/sign-in`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
      });
    } catch (error) {
      throw new Error('Unable to connect to server. Please check if the backend is running.');
    }

    if (!response.ok) {
      const errorData = await response.json().catch(() => null);
      const errorMessage = errorData?.message || errorData?.detail ||
        (typeof errorData === 'string' ? errorData : 'Sign in failed');
      throw new Error(errorMessage);
    }

    const data = await response.json();

    if (!data.user || !data.token) {
      throw new Error('Invalid response from server');
    }

    const { user, token } = data;
    const accessToken = token.access_token;
    const refreshToken = token.refresh_token;
    this.setTokens(accessToken, refreshToken);
    this.setUser(user);
    this.setupTokenRefresh();

    return { user, accessToken, refreshToken };
  }

  /**
   * Register new user
   */
  public async signUp(email: string, password: string, name: string): Promise<{ user: User; accessToken: string; refreshToken: string }> {
    let response: Response;

    try {
      response = await fetch(`${this.baseURL}/api/v1/auth/sign-up`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password, name }),
      });
    } catch (error) {
      throw new Error('Unable to connect to server. Please check if the backend is running.');
    }

    if (!response.ok) {
      const errorData = await response.json().catch(() => null);
      const errorMessage = errorData?.message || errorData?.detail ||
        (typeof errorData === 'string' ? errorData : 'Sign up failed');
      throw new Error(errorMessage);
    }

    const data = await response.json();

    if (!data.user || !data.token) {
      throw new Error('Invalid response from server');
    }

    const { user, token } = data;
    const accessToken = token.access_token;
    const refreshToken = token.refresh_token;
    this.setTokens(accessToken, refreshToken);
    this.setUser(user);
    this.setupTokenRefresh();

    return { user, accessToken, refreshToken };
  }

  /**
   * Sign out user
   */
  public async signOut(): Promise<void> {
    try {
      // Call server signout endpoint to invalidate session
      await fetch(`${this.baseURL}/api/v1/auth/sign-out`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${this.getAccessToken()}`,
        },
      });
    } catch (error) {
      console.warn('Server signout failed:', error);
    }

    this.clearTokens();
  }

  /**
   * Update user profile
   */
  public async updateProfile(updates: Partial<User>): Promise<User> {
    const response = await fetch('/api/users/profile', {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.getAccessToken()}`,
      },
      body: JSON.stringify(updates),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(
        errorData.message || errorData.detail || 'Profile update failed'
      );
    }

    const data = await response.json();

    if (!data.success || !data.data) {
      throw new Error('Invalid response from server');
    }

    const updatedUser = data.data.user;
    this.setUser(updatedUser);

    return updatedUser;
  }

  /**
   * Change password
   */
  public async changePassword(currentPassword: string, newPassword: string): Promise<void> {
    const response = await fetch('/api/users/change-password', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.getAccessToken()}`,
      },
      body: JSON.stringify({ currentPassword, newPassword }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(
        errorData.message || errorData.detail || 'Password change failed'
      );
    }
  }

  /**
   * Get current authentication state
   */
  public getAuthState(): AuthState {
    const user = this.getUser();
    const accessToken = this.getAccessToken();

    return {
      user,
      status: user && accessToken ? 'authenticated' : 'unauthenticated',
      error: null,
      accessToken: accessToken || undefined,
      refreshToken: this.getRefreshToken() || undefined,
    };
  }
}

// Create singleton instance
export const authClient = AuthClient.getInstance();
export default authClient;