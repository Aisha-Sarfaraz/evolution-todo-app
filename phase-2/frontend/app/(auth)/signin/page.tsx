import { Metadata } from "next";
import Link from "next/link";
import { SigninForm } from "@/components/auth/signin-form";

export const metadata: Metadata = {
  title: "Sign In",
  description: "Sign in to your Flowspace account",
};

export default function SigninPage() {
  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-h2 font-display font-bold text-neutral-900 dark:text-neutral-50">
          Welcome back
        </h1>
        <p className="mt-2 text-body text-neutral-500 dark:text-neutral-400">
          Sign in to continue to your workspace
        </p>
      </div>

      {/* Form */}
      <SigninForm />

      {/* Forgot Password */}
      <div className="text-center">
        <Link
          href="/reset-password"
          className="text-body-sm font-medium text-accent-600 dark:text-accent-400 hover:text-accent-500 transition-colors"
        >
          Forgot your password?
        </Link>
      </div>
    </div>
  );
}
