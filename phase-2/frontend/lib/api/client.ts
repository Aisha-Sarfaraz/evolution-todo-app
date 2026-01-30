/**
 * Centralized API client with JWT token injection and automatic refresh.
 *
 * T028: API client wrapper
 * T090: CSRF token handling
 *
 * Features:
 * - Automatic Authorization header injection
 * - Token refresh on 401 Unauthorized
 * - CSRF token handling for state-changing requests
 * - Typed error responses
 * - TypeScript generics for type-safe responses
 *
 * @see specs/001-fullstack-todo-web/spec.md - FR-064, FR-065
 */

import { authClient } from "@/lib/auth/better-auth";

/**
 * CSRF token cookie name.
 */
const CSRF_COOKIE_NAME = "csrf_token";

/**
 * CSRF header name.
 */
const CSRF_HEADER_NAME = "X-CSRF-Token";

/**
 * API base URL from environment or default to localhost.
 */
const API_BASE_URL = process.env["NEXT_PUBLIC_API_URL"] || "http://localhost:8000/api";

/**
 * Standard error response from API.
 */
export interface ApiError {
  error_code: string;
  detail: string;
  field?: string;
}

/**
 * Validation error response with multiple field errors.
 */
export interface ValidationError {
  error_code: "VALIDATION_ERROR";
  detail: string;
  errors: Array<{
    field: string;
    message: string;
    value?: unknown;
  }>;
}

/**
 * API response wrapper with data or error.
 */
export type ApiResponse<T> =
  | { data: T; error: null }
  | { data: null; error: ApiError | ValidationError };

/**
 * HTTP methods supported by the API client.
 */
type HttpMethod = "GET" | "POST" | "PUT" | "PATCH" | "DELETE";

/**
 * Request options for API calls.
 */
interface RequestOptions<TBody = unknown> {
  method?: HttpMethod;
  body?: TBody;
  headers?: Record<string, string>;
  skipAuth?: boolean;
}

/**
 * Flag to prevent concurrent token refreshes.
 */
let isRefreshing = false;

/**
 * In-memory JWT cache to avoid repeated /api/auth/token calls.
 */
let cachedJwt: string | null = null;
let cachedJwtExpiry: number = 0;

/**
 * JWT cache TTL in milliseconds (50 minutes - tokens expire in 60 min).
 */
const JWT_CACHE_TTL = 50 * 60 * 1000;

/**
 * Read CSRF token from cookie.
 *
 * @returns CSRF token string or null if not found
 */
function getCsrfToken(): string | null {
  if (typeof document === "undefined") {
    // Server-side rendering - no cookies available
    return null;
  }

  const cookies = document.cookie.split(";");
  for (const cookie of cookies) {
    const [name, value] = cookie.trim().split("=");
    if (name === CSRF_COOKIE_NAME && value) {
      return decodeURIComponent(value);
    }
  }
  return null;
}

/**
 * Check if request method requires CSRF protection.
 */
function requiresCsrf(method: HttpMethod): boolean {
  // State-changing methods require CSRF token
  return ["POST", "PUT", "PATCH", "DELETE"].includes(method);
}

/**
 * Queue of requests waiting for token refresh.
 */
let refreshSubscribers: Array<(token: string) => void> = [];

/**
 * Subscribe to token refresh completion.
 */
function subscribeToTokenRefresh(callback: (token: string) => void) {
  refreshSubscribers.push(callback);
}

/**
 * Notify all subscribers that token refresh is complete.
 */
function onTokenRefreshed(token: string) {
  refreshSubscribers.forEach((callback) => callback(token));
  refreshSubscribers = [];
}

/**
 * Get JWT access token from Better Auth's /api/auth/token endpoint.
 * Caches the token in memory to avoid repeated network calls.
 *
 * @returns JWT token string or null if not authenticated
 */
async function getAccessToken(): Promise<string | null> {
  // Return cached token if still valid
  if (cachedJwt && Date.now() < cachedJwtExpiry) {
    return cachedJwt;
  }

  try {
    // Use Better Auth's JWT client plugin to get a JWT token
    const result = await (authClient as any).token();
    if (result?.error || !result?.data?.token) {
      cachedJwt = null;
      cachedJwtExpiry = 0;
      return null;
    }
    cachedJwt = result.data.token;
    cachedJwtExpiry = Date.now() + JWT_CACHE_TTL;
    return cachedJwt;
  } catch {
    cachedJwt = null;
    cachedJwtExpiry = 0;
    return null;
  }
}

/**
 * Attempt to refresh the access token by fetching a new JWT.
 *
 * @returns New access token or null if refresh failed
 */
async function refreshToken(): Promise<string | null> {
  // Invalidate cache to force a fresh JWT
  cachedJwt = null;
  cachedJwtExpiry = 0;
  return getAccessToken();
}

/**
 * Parse error response from API.
 *
 * @param response - Fetch Response object
 * @returns Parsed error object
 */
async function parseError(response: Response): Promise<ApiError | ValidationError> {
  try {
    const errorData = await response.json();

    // Check if it's a structured error response
    if (errorData.error_code) {
      return errorData as ApiError | ValidationError;
    }

    // Fallback for unstructured errors
    return {
      error_code: "UNKNOWN_ERROR",
      detail: errorData.detail || errorData.message || "An unknown error occurred",
    };
  } catch {
    // JSON parsing failed
    return {
      error_code: "PARSE_ERROR",
      detail: `Request failed with status ${response.status}`,
    };
  }
}

/**
 * Make an API request with automatic auth and error handling.
 *
 * @param endpoint - API endpoint path (e.g., "/users/123/tasks")
 * @param options - Request options
 * @returns API response with typed data or error
 *
 * @example
 * ```typescript
 * // GET request
 * const { data, error } = await apiClient<Task[]>("/users/123/tasks");
 *
 * // POST request
 * const { data, error } = await apiClient<Task>("/users/123/tasks", {
 *   method: "POST",
 *   body: { title: "New Task", description: "Description" }
 * });
 *
 * // Handle response
 * if (error) {
 *   console.error(error.detail);
 * } else {
 *   console.log(data);
 * }
 * ```
 */
export async function apiClient<T, TBody = unknown>(
  endpoint: string,
  options: RequestOptions<TBody> = {}
): Promise<ApiResponse<T>> {
  const { method = "GET", body, headers = {}, skipAuth = false } = options;

  // Build full URL
  const url = endpoint.startsWith("http") ? endpoint : `${API_BASE_URL}${endpoint}`;

  // Build headers
  const requestHeaders: Record<string, string> = {
    "Content-Type": "application/json",
    ...headers,
  };

  // Add Authorization header if authenticated
  if (!skipAuth) {
    const token = await getAccessToken();
    if (token) {
      requestHeaders["Authorization"] = `Bearer ${token}`;
    }
  }

  // Add CSRF token for state-changing requests
  if (requiresCsrf(method)) {
    const csrfToken = getCsrfToken();
    if (csrfToken) {
      requestHeaders[CSRF_HEADER_NAME] = csrfToken;
    }
  }

  // Build request options
  const fetchOptions: RequestInit = {
    method,
    headers: requestHeaders,
    credentials: "include", // Include cookies for CSRF
  };

  // Add body for non-GET requests
  if (body && method !== "GET") {
    fetchOptions.body = JSON.stringify(body);
  }

  try {
    let response = await fetch(url, fetchOptions);

    // Handle 401 Unauthorized - attempt token refresh
    if (response.status === 401 && !skipAuth) {
      // Check if we're already refreshing
      if (!isRefreshing) {
        isRefreshing = true;

        const newToken = await refreshToken();

        isRefreshing = false;

        if (newToken) {
          onTokenRefreshed(newToken);

          // Retry original request with new token
          requestHeaders["Authorization"] = `Bearer ${newToken}`;
          response = await fetch(url, {
            ...fetchOptions,
            headers: requestHeaders,
          });
        } else {
          // Refresh failed - user needs to sign in again
          return {
            data: null,
            error: {
              error_code: "SESSION_EXPIRED",
              detail: "Your session has expired. Please sign in again.",
            },
          };
        }
      } else {
        // Wait for ongoing refresh to complete
        return new Promise((resolve) => {
          subscribeToTokenRefresh(async (token) => {
            requestHeaders["Authorization"] = `Bearer ${token}`;
            const retryResponse = await fetch(url, {
              ...fetchOptions,
              headers: requestHeaders,
            });

            if (!retryResponse.ok) {
              resolve({
                data: null,
                error: await parseError(retryResponse),
              });
            } else {
              resolve({
                data: (await retryResponse.json()) as T,
                error: null,
              });
            }
          });
        });
      }
    }

    // Handle error responses
    if (!response.ok) {
      return {
        data: null,
        error: await parseError(response),
      };
    }

    // Handle 204 No Content
    if (response.status === 204) {
      return {
        data: undefined as T,
        error: null,
      };
    }

    // Parse successful response
    const data = (await response.json()) as T;
    return {
      data,
      error: null,
    };
  } catch (err) {
    // Network error or other exception
    return {
      data: null,
      error: {
        error_code: "NETWORK_ERROR",
        detail: err instanceof Error ? err.message : "Network request failed",
      },
    };
  }
}

/**
 * Convenience methods for common HTTP operations.
 */
export const api = {
  /**
   * GET request.
   */
  get: <T>(endpoint: string, options?: Omit<RequestOptions, "method" | "body">) =>
    apiClient<T>(endpoint, { ...options, method: "GET" }),

  /**
   * POST request.
   */
  post: <T, TBody = unknown>(endpoint: string, body: TBody, options?: Omit<RequestOptions<TBody>, "method" | "body">) =>
    apiClient<T, TBody>(endpoint, { ...options, method: "POST", body }),

  /**
   * PUT request.
   */
  put: <T, TBody = unknown>(endpoint: string, body: TBody, options?: Omit<RequestOptions<TBody>, "method" | "body">) =>
    apiClient<T, TBody>(endpoint, { ...options, method: "PUT", body }),

  /**
   * PATCH request.
   */
  patch: <T, TBody = unknown>(endpoint: string, body: TBody, options?: Omit<RequestOptions<TBody>, "method" | "body">) =>
    apiClient<T, TBody>(endpoint, { ...options, method: "PATCH", body }),

  /**
   * DELETE request.
   */
  delete: <T>(endpoint: string, options?: Omit<RequestOptions, "method" | "body">) =>
    apiClient<T>(endpoint, { ...options, method: "DELETE" }),
};
