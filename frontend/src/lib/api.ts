import { createClient } from '@/lib/supabase/client';
import { Task, CreateTaskDTO, UpdateTaskDTO } from './types';

export class TaskAPI {
  private supabase = createClient();

  async getTasks(): Promise<{ tasks: Task[]; count: number }> {
    const { data: { user } } = await this.supabase.auth.getUser();
    if (!user) throw new Error('Not authenticated');

    const { data, error, count } = await this.supabase
      .from('tasks')
      .select('*', { count: 'exact' })
      .eq('user_id', user.id)
      .order('created_at', { ascending: false });

    if (error) throw new Error(error.message);

    const tasks: Task[] = (data || []).map(this.mapRow);
    return { tasks, count: count || 0 };
  }

  async createTask(taskData: CreateTaskDTO): Promise<Task> {
    const { data: { user } } = await this.supabase.auth.getUser();
    if (!user) throw new Error('Not authenticated');

    const { data, error } = await this.supabase
      .from('tasks')
      .insert({
        user_id: user.id,
        title: taskData.title,
        description: taskData.description || null,
        priority: taskData.priority || 'medium',
        status: 'pending',
        due_date: taskData.dueDate || null,
        tags: taskData.tags || [],
        estimated_time: taskData.estimatedTime || null,
      })
      .select()
      .single();

    if (error) throw new Error(error.message);
    return this.mapRow(data);
  }

  async updateTask(id: string, updates: UpdateTaskDTO): Promise<Task> {
    const row: Record<string, unknown> = {};
    if (updates.title !== undefined) row.title = updates.title;
    if (updates.description !== undefined) row.description = updates.description;
    if (updates.status !== undefined) {
      row.status = updates.status;
      if (updates.status === 'completed') row.completed_at = new Date().toISOString();
    }
    if (updates.priority !== undefined) row.priority = updates.priority;
    if (updates.dueDate !== undefined) row.due_date = updates.dueDate;
    if (updates.tags !== undefined) row.tags = updates.tags;
    if (updates.estimatedTime !== undefined) row.estimated_time = updates.estimatedTime;
    if (updates.actualTime !== undefined) row.actual_time = updates.actualTime;
    row.updated_at = new Date().toISOString();

    const { data, error } = await this.supabase
      .from('tasks')
      .update(row)
      .eq('id', id)
      .select()
      .single();

    if (error) throw new Error(error.message);
    return this.mapRow(data);
  }

  async deleteTask(id: string): Promise<void> {
    const { error } = await this.supabase
      .from('tasks')
      .delete()
      .eq('id', id);

    if (error) throw new Error(error.message);
  }

  private mapRow(row: any): Task {
    return {
      id: row.id,
      title: row.title,
      description: row.description,
      status: row.status,
      priority: row.priority,
      dueDate: row.due_date ? new Date(row.due_date) : undefined,
      createdAt: new Date(row.created_at),
      updatedAt: new Date(row.updated_at),
      completedAt: row.completed_at ? new Date(row.completed_at) : undefined,
      tags: row.tags || [],
      assignedTo: row.assigned_to,
      estimatedTime: row.estimated_time,
      actualTime: row.actual_time,
    };
  }
}

export const taskAPI = new TaskAPI();
export default taskAPI;
