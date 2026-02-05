/**
 * Embeddable chat page — designed to be loaded inside an iframe
 * from the Phase 2 frontend. Reads userId from URL search params.
 * No sidebar, no header — just the chat widget.
 */
"use client";

import React, { useEffect, useState, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import { ChatKit, useChatKit } from "@openai/chatkit-react";

function EmbedChatInner() {
  const searchParams = useSearchParams();
  const userId = searchParams.get("userId");
  const [ready, setReady] = useState(false);

  const backendUrl =
    process.env.NEXT_PUBLIC_API_URL || "http://localhost:8002/api";
  const chatUrl = userId
    ? `${backendUrl}/${userId}/chat`
    : `${backendUrl}/anonymous/chat`;

  const { control } = useChatKit({
    api: {
      url: chatUrl,
      domainKey:
        process.env.NEXT_PUBLIC_OPENAI_DOMAIN_KEY || "dev-placeholder",
      fetch: async (input, init) => {
        return fetch(input, {
          ...init,
          headers: {
            ...init?.headers,
            "Content-Type": "application/json",
          },
          credentials: "include",
        });
      },
    },
    theme: {
      colorScheme: "light",
      color: {
        accent: {
          primary: "#7c3aed",
          level: 2,
        },
      },
    },
    startScreen: {
      greeting:
        "Hi! I'm your Flowspace AI assistant. Ask me to manage your tasks!",
      prompts: [
        {
          label: "Show my tasks",
          prompt: "Show me all my pending tasks",
        },
        {
          label: "Add a task",
          prompt: "Help me add a new task",
        },
        {
          label: "What can you do?",
          prompt: "What can you help me with?",
        },
      ],
    },
    composer: {
      placeholder: "Ask me to manage your tasks...",
    },
    header: {
      title: {
        text: "Flowspace AI",
      },
    },
  });

  useEffect(() => {
    setReady(true);
  }, []);

  if (!ready) {
    return (
      <div className="flex items-center justify-center h-screen bg-white">
        <p className="text-gray-400 text-sm">Loading chat...</p>
      </div>
    );
  }

  if (!userId) {
    return (
      <div className="flex items-center justify-center h-screen bg-white">
        <p className="text-gray-500 text-sm">
          Missing userId parameter
        </p>
      </div>
    );
  }

  return (
    <div className="h-screen w-screen overflow-hidden bg-white">
      <ChatKit control={control} className="h-full w-full" />
    </div>
  );
}

export default function EmbedChatPage() {
  return (
    <Suspense
      fallback={
        <div className="flex items-center justify-center h-screen bg-white">
          <p className="text-gray-400 text-sm">Loading...</p>
        </div>
      }
    >
      <EmbedChatInner />
    </Suspense>
  );
}
