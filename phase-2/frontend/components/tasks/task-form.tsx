"use client";

/**
 * Task form component with professional Flowspace styling.
 * Supports both create and edit modes with validation.
 */

import { useState } from "react";
import { useForm } from "react-hook-form";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { createTask, updateTask } from "@/lib/api/tasks";
import { getCategories } from "@/lib/api/categories";
import { getTags, createTag } from "@/lib/api/tags";
import type { Task, TaskCreate, TaskUpdate, TaskWithRelations } from "@/lib/types/task";
import { clsx } from "clsx";

interface TaskFormProps {
  mode: "create" | "edit";
  task?: Task | TaskWithRelations;
  onClose?: () => void;
}

interface TaskFormData {
  title: string;
  description: string;
  priority: string;
  category_id: string;
}

const PRIORITY_OPTIONS = [
  { value: "Low", label: "Low", color: "text-neutral-500" },
  { value: "Medium", label: "Medium", color: "text-blue-500" },
  { value: "High", label: "High", color: "text-orange-500" },
  { value: "Urgent", label: "Urgent", color: "text-red-500" },
];

const MAX_TITLE_LENGTH = 200;
const MAX_DESCRIPTION_LENGTH = 2000;

export function TaskForm({ mode, task, onClose }: TaskFormProps) {
  const hasRelations = (t?: Task | TaskWithRelations): t is TaskWithRelations => {
    return t !== undefined && "tags" in t;
  };

  const [selectedTags, setSelectedTags] = useState<string[]>(
    hasRelations(task) && task.tags ? task.tags.map((t) => t.id) : []
  );
  const [newTagName, setNewTagName] = useState("");
  const [showTagInput, setShowTagInput] = useState(false);
  const queryClient = useQueryClient();

  const { data: categories } = useQuery({
    queryKey: ["categories"],
    queryFn: getCategories,
  });

  const { data: tags } = useQuery({
    queryKey: ["tags"],
    queryFn: getTags,
  });

  const {
    register,
    handleSubmit,
    reset,
    watch,
    formState: { errors },
  } = useForm<TaskFormData>({
    defaultValues: {
      title: task?.title || "",
      description: task?.description || "",
      priority: task?.priority || "Medium",
      category_id: task?.category_id || "",
    },
  });

  const titleValue = watch("title");
  const descriptionValue = watch("description");

  const createMutation = useMutation({
    mutationFn: (data: TaskCreate) => createTask(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["tasks"] });
      reset();
      setSelectedTags([]);
      onClose?.();
    },
  });

  const updateMutation = useMutation({
    mutationFn: (data: TaskUpdate) => updateTask(task!.id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["tasks"] });
      onClose?.();
    },
  });

  const createTagMutation = useMutation({
    mutationFn: createTag,
    onSuccess: (newTag) => {
      queryClient.invalidateQueries({ queryKey: ["tags"] });
      setSelectedTags((prev) => [...prev, newTag.id]);
      setNewTagName("");
      setShowTagInput(false);
    },
  });

  const mutation = mode === "create" ? createMutation : updateMutation;

  const onSubmit = (data: TaskFormData) => {
    const taskData: TaskCreate | TaskUpdate = {
      title: data.title.trim(),
      description: data.description?.trim() || null,
      priority: data.priority as Task["priority"],
      category_id: data.category_id || null,
      ...(selectedTags.length > 0 && { tag_ids: selectedTags }),
    };

    if (mode === "create") {
      createMutation.mutate(taskData as TaskCreate);
    } else {
      updateMutation.mutate(taskData as TaskUpdate);
    }
  };

  const handleTagToggle = (tagId: string) => {
    setSelectedTags((prev) =>
      prev.includes(tagId) ? prev.filter((id) => id !== tagId) : [...prev, tagId]
    );
  };

  const handleCreateTag = () => {
    const name = newTagName.trim();
    if (!name) return;
    createTagMutation.mutate({ name });
  };

  const handleClose = () => {
    reset();
    setSelectedTags([]);
    onClose?.();
  };

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 z-50 bg-neutral-900/60 dark:bg-black/70 backdrop-blur-sm animate-fade-in"
        onClick={handleClose}
      />

      {/* Modal */}
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4 pointer-events-none">
        <div
          className="relative w-full max-w-lg max-h-[90vh] overflow-hidden bg-white dark:bg-neutral-900 rounded-2xl shadow-soft-xl border border-neutral-200 dark:border-neutral-800 pointer-events-auto animate-scale-in"
          onClick={(e) => e.stopPropagation()}
        >
          {/* Header */}
          <div className="flex items-center justify-between px-6 py-4 border-b border-neutral-100 dark:border-neutral-800">
            <h2 className="text-h3 font-display font-semibold text-neutral-900 dark:text-neutral-100">
              {mode === "create" ? "Create New Task" : "Edit Task"}
            </h2>
            <button
              onClick={handleClose}
              className="p-2 -mr-2 text-neutral-400 hover:text-neutral-600 dark:hover:text-neutral-300 hover:bg-neutral-100 dark:hover:bg-neutral-800 rounded-lg transition-colors"
              aria-label="Close"
            >
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit(onSubmit)} className="overflow-y-auto max-h-[calc(90vh-140px)]">
            <div className="p-6 space-y-5">
              {/* Error Alert */}
              {mutation.isError && (
                <div className="p-4 rounded-xl bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800">
                  <div className="flex items-start gap-3">
                    <svg className="w-5 h-5 text-error flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <p className="text-body-sm text-red-700 dark:text-red-400">
                      Failed to {mode === "create" ? "create" : "update"} task. Please try again.
                    </p>
                  </div>
                </div>
              )}

              {/* Title Field */}
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <label htmlFor="title" className="text-body-sm font-medium text-neutral-700 dark:text-neutral-300">
                    Title <span className="text-error">*</span>
                  </label>
                  <span className={clsx(
                    "text-caption",
                    titleValue?.length > MAX_TITLE_LENGTH * 0.9
                      ? "text-error"
                      : "text-neutral-400 dark:text-neutral-500"
                  )}>
                    {titleValue?.length || 0}/{MAX_TITLE_LENGTH}
                  </span>
                </div>
                <input
                  id="title"
                  type="text"
                  maxLength={MAX_TITLE_LENGTH}
                  className={clsx(
                    "input-field",
                    errors.title && "border-error focus:border-error focus:ring-error/20"
                  )}
                  placeholder="What needs to be done?"
                  {...register("title", {
                    required: "Title is required",
                    maxLength: { value: MAX_TITLE_LENGTH, message: `Maximum ${MAX_TITLE_LENGTH} characters` },
                  })}
                />
                {errors.title && (
                  <p className="text-caption text-error flex items-center gap-1">
                    <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    {errors.title.message}
                  </p>
                )}
              </div>

              {/* Description Field */}
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <label htmlFor="description" className="text-body-sm font-medium text-neutral-700 dark:text-neutral-300">
                    Description
                  </label>
                  <span className={clsx(
                    "text-caption",
                    (descriptionValue?.length || 0) > MAX_DESCRIPTION_LENGTH * 0.9
                      ? "text-error"
                      : "text-neutral-400 dark:text-neutral-500"
                  )}>
                    {descriptionValue?.length || 0}/{MAX_DESCRIPTION_LENGTH}
                  </span>
                </div>
                <textarea
                  id="description"
                  rows={4}
                  maxLength={MAX_DESCRIPTION_LENGTH}
                  className="input-field resize-none"
                  placeholder="Add more details about this task..."
                  {...register("description", {
                    maxLength: { value: MAX_DESCRIPTION_LENGTH, message: `Maximum ${MAX_DESCRIPTION_LENGTH} characters` },
                  })}
                />
              </div>

              {/* Priority & Category Row */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {/* Priority */}
                <div className="space-y-2">
                  <label htmlFor="priority" className="text-body-sm font-medium text-neutral-700 dark:text-neutral-300">
                    Priority
                  </label>
                  <select
                    id="priority"
                    className="select-field"
                    {...register("priority")}
                  >
                    {PRIORITY_OPTIONS.map((option) => (
                      <option key={option.value} value={option.value}>
                        {option.label}
                      </option>
                    ))}
                  </select>
                </div>

                {/* Category */}
                <div className="space-y-2">
                  <label htmlFor="category_id" className="text-body-sm font-medium text-neutral-700 dark:text-neutral-300">
                    Category
                  </label>
                  <select
                    id="category_id"
                    className="select-field"
                    {...register("category_id")}
                  >
                    <option value="">No category</option>
                    {categories?.map((category) => (
                      <option key={category.id} value={category.id}>
                        {category.name}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              {/* Tags */}
              <div className="space-y-3">
                <label className="text-body-sm font-medium text-neutral-700 dark:text-neutral-300">
                  Tags
                </label>

                {/* Tag Chips */}
                {tags && tags.length > 0 && (
                  <div className="flex flex-wrap gap-2">
                    {tags.map((tag) => {
                      const isSelected = selectedTags.includes(tag.id);
                      return (
                        <button
                          key={tag.id}
                          type="button"
                          onClick={() => handleTagToggle(tag.id)}
                          className={clsx(
                            "inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-caption font-medium transition-all duration-200",
                            isSelected
                              ? "bg-accent-600 text-white shadow-sm"
                              : "bg-neutral-100 dark:bg-neutral-800 text-neutral-600 dark:text-neutral-400 hover:bg-neutral-200 dark:hover:bg-neutral-700"
                          )}
                        >
                          <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                            <path strokeLinecap="round" strokeLinejoin="round" d="M7 20l4-16m2 16l4-16M6 9h14M4 15h14" />
                          </svg>
                          {tag.name}
                          {isSelected && (
                            <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                              <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                            </svg>
                          )}
                        </button>
                      );
                    })}
                  </div>
                )}

                {/* Add New Tag */}
                {showTagInput ? (
                  <div className="flex items-center gap-2">
                    <input
                      type="text"
                      value={newTagName}
                      onChange={(e) => setNewTagName(e.target.value)}
                      onKeyDown={(e) => {
                        if (e.key === "Enter") {
                          e.preventDefault();
                          handleCreateTag();
                        }
                        if (e.key === "Escape") {
                          setShowTagInput(false);
                          setNewTagName("");
                        }
                      }}
                      placeholder="Tag name"
                      className="input-field flex-1 text-body-sm py-2"
                      autoFocus
                    />
                    <button
                      type="button"
                      onClick={handleCreateTag}
                      disabled={!newTagName.trim() || createTagMutation.isPending}
                      className="btn-primary py-2 px-4 text-body-sm"
                    >
                      {createTagMutation.isPending ? (
                        <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                        </svg>
                      ) : (
                        "Add"
                      )}
                    </button>
                    <button
                      type="button"
                      onClick={() => {
                        setShowTagInput(false);
                        setNewTagName("");
                      }}
                      className="btn-ghost py-2 px-3 text-body-sm"
                    >
                      Cancel
                    </button>
                  </div>
                ) : (
                  <button
                    type="button"
                    onClick={() => setShowTagInput(true)}
                    className="inline-flex items-center gap-1.5 text-body-sm text-accent-600 dark:text-accent-400 hover:text-accent-700 dark:hover:text-accent-300 font-medium transition-colors"
                  >
                    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" />
                    </svg>
                    Create new tag
                  </button>
                )}
              </div>
            </div>

            {/* Footer */}
            <div className="flex items-center justify-end gap-3 px-6 py-4 border-t border-neutral-100 dark:border-neutral-800 bg-neutral-50 dark:bg-neutral-800/50">
              <button
                type="button"
                onClick={handleClose}
                className="btn-ghost"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={mutation.isPending}
                className="btn-primary min-w-[120px]"
              >
                {mutation.isPending ? (
                  <span className="flex items-center gap-2">
                    <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                    </svg>
                    Saving...
                  </span>
                ) : mode === "create" ? (
                  "Create Task"
                ) : (
                  "Save Changes"
                )}
              </button>
            </div>
          </form>
        </div>
      </div>
    </>
  );
}
