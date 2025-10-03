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

  // Batch operations
  bulkUpdateTasks: async (updates) => {
    set((state) => {
      state.tasksAsync.loading = true;
      state.tasksAsync.error = null;
    });
    
    try {
      set((state) => {
        updates.forEach(({ id, updates: taskUpdates }) => {
          const taskIndex = state.tasks.findIndex(task => task.id === id);
          if (taskIndex !== -1) {
            state.tasks[taskIndex] = {
              ...state.tasks[taskIndex],
              ...taskUpdates,
              updatedAt: new Date(),
            };
          }
        });
        state.tasksAsync.loading = false;
        state.tasksAsync.lastUpdated = new Date();
      });
    } catch (error) {
      set((state) => {
        state.tasksAsync.loading = false;
        state.tasksAsync.error = {
          message: 'Failed to bulk update tasks',
          timestamp: new Date(),
        };
      });
      throw error;
    }
  },
  
  bulkDeleteTasks: async (ids) => {
    set((state) => {
      state.tasksAsync.loading = true;
      state.tasksAsync.error = null;
    });
    
    try {
      set((state) => {
        state.tasks = state.tasks.filter(task => !ids.includes(task.id));
        state.selectedTaskIds = state.selectedTaskIds.filter(id => !ids.includes(id));
        state.tasksAsync.loading = false;
        state.tasksAsync.lastUpdated = new Date();
      });
    } catch (error) {
      set((state) => {
        state.tasksAsync.loading = false;
        state.tasksAsync.error = {
          message: 'Failed to bulk delete tasks',
          timestamp: new Date(),
        };
      });
      throw error;
    }
  },
  
  // User management
  setUsers: async (users) => {
    set((state) => {
      state.usersAsync.loading = true;
      state.usersAsync.error = null;
    });
    
    try {
      set((state) => {
        state.users = users;
        state.usersAsync.loading = false;
        state.usersAsync.lastUpdated = new Date();
      });
    } catch (error) {
      set((state) => {
        state.usersAsync.loading = false;
        state.usersAsync.error = {
          message: 'Failed to set users',
          timestamp: new Date(),
        };
      });
      throw error;
    }
  },
  
  // Filtering and sorting
  setFilters: (newFilters) => {
    set((state) => {
      state.filters = { ...state.filters, ...newFilters };
    });
  },
  
  setSortConfig: (config) => {
    set((state) => {
      state.sortConfig = config;
    });
  },
  
  clearFilters: () => {
    set((state) => {
      state.filters = {};
    });
  },
  
  // Selection management
  selectTask: (id) => {
    set((state) => {
      if (!state.selectedTaskIds.includes(id)) {
        state.selectedTaskIds.push(id);
      }
    });
  },
  
  selectTasks: (ids) => {
    set((state) => {
      state.selectedTaskIds = [...new Set([...state.selectedTaskIds, ...ids])];
    });
  },
  
  clearSelection: () => {
    set((state) => {
      state.selectedTaskIds = [];
    });
  },
  
  // Error handling
  setError: (type, error) => {
    set((state) => {
      if (type === 'tasks') {
        state.tasksAsync.error = error;
      } else {
        state.usersAsync.error = error;
      }
    });
  },
  
  clearErrors: () => {
    set((state) => {
      state.tasksAsync.error = null;
      state.usersAsync.error = null;
    });
  },
  
  // Utility actions
  refreshTasks: async () => {
    // This would typically refetch from an API
    const { tasks } = get();
    await get().setTasks(tasks);
  },
  
  optimisticUpdate: (id, updates) => {
    set((state) => {
      const taskIndex = state.tasks.findIndex(task => task.id === id);
      if (taskIndex !== -1) {
        state.tasks[taskIndex] = {
          ...state.tasks[taskIndex],
          ...updates,
          updatedAt: new Date(),
        };
      }
    });
  },
  
  revertOptimisticUpdate: (id) => {
    // This would revert to the last known server state
    // Implementation would depend on how you track server state
    console.warn('Optimistic update revert not implemented');
  },
        }))
      ),
      {
        name: 'task-store',
        partialize: (state) => ({
          tasks: state.tasks,
          users: state.users,
          filters: state.filters,
          sortConfig: state.sortConfig,
        }),
      }
    ),
    {
      name: 'task-store',
    }
  )
);

export default useTaskStore;
