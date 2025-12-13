"use client";

import { ReactNode } from 'react';
import Link from 'next/link';
import { useAuth } from '@/lib/auth-provider';

interface AuthLayoutProps {
  children: ReactNode;
}

export default function AuthLayout({ children }: AuthLayoutProps) {
  const { isAuthenticated } = useAuth();

  // Redirect authenticated users to dashboard
  if (isAuthenticated) {
    window.location.href = '/dashboard';
    return null;
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        {/* Header */}
        <div className="text-center">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            Todo Evolution
          </h1>
          <p className="text-gray-600">
            Organize your tasks with recurring patterns and due dates
          </p>
        </div>

        {/* Navigation */}
        <div className="flex justify-center space-x-4 text-sm">
          <Link
            href="/sign-in"
            className="text-gray-600 hover:text-gray-900 font-medium"
          >
            Sign In
          </Link>
          <span className="text-gray-400">|</span>
          <Link
            href="/sign-up"
            className="text-blue-600 hover:text-blue-500 font-medium"
          >
            Sign Up
          </Link>
        </div>

        {/* Main Content */}
        <div className="bg-white py-8 px-6 shadow-lg rounded-lg">
          {children}
        </div>

        {/* Footer */}
        <div className="text-center text-xs text-gray-500">
          <p>
            By continuing, you agree to our{' '}
            <Link href="/terms" className="text-blue-600 hover:text-blue-500">
              Terms of Service
            </Link>{' '}
            and{' '}
            <Link href="/privacy" className="text-blue-600 hover:text-blue-500">
              Privacy Policy
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}