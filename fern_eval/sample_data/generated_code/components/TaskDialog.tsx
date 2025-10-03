import React, { useState } from "react";
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Button,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Grid,
  Chip,
  Box,
} from "@mui/material";

interface TaskDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: (taskData: any) => void;
  usersList: any[];
  taskData?: any;
  dialogMode: string;
}

function TaskDialog(props: TaskDialogProps) {
  const { isOpen, onClose, onSave, usersList, taskData, dialogMode } = props;

  const [formData, setFormData] = useState({
    taskTitle: taskData?.taskTitle || "",
    taskDescription: taskData?.taskDescription || "",
    taskPriority: taskData?.taskPriority || "normal",
    assignedTo: taskData?.assignedTo || "",
    dueDateTime: taskData?.dueDateTime?.split("T")[0] || "",
    estimatedTime: taskData?.estimatedTime || "",
    taskTags: taskData?.taskTags || [],
  });

  const [newTag, setNewTag] = useState("");

  const handleInputChange = (field: string, value: any) => {
    setFormData((prev) => ({
      ...prev,
      [field]: value,
    }));
  };

  const handleSubmit = () => {
    if (
      !formData.taskTitle ||
      !formData.taskDescription ||
      !formData.assignedTo ||
      !formData.dueDateTime
    ) {
      alert("Please fill in all required fields");
      return;
    }

    onSave(formData);
    onClose();
    resetForm();
  };

  const resetForm = () => {
    setFormData({
      taskTitle: "",
      taskDescription: "",
      taskPriority: "normal",
      assignedTo: "",
      dueDateTime: "",
      estimatedTime: "",
      taskTags: [],
    });
    setNewTag("");
  };

  const addTag = () => {
    if (newTag && !formData.taskTags.includes(newTag)) {
      setFormData((prev) => ({
        ...prev,
        taskTags: [...prev.taskTags, newTag],
      }));
      setNewTag("");
    }
  };

  const removeTag = (tagToRemove: string) => {
    setFormData((prev) => ({
      ...prev,
      taskTags: prev.taskTags.filter((tag) => tag !== tagToRemove),
    }));
  };

  const commonTags = [
    "Frontend",
    "Backend",
    "Design",
    "Bug Fix",
    "Feature",
    "Testing",
    "Documentation",
  ];

  return (
    <Dialog open={isOpen} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>
        {dialogMode === "edit" ? "Edit Task" : "Create New Task"}
      </DialogTitle>

      <DialogContent>
        <Grid container spacing={2} style={{ marginTop: "8px" }}>
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Task Title *"
              value={formData.taskTitle}
              onChange={(e) => handleInputChange("taskTitle", e.target.value)}
            />
          </Grid>

          <Grid item xs={12}>
            <TextField
              fullWidth
              multiline
              rows={3}
              label="Task Description *"
              value={formData.taskDescription}
              onChange={(e) =>
                handleInputChange("taskDescription", e.target.value)
              }
            />
          </Grid>

          <Grid item xs={6}>
            <FormControl fullWidth>
              <InputLabel>Priority</InputLabel>
              <Select
                value={formData.taskPriority}
                onChange={(e) =>
                  handleInputChange("taskPriority", e.target.value)
                }
              >
                <MenuItem value="low">Low</MenuItem>
                <MenuItem value="normal">Normal</MenuItem>
                <MenuItem value="high">High</MenuItem>
                <MenuItem value="critical">Critical</MenuItem>
              </Select>
            </FormControl>
          </Grid>

          <Grid item xs={6}>
            <FormControl fullWidth>
              <InputLabel>Assign To *</InputLabel>
              <Select
                value={formData.assignedTo}
                onChange={(e) =>
                  handleInputChange("assignedTo", e.target.value)
                }
              >
                {usersList.map((user) => (
                  <MenuItem key={user.userId} value={user.userName}>
                    {user.userName} - {user.userRole}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>

          <Grid item xs={6}>
            <TextField
              fullWidth
              type="date"
              label="Due Date *"
              InputLabelProps={{ shrink: true }}
              value={formData.dueDateTime}
              onChange={(e) => handleInputChange("dueDateTime", e.target.value)}
            />
          </Grid>

          <Grid item xs={6}>
            <TextField
              fullWidth
              type="number"
              label="Estimated Hours"
              value={formData.estimatedTime}
              onChange={(e) =>
                handleInputChange("estimatedTime", e.target.value)
              }
            />
          </Grid>

          <Grid item xs={12}>
            <Box display="flex" alignItems="center" gap={1} marginBottom={1}>
              <TextField
                size="small"
                label="Add Tag"
                value={newTag}
                onChange={(e) => setNewTag(e.target.value)}
                onKeyPress={(e) => e.key === "Enter" && addTag()}
              />
              <Button onClick={addTag} variant="outlined" size="small">
                Add
              </Button>
            </Box>

            <Box marginBottom={2}>
              {commonTags.map((tag) => (
                <Chip
                  key={tag}
                  label={tag}
                  onClick={() => {
                    if (!formData.taskTags.includes(tag)) {
                      setFormData((prev) => ({
                        ...prev,
                        taskTags: [...prev.taskTags, tag],
                      }));
                    }
                  }}
                  style={{ margin: "2px", cursor: "pointer" }}
                  variant="outlined"
                />
              ))}
            </Box>

            <Box>
              {formData.taskTags.map((tag, index) => (
                <Chip
                  key={index}
                  label={tag}
                  onDelete={() => removeTag(tag)}
                  style={{ margin: "2px" }}
                  color="primary"
                />
              ))}
            </Box>
          </Grid>
        </Grid>
      </DialogContent>

      <DialogActions>
        <Button
          onClick={() => {
            onClose();
            resetForm();
          }}
        >
          Cancel
        </Button>
        <Button onClick={handleSubmit} variant="contained">
          {dialogMode === "edit" ? "Update" : "Create"}
        </Button>
      </DialogActions>
    </Dialog>
  );
}

export default TaskDialog;
