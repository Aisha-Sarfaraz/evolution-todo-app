"use client";

import { useState, useRef, useEffect } from "react";
import { ChatKit, useChatKit } from "@openai/chatkit-react";
import { useSession } from "@/lib/auth/better-auth";

/**
 * Floating chat widget that renders the Phase 3 AI chatbot directly
 * inside the Phase 2 web app. Connects to the Phase 3 backend SSE endpoint
 * for AI-powered task management via natural language.
 *
 * All chatbot backend logic lives in Phase 3 (port 8002).
 * This component is the only Phase 2 file needed to surface the chatbot.
 */
export function FloatingChat() {
  const [isOpen, setIsOpen] = useState(false);
  const { data: session } = useSession();

  const userId = session?.user?.id;
  // Use ref to always have current userId in the fetch callback
  const userIdRef = useRef(userId);
  useEffect(() => {
    userIdRef.current = userId;
  }, [userId]);

  const backendUrl =
    process.env["NEXT_PUBLIC_CHAT_API_URL"] || "http://localhost:8002";
  const chatUrl = `${backendUrl}/api/chatkit`;

  const { control } = useChatKit({
    api: {
      url: chatUrl,
      domainKey: process.env["NEXT_PUBLIC_OPENAI_DOMAIN_KEY"] as string,
      fetch: async (input, init) => {
        // Inject user_id into the request body for the backend
        // Use ref to get current userId, not stale closure value
        const currentUserId = userIdRef.current;
        const body: BodyInit | null = init?.body ?? null;
        let modifiedBody = body;
        if (body && typeof body === "string") {
          try {
            const parsed = JSON.parse(body);
            parsed.user_id = currentUserId;
            modifiedBody = JSON.stringify(parsed);
          } catch {
            // keep original body
          }
        }

        return fetch(input, {
          ...init,
          body: modifiedBody,
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

  if (!session?.user?.id) return null;

  return (
    <>
      {/* Floating toggle button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="fixed bottom-6 right-6 z-[60] w-14 h-14 rounded-full bg-gradient-to-br from-accent-500 to-purple-600 text-white shadow-lg hover:shadow-xl hover:scale-105 transition-all duration-200 flex items-center justify-center"
        aria-label={isOpen ? "Close chat" : "Open AI assistant"}
      >
        {isOpen ? (
          <svg
            className="w-6 h-6"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            strokeWidth={2}
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M6 18L18 6M6 6l12 12"
            />
          </svg>
        ) : (
          <svg
            className="w-6 h-6"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            strokeWidth={2}
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
            />
          </svg>
        )}
      </button>

      {/* Chat panel */}
      {isOpen && (
        <div className="fixed bottom-24 right-6 z-[55] w-[400px] h-[550px] rounded-2xl shadow-2xl overflow-hidden border border-neutral-200 dark:border-neutral-700 bg-white dark:bg-neutral-900">
          <ChatKit control={control} className="h-full w-full" />
        </div>
      )}
    </>
  );
}
