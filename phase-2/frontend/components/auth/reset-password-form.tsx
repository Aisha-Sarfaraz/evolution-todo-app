"use client";

/**
 * Reset password form component with Flowspace styling.
 *
 * T055: [US1] Create reset password form component
 * Client component for password reset request and password update.
 */

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { requestPasswordReset, resetPassword } from "@/lib/auth/better-auth";

interface RequestResetFormData {
  email: string;
}

interface ResetPasswordFormData {
  newPassword: string;
  confirmPassword: string;
}

interface ResetPasswordFormProps {
  token: string | undefined;
}

export function ResetPasswordForm({ token }: ResetPasswordFormProps) {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  // Request reset form
  const requestForm = useForm<RequestResetFormData>();

  // Reset password form
  const resetForm = useForm<ResetPasswordFormData>();

  const newPassword = resetForm.watch("newPassword", "");

  const onRequestReset = async (data: RequestResetFormData) => {
    setIsLoading(true);
    setError(null);
    setSuccess(null);

    try {
      const { error: resetError } = await requestPasswordReset(data.email);

      if (resetError) {
        setError(resetError.message || "Failed to send reset email");
        return;
      }

      setSuccess("If this email exists, a password reset link has been sent. Please check your inbox.");
    } catch {
      setError("An unexpected error occurred. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  const onResetPassword = async (data: ResetPasswordFormData) => {
    if (!token) return;

    setIsLoading(true);
    setError(null);

    try {
      const { error: resetError } = await resetPassword(token, data.newPassword);

      if (resetError) {
        if (resetError.code === "TOKEN_EXPIRED") {
          setError("Reset link expired. Please request a new password reset.");
        } else {
          setError(resetError.message || "Failed to reset password");
        }
        return;
      }

      // Redirect to signin with success message
      router.push("/signin?reset=success");
    } catch {
      setError("An unexpected error occurred. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  // Show reset form if token is provided
  if (token) {
    return (
      <form onSubmit={resetForm.handleSubmit(onResetPassword)} className="space-y-5">
        {/* Error Alert */}
        {error && (
          <div className="flex items-start gap-3 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl">
            <svg className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <p className="text-sm text-red-700 dark:text-red-400">{error}</p>
          </div>
        )}

        {/* New Password Field */}
        <div className="space-y-2">
          <label
            htmlFor="newPassword"
            className="block text-sm font-medium text-neutral-700 dark:text-neutral-300"
          >
            New Password
          </label>
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
              <svg className="w-5 h-5 text-neutral-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
              </svg>
            </div>
            <input
              id="newPassword"
              type="password"
              autoComplete="new-password"
              placeholder="Enter new password"
              {...resetForm.register("newPassword", {
                required: "New password is required",
                minLength: { value: 8, message: "Password must be at least 8 characters" },
                pattern: {
                  value: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$/,
                  message: "Password must include uppercase, lowercase, and number",
                },
              })}
              className="input-field pl-12"
            />
          </div>
          {resetForm.formState.errors.newPassword && (
            <p className="text-sm text-red-600 dark:text-red-400">
              {resetForm.formState.errors.newPassword.message}
            </p>
          )}
        </div>

        {/* Confirm Password Field */}
        <div className="space-y-2">
          <label
            htmlFor="confirmPassword"
            className="block text-sm font-medium text-neutral-700 dark:text-neutral-300"
          >
            Confirm New Password
          </label>
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
              <svg className="w-5 h-5 text-neutral-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <input
              id="confirmPassword"
              type="password"
              autoComplete="new-password"
              placeholder="Confirm new password"
              {...resetForm.register("confirmPassword", {
                required: "Please confirm your password",
                validate: (value) => value === newPassword || "Passwords do not match",
              })}
              className="input-field pl-12"
            />
          </div>
          {resetForm.formState.errors.confirmPassword && (
            <p className="text-sm text-red-600 dark:text-red-400">
              {resetForm.formState.errors.confirmPassword.message}
            </p>
          )}
        </div>

        {/* Submit Button */}
        <button
          type="submit"
          disabled={isLoading}
          className="btn-primary w-full"
        >
          {isLoading ? (
            <>
              <svg className="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
              </svg>
              Resetting Password...
            </>
          ) : (
            "Reset Password"
          )}
        </button>
      </form>
    );
  }

  // Show request reset form
  return (
    <form onSubmit={requestForm.handleSubmit(onRequestReset)} className="space-y-5">
      {/* Error Alert */}
      {error && (
        <div className="flex items-start gap-3 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl">
          <svg className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <p className="text-sm text-red-700 dark:text-red-400">{error}</p>
        </div>
      )}

      {/* Success Alert */}
      {success && (
        <div className="flex items-start gap-3 p-4 bg-emerald-50 dark:bg-emerald-900/20 border border-emerald-200 dark:border-emerald-800 rounded-xl">
          <svg className="w-5 h-5 text-emerald-500 flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <p className="text-sm text-emerald-700 dark:text-emerald-400">{success}</p>
        </div>
      )}

      <p className="text-sm text-neutral-600 dark:text-neutral-400 text-center">
        Enter your email address and we&apos;ll send you a link to reset your password.
      </p>

      {/* Email Field */}
      <div className="space-y-2">
        <label
          htmlFor="email"
          className="block text-sm font-medium text-neutral-700 dark:text-neutral-300"
        >
          Email
        </label>
        <div className="relative">
          <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
            <svg className="w-5 h-5 text-neutral-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
            </svg>
          </div>
          <input
            id="email"
            type="email"
            autoComplete="email"
            placeholder="Enter your email"
            {...requestForm.register("email", {
              required: "Email is required",
              pattern: {
                value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                message: "Invalid email address",
              },
            })}
            className="input-field pl-12"
          />
        </div>
        {requestForm.formState.errors.email && (
          <p className="text-sm text-red-600 dark:text-red-400">
            {requestForm.formState.errors.email.message}
          </p>
        )}
      </div>

      {/* Submit Button */}
      <button
        type="submit"
        disabled={isLoading}
        className="btn-primary w-full"
      >
        {isLoading ? (
          <>
            <svg className="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
            </svg>
            Sending...
          </>
        ) : (
          "Send Reset Link"
        )}
      </button>
    </form>
  );
}
