/**
 * Better Auth configuration for the Todo Evolution frontend
 */

import { createAuthClient } from 'better-auth/react';

// Mock authentication configuration for MVP
const mockAuthConfig = {
  baseURL: process.env.NEXT_PUBLIC_BETTER_AUTH_URL || 'http://localhost:8001/api/auth',
  plugins: [],
};

// Create mock auth client for MVP
export const betterAuthClient = createAuthClient(mockAuthConfig);

// Export commonly used auth methods for easier access
export const {
  // Authentication methods
  signIn,
  signUp,
  signOut,
  getSession,
  refresh,

  // User management
  updateUser,
  deleteUser,
  changePassword,
  resetPassword,
  forgetPassword,

  // Social providers (disabled for MVP)
  // signInWithSocial,
  // linkSocialAccount,

  // Session management
  listSessions,
  revokeSession,
  revokeAllSessions,

  // Email verification
  sendVerificationEmail,
  verifyEmail,

  // Two-factor authentication (disabled for MVP)
  // enableTwoFactor,
  // disableTwoFactor,
  // verifyTwoFactor,

  // Utility methods
  useAuth,
  useUser,
  useSession,
  isAuthenticated,
} = betterAuthClient;

// Custom hooks for common authentication patterns
export function useAuthenticatedUser() {
  const { data: session, isLoading } = betterAuthClient.useSession();

  return {
    user: session?.user || null,
    isLoading,
    isAuthenticated: !!session?.user,
  };
}

// Helper function to check if user is authenticated
export async function checkAuthentication(): Promise<boolean> {
  try {
    const session = await betterAuthClient.getSession();
    return !!session?.user;
  } catch (error) {
    console.error('Error checking authentication:', error);
    return false;
  }
}

// Helper function to get current user
export async function getCurrentUser() {
  try {
    const session = await betterAuthClient.getSession();
    return session?.user || null;
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