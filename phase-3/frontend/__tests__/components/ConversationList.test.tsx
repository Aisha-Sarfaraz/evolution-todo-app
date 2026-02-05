/**
 * T050: Frontend unit test for ConversationList component.
 */
import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import React from "react";

describe("ConversationList", () => {
  const mockConversations = [
    {
      id: "conv-1",
      title: "Task planning",
      last_message_preview: "Show my tasks",
      updated_at: "2026-01-31T12:00:00Z",
    },
    {
      id: "conv-2",
      title: "Grocery list",
      last_message_preview: "Add milk to my list",
      updated_at: "2026-01-30T08:00:00Z",
    },
  ];

  it("renders conversation list", async () => {
    const { ConversationList } = await import(
      "@/components/chat/ConversationList"
    );
    render(
      <ConversationList
        conversations={mockConversations}
        onSelect={vi.fn()}
        onNewChat={vi.fn()}
      />
    );

    expect(screen.getByText("Task planning")).toBeInTheDocument();
    expect(screen.getByText("Grocery list")).toBeInTheDocument();
  });

  it("calls onSelect when conversation clicked", async () => {
    const { ConversationList } = await import(
      "@/components/chat/ConversationList"
    );
    const onSelect = vi.fn();
    render(
      <ConversationList
        conversations={mockConversations}
        onSelect={onSelect}
        onNewChat={vi.fn()}
      />
    );

    fireEvent.click(screen.getByText("Task planning"));
    expect(onSelect).toHaveBeenCalledWith("conv-1");
  });

  it("renders new chat button", async () => {
    const { ConversationList } = await import(
      "@/components/chat/ConversationList"
    );
    render(
      <ConversationList
        conversations={mockConversations}
        onSelect={vi.fn()}
        onNewChat={vi.fn()}
      />
    );

    expect(screen.getByText(/new chat/i)).toBeInTheDocument();
  });

  it("calls onNewChat when new chat button clicked", async () => {
    const { ConversationList } = await import(
      "@/components/chat/ConversationList"
    );
    const onNewChat = vi.fn();
    render(
      <ConversationList
        conversations={mockConversations}
        onSelect={vi.fn()}
        onNewChat={onNewChat}
      />
    );

    fireEvent.click(screen.getByText(/new chat/i));
    expect(onNewChat).toHaveBeenCalled();
  });

  it("shows last message preview", async () => {
    const { ConversationList } = await import(
      "@/components/chat/ConversationList"
    );
    render(
      <ConversationList
        conversations={mockConversations}
        onSelect={vi.fn()}
        onNewChat={vi.fn()}
      />
    );

    expect(screen.getByText("Show my tasks")).toBeInTheDocument();
  });
});
