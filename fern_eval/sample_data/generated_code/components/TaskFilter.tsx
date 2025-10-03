import React, { useState } from "react";
import {
  TextField,
  Button,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Box,
  Grid,
} from "@mui/material";

interface FilterProps {
  onSearch: (term: string) => void;
  onStatusFilter: (status: string) => void;
  onPriorityFilter: (priority: string) => void;
  onAssigneeFilter: (assignee: string) => void;
  onClearAll: () => void;
  assigneeList: string[];
}

function TaskFilter(props: FilterProps) {
  const {
    onSearch,
    onStatusFilter,
    onPriorityFilter,
    onAssigneeFilter,
    onClearAll,
    assigneeList,
  } = props;

  const [searchValue, setSearchValue] = useState("");
  const [statusValue, setStatusValue] = useState("all");
  const [priorityValue, setPriorityValue] = useState("all");
  const [assigneeValue, setAssigneeValue] = useState("all");
  const [showAdvanced, setShowAdvanced] = useState(false);

  const handleSearchChange = (e: any) => {
    const value = e.target.value;
    setSearchValue(value);
    onSearch(value);
  };

  const handleStatusChange = (e: any) => {
    const value = e.target.value;
    setStatusValue(value);
    onStatusFilter(value);
  };

  const handlePriorityChange = (e: any) => {
    const value = e.target.value;
    setPriorityValue(value);
    onPriorityFilter(value);
  };

  const handleAssigneeChange = (e: any) => {
    const value = e.target.value;
    setAssigneeValue(value);
    onAssigneeFilter(value);
  };

  const resetAllFilters = () => {
    setSearchValue("");
    setStatusValue("all");
    setPriorityValue("all");
    setAssigneeValue("all");
    onClearAll();
  };

  const hasFilters =
    searchValue !== "" ||
    statusValue !== "all" ||
    priorityValue !== "all" ||
    assigneeValue !== "all";

  return (
    <Box
      style={{
        marginBottom: "20px",
        padding: "16px",
        border: "1px solid #e0e0e0",
        borderRadius: "8px",
      }}
    >
      <Grid container spacing={2} alignItems="center">
        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            placeholder="Search tasks..."
            value={searchValue}
            onChange={handleSearchChange}
            variant="outlined"
            size="small"
          />
        </Grid>

        <Grid item xs={12} md={6}>
          <Box display="flex" gap={1} justifyContent="flex-end">
            <Button
              variant="outlined"
              onClick={() => setShowAdvanced(!showAdvanced)}
              color={hasFilters ? "primary" : "inherit"}
            >
              {showAdvanced ? "Hide Filters" : "Show Filters"}
            </Button>

            {hasFilters && (
              <Button onClick={resetAllFilters} color="secondary">
                Clear All
              </Button>
            )}
          </Box>
        </Grid>
      </Grid>

      {showAdvanced && (
        <Grid container spacing={2} style={{ marginTop: "16px" }}>
          <Grid item xs={12} sm={4}>
            <FormControl fullWidth size="small">
              <InputLabel>Status</InputLabel>
              <Select value={statusValue} onChange={handleStatusChange}>
                <MenuItem value="all">All</MenuItem>
                <MenuItem value="pending">Pending</MenuItem>
                <MenuItem value="active">Active</MenuItem>
                <MenuItem value="testing">Testing</MenuItem>
                <MenuItem value="done">Done</MenuItem>
              </Select>
            </FormControl>
          </Grid>

          <Grid item xs={12} sm={4}>
            <FormControl fullWidth size="small">
              <InputLabel>Priority</InputLabel>
              <Select value={priorityValue} onChange={handlePriorityChange}>
                <MenuItem value="all">All</MenuItem>
                <MenuItem value="low">Low</MenuItem>
                <MenuItem value="normal">Normal</MenuItem>
                <MenuItem value="high">High</MenuItem>
                <MenuItem value="critical">Critical</MenuItem>
              </Select>
            </FormControl>
          </Grid>

          <Grid item xs={12} sm={4}>
            <FormControl fullWidth size="small">
              <InputLabel>Assignee</InputLabel>
              <Select value={assigneeValue} onChange={handleAssigneeChange}>
                <MenuItem value="all">All</MenuItem>
                {assigneeList.map((assignee, index) => (
                  <MenuItem key={index} value={assignee}>
                    {assignee}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
        </Grid>
      )}
    </Box>
  );
}

export default TaskFilter;
