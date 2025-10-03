import React, { useMemo } from "react";
import {
  Grid,
  Paper,
  Typography,
  Box,
  LinearProgress,
  Card,
  CardContent,
  Avatar,
  Chip,
} from "@mui/material";
import {
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import {
  Assignment as TaskIcon,
  CheckCircle as CompletedIcon,
  Schedule as InProgressIcon,
  Warning as OverdueIcon,
} from "@mui/icons-material";
import { DashboardStats, Task, TaskStatus } from "../types";

interface DashboardOverviewProps {
  stats: DashboardStats;
  tasks: Task[];
  recentTasks: Task[];
}

const DashboardOverview: React.FC<DashboardOverviewProps> = ({
  stats,
  tasks,
  recentTasks,
}) => {
  // Calculate status distribution using useMemo for performance
  const statusDistributionData = useMemo(() => {
    const statusCounts = {
      todo: tasks.filter((task) => task.status === "todo").length,
      inProgress: tasks.filter((task) => task.status === "in-progress").length,
      review: tasks.filter((task) => task.status === "review").length,
      completed: tasks.filter((task) => task.status === "completed").length,
    };

    return [
      {
        name: "To Do",
        value: statusCounts.todo,
        color: "#9E9E9E",
      },
      {
        name: "In Progress",
        value: statusCounts.inProgress,
        color: "#2196F3",
      },
      {
        name: "Review",
        value: statusCounts.review,
        color: "#FF9800",
      },
      {
        name: "Completed",
        value: statusCounts.completed,
        color: "#4CAF50",
      },
    ];
  }, [tasks]);

  // Calculate priority distribution
  const priorityDistributionData = useMemo(() => {
    const priorityCounts = {
      low: tasks.filter((task) => task.priority === "low").length,
      medium: tasks.filter((task) => task.priority === "medium").length,
      high: tasks.filter((task) => task.priority === "high").length,
      urgent: tasks.filter((task) => task.priority === "urgent").length,
    };

    return [
      { name: "Low", value: priorityCounts.low },
      { name: "Medium", value: priorityCounts.medium },
      { name: "High", value: priorityCounts.high },
      { name: "Urgent", value: priorityCounts.urgent },
    ];
  }, [tasks]);

  // Helper function to render stat cards
  const renderStatCard = ({
    title,
    value,
    icon,
    color,
    subtitle,
  }: {
    title: string;
    value: number;
    icon: React.ReactNode;
    color: string;
    subtitle?: string;
  }) => (
    <Card sx={{ height: "100%" }}>
      <CardContent>
        <Box display="flex" alignItems="center" justifyContent="space-between">
          <Box>
            <Typography color="textSecondary" gutterBottom variant="body2">
              {title}
            </Typography>
            <Typography variant="h4" component="h2">
              {value}
            </Typography>
            {subtitle && (
              <Typography color="textSecondary" variant="body2">
                {subtitle}
              </Typography>
            )}
          </Box>
          <Avatar sx={{ bgcolor: color, width: 48, height: 48 }}>{icon}</Avatar>
        </Box>
      </CardContent>
    </Card>
  );

  // Helper function to get chip color based on status
  const getStatusChipColor = (status: TaskStatus) => {
    switch (status) {
      case "completed":
        return "success";
      case "in-progress":
        return "primary";
      case "review":
        return "warning";
      default:
        return "default";
    }
  };

  // Format date helper
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString();
  };

  return (
    <Grid container spacing={3}>
      {/* Statistics Cards Row */}
      <Grid item xs={12} sm={6} md={3}>
        {renderStatCard({
          title: "Total Tasks",
          value: stats.totalTasks,
          icon: <TaskIcon />,
          color: "#1976d2",
        })}
      </Grid>

      <Grid item xs={12} sm={6} md={3}>
        {renderStatCard({
          title: "Completed",
          value: stats.completedTasks,
          icon: <CompletedIcon />,
          color: "#388e3c",
          subtitle: `${Math.round(stats.completionRate)}% completion rate`,
        })}
      </Grid>

      <Grid item xs={12} sm={6} md={3}>
        {renderStatCard({
          title: "In Progress",
          value: stats.inProgressTasks,
          icon: <InProgressIcon />,
          color: "#f57c00",
        })}
      </Grid>

      <Grid item xs={12} sm={6} md={3}>
        {renderStatCard({
          title: "Overdue",
          value: stats.overdueTasks,
          icon: <OverdueIcon />,
          color: "#d32f2f",
        })}
      </Grid>

      {/* Overall Progress Section */}
      <Grid item xs={12}>
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            Overall Progress
          </Typography>
          <Box display="flex" alignItems="center">
            <Box width="100%" mr={1}>
              <LinearProgress
                variant="determinate"
                value={stats.completionRate}
                sx={{ height: 8, borderRadius: 4 }}
              />
            </Box>
            <Box minWidth={35}>
              <Typography variant="body2" color="text.secondary">
                {Math.round(stats.completionRate)}%
              </Typography>
            </Box>
          </Box>
        </Paper>
      </Grid>

      {/* Charts Section */}
      <Grid item xs={12} md={6}>
        <Paper sx={{ p: 3, height: 400 }}>
          <Typography variant="h6" gutterBottom>
            Task Status Distribution
          </Typography>
          <ResponsiveContainer width="100%" height="85%">
            <PieChart>
              <Pie
                data={statusDistributionData}
                cx="50%"
                cy="50%"
                outerRadius={80}
                dataKey="value"
                label={({ name, value }) => `${name}: ${value}`}
              >
                {statusDistributionData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </Paper>
      </Grid>

      <Grid item xs={12} md={6}>
        <Paper sx={{ p: 3, height: 400 }}>
          <Typography variant="h6" gutterBottom>
            Priority Distribution
          </Typography>
          <ResponsiveContainer width="100%" height="85%">
            <BarChart data={priorityDistributionData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="value" fill="#8884d8" />
            </BarChart>
          </ResponsiveContainer>
        </Paper>
      </Grid>

      {/* Recent Tasks Section */}
      <Grid item xs={12}>
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            Recent Tasks
          </Typography>
          <Grid container spacing={2}>
            {recentTasks.slice(0, 6).map((task) => (
              <Grid item xs={12} sm={6} md={4} key={task.id}>
                <Card variant="outlined" sx={{ height: "100%" }}>
                  <CardContent sx={{ pb: 2 }}>
                    <Box
                      display="flex"
                      justifyContent="space-between"
                      alignItems="flex-start"
                      mb={1}
                    >
                      <Typography variant="subtitle2" noWrap sx={{ pr: 1 }}>
                        {task.title}
                      </Typography>
                      <Chip
                        label={task.status}
                        size="small"
                        color={getStatusChipColor(task.status)}
                      />
                    </Box>
                    <Typography variant="body2" color="text.secondary" noWrap>
                      Assigned to: {task.assignee}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      Due: {formatDate(task.dueDate)}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Paper>
      </Grid>
    </Grid>
  );
};

export default DashboardOverview;
