"use client";

/**
 * Task filters component with professional Flowspace styling.
 * Provides status, priority, and sort controls.
 */

import { useCallback, useEffect, useState } from "react";
import type { TaskFilters, TaskPriority, TaskStatus } from "@/lib/types/task";
import { clsx } from "clsx";

interface TaskFiltersProps {
  filters: TaskFilters;
  onFiltersChange: (filters: TaskFilters) => void;
}

const PRIORITIES: { value: TaskPriority; label: string; color: string; bgColor: string }[] = [
  { value: "Low", label: "Low", color: "text-neutral-600 dark:text-neutral-400", bgColor: "bg-neutral-100 dark:bg-neutral-800" },
  { value: "Medium", label: "Medium", color: "text-blue-600 dark:text-blue-400", bgColor: "bg-blue-50 dark:bg-blue-900/30" },
  { value: "High", label: "High", color: "text-orange-600 dark:text-orange-400", bgColor: "bg-orange-50 dark:bg-orange-900/30" },
  { value: "Urgent", label: "Urgent", color: "text-red-600 dark:text-red-400", bgColor: "bg-red-50 dark:bg-red-900/30" },
];

const STATUSES: { value: TaskStatus | "all"; label: string; icon: React.ReactNode }[] = [
  {
    value: "all",
    label: "All",
    icon: (
      <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M4 6h16M4 10h16M4 14h16M4 18h16" />
      </svg>
    ),
  },
  {
    value: "pending",
    label: "Pending",
    icon: (
      <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
    ),
  },
  {
    value: "complete",
    label: "Completed",
    icon: (
      <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
    ),
  },
];

const SORT_OPTIONS = [
  { value: "created_at", label: "Date Created" },
  { value: "updated_at", label: "Date Updated" },
  { value: "priority", label: "Priority" },
  { value: "title", label: "Title" },
];

export function TaskFilters({ filters, onFiltersChange }: TaskFiltersProps) {
  const [searchValue, setSearchValue] = useState(filters.search || "");

  // Debounced search
  useEffect(() => {
    const timer = setTimeout(() => {
      if (searchValue !== filters.search) {
        onFiltersChange({ ...filters, search: searchValue || undefined });
      }
    }, 300);
    return () => clearTimeout(timer);
  }, [searchValue, filters, onFiltersChange]);

  // Sync search value with filters
  useEffect(() => {
    setSearchValue(filters.search || "");
  }, [filters.search]);

  const handleStatusChange = useCallback(
    (status: TaskStatus | "all") => {
      onFiltersChange({ ...filters, status: status === "all" ? undefined : status });
    },
    [filters, onFiltersChange]
  );

  const handlePriorityToggle = useCallback(
    (priority: TaskPriority) => {
      const currentPriorities = filters.priority?.split(",").filter(Boolean) || [];
      const index = currentPriorities.indexOf(priority);
      let newPriorities: string[];
      if (index >= 0) {
        newPriorities = currentPriorities.filter((p) => p !== priority);
      } else {
        newPriorities = [...currentPriorities, priority];
      }
      onFiltersChange({
        ...filters,
        priority: newPriorities.length > 0 ? newPriorities.join(",") : undefined,
      });
    },
    [filters, onFiltersChange]
  );

  const handleSortChange = useCallback(
    (sortBy: string) => {
      onFiltersChange({ ...filters, sort_by: sortBy as TaskFilters["sort_by"] });
    },
    [filters, onFiltersChange]
  );

  const handleOrderToggle = useCallback(() => {
    onFiltersChange({
      ...filters,
      order: filters.order === "asc" ? "desc" : "asc",
    });
  }, [filters, onFiltersChange]);

  const selectedPriorities = filters.priority?.split(",").filter(Boolean) || [];

  return (
    <div className="space-y-6">
      {/* Status Toggle */}
      <div className="space-y-3">
        <label className="text-body-sm font-medium text-neutral-700 dark:text-neutral-300">
          Status
        </label>
        <div className="flex flex-wrap gap-2">
          {STATUSES.map((status) => {
            const isActive = (filters.status || "all") === status.value;
            return (
              <button
                key={status.value}
                onClick={() => handleStatusChange(status.value)}
                className={clsx(
                  "inline-flex items-center gap-2 px-4 py-2 rounded-xl text-body-sm font-medium transition-all duration-200",
                  isActive
                    ? "bg-accent-600 text-white shadow-sm"
                    : "bg-neutral-100 dark:bg-neutral-800 text-neutral-600 dark:text-neutral-400 hover:bg-neutral-200 dark:hover:bg-neutral-700"
                )}
              >
                {status.icon}
                {status.label}
              </button>
            );
          })}
        </div>
      </div>

      {/* Priority Filters */}
      <div className="space-y-3">
        <label className="text-body-sm font-medium text-neutral-700 dark:text-neutral-300">
          Priority
        </label>
        <div className="flex flex-wrap gap-2">
          {PRIORITIES.map((priority) => {
            const isSelected = selectedPriorities.includes(priority.value);
            return (
              <button
                key={priority.value}
                onClick={() => handlePriorityToggle(priority.value)}
                className={clsx(
                  "inline-flex items-center gap-2 px-4 py-2 rounded-xl text-body-sm font-medium transition-all duration-200",
                  isSelected
                    ? `${priority.bgColor} ${priority.color} ring-2 ring-current ring-opacity-30`
                    : "bg-neutral-100 dark:bg-neutral-800 text-neutral-600 dark:text-neutral-400 hover:bg-neutral-200 dark:hover:bg-neutral-700"
                )}
              >
                <span className={clsx(
                  "w-2 h-2 rounded-full",
                  priority.value === "Low" && "bg-neutral-400",
                  priority.value === "Medium" && "bg-blue-500",
                  priority.value === "High" && "bg-orange-500",
                  priority.value === "Urgent" && "bg-red-500"
                )} />
                {priority.label}
                {isSelected && (
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                  </svg>
                )}
              </button>
            );
          })}
        </div>
      </div>

      {/* Sort Controls */}
      <div className="space-y-3">
        <label className="text-body-sm font-medium text-neutral-700 dark:text-neutral-300">
          Sort By
        </label>
        <div className="flex items-center gap-3">
          <select
            value={filters.sort_by || "created_at"}
            onChange={(e) => handleSortChange(e.target.value)}
            className="select-field flex-1"
          >
            {SORT_OPTIONS.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>

          <button
            onClick={handleOrderToggle}
            className={clsx(
              "p-3 rounded-xl border transition-all duration-200",
              "bg-white dark:bg-neutral-900 border-neutral-200 dark:border-neutral-700",
              "text-neutral-600 dark:text-neutral-400",
              "hover:border-accent-300 dark:hover:border-accent-700 hover:text-accent-600 dark:hover:text-accent-400"
            )}
            title={filters.order === "asc" ? "Ascending order" : "Descending order"}
          >
            {filters.order === "asc" ? (
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M3 4h13M3 8h9m-9 4h6m4 0l4-4m0 0l4 4m-4-4v12" />
              </svg>
            ) : (
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M3 4h13M3 8h9m-9 4h9m5-4v12m0 0l-4-4m4 4l4-4" />
              </svg>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
