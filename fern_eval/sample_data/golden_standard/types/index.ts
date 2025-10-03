// Types for the Task Management Dashboard

export interface Task {
  id: string;
  title: string;
  description: string;
  status: TaskStatus;
  priority: TaskPriority;
  assignee: string;
  dueDate: Date;
  createdAt: Date;
  updatedAt: Date;
  tags: string[];
  estimatedHours?: number;
  completedHours?: number;
}

export type TaskStatus = 'todo' | 'in-progress' | 'review' | 'completed';
export type TaskPriority = 'low' | 'medium' | 'high' | 'urgent';

export interface User {
  id: string;
  name: string;
  email: string;
  avatar?: string;
  role: 'admin' | 'manager' | 'developer' | 'designer';
}

export interface Project {
  id: string;
  name: string;
  description: string;
  tasks: Task[];
  members: User[];
  createdAt: Date;
  deadline?: Date;
}

export interface TaskFormData {
  title: string;
  description: string;
  priority: TaskPriority;
  assignee: string;
  dueDate: string;
  tags: string[];
  estimatedHours?: number;
}

export interface DashboardStats {
  totalTasks: number;
  completedTasks: number;
  inProgressTasks: number;
  overdueTasks: number;
  completionRate: number;
}
