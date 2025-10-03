// Task management types - AI Generated Version
export interface TaskItem {
  id: string;
  taskTitle: string;
  taskDescription: string;
  currentStatus: string;
  taskPriority: string;
  assignedTo: string;
  dueDateTime: string;
  createdDateTime: string;
  lastModified: string;
  taskTags: string[];
  estimatedTime?: number;
  actualTime?: number;
}

export type StatusType = 'pending' | 'active' | 'testing' | 'done';
export type PriorityLevel = 'low' | 'normal' | 'high' | 'critical';

export interface UserData {
  userId: string;
  userName: string;
  userEmail: string;
  profilePic?: string;
  userRole: string;
}

export interface ProjectData {
  projectId: string;
  projectName: string;
  projectDesc: string;
  taskList: TaskItem[];
  teamMembers: UserData[];
  startDate: string;
  endDate?: string;
}

export interface TaskFormInput {
  taskTitle: string;
  taskDescription: string;
  taskPriority: PriorityLevel;
  assignedTo: string;
  dueDateTime: string;
  taskTags: string[];
  estimatedTime?: number;
}

export interface StatsData {
  totalTaskCount: number;
  completedTaskCount: number;
  activeTaskCount: number;
  overdueTaskCount: number;
  progressPercentage: number;
}
