'use client';

import React, { createContext, useContext, useCallback, useEffect, useState } from 'react';
import { Notification } from '@/lib/types';

interface NotificationContextType {
  notifications: Notification[];
  addNotification: (notification: Omit<Notification, 'id' | 'createdAt' | 'isVisible'>) => void;
  removeNotification: (id: string) => void;
  clearNotifications: () => void;
}

/**
 * Context for managing application-wide notifications
 */
const NotificationContext = createContext<NotificationContextType | undefined>(undefined);

export function useNotifications() {
  const context = useContext(NotificationContext);
  if (!context) {
    throw new Error('useNotifications must be used within NotificationProvider');
  }
  return context;
}

interface NotificationProviderProps {
  children: React.ReactNode;
}

/**
 * Provider component for notification management
 */
export function NotificationProvider({ children }: NotificationProviderProps) {
  const [notifications, setNotifications] = useState<Notification[]>([]);

  const addNotification = useCallback((notification: Omit<Notification, 'id' | 'createdAt' | 'isVisible'>) => {
    const newNotification: Notification = {
      ...notification,
      id: `notification-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      createdAt: new Date(),
      isVisible: true,
    };

    setNotifications(prev => [newNotification, ...prev]);

    // Auto-remove notification after timeout (if specified)
    if (notification.timeout && notification.timeout > 0) {
      setTimeout(() => {
        removeNotification(newNotification.id);
      }, notification.timeout);
    }
  }, []);

  const removeNotification = useCallback((id: string) => {
    setNotifications(prev => prev.filter(notification => notification.id !== id));
  }, []);

  const clearNotifications = useCallback(() => {
    setNotifications([]);
  }, []);

  return (
    <NotificationContext.Provider
      value={{
        notifications,
        addNotification,
        removeNotification,
        clearNotifications,
      }}
    >
      {children}
    </NotificationContext.Provider>
  );
}

interface NotificationItemProps {
  notification: Notification;
  onRemove: (id: string) => void;
}

/**
 * Individual notification component
 */
function NotificationItem({ notification, onRemove }: NotificationItemProps) {
  const [isVisible, setIsVisible] = useState(true);

  const handleRemove = () => {
    setIsVisible(false);
    setTimeout(() => onRemove(notification.id), 300); // Wait for animation
  };

  useEffect(() => {
    if (notification.timeout && notification.timeout > 0) {
      const timer = setTimeout(handleRemove, notification.timeout);
      return () => clearTimeout(timer);
    }
  }, [notification.timeout, handleRemove, onRemove]);

  const getNotificationStyles = () => {
    const baseStyles = 'p-4 rounded-lg shadow-lg border transition-all duration-300 mb-2';

    switch (notification.type) {
      case 'success':
        return `${baseStyles} bg-green-50 border-green-200 text-green-800`;
      case 'error':
        return `${baseStyles} bg-red-50 border-red-200 text-red-800`;
      case 'warning':
        return `${baseStyles} bg-yellow-50 border-yellow-200 text-yellow-800`;
      case 'info':
      default:
        return `${baseStyles} bg-blue-50 border-blue-200 text-blue-800`;
    }
  };

  const getNotificationIcon = () => {
    const iconClass = 'w-5 h-5 flex-shrink-0';

    switch (notification.type) {
      case 'success':
        return (
          <svg className={`${iconClass} text-green-600`} fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
          </svg>
        );
      case 'error':
        return (
          <svg className={`${iconClass} text-red-600`} fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
          </svg>
        );
      case 'warning':
        return (
          <svg className={`${iconClass} text-yellow-600`} fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
          </svg>
        );
      case 'info':
      default:
        return (
          <svg className={`${iconClass} text-blue-600`} fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
          </svg>
        );
    }
  };

  return (
    <div
      className={`${getNotificationStyles()} ${
        isVisible ? 'opacity-100 transform translate-x-0' : 'opacity-0 transform translate-x-full'
      }`}
    >
      <div className="flex items-start">
        <div className="flex-shrink-0">
          {getNotificationIcon()}
        </div>
        <div className="ml-3 flex-1">
          {notification.title && (
            <h4 className="text-sm font-medium mb-1">{notification.title}</h4>
          )}
          <p className="text-sm">{notification.message}</p>
        </div>
        <div className="ml-4 flex-shrink-0 flex">
          <button
            onClick={handleRemove}
            className="inline-flex text-gray-400 hover:text-gray-600 focus:outline-none focus:text-gray-600 transition-colors"
            aria-label="Close notification"
          >
            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
              <path
                fillRule="evenodd"
                d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
                clipRule="evenodd"
              />
            </svg>
          </button>
        </div>
      </div>
    </div>
  );
}

/**
 * Container for displaying all notifications
 */
export function NotificationContainer() {
  const { notifications, removeNotification } = useNotifications();

  if (notifications.length === 0) {
    return null;
  }

  return (
    <div className="fixed top-4 right-4 z-50 max-w-sm w-full">
      {notifications.map((notification) => (
        <NotificationItem
          key={notification.id}
          notification={notification}
          onRemove={removeNotification}
        />
      ))}
    </div>
  );
}

/**
 * Hook for showing notifications with convenience methods
 */
export function useNotificationActions() {
  const { addNotification } = useNotifications();

  const showSuccess = useCallback(
    (message: string, options?: { title?: string; timeout?: number }) => {
      addNotification({
        type: 'success',
        message,
        title: options?.title,
        timeout: options?.timeout ?? 5000,
      });
    },
    [addNotification]
  );

  const showError = useCallback(
    (message: string, options?: { title?: string; timeout?: number }) => {
      addNotification({
        type: 'error',
        message,
        title: options?.title || 'Error',
        timeout: options?.timeout ?? 10000, // Errors stay longer
      });
    },
    [addNotification]
  );

  const showWarning = useCallback(
    (message: string, options?: { title?: string; timeout?: number }) => {
      addNotification({
        type: 'warning',
        message,
        title: options?.title || 'Warning',
        timeout: options?.timeout ?? 7000,
      });
    },
    [addNotification]
  );

  const showInfo = useCallback(
    (message: string, options?: { title?: string; timeout?: number }) => {
      addNotification({
        type: 'info',
        message,
        title: options?.title || 'Info',
        timeout: options?.timeout ?? 5000,
      });
    },
    [addNotification]
  );

  return {
    showSuccess,
    showError,
    showWarning,
    showInfo,
    addNotification,
  };
}

/**
 * Higher-order component for notification functionality
 */
export function withNotifications<P extends object>(
  Component: React.ComponentType<P>
) {
  return function WithNotificationsComponent(props: P) {
    return (
      <NotificationProvider>
        <Component {...props} />
        <NotificationContainer />
      </NotificationProvider>
    );
  };
}

export default NotificationProvider;