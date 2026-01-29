/**
 * Reset password page.
 *
 * T052: [US1] Create reset-password page
 * Server component that renders ResetPasswordForm.
 * Shows request form if no token, reset form if token provided.
 */

import { Metadata } from "next";
import Link from "next/link";
import { ResetPasswordForm } from "@/components/auth/reset-password-form";

export const metadata: Metadata = {
  title: "Reset Password",
  description: "Reset your password to regain access to your Flowspace account",
};

interface ResetPasswordPageProps {
  searchParams: Promise<{ token?: string }>;
}

export default async function ResetPasswordPage({ searchParams }: ResetPasswordPageProps) {
  const { token } = await searchParams;

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-h2 font-display font-bold text-neutral-900 dark:text-neutral-50">
          {token ? "Set New Password" : "Reset Password"}
        </h1>
        <p className="mt-2 text-body text-neutral-500 dark:text-neutral-400">
          {token
            ? "Enter your new password below"
            : "Enter your email to receive a reset link"}
        </p>
      </div>

      {/* Form */}
      <ResetPasswordForm token={token} />

      {/* Back to Sign In */}
      <div className="text-center">
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
    </div>
  );
}
