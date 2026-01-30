/**
 * Auth helpers for API calls.
 *
 * Provides user ID extraction from Better Auth session.
 */

import { authClient } from "@/lib/auth/better-auth";

/**
 * Get current user ID from Better Auth session.
 *
 * @returns User ID from authenticated session
 * @throws Error if not authenticated
 */
export async function getCurrentUserId(): Promise<string> {
  const session = await authClient.getSession();

  if (!session.data?.user?.id) {
    throw new Error("Not authenticated");
  }

  return session.data.user.id;
}
