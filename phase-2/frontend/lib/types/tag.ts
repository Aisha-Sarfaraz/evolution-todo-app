/**
 * TypeScript types for Tag entity.
 *
 * Matches backend Tag SQLModel schema from:
 * phase-2/backend/src/models/tag.py
 *
 * @see specs/001-fullstack-todo-web/spec.md - Data Structures
 */

/**
 * Tag entity - full tag representation.
 *
 * Matches TagRead schema from backend.
 */
export interface Tag {
  /** Unique identifier (UUID4) */
  id: string;
  /** Owner user ID (UUID4) */
  user_id: string;
  /** Tag name (1-30 characters, unique per user) */
  name: string;
  /** Optional hex color code (e.g., "#FF5733") */
  color: string | null;
  /** Creation timestamp (ISO 8601) */
  created_at: string;
}

/**
 * Tag creation payload.
 *
 * Matches TagCreate schema from backend.
 */
export interface TagCreate {
  /** Tag name (required, 1-30 characters) */
  name: string;
  /** Optional hex color code */
  color?: string | null;
}

/**
 * Tag update payload.
 *
 * Matches TagUpdate schema from backend.
 * All fields are optional - only provided fields are updated.
 */
export interface TagUpdate {
  /** Updated name */
  name?: string;
  /** Updated color */
  color?: string | null;
}

/**
 * Tag list response.
 */
export interface TagListResponse {
  /** List of tags */
  tags: Tag[];
  /** Total count */
  total: number;
}

/**
 * Tag with task count.
 *
 * Used for displaying tags with usage statistics.
 */
export interface TagWithCount extends Tag {
  /** Number of tasks with this tag */
  task_count: number;
}

/**
 * Task-Tag association.
 *
 * Matches TaskTagRead schema from backend.
 */
export interface TaskTag {
  /** Task ID (UUID4) */
  task_id: string;
  /** Tag ID (UUID4) */
  tag_id: string;
  /** Association creation timestamp (ISO 8601) */
  created_at: string;
}

/**
 * Bulk tag assignment payload.
 */
export interface BulkTagAssignment {
  /** List of tag IDs to assign */
  tag_ids: string[];
}
