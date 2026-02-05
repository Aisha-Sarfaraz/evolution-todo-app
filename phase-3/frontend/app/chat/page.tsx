/**
 * T042/T057/T058: Main chat page with conversation switching and lazy loading.
 *
 * The primary interface for Phase III — users interact with the AI
 * task assistant through this chat page. Includes conversation sidebar
 * for switching between conversations and lazy loading older messages.
 */
"use client";

import React, { useCallback, useEffect, useState } from "react";
import { ChatContainer } from "@/components/chat/ChatContainer";
import { ConversationList } from "@/components/chat/ConversationList";
import { NotificationBanner } from "@/components/chat/NotificationBanner";
import { apiClient, type Conversation } from "@/lib/api";
import { subscribeToPush } from "@/lib/push";

export default function ChatPage() {
  const [authToken, setAuthToken] = useState<string | null>(null);
  const [userId, setUserId] = useState<string | null>(null);
  const [conversationId, setConversationId] = useState<string | undefined>();
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [showNotifBanner, setShowNotifBanner] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadAuth() {
      try {
        const res = await fetch(
          `${process.env.NEXT_PUBLIC_AUTH_URL || ""}/api/auth/get-session`,
          { credentials: "include" }
        );
        if (res.ok) {
          const data = await res.json();
          if (data?.session?.token) {
            setAuthToken(data.session.token);
            setUserId(data.user?.id || data.session?.userId);
            apiClient.setAuthToken(data.session.token);
          }
        }
      } catch (err) {
        console.error("Failed to load auth session:", err);
      } finally {
        setLoading(false);
      }
    }
    loadAuth();
  }, []);

  const loadConversations = useCallback(async () => {
    if (!userId) return;
    try {
      const result = await apiClient.getConversations(userId);
      setConversations(result.conversations);
    } catch (err) {
      console.error("Failed to load conversations:", err);
    }
  }, [userId]);

  useEffect(() => {
    if (userId && authToken) {
      loadConversations();

      // T091: Prompt for push notification permission on first visit
      if ("Notification" in window && Notification.permission === "default") {
        subscribeToPush(userId, authToken).then((success) => {
          if (!success) {
            setShowNotifBanner(true);
          }
        });
      } else if (
        "Notification" in window &&
        Notification.permission === "denied"
      ) {
        setShowNotifBanner(true);
      }
    }
  }, [userId, authToken, loadConversations]);

  const handleSelectConversation = useCallback((id: string) => {
    setConversationId(id);
  }, []);

  const handleNewChat = useCallback(() => {
    setConversationId(undefined);
    // Refresh conversation list after a delay
    setTimeout(loadConversations, 1000);
  }, [loadConversations]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <p className="text-gray-500">Loading...</p>
      </div>
    );
  }

  if (!authToken || !userId) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <h2 className="text-xl font-semibold mb-2">Sign in required</h2>
          <p className="text-gray-500">
            Please sign in to use the chat assistant.
          </p>
          <a
            href={`${process.env.NEXT_PUBLIC_AUTH_URL || ""}/auth/login`}
            className="mt-4 inline-block px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Sign In
          </a>
        </div>
      </div>
    );
  }

  return (
    <div className="h-screen flex">
      {/* Sidebar */}
      {sidebarOpen && (
        <div className="w-72 flex-shrink-0">
          <ConversationList
            conversations={conversations}
            activeId={conversationId}
            onSelect={handleSelectConversation}
            onNewChat={handleNewChat}
          />
        </div>
      )}

      {/* Main chat area */}
      <div className="flex-1 flex flex-col">
        {showNotifBanner && (
          <NotificationBanner
            show={showNotifBanner}
            onDismiss={() => setShowNotifBanner(false)}
          />
        )}
        <header className="border-b px-4 py-3 flex items-center justify-between bg-white">
          <div className="flex items-center gap-3">
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="text-gray-500 hover:text-gray-700"
              aria-label="Toggle sidebar"
            >
              ☰
            </button>
            <h1 className="text-lg font-semibold">Todo Assistant</h1>
          </div>
        </header>
        <main className="flex-1 overflow-hidden">
          <ChatContainer
            userId={userId}
            authToken={authToken}
            conversationId={conversationId}
          />
        </main>
      </div>
    </div>
  );
}
