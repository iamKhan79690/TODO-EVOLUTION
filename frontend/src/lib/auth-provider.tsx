'use client';

import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import { User, AuthState } from './types';
import authClient from './auth-client';

interface AuthContextType extends AuthState {
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, name: string) => Promise<void>;
  logout: () => Promise<void>;
  updateProfile: (updates: Partial<User>) => Promise<User>;
  refreshToken: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

interface AuthProviderProps {
  children: ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [authState, setAuthState] = useState<AuthState>({
    user: null,
    status: 'idle',
    error: null,
  });

  useEffect(() => {
    // Check for existing session on mount
    const checkSession = async () => {
      setAuthState(prev => ({ ...prev, status: 'loading' }));

      try {
        const user = authClient.getUser();
        const accessToken = authClient.getAccessToken();

        if (user && accessToken) {
          setAuthState({
            user,
            status: 'authenticated',
            error: null,
            accessToken,
            refreshToken: authClient.getRefreshToken(),
          });
        } else {
          setAuthState({
            user: null,
            status: 'unauthenticated',
            error: null,
          });
        }
      } catch (error) {
        setAuthState({
          user: null,
          status: 'unauthenticated',
          error: 'Failed to check session',
        });
      }
    };

    checkSession();
  }, []);

  const login = async (email: string, password: string) => {
    setAuthState(prev => ({ ...prev, status: 'loading', error: null }));

    try {
      const { user, accessToken, refreshToken } = await authClient.signIn(email, password);

      setAuthState({
        user,
        status: 'authenticated',
        error: null,
        accessToken,
        refreshToken,
      });
    } catch (error) {
      setAuthState({
        user: null,
        status: 'unauthenticated',
        error: error instanceof Error ? error.message : 'Login failed',
      });
      throw error;
    }
  };

  const register = async (email: string, password: string, name: string) => {
    setAuthState(prev => ({ ...prev, status: 'loading', error: null }));

    try {
      const { user, accessToken, refreshToken } = await authClient.signUp(email, password, name);

      setAuthState({
        user,
        status: 'authenticated',
        error: null,
        accessToken,
        refreshToken,
      });
    } catch (error) {
      setAuthState({
        user: null,
        status: 'unauthenticated',
        error: error instanceof Error ? error.message : 'Registration failed',
      });
      throw error;
    }
  };

  const logout = async () => {
    setAuthState(prev => ({ ...prev, status: 'loading' }));

    try {
      await authClient.signOut();
      setAuthState({
        user: null,
        status: 'unauthenticated',
        error: null,
      });
    } catch (error) {
      // Even if logout fails on server, clear local state
      setAuthState({
        user: null,
        status: 'unauthenticated',
        error: null,
      });
    }
  };

  const updateProfile = async (updates: Partial<User>) => {
    setAuthState(prev => ({ ...prev, status: 'loading', error: null }));

    try {
      const updatedUser = await authClient.updateProfile(updates);

      setAuthState(prev => ({
        ...prev,
        user: updatedUser,
        status: 'authenticated',
      }));

      return updatedUser;
    } catch (error) {
      setAuthState(prev => ({
        ...prev,
        status: 'authenticated',
        error: error instanceof Error ? error.message : 'Profile update failed',
      }));
      throw error;
    }
  };

  const refreshToken = async () => {
    try {
      const success = await authClient.refreshToken();

      if (success) {
        setAuthState(prev => ({
          ...prev,
          accessToken: authClient.getAccessToken() || undefined,
          refreshToken: authClient.getRefreshToken() || undefined,
        }));
      } else {
        setAuthState({
          user: null,
          status: 'unauthenticated',
          error: 'Session expired',
        });
      }
    } catch (error) {
      setAuthState({
        user: null,
        status: 'unauthenticated',
        error: 'Token refresh failed',
      });
    }
  };

  const value: AuthContextType = {
    ...authState,
    login,
    register,
    logout,
    updateProfile,
    refreshToken,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export default AuthProvider;