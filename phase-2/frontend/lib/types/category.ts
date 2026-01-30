/**
 * TypeScript types for Category entity.
 *
 * Matches backend Category SQLModel schema from:
 * phase-2/backend/src/models/category.py
 *
 * @see specs/001-fullstack-todo-web/spec.md - Data Structures
 */

/**
 * Category entity - full category representation.
 *
 * Matches CategoryRead schema from backend.
 */
export interface Category {
  /** Unique identifier (UUID4) */
  id: string;
  /** Owner user ID (UUID4, null for system categories) */
  user_id: string | null;
  /** Category name (1-50 characters, unique per user) */
  name: string;
  /** Optional hex color code (e.g., "#FF5733") */
  color: string | null;
  /** Whether this is a system-defined category */
  is_system: boolean;
  /** Creation timestamp (ISO 8601) */
  created_at: string;
}

/**
 * Category creation payload.
 *
 * Matches CategoryCreate schema from backend.
 */
export interface CategoryCreate {
  /** Category name (required, 1-50 characters) */
  name: string;
  /** Optional hex color code */
  color?: string | null;
}

/**
 * Category update payload.
 *
 * Matches CategoryUpdate schema from backend.
 * All fields are optional - only provided fields are updated.
 */
export interface CategoryUpdate {
  /** Updated name */
  name?: string;
  /** Updated color */
  color?: string | null;
}

/**
 * System category names (pre-seeded, read-only).
 */
export const SYSTEM_CATEGORIES = [
  "Work",
  "Personal",
  "Shopping",
  "Health",
  "Finance",
] as const;

export type SystemCategoryName = (typeof SYSTEM_CATEGORIES)[number];

/**
 * Category list response.
 */
export interface CategoryListResponse {
  /** List of categories */
  categories: Category[];
  /** Total count */
  total: number;
}

/**
 * Category with task count.
 *
 * Used for displaying categories with usage statistics.
 */
export interface CategoryWithCount extends Category {
  /** Number of tasks in this category */
  task_count: number;
}
