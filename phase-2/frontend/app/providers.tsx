/**
 * Application Providers - TanStack Query and Auth configuration.
 *
 * Wraps the application with necessary context providers:
 * - QueryClientProvider for TanStack Query (data fetching, caching)
 * - Future: Auth provider for Better Auth session management
 *
 * @see https://tanstack.com/query/latest/docs/framework/react/quick-start
 */

"use client";

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ReactQueryDevtools } from "@tanstack/react-query-devtools";
import { useState, type ReactNode } from "react";

/**
 * Default query client configuration.
 *
 * Optimized for typical API interactions:
 * - staleTime: 60 seconds (data considered fresh for 1 minute)
 * - gcTime: 5 minutes (garbage collect unused data after 5 minutes)
 * - retry: 3 attempts with exponential backoff
 * - refetchOnWindowFocus: true (refresh when user returns to tab)
 */
function makeQueryClient() {
  return new QueryClient({
    defaultOptions: {
      queries: {
        // Data is considered fresh for 60 seconds
        staleTime: 60 * 1000,
        // Keep unused data in cache for 5 minutes
        gcTime: 5 * 60 * 1000,
        // Retry failed requests up to 3 times
        retry: 3,
        // Use exponential backoff for retries
        retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
        // Refetch when window regains focus
        refetchOnWindowFocus: true,
        // Don't refetch on mount if data is fresh
        refetchOnMount: false,
        // Refetch when network reconnects
        refetchOnReconnect: true,
      },
      mutations: {
        // Retry mutations once on failure
        retry: 1,
      },
    },
  });
}

// Browser-side query client singleton
let browserQueryClient: QueryClient | undefined = undefined;

/**
 * Get or create query client.
 *
 * On server: Always create a new client (avoid shared state between requests)
 * On browser: Reuse existing client (singleton pattern)
 */
function getQueryClient() {
  if (typeof window === "undefined") {
    // Server: always create a new QueryClient
    return makeQueryClient();
  }
  // Browser: use singleton
  if (!browserQueryClient) {
    browserQueryClient = makeQueryClient();
  }
  return browserQueryClient;
}

/**
 * Props for Providers component.
 */
interface ProvidersProps {
  children: ReactNode;
}

/**
 * Application providers wrapper.
 *
 * Must be used at the root layout to provide context to all pages.
 *
 * Usage in app/layout.tsx:
 * ```tsx
 * import { Providers } from "./providers";
 *
 * export default function RootLayout({ children }) {
 *   return (
 *     <html>
 *       <body>
 *         <Providers>{children}</Providers>
 *       </body>
 *     </html>
 *   );
 * }
 * ```
 */
export function Providers({ children }: ProvidersProps) {
  // Use useState to ensure client is created once per component lifecycle
  const [queryClient] = useState(getQueryClient);

  return (
    <QueryClientProvider client={queryClient}>
      {children}
      {/* Only show DevTools in development */}
      {process.env.NODE_ENV === "development" && (
        <ReactQueryDevtools initialIsOpen={false} />
      )}
    </QueryClientProvider>
  );
}
