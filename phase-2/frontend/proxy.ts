/**
 * Next.js 16 Authentication Proxy for Protected Routes.
 *
 * Implements route protection using Next.js 16 proxy pattern:
 * - Validates session cookie on protected routes
 * - Redirects unauthenticated users to signin page
 * - Redirects authenticated users away from auth pages to dashboard
 *
 * @see https://github.com/vercel/next.js/blob/v16.1.1/docs/01-app/02-guides/authentication.mdx
 * @see specs/001-fullstack-todo-web/spec.md - FR-007
 */

import { NextRequest, NextResponse } from "next/server";
import { getSessionCookie } from "better-auth/cookies";

/**
 * Protected routes requiring authentication.
 * Users without valid session are redirected to /signin.
 */
const protectedRoutes = [
  "/dashboard",
  "/tasks",
  "/categories",
  "/tags",
  "/profile",
];

/**
 * Public routes accessible without authentication.
 * Authenticated users are redirected to /tasks.
 */
const publicRoutes = ["/", "/signin", "/signup", "/verify-email", "/reset-password"];

/**
 * Auth callback routes that should be accessible regardless of auth state.
 */
const authCallbackRoutes = ["/api/auth"];

/**
 * Check if path matches any protected route.
 */
function isProtectedRoute(path: string): boolean {
  return protectedRoutes.some(
    (route) => path === route || path.startsWith(`${route}/`)
  );
}

/**
 * Check if path matches any public route.
 */
function isPublicRoute(path: string): boolean {
  return publicRoutes.some(
    (route) => path === route || (route !== "/" && path.startsWith(`${route}/`))
  );
}

/**
 * Check if path is an auth callback route.
 */
function isAuthCallbackRoute(path: string): boolean {
  return authCallbackRoutes.some((route) => path.startsWith(route));
}

/**
 * Next.js 16 Proxy function for authentication.
 *
 * Executes on every request matching the config matcher.
 * Uses Better Auth session cookie for authentication validation.
 *
 * @param request - Next.js request object
 * @returns NextResponse with redirect or continuation
 *
 * Behavior:
 * - Protected route without session → Redirect to /signin
 * - Public route (signin/signup) with session → Redirect to /tasks
 * - All other routes → Continue to next handler
 */
export default async function proxy(request: NextRequest) {
  const path = request.nextUrl.pathname;

  // Skip auth callback routes (Better Auth handles these)
  if (isAuthCallbackRoute(path)) {
    return NextResponse.next();
  }

  // Get session cookie using Better Auth helper
  const sessionCookie = getSessionCookie(request);
  const isAuthenticated = !!sessionCookie;

  // Redirect unauthenticated users from protected routes to signin
  if (isProtectedRoute(path) && !isAuthenticated) {
    const signinUrl = new URL("/signin", request.url);
    // Preserve the original URL for redirect after signin
    signinUrl.searchParams.set("callbackUrl", path);
    return NextResponse.redirect(signinUrl);
  }

  // Redirect authenticated users from auth pages to dashboard
  if (isPublicRoute(path) && isAuthenticated && path !== "/") {
    // Allow authenticated users to stay on homepage
    // But redirect away from signin/signup pages
    if (["/signin", "/signup"].includes(path)) {
      return NextResponse.redirect(new URL("/tasks", request.url));
    }
  }

  return NextResponse.next();
}

/**
 * Matcher configuration - routes the proxy should run on.
 *
 * Excludes:
 * - API routes (handled by API route handlers)
 * - Static files (_next/static, _next/image)
 * - Image files (png, jpg, jpeg, gif, svg, ico)
 * - Public assets (favicon, robots.txt)
 */
export const config = {
  matcher: [
    /*
     * Match all request paths except for:
     * - api (API routes)
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico, sitemap.xml, robots.txt (metadata files)
     * - Image files (png, jpg, etc.)
     */
    "/((?!api|_next/static|_next/image|favicon.ico|sitemap.xml|robots.txt|.*\\.png$|.*\\.jpg$|.*\\.jpeg$|.*\\.gif$|.*\\.svg$|.*\\.ico$).*)",
  ],
};
