/**
 * T040: ChatContainer component.
 *
 * Wraps OpenAI ChatKit with custom backend URL
 * and auth headers for the Phase III chat API.
 */
"use client";

import React from "react";
import { ChatKit, useChatKit } from "@openai/chatkit-react";

interface ChatContainerProps {
  userId: string;
  authToken: string;
  conversationId?: string;
  backendUrl?: string;
}

export interface ToolCallData {
  tool: string;
  input: Record<string, unknown>;
  output: Record<string, unknown>;
}

export function ChatContainer({
  userId,
  authToken,
  conversationId,
  backendUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8002/api",
}: ChatContainerProps) {
  const chatUrl = `${backendUrl}/${userId}/chat`;

  const { control } = useChatKit({
    api: {
      url: chatUrl,
      domainKey: process.env.NEXT_PUBLIC_OPENAI_DOMAIN_KEY || "dev-placeholder",
      fetch: async (input, init) => {
        const body = init?.body ? JSON.parse(init.body as string) : {};
        if (conversationId) {
          body.conversation_id = conversationId;
        }
        return fetch(input, {
          ...init,
          headers: {
            ...init?.headers,
            Authorization: `Bearer ${authToken}`,
            "Content-Type": "application/json",
          },
          body: JSON.stringify(body),
          credentials: "include",
        });
      },
    },
    startScreen: {
      greeting: "Hi! I'm your task assistant. How can I help?",
      prompts: [
        {
          label: "View Tasks",
          prompt: "Show me my pending tasks",
        },
        {
          label: "Add Task",
          prompt: "Help me add a new task",
        },
        {
          label: "Get Help",
          prompt: "What can you help me with?",
        },
      ],
    },
    composer: {
      placeholder: "Type a message to manage your tasks...",
    },
  });

  return (
    <div className="flex flex-col h-full">
      <ChatKit control={control} className="h-full w-full" />
    </div>
  );
}

export default ChatContainer;
