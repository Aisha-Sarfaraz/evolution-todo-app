/**
 * T045: Auth session management module.
 *
 * Extends Phase II Better Auth for Phase III chat authentication.
 */

const AUTH_URL = process.env.NEXT_PUBLIC_AUTH_URL || "http://localhost:3000";

interface AuthSession {
  token: string;
  userId: string;
  email?: string;
}

/**
 * Get the current auth session from Better Auth.
 */
export async function getSession(): Promise<AuthSession | null> {
  try {
    const response = await fetch(`${AUTH_URL}/api/auth/get-session`, {
      credentials: "include",
    });

    if (!response.ok) return null;

    const data = await response.json();

    if (!data?.session?.token) return null;

    return {
      token: data.session.token,
      userId: data.user?.id || data.session?.userId,
      email: data.user?.email,
    };
  } catch {
    return null;
  }
}

/**
 * Check if user is authenticated.
 */
export async function isAuthenticated(): Promise<boolean> {
  const session = await getSession();
  return session !== null;
}

/**
 * Get the auth token for API calls.
 */
export async function getAuthToken(): Promise<string | null> {
  const session = await getSession();
  return session?.token || null;
}
