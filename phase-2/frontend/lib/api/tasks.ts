/**
 * Task API methods.
 *
 * T077: [US2] Implement task API methods
 * CRUD operations using apiClient wrapper.
 */

import { api } from "./client";
import { getCurrentUserId } from "./auth-helpers";
import type { Task, TaskCreate, TaskUpdate, TaskListResponse, TaskFilters } from "@/lib/types/task";

/**
 * Get all tasks for the current user.
 *
 * T123-T130: Enhanced with search, filter, sort support.
 *
 * @param filters - Optional filter parameters
 */
export async function getTasks(filters?: TaskFilters): Promise<TaskListResponse> {
  const userId = await getCurrentUserId();

  // Build query string from filters
  const params = new URLSearchParams();
  if (filters) {
    if (filters.search) params.set("search", filters.search);
    if (filters.status && filters.status !== "all") params.set("status", filters.status);
    if (filters.priority) params.set("priority", filters.priority);
    if (filters.category) params.set("category", filters.category);
    if (filters.tags) params.set("tags", filters.tags);
    if (filters.created_after) params.set("created_after", filters.created_after);
    if (filters.created_before) params.set("created_before", filters.created_before);
    if (filters.updated_after) params.set("updated_after", filters.updated_after);
    if (filters.updated_before) params.set("updated_before", filters.updated_before);
    if (filters.sort_by) params.set("sort_by", filters.sort_by);
    if (filters.order) params.set("order", filters.order);
    if (filters.limit) params.set("limit", String(filters.limit));
    if (filters.offset) params.set("offset", String(filters.offset));
  }

  const queryString = params.toString();
  const url = `/${userId}/tasks${queryString ? `?${queryString}` : ""}`;

  const { data, error } = await api.get<TaskListResponse>(url);

  if (error) {
    throw new Error(error.detail || "Failed to fetch tasks");
  }

  return data;
}

/**
 * Get a single task by ID.
 */
export async function getTask(taskId: string): Promise<Task> {
  const userId = await getCurrentUserId();
  const { data, error } = await api.get<Task>(`/${userId}/tasks/${taskId}`);

  if (error) {
    throw new Error(error.detail || "Failed to fetch task");
  }

  return data;
}

/**
 * Create a new task.
 */
export async function createTask(taskData: TaskCreate): Promise<Task> {
  const userId = await getCurrentUserId();
  const { data, error } = await api.post<Task>(`/${userId}/tasks`, taskData);

  if (error) {
    throw new Error(error.detail || "Failed to create task");
  }

  return data;
}

/**
 * Update an existing task.
 */
export async function updateTask(taskId: string, taskData: TaskUpdate): Promise<Task> {
  const userId = await getCurrentUserId();
  const { data, error } = await api.put<Task>(`/${userId}/tasks/${taskId}`, taskData);

  if (error) {
    throw new Error(error.detail || "Failed to update task");
  }

  return data;
}

/**
 * Delete a task.
 */
export async function deleteTask(taskId: string): Promise<void> {
  const userId = await getCurrentUserId();
  const { error } = await api.delete(`/${userId}/tasks/${taskId}`);

  if (error) {
    throw new Error(error.detail || "Failed to delete task");
  }
}

/**
 * Toggle task completion status.
 */
export async function toggleComplete(taskId: string): Promise<Task> {
  const userId = await getCurrentUserId();
  const { data, error } = await api.patch<Task>(`/${userId}/tasks/${taskId}/complete`, {});

  if (error) {
    throw new Error(error.detail || "Failed to toggle task completion");
  }

  return data;
}
