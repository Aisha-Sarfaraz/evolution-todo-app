"use client";

import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { toggleComplete, deleteTask } from "@/lib/api/tasks";
import type { Task } from "@/lib/types/task";
import { TaskForm } from "./task-form";
import { clsx } from "clsx";

interface TaskActionsProps {
  task: Task;
  variant?: "checkbox" | "menu" | "full";
}

export function TaskActions({ task, variant = "full" }: TaskActionsProps) {
  const [showEditForm, setShowEditForm] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [showMenu, setShowMenu] = useState(false);
  const queryClient = useQueryClient();

  const toggleMutation = useMutation({
    mutationFn: () => toggleComplete(task.id),
    onMutate: async () => {
      await queryClient.cancelQueries({ queryKey: ["tasks"] });
      const previousTasks = queryClient.getQueryData(["tasks"]);
      queryClient.setQueryData(["tasks"], (old: { tasks: Task[]; total: number } | undefined) => {
        if (!old) return old;
        return {
          ...old,
          tasks: old.tasks.map((t) =>
            t.id === task.id
              ? {
                  ...t,
                  status: t.status === "complete" ? "pending" : "complete",
                  completed_at: t.status === "complete" ? null : new Date().toISOString(),
                }
              : t
          ),
        };
      });
      return { previousTasks };
    },
    onError: (_err, _variables, context) => {
      if (context?.previousTasks) {
        queryClient.setQueryData(["tasks"], context.previousTasks);
      }
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ["tasks"] });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: () => deleteTask(task.id),
    onMutate: async () => {
      await queryClient.cancelQueries({ queryKey: ["tasks"] });
      const previousTasks = queryClient.getQueryData(["tasks"]);
      queryClient.setQueryData(["tasks"], (old: { tasks: Task[]; total: number } | undefined) => {
        if (!old) return old;
        return {
          ...old,
          tasks: old.tasks.filter((t) => t.id !== task.id),
          total: old.total - 1,
        };
      });
      return { previousTasks };
    },
    onError: (_err, _variables, context) => {
      if (context?.previousTasks) {
        queryClient.setQueryData(["tasks"], context.previousTasks);
      }
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ["tasks"] });
      setShowDeleteConfirm(false);
    },
  });

  const isCompleted = task.status === "complete";

  // Checkbox only
  if (variant === "checkbox") {
    return (
      <button
        onClick={(e) => {
          e.stopPropagation();
          toggleMutation.mutate();
        }}
        disabled={toggleMutation.isPending}
        className={clsx(
          "w-6 h-6 rounded-full flex items-center justify-center transition-all duration-200",
          "border-2 focus:outline-none focus:ring-2 focus:ring-accent-500/20 focus:ring-offset-2",
          isCompleted
            ? "bg-success border-success text-white"
            : "border-neutral-300 dark:border-neutral-600 hover:border-success hover:bg-success/10",
          toggleMutation.isPending && "opacity-50"
        )}
        aria-label={isCompleted ? "Mark as incomplete" : "Mark as complete"}
      >
        {isCompleted && (
          <svg
            className="w-3.5 h-3.5"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            strokeWidth={3}
          >
            <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
          </svg>
        )}
      </button>
    );
  }

  // Menu only
  if (variant === "menu") {
    return (
      <div className="relative">
        <button
          onClick={(e) => {
            e.stopPropagation();
            setShowMenu(!showMenu);
          }}
          className="p-2 rounded-lg text-neutral-400 hover:text-neutral-600 dark:hover:text-neutral-300 hover:bg-neutral-100 dark:hover:bg-neutral-800 transition-colors"
          aria-label="Task actions"
        >
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M12 5v.01M12 12v.01M12 19v.01M12 6a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2z"
            />
          </svg>
        </button>

        {showMenu && (
          <>
            <div className="fixed inset-0 z-40" onClick={() => setShowMenu(false)} />
            <div className="absolute right-0 top-full mt-1 z-50 min-w-[160px] py-1.5 bg-white dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-800 rounded-xl shadow-soft-lg animate-fade-in-down">
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  setShowMenu(false);
                  setShowEditForm(true);
                }}
                className="w-full px-4 py-2.5 text-left text-body-sm text-neutral-700 dark:text-neutral-300 hover:bg-neutral-50 dark:hover:bg-neutral-800 transition-colors flex items-center gap-3"
              >
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
                  />
                </svg>
                Edit
              </button>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  setShowMenu(false);
                  toggleMutation.mutate();
                }}
                className="w-full px-4 py-2.5 text-left text-body-sm text-neutral-700 dark:text-neutral-300 hover:bg-neutral-50 dark:hover:bg-neutral-800 transition-colors flex items-center gap-3"
              >
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                </svg>
                {isCompleted ? "Mark incomplete" : "Mark complete"}
              </button>
              <div className="my-1.5 border-t border-neutral-100 dark:border-neutral-800" />
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  setShowMenu(false);
                  setShowDeleteConfirm(true);
                }}
                className="w-full px-4 py-2.5 text-left text-body-sm text-error hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors flex items-center gap-3"
              >
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                  />
                </svg>
                Delete
              </button>
            </div>
          </>
        )}

        {/* Edit modal */}
        {showEditForm && (
          <TaskForm
            mode="edit"
            task={task}
            onClose={() => setShowEditForm(false)}
          />
        )}

        {/* Delete confirmation modal */}
        {showDeleteConfirm && (
          <>
            <div
              className="fixed inset-0 z-50 bg-neutral-900/60 dark:bg-black/70 backdrop-blur-sm animate-fade-in"
              onClick={(e) => {
                e.stopPropagation();
                setShowDeleteConfirm(false);
              }}
            />
            <div
              className="fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 z-50 w-full max-w-sm p-6 bg-white dark:bg-neutral-900 rounded-2xl shadow-soft-xl border border-neutral-200 dark:border-neutral-800 animate-scale-in"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="flex items-start gap-4">
                <div className="w-10 h-10 rounded-full bg-red-100 dark:bg-red-900/30 flex items-center justify-center flex-shrink-0">
                  <svg
                    className="w-5 h-5 text-error"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                    strokeWidth={2}
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                    />
                  </svg>
                </div>
                <div>
                  <h3 className="text-h4 font-display font-semibold text-neutral-900 dark:text-neutral-100 mb-1">
                    Delete task?
                  </h3>
                  <p className="text-body-sm text-neutral-500 dark:text-neutral-400">
                    This action cannot be undone. The task will be permanently removed.
                  </p>
                </div>
              </div>
              <div className="flex items-center justify-end gap-3 mt-6">
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    setShowDeleteConfirm(false);
                  }}
                  className="btn-ghost"
                >
                  Cancel
                </button>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    deleteMutation.mutate();
                  }}
                  disabled={deleteMutation.isPending}
                  className="btn-destructive"
                >
                  {deleteMutation.isPending ? "Deleting..." : "Delete"}
                </button>
              </div>
            </div>
          </>
        )}
      </div>
    );
  }

  // Full variant (default)
  return (
    <div className="flex items-center gap-2" onClick={(e) => e.stopPropagation()}>
      <button
        onClick={() => toggleMutation.mutate()}
        disabled={toggleMutation.isPending}
        className={clsx(
          "w-6 h-6 rounded-full flex items-center justify-center transition-all duration-200",
          "border-2 focus:outline-none focus:ring-2 focus:ring-accent-500/20 focus:ring-offset-2",
          isCompleted
            ? "bg-success border-success text-white"
            : "border-neutral-300 dark:border-neutral-600 hover:border-success hover:bg-success/10",
          toggleMutation.isPending && "opacity-50"
        )}
        aria-label={isCompleted ? "Mark as incomplete" : "Mark as complete"}
      >
        {isCompleted && (
          <svg
            className="w-3.5 h-3.5"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            strokeWidth={3}
          >
            <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
          </svg>
        )}
      </button>

      <button
        onClick={() => setShowEditForm(true)}
        className="p-1.5 rounded-lg text-neutral-400 hover:text-neutral-600 dark:hover:text-neutral-300 hover:bg-neutral-100 dark:hover:bg-neutral-800 transition-colors"
        aria-label="Edit task"
      >
        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
          />
        </svg>
      </button>

      <button
        onClick={() => setShowDeleteConfirm(true)}
        className="p-1.5 rounded-lg text-neutral-400 hover:text-error hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors"
        aria-label="Delete task"
      >
        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
          />
        </svg>
      </button>

      {/* Edit modal */}
      {showEditForm && (
        <TaskForm mode="edit" task={task} onClose={() => setShowEditForm(false)} />
      )}

      {/* Delete confirmation modal */}
      {showDeleteConfirm && (
        <>
          <div
            className="fixed inset-0 z-50 bg-neutral-900/60 dark:bg-black/70 backdrop-blur-sm animate-fade-in"
            onClick={() => setShowDeleteConfirm(false)}
          />
          <div className="fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 z-50 w-full max-w-sm p-6 bg-white dark:bg-neutral-900 rounded-2xl shadow-soft-xl border border-neutral-200 dark:border-neutral-800 animate-scale-in">
            <div className="flex items-start gap-4">
              <div className="w-10 h-10 rounded-full bg-red-100 dark:bg-red-900/30 flex items-center justify-center flex-shrink-0">
                <svg
                  className="w-5 h-5 text-error"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  strokeWidth={2}
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                  />
                </svg>
              </div>
              <div>
                <h3 className="text-h4 font-display font-semibold text-neutral-900 dark:text-neutral-100 mb-1">
                  Delete task?
                </h3>
                <p className="text-body-sm text-neutral-500 dark:text-neutral-400">
                  This action cannot be undone. The task will be permanently removed.
                </p>
              </div>
            </div>
            <div className="flex items-center justify-end gap-3 mt-6">
              <button onClick={() => setShowDeleteConfirm(false)} className="btn-ghost">
                Cancel
              </button>
              <button
                onClick={() => deleteMutation.mutate()}
                disabled={deleteMutation.isPending}
                className="btn-destructive"
              >
                {deleteMutation.isPending ? "Deleting..." : "Delete"}
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
