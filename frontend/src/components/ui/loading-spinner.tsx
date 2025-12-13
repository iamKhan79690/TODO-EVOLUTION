'use client';

import React from 'react';

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  className?: string;
  text?: string;
}

/**
 * Reusable loading spinner component with different sizes and optional text
 */
export function LoadingSpinner({
  size = 'md',
  className = '',
  text,
}: LoadingSpinnerProps) {
  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-6 h-6',
    lg: 'w-8 h-8',
  };

  return (
    <div className={`flex items-center justify-center ${className}`}>
      <div
        className={`
          ${sizeClasses[size]}
          animate-spin rounded-full border-2 border-gray-300 border-t-blue-600
        `}
      />
      {text && (
        <span className="ml-2 text-sm text-gray-600">{text}</span>
      )}
    </div>
  );
}

interface LoadingOverlayProps {
  isLoading: boolean;
  text?: string;
  children: React.ReactNode;
  className?: string;
}

/**
 * Loading overlay that covers its children when loading
 */
export function LoadingOverlay({
  isLoading,
  text = 'Loading...',
  children,
  className = '',
}: LoadingOverlayProps) {
  return (
    <div className={`relative ${className}`}>
      {children}
      {isLoading && (
        <div className="absolute inset-0 bg-white bg-opacity-75 flex items-center justify-center z-50">
          <LoadingSpinner text={text} />
        </div>
      )}
    </div>
  );
}

interface LoadingStateProps {
  isLoading: boolean;
  error?: string | null;
  children: React.ReactNode;
  fallback?: React.ReactNode;
  errorFallback?: React.ReactNode;
  className?: string;
}

/**
 * Component that handles loading and error states
 */
export function LoadingState({
  isLoading,
  error,
  children,
  fallback,
  errorFallback,
  className = '',
}: LoadingStateProps) {
  if (error) {
    return (
      errorFallback || (
        <div className={`text-center py-8 ${className}`}>
          <div className="text-red-600 mb-2">
            <svg
              className="w-12 h-12 mx-auto"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 15.5c-.77.833.192 2.5 1.732 2.5z"
              />
            </svg>
          </div>
          <p className="text-gray-600">{error}</p>
        </div>
      )
    );
  }

  if (isLoading) {
    return (
      fallback || (
        <div className={`text-center py-8 ${className}`}>
          <LoadingSpinner size="lg" text="Loading..." />
        </div>
      )
    );
  }

  return <>{children}</>;
}

/**
 * Skeleton loading component for content placeholders
 */
export function Skeleton({
  className = '',
  lines = 3,
}: {
  className?: string;
  lines?: number;
}) {
  return (
    <div className={`space-y-2 ${className}`}>
      {Array.from({ length: lines }).map((_, index) => (
        <div
          key={index}
          className={`
            h-4 bg-gray-200 rounded animate-pulse
            ${index === lines - 1 ? 'w-3/4' : 'w-full'}
          `}
        />
      ))}
    </div>
  );
}

/**
 * Card skeleton for task items
 */
export function TaskCardSkeleton() {
  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
      <div className="space-y-3">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <Skeleton className="w-3/4" lines={1} />
            <Skeleton className="w-full mt-2" lines={2} />
          </div>
          <div className="flex space-x-2">
            <div className="w-8 h-8 bg-gray-200 rounded animate-pulse" />
            <div className="w-8 h-8 bg-gray-200 rounded animate-pulse" />
          </div>
        </div>
        <div className="flex items-center justify-between">
          <div className="flex space-x-2">
            <div className="w-16 h-6 bg-gray-200 rounded-full animate-pulse" />
            <div className="w-16 h-6 bg-gray-200 rounded-full animate-pulse" />
          </div>
          <div className="w-20 h-4 bg-gray-200 rounded animate-pulse" />
        </div>
      </div>
    </div>
  );
}

/**
 * List skeleton for multiple items
 */
export function TaskListSkeleton({ count = 5 }: { count?: number }) {
  return (
    <div className="space-y-4">
      {Array.from({ length: count }).map((_, index) => (
        <TaskCardSkeleton key={index} />
      ))}
    </div>
  );
}

/**
 * Full page loading component
 */
export function FullPageLoading({ text = 'Loading...' }: { text?: string }) {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="text-center">
        <LoadingSpinner size="lg" text={text} className="mb-4" />
        <p className="text-gray-600">Please wait while we load your content...</p>
      </div>
    </div>
  );
}

/**
 * Button loading state component
 */
export function LoadingButton({
  isLoading,
  children,
  disabled,
  className = '',
  ...props
}: React.ButtonHTMLAttributes<HTMLButtonElement> & {
  isLoading?: boolean;
}) {
  return (
    <button
      {...props}
      disabled={disabled || isLoading}
      className={`
        relative inline-flex items-center justify-center
        ${isLoading ? 'opacity-75 cursor-not-allowed' : ''}
        ${className}
      `}
    >
      {isLoading && (
        <LoadingSpinner size="sm" className="mr-2" />
      )}
      {children}
    </button>
  );
}

export default LoadingSpinner;