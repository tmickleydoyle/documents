import React, { useState, useEffect, useCallback, useMemo } from "react";
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
  Alert,
  FormHelperText,
  CircularProgress,
  Divider,
  IconButton,
} from "@mui/material";
import {
  Close as CloseIcon,
  Save as SaveIcon,
  Add as AddIcon,
} from "@mui/icons-material";
import { useForm, Controller } from "react-hook-form";
import { yupResolver } from "@hookform/resolvers/yup";
import * as yup from "yup";
import { TaskFormData, TaskPriority, User } from "../types";

interface TaskFormProps {
  open: boolean;
  onClose: () => void;
  onSubmit: (data: TaskFormData) => void;
  users: User[];
  initialData?: Partial<TaskFormData>;
  mode: "create" | "edit";
  loading?: boolean;
  error?: string | null;
  onClearError?: () => void;
}

// Validation schema using Yup
const taskFormSchema = yup.object().shape({
  title: yup
    .string()
    .required("Task title is required")
    .min(3, "Title must be at least 3 characters")
    .max(100, "Title must not exceed 100 characters"),
  description: yup
    .string()
    .required("Description is required")
    .min(10, "Description must be at least 10 characters")
    .max(500, "Description must not exceed 500 characters"),
  priority: yup
    .string()
    .oneOf(["low", "medium", "high", "urgent"], "Invalid priority")
    .required("Priority is required"),
  assignee: yup
    .string()
    .required("Please assign this task to someone"),
  dueDate: yup
    .date()
    .required("Due date is required")
    .min(new Date(), "Due date cannot be in the past"),
  estimatedHours: yup
    .number()
    .nullable()
    .min(0.5, "Estimated hours must be at least 0.5")
    .max(1000, "Estimated hours must not exceed 1000"),
  tags: yup
    .array()
    .of(yup.string())
    .max(10, "Maximum 10 tags allowed"),
});

const TaskForm: React.FC<TaskFormProps> = ({
  open,
  onClose,
  onSubmit,
  users,
  initialData,
  mode,
  loading = false,
  error = null,
  onClearError,
}) => {
  const [tagList, setTagList] = useState<string[]>(initialData?.tags || []);

  // Memoized default values to prevent unnecessary re-renders
  const defaultValues = useMemo(() => ({
    title: initialData?.title || "",
    description: initialData?.description || "",
    priority: initialData?.priority || "medium",
    assignee: initialData?.assignee || "",
    dueDate: initialData?.dueDate 
      ? new Date(initialData.dueDate).toISOString().split('T')[0] 
      : "",
    estimatedHours: initialData?.estimatedHours || undefined,
    tags: initialData?.tags || [],
  }), [initialData]);

  const formController = useForm<TaskFormData>({
    defaultValues,
    resolver: yupResolver(taskFormSchema),
    mode: "onChange", // Validate on change for better UX
  });

  const { control, handleSubmit, formState, reset, setValue } = formController;
  const { errors } = formState;

  // Effect to sync tags when initial data changes
  useEffect(() => {
    if (initialData?.tags) {
      setTagList(initialData.tags);
    }
  }, [initialData?.tags]);

  const onFormSubmit = useCallback(async (data: TaskFormData) => {
    try {
      if (onClearError) onClearError();
      
      const formData = { 
        ...data, 
        tags: tagList,
        dueDate: new Date(data.dueDate),
      };
      
      await onSubmit(formData);
      
      if (!loading && !error) {
        reset();
        setTagList([]);
        onClose();
      }
    } catch (err) {
      console.error('Error submitting task form:', err);
    }
  }, [tagList, onSubmit, loading, error, reset, onClose, onClearError]);

  const handleClose = useCallback(() => {
    if (!loading) {
      reset();
      setTagList([]);
      if (onClearError) onClearError();
      onClose();
    }
  }, [loading, reset, onClose, onClearError]);

  const addTag = useCallback((newTag: string) => {
    if (newTag && !tagList.includes(newTag) && tagList.length < 10) {
      const updatedTagList = [...tagList, newTag.trim()];
      setTagList(updatedTagList);
      setValue("tags", updatedTagList);
    }
  }, [tagList, setValue]);

  const removeTag = useCallback((tagToRemove: string) => {
    const updatedTagList = tagList.filter((tag) => tag !== tagToRemove);
    setTagList(updatedTagList);
    setValue("tags", updatedTagList);
  }, [tagList, setValue]);

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
      onClose={handleClose}
      maxWidth="md"
      fullWidth
      disableEscapeKeyDown={loading}
      PaperProps={{
        sx: { borderRadius: 2 },
        "aria-labelledby": "task-form-dialog-title",
      }}
    >
      <DialogTitle
        id="task-form-dialog-title"
        sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}
      >
        <Typography variant="h5" component="h2">
          {mode === "create" ? "Create New Task" : "Edit Task"}
        </Typography>
        <IconButton
          aria-label="close"
          onClick={handleClose}
          disabled={loading}
          sx={{ color: 'grey.500' }}
        >
          <CloseIcon />
        </IconButton>
      </DialogTitle>
      
      {error && (
        <Alert 
          severity="error" 
          sx={{ mx: 3, mt: 2 }}
          onClose={onClearError}
        >
          {error}
        </Alert>
      )}

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

        <DialogActions sx={{ p: 3, gap: 1 }}>
          <Button 
            onClick={handleClose} 
            color="inherit"
            disabled={loading}
            size="large"
          >
            Cancel
          </Button>
          <Button
            type="submit"
            variant="contained"
            color="primary"
            size="large"
            disabled={loading || !formState.isValid}
            startIcon={loading ? <CircularProgress size={16} /> : <SaveIcon />}
            sx={{ minWidth: 140 }}
          >
            {loading 
              ? 'Saving...' 
              : mode === "create" 
                ? "Create Task" 
                : "Update Task"
            }
          </Button>
        </DialogActions>
      </form>
    </Dialog>
  );
};

export default TaskForm;
