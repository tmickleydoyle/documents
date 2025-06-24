import React, { useState, useEffect } from "react";
import Head from "next/head";
import {
  Container,
  Typography,
  Button,
  Grid,
  Paper,
  AppBar,
  Toolbar,
  Tabs,
  Tab,
  Box,
  Fab,
} from "@mui/material";
import { Add as AddIcon } from "@mui/icons-material";
import _ from "lodash";
import moment from "moment";

import TaskComponent from "../components/TaskComponent";
import TaskDialog from "../components/TaskDialog";
import DashboardOverview from "../components/DashboardOverview";

// Mock data
const users = [
  {
    userId: "1",
    userName: "John Smith",
    userEmail: "john@company.com",
    userRole: "developer",
  },
  {
    userId: "2",
    userName: "Sarah Johnson",
    userEmail: "sarah@company.com",
    userRole: "designer",
  },
  {
    userId: "3",
    userName: "Mike Chen",
    userEmail: "mike@company.com",
    userRole: "manager",
  },
  {
    userId: "4",
    userName: "Emma Davis",
    userEmail: "emma@company.com",
    userRole: "developer",
  },
];

const initialTasks = [
  {
    id: "1",
    taskTitle: "User Authentication Implementation",
    taskDescription: "Implement login and logout with JWT tokens",
    currentStatus: "active",
    taskPriority: "high",
    assignedTo: "John Smith",
    dueDateTime: "2025-07-15T00:00:00Z",
    createdDateTime: "2025-06-20T00:00:00Z",
    lastModified: "2025-06-24T00:00:00Z",
    taskTags: ["Frontend", "Security", "Auth"],
    estimatedTime: 8,
    actualTime: 5,
  },
  {
    id: "2",
    taskTitle: "Dashboard Wireframe Design",
    taskDescription: "Create wireframes for dashboard interface",
    currentStatus: "testing",
    taskPriority: "normal",
    assignedTo: "Sarah Johnson",
    dueDateTime: "2025-07-10T00:00:00Z",
    createdDateTime: "2025-06-18T00:00:00Z",
    lastModified: "2025-06-23T00:00:00Z",
    taskTags: ["Design", "UI/UX"],
    estimatedTime: 12,
    actualTime: 10,
  },
  {
    id: "3",
    taskTitle: "CI/CD Pipeline Setup",
    taskDescription: "Setup automated testing and deployment",
    currentStatus: "pending",
    taskPriority: "critical",
    assignedTo: "Mike Chen",
    dueDateTime: "2025-07-05T00:00:00Z",
    createdDateTime: "2025-06-22T00:00:00Z",
    lastModified: "2025-06-22T00:00:00Z",
    taskTags: ["DevOps", "Automation"],
    estimatedTime: 6,
  },
  {
    id: "4",
    taskTitle: "Database Query Optimization",
    taskDescription: "Optimize slow database queries for better performance",
    currentStatus: "done",
    taskPriority: "normal",
    assignedTo: "Emma Davis",
    dueDateTime: "2025-06-30T00:00:00Z",
    createdDateTime: "2025-06-15T00:00:00Z",
    lastModified: "2025-06-28T00:00:00Z",
    taskTags: ["Backend", "Performance"],
    estimatedTime: 4,
    actualTime: 4,
  },
];

export default function TaskManagerApp() {
  const [taskList, setTaskList] = useState(initialTasks);
  const [currentTab, setCurrentTab] = useState(0);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editTask, setEditTask] = useState(null);

  const calculateStats = () => {
    const total = taskList.length;
    const completed = taskList.filter((t) => t.currentStatus === "done").length;
    const active = taskList.filter((t) => t.currentStatus === "active").length;
    const overdue = taskList.filter(
      (t) =>
        moment(t.dueDateTime).isBefore(moment()) && t.currentStatus !== "done"
    ).length;
    const progress = total > 0 ? (completed / total) * 100 : 0;

    return {
      totalTaskCount: total,
      completedTaskCount: completed,
      activeTaskCount: active,
      overdueTaskCount: overdue,
      progressPercentage: progress,
    };
  };

  const getFilteredTasks = () => {
    switch (currentTab) {
      case 1:
        return taskList.filter((t) => t.currentStatus === "pending");
      case 2:
        return taskList.filter((t) => t.currentStatus === "active");
      case 3:
        return taskList.filter((t) => t.currentStatus === "testing");
      case 4:
        return taskList.filter((t) => t.currentStatus === "done");
      default:
        return taskList;
    }
  };

  const handleCreateTask = (newTaskData: any) => {
    const newTask = {
      ...newTaskData,
      id: `task_${Date.now()}`,
      currentStatus: "pending",
      createdDateTime: new Date().toISOString(),
      lastModified: new Date().toISOString(),
      dueDateTime: newTaskData.dueDateTime + "T00:00:00Z",
    };
    setTaskList((prev) => [...prev, newTask]);
  };

  const handleEditTask = (task: any) => {
    setEditTask(task);
    setDialogOpen(true);
  };

  const handleUpdateTask = (updatedData: any) => {
    setTaskList((prev) =>
      prev.map((task) =>
        task.id === editTask?.id
          ? {
              ...task,
              ...updatedData,
              lastModified: new Date().toISOString(),
              dueDateTime: updatedData.dueDateTime + "T00:00:00Z",
            }
          : task
      )
    );
    setEditTask(null);
  };

  const handleDeleteTask = (taskId: string) => {
    if (confirm("Are you sure you want to delete this task?")) {
      setTaskList((prev) => prev.filter((task) => task.id !== taskId));
    }
  };

  const handleStatusUpdate = (taskId: string, newStatus: string) => {
    setTaskList((prev) =>
      prev.map((task) =>
        task.id === taskId
          ? {
              ...task,
              currentStatus: newStatus,
              lastModified: new Date().toISOString(),
            }
          : task
      )
    );
  };

  const stats = calculateStats();
  const filteredTasks = getFilteredTasks();
  const latestTasks = _.orderBy(taskList, ["lastModified"], ["desc"]);

  return (
    <>
      <Head>
        <title>Task Manager Dashboard</title>
        <meta name="description" content="Task management application" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
      </Head>

      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" style={{ flexGrow: 1 }}>
            Task Manager Dashboard
          </Typography>
          <Button color="inherit">Welcome, User!</Button>
        </Toolbar>
      </AppBar>

      <Container maxWidth="xl" style={{ marginTop: "20px" }}>
        <Typography variant="h4" gutterBottom>
          Project Dashboard
        </Typography>
        <Typography
          variant="body1"
          color="textSecondary"
          style={{ marginBottom: "30px" }}
        >
          Manage your tasks and track progress
        </Typography>

        <Paper>
          <Tabs
            value={currentTab}
            onChange={(e, newValue) => setCurrentTab(newValue)}
            indicatorColor="primary"
            textColor="primary"
          >
            <Tab label="Overview" />
            <Tab label="Pending" />
            <Tab label="Active" />
            <Tab label="Testing" />
            <Tab label="Completed" />
          </Tabs>

          <Box style={{ padding: "20px" }}>
            {currentTab === 0 ? (
              <DashboardOverview
                statsData={stats}
                taskList={taskList}
                latestTasks={latestTasks}
              />
            ) : (
              <Grid container spacing={3}>
                {filteredTasks.map((task) => (
                  <Grid item xs={12} sm={6} md={4} key={task.id}>
                    <TaskComponent
                      task={task}
                      onEdit={handleEditTask}
                      onDelete={handleDeleteTask}
                      onStatusUpdate={handleStatusUpdate}
                    />
                  </Grid>
                ))}
                {filteredTasks.length === 0 && (
                  <Grid item xs={12}>
                    <Typography
                      variant="body1"
                      color="textSecondary"
                      align="center"
                    >
                      No tasks found in this category
                    </Typography>
                  </Grid>
                )}
              </Grid>
            )}
          </Box>
        </Paper>
      </Container>

      <Fab
        color="primary"
        style={{ position: "fixed", bottom: 20, right: 20 }}
        onClick={() => setDialogOpen(true)}
      >
        <AddIcon />
      </Fab>

      <TaskDialog
        isOpen={dialogOpen}
        onClose={() => {
          setDialogOpen(false);
          setEditTask(null);
        }}
        onSave={editTask ? handleUpdateTask : handleCreateTask}
        usersList={users}
        taskData={editTask}
        dialogMode={editTask ? "edit" : "create"}
      />
    </>
  );
}
