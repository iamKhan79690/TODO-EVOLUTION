'use client';

import React, { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Task, TaskPriority, CreateTaskDTO, UpdateTaskDTO } from '@/lib/types';
import { format } from 'date-fns';
import {
  Plus,
  X,
  Calendar,
  Clock,
  Flag
} from 'lucide-react';

// Validation schema
const taskSchema = z.object({
  title: z.string().min(1, 'Title is required').max(200, 'Title must be less than 200 characters'),
  description: z.string().max(2000, 'Description must be less than 2000 characters').optional(),
  priority: z.enum(['low', 'medium', 'high', 'urgent']).default('medium'),
  dueDate: z.string().optional(),
  tags: z.array(z.string()).optional(),
  assignedTo: z.string().optional(),
  estimatedTime: z.number().min(0, 'Estimated time must be positive').optional(),
});

type TaskFormData = z.infer<typeof taskSchema>;

interface TaskFormProps {
  task?: Task | null;
  onSubmit: (data: CreateTaskDTO | UpdateTaskDTO) => Promise<void>;
  onCancel: () => void;
  isLoading?: boolean;
  mode?: 'create' | 'edit';
}

/**
 * Task creation and editing form component with validation
 */
export default function TaskForm({
  task,
  onSubmit,
  onCancel,
  isLoading = false,
  mode = 'create'
}: TaskFormProps) {
  const [newTag, setNewTag] = useState('');
  const [tags, setTags] = useState<string[]>(task?.tags || []);

  const {
    register,
    handleSubmit,
    formState: { errors, isDirty },
    setValue,
    watch,
    reset,
  } = useForm<TaskFormData>({
    resolver: zodResolver(taskSchema),
    defaultValues: {
      title: task?.title || '',
      description: task?.description || '',
      priority: task?.priority || 'medium',
      dueDate: task?.dueDate ? format(new Date(task.dueDate), 'yyyy-MM-dd') : '',
      tags: task?.tags || [],
      assignedTo: task?.assignedTo || '',
      estimatedTime: task?.estimatedTime || undefined,
    },
  });

  // Update form when task prop changes
  useEffect(() => {
    if (task) {
      reset({
        title: task.title,
        description: task.description || '',
        priority: task.priority,
        dueDate: task.dueDate ? format(new Date(task.dueDate), 'yyyy-MM-dd') : '',
        tags: task.tags || [],
        assignedTo: task.assignedTo || '',
        estimatedTime: task.estimatedTime || undefined,
      });
      setTags(task.tags || []);
    }
  }, [task, reset]);

  const handleFormSubmit = async (data: TaskFormData) => {
    try {
      const submitData = {
        ...data,
        tags: tags.length > 0 ? tags : undefined,
        dueDate: data.dueDate || undefined,
        estimatedTime: data.estimatedTime || undefined,
      };

      await onSubmit(submitData);
      if (mode === 'create') {
        reset(); // Reset form only for create mode
        setTags([]);
        setNewTag('');
      }
    } catch (error) {
      console.error('Failed to save task:', error);
    }
  };

  const addTag = () => {
    if (newTag.trim() && !tags.includes(newTag.trim())) {
      setTags([...tags, newTag.trim()]);
      setNewTag('');
    }
  };

  const removeTag = (tagToRemove: string) => {
    setTags(tags.filter(tag => tag !== tagToRemove));
  };

  const handleTagKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      addTag();
    }
  };

  const selectedPriority = watch('priority');
  const hasChanges = isDirty || tags.length !== (task?.tags?.length || 0);

  return (
    <div className="bg-white rounded-lg shadow-lg border border-gray-200">
      <div className="px-6 py-4 border-b border-gray-200">
        <h2 className="text-lg font-semibold text-gray-900">
          {mode === 'create' ? 'Create New Task' : 'Edit Task'}
        </h2>
      </div>

      <form onSubmit={handleSubmit(handleFormSubmit)} className="p-6 space-y-6">
        {/* Title */}
        <div>
          <label htmlFor="title" className="block text-sm font-medium text-gray-700 mb-1">
            Title <span className="text-red-500">*</span>
          </label>
          <input
            {...register('title')}
            type="text"
            id="title"
            className={`
              w-full px-3 py-2 border rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500
              ${errors.title ? 'border-red-300' : 'border-gray-300'}
            `}
            placeholder="Enter task title..."
          />
          {errors.title && (
            <p className="mt-1 text-sm text-red-600">{errors.title.message}</p>
          )}
        </div>

        {/* Description */}
        <div>
          <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-1">
            Description
          </label>
          <textarea
            {...register('description')}
            id="description"
            rows={3}
            className={`
              w-full px-3 py-2 border rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500
              ${errors.description ? 'border-red-300' : 'border-gray-300'}
            `}
            placeholder="Enter task description..."
          />
          {errors.description && (
            <p className="mt-1 text-sm text-red-600">{errors.description.message}</p>
          )}
        </div>

        {/* Priority and Due Date */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Priority */}
          <div>
            <label htmlFor="priority" className="block text-sm font-medium text-gray-700 mb-1">
              <Flag className="inline w-4 h-4 mr-1" />
              Priority
            </label>
            <select
              {...register('priority')}
              id="priority"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
              <option value="urgent">Urgent</option>
            </select>
          </div>

          {/* Due Date */}
          <div>
            <label htmlFor="dueDate" className="block text-sm font-medium text-gray-700 mb-1">
              <Calendar className="inline w-4 h-4 mr-1" />
              Due Date
            </label>
            <input
              {...register('dueDate')}
              type="date"
              id="dueDate"
              className={`
                w-full px-3 py-2 border rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500
                ${errors.dueDate ? 'border-red-300' : 'border-gray-300'}
              `}
            />
            {errors.dueDate && (
              <p className="mt-1 text-sm text-red-600">{errors.dueDate.message}</p>
            )}
          </div>
        </div>

        {/* Estimated Time */}
        <div>
          <label htmlFor="estimatedTime" className="block text-sm font-medium text-gray-700 mb-1">
            <Clock className="inline w-4 h-4 mr-1" />
            Estimated Time (minutes)
          </label>
          <input
            {...register('estimatedTime', { valueAsNumber: true })}
            type="number"
            id="estimatedTime"
            min="0"
            className={`
              w-full px-3 py-2 border rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500
              ${errors.estimatedTime ? 'border-red-300' : 'border-gray-300'}
            `}
            placeholder="Enter estimated time in minutes..."
          />
          {errors.estimatedTime && (
            <p className="mt-1 text-sm text-red-600">{errors.estimatedTime.message}</p>
          )}
        </div>

        {/* Tags */}
        <div>
          <label htmlFor="tags" className="block text-sm font-medium text-gray-700 mb-1">
            Tags
          </label>
          <div className="space-y-2">
            <div className="flex gap-2">
              <input
                type="text"
                value={newTag}
                onChange={(e) => setNewTag(e.target.value)}
                onKeyPress={handleTagKeyPress}
                placeholder="Add a tag..."
                className="flex-1 px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
              <button
                type="button"
                onClick={addTag}
                className="px-3 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg transition-colors"
              >
                <Plus className="w-4 h-4" />
              </button>
            </div>
            {tags.length > 0 && (
              <div className="flex flex-wrap gap-2">
                {tags.map((tag) => (
                  <span
                    key={tag}
                    className="inline-flex items-center px-3 py-1 rounded-full text-sm bg-blue-100 text-blue-800"
                  >
                    {tag}
                    <button
                      type="button"
                      onClick={() => removeTag(tag)}
                      className="ml-1 hover:text-blue-600"
                    >
                      <X className="w-3 h-3" />
                    </button>
                  </span>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Form Actions */}
        <div className="flex justify-end space-x-3 pt-6 border-t border-gray-200">
          <button
            type="button"
            onClick={onCancel}
            disabled={isLoading}
            className="px-4 py-2 text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={isLoading || !hasChanges}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
          >
            {isLoading ? (
              <>
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2" />
                {mode === 'create' ? 'Creating...' : 'Updating...'}
              </>
            ) : (
              <>
                {mode === 'create' ? <Plus className="w-4 h-4 mr-2" /> : null}
                {mode === 'create' ? 'Create Task' : 'Update Task'}
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
}