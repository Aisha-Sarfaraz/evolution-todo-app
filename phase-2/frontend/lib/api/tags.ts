/**
 * Tag API methods.
 *
 * T111: [US5] Tag CRUD operations using apiClient wrapper.
 */

import { api } from "./client";
import { getCurrentUserId } from "./auth-helpers";

export interface Tag {
  id: string;
  name: string;
  user_id: string;
  created_at: string;
}

export interface TagCreate {
  name: string;
}

export interface TagUpdate {
  name: string;
}

interface TagListResponse {
  tags: Tag[];
  total: number;
}

/**
 * Get all tags for the current user.
 * Returns tags sorted alphabetically.
 */
export async function getTags(): Promise<Tag[]> {
  const userId = await getCurrentUserId();
  const { data, error } = await api.get<TagListResponse>(`/${userId}/tags`);

  if (error) {
    throw new Error(error.detail || "Failed to fetch tags");
  }

  return data.tags;
}

/**
 * Create a new tag.
 */
export async function createTag(tagData: TagCreate): Promise<Tag> {
  const userId = await getCurrentUserId();
  const { data, error } = await api.post<Tag>(`/${userId}/tags`, tagData);

  if (error) {
    throw new Error(error.detail || "Failed to create tag");
  }

  return data;
}

/**
 * Rename a tag.
 */
export async function updateTag(tagId: string, tagData: TagUpdate): Promise<Tag> {
  const userId = await getCurrentUserId();
  const { data, error } = await api.put<Tag>(`/${userId}/tags/${tagId}`, tagData);

  if (error) {
    throw new Error(error.detail || "Failed to update tag");
  }

  return data;
}

/**
 * Delete a tag.
 * Associated TaskTag entries will be removed via cascade.
 */
export async function deleteTag(tagId: string): Promise<void> {
  const userId = await getCurrentUserId();
  const { error } = await api.delete(`/${userId}/tags/${tagId}`);

  if (error) {
    throw new Error(error.detail || "Failed to delete tag");
  }
}
