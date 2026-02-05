/**
 * T029: Frontend unit test for ToolCallDisplay component.
 */
import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import React from "react";

describe("ToolCallDisplay", () => {
  it("renders tool call with task created action", async () => {
    const { ToolCallDisplay } = await import(
      "@/components/chat/ToolCallDisplay"
    );
    render(
      <ToolCallDisplay
        toolCalls={[
          {
            tool: "create_task",
            input: { title: "Buy groceries" },
            output: { id: "abc-123" },
          },
        ]}
      />
    );

    expect(screen.getByText(/created/i)).toBeInTheDocument();
    expect(screen.getByText(/Buy groceries/i)).toBeInTheDocument();
  });

  it("renders tool call with task completed action", async () => {
    const { ToolCallDisplay } = await import(
      "@/components/chat/ToolCallDisplay"
    );
    render(
      <ToolCallDisplay
        toolCalls={[
          {
            tool: "complete_task",
            input: { task_id: "abc-123" },
            output: { status: "complete" },
          },
        ]}
      />
    );

    expect(screen.getByText(/complete/i)).toBeInTheDocument();
  });

  it("renders nothing when tool_calls is empty", async () => {
    const { ToolCallDisplay } = await import(
      "@/components/chat/ToolCallDisplay"
    );
    const { container } = render(<ToolCallDisplay toolCalls={[]} />);

    expect(container.children.length).toBeLessThanOrEqual(1);
  });

  it("renders multiple tool calls", async () => {
    const { ToolCallDisplay } = await import(
      "@/components/chat/ToolCallDisplay"
    );
    render(
      <ToolCallDisplay
        toolCalls={[
          {
            tool: "create_task",
            input: { title: "Task 1" },
            output: { id: "1" },
          },
          {
            tool: "create_task",
            input: { title: "Task 2" },
            output: { id: "2" },
          },
        ]}
      />
    );

    expect(screen.getByText(/Task 1/i)).toBeInTheDocument();
    expect(screen.getByText(/Task 2/i)).toBeInTheDocument();
  });
});
