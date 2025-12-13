'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useCallback } from 'react';
import {
  Task,
  CreateTaskDTO,
  UpdateTaskDTO,
  TaskQueryParams,
  UseTasksReturn,
  TaskStatsResponse,
  ApiResponse
} from '@/lib/types';
import taskAPI from '@/lib/api';

// Query keys for React Query
export const taskKeys = {
  all: ['tasks'] as const,
  lists: () => [...taskKeys.all, 'list'] as const,
  list: (params: TaskQueryParams = {}) => [...taskKeys.lists(), params] as const,
  details: () => [...taskKeys.all, 'detail'] as const,
  detail: (id: string) => [...taskKeys.details(), id] as const,
  stats: () => [...taskKeys.all, 'stats'] as const,
};

/**
 * Custom hook for task management operations
 * Provides complete CRUD functionality with optimistic updates and caching
 */
export function useTasks(params: TaskQueryParams = {}): UseTasksReturn {
  const queryClient = useQueryClient();

  // Fetch tasks with caching and background refetching
  const {
    data: response,
    isLoading,
    error,
    refetch,
  } = useQuery({
    queryKey: taskKeys.list(params),
    queryFn: () => taskAPI.getTasks(params),
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 10 * 60 * 1000, // 10 minutes
    refetchOnWindowFocus: true,
    refetchOnReconnect: true,
  });

  const tasks = response?.data || [];

  // Create task mutation with optimistic update
  const createTaskMutation = useMutation({
    mutationFn: (taskData: CreateTaskDTO) => taskAPI.createTask(taskData),
    onMutate: async (newTask) => {
      // Cancel any in-flight queries for the tasks list
      await queryClient.cancelQueries({ queryKey: taskKeys.lists() });

      // Get the current tasks data
      const previousTasksResponse = queryClient.getQueryData(taskKeys.list(params));

      // Optimistically update the tasks list with the new task
      const optimisticTask: Task = {
        id: `temp-${Date.now()}`, // Temporary ID
        ...newTask,
        status: newTask.status || 'pending',
        priority: newTask.priority || 'medium',
        createdAt: new Date(),
        updatedAt: new Date(),
        dueDate: newTask.dueDate ? new Date(newTask.dueDate) : undefined,
      };

      queryClient.setQueryData(taskKeys.list(params), (old: any) => {
        if (!old?.data) return { data: [optimisticTask], pagination: { currentPage: 1, totalPages: 1, totalItems: 1, itemsPerPage: 20, hasNextPage: false, hasPreviousPage: false }, success: true, message: '' };
        return {
          ...old,
          data: [optimisticTask, ...old.data],
          pagination: {
            ...old.pagination,
            totalItems: old.pagination.totalItems + 1,
          },
        };
      });

      return { previousTasksResponse };
    },
    onError: (error, variables, context) => {
      // Rollback to the previous data on error
      if (context?.previousTasksResponse) {
        queryClient.setQueryData(taskKeys.list(params), context.previousTasksResponse);
      }
    },
    onSuccess: (response) => {
      // Update the optimistic task with the real data from the server
      queryClient.setQueryData(taskKeys.list(params), (old: any) => {
        if (!old?.data) return old;
        return {
          ...old,
          data: old.data.map((task: Task) =>
            task.id.startsWith('temp-') ? response.data : task
          ),
          pagination: {
            ...old.pagination,
            totalItems: old.pagination.totalItems,
          },
        };
      });

      // Invalidate and refetch to ensure consistency
      queryClient.invalidateQueries({ queryKey: taskKeys.lists() });
      queryClient.invalidateQueries({ queryKey: taskKeys.stats() });
    },
  });

  // Update task mutation with optimistic update
  const updateTaskMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: UpdateTaskDTO }) =>
      taskAPI.updateTask(id, data),
    onMutate: async ({ id, data }) => {
      await queryClient.cancelQueries({ queryKey: taskKeys.lists() });

      const previousTasksResponse = queryClient.getQueryData(taskKeys.list(params));

      // Optimistically update the task in the list
      queryClient.setQueryData(taskKeys.list(params), (old: any) => {
        if (!old?.data) return old;
        return {
          ...old,
          data: old.data.map((task: Task) =>
            task.id === id
              ? {
                  ...task,
                  ...data,
                  updatedAt: new Date(),
                  dueDate: data.dueDate ? new Date(data.dueDate) : task.dueDate,
                }
              : task
          ),
        };
      });

      // Also update the individual task cache if it exists
      const previousTaskDetail = queryClient.getQueryData(taskKeys.detail(id));
      if (previousTaskDetail) {
        queryClient.setQueryData(taskKeys.detail(id), (old: any) => ({
          ...old,
          data: {
            ...old.data,
            ...data,
            updatedAt: new Date(),
            dueDate: data.dueDate ? new Date(data.dueDate) : old.data.dueDate,
          },
        }));
      }

      return { previousTasksResponse };
    },
    onError: (error, variables, context) => {
      if (context?.previousTasksResponse) {
        queryClient.setQueryData(taskKeys.list(params), context.previousTasksResponse);
      }
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: taskKeys.lists() });
      queryClient.invalidateQueries({ queryKey: taskKeys.stats() });
    },
  });

  // Delete task mutation with optimistic update
  const deleteTaskMutation = useMutation({
    mutationFn: (id: string) => taskAPI.deleteTask(id),
    onMutate: async (id) => {
      await queryClient.cancelQueries({ queryKey: taskKeys.lists() });

      const previousTasksResponse = queryClient.getQueryData(taskKeys.list(params));

      // Optimistically remove the task from the list
      queryClient.setQueryData(taskKeys.list(params), (old: any) => {
        if (!old?.data) return old;
        return {
          ...old,
          data: old.data.filter((task: Task) => task.id !== id),
          pagination: {
            ...old.pagination,
            totalItems: Math.max(0, old.pagination.totalItems - 1),
          },
        };
      });

      return { previousTasksResponse };
    },
    onError: (error, variables, context) => {
      if (context?.previousTasksResponse) {
        queryClient.setQueryData(taskKeys.list(params), context.previousTasksResponse);
      }
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: taskKeys.lists() });
      queryClient.invalidateQueries({ queryKey: taskKeys.stats() });
    },
  });

  // Bulk update mutation
  const bulkUpdateMutation = useMutation({
    mutationFn: ({ taskIds, data }: { taskIds: string[]; data: UpdateTaskDTO }) =>
      taskAPI.bulkUpdate(taskIds, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: taskKeys.lists() });
      queryClient.invalidateQueries({ queryKey: taskKeys.stats() });
    },
  });

  // Bulk delete mutation
  const bulkDeleteMutation = useMutation({
    mutationFn: (taskIds: string[]) => taskAPI.bulkDelete(taskIds),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: taskKeys.lists() });
      queryClient.invalidateQueries({ queryKey: taskKeys.stats() });
    },
  });

  // Wrapper functions for easier usage
  const createTask = useCallback(
    async (taskData: CreateTaskDTO) => {
      return createTaskMutation.mutateAsync(taskData);
    },
    [createTaskMutation]
  );

  const updateTask = useCallback(
    async (id: string, data: UpdateTaskDTO) => {
      return updateTaskMutation.mutateAsync({ id, data });
    },
    [updateTaskMutation]
  );

  const deleteTask = useCallback(
    async (id: string) => {
      return deleteTaskMutation.mutateAsync(id);
    },
    [deleteTaskMutation]
  );

  const bulkUpdate = useCallback(
    async (taskIds: string[], data: UpdateTaskDTO) => {
      return bulkUpdateMutation.mutateAsync({ taskIds, data });
    },
    [bulkUpdateMutation]
  );

  const bulkDelete = useCallback(
    async (taskIds: string[]) => {
      return bulkDeleteMutation.mutateAsync(taskIds);
    },
    [bulkDeleteMutation]
  );

  return {
    tasks,
    isLoading,
    error: error?.message || null,
    refetch,
    createTask,
    updateTask,
    deleteTask,
    bulkUpdate,
    bulkDelete,
  };
}

/**
 * Hook for getting a single task by ID
 */
export function useTask(id: string) {
  return useQuery({
    queryKey: taskKeys.detail(id),
    queryFn: () => taskAPI.getTask(id),
    enabled: !!id,
    staleTime: 5 * 60 * 1000,
  });
}

/**
 * Hook for getting task statistics
 */
export function useTaskStats(params?: {
  dateRange?: {
    from: string;
    to: string;
  };
}) {
  return useQuery({
    queryKey: taskKeys.stats(),
    queryFn: () => taskAPI.getTaskStats(params),
    staleTime: 2 * 60 * 1000, // 2 minutes for stats
    refetchInterval: 5 * 60 * 1000, // Refresh every 5 minutes
  });
}

/**
 * Hook for advanced task search
 */
export function useTaskSearch() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: taskAPI.searchTasks,
    onSuccess: (response) => {
      // Cache the search results
      queryClient.setQueryData(
        taskKeys.list({ search: 'advanced' }),
        response
      );
    },
  });
}

/**
 * Hook for task operations loading states
 */
export function useTaskLoadingStates() {
  const queryClient = useQueryClient();

  const isLoading = queryClient.isFetching({
    queryKey: taskKeys.lists(),
  });

  const isCreating = queryClient.isMutating({
    mutationKey: ['createTask'],
  });

  const isUpdating = queryClient.isMutating({
    mutationKey: ['updateTask'],
  });

  const isDeleting = queryClient.isMutating({
    mutationKey: ['deleteTask'],
  });

  return {
    isLoading: isLoading > 0,
    isCreating: isCreating > 0,
    isUpdating: isUpdating > 0,
    isDeleting: isDeleting > 0,
    isAnyMutationRunning: isCreating + isUpdating + isDeleting > 0,
  };
}

/**
 * Hook for invalidating task queries
 */
export function useInvalidateTasks() {
  const queryClient = useQueryClient();

  const invalidateTasks = useCallback(() => {
    queryClient.invalidateQueries({ queryKey: taskKeys.lists() });
    queryClient.invalidateQueries({ queryKey: taskKeys.stats() });
  }, [queryClient]);

  const invalidateTask = useCallback((id: string) => {
    queryClient.invalidateQueries({ queryKey: taskKeys.detail(id) });
  }, [queryClient]);

  return {
    invalidateTasks,
    invalidateTask,
  };
}