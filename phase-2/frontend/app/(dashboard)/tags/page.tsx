/**
 * Tags management page with Flowspace styling.
 *
 * T111: [US5] Create tags management page
 * List all tags with create/rename/delete actions.
 */

"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { getTags, createTag, updateTag, deleteTag, type Tag } from "@/lib/api/tags";
import { clsx } from "clsx";

export default function TagsPage() {
  const [newTagName, setNewTagName] = useState("");
  const [editingTag, setEditingTag] = useState<{ id: string; name: string } | null>(null);
  const [error, setError] = useState<string | null>(null);
  const queryClient = useQueryClient();

  const { data: tags, isLoading, isError, refetch } = useQuery({
    queryKey: ["tags"],
    queryFn: getTags,
  });

  const createMutation = useMutation({
    mutationFn: createTag,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["tags"] });
      setNewTagName("");
      setError(null);
    },
    onError: (err: Error) => {
      setError(err.message);
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, name }: { id: string; name: string }) => updateTag(id, { name }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["tags"] });
      setEditingTag(null);
      setError(null);
    },
    onError: (err: Error) => {
      setError(err.message);
    },
  });

  const deleteMutation = useMutation({
    mutationFn: deleteTag,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["tags"] });
    },
    onError: (err: Error) => {
      setError(err.message);
    },
  });

  const handleCreate = (e: React.FormEvent) => {
    e.preventDefault();
    const name = newTagName.trim();
    if (!name) return;
    createMutation.mutate({ name });
  };

  const handleUpdate = (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingTag) return;
    const name = editingTag.name.trim();
    if (!name) return;
    updateMutation.mutate({ id: editingTag.id, name });
  };

  const handleDelete = (tagId: string) => {
    deleteMutation.mutate(tagId);
  };

  return (
    <div className="space-y-8">
      {/* Page Header */}
      <div>
        <h1 className="text-h1 font-display font-bold text-neutral-900 dark:text-neutral-50">
          Tags
        </h1>
        <p className="mt-1 text-body text-neutral-500 dark:text-neutral-400">
          Create and manage tags for your tasks
        </p>
      </div>

      {/* Create Tag Form */}
      <div className="card p-6">
        <form onSubmit={handleCreate} className="space-y-4">
          <div className="flex flex-col sm:flex-row gap-3">
            <div className="flex-1">
              <input
                type="text"
                value={newTagName}
                onChange={(e) => {
                  setNewTagName(e.target.value);
                  setError(null);
                }}
                placeholder="Enter new tag name..."
                className="input-field"
                maxLength={50}
              />
            </div>
            <button
              type="submit"
              disabled={createMutation.isPending || !newTagName.trim()}
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
                  Add Tag
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
            <span className="text-body">Loading tags...</span>
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
              Failed to load tags
            </h3>
            <p className="text-body-sm text-neutral-500 dark:text-neutral-400 mb-4">
              We couldn't load your tags. Please try again.
            </p>
            <button onClick={() => refetch()} className="btn-primary">
              Try Again
            </button>
          </div>
        </div>
      )}

      {/* Tags List */}
      {!isLoading && !isError && (
        <div className="space-y-4">
          <div className="flex items-center gap-3">
            <h2 className="text-h4 font-display font-semibold text-neutral-900 dark:text-neutral-100">
              Your Tags
            </h2>
            <span className="text-caption text-neutral-400 dark:text-neutral-500">
              {tags?.length || 0} tags
            </span>
          </div>

          {tags?.length === 0 ? (
            <div className="card p-8">
              <div className="text-center">
                <div className="w-12 h-12 mx-auto mb-4 rounded-xl bg-neutral-100 dark:bg-neutral-800 flex items-center justify-center">
                  <svg className="w-6 h-6 text-neutral-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M7 20l4-16m2 16l4-16M6 9h14M4 15h14" />
                  </svg>
                </div>
                <h3 className="text-h4 font-display font-semibold text-neutral-900 dark:text-neutral-100 mb-2">
                  No tags yet
                </h3>
                <p className="text-body-sm text-neutral-500 dark:text-neutral-400">
                  Create a tag above to label your tasks!
                </p>
              </div>
            </div>
          ) : (
            <div className="card p-6">
              <div className="flex flex-wrap gap-3">
                {tags?.map((tag, index) => (
                  <div
                    key={tag.id}
                    className="animate-fade-in-up"
                    style={{ animationDelay: `${index * 30}ms` }}
                  >
                    <TagItem
                      tag={tag}
                      isEditing={editingTag?.id === tag.id}
                      editValue={editingTag?.id === tag.id ? editingTag.name : ""}
                      onEditStart={() => setEditingTag({ id: tag.id, name: tag.name })}
                      onEditChange={(name) => setEditingTag({ id: tag.id, name })}
                      onEditSubmit={handleUpdate}
                      onEditCancel={() => setEditingTag(null)}
                      onDelete={handleDelete}
                      isDeleting={deleteMutation.isPending}
                      isUpdating={updateMutation.isPending}
                    />
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function TagItem({
  tag,
  isEditing,
  editValue,
  onEditStart,
  onEditChange,
  onEditSubmit,
  onEditCancel,
  onDelete,
  isDeleting,
  isUpdating,
}: {
  tag: Tag;
  isEditing: boolean;
  editValue: string;
  onEditStart: () => void;
  onEditChange: (name: string) => void;
  onEditSubmit: (e: React.FormEvent) => void;
  onEditCancel: () => void;
  onDelete: (id: string) => void;
  isDeleting: boolean;
  isUpdating: boolean;
}) {
  if (isEditing) {
    return (
      <form onSubmit={onEditSubmit} className="flex items-center gap-2">
        <input
          type="text"
          value={editValue}
          onChange={(e) => onEditChange(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Escape") {
              onEditCancel();
            }
          }}
          className="px-3 py-1.5 text-body-sm border border-accent-300 dark:border-accent-600 rounded-full focus:outline-none focus:ring-2 focus:ring-accent-500/20 bg-white dark:bg-neutral-900 text-neutral-900 dark:text-neutral-100"
          maxLength={50}
          autoFocus
        />
        <button
          type="submit"
          disabled={isUpdating || !editValue.trim()}
          className="p-1.5 text-green-600 hover:text-green-700 dark:text-green-400 hover:bg-green-50 dark:hover:bg-green-900/20 rounded-lg transition-colors disabled:opacity-50"
          title="Save"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
          </svg>
        </button>
        <button
          type="button"
          onClick={onEditCancel}
          className="p-1.5 text-neutral-400 hover:text-neutral-600 dark:hover:text-neutral-300 hover:bg-neutral-100 dark:hover:bg-neutral-800 rounded-lg transition-colors"
          title="Cancel"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </form>
    );
  }

  return (
    <div
      className={clsx(
        "group inline-flex items-center gap-2 px-4 py-2 rounded-full transition-all duration-200",
        "bg-neutral-100 dark:bg-neutral-800",
        "border border-neutral-200 dark:border-neutral-700",
        "hover:border-accent-300 dark:hover:border-accent-700",
        "hover:shadow-soft"
      )}
    >
      <svg className="w-4 h-4 text-accent-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M7 20l4-16m2 16l4-16M6 9h14M4 15h14" />
      </svg>
      <span className="text-body-sm font-medium text-neutral-700 dark:text-neutral-300">
        {tag.name}
      </span>
      <div className="flex items-center gap-1 ml-1 opacity-0 group-hover:opacity-100 transition-opacity">
        <button
          onClick={onEditStart}
          className="p-1 text-neutral-400 hover:text-accent-600 dark:hover:text-accent-400 transition-colors"
          title="Rename tag"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={2}>
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
            />
          </svg>
        </button>
        <button
          onClick={() => onDelete(tag.id)}
          disabled={isDeleting}
          className="p-1 text-neutral-400 hover:text-error transition-colors disabled:opacity-50"
          title="Delete tag"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
    </div>
  );
}
