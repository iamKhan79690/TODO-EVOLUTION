'use client';

import { useState, useEffect } from 'react';
import TaskForm from '@/components/tasks/TaskForm';
import TaskItem from '@/components/tasks/TaskItem';
import { LoadingSpinner } from '@/components/ui/loading-spinner';
import { taskAPI } from '@/lib/api';
import { Task, CreateTaskDTO, UpdateTaskDTO } from '@/lib/types';

export default function Dashboard() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [editingTask, setEditingTask] = useState<Task | null>(null);

  useEffect(() => {
    loadTasks();
  }, []);

  const loadTasks = async () => {
    try {
      setLoading(true);
      const response = await taskAPI.getTasks();
      // Backend returns { tasks: [...], count, user_id }
      // Access .tasks or fallback to .data or empty array
      const taskList = (response as any).tasks || (response as any).data || [];
      setTasks(taskList);
    } catch (error) {
      console.error('Failed to load tasks:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateTask = async (taskData: CreateTaskDTO | UpdateTaskDTO) => {
    try {
      const response = await taskAPI.createTask(taskData as CreateTaskDTO);
      // Backend returns task object directly, or might be in .data
      const newTask = (response as any).data || response;
      if (newTask && newTask.id) {
        setTasks(prev => [newTask, ...prev]);
      }
      setShowCreateForm(false);
    } catch (error) {
      console.error('Failed to create task:', error);
    }
  };

  const handleUpdateTask = async (taskId: string, updates: Partial<Task>) => {
    try {
      await taskAPI.updateTask(taskId, updates as UpdateTaskDTO);
      setTasks(prev =>
        prev.map(task =>
          task.id === taskId ? { ...task, ...updates } : task
        )
      );
      setEditingTask(null);
    } catch (error) {
      console.error('Failed to update task:', error);
    }
  };

  const handleDeleteTask = async (taskId: string) => {
    try {
      await taskAPI.deleteTask(taskId);
      setTasks(prev => prev.filter(task => task.id !== taskId));
    } catch (error) {
      console.error('Failed to delete task:', error);
    }
  };

  const handleEditTask = (task: Task) => {
    setEditingTask(task);
    setShowCreateForm(false);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <LoadingSpinner />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto p-6">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Task Dashboard</h1>
          <p className="text-gray-600">Manage your tasks and stay productive</p>
        </div>

        <div className="mb-6">
          <button
            onClick={() => {
              setShowCreateForm(!showCreateForm);
              setEditingTask(null);
            }}
            className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-medium transition-colors"
          >
            {showCreateForm ? 'Cancel' : 'Create New Task'}
          </button>
        </div>

        {showCreateForm && (
          <div className="mb-8">
            <TaskForm
              onSubmit={handleCreateTask}
              onCancel={() => setShowCreateForm(false)}
              mode="create"
            />
          </div>
        )}

        {editingTask && (
          <div className="mb-8">
            <TaskForm
              task={editingTask}
              onSubmit={async (data) => {
                await handleUpdateTask(editingTask.id, data as Partial<Task>);
              }}
              onCancel={() => setEditingTask(null)}
              mode="edit"
            />
          </div>
        )}

        <div className="space-y-4">
          {tasks.length === 0 ? (
            <div className="text-center py-12 bg-white rounded-lg shadow">
              <h3 className="text-lg font-medium text-gray-900 mb-2">No tasks yet</h3>
              <p className="text-gray-600">Create your first task to get started!</p>
            </div>
          ) : (
            tasks.map(task => (
              <TaskItem
                key={task.id}
                task={task}
                onUpdate={handleUpdateTask}
                onDelete={handleDeleteTask}
                onEdit={handleEditTask}
              />
            ))
          )}
        </div>
      </div>
    </div>
  );
}