'use client';

import { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/auth-provider';
import { taskAPI } from '@/lib/api';
import { Task, CreateTaskDTO, UpdateTaskDTO } from '@/lib/types';
import { ChatWidget } from './chat-widget';
import './dashboard.css';

function getGreeting() {
  const h = new Date().getHours();
  if (h < 12) return 'Good morning';
  if (h < 17) return 'Good afternoon';
  return 'Good evening';
}

function getDateString() {
  return new Date().toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' });
}

function getPriorityLabel(priority: string) {
  const map: Record<string, { cls: string; label: string }> = {
    urgent: { cls: 'ptag ptag-urgent', label: 'Urgent' },
    high:   { cls: 'ptag ptag-high', label: 'High' },
    medium: { cls: 'ptag ptag-medium', label: 'Med' },
    low:    { cls: 'ptag ptag-low', label: 'Low' },
  };
  const p = map[priority] || map.medium;
  return <span className={p.cls}>{p.label}</span>;
}

function TaskRow({ task, onToggle, onDelete }: {
  task: Task;
  onToggle: (id: string) => void;
  onDelete: (id: string) => void;
}) {
  const isDone = task.status === 'completed';
  return (
    <div className="task-row">
      <button
        className={`task-cb${isDone ? ' checked' : ''}`}
        onClick={() => onToggle(task.id)}
      >
        {isDone && (
          <svg viewBox="0 0 10 8" width="10" height="8" fill="none">
            <polyline
              points="1,4 3.5,6.5 9,1"
              stroke="oklch(36% 0.15 142)"
              strokeWidth="1.75"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        )}
      </button>
      <span className={`task-label${isDone ? ' done' : ''}`}>{task.title}</span>
      <div className="task-meta">
        {task.dueDate && (
          <span className="task-time">
            {new Date(task.dueDate).toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' })}
          </span>
        )}
        {getPriorityLabel(task.priority)}
      </div>
      <button className="task-delete" onClick={() => onDelete(task.id)} title="Delete task">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <polyline points="3 6 5 6 21 6"></polyline>
          <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
        </svg>
      </button>
    </div>
  );
}

function Sidebar({ pendingCount, userName, onLogout }: {
  pendingCount: number;
  userName: string;
  onLogout: () => void;
}) {
  const initial = userName ? userName.charAt(0).toUpperCase() : 'U';

  return (
    <aside className="dash-sidebar">
      <div className="sidebar-top">
        <a className="sidebar-logo" href="/">Taska<span>.</span></a>
      </div>

      <div className="sidebar-nav">
        <div className="nav-item active">
          <span className="nav-icon">
            <svg viewBox="0 0 24 24">
              <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
              <line x1="16" y1="2" x2="16" y2="6"></line>
              <line x1="8" y1="2" x2="8" y2="6"></line>
              <line x1="3" y1="10" x2="21" y2="10"></line>
            </svg>
          </span>
          My Tasks
          {pendingCount > 0 && <span className="nav-badge">{pendingCount}</span>}
        </div>
      </div>

      <div className="sidebar-bottom">
        <div className="user-row" onClick={onLogout} title="Sign out">
          <div className="user-av">{initial}</div>
          <div>
            <div className="user-name">{userName}</div>
            <div className="user-plan">Sign out</div>
          </div>
        </div>
      </div>
    </aside>
  );
}

export default function Dashboard() {
  const { user, isAuthenticated, isLoading: authLoading, logout } = useAuth();
  const router = useRouter();
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [newTaskTitle, setNewTaskTitle] = useState('');
  const [isAddingTask, setIsAddingTask] = useState(false);

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push('/auth/signin');
      return;
    }
    if (isAuthenticated) {
      loadTasks();
    }
  }, [isAuthenticated, authLoading]);

  const loadTasks = async () => {
    try {
      setLoading(true);
      const { tasks } = await taskAPI.getTasks();
      setTasks(tasks);
    } catch (error) {
      console.error('Failed to load tasks:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleToggle = useCallback(async (id: string) => {
    const task = tasks.find(t => t.id === id);
    if (!task) return;
    const newStatus = task.status === 'completed' ? 'pending' : 'completed';
    setTasks(prev => prev.map(t => t.id === id ? { ...t, status: newStatus as any } : t));
    try {
      await taskAPI.updateTask(id, { status: newStatus as any });
    } catch {
      setTasks(prev => prev.map(t => t.id === id ? { ...t, status: task.status } : t));
    }
  }, [tasks]);

  const handleDelete = useCallback(async (id: string) => {
    const prev = tasks;
    setTasks(t => t.filter(task => task.id !== id));
    try {
      await taskAPI.deleteTask(id);
    } catch {
      setTasks(prev);
    }
  }, [tasks]);

  const handleAddTask = async (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key !== 'Enter' || !newTaskTitle.trim()) return;
    const title = newTaskTitle.trim();
    setNewTaskTitle('');
    setIsAddingTask(false);
    try {
      const newTask = await taskAPI.createTask({ title, priority: 'medium' });
      setTasks(prev => [newTask, ...prev]);
    } catch (error) {
      console.error('Failed to create task:', error);
    }
  };

  const handleLogout = async () => {
    await logout();
    router.push('/');
  };

  const userName = user?.user_metadata?.full_name || user?.email?.split('@')[0] || 'User';
  const firstName = userName.split(' ')[0];

  const doneCount = tasks.filter(t => t.status === 'completed').length;
  const total = tasks.length;
  const pct = total > 0 ? Math.round((doneCount / total) * 100) : 0;
  const pendingCount = total - doneCount;

  const pendingTasks = tasks.filter(t => t.status !== 'completed');
  const completedTasks = tasks.filter(t => t.status === 'completed');

  if (authLoading) {
    return (
      <div className="dashboard-app" style={{ alignItems: 'center', justifyContent: 'center' }}>
        <p style={{ color: 'var(--fg-3)' }}>Loading...</p>
      </div>
    );
  }

  return (
    <div className="dashboard-app">
      <Sidebar pendingCount={pendingCount} userName={userName} onLogout={handleLogout} />

      <main className="dash-main">
        <div className="main-header">
          <div className="main-date">{getDateString()}</div>
          <div className="main-greeting">{getGreeting()}, {firstName}</div>
          {total > 0 && (
            <div className="progress-row">
              <span className="progress-label">{doneCount} of {total} tasks complete</span>
              <div className="progress-track">
                <div className="progress-fill" style={{ width: `${pct}%` }}></div>
              </div>
              <span className="progress-pct">{pct}%</span>
            </div>
          )}
        </div>

        <div className="task-board">
          {loading ? (
            <div className="empty-state">
              <p>Loading tasks...</p>
            </div>
          ) : (
            <>
              {pendingTasks.length > 0 && (
                <div className="task-section">
                  <div className="section-hd">Pending</div>
                  {pendingTasks.map(task => (
                    <TaskRow key={task.id} task={task} onToggle={handleToggle} onDelete={handleDelete} />
                  ))}
                </div>
              )}

              {completedTasks.length > 0 && (
                <div className="task-section">
                  <div className="section-hd">Completed</div>
                  {completedTasks.map(task => (
                    <TaskRow key={task.id} task={task} onToggle={handleToggle} onDelete={handleDelete} />
                  ))}
                </div>
              )}

              {tasks.length === 0 && (
                <div className="empty-state">
                  <div className="empty-state-icon">&#10003;</div>
                  <h3>No tasks yet</h3>
                  <p>Click below to add your first task.</p>
                </div>
              )}

              <div className="add-task-row" onClick={() => setIsAddingTask(true)}>
                {isAddingTask ? (
                  <input
                    className="add-task-input"
                    placeholder="What needs to be done? Press Enter..."
                    value={newTaskTitle}
                    onChange={e => setNewTaskTitle(e.target.value)}
                    onKeyDown={handleAddTask}
                    onBlur={() => { if (!newTaskTitle) setIsAddingTask(false); }}
                    autoFocus
                  />
                ) : (
                  <>
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <line x1="12" y1="5" x2="12" y2="19"></line>
                      <line x1="5" y1="12" x2="19" y2="12"></line>
                    </svg>
                    Add a task
                  </>
                )}
              </div>
            </>
          )}
        </div>
      </main>

      <ChatWidget onTaskCreated={loadTasks} />
    </div>
  );
}
