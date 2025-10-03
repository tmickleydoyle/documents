import React, { useState, useEffect } from "react";
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  Box,
  Typography,
  Grid,
  Autocomplete,
} from "@mui/material";
import { useForm, Controller } from "react-hook-form";
import { TaskFormData, TaskPriority, User } from "../types";

interface TaskFormProps {
  open: boolean;
  onClose: () => void;
  onSubmit: (data: TaskFormData) => void;
  users: User[];
  initialData?: Partial<TaskFormData>;
  mode: "create" | "edit";
}

const TaskForm: React.FC<TaskFormProps> = ({
  open,
  onClose,
  onSubmit,
  users,
  initialData,
  mode,
}) => {
  const [tagList, setTagList] = useState<string[]>(initialData?.tags || []);

  const formController = useForm<TaskFormData>({
    defaultValues: {
      title: initialData?.title || "",
      description: initialData?.description || "",
      priority: initialData?.priority || "medium",
      assignee: initialData?.assignee || "",
      dueDate: initialData?.dueDate || "",
      estimatedHours: initialData?.estimatedHours || undefined,
      tags: initialData?.tags || [],
    },
  });

  const { control, handleSubmit, formState, reset, setValue } = formController;
  const { errors } = formState;

  // Effect to sync tags when initial data changes
  useEffect(() => {
    if (initialData?.tags) {
      setTagList(initialData.tags);
    }
  }, [initialData?.tags]);

  const onFormSubmit = (data: TaskFormData) => {
    const formData = { ...data, tags: tagList };
    onSubmit(formData);
    reset();
    setTagList([]);
    onClose();
  };

  const addTag = (newTag: string) => {
    if (newTag && !tagList.includes(newTag)) {
      const updatedTagList = [...tagList, newTag];
      setTagList(updatedTagList);
      setValue("tags", updatedTagList);
    }
  };

  const removeTag = (tagToRemove: string) => {
    const updatedTagList = tagList.filter((tag) => tag !== tagToRemove);
    setTagList(updatedTagList);
    setValue("tags", updatedTagList);
  };

  const availableTags = [
    "Frontend",
    "Backend",
    "UI/UX",
    "Bug",
    "Feature",
    "Testing",
    "Documentation",
    "Performance",
    "Security",
  ];

  const priorityOptions = [
    { value: "low", label: "Low" },
    { value: "medium", label: "Medium" },
    { value: "high", label: "High" },
    { value: "urgent", label: "Urgent" },
  ];

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="md"
      fullWidth
      PaperProps={{
        sx: { borderRadius: 2 },
      }}
    >
      <DialogTitle>
        <Typography variant="h5" component="h2">
          {mode === "create" ? "Create New Task" : "Edit Task"}
        </Typography>
      </DialogTitle>

      <form onSubmit={handleSubmit(onFormSubmit)}>
        <DialogContent dividers>
          <Grid container spacing={3}>
            {/* Task Title Field */}
            <Grid item xs={12}>
              <Controller
                name="title"
                control={control}
                rules={{ required: "Task title is required" }}
                render={({ field }) => (
                  <TextField
                    {...field}
                    fullWidth
                    label="Task Title"
                    error={!!errors.title}
                    helperText={errors.title?.message}
                    variant="outlined"
                  />
                )}
              />
            </Grid>

            {/* Description Field */}
            <Grid item xs={12}>
              <Controller
                name="description"
                control={control}
                rules={{ required: "Description is required" }}
                render={({ field }) => (
                  <TextField
                    {...field}
                    fullWidth
                    label="Description"
                    multiline
                    rows={4}
                    error={!!errors.description}
                    helperText={errors.description?.message}
                    variant="outlined"
                  />
                )}
              />
            </Grid>

            {/* Priority and Assignee Row */}
            <Grid item xs={12} sm={6}>
              <Controller
                name="priority"
                control={control}
                render={({ field }) => (
                  <FormControl fullWidth>
                    <InputLabel>Priority</InputLabel>
                    <Select {...field} label="Priority">
                      {priorityOptions.map((option) => (
                        <MenuItem key={option.value} value={option.value}>
                          {option.label}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                )}
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <Controller
                name="assignee"
                control={control}
                rules={{ required: "Please assign this task to someone" }}
                render={({ field }) => (
                  <FormControl fullWidth error={!!errors.assignee}>
                    <InputLabel>Assignee</InputLabel>
                    <Select {...field} label="Assignee">
                      {users.map((user) => (
                        <MenuItem key={user.id} value={user.name}>
                          {user.name} ({user.role})
                        </MenuItem>
                      ))}
                    </Select>
                    {errors.assignee && (
                      <Typography
                        variant="caption"
                        color="error"
                        sx={{ mt: 0.5, ml: 1.5 }}
                      >
                        {errors.assignee.message}
                      </Typography>
                    )}
                  </FormControl>
                )}
              />
            </Grid>

            {/* Due Date and Estimated Hours Row */}
            <Grid item xs={12} sm={6}>
              <Controller
                name="dueDate"
                control={control}
                rules={{ required: "Due date is required" }}
                render={({ field }) => (
                  <TextField
                    {...field}
                    fullWidth
                    label="Due Date"
                    type="date"
                    InputLabelProps={{ shrink: true }}
                    error={!!errors.dueDate}
                    helperText={errors.dueDate?.message}
                  />
                )}
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <Controller
                name="estimatedHours"
                control={control}
                render={({ field }) => (
                  <TextField
                    {...field}
                    fullWidth
                    label="Estimated Hours"
                    type="number"
                    inputProps={{ min: 0, step: 0.5 }}
                  />
                )}
              />
            </Grid>

            {/* Tags Section */}
            <Grid item xs={12}>
              <Typography variant="subtitle2" gutterBottom>
                Tags
              </Typography>
              <Autocomplete
                multiple
                freeSolo
                options={availableTags}
                value={tagList}
                onChange={(event, newValue) => {
                  setTagList(newValue);
                  setValue("tags", newValue);
                }}
                renderTags={(value, getTagProps) =>
                  value.map((option, index) => (
                    <Chip
                      variant="outlined"
                      label={option}
                      {...getTagProps({ index })}
                      key={option}
                    />
                  ))
                }
                renderInput={(params) => (
                  <TextField
                    {...params}
                    placeholder="Add tags..."
                    variant="outlined"
                  />
                )}
              />
            </Grid>
          </Grid>
        </DialogContent>

        <DialogActions sx={{ p: 3 }}>
          <Button onClick={onClose} color="inherit">
            Cancel
          </Button>
          <Button
            type="submit"
            variant="contained"
            color="primary"
            sx={{ minWidth: 100 }}
          >
            {mode === "create" ? "Create Task" : "Update Task"}
          </Button>
        </DialogActions>
      </form>
    </Dialog>
  );
};

export default TaskForm;
