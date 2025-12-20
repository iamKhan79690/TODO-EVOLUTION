'use client'

import React from 'react';

/**
 * Loading components for ChatKit interface
 * Provides various loading states with consistent styling
 */

interface LoadingSpinnerProps {
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl';
  color?: 'primary' | 'secondary' | 'white';
  className?: string;
}

export function LoadingSpinner({ size = 'md', color = 'primary', className = '' }: LoadingSpinnerProps) {
  const sizeClasses = {
    xs: 'w-4 h-4',
    sm: 'w-5 h-5',
    md: 'w-6 h-6',
    lg: 'w-8 h-8',
    xl: 'w-12 h-12',
  };

  const colorClasses = {
    primary: 'text-blue-600',
    secondary: 'text-gray-500',
    white: 'text-white',
  };

  return (
    <div
      className={`animate-spin ${sizeClasses[size]} ${colorClasses[color]} ${className}`}
      role="status"
      aria-label="Loading"
    >
      <svg
        className="w-full h-full"
        fill="none"
        viewBox="0 0 24 24"
      >
        <circle
          className="opacity-25"
          cx="12"
          cy="12"
          r="10"
          stroke="currentColor"
          strokeWidth="4"
        />
        <path
          className="opacity-75"
          fill="currentColor"
          d="m4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
        />
      </svg>
      <span className="sr-only">Loading...</span>
    </div>
  );
}

interface LoadingDotsProps {
  color?: 'primary' | 'secondary' | 'white';
  className?: string;
}

export function LoadingDots({ color = 'primary', className = '' }: LoadingDotsProps) {
  const colorClasses = {
    primary: 'bg-blue-600',
    secondary: 'bg-gray-500',
    white: 'bg-white',
  };

  return (
    <div className={`flex space-x-1 ${className}`} role="status" aria-label="Loading">
      <div
        className={`w-2 h-2 rounded-full ${colorClasses[color]} animate-bounce`}
        style={{ animationDelay: '0ms' }}
      />
      <div
        className={`w-2 h-2 rounded-full ${colorClasses[color]} animate-bounce`}
        style={{ animationDelay: '150ms' }}
      />
      <div
        className={`w-2 h-2 rounded-full ${colorClasses[color]} animate-bounce`}
        style={{ animationDelay: '300ms' }}
      />
      <span className="sr-only">Loading...</span>
    </div>
  );
}

interface LoadingPulseProps {
  className?: string;
}

export function LoadingPulse({ className = '' }: LoadingPulseProps) {
  return (
    <div
      className={`animate-pulse ${className}`}
      role="status"
      aria-label="Loading"
    >
      <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
      <div className="h-4 bg-gray-200 rounded w-1/2 mb-2"></div>
      <div className="h-4 bg-gray-200 rounded w-5/6"></div>
      <span className="sr-only">Loading...</span>
    </div>
  );
}

interface LoadingSkeletonProps {
  lines?: number;
  className?: string;
}

export function LoadingSkeleton({ lines = 3, className = '' }: LoadingSkeletonProps) {
  return (
    <div className={`space-y-3 ${className}`} role="status" aria-label="Loading content">
      {Array.from({ length: lines }).map((_, index) => (
        <div
          key={index}
          className="animate-pulse"
        >
          <div
            className="h-4 bg-gray-200 rounded"
            style={{
              width: `${Math.random() * 40 + 60}%`, // 60-100% width
            }}
          ></div>
        </div>
      ))}
      <span className="sr-only">Loading content...</span>
    </div>
  );
}

interface LoadingMessageProps {
  message?: string;
  className?: string;
}

export function LoadingMessage({ message = 'Loading...', className = '' }: LoadingMessageProps) {
  return (
    <div className={`flex items-center space-x-2 ${className}`} role="status" aria-label="Loading">
      <LoadingSpinner size="sm" />
      <span className="text-gray-600">{message}</span>
    </div>
  );
}

interface LoadingPageProps {
  message?: string;
  size?: 'sm' | 'md' | 'lg';
}

export function LoadingPage({ message = 'Loading...', size = 'md' }: LoadingPageProps) {
  const sizeClasses = {
    sm: 'w-8 h-8',
    md: 'w-12 h-12',
    lg: 'w-16 h-16',
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="text-center">
        <div className="flex justify-center mb-4">
          <LoadingSpinner size={size} />
        </div>
        <p className="text-gray-600 font-medium">{message}</p>
      </div>
    </div>
  );
}

interface LoadingCardProps {
  title?: string;
  className?: string;
}

export function LoadingCard({ title = 'Loading...', className = '' }: LoadingCardProps) {
  return (
    <div className={`bg-white rounded-lg shadow-sm border border-gray-200 p-6 ${className}`}>
      <div className="animate-pulse">
        <div className="h-6 bg-gray-200 rounded w-1/3 mb-4"></div>
        <div className="space-y-2">
          <div className="h-4 bg-gray-200 rounded"></div>
          <div className="h-4 bg-gray-200 rounded w-5/6"></div>
          <div className="h-4 bg-gray-200 rounded w-4/6"></div>
        </div>
      </div>
      <div className="sr-only">{title}</div>
    </div>
  );
}

interface LoadingButtonProps {
  children: React.ReactNode;
  loading?: boolean;
  disabled?: boolean;
  className?: string;
}

export function LoadingButton({
  children,
  loading = false,
  disabled = false,
  className = ''
}: LoadingButtonProps) {
  return (
    <button
      className={`
        inline-flex items-center justify-center px-4 py-2 border border-transparent
        text-sm font-medium rounded-md shadow-sm text-white bg-blue-600
        hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2
        focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed
        ${className}
      `}
      disabled={disabled || loading}
    >
      {loading && <LoadingSpinner size="sm" color="white" className="mr-2" />}
      {children}
    </button>
  );
}

// Chat-specific loading components
interface ChatLoadingProps {
  message?: string;
  showTypingIndicator?: boolean;
}

export function ChatLoading({
  message = 'AI is typing...',
  showTypingIndicator = true
}: ChatLoadingProps) {
  return (
    <div className="flex items-start space-x-3 p-4">
      <div className="flex-shrink-0 w-8 h-8 bg-gray-300 rounded-full flex items-center justify-center">
        <span className="text-gray-600 text-sm font-medium">AI</span>
      </div>
      <div className="flex-1 min-w-0">
        <div className="bg-gray-100 rounded-lg p-3 inline-block max-w-md">
          {showTypingIndicator ? (
            <div className="flex items-center space-x-1">
              <LoadingDots color="secondary" />
              <span className="text-gray-600 text-sm">{message}</span>
            </div>
          ) : (
            <LoadingMessage message={message} />
          )}
        </div>
      </div>
    </div>
  );
}

interface MessageLoadingProps {
  isOwn?: boolean;
}

export function MessageLoading({ isOwn = false }: MessageLoadingProps) {
  return (
    <div className={`flex ${isOwn ? 'justify-end' : 'justify-start'} mb-4`}>
      <div
        className={`
          max-w-xs lg:max-w-md px-4 py-2 rounded-lg
          ${isOwn
            ? 'bg-blue-600 text-white'
            : 'bg-gray-200 text-gray-800'
          }
        `}
      >
        <LoadingDots color={isOwn ? 'white' : 'secondary'} />
      </div>
    </div>
  );
}

interface ConversationLoadingProps {
  count?: number;
}

export function ConversationLoading({ count = 5 }: ConversationLoadingProps) {
  return (
    <div className="space-y-2">
      {Array.from({ length: count }).map((_, index) => (
        <div
          key={index}
          className="p-3 bg-white border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer"
        >
          <div className="animate-pulse">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gray-200 rounded-full"></div>
              <div className="flex-1 min-w-0">
                <div className="h-4 bg-gray-200 rounded w-3/4 mb-1"></div>
                <div className="h-3 bg-gray-200 rounded w-1/2"></div>
              </div>
              <div className="h-3 bg-gray-200 rounded w-16"></div>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}

export default {
  LoadingSpinner,
  LoadingDots,
  LoadingPulse,
  LoadingSkeleton,
  LoadingMessage,
  LoadingPage,
  LoadingCard,
  LoadingButton,
  ChatLoading,
  MessageLoading,
  ConversationLoading,
};