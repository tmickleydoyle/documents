import React, { memo, useCallback, useMemo } from "react";
import {
  Card,
  CardContent,
  CardActions,
  Typography,
  Chip,
  IconButton,
  Box,
  Tooltip,
  Avatar,
  LinearProgress,
  Alert,
  Skeleton,
} from "@mui/material";
import {
  Edit as EditIcon,
  Delete as DeleteIcon,
  AccessTime as TimeIcon,
  Person as PersonIcon,
  Warning as WarningIcon,
  CheckCircle as CheckCircleIcon,
  Schedule as ScheduleIcon,
} from "@mui/icons-material";
import { format, isValid, parseISO, differenceInDays } from "date-fns";
import { TaskItem, TaskPriority, TaskStatus } from "../types";

interface TaskCardProps {
  task: TaskItem;
  onEdit: (task: TaskItem) => void;
  onDelete: (taskId: string) => void;
  onStatusChange: (taskId: string, status: TaskStatus) => void;
  loading?: boolean;
  disabled?: boolean;
  compact?: boolean;
  showProgress?: boolean;
}

const getPriorityColor = (priority: TaskPriority) => {
  switch (priority) {
    case "urgent":
      return "error";
    case "high":
      return "warning";
    case "medium":
      return "info";
    case "low":
      return "success";
    default:
      return "default";
  }
};

const getStatusColor = (status: TaskStatus) => {
  switch (status) {
    case "completed":
      return "success";
    case "in-progress":
      return "primary";
    case "review":
      return "warning";
    case "todo":
      return "default";
    default:
      return "default";
  }
};

const TaskCard: React.FC<TaskCardProps> = memo(({
  task,
  onEdit,
  onDelete,
  onStatusChange,
  loading = false,
  disabled = false,
  compact = false,
  showProgress = true,
}) => {
  // Memoized calculations for performance
  const { isOverdue, daysUntilDue, completionPercentage, formattedDueDate } = useMemo(() => {
    if (!task.dueDate) {
      return {
        isOverdue: false,
        daysUntilDue: null,
        completionPercentage: 0,
        formattedDueDate: 'No due date'
      };
    }

    const dueDate = typeof task.dueDate === 'string' ? parseISO(task.dueDate) : task.dueDate;
    if (!isValid(dueDate)) {
      return {
        isOverdue: false,
        daysUntilDue: null,
        completionPercentage: 0,
        formattedDueDate: 'Invalid date'
      };
    }

    const now = new Date();
    const isOverdue = dueDate < now && task.status !== "completed";
    const daysUntilDue = differenceInDays(dueDate, now);
    const completionPercentage = task.estimatedHours && task.completedHours 
      ? Math.min(100, (task.completedHours / task.estimatedHours) * 100) 
      : 0;
    
    const formattedDueDate = format(dueDate, "MMM dd, yyyy");

    return { isOverdue, daysUntilDue, completionPercentage, formattedDueDate };
  }, [task.dueDate, task.status, task.estimatedHours, task.completedHours]);

  // Memoized event handlers
  const handleStatusClick = useCallback(() => {
    if (disabled || loading) return;
    
    try {
      const statusOrder: TaskStatus[] = [
        "todo",
        "in-progress",
        "review",
        "completed",
      ];
      const currentIndex = statusOrder.indexOf(task.status);
      const nextStatus = statusOrder[(currentIndex + 1) % statusOrder.length];
      onStatusChange(task.id, nextStatus);
    } catch (error) {
      console.error('Error changing task status:', error);
    }
  }, [task.id, task.status, onStatusChange, disabled, loading]);

  const handleEditClick = useCallback(() => {
    if (disabled || loading) return;
    
    try {
      onEdit(task);
    } catch (error) {
      console.error('Error editing task:', error);
    }
  }, [task, onEdit, disabled, loading]);

  const handleDeleteClick = useCallback(() => {
    if (disabled || loading) return;
    
    try {
      onDelete(task.id);
    } catch (error) {
      console.error('Error deleting task:', error);
    }
  }, [task.id, onDelete, disabled, loading]);

  // Show loading skeleton if loading
  if (loading) {
    return (
      <Card sx={{ height: "100%", p: 2 }}>
        <Skeleton variant="text" width="80%" height={40} />
        <Skeleton variant="text" width="60%" height={20} sx={{ mt: 1 }} />
        <Skeleton variant="rectangular" width="100%" height={60} sx={{ mt: 2 }} />
        <Box sx={{ mt: 2, display: 'flex', gap: 1 }}>
          <Skeleton variant="circular" width={32} height={32} />
          <Skeleton variant="circular" width={32} height={32} />
        </Box>
      </Card>
    );
  }

  // Error boundary for malformed task data
  if (!task || !task.id) {
    return (
      <Card sx={{ height: "100%", p: 2 }}>
        <Alert severity="error" sx={{ height: '100%', display: 'flex', alignItems: 'center' }}>
          <WarningIcon sx={{ mr: 1 }} />
          Invalid task data
        </Alert>
      </Card>
    );
  }

  return (
    <Card
      role="article"
      aria-label={`Task: ${task.title || 'Untitled'}`}
      tabIndex={0}
      sx={{
        height: compact ? "auto" : "100%",
        display: "flex",
        flexDirection: "column",
        position: "relative",
        border: isOverdue ? "2px solid" : "1px solid",
        borderColor: isOverdue ? "error.main" : "divider",
        opacity: disabled ? 0.7 : 1,
        pointerEvents: disabled ? 'none' : 'auto',
        "&:hover": !disabled ? {
          boxShadow: 3,
          transform: "translateY(-2px)",
          transition: "all 0.2s ease-in-out",
        } : {},
        "&:focus": {
          outline: '2px solid',
          outlineColor: 'primary.main',
          outlineOffset: '2px',
        },
      }}
    >
      <CardContent sx={{ flexGrow: 1, pb: 1 }}>
        <Box
          display="flex"
          justifyContent="space-between"
          alignItems="flex-start"
          mb={1}
        >
          <Typography variant="h6" component="h3" noWrap sx={{ pr: 1 }}>
            {task.title}
          </Typography>
          <Chip
            label={task.priority}
            size="small"
            color={getPriorityColor(task.priority)}
            variant="outlined"
          />
        </Box>

        <Typography
          variant="body2"
          color="text.secondary"
          sx={{
            mb: 2,
            overflow: "hidden",
            textOverflow: "ellipsis",
            display: "-webkit-box",
            WebkitLineClamp: 2,
            WebkitBoxOrient: "vertical",
          }}
        >
          {task.description}
        </Typography>

        <Box display="flex" flexWrap="wrap" gap={0.5} mb={2}>
          {task.tags.map((tag) => (
            <Chip
              key={tag}
              label={tag}
              size="small"
              variant="outlined"
              sx={{ fontSize: "0.7rem", height: 20 }}
            />
          ))}
        </Box>

        <Box display="flex" alignItems="center" gap={1} mb={1}>
          <PersonIcon fontSize="small" color="action" />
          <Typography variant="body2" color="text.secondary">
            {task.assignee}
          </Typography>
        </Box>

        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Typography
            variant="body2"
            color={isOverdue ? "error.main" : "text.secondary"}
            sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}
          >
            {isOverdue ? (
              <WarningIcon fontSize="small" color="error" />
            ) : task.status === 'completed' ? (
              <CheckCircleIcon fontSize="small" color="success" />
            ) : (
              <ScheduleIcon fontSize="small" color="action" />
            )}
            Due: {formattedDueDate}
          </Typography>
          {daysUntilDue !== null && (
            <Typography
              variant="caption"
              color={isOverdue ? "error.main" : daysUntilDue <= 1 ? "warning.main" : "text.secondary"}
              sx={{ fontWeight: 'medium' }}
            >
              {daysUntilDue === 0 ? 'Today' : 
               daysUntilDue === 1 ? 'Tomorrow' :
               daysUntilDue < 0 ? `${Math.abs(daysUntilDue)} days overdue` :
               `${daysUntilDue} days left`}
            </Typography>
          )}
        </Box>

        {task.estimatedHours && (
          <Box sx={{ mt: 1 }}>
            <Typography
              variant="caption"
              color="text.secondary"
              display="block"
            >
              Estimated: {task.estimatedHours}h
              {task.completedHours && ` / Completed: ${task.completedHours}h`}
            </Typography>
            {showProgress && task.completedHours && (
              <Box sx={{ mt: 0.5 }}>
                <LinearProgress
                  variant="determinate"
                  value={completionPercentage}
                  sx={{
                    height: 4,
                    borderRadius: 2,
                    '& .MuiLinearProgress-bar': {
                      borderRadius: 2,
                    },
                  }}
                />
                <Typography
                  variant="caption"
                  color="text.secondary"
                  sx={{ fontSize: '0.65rem' }}
                >
                  {Math.round(completionPercentage)}% complete
                </Typography>
              </Box>
            )}
          </Box>
        )}
      </CardContent>

      <CardActions sx={{ pt: 0, justifyContent: "space-between" }}>
        <Chip
          label={task.status.replace("-", " ")}
          size="small"
          color={getStatusColor(task.status)}
          onClick={handleStatusClick}
          sx={{
            cursor: "pointer",
            textTransform: "capitalize",
            "&:hover": { opacity: 0.8 },
          }}
        />

        <Box>
          <Tooltip title="Edit Task">
            <IconButton
              size="small"
              onClick={handleEditClick}
              color="primary"
              disabled={disabled || loading}
              aria-label={`Edit task ${task.title || 'Untitled'}`}
            >
              <EditIcon fontSize="small" />
            </IconButton>
          </Tooltip>
          <Tooltip title="Delete Task">
            <IconButton
              size="small"
              onClick={handleDeleteClick}
              color="error"
              disabled={disabled || loading}
              aria-label={`Delete task ${task.title || 'Untitled'}`}
            >
              <DeleteIcon fontSize="small" />
            </IconButton>
          </Tooltip>
        </Box>
      </CardActions>
    </Card>
  );
});

TaskCard.displayName = 'TaskCard';

export default TaskCard;
