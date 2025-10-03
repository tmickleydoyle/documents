import React from "react";
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
} from "@mui/material";
import {
  Edit as EditIcon,
  Delete as DeleteIcon,
  AccessTime as TimeIcon,
  Person as PersonIcon,
} from "@mui/icons-material";
import { format } from "date-fns";
import { Task, TaskPriority, TaskStatus } from "../types";

interface TaskCardProps {
  task: Task;
  onEdit: (task: Task) => void;
  onDelete: (taskId: string) => void;
  onStatusChange: (taskId: string, status: TaskStatus) => void;
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

const TaskCard: React.FC<TaskCardProps> = ({
  task,
  onEdit,
  onDelete,
  onStatusChange,
}) => {
  const isOverdue =
    task.dueDate &&
    new Date(task.dueDate) < new Date() &&
    task.status !== "completed";

  const handleStatusClick = () => {
    const statusOrder: TaskStatus[] = [
      "todo",
      "in-progress",
      "review",
      "completed",
    ];
    const currentIndex = statusOrder.indexOf(task.status);
    const nextStatus = statusOrder[(currentIndex + 1) % statusOrder.length];
    onStatusChange(task.id, nextStatus);
  };

  return (
    <Card
      sx={{
        height: "100%",
        display: "flex",
        flexDirection: "column",
        position: "relative",
        border: isOverdue ? "2px solid" : "1px solid",
        borderColor: isOverdue ? "error.main" : "divider",
        "&:hover": {
          boxShadow: 3,
          transform: "translateY(-2px)",
          transition: "all 0.2s ease-in-out",
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

        <Box display="flex" alignItems="center" gap={1}>
          <TimeIcon fontSize="small" color="action" />
          <Typography
            variant="body2"
            color={isOverdue ? "error.main" : "text.secondary"}
          >
            Due: {format(new Date(task.dueDate), "MMM dd, yyyy")}
          </Typography>
        </Box>

        {task.estimatedHours && (
          <Typography
            variant="caption"
            color="text.secondary"
            display="block"
            mt={1}
          >
            Est: {task.estimatedHours}h
            {task.completedHours && ` / Completed: ${task.completedHours}h`}
          </Typography>
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
              onClick={() => onEdit(task)}
              color="primary"
            >
              <EditIcon fontSize="small" />
            </IconButton>
          </Tooltip>
          <Tooltip title="Delete Task">
            <IconButton
              size="small"
              onClick={() => onDelete(task.id)}
              color="error"
            >
              <DeleteIcon fontSize="small" />
            </IconButton>
          </Tooltip>
        </Box>
      </CardActions>
    </Card>
  );
};

export default TaskCard;
