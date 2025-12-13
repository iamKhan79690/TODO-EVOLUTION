"use client";

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import SignUpForm from '@/components/auth/signup-form';
import { useAuth } from '@/lib/auth-provider';

export default function SignUpPage() {
  const router = useRouter();
  const { signUp, isAuthenticated, isLoading: authLoading } = useAuth();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  // Handle form submission
  const handleSubmit = async (formData: {
    email: string;
    password: string;
    name: string;
  }) => {
    setIsSubmitting(true);
    setError(null);

    try {
      await signUp(formData.email, formData.password, formData.name);
      setSuccess(true);

      // Redirect to dashboard after successful sign up
      setTimeout(() => {
        router.push('/dashboard');
      }, 2000);

    } catch (err: any) {
      console.error('Sign up error:', err);

      // Handle different types of errors
      if (err.message?.includes('Email already exists')) {
        setError('An account with this email already exists. Please sign in instead.');
      } else if (err.message?.includes('password')) {
        setError('Password does not meet the requirements. Please choose a stronger password.');
      } else if (err.message?.includes('email')) {
        setError('Please enter a valid email address.');
      } else {
        setError('Something went wrong. Please try again later.');
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  // Show loading state while checking authentication
  if (authLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  // Redirect if already authenticated
  if (isAuthenticated) {
    return null; // Will be handled by AuthLayout
  }

  // Show success state
  if (success) {
    return (
      <div className="text-center">
        <div className="mb-4">
          <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-green-100">
            <svg className="h-6 w-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
          </div>
        </div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          Account Created Successfully!
        </h2>
        <p className="text-gray-600 mb-4">
          Welcome to Todo Evolution! Redirecting you to your dashboard...
        </p>
        <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600 mx-auto"></div>
      </div>
    );
  }

  return (
    <div>
      <div className="mb-6 text-center">
        <h2 className="text-3xl font-bold text-gray-900">
          Create Your Account
        </h2>
        <p className="mt-2 text-gray-600">
          Start organizing your tasks with Todo Evolution
        </p>
      </div>

      {error && (
        <div className="mb-4 bg-red-50 border border-red-200 rounded-md p-4">
          <div className="text-red-800 text-sm">{error}</div>
        </div>
      )}

      <SignUpForm
        onSubmit={handleSubmit}
        isSubmitting={isSubmitting}
      />

      <div className="mt-6 text-center">
        <p className="text-sm text-gray-600">
          Already have an account?{' '}
          <Link
            href="/sign-in"
            className="text-blue-600 hover:text-blue-500 font-medium"
          >
            Sign in here
          </Link>
        </p>
      </div>
    </div>
  );
}