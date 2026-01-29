/**
 * Categories management page with Flowspace styling.
 *
 * T110: [US5] Create categories management page
 * List all categories with create/delete actions.
 */

"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { getCategories, createCategory, deleteCategory, type Category } from "@/lib/api/categories";
import { clsx } from "clsx";

export default function CategoriesPage() {
  const [newCategoryName, setNewCategoryName] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [deleteConfirmId, setDeleteConfirmId] = useState<string | null>(null);
  const queryClient = useQueryClient();

  const { data: categories, isLoading, isError, refetch } = useQuery({
    queryKey: ["categories"],
    queryFn: getCategories,
  });

  const createMutation = useMutation({
    mutationFn: createCategory,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["categories"] });
      setNewCategoryName("");
      setError(null);
    },
    onError: (err: Error) => {
      setError(err.message);
    },
  });

  const deleteMutation = useMutation({
    mutationFn: deleteCategory,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["categories"] });
      setDeleteConfirmId(null);
    },
    onError: (err: Error) => {
      setError(err.message);
    },
  });

  const handleCreate = (e: React.FormEvent) => {
    e.preventDefault();
    const name = newCategoryName.trim();
    if (!name) return;
    createMutation.mutate({ name });
  };

  const handleDelete = (categoryId: string) => {
    deleteMutation.mutate(categoryId);
  };

  // Separate system and custom categories
  const systemCategories = categories?.filter((c) => c.is_system) || [];
  const customCategories = categories?.filter((c) => !c.is_system) || [];

  return (
    <div className="space-y-8">
      {/* Page Header */}
      <div>
        <h1 className="text-h1 font-display font-bold text-neutral-900 dark:text-neutral-50">
          Categories
        </h1>
        <p className="mt-1 text-body text-neutral-500 dark:text-neutral-400">
          Organize your tasks with categories
        </p>
      </div>

      {/* Create Category Form */}
      <div className="card p-6">
        <form onSubmit={handleCreate} className="space-y-4">
          <div className="flex flex-col sm:flex-row gap-3">
            <div className="flex-1">
              <input
                type="text"
                value={newCategoryName}
                onChange={(e) => {
                  setNewCategoryName(e.target.value);
                  setError(null);
                }}
                placeholder="Enter new category name..."
                className="input-field"
                maxLength={50}
              />
            </div>
            <button
              type="submit"
              disabled={createMutation.isPending || !newCategoryName.trim()}
              className="btn-primary whitespace-nowrap"
            >
              {createMutation.isPending ? (
                <span className="flex items-center gap-2">
                  <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                  </svg>
                  Creating...
                </span>
              ) : (
                <span className="flex items-center gap-2">
                  <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" />
                  </svg>
                  Add Category
                </span>
              )}
            </button>
          </div>

          {error && (
            <div className="flex items-start gap-3 p-4 rounded-xl bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800">
              <svg className="w-5 h-5 text-error flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <p className="text-body-sm text-red-700 dark:text-red-400">{error}</p>
            </div>
          )}
        </form>
      </div>

      {/* Loading State */}
      {isLoading && (
        <div className="card p-8">
          <div className="flex items-center justify-center gap-3 text-neutral-500 dark:text-neutral-400">
            <svg className="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
            </svg>
            <span className="text-body">Loading categories...</span>
          </div>
        </div>
      )}

      {/* Error State */}
      {isError && (
        <div className="card p-8">
          <div className="text-center">
            <div className="w-12 h-12 mx-auto mb-4 rounded-xl bg-red-100 dark:bg-red-900/30 flex items-center justify-center">
              <svg className="w-6 h-6 text-error" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <h3 className="text-h4 font-display font-semibold text-neutral-900 dark:text-neutral-100 mb-2">
              Failed to load categories
            </h3>
            <p className="text-body-sm text-neutral-500 dark:text-neutral-400 mb-4">
              We couldn't load your categories. Please try again.
            </p>
            <button onClick={() => refetch()} className="btn-primary">
              Try Again
            </button>
          </div>
        </div>
      )}

      {/* System Categories */}
      {!isLoading && !isError && systemCategories.length > 0 && (
        <div className="space-y-4">
          <div className="flex items-center gap-3">
            <h2 className="text-h4 font-display font-semibold text-neutral-900 dark:text-neutral-100">
              System Categories
            </h2>
            <span className="text-caption text-neutral-400 dark:text-neutral-500">
              {systemCategories.length} categories
            </span>
          </div>
          <div className="grid gap-3">
            {systemCategories.map((category, index) => (
              <div
                key={category.id}
                className="animate-fade-in-up"
                style={{ animationDelay: `${index * 50}ms` }}
              >
                <CategoryItem
                  category={category}
                  onDeleteClick={() => {}}
                  isDeleting={false}
                  showDeleteConfirm={false}
                  onDeleteConfirm={() => {}}
                  onDeleteCancel={() => {}}
                />
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Custom Categories */}
      {!isLoading && !isError && (
        <div className="space-y-4">
          <div className="flex items-center gap-3">
            <h2 className="text-h4 font-display font-semibold text-neutral-900 dark:text-neutral-100">
              Your Categories
            </h2>
            <span className="text-caption text-neutral-400 dark:text-neutral-500">
              {customCategories.length} categories
            </span>
          </div>

          {customCategories.length === 0 ? (
            <div className="card p-8">
              <div className="text-center">
                <div className="w-12 h-12 mx-auto mb-4 rounded-xl bg-neutral-100 dark:bg-neutral-800 flex items-center justify-center">
                  <svg className="w-6 h-6 text-neutral-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
                  </svg>
                </div>
                <h3 className="text-h4 font-display font-semibold text-neutral-900 dark:text-neutral-100 mb-2">
                  No custom categories yet
                </h3>
                <p className="text-body-sm text-neutral-500 dark:text-neutral-400">
                  Create a category above to organize your tasks!
                </p>
              </div>
            </div>
          ) : (
            <div className="grid gap-3">
              {customCategories.map((category, index) => (
                <div
                  key={category.id}
                  className="animate-fade-in-up"
                  style={{ animationDelay: `${(systemCategories.length + index) * 50}ms` }}
                >
                  <CategoryItem
                    category={category}
                    onDeleteClick={() => setDeleteConfirmId(category.id)}
                    isDeleting={deleteMutation.isPending}
                    showDeleteConfirm={deleteConfirmId === category.id}
                    onDeleteConfirm={() => handleDelete(category.id)}
                    onDeleteCancel={() => setDeleteConfirmId(null)}
                  />
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function CategoryItem({
  category,
  onDeleteClick,
  isDeleting,
  showDeleteConfirm,
  onDeleteConfirm,
  onDeleteCancel,
}: {
  category: Category;
  onDeleteClick: () => void;
  isDeleting: boolean;
  showDeleteConfirm: boolean;
  onDeleteConfirm: () => void;
  onDeleteCancel: () => void;
}) {
  return (
    <div
      className={clsx(
        "group p-4 rounded-xl transition-all duration-200",
        "bg-white dark:bg-neutral-900",
        "border border-neutral-200 dark:border-neutral-800",
        "hover:border-neutral-300 dark:hover:border-neutral-700",
        "hover:shadow-soft-md"
      )}
    >
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-3 h-3 rounded-full bg-accent-500" />
          <span className="font-medium text-neutral-900 dark:text-neutral-100">
            {category.name}
          </span>
          {category.is_system && (
            <span className="px-2 py-0.5 text-caption font-medium bg-neutral-100 dark:bg-neutral-800 text-neutral-500 dark:text-neutral-400 rounded-md">
              System
            </span>
          )}
        </div>

        {!category.is_system && (
          <div className="flex items-center gap-2">
            {showDeleteConfirm ? (
              <div className="flex items-center gap-2 animate-fade-in">
                <span className="text-caption text-neutral-500 dark:text-neutral-400">Delete?</span>
                <button
                  onClick={onDeleteConfirm}
                  disabled={isDeleting}
                  className="px-3 py-1 text-caption font-medium text-white bg-error hover:bg-red-600 rounded-lg transition-colors disabled:opacity-50"
                >
                  {isDeleting ? "..." : "Yes"}
                </button>
                <button
                  onClick={onDeleteCancel}
                  className="px-3 py-1 text-caption font-medium text-neutral-600 dark:text-neutral-400 hover:bg-neutral-100 dark:hover:bg-neutral-800 rounded-lg transition-colors"
                >
                  No
                </button>
              </div>
            ) : (
              <button
                onClick={onDeleteClick}
                className="p-2 text-neutral-400 hover:text-error hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-colors opacity-0 group-hover:opacity-100"
                title="Delete category"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={2}>
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                  />
                </svg>
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
