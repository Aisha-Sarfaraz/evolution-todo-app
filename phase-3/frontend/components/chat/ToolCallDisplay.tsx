/**
 * T041: ToolCallDisplay component.
 *
 * Renders visual confirmations for tool calls (task created, completed, etc.)
 * within the chat interface.
 */
"use client";

import React from "react";

interface ToolCall {
  tool: string;
  input: Record<string, unknown>;
  output: Record<string, unknown>;
}

interface ToolCallDisplayProps {
  toolCalls: ToolCall[];
}

const TOOL_LABELS: Record<string, { label: string; icon: string }> = {
  create_task: { label: "Task Created", icon: "+" },
  mcp_create_task: { label: "Task Created", icon: "+" },
  list_tasks: { label: "Tasks Listed", icon: "≡" },
  mcp_list_tasks: { label: "Tasks Listed", icon: "≡" },
  update_task: { label: "Task Updated", icon: "↻" },
  mcp_update_task: { label: "Task Updated", icon: "↻" },
  complete_task: { label: "Task Completed", icon: "✓" },
  mcp_complete_task: { label: "Task Completed", icon: "✓" },
  delete_task: { label: "Task Deleted", icon: "✕" },
  mcp_delete_task: { label: "Task Deleted", icon: "✕" },
};

function getToolInfo(tool: string) {
  return TOOL_LABELS[tool] || { label: tool, icon: "⚡" };
}

function getDisplayTitle(toolCall: ToolCall): string {
  const input = toolCall.input;
  if (input.title && typeof input.title === "string") {
    return input.title;
  }
  if (input.task_id && typeof input.task_id === "string") {
    return `Task ${input.task_id.slice(0, 8)}...`;
  }
  return "";
}

export function ToolCallDisplay({ toolCalls }: ToolCallDisplayProps) {
  if (!toolCalls || toolCalls.length === 0) {
    return null;
  }

  return (
    <div className="space-y-2 my-2">
      {toolCalls.map((tc, idx) => {
        const info = getToolInfo(tc.tool);
        const title = getDisplayTitle(tc);

        return (
          <div
            key={idx}
            className="flex items-center gap-2 px-3 py-2 bg-gray-50 rounded-lg text-sm border border-gray-200"
          >
            <span className="text-lg">{info.icon}</span>
            <span className="font-medium">{info.label}</span>
            {title && (
              <span className="text-gray-600">— {title}</span>
            )}
          </div>
        );
      })}
    </div>
  );
}

export default ToolCallDisplay;
