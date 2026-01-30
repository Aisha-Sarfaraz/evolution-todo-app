/**
 * Better Auth client configuration for Next.js App Router.
 *
 * Provides client-side authentication functions for:
 * - Email/password signin/signup
 * - Session management
 * - Token refresh
 * - Profile management
 *
 * @see https://better-auth.com/docs/integrations/next
 */

import { createAuthClient } from "better-auth/react";
import { jwtClient } from "better-auth/client/plugins";

/**
 * Better Auth client instance.
 *
 * Configured for email/password authentication with:
 * - Base URL from environment variable
 * - CSRF protection enabled
 * - Session cookie management
 *
 * Usage:
 * ```tsx
 * import { authClient } from "@/lib/auth/better-auth";
 *
 * // Sign up
 * const { data, error } = await authClient.signUp.email({
 *   email: "user@example.com",
 *   password: "SecurePass123!",
 *   name: "User Name"
 * });
 *
 * // Sign in
 * const { data, error } = await authClient.signIn.email({
 *   email: "user@example.com",
 *   password: "SecurePass123!"
 * });
 *
 * // Get session
 * const session = await authClient.getSession();
 *
 * // Sign out
 * await authClient.signOut();
 * ```
 */
export const authClient = createAuthClient({
  baseURL: process.env["NEXT_PUBLIC_AUTH_URL"] || "http://localhost:3000",
  plugins: [jwtClient()],
});

/**
 * Hook for accessing current session in React components.
 *
 * Usage:
 * ```tsx
 * function ProfilePage() {
 *   const { data: session, isPending, error } = useSession();
 *
 *   if (isPending) return <Loading />;
 *   if (error) return <Error message={error.message} />;
 *   if (!session) return <Redirect to="/signin" />;
 *
 *   return <Profile user={session.user} />;
 * }
 * ```
 */
export const useSession = authClient.useSession;

/**
 * Sign up with email and password.
 *
 * @param email - User's email address
 * @param password - User's password (min 8 chars, 1 uppercase, 1 number)
 * @param name - User's display name
 *
 * @returns Promise resolving to session data or error
 */
export async function signUp(email: string, password: string, name: string) {
  return authClient.signUp.email({
    email,
    password,
    name,
  });
}

/**
 * Sign in with email and password.
 *
 * @param email - User's email address
 * @param password - User's password
 *
 * @returns Promise resolving to session data or error
 */
export async function signIn(email: string, password: string) {
  return authClient.signIn.email({
    email,
    password,
  });
}

/**
 * Sign out current user.
 *
 * Clears session cookies and invalidates tokens.
 */
export async function signOut() {
  return authClient.signOut();
}

/**
 * Get current session.
 *
 * @returns Current session with user data or null if not authenticated
 */
export async function getSession() {
  return authClient.getSession();
}

/**
 * Request password reset email.
 *
 * @param email - User's email address
 *
 * @returns Promise resolving when email is sent
 */
export async function requestPasswordReset(email: string) {
  // Better Auth v1.4.14 uses forgetPassword to request reset email
  // @ts-ignore - Type definitions may be outdated
  return authClient.forgetPassword({
    email,
    redirectTo: `${process.env["NEXT_PUBLIC_APP_URL"]}/reset-password`,
  });
}

/**
 * Reset password with token.
 *
 * @param token - Password reset token from email
 * @param newPassword - New password
 *
 * @returns Promise resolving when password is reset
 */
export async function resetPassword(token: string, newPassword: string) {
  return authClient.resetPassword({
    token,
    newPassword,
  });
}

/**
 * Type exports for Better Auth session and user.
 */
export type Session = Awaited<ReturnType<typeof authClient.getSession>>;
export type User = NonNullable<Session>["user"];
