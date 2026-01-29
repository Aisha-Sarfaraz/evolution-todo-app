import { Metadata } from "next";
import { SignupForm } from "@/components/auth/signup-form";

export const metadata: Metadata = {
  title: "Create Account",
  description: "Create your Flowspace account and start organizing",
};

export default function SignupPage() {
  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-h2 font-display font-bold text-neutral-900 dark:text-neutral-50">
          Create your account
        </h1>
        <p className="mt-2 text-body text-neutral-500 dark:text-neutral-400">
          Start your productivity journey with Flowspace
        </p>
      </div>

      {/* Form */}
      <SignupForm />

      {/* Terms */}
      <p className="text-center text-caption text-neutral-500 dark:text-neutral-400">
        By creating an account, you agree to our{" "}
        <a href="#" className="underline hover:text-neutral-700 dark:hover:text-neutral-300">
          Terms of Service
        </a>{" "}
        and{" "}
        <a href="#" className="underline hover:text-neutral-700 dark:hover:text-neutral-300">
          Privacy Policy
        </a>
      </p>
    </div>
  );
}
