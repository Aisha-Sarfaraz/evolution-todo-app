/**
 * Verify email page with Flowspace styling.
 *
 * T051: [US1] Create verify-email page
 * Server component that extracts token from URL and calls verify endpoint.
 */

import { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "Verify Email",
  description: "Verify your email address to complete your Flowspace registration",
};

interface VerifyEmailPageProps {
  searchParams: Promise<{ token?: string }>;
}

async function verifyEmail(token: string): Promise<{ success: boolean; message: string }> {
  try {
    const response = await fetch(
      `${process.env["NEXT_PUBLIC_API_URL"] ?? "http://localhost:8000"}/api/auth/verify-email`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ token }),
      }
    );

    const data = await response.json();

    if (response.ok) {
      return { success: true, message: data.message || "Email verified successfully!" };
    }

    return { success: false, message: data.detail?.detail || "Verification failed" };
  } catch {
    return { success: false, message: "An error occurred during verification" };
  }
}

export default async function VerifyEmailPage({ searchParams }: VerifyEmailPageProps) {
  const { token } = await searchParams;

  // If no token provided, show instructions
  if (!token) {
    return (
      <div className="space-y-8 text-center">
        {/* Icon */}
        <div className="flex justify-center">
          <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-accent-500 to-accent-600 flex items-center justify-center shadow-lg shadow-accent-500/30">
            <svg className="w-10 h-10 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
            </svg>
          </div>
        </div>

        {/* Content */}
        <div>
          <h1 className="text-h2 font-display font-bold text-neutral-900 dark:text-neutral-50 mb-3">
            Check Your Email
          </h1>
          <p className="text-body text-neutral-500 dark:text-neutral-400 max-w-sm mx-auto">
            We&apos;ve sent you a verification link. Please check your email and click the link
            to verify your account.
          </p>
        </div>

        {/* Tips */}
        <div className="bg-neutral-50 dark:bg-neutral-800/50 rounded-xl p-4 text-left max-w-sm mx-auto">
          <p className="text-body-sm font-medium text-neutral-700 dark:text-neutral-300 mb-2">
            Didn&apos;t receive the email?
          </p>
          <ul className="text-body-sm text-neutral-500 dark:text-neutral-400 space-y-1">
            <li className="flex items-start gap-2">
              <span className="text-accent-500 mt-1">&#x2022;</span>
              Check your spam or junk folder
            </li>
            <li className="flex items-start gap-2">
              <span className="text-accent-500 mt-1">&#x2022;</span>
              Make sure you entered the correct email
            </li>
          </ul>
        </div>

        {/* Back to Sign In */}
        <Link
          href="/signin"
          className="inline-flex items-center gap-2 text-body-sm font-medium text-accent-600 dark:text-accent-400 hover:text-accent-500 transition-colors"
        >
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
          </svg>
          Back to Sign In
        </Link>
      </div>
    );
  }

  // Verify the token
  const result = await verifyEmail(token);

  return (
    <div className="space-y-8 text-center">
      {result.success ? (
        <>
          {/* Success Icon */}
          <div className="flex justify-center">
            <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-green-400 to-green-600 flex items-center justify-center shadow-lg shadow-green-500/30">
              <svg className="w-10 h-10 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
          </div>

          {/* Success Content */}
          <div>
            <h1 className="text-h2 font-display font-bold text-neutral-900 dark:text-neutral-50 mb-3">
              Email Verified!
            </h1>
            <p className="text-body text-neutral-500 dark:text-neutral-400 max-w-sm mx-auto">
              {result.message}
            </p>
          </div>

          {/* Sign In Button */}
          <Link
            href="/signin"
            className="btn-primary inline-flex"
          >
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1" />
            </svg>
            Sign In Now
          </Link>
        </>
      ) : (
        <>
          {/* Error Icon */}
          <div className="flex justify-center">
            <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-red-400 to-red-600 flex items-center justify-center shadow-lg shadow-red-500/30">
              <svg className="w-10 h-10 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
          </div>

          {/* Error Content */}
          <div>
            <h1 className="text-h2 font-display font-bold text-neutral-900 dark:text-neutral-50 mb-3">
              Verification Failed
            </h1>
            <p className="text-body text-neutral-500 dark:text-neutral-400 max-w-sm mx-auto">
              {result.message}
            </p>
          </div>

          {/* Error Details */}
          <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl p-4 max-w-sm mx-auto">
            <p className="text-body-sm text-red-700 dark:text-red-400">
              The verification link may have expired or already been used. Please try signing up again to receive a new verification email.
            </p>
          </div>

          {/* Try Again Button */}
          <Link
            href="/signup"
            className="inline-flex items-center gap-2 text-body-sm font-medium text-accent-600 dark:text-accent-400 hover:text-accent-500 transition-colors"
          >
            Try signing up again
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 5l7 7m0 0l-7 7m7-7H3" />
            </svg>
          </Link>
        </>
      )}
    </div>
  );
}
