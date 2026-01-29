/**
 * Better Auth API route handler for Next.js App Router.
 *
 * Mounts Better Auth handlers at /api/auth/[...all] to handle:
 * - Authentication (sign-up, sign-in, sign-out)
 * - Session management
 * - JWT token issuance (/api/auth/token)
 * - JWKS public keys (/api/auth/jwks)
 *
 * @see https://better-auth.com/docs/integrations/next
 */

import { auth } from "@/lib/auth/auth";
import { toNextJsHandler } from "better-auth/next-js";

export const { GET, POST } = toNextJsHandler(auth);
