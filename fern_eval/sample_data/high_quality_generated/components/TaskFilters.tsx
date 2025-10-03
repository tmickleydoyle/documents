import React, { useState, useCallback } from "react";
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
  Collapse,
} from "@mui/material";
import {
  Search as SearchIcon,
  FilterList as FilterIcon,
  Clear as ClearIcon,
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
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
  const [filtersExpanded, setFiltersExpanded] = useState(false);

  // Check if any filters are currently active
  const hasActiveFilters = useCallback(() => {
    return (
      searchTerm !== "" ||
      statusFilter !== "all" ||
      priorityFilter !== "all" ||
      assigneeFilter !== ""
    );
  }, [searchTerm, statusFilter, priorityFilter, assigneeFilter]);

  // Handle search input changes
  const handleSearchChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    onSearchChange(event.target.value);
  };

  // Handle clear search
  const handleClearSearch = () => {
    onSearchChange("");
  };

  // Toggle filter panel
  const toggleFilters = () => {
    setFiltersExpanded(!filtersExpanded);
  };

  // Status options for dropdown
  const statusOptions = [
    { value: "all", label: "All Statuses" },
    { value: "todo", label: "To Do" },
    { value: "in-progress", label: "In Progress" },
    { value: "review", label: "Review" },
    { value: "completed", label: "Completed" },
  ];

  // Priority options for dropdown
  const priorityOptions = [
    { value: "all", label: "All Priorities" },
    { value: "low", label: "Low" },
    { value: "medium", label: "Medium" },
    { value: "high", label: "High" },
    { value: "urgent", label: "Urgent" },
  ];

  return (
    <Box sx={{ mb: 3 }}>
      <Grid container spacing={2} alignItems="center">
        {/* Search Field */}
        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            variant="outlined"
            placeholder="Search tasks..."
            value={searchTerm}
            onChange={handleSearchChange}
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
                    onClick={handleClearSearch}
                    sx={{ minWidth: "auto", p: 0.5 }}
                  >
                    <ClearIcon fontSize="small" />
                  </Button>
                </InputAdornment>
              ),
            }}
          />
        </Grid>

        {/* Filter Controls */}
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
              endIcon={
                filtersExpanded ? <ExpandLessIcon /> : <ExpandMoreIcon />
              }
              onClick={toggleFilters}
              color={hasActiveFilters() ? "primary" : "inherit"}
            >
              Filters
              {hasActiveFilters() && (
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

            {hasActiveFilters() && (
              <Button
                variant="text"
                size="small"
                onClick={onClearFilters}
                startIcon={<ClearIcon />}
              >
                Clear All
              </Button>
            )}
          </Box>
        </Grid>
      </Grid>

      {/* Collapsible Filter Panel */}
      <Collapse in={filtersExpanded}>
        <Box
          sx={{
            mt: 2,
            p: 2,
            border: 1,
            borderColor: "divider",
            borderRadius: 1,
            backgroundColor: "background.paper",
          }}
        >
          <Typography variant="subtitle2" gutterBottom>
            Filter Options
          </Typography>

          <Grid container spacing={2}>
            {/* Status Filter */}
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
                  {statusOptions.map((option) => (
                    <MenuItem key={option.value} value={option.value}>
                      {option.label}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>

            {/* Priority Filter */}
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
                  {priorityOptions.map((option) => (
                    <MenuItem key={option.value} value={option.value}>
                      {option.label}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>

            {/* Assignee Filter */}
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
      </Collapse>
    </Box>
  );
};

export default TaskFilters;
