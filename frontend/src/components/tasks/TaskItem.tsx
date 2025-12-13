'use client';

import React, { useState } from 'react';
import { Task, TaskStatus, TaskPriority } from '@/lib/types';
import { format } from 'date-fns';
import {
  CheckCircle2,
  Circle,
  Clock,
  AlertCircle,
  XCircle,
  Edit2,
  Trash2,
  Calendar,
  Tag
} from 'lucide-react';

interface TaskItemProps {
  task: Task;
  onUpdate: (id: string, updates: Partial<Task>) => void;
  onDelete: (id: string) => void;
  onEdit: (task: Task) => void;
  isCompact?: boolean;
}

/**
 * Individual task component with edit, delete, and status change actions
 */
export default function TaskItem({ task, onUpdate, onDelete, onEdit, isCompact = false }: TaskItemProps) {
  const [isLoading, setIsLoading] = useState(false);

  const handleStatusChange = async (newStatus: TaskStatus) => {
    if (isLoading) return;

    setIsLoading(true);
    try {
      await onUpdate(task.id, {
        status: newStatus,
        completedAt: newStatus === 'completed' ? new Date() : undefined
      });
    } catch (error) {
      console.error('Failed to update task status:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDelete = async () => {
    if (isLoading) return;

    if (window.confirm('Are you sure you want to delete this task?')) {
      setIsLoading(true);
      try {
        await onDelete(task.id);
      } catch (error) {
        console.error('Failed to delete task:', error);
      } finally {
        setIsLoading(false);
      }
    }
  };

  const getStatusIcon = (status: TaskStatus) => {
    const iconClass = 'w-5 h-5';
    switch (status) {
      case 'completed':
        return <CheckCircle2 className={`${iconClass} text-green-600`} />;
      case 'in_progress':
        return <Clock className={`${iconClass} text-blue-600`} />;
      case 'blocked':
        return <XCircle className={`${iconClass} text-red-600`} />;
      case 'cancelled':
        return <AlertCircle className={`${iconClass} text-gray-400`} />;
      default:
        return <Circle className={`${iconClass} text-gray-400`} />;
    }
  };

  const getPriorityColor = (priority: TaskPriority) => {
    switch (priority) {
      case 'urgent':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'high':
        return 'bg-orange-100 text-orange-800 border-orange-200';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'low':
        return 'bg-green-100 text-green-800 border-green-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const isCompleted = task.status === 'completed';
  const isOverdue = task.dueDate && new Date(task.dueDate) < new Date() && !isCompleted;

  const baseClasses = `
    ${isCompact ? 'p-3' : 'p-4'}
    bg-white border rounded-lg shadow-sm hover:shadow-md transition-all duration-200
    ${isCompleted ? 'opacity-75' : ''}
    ${isOverdue ? 'border-red-200' : 'border-gray-200'}
  `;

  return (
    <div className={baseClasses}>
      <div className="flex items-start space-x-3">
        {/* Status checkbox/icon */}
        <button
          onClick={() => handleStatusChange(isCompleted ? 'pending' : 'completed')}
          disabled={isLoading}
          className={`
            flex-shrink-0 mt-1 p-1 rounded-full hover:bg-gray-100
            transition-colors disabled:opacity-50 disabled:cursor-not-allowed
            ${isCompleted ? 'text-green-600' : 'text-gray-400 hover:text-gray-600'}
          `}
          aria-label={isCompleted ? 'Mark as incomplete' : 'Mark as complete'}
        >
          {getStatusIcon(task.status)}
        </button>

        {/* Task content */}
        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between">
            {/* Title and description */}
            <div className="flex-1 mr-2">
              <h3 className={`
                ${isCompact ? 'text-sm' : 'text-base'}
                font-medium text-gray-900
                ${isCompleted ? 'line-through' : ''}
              `}>
                {task.title}
              </h3>

              {task.description && !isCompact && (
                <p className="mt-1 text-sm text-gray-600 line-clamp-2">
                  {task.description}
                </p>
              )}

              {/* Tags */}
              {task.tags && task.tags.length > 0 && !isCompact && (
                <div className="mt-2 flex flex-wrap gap-1">
                  {task.tags.map((tag) => (
                    <span
                      key={tag}
                      className="inline-flex items-center px-2 py-1 rounded text-xs bg-gray-100 text-gray-700"
                    >
                      <Tag className="w-3 h-3 mr-1" />
                      {tag}
                    </span>
                  ))}
                </div>
              )}
            </div>

            {/* Actions */}
            <div className="flex items-center space-x-1 flex-shrink-0">
              <button
                onClick={() => onEdit(task)}
                disabled={isLoading}
                className="p-1 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded transition-colors disabled:opacity-50"
                aria-label="Edit task"
              >
                <Edit2 className="w-4 h-4" />
              </button>

              <button
                onClick={handleDelete}
                disabled={isLoading}
                className="p-1 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded transition-colors disabled:opacity-50"
                aria-label="Delete task"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* Metadata */}
          <div className="mt-3 flex items-center justify-between">
            <div className="flex items-center space-x-3">
              {/* Priority badge */}
              <span className={`
                inline-flex items-center px-2 py-1 rounded-full text-xs font-medium border
                ${getPriorityColor(task.priority)}
              `}>
                {task.priority}
              </span>

              {/* Due date */}
              {(task.dueDate || (task as any).due_date) && (
                <span className={`
                  inline-flex items-center text-xs
                  ${isOverdue ? 'text-red-600 font-medium' : 'text-gray-500'}
                `}>
                  <Calendar className="w-3 h-3 mr-1" />
                  {(() => {
                    try {
                      const dateStr = task.dueDate || (task as any).due_date;
                      const date = new Date(dateStr);
                      return isNaN(date.getTime()) ? 'N/A' : format(date, 'MMM d, yyyy');
                    } catch {
                      return 'N/A';
                    }
                  })()}
                  {isOverdue && ' (Overdue)'}
                </span>
              )}

              {/* Estimated time */}
              {task.estimatedTime && !isCompact && (
                <span className="text-xs text-gray-500">
                  {task.estimatedTime}min
                </span>
              )}
            </div>

            {/* Creation date */}
            <span className="text-xs text-gray-400">
              {(() => {
                try {
                  const dateStr = (task as any).created_at || task.createdAt;
                  if (!dateStr) return 'N/A';
                  const date = new Date(dateStr);
                  return isNaN(date.getTime()) ? 'N/A' : format(date, 'MMM d');
                } catch {
                  return 'N/A';
                }
              })()}
            </span>
          </div>
        </div>
      </div>

      {/* Loading overlay */}
      {isLoading && (
        <div className="absolute inset-0 bg-white bg-opacity-50 rounded-lg flex items-center justify-center">
          <div className="w-6 h-6 border-2 border-blue-600 border-t-transparent rounded-full animate-spin" />
        </div>
      )}
    </div>
  );
}

/**
 * Compact version of TaskItem for list views
 */
export function CompactTaskItem(props: Omit<TaskItemProps, 'isCompact'>) {
  return <TaskItem {...props} isCompact={true} />;
}

/**
 * Grid version of TaskItem for card views
 */
export function GridTaskItem(props: Omit<TaskItemProps, 'isCompact'>) {
  return (
    <div className="h-full">
      <TaskItem {...props} isCompact={false} />
    </div>
  );
}