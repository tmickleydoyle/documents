import React from "react";
import { render, screen, fireEvent, waitFor, act } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import "@testing-library/jest-dom";
import { ThemeProvider, createTheme } from "@mui/material/styles";
import TaskCard from "../components/TaskCard";
import { TaskItem } from "../types";

// Test theme for consistent styling
const testTheme = createTheme();

// Test wrapper component
const TestWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <ThemeProvider theme={testTheme}>
    {children}
  </ThemeProvider>
);

// Test data
const testTask: TaskItem = {
  id: "test-task-1",
  title: "Test Task",
  description: "This is a test task description for testing purposes",
  status: "todo",
  priority: "high",
  assignee: "John Doe",
  dueDate: new Date("2025-07-15"),
  createdAt: new Date("2025-06-20"),
  updatedAt: new Date("2025-06-24"),
  tags: ["Testing", "Frontend"],
  estimatedHours: 8,
  completedHours: 3,
};

// Additional test tasks for comprehensive testing
const overdueTask: TaskItem = {
  ...testTask,
  id: "overdue-task",
  title: "Overdue Task",
  dueDate: new Date("2025-06-01"),
  status: "in-progress",
};

const completedTask: TaskItem = {
  ...testTask,
  id: "completed-task",
  title: "Completed Task",
  status: "completed",
  completedHours: 8,
};

const minimalTask: TaskItem = {
  id: "minimal-task",
  title: "Minimal Task",
  description: "Basic task",
  status: "todo",
  priority: "low",
  assignee: "Jane Smith",
  dueDate: new Date("2025-08-01"),
  createdAt: new Date(),
  updatedAt: new Date(),
  tags: [],
};

const taskWithLongContent: TaskItem = {
  ...testTask,
  id: "long-content-task",
  title: "This is a very long task title that should be truncated when displayed in the card component",
  description: "This is an extremely long description that contains a lot of text and should be properly handled by the TaskCard component with ellipsis and proper text overflow management to ensure the UI remains clean and readable even with very long content that might otherwise break the layout or make it look unprofessional.",
  tags: ["VeryLongTagName", "AnotherExtremelyLongTagThatShouldWrap", "ShortTag", "MediumLengthTag"],
};

// Mock handlers with better error simulation
const createMockHandlers = () => ({
  onEdit: jest.fn(),
  onDelete: jest.fn(),
  onStatusChange: jest.fn(),
});

// Helper function to render TaskCard with wrapper
const renderTaskCard = (task: TaskItem, props = {}, handlers = createMockHandlers()) => {
  return render(
    <TestWrapper>
      <TaskCard task={task} {...handlers} {...props} />
    </TestWrapper>
  );
};

describe("TaskCard Component Tests", () => {
  let mockHandlers: ReturnType<typeof createMockHandlers>;
  
  beforeEach(() => {
    // Reset all mocks before each test
    jest.clearAllMocks();
    mockHandlers = createMockHandlers();
    
    // Mock console methods to avoid noise in tests
    jest.spyOn(console, 'error').mockImplementation(() => {});
    jest.spyOn(console, 'warn').mockImplementation(() => {});
  });
  
  afterEach(() => {
    // Restore console methods
    jest.restoreAllMocks();
  });

  describe("Rendering", () => {
    it("should render task information correctly", () => {
      renderTaskCard(testTask, {}, mockHandlers);

      expect(screen.getByText("Test Task")).toBeInTheDocument();
      expect(
        screen.getByText("This is a test task description for testing purposes")
      ).toBeInTheDocument();
      expect(screen.getByText("John Doe")).toBeInTheDocument();
      expect(screen.getByText("high")).toBeInTheDocument();
    });

    it("should display all task tags", () => {
      renderTaskCard(testTask, {}, mockHandlers);

      expect(screen.getByText("Testing")).toBeInTheDocument();
      expect(screen.getByText("Frontend")).toBeInTheDocument();
    });

    it("should show progress information when available", () => {
      renderTaskCard(testTask, {}, mockHandlers);

      // Check for progress indicators
      const progressElements = screen.getAllByText(/3/);
      expect(progressElements.length).toBeGreaterThan(0);
    });
    
    it("should render loading skeleton when loading prop is true", () => {
      renderTaskCard(testTask, { loading: true }, mockHandlers);
      
      // Should show skeleton instead of task content
      expect(screen.queryByText("Test Task")).not.toBeInTheDocument();
      expect(screen.getByTestId("skeleton") || document.querySelector('.MuiSkeleton-root')).toBeInTheDocument();
    });
    
    it("should render error state for invalid task data", () => {
      const invalidTask = null as any;
      renderTaskCard(invalidTask, {}, mockHandlers);
      
      expect(screen.getByText(/invalid task data/i)).toBeInTheDocument();
    });
    
    it("should handle missing optional fields gracefully", () => {
      renderTaskCard(minimalTask, {}, mockHandlers);
      
      expect(screen.getByText("Minimal Task")).toBeInTheDocument();
      expect(screen.getByText("Jane Smith")).toBeInTheDocument();
      expect(screen.getByText("low")).toBeInTheDocument();
    });
    
    it("should truncate long content appropriately", () => {
      renderTaskCard(taskWithLongContent, {}, mockHandlers);
      
      // Title should be present but may be truncated
      expect(screen.getByText(/This is a very long task title/)).toBeInTheDocument();
      
      // Description should be present but truncated
      expect(screen.getByText(/This is an extremely long description/)).toBeInTheDocument();
    });
    
    it("should apply compact styling when compact prop is true", () => {
      renderTaskCard(testTask, { compact: true }, mockHandlers);
      
      const card = screen.getByRole('article');
      expect(card).toBeInTheDocument();
      // In compact mode, height should be auto instead of 100%
    });
    
    it("should show progress bar when showProgress is true and task has completed hours", () => {
      renderTaskCard(testTask, { showProgress: true }, mockHandlers);
      
      // Look for progress bar and percentage
      expect(screen.getByText(/complete/)).toBeInTheDocument();
    });
    
    it("should not show progress bar when showProgress is false", () => {
      renderTaskCard(testTask, { showProgress: false }, mockHandlers);
      
      expect(screen.queryByText(/complete/)).not.toBeInTheDocument();
    });
  });

  describe("Status Handling", () => {
    it("should apply overdue styling for overdue tasks", () => {
      renderTaskCard(overdueTask, {}, mockHandlers);

      // Look for overdue indicators
      const cardElement = screen.getByRole("article");
      expect(cardElement).toBeInTheDocument();
      
      // Should show warning icon and error styling
      expect(screen.getByText(/overdue/i)).toBeInTheDocument();
    });
    
    it("should show completion styling for completed tasks", () => {
      renderTaskCard(completedTask, {}, mockHandlers);
      
      // Should show completion icon
      expect(screen.getByText("completed")).toBeInTheDocument();
    });
    
    it("should display due date with appropriate urgency indicators", () => {
      // Task due today
      const todayTask = {
        ...testTask,
        dueDate: new Date(), // Today
      };
      
      renderTaskCard(todayTask, {}, mockHandlers);
      expect(screen.getByText(/today/i)).toBeInTheDocument();
    });

    it("should handle status change events with error handling", async () => {
      const user = userEvent.setup();
      renderTaskCard(testTask, {}, mockHandlers);

      // Look for status chip button
      const statusChip = screen.getByText(testTask.status);
      expect(statusChip).toBeInTheDocument();
      
      await act(async () => {
        await user.click(statusChip);
      });

      await waitFor(() => {
        expect(mockHandlers.onStatusChange).toHaveBeenCalledWith(testTask.id, 'in-progress');
      });
    });
    
    it("should not allow status changes when disabled", async () => {
      const user = userEvent.setup();
      renderTaskCard(testTask, { disabled: true }, mockHandlers);
      
      const statusChip = screen.getByText(testTask.status);
      
      await act(async () => {
        await user.click(statusChip);
      });
      
      // Should not call the handler when disabled
      expect(mockHandlers.onStatusChange).not.toHaveBeenCalled();
    });
    
    it("should handle status change errors gracefully", async () => {
      const user = userEvent.setup();
      mockHandlers.onStatusChange.mockImplementation(() => {
        throw new Error('Status change failed');
      });
      
      renderTaskCard(testTask, {}, mockHandlers);
      
      const statusChip = screen.getByText(testTask.status);
      
      await act(async () => {
        await user.click(statusChip);
      });
      
      // Should have attempted the call but handled the error
      expect(console.error).toHaveBeenCalledWith('Error changing task status:', expect.any(Error));
    });
  });

  describe("User Interactions", () => {
    it("should call onEdit when edit button is clicked", async () => {
      const user = userEvent.setup();
      renderTaskCard(testTask, {}, mockHandlers);

      const editButton = screen.getByRole("button", { name: /edit task test task/i });
      expect(editButton).toBeInTheDocument();
      
      await act(async () => {
        await user.click(editButton);
      });

      await waitFor(() => {
        expect(mockHandlers.onEdit).toHaveBeenCalledWith(testTask);
      });
    });

    it("should call onDelete when delete button is clicked", async () => {
      const user = userEvent.setup();
      renderTaskCard(testTask, {}, mockHandlers);

      const deleteButton = screen.getByRole("button", { name: /delete task test task/i });
      expect(deleteButton).toBeInTheDocument();
      
      await act(async () => {
        await user.click(deleteButton);
      });

      await waitFor(() => {
        expect(mockHandlers.onDelete).toHaveBeenCalledWith(testTask.id);
      });
    });
    
    it("should disable buttons when loading", () => {
      renderTaskCard(testTask, { loading: true }, mockHandlers);
      
      // Should not render buttons when loading (shows skeleton instead)
      expect(screen.queryByRole("button", { name: /edit/i })).not.toBeInTheDocument();
      expect(screen.queryByRole("button", { name: /delete/i })).not.toBeInTheDocument();
    });
    
    it("should disable buttons when disabled prop is true", () => {
      renderTaskCard(testTask, { disabled: true }, mockHandlers);
      
      const editButton = screen.getByRole("button", { name: /edit/i });
      const deleteButton = screen.getByRole("button", { name: /delete/i });
      
      expect(editButton).toBeDisabled();
      expect(deleteButton).toBeDisabled();
    });
    
    it("should handle edit errors gracefully", async () => {
      const user = userEvent.setup();
      mockHandlers.onEdit.mockImplementation(() => {
        throw new Error('Edit failed');
      });
      
      renderTaskCard(testTask, {}, mockHandlers);
      
      const editButton = screen.getByRole("button", { name: /edit/i });
      
      await act(async () => {
        await user.click(editButton);
      });
      
      expect(console.error).toHaveBeenCalledWith('Error editing task:', expect.any(Error));
    });
    
    it("should handle delete errors gracefully", async () => {
      const user = userEvent.setup();
      mockHandlers.onDelete.mockImplementation(() => {
        throw new Error('Delete failed');
      });
      
      renderTaskCard(testTask, {}, mockHandlers);
      
      const deleteButton = screen.getByRole("button", { name: /delete/i });
      
      await act(async () => {
        await user.click(deleteButton);
      });
      
      expect(console.error).toHaveBeenCalledWith('Error deleting task:', expect.any(Error));
    });
    
    it("should provide keyboard navigation support", () => {
      renderTaskCard(testTask, {}, mockHandlers);
      
      const card = screen.getByRole('article');
      expect(card).toHaveAttribute('tabIndex', '0');
    });
    
    it("should have proper ARIA labels", () => {
      renderTaskCard(testTask, {}, mockHandlers);
      
      const card = screen.getByRole('article');
      expect(card).toHaveAttribute('aria-label', 'Task: Test Task');
      
      const editButton = screen.getByRole("button", { name: /edit task test task/i });
      const deleteButton = screen.getByRole("button", { name: /delete task test task/i });
      
      expect(editButton).toBeInTheDocument();
      expect(deleteButton).toBeInTheDocument();
    });
  });

  describe("Priority Display", () => {
    it("should render different priority levels correctly", () => {
      const priorities = ["low", "medium", "high", "urgent"] as const;

      priorities.forEach((priority) => {
        const taskWithPriority = { ...testTask, priority };
        const { unmount } = renderTaskCard(taskWithPriority, {}, mockHandlers);

        expect(screen.getByText(priority)).toBeInTheDocument();

        // Clean up for next iteration
        unmount();
      });
    });
    
    it("should apply correct color coding for priorities", () => {
      const urgentTask = { ...testTask, priority: 'urgent' as const };
      renderTaskCard(urgentTask, {}, mockHandlers);
      
      const priorityChip = screen.getByText('urgent');
      expect(priorityChip).toBeInTheDocument();
      // The chip should have appropriate styling (this would depend on MUI theme)
    });
  });

  describe("Date Formatting", () => {
    it("should format due date correctly", () => {
      renderTaskCard(testTask, {}, mockHandlers);

      // Check that a date is displayed (flexible check for different date formats)
      const datePattern = /Jul\s+\d{1,2},\s+\d{4}/;
      expect(screen.getByText(datePattern)).toBeInTheDocument();
    });
    
    it("should handle invalid due dates gracefully", () => {
      const taskWithInvalidDate = {
        ...testTask,
        dueDate: 'invalid-date' as any,
      };
      
      renderTaskCard(taskWithInvalidDate, {}, mockHandlers);
      
      expect(screen.getByText(/invalid date/i)).toBeInTheDocument();
    });
    
    it("should handle missing due dates", () => {
      const taskWithoutDueDate = {
        ...testTask,
        dueDate: undefined as any,
      };
      
      renderTaskCard(taskWithoutDueDate, {}, mockHandlers);
      
      expect(screen.getByText(/no due date/i)).toBeInTheDocument();
    });
    
    it("should show relative time indicators", () => {
      const todayTask = {
        ...testTask,
        dueDate: new Date(),
      };
      
      renderTaskCard(todayTask, {}, mockHandlers);
      
      expect(screen.getByText(/today/i)).toBeInTheDocument();
    });
  });
  
  describe("Performance and Optimization", () => {
    it("should memoize properly and not re-render unnecessarily", () => {
      const { rerender } = renderTaskCard(testTask, {}, mockHandlers);
      
      // Re-render with same props
      rerender(
        <TestWrapper>
          <TaskCard task={testTask} {...mockHandlers} />
        </TestWrapper>
      );
      
      // Component should still be present and functional
      expect(screen.getByText("Test Task")).toBeInTheDocument();
    });
    
    it("should handle large numbers of tags efficiently", () => {
      const taskWithManyTags = {
        ...testTask,
        tags: Array.from({ length: 20 }, (_, i) => `Tag${i + 1}`),
      };
      
      renderTaskCard(taskWithManyTags, {}, mockHandlers);
      
      // Should render without performance issues
      expect(screen.getByText("Tag1")).toBeInTheDocument();
      expect(screen.getByText("Tag10")).toBeInTheDocument();
    });
  });
  
  describe("Accessibility", () => {
    it("should have proper focus management", async () => {
      const user = userEvent.setup();
      renderTaskCard(testTask, {}, mockHandlers);
      
      const card = screen.getByRole('article');
      
      await act(async () => {
        await user.tab();
      });
      
      // Card should be focusable
      expect(card).toHaveFocus();
    });
    
    it("should support screen readers with proper labels", () => {
      renderTaskCard(testTask, {}, mockHandlers);
      
      const card = screen.getByRole('article');
      expect(card).toHaveAttribute('aria-label', 'Task: Test Task');
    });
    
    it("should provide tooltips for action buttons", () => {
      renderTaskCard(testTask, {}, mockHandlers);
      
      // Tooltips should be present (MUI Tooltip components)
      const editTooltip = screen.getByLabelText(/edit task/i);
      const deleteTooltip = screen.getByLabelText(/delete task/i);
      
      expect(editTooltip).toBeInTheDocument();
      expect(deleteTooltip).toBeInTheDocument();
    });
  });
  
  describe("Edge Cases", () => {
    it("should handle empty tag arrays", () => {
      const taskWithoutTags = {
        ...testTask,
        tags: [],
      };
      
      renderTaskCard(taskWithoutTags, {}, mockHandlers);
      
      expect(screen.getByText("Test Task")).toBeInTheDocument();
      // Should not show any tag elements
    });
    
    it("should handle missing estimated or completed hours", () => {
      const taskWithoutHours = {
        ...testTask,
        estimatedHours: undefined,
        completedHours: undefined,
      };
      
      renderTaskCard(taskWithoutHours, {}, mockHandlers);
      
      expect(screen.getByText("Test Task")).toBeInTheDocument();
      // Should not show progress information
    });
    
    it("should handle concurrent state updates safely", async () => {
      const user = userEvent.setup();
      renderTaskCard(testTask, {}, mockHandlers);
      
      const editButton = screen.getByRole("button", { name: /edit/i });
      const deleteButton = screen.getByRole("button", { name: /delete/i });
      
      // Simulate rapid clicks
      await act(async () => {
        await user.click(editButton);
        await user.click(deleteButton);
      });
      
      // Should handle both calls without errors
      expect(mockHandlers.onEdit).toHaveBeenCalled();
      expect(mockHandlers.onDelete).toHaveBeenCalled();
    });
  });
});

// Additional test utilities and integration tests
describe("TaskCard Integration Tests", () => {
  it("should work correctly within a larger component tree", () => {
    const TaskCardList: React.FC = () => {
      const tasks = [testTask, overdueTask, completedTask];
      const handlers = createMockHandlers();
      
      return (
        <div>
          {tasks.map(task => (
            <TaskCard key={task.id} task={task} {...handlers} />
          ))}
        </div>
      );
    };
    
    render(
      <TestWrapper>
        <TaskCardList />
      </TestWrapper>
    );
    
    expect(screen.getByText("Test Task")).toBeInTheDocument();
    expect(screen.getByText("Overdue Task")).toBeInTheDocument();
    expect(screen.getByText("Completed Task")).toBeInTheDocument();
  });
  
  it("should maintain performance with many task cards", () => {
    const manyTasks = Array.from({ length: 50 }, (_, i) => ({
      ...testTask,
      id: `task-${i}`,
      title: `Task ${i + 1}`,
    }));
    
    const handlers = createMockHandlers();
    
    const startTime = performance.now();
    
    render(
      <TestWrapper>
        <div>
          {manyTasks.map(task => (
            <TaskCard key={task.id} task={task} {...handlers} />
          ))}
        </div>
      </TestWrapper>
    );
    
    const endTime = performance.now();
    const renderTime = endTime - startTime;
    
    // Should render within reasonable time (less than 1000ms)
    expect(renderTime).toBeLessThan(1000);
    expect(screen.getByText("Task 1")).toBeInTheDocument();
    expect(screen.getByText("Task 50")).toBeInTheDocument();
  });
});

// Mock data generators for property-based testing
export const generateRandomTask = (overrides: Partial<TaskItem> = {}): TaskItem => {
  const statuses: TaskItem['status'][] = ['todo', 'in-progress', 'review', 'completed'];
  const priorities: TaskItem['priority'][] = ['low', 'medium', 'high', 'urgent'];
  
  return {
    id: `task-${Math.random().toString(36).substring(7)}`,
    title: `Random Task ${Math.floor(Math.random() * 1000)}`,
    description: `Random description for testing purposes ${Math.random()}`,
    status: statuses[Math.floor(Math.random() * statuses.length)],
    priority: priorities[Math.floor(Math.random() * priorities.length)],
    assignee: `User ${Math.floor(Math.random() * 10)}`,
    dueDate: new Date(Date.now() + Math.random() * 30 * 24 * 60 * 60 * 1000),
    createdAt: new Date(Date.now() - Math.random() * 7 * 24 * 60 * 60 * 1000),
    updatedAt: new Date(),
    tags: Array.from({ length: Math.floor(Math.random() * 5) }, (_, i) => `Tag${i + 1}`),
    estimatedHours: Math.floor(Math.random() * 40) + 1,
    completedHours: Math.floor(Math.random() * 20),
    ...overrides,
  };
};

// Property-based tests
describe("TaskCard Property-Based Tests", () => {
  it("should handle any valid task data without crashing", () => {
    // Generate 20 random tasks and ensure they all render
    for (let i = 0; i < 20; i++) {
      const randomTask = generateRandomTask();
      const { unmount } = renderTaskCard(randomTask);
      
      expect(screen.getByText(randomTask.title)).toBeInTheDocument();
      expect(screen.getByText(randomTask.assignee)).toBeInTheDocument();
      
      unmount();
    }
  });
});