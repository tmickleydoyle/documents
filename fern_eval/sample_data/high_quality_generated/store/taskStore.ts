import { create } from 'zustand';
import { TaskItem, UserProfile, TaskStatus } from '../types';

interface TaskState {
  tasks: TaskItem[];
  users: UserProfile[];
  loading: boolean;
  error: string | null;

  // Actions
  setTasks: (tasks: TaskItem[]) => void;
  addTask: (task: Omit<TaskItem, 'id' | 'createdAt' | 'updatedAt'>) => void;
  updateTask: (id: string, updates: Partial<TaskItem>) => void;
  deleteTask: (id: string) => void;
  updateTaskStatus: (id: string, status: TaskStatus) => void;
  setUsers: (users: UserProfile[]) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
}

export const useTaskStore = create<TaskState>((set, get) => ({
  tasks: [],
  users: [],
  loading: false,
  error: null,

  setTasks: (tasks) => set({ tasks }),

  addTask: (taskData) => {
    const newTask: TaskItem = {
      ...taskData,
      id: `task_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`,
      createdAt: new Date(),
      updatedAt: new Date(),
    };
    set((state) => ({
      tasks: [...state.tasks, newTask]
    }));
  },

  updateTask: (id, updates) => {
    set((state) => ({
      tasks: state.tasks.map((task) =>
        task.id === id
          ? { ...task, ...updates, updatedAt: new Date() }
          : task
      ),
    }));
  },

  deleteTask: (id) => {
    set((state) => ({
      tasks: state.tasks.filter((task) => task.id !== id),
    }));
  },

  updateTaskStatus: (id, status) => {
    const { updateTask } = get();
    updateTask(id, { status });
  },

  setUsers: (users) => set({ users }),
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),
}));

export default useTaskStore;
