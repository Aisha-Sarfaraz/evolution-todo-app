/**
 * T055: ConversationList sidebar component.
 *
 * Displays conversation list with last message preview,
 * timestamp, and new chat button.
 */
"use client";

import React from "react";
import { formatDistanceToNow } from "date-fns";

interface Conversation {
  id: string;
  title: string | null;
  last_message_preview: string | null;
  updated_at: string;
}

interface ConversationListProps {
  conversations: Conversation[];
  activeId?: string;
  onSelect: (conversationId: string) => void;
  onNewChat: () => void;
}

export function ConversationList({
  conversations,
  activeId,
  onSelect,
  onNewChat,
}: ConversationListProps) {
  return (
    <div className="flex flex-col h-full bg-gray-50 border-r">
      <div className="p-3 border-b">
        <button
          onClick={onNewChat}
          className="w-full px-3 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm font-medium"
        >
          + New Chat
        </button>
      </div>
      <div className="flex-1 overflow-y-auto">
        {conversations.length === 0 && (
          <p className="text-center text-gray-400 text-sm mt-8">
            No conversations yet
          </p>
        )}
        {conversations.map((conv) => (
          <button
            key={conv.id}
            onClick={() => onSelect(conv.id)}
            className={`w-full text-left px-3 py-3 border-b hover:bg-gray-100 transition-colors ${
              activeId === conv.id ? "bg-blue-50 border-l-2 border-l-blue-600" : ""
            }`}
          >
            <div className="font-medium text-sm truncate">
              {conv.title || "New conversation"}
            </div>
            {conv.last_message_preview && (
              <div className="text-xs text-gray-500 truncate mt-0.5">
                {conv.last_message_preview}
              </div>
            )}
            <div className="text-xs text-gray-400 mt-1">
              {formatDistanceToNow(new Date(conv.updated_at), {
                addSuffix: true,
              })}
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}

export default ConversationList;
