"use client";

/**
 * Task detail modal component with professional Flowspace styling.
 * Displays full task information with edit capability.
 */

import { useState } from "react";
import type { Task, TaskWithRelations } from "@/lib/types/task";
import { TaskForm } from "./task-form";
import { TaskActions } from "./task-actions";
import { PriorityBadge, StatusBadge, Badge } from "@/components/ui/badge";
import { clsx } from "clsx";
import { format, formatDistanceToNow } from "date-fns";

interface TaskDetailModalProps {
  task: Task | TaskWithRelations;
  onClose: () => void;
}

export function TaskDetailModal({ task, onClose }: TaskDetailModalProps) {
  const [isEditing, setIsEditing] = useState(false);

  const hasRelations = (t: Task | TaskWithRelations): t is TaskWithRelations => {
    return "category" in t || "tags" in t;
  };

  const taskWithRelations = hasRelations(task) ? task : null;

  if (isEditing) {
    return (
      <TaskForm
        mode="edit"
        task={task}
        onClose={() => {
          setIsEditing(false);
          onClose();
        }}
      />
    );
  }

  const isCompleted = task.status === "complete";

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 z-50 bg-neutral-900/60 dark:bg-black/70 backdrop-blur-sm animate-fade-in"
        onClick={onClose}
      />

      {/* Modal */}
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4 pointer-events-none">
        <div
          className="relative w-full max-w-2xl max-h-[90vh] overflow-hidden bg-white dark:bg-neutral-900 rounded-2xl shadow-soft-xl border border-neutral-200 dark:border-neutral-800 pointer-events-auto animate-scale-in"
          onClick={(e) => e.stopPropagation()}
        >
          {/* Priority indicator bar */}
          <div
            className={clsx(
              "absolute top-0 left-0 right-0 h-1",
              task.priority === "Low" && "bg-neutral-300 dark:bg-neutral-600",
              task.priority === "Medium" && "bg-blue-500",
              task.priority === "High" && "bg-orange-500",
              task.priority === "Urgent" && "bg-red-500"
            )}
          />

          {/* Header */}
          <div className="flex items-start justify-between gap-4 px-6 pt-6 pb-4">
            <div className="flex-1 min-w-0">
              <h2
                className={clsx(
                  "text-h2 font-display font-bold text-neutral-900 dark:text-neutral-100 mb-2",
                  isCompleted && "line-through opacity-70"
                )}
              >
                {task.title}
              </h2>
              <div className="flex flex-wrap items-center gap-2">
                <StatusBadge status={isCompleted ? "complete" : "pending"} />
                <PriorityBadge priority={task.priority as "Low" | "Medium" | "High" | "Urgent"} />
                {taskWithRelations?.category && (
                  <Badge variant="category">
                    {taskWithRelations.category.name}
                  </Badge>
                )}
              </div>
            </div>
            <button
              onClick={onClose}
              className="p-2 -mr-2 -mt-2 text-neutral-400 hover:text-neutral-600 dark:hover:text-neutral-300 hover:bg-neutral-100 dark:hover:bg-neutral-800 rounded-lg transition-colors flex-shrink-0"
              aria-label="Close"
            >
              <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          {/* Content */}
          <div className="px-6 pb-6 space-y-6 overflow-y-auto max-h-[calc(90vh-200px)]">
            {/* Tags */}
            {taskWithRelations?.tags && taskWithRelations.tags.length > 0 && (
              <div className="flex flex-wrap gap-2">
                {taskWithRelations.tags.map((tag) => (
                  <Badge key={tag.id} variant="tag">
                    {tag.name}
                  </Badge>
                ))}
              </div>
            )}

            {/* Description */}
            <div className="space-y-2">
              <h3 className="text-body-sm font-medium text-neutral-500 dark:text-neutral-400 uppercase tracking-wider">
                Description
              </h3>
              <div className="p-4 rounded-xl bg-neutral-50 dark:bg-neutral-800/50 border border-neutral-100 dark:border-neutral-800">
                {task.description ? (
                  <p className="text-body text-neutral-700 dark:text-neutral-300 whitespace-pre-wrap">
                    {task.description}
                  </p>
                ) : (
                  <p className="text-body text-neutral-400 dark:text-neutral-500 italic">
                    No description provided
                  </p>
                )}
              </div>
            </div>

            {/* Metadata */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="p-4 rounded-xl bg-neutral-50 dark:bg-neutral-800/50 border border-neutral-100 dark:border-neutral-800">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-xl bg-accent-100 dark:bg-accent-900/30 flex items-center justify-center">
                    <svg className="w-5 h-5 text-accent-600 dark:text-accent-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                    </svg>
                  </div>
                  <div>
                    <p className="text-caption text-neutral-500 dark:text-neutral-400">Created</p>
                    <p className="text-body-sm font-medium text-neutral-900 dark:text-neutral-100">
                      {format(new Date(task.created_at), "MMM d, yyyy")}
                    </p>
                    <p className="text-caption text-neutral-400 dark:text-neutral-500">
                      {formatDistanceToNow(new Date(task.created_at), { addSuffix: true })}
                    </p>
                  </div>
                </div>
              </div>

              {task.updated_at && task.updated_at !== task.created_at && (
                <div className="p-4 rounded-xl bg-neutral-50 dark:bg-neutral-800/50 border border-neutral-100 dark:border-neutral-800">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-xl bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center">
                      <svg className="w-5 h-5 text-blue-600 dark:text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                        <path strokeLinecap="round" strokeLinejoin="round" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                      </svg>
                    </div>
                    <div>
                      <p className="text-caption text-neutral-500 dark:text-neutral-400">Last Updated</p>
                      <p className="text-body-sm font-medium text-neutral-900 dark:text-neutral-100">
                        {format(new Date(task.updated_at), "MMM d, yyyy")}
                      </p>
                      <p className="text-caption text-neutral-400 dark:text-neutral-500">
                        {formatDistanceToNow(new Date(task.updated_at), { addSuffix: true })}
                      </p>
                    </div>
                  </div>
                </div>
              )}

              {task.completed_at && (
                <div className="p-4 rounded-xl bg-green-50 dark:bg-green-900/20 border border-green-100 dark:border-green-900/30">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-xl bg-green-100 dark:bg-green-900/30 flex items-center justify-center">
                      <svg className="w-5 h-5 text-green-600 dark:text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                        <path strokeLinecap="round" strokeLinejoin="round" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                    </div>
                    <div>
                      <p className="text-caption text-green-600 dark:text-green-400">Completed</p>
                      <p className="text-body-sm font-medium text-green-700 dark:text-green-300">
                        {format(new Date(task.completed_at), "MMM d, yyyy")}
                      </p>
                      <p className="text-caption text-green-600/70 dark:text-green-400/70">
                        {formatDistanceToNow(new Date(task.completed_at), { addSuffix: true })}
                      </p>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Footer */}
          <div className="flex items-center justify-between gap-4 px-6 py-4 border-t border-neutral-100 dark:border-neutral-800 bg-neutral-50 dark:bg-neutral-800/50">
            <div onClick={(e) => e.stopPropagation()}>
              <TaskActions task={task} variant="checkbox" />
            </div>
            <div className="flex items-center gap-3">
              <button
                onClick={onClose}
                className="btn-ghost"
              >
                Close
              </button>
              <button
                onClick={() => setIsEditing(true)}
                className="btn-primary"
              >
                <svg className="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                </svg>
                Edit Task
              </button>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
