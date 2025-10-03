import React from "react";
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
  const statusDistribution = [
    {
      name: "To Do",
      value: tasks.filter((t) => t.status === "todo").length,
      color: "#9E9E9E",
    },
    {
      name: "In Progress",
      value: tasks.filter((t) => t.status === "in-progress").length,
      color: "#2196F3",
    },
    {
      name: "Review",
      value: tasks.filter((t) => t.status === "review").length,
      color: "#FF9800",
    },
    {
      name: "Completed",
      value: tasks.filter((t) => t.status === "completed").length,
      color: "#4CAF50",
    },
  ];

  const priorityDistribution = [
    { name: "Low", value: tasks.filter((t) => t.priority === "low").length },
    {
      name: "Medium",
      value: tasks.filter((t) => t.priority === "medium").length,
    },
    { name: "High", value: tasks.filter((t) => t.priority === "high").length },
    {
      name: "Urgent",
      value: tasks.filter((t) => t.priority === "urgent").length,
    },
  ];

  const StatCard = ({
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

  return (
    <Grid container spacing={3}>
      {/* Key Statistics */}
      <Grid item xs={12} sm={6} md={3}>
        <StatCard
          title="Total Tasks"
          value={stats.totalTasks}
          icon={<TaskIcon />}
          color="#1976d2"
        />
      </Grid>

      <Grid item xs={12} sm={6} md={3}>
        <StatCard
          title="Completed"
          value={stats.completedTasks}
          icon={<CompletedIcon />}
          color="#388e3c"
          subtitle={`${Math.round(stats.completionRate)}% completion rate`}
        />
      </Grid>

      <Grid item xs={12} sm={6} md={3}>
        <StatCard
          title="In Progress"
          value={stats.inProgressTasks}
          icon={<InProgressIcon />}
          color="#f57c00"
        />
      </Grid>

      <Grid item xs={12} sm={6} md={3}>
        <StatCard
          title="Overdue"
          value={stats.overdueTasks}
          icon={<OverdueIcon />}
          color="#d32f2f"
        />
      </Grid>

      {/* Progress Bar */}
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

      {/* Charts */}
      <Grid item xs={12} md={6}>
        <Paper sx={{ p: 3, height: 400 }}>
          <Typography variant="h6" gutterBottom>
            Task Status Distribution
          </Typography>
          <ResponsiveContainer width="100%" height="85%">
            <PieChart>
              <Pie
                data={statusDistribution}
                cx="50%"
                cy="50%"
                outerRadius={80}
                dataKey="value"
                label={({ name, value }) => `${name}: ${value}`}
              >
                {statusDistribution.map((entry, index) => (
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
            <BarChart data={priorityDistribution}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="value" fill="#8884d8" />
            </BarChart>
          </ResponsiveContainer>
        </Paper>
      </Grid>

      {/* Recent Tasks */}
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
                        color={
                          task.status === "completed"
                            ? "success"
                            : task.status === "in-progress"
                            ? "primary"
                            : task.status === "review"
                            ? "warning"
                            : "default"
                        }
                      />
                    </Box>
                    <Typography variant="body2" color="text.secondary" noWrap>
                      Assigned to: {task.assignee}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      Due: {new Date(task.dueDate).toLocaleDateString()}
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
