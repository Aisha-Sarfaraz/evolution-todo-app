/**
 * TypeScript types for Task entity.
 *
 * Matches backend Task SQLModel schema from:
 * phase-2/backend/src/models/task.py
 *
 * @see specs/001-fullstack-todo-web/spec.md - Data Structures
 */

/**
 * Task status enum - matches backend TaskStatus.
 */
export type TaskStatus = "pending" | "complete";

/**
 * Task priority enum - matches backend TaskPriority.
 */
export type TaskPriority = "Low" | "Medium" | "High" | "Urgent";

/**
 * Task entity - full task representation.
 *
 * Matches TaskRead schema from backend.
 */
export interface Task {
  /** Unique identifier (UUID4) */
  id: string;
  /** Owner user ID (UUID4) */
  user_id: string;
  /** Task title (1-200 characters) */
  title: string;
  /** Task description (0-2000 characters, nullable) */
  description: string | null;
  /** Task status: pending or complete */
  status: TaskStatus;
  /** Task priority: Low, Medium, High, or Urgent */
  priority: TaskPriority;
  /** Optional category ID (UUID4) */
  category_id: string | null;
  /** Creation timestamp (ISO 8601) */
  created_at: string;
  /** Last modification timestamp (ISO 8601) */
  updated_at: string;
  /** Completion timestamp (ISO 8601, nullable) */
  completed_at: string | null;
}

/**
 * Task creation payload.
 *
 * Matches TaskCreate schema from backend.
 */
export interface TaskCreate {
  /** Task title (required, 1-200 characters) */
  title: string;
  /** Task description (optional, max 2000 characters) */
  description?: string | null;
  /** Task priority (default: Medium) */
  priority?: TaskPriority;
  /** Category ID to assign (optional) */
  category_id?: string | null;
  /** Tag IDs to assign (optional) */
  tag_ids?: string[];
}

/**
 * Task update payload.
 *
 * Matches TaskUpdate schema from backend.
 * All fields are optional - only provided fields are updated.
 */
export interface TaskUpdate {
  /** Updated title */
  title?: string;
  /** Updated description */
  description?: string | null;
  /** Updated priority */
  priority?: TaskPriority;
  /** Updated category ID */
  category_id?: string | null;
  /** Updated tag IDs */
  tag_ids?: string[];
}

/**
 * Task completion toggle payload.
 *
 * Matches TaskComplete schema from backend.
 */
export interface TaskComplete {
  /** New status (pending or complete) */
  status: TaskStatus;
}

/**
 * Task list response from backend.
 */
export interface TaskListResponse {
  /** List of tasks */
  tasks: Task[];
  /** Total count of tasks matching filters */
  total: number;
}

/**
 * Task filter parameters for list endpoint.
 *
 * T131-T134: Enhanced filters for task discovery.
 * Note: Using explicit `| undefined` for exactOptionalPropertyTypes compatibility.
 */
export interface TaskFilters {
  /** Filter by status (pending, complete, all) */
  status?: TaskStatus | "all" | undefined;
  /** Filter by priority (comma-separated for multiple) */
  priority?: string | undefined;
  /** Filter by category ID */
  category?: string | undefined;
  /** Filter by tag IDs (comma-separated, AND logic) */
  tags?: string | undefined;
  /** Search query for title/description */
  search?: string | undefined;
  /** Filter tasks created after this date (ISO 8601) */
  created_after?: string | undefined;
  /** Filter tasks created before this date (ISO 8601) */
  created_before?: string | undefined;
  /** Filter tasks updated after this date (ISO 8601) */
  updated_after?: string | undefined;
  /** Filter tasks updated before this date (ISO 8601) */
  updated_before?: string | undefined;
  /** Sort field */
  sort_by?: "created_at" | "updated_at" | "title" | "priority" | undefined;
  /** Sort direction */
  order?: "asc" | "desc" | undefined;
  /** Maximum results per page */
  limit?: number | undefined;
  /** Number of results to skip */
  offset?: number | undefined;
}

/**
 * Task with expanded relationships.
 *
 * Used when fetching task with category and tags loaded.
 */
export interface TaskWithRelations extends Task {
  /** Expanded category object */
  category?: {
    id: string;
    name: string;
    color: string | null;
  } | null;
  /** List of associated tags */
  tags?: Array<{
    id: string;
    name: string;
    color: string | null;
  }>;
}
