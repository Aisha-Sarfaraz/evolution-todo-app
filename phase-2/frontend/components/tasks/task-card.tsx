"use client";

import { useState } from "react";
import type { Task, TaskWithRelations } from "@/lib/types/task";
import { TaskActions } from "./task-actions";
import { TaskDetailModal } from "./task-detail-modal";
import { PriorityBadge, Badge } from "@/components/ui/badge";
import { clsx } from "clsx";
import { formatDistanceToNow } from "date-fns";

interface TaskCardProps {
  task: Task | TaskWithRelations;
}

export function TaskCard({ task }: TaskCardProps) {
  const [showDetail, setShowDetail] = useState(false);
  const isCompleted = task.status === "complete";

  const hasRelations = (t: Task | TaskWithRelations): t is TaskWithRelations => {
    return "category" in t || "tags" in t;
  };

  const taskWithRelations = hasRelations(task) ? task : null;

  const formattedDate = formatDistanceToNow(new Date(task.created_at), {
    addSuffix: true,
  });

  return (
    <>
      <div
        className={clsx(
          "group relative p-5 rounded-2xl transition-all duration-200",
          "bg-white dark:bg-neutral-900",
          "border border-neutral-200 dark:border-neutral-800",
          "hover:border-neutral-300 dark:hover:border-neutral-700",
          "hover:shadow-soft-md hover:-translate-y-0.5",
          "cursor-pointer",
          isCompleted && "opacity-70"
        )}
        onClick={() => setShowDetail(true)}
      >
        {/* Priority indicator line */}
        <div
          className={clsx(
            "absolute left-0 top-4 bottom-4 w-1 rounded-full transition-all",
            task.priority === "Low" && "bg-neutral-300 dark:bg-neutral-600",
            task.priority === "Medium" && "bg-blue-500",
            task.priority === "High" && "bg-orange-500",
            task.priority === "Urgent" && "bg-red-500"
          )}
        />

        <div className="flex items-start gap-4 pl-3">
          {/* Checkbox */}
          <div onClick={(e) => e.stopPropagation()}>
            <TaskActions task={task} variant="checkbox" />
          </div>

          {/* Content */}
          <div className="flex-1 min-w-0">
            {/* Title */}
            <h3
              className={clsx(
                "text-body font-medium text-neutral-900 dark:text-neutral-100 mb-1",
                "transition-all duration-200",
                isCompleted && "line-through text-neutral-500 dark:text-neutral-500"
              )}
            >
              {task.title.length > 60 ? `${task.title.slice(0, 60)}...` : task.title}
            </h3>

            {/* Description preview */}
            {task.description && (
              <p
                className={clsx(
                  "text-body-sm text-neutral-500 dark:text-neutral-400 truncate-2 mb-3",
                  isCompleted && "line-through"
                )}
              >
                {task.description.length > 100
                  ? `${task.description.slice(0, 100)}...`
                  : task.description}
              </p>
            )}

            {/* Meta row */}
            <div className="flex flex-wrap items-center gap-2">
              {/* Priority badge */}
              <PriorityBadge priority={task.priority as "Low" | "Medium" | "High" | "Urgent"} size="sm" />

              {/* Category */}
              {taskWithRelations?.category && (
                <Badge variant="category" size="sm">
                  {taskWithRelations.category.name}
                </Badge>
              )}

              {/* Tags (show first 2) */}
              {taskWithRelations?.tags && taskWithRelations.tags.length > 0 && (
                <>
                  {taskWithRelations.tags.slice(0, 2).map((tag) => (
                    <Badge key={tag.id} variant="tag" size="sm">
                      {tag.name}
                    </Badge>
                  ))}
                  {taskWithRelations.tags.length > 2 && (
                    <span className="text-caption text-neutral-400 dark:text-neutral-500">
                      +{taskWithRelations.tags.length - 2} more
                    </span>
                  )}
                </>
              )}
            </div>

            {/* Timestamp */}
            <div className="flex items-center gap-4 mt-3 text-caption text-neutral-400 dark:text-neutral-500">
              <span className="flex items-center gap-1">
                <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
                {formattedDate}
              </span>
              {task.completed_at && (
                <span className="flex items-center gap-1 text-success-dark dark:text-green-400">
                  <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                  </svg>
                  Completed
                </span>
              )}
            </div>
          </div>

          {/* Actions (visible on hover) */}
          <div
            className="opacity-0 group-hover:opacity-100 transition-opacity"
            onClick={(e) => e.stopPropagation()}
          >
            <TaskActions task={task} variant="menu" />
          </div>
        </div>
      </div>

      {showDetail && (
        <TaskDetailModal task={task} onClose={() => setShowDetail(false)} />
      )}
    </>
  );
}
