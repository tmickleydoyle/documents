import React, { useState, useEffect, useMemo, useCallback } from "react";
import Head from "next/head";
import {
  Box,
  Container,
  Typography,
  Button,
  Grid,
  Paper,
  Tabs,
  Tab,
  Fab,
  AppBar,
  Toolbar,
  Avatar,
  Menu,
  MenuItem,
  IconButton,
  Badge,
  Snackbar,
  Alert,
} from "@mui/material";
import {
  Add as AddIcon,
  Dashboard as DashboardIcon,
  Assignment as TaskIcon,
  Notifications as NotificationsIcon,
  Settings as SettingsIcon,
  ExitToApp as LogoutIcon,
} from "@mui/icons-material";
import { Task, User, TaskFormData, DashboardStats } from "../types";
import useTaskStore from "../store/taskStore";
import TaskCard from "../components/TaskCard";
import TaskForm from "../components/TaskForm";
import DashboardOverview from "../components/DashboardOverview";

// Sample data for demonstration purposes
const sampleUsers: User[] = [
  {
    id: "1",
    name: "John Smith",
    email: "john@company.com",
    role: "developer",
    avatar: "",
  },
  {
    id: "2",
    name: "Sarah Johnson",
    email: "sarah@company.com",
    role: "designer",
    avatar: "",
  },
  {
    id: "3",
    name: "Mike Chen",
    email: "mike@company.com",
    role: "manager",
    avatar: "",
  },
  {
    id: "4",
    name: "Emma Davis",
    email: "emma@company.com",
    role: "developer",
    avatar: "",
  },
];

const sampleTasks: Task[] = [
  {
    id: "1",
    title: "Implement user authentication",
    description:
      "Create login/logout functionality with JWT tokens and secure session management",
    status: "in-progress",
    priority: "high",
    assignee: "John Smith",
    dueDate: new Date("2025-07-15"),
    createdAt: new Date("2025-06-20"),
    updatedAt: new Date("2025-06-24"),
    tags: ["Frontend", "Security", "Authentication"],
    estimatedHours: 8,
    completedHours: 5,
  },
  {
    id: "2",
    title: "Design dashboard wireframes",
    description:
      "Create comprehensive wireframes for the main dashboard interface including all key components",
    status: "review",
    priority: "medium",
    assignee: "Sarah Johnson",
    dueDate: new Date("2025-07-10"),
    createdAt: new Date("2025-06-18"),
    updatedAt: new Date("2025-06-23"),
    tags: ["UI/UX", "Design", "Wireframes"],
    estimatedHours: 12,
    completedHours: 10,
  },
  {
    id: "3",
    title: "Set up CI/CD pipeline",
    description:
      "Configure automated testing and deployment pipeline using GitHub Actions",
    status: "todo",
    priority: "urgent",
    assignee: "Mike Chen",
    dueDate: new Date("2025-07-05"),
    createdAt: new Date("2025-06-22"),
    updatedAt: new Date("2025-06-22"),
    tags: ["DevOps", "CI/CD", "Automation"],
    estimatedHours: 6,
  },
  {
    id: "4",
    title: "Optimize database queries",
    description:
      "Review and optimize slow database queries to improve application performance",
    status: "completed",
    priority: "medium",
    assignee: "Emma Davis",
    dueDate: new Date("2025-06-30"),
    createdAt: new Date("2025-06-15"),
    updatedAt: new Date("2025-06-28"),
    tags: ["Backend", "Performance", "Database"],
    estimatedHours: 4,
    completedHours: 4,
  },
];

// Tab panel component for switching between different views
interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

const TabPanel: React.FC<TabPanelProps> = ({ children, value, index }) => {
  return (
    <div hidden={value !== index} style={{ paddingTop: 24 }}>
      {value === index && children}
    </div>
  );
};

const HomePage: React.FC = () => {
  // Store state
  const store = useTaskStore();
  const {
    tasks,
    users,
    addTask,
    updateTask,
    deleteTask,
    updateTaskStatus,
    setTasks,
    setUsers,
  } = store;

  // Component state
  const [activeTab, setActiveTab] = useState(0);
  const [isTaskFormOpen, setIsTaskFormOpen] = useState(false);
  const [taskBeingEdited, setTaskBeingEdited] = useState<Task | null>(null);
  const [userMenuElement, setUserMenuElement] = useState<HTMLElement | null>(
    null
  );
  const [snackbarMessage, setSnackbarMessage] = useState<string>("");
  const [snackbarOpen, setSnackbarOpen] = useState(false);

  // Initialize data on component mount
  useEffect(() => {
    setTasks(sampleTasks);
    setUsers(sampleUsers);
  }, [setTasks, setUsers]);

  // Calculate dashboard statistics
  const dashboardStats: DashboardStats = useMemo(() => {
    const total = tasks.length;
    const completed = tasks.filter(
      (task) => task.status === "completed"
    ).length;
    const inProgress = tasks.filter(
      (task) => task.status === "in-progress"
    ).length;
    const overdue = tasks.filter(
      (task) =>
        new Date(task.dueDate) < new Date() && task.status !== "completed"
    ).length;
    const completionPercentage = total > 0 ? (completed / total) * 100 : 0;

    return {
      totalTasks: total,
      completedTasks: completed,
      inProgressTasks: inProgress,
      overdueTasks: overdue,
      completionRate: completionPercentage,
    };
  }, [tasks]);

  // Get recent tasks sorted by update date
  const recentTasksList = useMemo(() => {
    return [...tasks].sort(
      (a, b) =>
        new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime()
    );
  }, [tasks]);

  // Filter tasks based on selected tab
  const getFilteredTasks = useMemo(() => {
    const statusMap = {
      1: "todo",
      2: "in-progress",
      3: "review",
      4: "completed",
    };

    if (activeTab === 0) {
      return tasks; // All tasks for overview
    }

    const targetStatus = statusMap[activeTab as keyof typeof statusMap];
    return tasks.filter((task) => task.status === targetStatus);
  }, [tasks, activeTab]);

  // Event handlers
  const handleTabChange = useCallback(
    (_: React.SyntheticEvent, newValue: number) => {
      setActiveTab(newValue);
    },
    []
  );

  const handleCreateNewTask = useCallback(
    (formData: TaskFormData) => {
      addTask({
        title: formData.title,
        description: formData.description,
        status: "todo",
        priority: formData.priority,
        assignee: formData.assignee,
        dueDate: new Date(formData.dueDate),
        tags: formData.tags,
        estimatedHours: formData.estimatedHours,
      });
      setSnackbarMessage("Task created successfully!");
      setSnackbarOpen(true);
    },
    [addTask]
  );

  const handleEditTask = useCallback((task: Task) => {
    setTaskBeingEdited(task);
    setIsTaskFormOpen(true);
  }, []);

  const handleUpdateExistingTask = useCallback(
    (formData: TaskFormData) => {
      if (taskBeingEdited) {
        updateTask(taskBeingEdited.id, {
          title: formData.title,
          description: formData.description,
          priority: formData.priority,
          assignee: formData.assignee,
          dueDate: new Date(formData.dueDate),
          tags: formData.tags,
          estimatedHours: formData.estimatedHours,
        });
        setTaskBeingEdited(null);
        setSnackbarMessage("Task updated successfully!");
        setSnackbarOpen(true);
      }
    },
    [taskBeingEdited, updateTask]
  );

  const handleFormClose = useCallback(() => {
    setIsTaskFormOpen(false);
    setTaskBeingEdited(null);
  }, []);

  const handleUserMenuOpen = useCallback(
    (event: React.MouseEvent<HTMLElement>) => {
      setUserMenuElement(event.currentTarget);
    },
    []
  );

  const handleUserMenuClose = useCallback(() => {
    setUserMenuElement(null);
  }, []);

  const handleSnackbarClose = useCallback(() => {
    setSnackbarOpen(false);
  }, []);

  const openTaskForm = useCallback(() => {
    setIsTaskFormOpen(true);
  }, []);

  // Render task grid
  const renderTaskGrid = (tasksToRender: Task[]) => (
    <Grid container spacing={3}>
      {tasksToRender.map((task) => (
        <Grid item xs={12} sm={6} md={4} key={task.id}>
          <TaskCard
            task={task}
            onEdit={handleEditTask}
            onDelete={deleteTask}
            onStatusChange={updateTaskStatus}
          />
        </Grid>
      ))}
    </Grid>
  );

  return (
    <>
      <Head>
        <title>Task Dashboard - Manage Your Projects</title>
        <meta
          name="description"
          content="Comprehensive task management dashboard for tracking projects and team productivity"
        />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
      </Head>

      {/* App Header */}
      <AppBar position="sticky" elevation={1}>
        <Toolbar>
          <Box display="flex" alignItems="center" flexGrow={1}>
            <DashboardIcon sx={{ mr: 2 }} />
            <Typography variant="h6" component="h1">
              Task Dashboard
            </Typography>
          </Box>

          <Box display="flex" alignItems="center" gap={1}>
            <IconButton color="inherit">
              <Badge badgeContent={3} color="error">
                <NotificationsIcon />
              </Badge>
            </IconButton>

            <IconButton color="inherit" onClick={handleUserMenuOpen}>
              <Avatar sx={{ width: 32, height: 32, bgcolor: "secondary.main" }}>
                JD
              </Avatar>
            </IconButton>
          </Box>

          <Menu
            anchorEl={userMenuElement}
            open={Boolean(userMenuElement)}
            onClose={handleUserMenuClose}
          >
            <MenuItem onClick={handleUserMenuClose}>
              <SettingsIcon sx={{ mr: 1 }} />
              Settings
            </MenuItem>
            <MenuItem onClick={handleUserMenuClose}>
              <LogoutIcon sx={{ mr: 1 }} />
              Logout
            </MenuItem>
          </Menu>
        </Toolbar>
      </AppBar>

      {/* Main Content */}
      <Container maxWidth="xl" sx={{ py: 4 }}>
        <Box mb={4}>
          <Typography variant="h4" component="h2" gutterBottom>
            Welcome back, John!
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Here's what's happening with your projects today.
          </Typography>
        </Box>

        <Paper sx={{ width: "100%" }}>
          <Tabs
            value={activeTab}
            onChange={handleTabChange}
            variant="scrollable"
            scrollButtons="auto"
          >
            <Tab icon={<DashboardIcon />} label="Overview" />
            <Tab icon={<TaskIcon />} label="To Do" />
            <Tab icon={<TaskIcon />} label="In Progress" />
            <Tab icon={<TaskIcon />} label="Review" />
            <Tab icon={<TaskIcon />} label="Completed" />
          </Tabs>

          {/* Overview Tab */}
          <TabPanel value={activeTab} index={0}>
            <Box p={3}>
              <DashboardOverview
                stats={dashboardStats}
                tasks={tasks}
                recentTasks={recentTasksList}
              />
            </Box>
          </TabPanel>

          {/* Task Status Tabs */}
          <TabPanel value={activeTab} index={1}>
            <Box p={3}>{renderTaskGrid(getFilteredTasks)}</Box>
          </TabPanel>

          <TabPanel value={activeTab} index={2}>
            <Box p={3}>{renderTaskGrid(getFilteredTasks)}</Box>
          </TabPanel>

          <TabPanel value={activeTab} index={3}>
            <Box p={3}>{renderTaskGrid(getFilteredTasks)}</Box>
          </TabPanel>

          <TabPanel value={activeTab} index={4}>
            <Box p={3}>{renderTaskGrid(getFilteredTasks)}</Box>
          </TabPanel>
        </Paper>
      </Container>

      {/* Floating Action Button for Adding Tasks */}
      <Fab
        color="primary"
        aria-label="add new task"
        sx={{ position: "fixed", bottom: 16, right: 16 }}
        onClick={openTaskForm}
      >
        <AddIcon />
      </Fab>

      {/* Task Creation/Edit Form */}
      <TaskForm
        open={isTaskFormOpen}
        onClose={handleFormClose}
        onSubmit={
          taskBeingEdited ? handleUpdateExistingTask : handleCreateNewTask
        }
        users={users}
        initialData={
          taskBeingEdited
            ? {
                title: taskBeingEdited.title,
                description: taskBeingEdited.description,
                priority: taskBeingEdited.priority,
                assignee: taskBeingEdited.assignee,
                dueDate: taskBeingEdited.dueDate.toISOString().split("T")[0],
                tags: taskBeingEdited.tags,
                estimatedHours: taskBeingEdited.estimatedHours,
              }
            : undefined
        }
        mode={taskBeingEdited ? "edit" : "create"}
      />

      {/* Success Messages */}
      <Snackbar
        open={snackbarOpen}
        autoHideDuration={6000}
        onClose={handleSnackbarClose}
      >
        <Alert onClose={handleSnackbarClose} severity="success">
          {snackbarMessage}
        </Alert>
      </Snackbar>
    </>
  );
};

export default HomePage;
