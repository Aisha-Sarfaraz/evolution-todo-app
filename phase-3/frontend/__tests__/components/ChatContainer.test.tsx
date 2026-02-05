/**
 * T028: Frontend unit test for ChatContainer component.
 */
import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import React from "react";

// Mock the ChatKit components
vi.mock("@openai/chatkit-react", () => ({
  ChatProvider: ({ children }: { children: React.ReactNode }) => (
    <div data-testid="chat-provider">{children}</div>
  ),
  ChatMessages: () => <div data-testid="chat-messages" />,
  ChatInput: () => <div data-testid="chat-input" />,
}));

describe("ChatContainer", () => {
  it("renders chat provider wrapper", async () => {
    const { ChatContainer } = await import(
      "@/components/chat/ChatContainer"
    );
    render(<ChatContainer userId="test-user" authToken="fake-token" />);

    expect(screen.getByTestId("chat-provider")).toBeInTheDocument();
  });

  it("renders chat messages area", async () => {
    const { ChatContainer } = await import(
      "@/components/chat/ChatContainer"
    );
    render(<ChatContainer userId="test-user" authToken="fake-token" />);

    expect(screen.getByTestId("chat-messages")).toBeInTheDocument();
  });

  it("renders chat input area", async () => {
    const { ChatContainer } = await import(
      "@/components/chat/ChatContainer"
    );
    render(<ChatContainer userId="test-user" authToken="fake-token" />);

    expect(screen.getByTestId("chat-input")).toBeInTheDocument();
  });

  it("passes backendUrl to ChatProvider", async () => {
    const { ChatContainer } = await import(
      "@/components/chat/ChatContainer"
    );
    const { container } = render(
      <ChatContainer
        userId="test-user"
        authToken="fake-token"
        backendUrl="http://localhost:8002/api"
      />
    );

    expect(container).toBeTruthy();
  });
});
