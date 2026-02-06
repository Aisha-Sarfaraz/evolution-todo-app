"use client";

import { useState, useRef, useEffect, Component, type ReactNode } from "react";
import { ChatKit, useChatKit } from "@openai/chatkit-react";
import { useSession } from "@/lib/auth/better-auth";

// Error boundary to prevent ChatKit crashes from unmounting the whole component
class ChatErrorBoundary extends Component<
  { children: ReactNode; onError?: (error: Error) => void },
  { hasError: boolean }
> {
  constructor(props: { children: ReactNode; onError?: (error: Error) => void }) {
    super(props);
    this.state = { hasError: false };
  }
  static getDerivedStateFromError() {
    return { hasError: true };
  }
  componentDidCatch(error: Error) {
    console.error("[ChatKit] React error boundary caught:", error);
    this.props.onError?.(error);
  }
  render() {
    if (this.state.hasError) {
      return (
        <div className="flex items-center justify-center h-full p-4 text-center text-sm text-neutral-500">
          <div>
            <p>Chat encountered an error.</p>
            <button
              onClick={() => this.setState({ hasError: false })}
              className="mt-2 px-3 py-1 text-xs bg-purple-600 text-white rounded hover:bg-purple-700"
            >
              Retry
            </button>
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}

export function FloatingChat() {
  const [isOpen, setIsOpen] = useState(false);
  const { data: session } = useSession();

  const userId = session?.user?.id;
  const userIdRef = useRef(userId);
  // Track if we ever had a valid session (prevents unmount on brief refresh)
  const hadSessionRef = useRef(false);

  useEffect(() => {
    userIdRef.current = userId;
    if (userId) hadSessionRef.current = true;
  }, [userId]);

  const chatUrl = "/api/chat";

  const { control } = useChatKit({
    api: {
      url: chatUrl,
      domainKey: process.env["NEXT_PUBLIC_OPENAI_DOMAIN_KEY"] as string,
      fetch: async (input, init) => {
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
    onReady: () => {
      console.log("[ChatKit] Widget ready");
    },
    onError: (event: { error: Error }) => {
      console.error("[ChatKit] Error:", event.error);
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

  // Don't render until we've had a session at least once
  // Use hadSessionRef to prevent unmounting during brief session refreshes
  if (!userId && !hadSessionRef.current) return null;

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
          <ChatErrorBoundary>
            <ChatKit control={control} className="h-full w-full" />
          </ChatErrorBoundary>
        </div>
      )}
    </>
  );
}
