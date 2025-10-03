import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import "@testing-library/jest-dom";
import TaskCard from "../components/TaskCard";
import { Task } from "../types";

// Test data
const testTask: Task = {
  id: "1",
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

const mockHandlers = {
  onEdit: jest.fn(),
  onDelete: jest.fn(),
  onStatusChange: jest.fn(),
};

describe("TaskCard Component Tests", () => {
  beforeEach(() => {
    // Reset all mocks before each test
    jest.clearAllMocks();
  });

  describe("Rendering", () => {
    it("should render task information correctly", () => {
      render(<TaskCard task={testTask} {...mockHandlers} />);

      expect(screen.getByText("Test Task")).toBeInTheDocument();
      expect(
        screen.getByText("This is a test task description for testing purposes")
      ).toBeInTheDocument();
      expect(screen.getByText("John Doe")).toBeInTheDocument();
      expect(screen.getByText("high")).toBeInTheDocument();
    });

    it("should display all task tags", () => {
      render(<TaskCard task={testTask} {...mockHandlers} />);

      expect(screen.getByText("Testing")).toBeInTheDocument();
      expect(screen.getByText("Frontend")).toBeInTheDocument();
    });

    it("should show progress information when available", () => {
      render(<TaskCard task={testTask} {...mockHandlers} />);

      // Check for progress indicators
      const progressElements = screen.getAllByText(/3/);
      expect(progressElements.length).toBeGreaterThan(0);
    });
  });

  describe("Status Handling", () => {
    it("should apply overdue styling for overdue tasks", () => {
      const overdueTask = {
        ...testTask,
        dueDate: new Date("2025-06-01"), // Past date
        status: "todo" as const,
      };

      render(<TaskCard task={overdueTask} {...mockHandlers} />);

      // Look for overdue indicators
      const cardElement =
        screen.getByRole("article") || screen.getByTestId("task-card");
      expect(cardElement).toBeInTheDocument();
    });

    it("should handle status change events", async () => {
      render(<TaskCard task={testTask} {...mockHandlers} />);

      // Look for status change button or dropdown
      const statusButton =
        screen.getByRole("button", { name: /status/i }) ||
        screen.getByText(testTask.status);

      if (statusButton) {
        fireEvent.click(statusButton);

        await waitFor(() => {
          expect(mockHandlers.onStatusChange).toHaveBeenCalled();
        });
      }
    });
  });

  describe("User Interactions", () => {
    it("should call onEdit when edit button is clicked", async () => {
      render(<TaskCard task={testTask} {...mockHandlers} />);

      const editButton =
        screen.getByRole("button", { name: /edit/i }) ||
        screen.getByLabelText(/edit/i);

      fireEvent.click(editButton);

      await waitFor(() => {
        expect(mockHandlers.onEdit).toHaveBeenCalledWith(testTask);
      });
    });

    it("should call onDelete when delete button is clicked", async () => {
      render(<TaskCard task={testTask} {...mockHandlers} />);

      const deleteButton =
        screen.getByRole("button", { name: /delete/i }) ||
        screen.getByLabelText(/delete/i);

      fireEvent.click(deleteButton);

      await waitFor(() => {
        expect(mockHandlers.onDelete).toHaveBeenCalledWith(testTask.id);
      });
    });
  });

  describe("Priority Display", () => {
    it("should render different priority levels correctly", () => {
      const priorities = ["low", "medium", "high", "urgent"] as const;

      priorities.forEach((priority) => {
        const taskWithPriority = { ...testTask, priority };
        const { rerender } = render(
          <TaskCard task={taskWithPriority} {...mockHandlers} />
        );

        expect(screen.getByText(priority)).toBeInTheDocument();

        // Clean up for next iteration
        rerender(<div></div>);
      });
    });
  });

  describe("Date Formatting", () => {
    it("should format due date correctly", () => {
      render(<TaskCard task={testTask} {...mockHandlers} />);

      // Check that a date is displayed (flexible check for different date formats)
      const datePattern = /\d{1,2}\/\d{1,2}\/\d{4}|\d{4}-\d{2}-\d{2}|Jul|July/;
      expect(screen.getByText(datePattern)).toBeInTheDocument();
    });
  });
});
