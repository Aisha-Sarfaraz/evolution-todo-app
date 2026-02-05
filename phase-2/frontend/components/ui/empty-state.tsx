"use client";

import { type ReactNode } from "react";
import { clsx } from "clsx";
import { Button } from "./button";

export interface EmptyStateProps {
  icon?: ReactNode;
  title: string;
  description?: string;
  action?: {
    label: string;
    onClick: () => void;
    variant?: "primary" | "secondary" | "outline";
  } | undefined;
  className?: string;
}

// Default empty state icons
const defaultIcons = {
  tasks: (
    <svg
      className="w-16 h-16"
      fill="none"
      viewBox="0 0 24 24"
      stroke="currentColor"
      strokeWidth={1}
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4"
      />
    </svg>
  ),
  search: (
    <svg
      className="w-16 h-16"
      fill="none"
      viewBox="0 0 24 24"
      stroke="currentColor"
      strokeWidth={1}
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
      />
    </svg>
  ),
  error: (
    <svg
      className="w-16 h-16"
      fill="none"
      viewBox="0 0 24 24"
      stroke="currentColor"
      strokeWidth={1}
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
      />
    </svg>
  ),
  categories: (
    <svg
      className="w-16 h-16"
      fill="none"
      viewBox="0 0 24 24"
      stroke="currentColor"
      strokeWidth={1}
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z"
      />
    </svg>
  ),
  tags: (
    <svg
      className="w-16 h-16"
      fill="none"
      viewBox="0 0 24 24"
      stroke="currentColor"
      strokeWidth={1}
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M7 20l4-16m2 16l4-16M6 9h14M4 15h14"
      />
    </svg>
  ),
};

export function EmptyState({
  icon,
  title,
  description,
  action,
  className,
}: EmptyStateProps) {
  return (
    <div
      className={clsx(
        "flex flex-col items-center justify-center py-16 px-4 text-center",
        className
      )}
    >
      {icon && (
        <div className="mb-6 text-neutral-300 dark:text-neutral-600">{icon}</div>
      )}
      <h3 className="text-h4 font-display text-neutral-900 dark:text-neutral-100 mb-2">
        {title}
      </h3>
      {description && (
        <p className="text-body-sm text-neutral-500 dark:text-neutral-400 max-w-sm mb-6">
          {description}
        </p>
      )}
      {action && (
        <Button variant={action.variant || "primary"} onClick={action.onClick}>
          {action.label}
        </Button>
      )}
    </div>
  );
}

// Pre-configured empty states
export function EmptyTasksState({
  onCreateTask,
}: {
  onCreateTask?: (() => void) | undefined;
}) {
  return (
    <EmptyState
      icon={defaultIcons.tasks}
      title="No tasks yet"
      description="Create your first task to get started with organizing your work."
      action={
        onCreateTask
          ? {
              label: "Create your first task",
              onClick: onCreateTask,
            }
          : undefined
      }
    />
  );
}

export function EmptySearchState({
  searchTerm,
  onClearSearch,
}: {
  searchTerm?: string | undefined;
  onClearSearch?: (() => void) | undefined;
}) {
  return (
    <EmptyState
      icon={defaultIcons.search}
      title="No results found"
      description={
        searchTerm
          ? `No tasks found matching "${searchTerm}". Try different keywords or clear filters.`
          : "No tasks match your current filters. Try adjusting your search criteria."
      }
      action={
        onClearSearch
          ? {
              label: "Clear filters",
              onClick: onClearSearch,
              variant: "outline",
            }
          : undefined
      }
    />
  );
}

export function ErrorState({
  title = "Something went wrong",
  description = "We encountered an error while loading. Please try again.",
  onRetry,
}: {
  title?: string | undefined;
  description?: string | undefined;
  onRetry?: (() => void) | undefined;
}) {
  return (
    <EmptyState
      icon={defaultIcons.error}
      title={title}
      description={description}
      action={
        onRetry
          ? {
              label: "Try again",
              onClick: onRetry,
              variant: "outline",
            }
          : undefined
      }
    />
  );
}
