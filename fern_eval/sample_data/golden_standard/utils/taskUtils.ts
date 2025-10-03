// Utility functions for the task management application

import { Task, TaskStatus, TaskPriority } from '../types';

/**
 * Calculate task statistics for dashboard
 */
export const calculateTaskStats = (tasks: Task[]) => {
  const totalTasks = tasks.length;
  const completedTasks = tasks.filter(t => t.status === 'completed').length;
  const inProgressTasks = tasks.filter(t => t.status === 'in-progress').length;
  const overdueTasks = tasks.filter(t =>
    new Date(t.dueDate) < new Date() && t.status !== 'completed'
  ).length;
  const completionRate = totalTasks > 0 ? (completedTasks / totalTasks) * 100 : 0;

  return {
    totalTasks,
    completedTasks,
    inProgressTasks,
    overdueTasks,
    completionRate
  };
};

/**
 * Sort tasks by priority and due date
 */
export const sortTasksByPriority = (tasks: Task[]): Task[] => {
  const priorityOrder: Record<TaskPriority, number> = {
    urgent: 4,
    high: 3,
    medium: 2,
    low: 1
  };

  return [...tasks].sort((a, b) => {
    // First sort by priority
    const priorityDiff = priorityOrder[b.priority] - priorityOrder[a.priority];
    if (priorityDiff !== 0) return priorityDiff;

    // Then by due date
    return new Date(a.dueDate).getTime() - new Date(b.dueDate).getTime();
  });
};

/**
 * Filter tasks by status
 */
export const filterTasksByStatus = (tasks: Task[], status: TaskStatus): Task[] => {
  return tasks.filter(task => task.status === status);
};

/**
 * Search tasks by title or description
 */
export const searchTasks = (tasks: Task[], searchTerm: string): Task[] => {
  if (!searchTerm.trim()) return tasks;

  const lowercaseSearch = searchTerm.toLowerCase();
  return tasks.filter(task =>
    task.title.toLowerCase().includes(lowercaseSearch) ||
    task.description.toLowerCase().includes(lowercaseSearch) ||
    task.tags.some(tag => tag.toLowerCase().includes(lowercaseSearch))
  );
};

/**
 * Format date for display
 */
export const formatDate = (date: Date): string => {
  return new Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  }).format(date);
};

/**
 * Get relative time (e.g., "2 days ago")
 */
export const getRelativeTime = (date: Date): string => {
  const now = new Date();
  const diffInSeconds = Math.floor((now.getTime() - date.getTime()) / 1000);

  if (diffInSeconds < 60) return 'just now';
  if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)} minutes ago`;
  if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)} hours ago`;
  if (diffInSeconds < 2592000) return `${Math.floor(diffInSeconds / 86400)} days ago`;

  return formatDate(date);
};

/**
 * Validate task form data
 */
export const validateTaskForm = (data: any): string[] => {
  const errors: string[] = [];

  if (!data.title?.trim()) {
    errors.push('Task title is required');
  }

  if (!data.description?.trim()) {
    errors.push('Task description is required');
  }

  if (!data.assignee?.trim()) {
    errors.push('Assignee is required');
  }

  if (!data.dueDate) {
    errors.push('Due date is required');
  } else if (new Date(data.dueDate) < new Date()) {
    errors.push('Due date cannot be in the past');
  }

  if (data.estimatedHours && (data.estimatedHours < 0 || data.estimatedHours > 1000)) {
    errors.push('Estimated hours must be between 0 and 1000');
  }

  return errors;
};

/**
 * Generate unique ID for new tasks
 */
export const generateTaskId = (): string => {
  return `task_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
};

/**
 * Calculate completion percentage based on hours
 */
export const calculateCompletionPercentage = (completedHours: number, estimatedHours: number): number => {
  if (!estimatedHours || estimatedHours === 0) return 0;
  return Math.min(100, (completedHours / estimatedHours) * 100);
};

/**
 * Group tasks by assignee
 */
export const groupTasksByAssignee = (tasks: Task[]): Record<string, Task[]> => {
  return tasks.reduce((acc, task) => {
    if (!acc[task.assignee]) {
      acc[task.assignee] = [];
    }
    acc[task.assignee].push(task);
    return acc;
  }, {} as Record<string, Task[]>);
};

/**
 * Get tasks due within specified days
 */
export const getTasksDueSoon = (tasks: Task[], days: number = 3): Task[] => {
  const futureDate = new Date();
  futureDate.setDate(futureDate.getDate() + days);

  return tasks.filter(task =>
    task.status !== 'completed' &&
    new Date(task.dueDate) <= futureDate &&
    new Date(task.dueDate) >= new Date()
  );
};
