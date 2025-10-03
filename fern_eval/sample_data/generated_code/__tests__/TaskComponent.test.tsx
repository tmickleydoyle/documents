import React from "react";
import { render, screen } from "@testing-library/react";
import TaskComponent from "../components/TaskComponent";

const sampleTask = {
  id: "1",
  taskTitle: "Sample Task",
  taskDescription: "This is a sample task for testing",
  currentStatus: "pending",
  taskPriority: "high",
  assignedTo: "John Doe",
  dueDateTime: "2025-07-15T00:00:00Z",
  createdDateTime: "2025-06-20T00:00:00Z",
  lastModified: "2025-06-24T00:00:00Z",
  taskTags: ["Test", "Sample"],
  estimatedTime: 5,
  actualTime: 2,
};

const mockProps = {
  onEdit: jest.fn(),
  onDelete: jest.fn(),
  onStatusUpdate: jest.fn(),
};

describe("TaskComponent", () => {
  it("should render task title", () => {
    render(<TaskComponent task={sampleTask} {...mockProps} />);
    expect(screen.getByText("Sample Task")).toBeInTheDocument();
  });

  it("should render task description", () => {
    render(<TaskComponent task={sampleTask} {...mockProps} />);
    expect(
      screen.getByText("This is a sample task for testing")
    ).toBeInTheDocument();
  });

  it("should render assignee name", () => {
    render(<TaskComponent task={sampleTask} {...mockProps} />);
    expect(screen.getByText(/John Doe/)).toBeInTheDocument();
  });

  it("should render priority badge", () => {
    render(<TaskComponent task={sampleTask} {...mockProps} />);
    expect(screen.getByText("high")).toBeInTheDocument();
  });

  it("should render tags", () => {
    render(<TaskComponent task={sampleTask} {...mockProps} />);
    expect(screen.getByText("Test")).toBeInTheDocument();
    expect(screen.getByText("Sample")).toBeInTheDocument();
  });
});
