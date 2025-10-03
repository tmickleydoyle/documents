// Task utility functions
import { TaskItem, TaskStatus, TaskPriority } from '../types';

/**
 * Calculate dashboard statistics
 */
export const calculateStats = (tasks: TaskItem[]) => {
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
export const sortTasksByPriority = (tasks: TaskItem[]): TaskItem[] => {
  const priorityWeights: Record<TaskPriority, number> = {
    urgent: 4,
    high: 3,
    medium: 2,
    low: 1
  };

  return [...tasks].sort((a, b) => {
    // Sort by priority first
    const priorityDiff = priorityWeights[b.priority] - priorityWeights[a.priority];
    if (priorityDiff !== 0) return priorityDiff;

    // Then by due date
    return new Date(a.dueDate).getTime() - new Date(b.dueDate).getTime();
  });
};

/**
 * Filter tasks by status
 */
export const filterTasksByStatus = (tasks: TaskItem[], status: TaskStatus): TaskItem[] => {
  return tasks.filter(task => task.status === status);
};

/**
 * Search tasks
 */
export const searchTasks = (tasks: TaskItem[], searchTerm: string): TaskItem[] => {
  if (!searchTerm.trim()) return tasks;

  const searchLower = searchTerm.toLowerCase();
  return tasks.filter(task =>
    task.title.toLowerCase().includes(searchLower) ||
    task.description.toLowerCase().includes(searchLower) ||
    task.tags.some(tag => tag.toLowerCase().includes(searchLower))
  );
};

/**
 * Format date for display
 */
export const formatDisplayDate = (date: Date): string => {
  return new Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  }).format(date);
};

/**
 * Get relative time
 */
export const getRelativeTime = (date: Date): string => {
  const now = new Date();
  const diffInSeconds = Math.floor((now.getTime() - date.getTime()) / 1000);

  if (diffInSeconds < 60) return 'just now';
  if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)} minutes ago`;
  if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)} hours ago`;
  if (diffInSeconds < 2592000) return `${Math.floor(diffInSeconds / 86400)} days ago`;

  return formatDisplayDate(date);
};

/**
 * Validate task form
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
 * Generate task ID
 */
export const generateTaskId = (): string => {
  return `task_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`;
};

/**
 * Calculate completion percentage
 */
export const calculateCompletionPercentage = (completedHours: number, estimatedHours: number): number => {
  if (!estimatedHours || estimatedHours === 0) return 0;
  return Math.min(100, (completedHours / estimatedHours) * 100);
};

/**
 * Group tasks by assignee
 */
export const groupTasksByAssignee = (tasks: TaskItem[]): Record<string, TaskItem[]> => {
  return tasks.reduce((acc, task) => {
    if (!acc[task.assignee]) {
      acc[task.assignee] = [];
    }
    acc[task.assignee].push(task);
    return acc;
  }, {} as Record<string, TaskItem[]>);
};

/**
 * Get tasks due soon
 */
export const getTasksDueSoon = (tasks: TaskItem[], days: number = 3): TaskItem[] => {
  const futureDate = new Date();
  futureDate.setDate(futureDate.getDate() + days);

  return tasks.filter(task =>
    task.status !== 'completed' &&
    new Date(task.dueDate) <= futureDate &&
    new Date(task.dueDate) >= new Date()
  );
};
