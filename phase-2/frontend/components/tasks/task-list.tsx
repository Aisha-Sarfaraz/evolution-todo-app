"use client";

import { useQuery } from "@tanstack/react-query";
import { getTasks } from "@/lib/api/tasks";
import { TaskCard } from "./task-card";
import { SkeletonTaskList } from "@/components/ui/skeleton";
import { EmptyTasksState, EmptySearchState, ErrorState } from "@/components/ui/empty-state";
import type { Task, TaskFilters } from "@/lib/types/task";

interface TaskListProps {
  filters?: TaskFilters;
  onClearFilters?: () => void;
  onCreateTask?: () => void;
}

export function TaskList({ filters, onClearFilters, onCreateTask }: TaskListProps) {
  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ["tasks", filters],
    queryFn: () => getTasks(filters),
  });

  if (isLoading) {
    return (
      <div className="space-y-4">
        <div className="flex items-center justify-between mb-2">
          <div className="h-5 w-32 bg-neutral-200 dark:bg-neutral-800 rounded animate-pulse" />
        </div>
        <SkeletonTaskList count={5} />
      </div>
    );
  }

  if (error) {
    return (
      <div className="card p-8">
        <ErrorState
          title="Failed to load tasks"
          description="We couldn't load your tasks. Please check your connection and try again."
          onRetry={() => refetch()}
        />
      </div>
    );
  }

  const tasks = data?.tasks || [];
  const total = data?.total || 0;

  const hasFilters =
    filters &&
    (filters.search ||
      (filters.status && filters.status !== "all") ||
      filters.priority ||
      filters.category ||
      filters.tags);

  if (tasks.length === 0) {
    return (
      <div className="card p-8">
        {hasFilters ? (
          <EmptySearchState
            searchTerm={filters?.search}
            onClearSearch={onClearFilters}
          />
        ) : (
          <EmptyTasksState onCreateTask={onCreateTask} />
        )}
      </div>
    );
  }

  const pendingTasks = tasks.filter((t: Task) => t.status === "pending");
  const completedTasks = tasks.filter((t: Task) => t.status === "complete");

  return (
    <div className="space-y-6">
      {/* Stats bar */}
      <div className="flex items-center justify-between">
        <p className="text-body-sm text-neutral-500 dark:text-neutral-400">
          {total} task{total !== 1 ? "s" : ""} total
          {pendingTasks.length > 0 && (
            <span className="text-neutral-400 dark:text-neutral-500">
              {" "}· {pendingTasks.length} pending
            </span>
          )}
          {completedTasks.length > 0 && (
            <span className="text-success-dark dark:text-green-400">
              {" "}· {completedTasks.length} completed
            </span>
          )}
        </p>
      </div>

      {/* Task list */}
      <div className="space-y-3">
        {/* Pending tasks first */}
        {pendingTasks.map((task: Task, index: number) => (
          <div
            key={task.id}
            className="animate-fade-in-up"
            style={{ animationDelay: `${index * 50}ms` }}
          >
            <TaskCard task={task} />
          </div>
        ))}

        {/* Completed tasks section */}
        {completedTasks.length > 0 && pendingTasks.length > 0 && (
          <div className="pt-4">
            <div className="flex items-center gap-3 mb-4">
              <div className="h-px flex-1 bg-neutral-200 dark:bg-neutral-800" />
              <span className="text-caption font-medium text-neutral-400 dark:text-neutral-500 uppercase tracking-wider">
                Completed
              </span>
              <div className="h-px flex-1 bg-neutral-200 dark:bg-neutral-800" />
            </div>
          </div>
        )}

        {completedTasks.map((task: Task, index: number) => (
          <div
            key={task.id}
            className="animate-fade-in-up"
            style={{ animationDelay: `${(pendingTasks.length + index) * 50}ms` }}
          >
            <TaskCard task={task} />
          </div>
        ))}
      </div>
    </div>
  );
}
