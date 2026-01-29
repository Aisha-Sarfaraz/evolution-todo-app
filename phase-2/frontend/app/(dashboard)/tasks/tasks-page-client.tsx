"use client";

/**
 * Tasks page client component with professional Flowspace styling.
 */

import { useCallback, useEffect, useState } from "react";
import { useSearchParams, useRouter, usePathname } from "next/navigation";
import { TaskList } from "@/components/tasks/task-list";
import { TaskFilters } from "@/components/tasks/task-filters";
import { TaskForm } from "@/components/tasks/task-form";
import { Button } from "@/components/ui/button";
import type { TaskFilters as TaskFiltersType } from "@/lib/types/task";
import { clsx } from "clsx";

export function TasksPageClient() {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();

  // Parse filters from URL on mount
  const [filters, setFilters] = useState<TaskFiltersType>(() => {
    const filtersFromUrl: TaskFiltersType = {};

    const search = searchParams.get("search");
    if (search) filtersFromUrl.search = search;

    const status = searchParams.get("status");
    if (status) filtersFromUrl.status = status as TaskFiltersType["status"];

    const priority = searchParams.get("priority");
    if (priority) filtersFromUrl.priority = priority;

    const category = searchParams.get("category");
    if (category) filtersFromUrl.category = category;

    const tags = searchParams.get("tags");
    if (tags) filtersFromUrl.tags = tags;

    const sortBy = searchParams.get("sort_by");
    if (sortBy) filtersFromUrl.sort_by = sortBy as TaskFiltersType["sort_by"];

    const order = searchParams.get("order");
    if (order) filtersFromUrl.order = order as TaskFiltersType["order"];

    return filtersFromUrl;
  });

  const [showFilters, setShowFilters] = useState(false);
  const [showCreateModal, setShowCreateModal] = useState(false);

  // Sync filters to URL when they change
  useEffect(() => {
    const params = new URLSearchParams();

    if (filters.search) params.set("search", filters.search);
    if (filters.status && filters.status !== "all") params.set("status", filters.status);
    if (filters.priority) params.set("priority", filters.priority);
    if (filters.category) params.set("category", filters.category);
    if (filters.tags) params.set("tags", filters.tags);
    if (filters.sort_by && filters.sort_by !== "created_at") params.set("sort_by", filters.sort_by);
    if (filters.order && filters.order !== "desc") params.set("order", filters.order);

    const queryString = params.toString();
    const newUrl = queryString ? `${pathname}?${queryString}` : pathname;

    const currentQueryString = searchParams.toString();
    if (queryString !== currentQueryString) {
      router.replace(newUrl, { scroll: false });
    }
  }, [filters, pathname, router, searchParams]);

  const handleFiltersChange = useCallback((newFilters: TaskFiltersType) => {
    setFilters(newFilters);
  }, []);

  const handleClearFilters = useCallback(() => {
    setFilters({});
  }, []);

  const hasActiveFilters =
    filters.search ||
    (filters.status && filters.status !== "all") ||
    filters.priority ||
    filters.category ||
    filters.tags;

  return (
    <div className="space-y-8">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-h1 font-display font-bold text-neutral-900 dark:text-neutral-50">
            My Tasks
          </h1>
          <p className="mt-1 text-body text-neutral-500 dark:text-neutral-400">
            Organize, prioritize, and accomplish your goals
          </p>
        </div>
        <Button
          variant="primary"
          onClick={() => setShowCreateModal(true)}
          leftIcon={
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" />
            </svg>
          }
        >
          New Task
        </Button>
      </div>

      {/* Search and Filter Bar */}
      <div className="flex flex-col sm:flex-row gap-4">
        {/* Search Input */}
        <div className="flex-1 relative">
          <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
            <svg
              className="w-5 h-5 text-neutral-400"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth={2}
            >
              <path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
          <input
            type="text"
            placeholder="Search tasks..."
            value={filters.search || ""}
            onChange={(e) => setFilters({ ...filters, search: e.target.value || undefined })}
            className="w-full pl-12 pr-4 py-3 rounded-xl text-body bg-white dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-700 text-neutral-900 dark:text-neutral-100 placeholder:text-neutral-400 dark:placeholder:text-neutral-500 focus:outline-none focus:ring-2 focus:ring-accent-500/20 focus:border-accent-500 transition-all duration-200"
          />
          {filters.search && (
            <button
              onClick={() => setFilters({ ...filters, search: undefined })}
              className="absolute inset-y-0 right-0 pr-4 flex items-center text-neutral-400 hover:text-neutral-600 dark:hover:text-neutral-300 transition-colors"
            >
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          )}
        </div>

        {/* Filter Button */}
        <div className="flex items-center gap-3">
          <button
            onClick={() => setShowFilters(!showFilters)}
            className={clsx(
              "inline-flex items-center gap-2 px-5 py-3 rounded-xl font-medium transition-all duration-200",
              showFilters || hasActiveFilters
                ? "bg-accent-600 text-white shadow-soft hover:bg-accent-700"
                : "bg-white dark:bg-neutral-900 text-neutral-700 dark:text-neutral-300 border border-neutral-200 dark:border-neutral-700 hover:border-accent-300 dark:hover:border-accent-700 hover:text-accent-600 dark:hover:text-accent-400"
            )}
          >
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z"
              />
            </svg>
            <span>Filters</span>
            {hasActiveFilters && (
              <span className="w-2 h-2 rounded-full bg-white animate-pulse-soft" />
            )}
          </button>

          {hasActiveFilters && (
            <button
              onClick={handleClearFilters}
              className="text-body-sm font-medium text-neutral-500 dark:text-neutral-400 hover:text-accent-600 dark:hover:text-accent-400 transition-colors"
            >
              Clear all
            </button>
          )}
        </div>
      </div>

      {/* Filters Panel */}
      {showFilters && (
        <div className="animate-fade-in-down">
          <div className="card p-6">
            <TaskFilters filters={filters} onFiltersChange={handleFiltersChange} />
          </div>
        </div>
      )}

      {/* Active Filters Pills */}
      {hasActiveFilters && (
        <div className="flex flex-wrap items-center gap-2">
          <span className="text-caption text-neutral-500 dark:text-neutral-400">Active filters:</span>
          {filters.status && filters.status !== "all" && (
            <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full text-caption font-medium bg-accent-50 text-accent-700 dark:bg-accent-900/30 dark:text-accent-400">
              Status: {filters.status}
              <button
                onClick={() => setFilters({ ...filters, status: undefined })}
                className="ml-1 hover:text-accent-900 dark:hover:text-accent-300"
              >
                <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </span>
          )}
          {filters.priority && (
            <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full text-caption font-medium bg-accent-50 text-accent-700 dark:bg-accent-900/30 dark:text-accent-400">
              Priority: {filters.priority}
              <button
                onClick={() => setFilters({ ...filters, priority: undefined })}
                className="ml-1 hover:text-accent-900 dark:hover:text-accent-300"
              >
                <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </span>
          )}
          {filters.category && (
            <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full text-caption font-medium bg-accent-50 text-accent-700 dark:bg-accent-900/30 dark:text-accent-400">
              Category
              <button
                onClick={() => setFilters({ ...filters, category: undefined })}
                className="ml-1 hover:text-accent-900 dark:hover:text-accent-300"
              >
                <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </span>
          )}
        </div>
      )}

      {/* Task List */}
      <TaskList
        filters={filters}
        onClearFilters={handleClearFilters}
        onCreateTask={() => setShowCreateModal(true)}
      />

      {/* Create Task Modal */}
      {showCreateModal && (
        <TaskForm mode="create" onClose={() => setShowCreateModal(false)} />
      )}
    </div>
  );
}
