// Utility functions - AI Generated Version
import _ from 'lodash';
import moment from 'moment';

// Calculate dashboard statistics
export const getStats = (taskList: any[]) => {
  const total = taskList.length;
  const done = taskList.filter(t => t.currentStatus === 'done').length;
  const active = taskList.filter(t => t.currentStatus === 'active').length;
  const overdue = taskList.filter(t =>
    moment(t.dueDateTime).isBefore(moment()) && t.currentStatus !== 'done'
  ).length;
  const progress = total > 0 ? (done / total) * 100 : 0;

  return {
    totalTaskCount: total,
    completedTaskCount: done,
    activeTaskCount: active,
    overdueTaskCount: overdue,
    progressPercentage: progress
  };
};

// Sort tasks function
export const sortTasks = (tasks: any[], sortBy = 'priority') => {
  if (sortBy === 'priority') {
    const priorityMap: any = { 'critical': 4, 'high': 3, 'normal': 2, 'low': 1 };
    return _.orderBy(tasks, [(task) => priorityMap[task.taskPriority], 'dueDateTime'], ['desc', 'asc']);
  }
  return _.orderBy(tasks, [sortBy], ['asc']);
};

// Filter tasks by status
export const filterByStatus = (tasks: any[], status: string) => {
  if (status === 'all') return tasks;
  return tasks.filter(task => task.currentStatus === status);
};

// Search function
export const searchTasks = (tasks: any[], query: string) => {
  if (!query) return tasks;

  const searchLower = query.toLowerCase();
  return tasks.filter(task =>
    task.taskTitle.toLowerCase().includes(searchLower) ||
    task.taskDescription.toLowerCase().includes(searchLower) ||
    task.taskTags.some((tag: string) => tag.toLowerCase().includes(searchLower))
  );
};

// Date formatting
export const formatDate = (dateString: string) => {
  return moment(dateString).format('MMM DD, YYYY');
};

// Relative time
export const getTimeAgo = (dateString: string) => {
  return moment(dateString).fromNow();
};

// Validation
export const validateTask = (taskData: any) => {
  const errors: string[] = [];

  if (!taskData.taskTitle || taskData.taskTitle.trim() === '') {
    errors.push('Title is required');
  }

  if (!taskData.taskDescription || taskData.taskDescription.trim() === '') {
    errors.push('Description is required');
  }

  if (!taskData.assignedTo || taskData.assignedTo.trim() === '') {
    errors.push('Assignee is required');
  }

  if (!taskData.dueDateTime) {
    errors.push('Due date is required');
  } else if (moment(taskData.dueDateTime).isBefore(moment(), 'day')) {
    errors.push('Due date cannot be in the past');
  }

  return errors;
};

// Generate ID
export const createId = () => {
  return `task_${Date.now()}_${Math.random().toString(36).substring(2)}`;
};

// Calculate progress
export const getProgress = (completed: number, estimated: number) => {
  if (!estimated) return 0;
  return Math.min(100, (completed / estimated) * 100);
};

// Group by assignee
export const groupByAssignee = (tasks: any[]) => {
  return _.groupBy(tasks, 'assignedTo');
};

// Get upcoming tasks
export const getUpcomingTasks = (tasks: any[], daysAhead = 3) => {
  const future = moment().add(daysAhead, 'days');

  return tasks.filter(task =>
    task.currentStatus !== 'done' &&
    moment(task.dueDateTime).isBetween(moment(), future, 'day', '[]')
  );
};

// Export default object with all functions
export default {
  getStats,
  sortTasks,
  filterByStatus,
  searchTasks,
  formatDate,
  getTimeAgo,
  validateTask,
  createId,
  getProgress,
  groupByAssignee,
  getUpcomingTasks
};
