/**
 * T090: NotificationBanner component.
 *
 * In-app fallback notification banner shown when push permission
 * is denied or notifications are not supported.
 */
"use client";

import React from "react";

interface NotificationBannerProps {
  show: boolean;
  onDismiss: () => void;
  message?: string;
}

export function NotificationBanner({
  show,
  onDismiss,
  message = "Enable notifications to get task reminders. Click to allow.",
}: NotificationBannerProps) {
  if (!show) return null;

  return (
    <div className="bg-yellow-50 border-b border-yellow-200 px-4 py-2 flex items-center justify-between">
      <p className="text-sm text-yellow-800">{message}</p>
      <button
        onClick={onDismiss}
        className="text-yellow-600 hover:text-yellow-800 text-sm font-medium ml-4"
        aria-label="Dismiss notification banner"
      >
        Dismiss
      </button>
    </div>
  );
}

export default NotificationBanner;
