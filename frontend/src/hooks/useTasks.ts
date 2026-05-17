'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useCallback } from 'react';
import { Task, CreateTaskDTO, UpdateTaskDTO, TaskQueryParams, UseTasksReturn } from '@/lib/types';
import taskAPI from '@/lib/api';

export const taskKeys = {
  all: ['tasks'] as const,
  lists: () => [...taskKeys.all, 'list'] as const,
  list: (params: TaskQueryParams = {}) => [...taskKeys.lists(), params] as const,
  details: () => [...taskKeys.all, 'detail'] as const,
  detail: (id: string) => [...taskKeys.details(), id] as const,
  stats: () => [...taskKeys.all, 'stats'] as const,
};

export function useTasks(params: TaskQueryParams = {}): UseTasksReturn {
  const queryClient = useQueryClient();

  const { data, isLoading, error, refetch } = useQuery({
    queryKey: taskKeys.list(params),
    queryFn: () => taskAPI.getTasks(),
    staleTime: 5 * 60 * 1000,
    refetchOnWindowFocus: true,
  });

  const tasks = data?.tasks || [];

  const createTaskMutation = useMutation({
    mutationFn: (taskData: CreateTaskDTO) => taskAPI.createTask(taskData),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: taskKeys.lists() });
    },
  });

  const updateTaskMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: UpdateTaskDTO }) =>
      taskAPI.updateTask(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: taskKeys.lists() });
    },
  });

  const deleteTaskMutation = useMutation({
    mutationFn: (id: string) => taskAPI.deleteTask(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: taskKeys.lists() });
    },
  });

  const bulkUpdateMutation = useMutation({
    mutationFn: ({ taskIds, data }: { taskIds: string[]; data: UpdateTaskDTO }) =>
      Promise.all(taskIds.map(id => taskAPI.updateTask(id, data))),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: taskKeys.lists() });
    },
  });

  const bulkDeleteMutation = useMutation({
    mutationFn: (taskIds: string[]) =>
      Promise.all(taskIds.map(id => taskAPI.deleteTask(id))),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: taskKeys.lists() });
    },
  });

  return {
    tasks,
    isLoading,
    error: error?.message || null,
    refetch,
    createTask: useCallback((d: CreateTaskDTO) => createTaskMutation.mutateAsync(d), [createTaskMutation]),
    updateTask: useCallback((id: string, d: UpdateTaskDTO) => updateTaskMutation.mutateAsync({ id, data: d }), [updateTaskMutation]),
    deleteTask: useCallback((id: string) => deleteTaskMutation.mutateAsync(id), [deleteTaskMutation]),
    bulkUpdate: useCallback((ids: string[], d: UpdateTaskDTO) => bulkUpdateMutation.mutateAsync({ taskIds: ids, data: d }), [bulkUpdateMutation]),
    bulkDelete: useCallback((ids: string[]) => bulkDeleteMutation.mutateAsync(ids), [bulkDeleteMutation]),
  };
}
