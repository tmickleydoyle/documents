import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import "@testing-library/jest-dom";
import TaskCard from "../components/TaskCard";
import { Task } from "../types";

const mockTask: Task = {
  id: "1",
  title: "Test Task",
  description: "This is a test task description",
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

describe("TaskCard Component", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it("renders task information correctly", () => {
    render(<TaskCard task={mockTask} {...mockHandlers} />);

    expect(screen.getByText("Test Task")).toBeInTheDocument();
    expect(
      screen.getByText("This is a test task description")
    ).toBeInTheDocument();
    expect(screen.getByText("John Doe")).toBeInTheDocument();
    expect(screen.getByText("high")).toBeInTheDocument();
  });

  it("displays tags correctly", () => {
    render(<TaskCard task={mockTask} {...mockHandlers} />);

    expect(screen.getByText("Testing")).toBeInTheDocument();
    expect(screen.getByText("Frontend")).toBeInTheDocument();
  });

  it("shows overdue styling for overdue tasks", () => {
    const overdueTask = {
      ...mockTask,
      dueDate: new Date("2025-06-01"), // Past date
      status: "todo" as const,
    };

    render(<TaskCard task={overdueTask} {...mockHandlers} />);

    // Check if the card has overdue styling (red border)
    const card =
      screen.getByRole("article", { hidden: true }) ||
      screen.getByTestId("task-card") ||
      document.querySelector('[class*="MuiCard"]');

    expect(card).toHaveStyle({ borderColor: "error.main" });
  });

  it("calls onEdit when edit button is clicked", async () => {
    render(<TaskCard task={mockTask} {...mockHandlers} />);

    const editButton =
      screen.getByLabelText("Edit Task") ||
      screen.getByRole("button", { name: /edit/i });

    fireEvent.click(editButton);

    await waitFor(() => {
      expect(mockHandlers.onEdit).toHaveBeenCalledWith(mockTask);
    });
  });

  it("calls onDelete when delete button is clicked", async () => {
    render(<TaskCard task={mockTask} {...mockHandlers} />);

    const deleteButton =
      screen.getByLabelText("Delete Task") ||
      screen.getByRole("button", { name: /delete/i });

    fireEvent.click(deleteButton);

    await waitFor(() => {
      expect(mockHandlers.onDelete).toHaveBeenCalledWith(mockTask.id);
    });
  });

  it("cycles through statuses when status chip is clicked", async () => {
    render(<TaskCard task={mockTask} {...mockHandlers} />);

    const statusChip = screen.getByText("todo");

    fireEvent.click(statusChip);

    await waitFor(() => {
      expect(mockHandlers.onStatusChange).toHaveBeenCalledWith(
        mockTask.id,
        "in-progress"
      );
    });
  });

  it("displays estimated and completed hours when available", () => {
    render(<TaskCard task={mockTask} {...mockHandlers} />);

    expect(screen.getByText(/Est: 8h/)).toBeInTheDocument();
    expect(screen.getByText(/Completed: 3h/)).toBeInTheDocument();
  });
});
