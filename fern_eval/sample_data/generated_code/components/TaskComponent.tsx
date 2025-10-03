import React from "react";
import {
  Card,
  CardContent,
  CardActions,
  Typography,
  Chip,
  Button,
  Box,
} from "@mui/material";
import moment from "moment";

interface TaskProps {
  task: any;
  onEdit: (task: any) => void;
  onDelete: (id: string) => void;
  onStatusUpdate: (id: string, newStatus: string) => void;
}

const TaskComponent = (props: TaskProps) => {
  const { task, onEdit, onDelete, onStatusUpdate } = props;

  const getPriorityColor = (priority: string) => {
    if (priority === "critical") return "error";
    if (priority === "high") return "warning";
    if (priority === "normal") return "info";
    return "success";
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "done":
        return "success";
      case "active":
        return "primary";
      case "testing":
        return "warning";
      default:
        return "default";
    }
  };

  const handleStatusChange = () => {
    const statuses = ["pending", "active", "testing", "done"];
    const currentIndex = statuses.indexOf(task.currentStatus);
    const nextStatus = statuses[(currentIndex + 1) % statuses.length];
    onStatusUpdate(task.id, nextStatus);
  };

  const isTaskOverdue = () => {
    return (
      moment(task.dueDateTime).isBefore(moment()) &&
      task.currentStatus !== "done"
    );
  };

  return (
    <Card
      style={{
        marginBottom: "16px",
        border: isTaskOverdue() ? "2px solid red" : "1px solid #e0e0e0",
      }}
    >
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="start">
          <Typography variant="h6" style={{ fontWeight: "bold" }}>
            {task.taskTitle}
          </Typography>
          <Chip
            label={task.taskPriority}
            color={getPriorityColor(task.taskPriority)}
            size="small"
          />
        </Box>

        <Typography
          variant="body2"
          color="textSecondary"
          style={{ margin: "8px 0" }}
        >
          {task.taskDescription}
        </Typography>

        <div style={{ marginBottom: "8px" }}>
          {task.taskTags.map((tag: string, index: number) => (
            <Chip
              key={index}
              label={tag}
              size="small"
              style={{ marginRight: "4px", marginBottom: "4px" }}
            />
          ))}
        </div>

        <Typography variant="body2" style={{ marginBottom: "4px" }}>
          Assigned to: {task.assignedTo}
        </Typography>

        <Typography
          variant="body2"
          style={{
            color: isTaskOverdue() ? "red" : "inherit",
          }}
        >
          Due: {moment(task.dueDateTime).format("MMM DD, YYYY")}
        </Typography>

        {task.estimatedTime && (
          <Typography variant="caption" display="block">
            Estimated: {task.estimatedTime}h
            {task.actualTime && ` | Actual: ${task.actualTime}h`}
          </Typography>
        )}
      </CardContent>

      <CardActions style={{ justifyContent: "space-between" }}>
        <Chip
          label={task.currentStatus.toUpperCase()}
          color={getStatusColor(task.currentStatus)}
          onClick={handleStatusChange}
          style={{ cursor: "pointer" }}
        />

        <div>
          <Button
            size="small"
            onClick={() => onEdit(task)}
            style={{ marginRight: "8px" }}
          >
            Edit
          </Button>
          <Button size="small" color="error" onClick={() => onDelete(task.id)}>
            Delete
          </Button>
        </div>
      </CardActions>
    </Card>
  );
};

export default TaskComponent;
