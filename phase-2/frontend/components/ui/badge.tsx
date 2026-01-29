"use client";

import { type ReactNode } from "react";
import { clsx } from "clsx";

export interface BadgeProps {
  children: ReactNode;
  variant?:
    | "default"
    | "priority-low"
    | "priority-medium"
    | "priority-high"
    | "priority-urgent"
    | "category"
    | "tag"
    | "status-pending"
    | "status-complete"
    | "success"
    | "warning"
    | "error";
  size?: "sm" | "md";
  icon?: ReactNode;
  removable?: boolean;
  onRemove?: () => void;
  className?: string;
}

const variantStyles = {
  default:
    "bg-neutral-100 text-neutral-600 dark:bg-neutral-800 dark:text-neutral-400",
  "priority-low":
    "bg-neutral-100 text-neutral-500 dark:bg-neutral-800 dark:text-neutral-400",
  "priority-medium":
    "bg-blue-50 text-blue-600 dark:bg-blue-900/30 dark:text-blue-400",
  "priority-high":
    "bg-orange-50 text-orange-600 dark:bg-orange-900/30 dark:text-orange-400",
  "priority-urgent":
    "bg-red-50 text-red-600 dark:bg-red-900/30 dark:text-red-400",
  category:
    "bg-accent-50 text-accent-700 dark:bg-accent-900/30 dark:text-accent-400",
  tag: "bg-neutral-100 text-neutral-600 dark:bg-neutral-800 dark:text-neutral-400 border border-neutral-200 dark:border-neutral-700",
  "status-pending":
    "bg-amber-50 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400",
  "status-complete":
    "bg-green-50 text-green-700 dark:bg-green-900/30 dark:text-green-400",
  success:
    "bg-green-50 text-green-700 dark:bg-green-900/30 dark:text-green-400",
  warning:
    "bg-amber-50 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400",
  error: "bg-red-50 text-red-700 dark:bg-red-900/30 dark:text-red-400",
};

const sizeStyles = {
  sm: "px-2 py-0.5 text-[11px]",
  md: "px-2.5 py-1 text-caption",
};

export function Badge({
  children,
  variant = "default",
  size = "md",
  icon,
  removable = false,
  onRemove,
  className,
}: BadgeProps) {
  return (
    <span
      className={clsx(
        "inline-flex items-center gap-1 rounded-full font-medium",
        variantStyles[variant],
        sizeStyles[size],
        className
      )}
    >
      {icon && <span className="flex-shrink-0">{icon}</span>}
      {children}
      {removable && onRemove && (
        <button
          type="button"
          onClick={(e) => {
            e.stopPropagation();
            onRemove();
          }}
          className="ml-0.5 -mr-1 p-0.5 rounded-full hover:bg-black/10 dark:hover:bg-white/10 transition-colors"
          aria-label="Remove"
        >
          <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M6 18L18 6M6 6l12 12"
            />
          </svg>
        </button>
      )}
    </span>
  );
}

// Convenience components for priority badges
export function PriorityBadge({
  priority,
  size = "md",
}: {
  priority: "Low" | "Medium" | "High" | "Urgent";
  size?: "sm" | "md";
}) {
  const priorityMap = {
    Low: "priority-low",
    Medium: "priority-medium",
    High: "priority-high",
    Urgent: "priority-urgent",
  } as const;

  const icons = {
    Low: null,
    Medium: (
      <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
        <path
          fillRule="evenodd"
          d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z"
          clipRule="evenodd"
        />
      </svg>
    ),
    High: (
      <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
        <path
          fillRule="evenodd"
          d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"
          clipRule="evenodd"
        />
      </svg>
    ),
    Urgent: (
      <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
        <path
          fillRule="evenodd"
          d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z"
          clipRule="evenodd"
        />
      </svg>
    ),
  };

  return (
    <Badge variant={priorityMap[priority]} size={size} icon={icons[priority]}>
      {priority}
    </Badge>
  );
}

// Status badge
export function StatusBadge({
  status,
  size = "md",
}: {
  status: "pending" | "complete";
  size?: "sm" | "md";
}) {
  const statusMap = {
    pending: "status-pending",
    complete: "status-complete",
  } as const;

  const labels = {
    pending: "Pending",
    complete: "Complete",
  };

  return (
    <Badge variant={statusMap[status]} size={size}>
      {labels[status]}
    </Badge>
  );
}
