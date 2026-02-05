/**
 * T056: Chat layout with sidebar and main chat area.
 */
import React from "react";

export default function ChatLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="flex h-screen bg-white">
      {children}
    </div>
  );
}
