import React, { useState } from "react";
import {
  Box,
  TextField,
  InputAdornment,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  Button,
  Grid,
  Typography,
} from "@mui/material";
import {
  Search as SearchIcon,
  FilterList as FilterIcon,
  Clear as ClearIcon,
} from "@mui/icons-material";
import { TaskStatus, TaskPriority } from "../types";

interface TaskFiltersProps {
  searchTerm: string;
  statusFilter: TaskStatus | "all";
  priorityFilter: TaskPriority | "all";
  assigneeFilter: string;
  onSearchChange: (search: string) => void;
  onStatusFilterChange: (status: TaskStatus | "all") => void;
  onPriorityFilterChange: (priority: TaskPriority | "all") => void;
  onAssigneeFilterChange: (assignee: string) => void;
  onClearFilters: () => void;
  assignees: string[];
}

const TaskFilters: React.FC<TaskFiltersProps> = ({
  searchTerm,
  statusFilter,
  priorityFilter,
  assigneeFilter,
  onSearchChange,
  onStatusFilterChange,
  onPriorityFilterChange,
  onAssigneeFilterChange,
  onClearFilters,
  assignees,
}) => {
  const [showFilters, setShowFilters] = useState(false);

  const hasActiveFilters =
    searchTerm !== "" ||
    statusFilter !== "all" ||
    priorityFilter !== "all" ||
    assigneeFilter !== "";

  return (
    <Box sx={{ mb: 3 }}>
      <Grid container spacing={2} alignItems="center">
        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            variant="outlined"
            placeholder="Search tasks..."
            value={searchTerm}
            onChange={(e) => onSearchChange(e.target.value)}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon color="action" />
                </InputAdornment>
              ),
              endAdornment: searchTerm && (
                <InputAdornment position="end">
                  <Button
                    size="small"
                    onClick={() => onSearchChange("")}
                    sx={{ minWidth: "auto", p: 0.5 }}
                  >
                    <ClearIcon fontSize="small" />
                  </Button>
                </InputAdornment>
              ),
            }}
          />
        </Grid>

        <Grid item xs={12} md={6}>
          <Box
            display="flex"
            gap={1}
            alignItems="center"
            justifyContent="flex-end"
          >
            <Button
              variant="outlined"
              startIcon={<FilterIcon />}
              onClick={() => setShowFilters(!showFilters)}
              color={hasActiveFilters ? "primary" : "inherit"}
            >
              Filters
              {hasActiveFilters && (
                <Chip
                  size="small"
                  label="●"
                  sx={{
                    ml: 1,
                    height: 16,
                    width: 16,
                    "& .MuiChip-label": { p: 0 },
                  }}
                />
              )}
            </Button>

            {hasActiveFilters && (
              <Button
                variant="text"
                size="small"
                onClick={onClearFilters}
                startIcon={<ClearIcon />}
              >
                Clear
              </Button>
            )}
          </Box>
        </Grid>
      </Grid>

      {showFilters && (
        <Box
          sx={{
            mt: 2,
            p: 2,
            border: 1,
            borderColor: "divider",
            borderRadius: 1,
          }}
        >
          <Typography variant="subtitle2" gutterBottom>
            Filter Options
          </Typography>

          <Grid container spacing={2}>
            <Grid item xs={12} sm={4}>
              <FormControl fullWidth size="small">
                <InputLabel>Status</InputLabel>
                <Select
                  value={statusFilter}
                  onChange={(e) =>
                    onStatusFilterChange(e.target.value as TaskStatus | "all")
                  }
                  label="Status"
                >
                  <MenuItem value="all">All Statuses</MenuItem>
                  <MenuItem value="todo">To Do</MenuItem>
                  <MenuItem value="in-progress">In Progress</MenuItem>
                  <MenuItem value="review">Review</MenuItem>
                  <MenuItem value="completed">Completed</MenuItem>
                </Select>
              </FormControl>
            </Grid>

            <Grid item xs={12} sm={4}>
              <FormControl fullWidth size="small">
                <InputLabel>Priority</InputLabel>
                <Select
                  value={priorityFilter}
                  onChange={(e) =>
                    onPriorityFilterChange(
                      e.target.value as TaskPriority | "all"
                    )
                  }
                  label="Priority"
                >
                  <MenuItem value="all">All Priorities</MenuItem>
                  <MenuItem value="low">Low</MenuItem>
                  <MenuItem value="medium">Medium</MenuItem>
                  <MenuItem value="high">High</MenuItem>
                  <MenuItem value="urgent">Urgent</MenuItem>
                </Select>
              </FormControl>
            </Grid>

            <Grid item xs={12} sm={4}>
              <FormControl fullWidth size="small">
                <InputLabel>Assignee</InputLabel>
                <Select
                  value={assigneeFilter}
                  onChange={(e) => onAssigneeFilterChange(e.target.value)}
                  label="Assignee"
                >
                  <MenuItem value="">All Assignees</MenuItem>
                  {assignees.map((assignee) => (
                    <MenuItem key={assignee} value={assignee}>
                      {assignee}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
          </Grid>
        </Box>
      )}
    </Box>
  );
};

export default TaskFilters;
