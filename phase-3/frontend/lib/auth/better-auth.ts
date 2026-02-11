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

export const authClient = createAuthClient({
  baseURL: process.env["NEXT_PUBLIC_AUTH_URL"] || "http://localhost:3000",
  plugins: [jwtClient()],
});

export const useSession = authClient.useSession;

export async function signUp(email: string, password: string, name: string) {
  return authClient.signUp.email({ email, password, name });
}

export async function signIn(email: string, password: string) {
  return authClient.signIn.email({ email, password });
}

export async function signOut() {
  return authClient.signOut();
}

export async function getSession() {
  return authClient.getSession();
}
