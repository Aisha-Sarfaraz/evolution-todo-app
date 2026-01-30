/**
 * Better Auth server configuration.
 *
 * This configures Better Auth with:
 * - PostgreSQL database (Neon)
 * - Email/password authentication
 * - JWT plugin for token issuance via /api/auth/token and JWKS via /api/auth/jwks
 *
 * @see https://better-auth.com/docs/installation
 * @see https://better-auth.com/docs/plugins/jwt
 */

import { betterAuth } from "better-auth";
import { jwt } from "better-auth/plugins";
import { Pool, neonConfig } from "@neondatabase/serverless";
import ws from "ws";

// Enable WebSocket for Neon serverless in Node.js environments (Vercel)
neonConfig.webSocketConstructor = ws;

/**
 * Better Auth server instance.
 *
 * Configured with:
 * - PostgreSQL connection via pg.Pool
 * - Email/password authentication enabled
 * - JWT plugin for token issuance and JWKS endpoint
 *
 * Endpoints exposed:
 * - POST /api/auth/sign-up/email
 * - POST /api/auth/sign-in/email
 * - POST /api/auth/sign-out
 * - GET /api/auth/session
 * - GET /api/auth/token (JWT token retrieval)
 * - GET /api/auth/jwks (JWKS public keys for verification)
 */
export const auth = betterAuth({
  baseURL: process.env["BETTER_AUTH_URL"] || "http://localhost:3000",
  secret: process.env["BETTER_AUTH_SECRET"],

  database: new Pool({
    connectionString: process.env["DATABASE_URL"],
  }),

  emailAndPassword: {
    enabled: true,
    // Disabled until SMTP is configured for email delivery
    requireEmailVerification: false,
  },

  session: {
    expiresIn: 60 * 60, // 1 hour in seconds
    updateAge: 60 * 15, // 15 minutes - update session if older
  },

  plugins: [
    jwt({
      // JWT tokens will be signed with asymmetric keys
      // JWKS endpoint will expose public keys at /api/auth/jwks
    }),
  ],

  // Advanced security configuration
  advanced: {
    cookiePrefix: "better-auth",
    useSecureCookies: process.env.NODE_ENV === "production",
    crossSubDomainCookies: {
      enabled: false,
    },
    // Explicit CSRF protection (enabled by default, but explicit is better)
    disableCSRFCheck: false,
  },

  // Trusted origins for CORS and CSRF validation
  trustedOrigins: [
    process.env["BETTER_AUTH_URL"] || "http://localhost:3000",
    process.env["NEXT_PUBLIC_API_URL"] || "http://localhost:8000",
  ],
});

export type Session = typeof auth.$Infer.Session;
export type User = typeof auth.$Infer.Session.user;
