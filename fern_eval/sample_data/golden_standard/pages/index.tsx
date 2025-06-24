import React, { useState, useEffect, useMemo } from "react";
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
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Divider,
} from "@mui/material";
import {
  Add as AddIcon,
  Dashboard as DashboardIcon,
  Assignment as TaskIcon,
  Notifications as NotificationsIcon,
  Settings as SettingsIcon,
  ExitToApp as LogoutIcon,
  FilterList as FilterIcon,
} from "@mui/icons-material";
import { Task, User, TaskFormData, DashboardStats } from "../types";
import useTaskStore from "../store/taskStore";
import TaskCard from "../components/TaskCard";
import TaskForm from "../components/TaskForm";
import DashboardOverview from "../components/DashboardOverview";

// Mock data for demonstration
const mockUsers: User[] = [
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

const mockTasks: Task[] = [
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

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel({ children, value, index }: TabPanelProps) {
  return (
    <div hidden={value !== index} style={{ paddingTop: 24 }}>
      {value === index && children}
    </div>
  );
}

const TaskDashboard: React.FC = () => {
  const {
    tasks,
    users,
    addTask,
    updateTask,
    deleteTask,
    updateTaskStatus,
    setTasks,
    setUsers,
  } = useTaskStore();
  const [currentTab, setCurrentTab] = useState(0);
  const [taskFormOpen, setTaskFormOpen] = useState(false);
  const [editingTask, setEditingTask] = useState<Task | null>(null);
  const [userMenuAnchor, setUserMenuAnchor] = useState<null | HTMLElement>(
    null
  );

  // Initialize with mock data
  useEffect(() => {
    setTasks(mockTasks);
    setUsers(mockUsers);
  }, [setTasks, setUsers]);

  const stats: DashboardStats = useMemo(() => {
    const totalTasks = tasks.length;
    const completedTasks = tasks.filter((t) => t.status === "completed").length;
    const inProgressTasks = tasks.filter(
      (t) => t.status === "in-progress"
    ).length;
    const overdueTasks = tasks.filter(
      (t) => new Date(t.dueDate) < new Date() && t.status !== "completed"
    ).length;
    const completionRate =
      totalTasks > 0 ? (completedTasks / totalTasks) * 100 : 0;

    return {
      totalTasks,
      completedTasks,
      inProgressTasks,
      overdueTasks,
      completionRate,
    };
  }, [tasks]);

  const recentTasks = useMemo(
    () =>
      [...tasks].sort(
        (a, b) =>
          new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime()
      ),
    [tasks]
  );

  const handleTabChange = (_: React.SyntheticEvent, newValue: number) => {
    setCurrentTab(newValue);
  };

  const handleCreateTask = (data: TaskFormData) => {
    addTask({
      title: data.title,
      description: data.description,
      status: "todo",
      priority: data.priority,
      assignee: data.assignee,
      dueDate: new Date(data.dueDate),
      tags: data.tags,
      estimatedHours: data.estimatedHours,
    });
  };

  const handleEditTask = (task: Task) => {
    setEditingTask(task);
    setTaskFormOpen(true);
  };

  const handleUpdateTask = (data: TaskFormData) => {
    if (editingTask) {
      updateTask(editingTask.id, {
        title: data.title,
        description: data.description,
        priority: data.priority,
        assignee: data.assignee,
        dueDate: new Date(data.dueDate),
        tags: data.tags,
        estimatedHours: data.estimatedHours,
      });
      setEditingTask(null);
    }
  };

  const handleCloseForm = () => {
    setTaskFormOpen(false);
    setEditingTask(null);
  };

  const handleUserMenuClick = (event: React.MouseEvent<HTMLElement>) => {
    setUserMenuAnchor(event.currentTarget);
  };

  const handleUserMenuClose = () => {
    setUserMenuAnchor(null);
  };

  const filteredTasks = useMemo(() => {
    switch (currentTab) {
      case 1:
        return tasks.filter((t) => t.status === "todo");
      case 2:
        return tasks.filter((t) => t.status === "in-progress");
      case 3:
        return tasks.filter((t) => t.status === "review");
      case 4:
        return tasks.filter((t) => t.status === "completed");
      default:
        return tasks;
    }
  }, [tasks, currentTab]);

  return (
    <>
      <Head>
        <title>Task Dashboard - Manage Your Projects</title>
        <meta
          name="description"
          content="Comprehensive task management dashboard"
        />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
      </Head>

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

            <IconButton color="inherit" onClick={handleUserMenuClick}>
              <Avatar sx={{ width: 32, height: 32, bgcolor: "secondary.main" }}>
                JD
              </Avatar>
            </IconButton>
          </Box>

          <Menu
            anchorEl={userMenuAnchor}
            open={Boolean(userMenuAnchor)}
            onClose={handleUserMenuClose}
          >
            <MenuItem onClick={handleUserMenuClose}>
              <ListItemIcon>
                <SettingsIcon />
              </ListItemIcon>
              Settings
            </MenuItem>
            <MenuItem onClick={handleUserMenuClose}>
              <ListItemIcon>
                <LogoutIcon />
              </ListItemIcon>
              Logout
            </MenuItem>
          </Menu>
        </Toolbar>
      </AppBar>

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
            value={currentTab}
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

          <TabPanel value={currentTab} index={0}>
            <Box p={3}>
              <DashboardOverview
                stats={stats}
                tasks={tasks}
                recentTasks={recentTasks}
              />
            </Box>
          </TabPanel>

          <TabPanel value={currentTab} index={1}>
            <Box p={3}>
              <Grid container spacing={3}>
                {filteredTasks.map((task) => (
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
            </Box>
          </TabPanel>

          <TabPanel value={currentTab} index={2}>
            <Box p={3}>
              <Grid container spacing={3}>
                {filteredTasks.map((task) => (
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
            </Box>
          </TabPanel>

          <TabPanel value={currentTab} index={3}>
            <Box p={3}>
              <Grid container spacing={3}>
                {filteredTasks.map((task) => (
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
            </Box>
          </TabPanel>

          <TabPanel value={currentTab} index={4}>
            <Box p={3}>
              <Grid container spacing={3}>
                {filteredTasks.map((task) => (
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
            </Box>
          </TabPanel>
        </Paper>
      </Container>

      {/* Floating Action Button */}
      <Fab
        color="primary"
        aria-label="add task"
        sx={{ position: "fixed", bottom: 16, right: 16 }}
        onClick={() => setTaskFormOpen(true)}
      >
        <AddIcon />
      </Fab>

      {/* Task Form Dialog */}
      <TaskForm
        open={taskFormOpen}
        onClose={handleCloseForm}
        onSubmit={editingTask ? handleUpdateTask : handleCreateTask}
        users={users}
        initialData={
          editingTask
            ? {
                title: editingTask.title,
                description: editingTask.description,
                priority: editingTask.priority,
                assignee: editingTask.assignee,
                dueDate: editingTask.dueDate.toISOString().split("T")[0],
                tags: editingTask.tags,
                estimatedHours: editingTask.estimatedHours,
              }
            : undefined
        }
        mode={editingTask ? "edit" : "create"}
      />
    </>
  );
};

export default TaskDashboard;

export default HomePage;
