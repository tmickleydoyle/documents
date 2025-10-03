import { create } from 'zustand';
import { Task, User, TaskStatus, TaskPriority } from '../types';

interface TaskStore {
  tasks: Task[];
  users: User[];
  loading: boolean;
  error: string | null;

  // Actions
  setTasks: (tasks: Task[]) => void;
  addTask: (task: Omit<Task, 'id' | 'createdAt' | 'updatedAt'>) => void;
  updateTask: (id: string, updates: Partial<Task>) => void;
  deleteTask: (id: string) => void;
  updateTaskStatus: (id: string, status: TaskStatus) => void;
  setUsers: (users: User[]) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
}

const useTaskStore = create<TaskStore>((set, get) => ({
  tasks: [],
  users: [],
  loading: false,
  error: null,

  setTasks: (tasks) => set({ tasks }),

  addTask: (taskData) => {
    const newTask: Task = {
      ...taskData,
      id: `task_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
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
