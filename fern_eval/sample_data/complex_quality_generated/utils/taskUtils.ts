// Task utility functions with performance optimizations
import { TaskItem, TaskStatus, TaskPriority } from '../types';

// Memoization cache for expensive operations
const memoCache = new Map<string, any>();
const CACHE_EXPIRY = 5 * 60 * 1000; // 5 minutes

// Cache entry interface
interface CacheEntry<T> {
  data: T;
  timestamp: number;
}

// Memoization decorator
function memoize<T extends (...args: any[]) => any>(
  fn: T,
  keyGenerator?: (...args: Parameters<T>) => string
): T {
  return ((...args: Parameters<T>): ReturnType<T> => {
    const key = keyGenerator ? keyGenerator(...args) : JSON.stringify(args);
    const cached = memoCache.get(key) as CacheEntry<ReturnType<T>> | undefined;
    
    if (cached && Date.now() - cached.timestamp < CACHE_EXPIRY) {
      return cached.data;
    }
    
    const result = fn(...args);
    memoCache.set(key, { data: result, timestamp: Date.now() });
    
    return result;
  }) as T;
}

// Performance monitoring
const performanceMetrics = {
  functionCalls: new Map<string, number>(),
  totalExecutionTime: new Map<string, number>(),
};

function measurePerformance<T extends (...args: any[]) => any>(
  fn: T,
  functionName: string
): T {
  return ((...args: Parameters<T>): ReturnType<T> => {
    const startTime = performance.now();
    const result = fn(...args);
    const endTime = performance.now();
    
    const calls = performanceMetrics.functionCalls.get(functionName) || 0;
    const totalTime = performanceMetrics.totalExecutionTime.get(functionName) || 0;
    
    performanceMetrics.functionCalls.set(functionName, calls + 1);
    performanceMetrics.totalExecutionTime.set(functionName, totalTime + (endTime - startTime));
    
    return result;
  }) as T;
}

// Export performance metrics for monitoring
export const getPerformanceMetrics = () => ({
  functionCalls: Object.fromEntries(performanceMetrics.functionCalls),
  totalExecutionTime: Object.fromEntries(performanceMetrics.totalExecutionTime),
  averageExecutionTime: Object.fromEntries(
    Array.from(performanceMetrics.functionCalls.entries()).map(([name, calls]) => [
      name,
      (performanceMetrics.totalExecutionTime.get(name) || 0) / calls,
    ])
  ),
});

// Clear performance metrics
export const clearPerformanceMetrics = () => {
  performanceMetrics.functionCalls.clear();
  performanceMetrics.totalExecutionTime.clear();
};

// Clear memoization cache
export const clearMemoCache = () => {
  memoCache.clear();
};

// Optimized date utilities
const dateCache = new Map<string, Date>();

const getDate = (dateInput: string | Date | number): Date => {
  if (dateInput instanceof Date) return dateInput;
  if (typeof dateInput === 'number') return new Date(dateInput);
  
  const cached = dateCache.get(dateInput);
  if (cached) return cached;
  
  const date = new Date(dateInput);
  dateCache.set(dateInput, date);
  return date;
};

// Priority weight constants for better performance
const PRIORITY_WEIGHTS: Record<TaskPriority, number> = {
  urgent: 4,
  high: 3,
  medium: 2,
  low: 1,
} as const;

// Status order for better performance
const STATUS_ORDER: Record<TaskStatus, number> = {
  'todo': 1,
  'in-progress': 2,
  'review': 3,
  'completed': 4,
} as const;

/**
 * Calculate dashboard statistics with memoization and performance optimization
 */
export const calculateStats = memoize(
  measurePerformance(
    (tasks: TaskItem[]) => {
      const now = Date.now();
      let totalTasks = 0;
      let completedTasks = 0;
      let inProgressTasks = 0;
      let overdueTasks = 0;
      
      // Single loop for better performance
      for (const task of tasks) {
        totalTasks++;
        
        switch (task.status) {
          case 'completed':
            completedTasks++;
            break;
          case 'in-progress':
            inProgressTasks++;
            break;
        }
        
        // Check overdue only for non-completed tasks
        if (task.status !== 'completed' && getDate(task.dueDate).getTime() < now) {
          overdueTasks++;
        }
      }
      
      const completionRate = totalTasks > 0 ? (completedTasks / totalTasks) * 100 : 0;
      
      return {
        totalTasks,
        completedTasks,
        inProgressTasks,
        overdueTasks,
        completionRate,
        timestamp: now,
      };
    },
    'calculateStats'
  ),
  (tasks) => `stats_${tasks.length}_${tasks.map(t => `${t.id}_${t.status}_${t.dueDate}`).join('|')}`
);

/**
 * Sort tasks by priority and due date with optimization
 */
export const sortTasksByPriority = memoize(
  measurePerformance(
    (tasks: TaskItem[]): TaskItem[] => {
      // Pre-compute dates and priorities for better performance
      const tasksWithComputedValues = tasks.map(task => ({
        task,
        priorityWeight: PRIORITY_WEIGHTS[task.priority],
        dueDateTime: getDate(task.dueDate).getTime(),
      }));
      
      return tasksWithComputedValues
        .sort((a, b) => {
          // Sort by priority first
          const priorityDiff = b.priorityWeight - a.priorityWeight;
          if (priorityDiff !== 0) return priorityDiff;
          
          // Then by due date
          return a.dueDateTime - b.dueDateTime;
        })
        .map(({ task }) => task);
    },
    'sortTasksByPriority'
  ),
  (tasks) => `priority_sort_${tasks.length}_${tasks.map(t => `${t.id}_${t.priority}_${t.dueDate}`).join('|')}`
);

/**
 * Filter tasks by status with memoization
 */
export const filterTasksByStatus = memoize(
  measurePerformance(
    (tasks: TaskItem[], status: TaskStatus): TaskItem[] => {
      const result: TaskItem[] = [];
      
      // Use for loop for better performance than filter
      for (let i = 0; i < tasks.length; i++) {
        if (tasks[i].status === status) {
          result.push(tasks[i]);
        }
      }
      
      return result;
    },
    'filterTasksByStatus'
  ),
  (tasks, status) => `status_filter_${status}_${tasks.length}_${tasks.map(t => `${t.id}_${t.status}`).join('|')}`
);

/**
 * Search tasks with optimized string matching and memoization
 */
export const searchTasks = memoize(
  measurePerformance(
    (tasks: TaskItem[], searchTerm: string): TaskItem[] => {
      const trimmedTerm = searchTerm.trim();
      if (!trimmedTerm) return tasks;
      
      const searchLower = trimmedTerm.toLowerCase();
      const result: TaskItem[] = [];
      
      // Pre-compile regex for better performance on large datasets
      const searchRegex = new RegExp(searchLower.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'i');
      
      for (const task of tasks) {
        // Use regex test for better performance
        if (
          searchRegex.test(task.title) ||
          searchRegex.test(task.description) ||
          task.tags.some(tag => searchRegex.test(tag))
        ) {
          result.push(task);
        }
      }
      
      return result;
    },
    'searchTasks'
  ),
  (tasks, searchTerm) => `search_${searchTerm.toLowerCase()}_${tasks.length}_${tasks.map(t => t.id).join('|')}`
);

/**
 * Format date for display with caching
 */
const dateFormatter = new Intl.DateTimeFormat('en-US', {
  year: 'numeric',
  month: 'short',
  day: 'numeric'
});

export const formatDisplayDate = memoize(
  measurePerformance(
    (date: Date | string | number): string => {
      const dateObj = getDate(date);
      return dateFormatter.format(dateObj);
    },
    'formatDisplayDate'
  ),
  (date) => `format_${typeof date === 'string' ? date : date instanceof Date ? date.toISOString() : date.toString()}`
);

/**
 * Get relative time with performance optimization
 */
export const getRelativeTime = memoize(
  measurePerformance(
    (date: Date | string | number): string => {
      const now = Date.now();
      const dateTime = getDate(date).getTime();
      const diffInSeconds = Math.floor((now - dateTime) / 1000);
      
      // Use constants for better performance
      const MINUTE = 60;
      const HOUR = 3600;
      const DAY = 86400;
      const MONTH = 2592000;
      
      if (diffInSeconds < MINUTE) return 'just now';
      if (diffInSeconds < HOUR) return `${Math.floor(diffInSeconds / MINUTE)} minutes ago`;
      if (diffInSeconds < DAY) return `${Math.floor(diffInSeconds / HOUR)} hours ago`;
      if (diffInSeconds < MONTH) return `${Math.floor(diffInSeconds / DAY)} days ago`;
      
      return formatDisplayDate(date);
    },
    'getRelativeTime'
  ),
  (date) => {
    const timestamp = getDate(date).getTime();
    const nowBucket = Math.floor(Date.now() / 60000); // Cache for 1 minute buckets
    return `relative_${timestamp}_${nowBucket}`;
  }
);

/**
 * Validate task form with comprehensive validation
 */
export const validateTaskForm = measurePerformance(
  (data: any): { isValid: boolean; errors: string[]; warnings: string[] } => {
    const errors: string[] = [];
    const warnings: string[] = [];
    
    // Title validation
    if (!data.title?.trim()) {
      errors.push('Task title is required');
    } else if (data.title.trim().length < 3) {
      errors.push('Task title must be at least 3 characters');
    } else if (data.title.trim().length > 100) {
      errors.push('Task title must not exceed 100 characters');
    }
    
    // Description validation
    if (!data.description?.trim()) {
      errors.push('Task description is required');
    } else if (data.description.trim().length < 10) {
      errors.push('Task description must be at least 10 characters');
    } else if (data.description.trim().length > 500) {
      errors.push('Task description must not exceed 500 characters');
    }
    
    // Assignee validation
    if (!data.assignee?.trim()) {
      errors.push('Assignee is required');
    }
    
    // Due date validation
    if (!data.dueDate) {
      errors.push('Due date is required');
    } else {
      const dueDate = getDate(data.dueDate);
      const now = new Date();
      const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
      
      if (dueDate < today) {
        errors.push('Due date cannot be in the past');
      } else if (dueDate > new Date(Date.now() + 365 * 24 * 60 * 60 * 1000)) {
        warnings.push('Due date is more than a year away');
      }
    }
    
    // Priority validation
    if (data.priority && !['low', 'medium', 'high', 'urgent'].includes(data.priority)) {
      errors.push('Invalid priority level');
    }
    
    // Estimated hours validation
    if (data.estimatedHours !== undefined && data.estimatedHours !== null) {
      const hours = Number(data.estimatedHours);
      if (isNaN(hours) || hours < 0) {
        errors.push('Estimated hours must be a positive number');
      } else if (hours > 1000) {
        errors.push('Estimated hours must not exceed 1000');
      } else if (hours > 100) {
        warnings.push('Task with over 100 estimated hours might be too large');
      }
    }
    
    // Tags validation
    if (data.tags && Array.isArray(data.tags)) {
      if (data.tags.length > 10) {
        errors.push('Maximum 10 tags allowed');
      }
      
      for (const tag of data.tags) {
        if (typeof tag !== 'string' || tag.trim().length === 0) {
          errors.push('All tags must be non-empty strings');
          break;
        }
        if (tag.length > 30) {
          errors.push('Tag length must not exceed 30 characters');
          break;
        }
      }
    }
    
    return {
      isValid: errors.length === 0,
      errors,
      warnings,
    };
  },
  'validateTaskForm'
);

/**
 * Generate task ID with collision avoidance
 */
let idCounter = 0;
export const generateTaskId = (): string => {
  return `task_${Date.now()}_${++idCounter}_${Math.random().toString(36).substring(2, 9)}`;
};

/**
 * Calculate completion percentage with validation
 */
export const calculateCompletionPercentage = memoize(
  measurePerformance(
    (completedHours: number, estimatedHours: number): number => {
      // Input validation
      if (!estimatedHours || estimatedHours <= 0 || !Number.isFinite(estimatedHours)) return 0;
      if (!completedHours || completedHours < 0 || !Number.isFinite(completedHours)) return 0;
      
      return Math.min(100, Math.max(0, (completedHours / estimatedHours) * 100));
    },
    'calculateCompletionPercentage'
  ),
  (completedHours, estimatedHours) => `completion_${completedHours}_${estimatedHours}`
);

/**
 * Group tasks by assignee with optimization
 */
export const groupTasksByAssignee = memoize(
  measurePerformance(
    (tasks: TaskItem[]): Record<string, TaskItem[]> => {
      const groups: Record<string, TaskItem[]> = {};
      
      // Use for loop for better performance
      for (const task of tasks) {
        const assignee = task.assignee || 'Unassigned';
        if (!groups[assignee]) {
          groups[assignee] = [];
        }
        groups[assignee].push(task);
      }
      
      return groups;
    },
    'groupTasksByAssignee'
  ),
  (tasks) => `group_assignee_${tasks.length}_${tasks.map(t => `${t.id}_${t.assignee}`).join('|')}`
);

/**
 * Get tasks due soon with optimization
 */
export const getTasksDueSoon = memoize(
  measurePerformance(
    (tasks: TaskItem[], days: number = 3): TaskItem[] => {
      const now = Date.now();
      const futureTime = now + (days * 24 * 60 * 60 * 1000);
      const result: TaskItem[] = [];
      
      for (const task of tasks) {
        if (task.status !== 'completed') {
          const dueTime = getDate(task.dueDate).getTime();
          if (dueTime >= now && dueTime <= futureTime) {
            result.push(task);
          }
        }
      }
      
      return result;
    },
    'getTasksDueSoon'
  ),
  (tasks, days) => {
    const dayBucket = Math.floor(Date.now() / (24 * 60 * 60 * 1000)); // Cache per day
    return `due_soon_${days}_${dayBucket}_${tasks.length}_${tasks.map(t => `${t.id}_${t.status}_${t.dueDate}`).join('|')}`;
  }
);

// Additional utility functions for enhanced functionality

/**
 * Batch process tasks with performance monitoring
 */
export const batchProcessTasks = <T>(
  tasks: TaskItem[],
  processor: (task: TaskItem) => T,
  batchSize: number = 100
): T[] => {
  const results: T[] = [];
  
  for (let i = 0; i < tasks.length; i += batchSize) {
    const batch = tasks.slice(i, i + batchSize);
    const batchResults = batch.map(processor);
    results.push(...batchResults);
    
    // Allow other tasks to run if processing large datasets
    if (i + batchSize < tasks.length && typeof setImmediate !== 'undefined') {
      setImmediate(() => {});
    }
  }
  
  return results;
};

/**
 * Advanced task filtering with multiple criteria
 */
export const advancedFilterTasks = memoize(
  measurePerformance(
    (tasks: TaskItem[], filters: {
      statuses?: TaskStatus[];
      priorities?: TaskPriority[];
      assignees?: string[];
      tags?: string[];
      dateRange?: { start: Date; end: Date };
      searchTerm?: string;
    }): TaskItem[] => {
      let filtered = tasks;
      
      if (filters.statuses?.length) {
        const statusSet = new Set(filters.statuses);
        filtered = filtered.filter(task => statusSet.has(task.status));
      }
      
      if (filters.priorities?.length) {
        const prioritySet = new Set(filters.priorities);
        filtered = filtered.filter(task => prioritySet.has(task.priority));
      }
      
      if (filters.assignees?.length) {
        const assigneeSet = new Set(filters.assignees);
        filtered = filtered.filter(task => assigneeSet.has(task.assignee));
      }
      
      if (filters.tags?.length) {
        const tagSet = new Set(filters.tags);
        filtered = filtered.filter(task => 
          task.tags.some(tag => tagSet.has(tag))
        );
      }
      
      if (filters.dateRange) {
        const startTime = filters.dateRange.start.getTime();
        const endTime = filters.dateRange.end.getTime();
        filtered = filtered.filter(task => {
          const dueTime = getDate(task.dueDate).getTime();
          return dueTime >= startTime && dueTime <= endTime;
        });
      }
      
      if (filters.searchTerm) {
        filtered = searchTasks(filtered, filters.searchTerm);
      }
      
      return filtered;
    },
    'advancedFilterTasks'
  ),
  (tasks, filters) => `advanced_filter_${JSON.stringify(filters)}_${tasks.length}_${tasks.map(t => t.id).join('|')}`
);

/**
 * Get task analytics with performance metrics
 */
export const getTaskAnalytics = memoize(
  measurePerformance(
    (tasks: TaskItem[]) => {
      const analytics = {
        ...calculateStats(tasks),
        priorityDistribution: {} as Record<TaskPriority, number>,
        assigneeWorkload: {} as Record<string, {
          total: number;
          completed: number;
          overdue: number;
          totalHours: number;
        }>,
        averageCompletionTime: 0,
        productivityTrends: {} as Record<string, number>,
      };
      
      const now = Date.now();
      let totalCompletionTime = 0;
      let completedWithDates = 0;
      
      // Initialize priority distribution
      for (const priority of ['low', 'medium', 'high', 'urgent'] as TaskPriority[]) {
        analytics.priorityDistribution[priority] = 0;
      }
      
      for (const task of tasks) {
        // Priority distribution
        analytics.priorityDistribution[task.priority]++;
        
        // Assignee workload
        const assignee = task.assignee || 'Unassigned';
        if (!analytics.assigneeWorkload[assignee]) {
          analytics.assigneeWorkload[assignee] = {
            total: 0,
            completed: 0,
            overdue: 0,
            totalHours: 0,
          };
        }
        
        const workload = analytics.assigneeWorkload[assignee];
        workload.total++;
        workload.totalHours += task.estimatedHours || 0;
        
        if (task.status === 'completed') {
          workload.completed++;
          
          // Calculate completion time
          if (task.createdAt && task.updatedAt) {
            const createdTime = getDate(task.createdAt).getTime();
            const completedTime = getDate(task.updatedAt).getTime();
            totalCompletionTime += completedTime - createdTime;
            completedWithDates++;
          }
        }
        
        if (task.status !== 'completed' && getDate(task.dueDate).getTime() < now) {
          workload.overdue++;
        }
      }
      
      // Calculate average completion time in days
      analytics.averageCompletionTime = completedWithDates > 0 
        ? totalCompletionTime / completedWithDates / (1000 * 60 * 60 * 24)
        : 0;
      
      return analytics;
    },
    'getTaskAnalytics'
  ),
  (tasks) => `analytics_${tasks.length}_${tasks.map(t => `${t.id}_${t.status}_${t.priority}_${t.assignee}`).join('|')}`
);

// Performance optimization utilities
export const debounce = <T extends (...args: any[]) => any>(
  func: T,
  wait: number
): ((...args: Parameters<T>) => void) => {
  let timeout: NodeJS.Timeout | null = null;
  
  return (...args: Parameters<T>): void => {
    if (timeout) {
      clearTimeout(timeout);
    }
    
    timeout = setTimeout(() => {
      func(...args);
    }, wait);
  };
};

export const throttle = <T extends (...args: any[]) => any>(
  func: T,
  limit: number
): ((...args: Parameters<T>) => void) => {
  let inThrottle: boolean = false;
  
  return (...args: Parameters<T>): void => {
    if (!inThrottle) {
      func(...args);
      inThrottle = true;
      setTimeout(() => {
        inThrottle = false;
      }, limit);
    }
  };
};