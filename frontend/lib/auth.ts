/**
 * Better Auth configuration for the Todo Evolution frontend
 */

import { createAuthClient } from 'better-auth/react';

// Better Auth client configuration
const authConfig = {
  baseURL: process.env.NEXT_PUBLIC_BETTER_AUTH_URL || 'http://localhost:8001/api/auth',
  plugins: [],
};

// Create auth client
export const betterAuthClient = createAuthClient(authConfig);

// Export commonly used auth methods for easier access
// Note: Only methods that exist in Better Auth client are exported
export const {
  signIn,
  signUp,
  signOut,
  getSession,
  useSession,
} = betterAuthClient;

// Custom hooks for common authentication patterns
export function useAuthenticatedUser() {
  const { data: session, isPending } = betterAuthClient.useSession();

  return {
    user: session?.user || null,
    isLoading: isPending,
    isAuthenticated: !!session?.user,
  };
}

// Helper function to check if user is authenticated
export async function checkAuthentication(): Promise<boolean> {
  try {
    const result = await betterAuthClient.getSession();
    return !!(result && 'data' in result && result.data?.user);
  } catch (error) {
    console.error('Error checking authentication:', error);
    return false;
  }
}

// Helper function to get current user
export async function getCurrentUser() {
  try {
    const result = await betterAuthClient.getSession();
    if (result && 'data' in result && result.data?.user) {
      return result.data.user;
    }
    return null;
  } catch (error) {
    console.error('Error getting current user:', error);
    return null;
  }
}

// Helper function to redirect authenticated/unauthenticated users
export function redirectBasedOnAuth(isAuthenticated: boolean) {
  const currentPath = window.location.pathname;

  if (isAuthenticated) {
    // If authenticated and on auth pages, redirect to dashboard
    if (currentPath.startsWith('/sign-') || currentPath === '/') {
      window.location.href = '/dashboard';
    }
  } else {
    // If not authenticated and on protected pages, redirect to sign in
    const protectedPaths = ['/dashboard', '/tasks', '/settings', '/profile'];
    const isProtectedPath = protectedPaths.some(path => currentPath.startsWith(path));

    if (isProtectedPath) {
      window.location.href = '/sign-in';
    }
  }
}

// Export default for convenience
export default betterAuthClient;