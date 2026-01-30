/**
 * Category API methods.
 *
 * T110: [US5] Category CRUD operations using apiClient wrapper.
 */

import { api } from "./client";
import { getCurrentUserId } from "./auth-helpers";

export interface Category {
  id: string;
  name: string;
  user_id: string | null;
  is_system: boolean;
  created_at: string;
}

export interface CategoryCreate {
  name: string;
}

interface CategoryListResponse {
  categories: Category[];
  total: number;
}

/**
 * Get all categories for the current user.
 * Includes system categories and user's custom categories.
 */
export async function getCategories(): Promise<Category[]> {
  const userId = await getCurrentUserId();
  const { data, error } = await api.get<CategoryListResponse>(`/${userId}/categories`);

  if (error) {
    throw new Error(error.detail || "Failed to fetch categories");
  }

  return data.categories;
}

/**
 * Create a new custom category.
 */
export async function createCategory(categoryData: CategoryCreate): Promise<Category> {
  const userId = await getCurrentUserId();
  const { data, error } = await api.post<Category>(`/${userId}/categories`, categoryData);

  if (error) {
    throw new Error(error.detail || "Failed to create category");
  }

  return data;
}

/**
 * Delete a custom category.
 * System categories cannot be deleted.
 */
export async function deleteCategory(categoryId: string): Promise<void> {
  const userId = await getCurrentUserId();
  const { error } = await api.delete(`/${userId}/categories/${categoryId}`);

  if (error) {
    throw new Error(error.detail || "Failed to delete category");
  }
}
