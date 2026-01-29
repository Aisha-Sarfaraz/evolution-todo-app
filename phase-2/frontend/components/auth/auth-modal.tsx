"use client";

/**
 * Auth modal component with professional Flowspace styling.
 * Provides tabbed signin/signup forms in a modal overlay.
 */

import { useState, useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useForm } from "react-hook-form";
import { signIn, signUp } from "@/lib/auth/better-auth";
import { clsx } from "clsx";

interface AuthModalProps {
  isOpen: boolean;
  onClose: () => void;
  defaultTab?: "signin" | "signup";
}

interface SignInFormData {
  email: string;
  password: string;
}

interface SignUpFormData {
  name: string;
  email: string;
  password: string;
}

interface PasswordStrength {
  score: number;
  label: string;
  color: string;
  bgColor: string;
}

function checkPasswordStrength(password: string): PasswordStrength {
  let score = 0;
  if (password.length >= 8) score++;
  if (password.length >= 12) score++;
  if (/[a-z]/.test(password)) score++;
  if (/[A-Z]/.test(password)) score++;
  if (/\d/.test(password)) score++;
  if (/[^a-zA-Z0-9]/.test(password)) score++;

  if (score <= 2) return { score, label: "Weak", color: "text-red-500", bgColor: "bg-red-500" };
  if (score <= 4) return { score, label: "Medium", color: "text-amber-500", bgColor: "bg-amber-500" };
  return { score, label: "Strong", color: "text-green-500", bgColor: "bg-green-500" };
}

export function AuthModal({ isOpen, onClose, defaultTab = "signin" }: AuthModalProps) {
  const [activeTab, setActiveTab] = useState<"signin" | "signup">(defaultTab);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showPassword, setShowPassword] = useState(false);
  const router = useRouter();
  const searchParams = useSearchParams();

  const signinForm = useForm<SignInFormData>({
    defaultValues: { email: "", password: "" },
  });

  const signupForm = useForm<SignUpFormData>({
    defaultValues: { name: "", email: "", password: "" },
  });

  const signupPassword = signupForm.watch("password", "");
  const passwordStrength = checkPasswordStrength(signupPassword);

  useEffect(() => {
    if (isOpen) {
      setActiveTab(defaultTab);
      setError(null);
      setShowPassword(false);
      signinForm.reset();
      signupForm.reset();
    }
  }, [isOpen, defaultTab, signinForm, signupForm]);

  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === "Escape" && isOpen) {
        onClose();
      }
    };

    if (isOpen) {
      document.addEventListener("keydown", handleEscape);
      document.body.style.overflow = "hidden";
    }

    return () => {
      document.removeEventListener("keydown", handleEscape);
      document.body.style.overflow = "";
    };
  }, [isOpen, onClose]);

  const onSignIn = async (data: SignInFormData) => {
    setIsLoading(true);
    setError(null);

    try {
      const { error: authError } = await signIn(data.email, data.password);

      if (authError) {
        if (authError.code === "EMAIL_NOT_VERIFIED") {
          setError("Please verify your email before signing in.");
        } else if (authError.code === "INVALID_CREDENTIALS") {
          setError("Invalid email or password.");
        } else {
          setError(authError.message || "Failed to sign in");
        }
        return;
      }

      const callbackUrl = searchParams.get("callbackUrl") || "/tasks";
      onClose();
      router.push(callbackUrl);
      router.refresh();
    } catch {
      setError("An unexpected error occurred. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  const onSignUp = async (data: SignUpFormData) => {
    setIsLoading(true);
    setError(null);

    try {
      const { error: authError } = await signUp(data.email, data.password, data.name);

      if (authError) {
        setError(authError.message || "Failed to create account");
        return;
      }

      onClose();
      router.push("/verify-email");
    } catch {
      setError("An unexpected error occurred. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 z-50 bg-neutral-900/60 dark:bg-black/70 backdrop-blur-sm animate-fade-in"
        onClick={onClose}
      />

      {/* Modal */}
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4 pointer-events-none">
        <div
          className="relative w-full max-w-md overflow-hidden bg-white dark:bg-neutral-900 rounded-2xl shadow-soft-xl border border-neutral-200 dark:border-neutral-800 pointer-events-auto animate-scale-in"
          onClick={(e) => e.stopPropagation()}
        >
          {/* Close Button */}
          <button
            onClick={onClose}
            className="absolute top-4 right-4 p-2 text-neutral-400 hover:text-neutral-600 dark:hover:text-neutral-300 hover:bg-neutral-100 dark:hover:bg-neutral-800 rounded-lg transition-colors z-10"
            aria-label="Close"
          >
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>

          {/* Header */}
          <div className="px-6 pt-6 pb-4 text-center">
            <div className="w-12 h-12 mx-auto mb-4 rounded-xl bg-gradient-to-br from-accent-500 to-purple-600 flex items-center justify-center shadow-soft">
              <svg className="w-6 h-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <h2 className="text-h3 font-display font-bold text-neutral-900 dark:text-neutral-100">
              {activeTab === "signin" ? "Welcome back" : "Create account"}
            </h2>
            <p className="mt-1 text-body-sm text-neutral-500 dark:text-neutral-400">
              {activeTab === "signin"
                ? "Sign in to continue to Flowspace"
                : "Start organizing your tasks today"}
            </p>
          </div>

          {/* Tabs */}
          <div className="px-6 mb-4">
            <div className="flex p-1 bg-neutral-100 dark:bg-neutral-800 rounded-xl">
              <button
                onClick={() => {
                  setActiveTab("signin");
                  setError(null);
                }}
                className={clsx(
                  "flex-1 py-2.5 text-body-sm font-medium rounded-lg transition-all duration-200",
                  activeTab === "signin"
                    ? "bg-white dark:bg-neutral-900 text-neutral-900 dark:text-neutral-100 shadow-sm"
                    : "text-neutral-500 dark:text-neutral-400 hover:text-neutral-700 dark:hover:text-neutral-300"
                )}
              >
                Sign In
              </button>
              <button
                onClick={() => {
                  setActiveTab("signup");
                  setError(null);
                }}
                className={clsx(
                  "flex-1 py-2.5 text-body-sm font-medium rounded-lg transition-all duration-200",
                  activeTab === "signup"
                    ? "bg-white dark:bg-neutral-900 text-neutral-900 dark:text-neutral-100 shadow-sm"
                    : "text-neutral-500 dark:text-neutral-400 hover:text-neutral-700 dark:hover:text-neutral-300"
                )}
              >
                Sign Up
              </button>
            </div>
          </div>

          {/* Form Content */}
          <div className="px-6 pb-6">
            {/* Error Alert */}
            {error && (
              <div className="mb-4 p-4 rounded-xl bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800">
                <div className="flex items-start gap-3">
                  <svg className="w-5 h-5 text-error flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <p className="text-body-sm text-red-700 dark:text-red-400">{error}</p>
                </div>
              </div>
            )}

            {activeTab === "signin" ? (
              <form onSubmit={signinForm.handleSubmit(onSignIn)} className="space-y-4">
                {/* Email */}
                <div className="space-y-2">
                  <label htmlFor="signin-email" className="text-body-sm font-medium text-neutral-700 dark:text-neutral-300">
                    Email
                  </label>
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                      <svg className="w-5 h-5 text-neutral-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                        <path strokeLinecap="round" strokeLinejoin="round" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                      </svg>
                    </div>
                    <input
                      id="signin-email"
                      type="email"
                      autoComplete="email"
                      placeholder="you@example.com"
                      className={clsx(
                        "input-field pl-12",
                        signinForm.formState.errors.email && "border-error focus:border-error"
                      )}
                      {...signinForm.register("email", {
                        required: "Email is required",
                        pattern: {
                          value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                          message: "Invalid email address",
                        },
                      })}
                    />
                  </div>
                  {signinForm.formState.errors.email && (
                    <p className="text-caption text-error">{signinForm.formState.errors.email.message}</p>
                  )}
                </div>

                {/* Password */}
                <div className="space-y-2">
                  <label htmlFor="signin-password" className="text-body-sm font-medium text-neutral-700 dark:text-neutral-300">
                    Password
                  </label>
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                      <svg className="w-5 h-5 text-neutral-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                        <path strokeLinecap="round" strokeLinejoin="round" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                      </svg>
                    </div>
                    <input
                      id="signin-password"
                      type={showPassword ? "text" : "password"}
                      autoComplete="current-password"
                      placeholder="Enter your password"
                      className={clsx(
                        "input-field pl-12 pr-12",
                        signinForm.formState.errors.password && "border-error focus:border-error"
                      )}
                      {...signinForm.register("password", { required: "Password is required" })}
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute inset-y-0 right-0 pr-4 flex items-center text-neutral-400 hover:text-neutral-600 dark:hover:text-neutral-300"
                    >
                      {showPassword ? (
                        <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                          <path strokeLinecap="round" strokeLinejoin="round" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
                        </svg>
                      ) : (
                        <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                          <path strokeLinecap="round" strokeLinejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                          <path strokeLinecap="round" strokeLinejoin="round" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                        </svg>
                      )}
                    </button>
                  </div>
                  {signinForm.formState.errors.password && (
                    <p className="text-caption text-error">{signinForm.formState.errors.password.message}</p>
                  )}
                </div>

                {/* Forgot Password Link */}
                <div className="text-right">
                  <a
                    href="/reset-password"
                    className="text-body-sm text-accent-600 dark:text-accent-400 hover:text-accent-700 dark:hover:text-accent-300 font-medium"
                  >
                    Forgot password?
                  </a>
                </div>

                {/* Submit */}
                <button type="submit" disabled={isLoading} className="btn-primary w-full py-3">
                  {isLoading ? (
                    <span className="flex items-center justify-center gap-2">
                      <svg className="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                      </svg>
                      Signing in...
                    </span>
                  ) : (
                    "Sign In"
                  )}
                </button>
              </form>
            ) : (
              <form onSubmit={signupForm.handleSubmit(onSignUp)} className="space-y-4">
                {/* Name */}
                <div className="space-y-2">
                  <label htmlFor="signup-name" className="text-body-sm font-medium text-neutral-700 dark:text-neutral-300">
                    Full name
                  </label>
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                      <svg className="w-5 h-5 text-neutral-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                        <path strokeLinecap="round" strokeLinejoin="round" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                      </svg>
                    </div>
                    <input
                      id="signup-name"
                      type="text"
                      autoComplete="name"
                      placeholder="John Doe"
                      className={clsx(
                        "input-field pl-12",
                        signupForm.formState.errors.name && "border-error focus:border-error"
                      )}
                      {...signupForm.register("name", {
                        required: "Name is required",
                        minLength: { value: 2, message: "Name must be at least 2 characters" },
                      })}
                    />
                  </div>
                  {signupForm.formState.errors.name && (
                    <p className="text-caption text-error">{signupForm.formState.errors.name.message}</p>
                  )}
                </div>

                {/* Email */}
                <div className="space-y-2">
                  <label htmlFor="signup-email" className="text-body-sm font-medium text-neutral-700 dark:text-neutral-300">
                    Email
                  </label>
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                      <svg className="w-5 h-5 text-neutral-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                        <path strokeLinecap="round" strokeLinejoin="round" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                      </svg>
                    </div>
                    <input
                      id="signup-email"
                      type="email"
                      autoComplete="email"
                      placeholder="you@example.com"
                      className={clsx(
                        "input-field pl-12",
                        signupForm.formState.errors.email && "border-error focus:border-error"
                      )}
                      {...signupForm.register("email", {
                        required: "Email is required",
                        pattern: {
                          value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                          message: "Invalid email address",
                        },
                      })}
                    />
                  </div>
                  {signupForm.formState.errors.email && (
                    <p className="text-caption text-error">{signupForm.formState.errors.email.message}</p>
                  )}
                </div>

                {/* Password */}
                <div className="space-y-2">
                  <label htmlFor="signup-password" className="text-body-sm font-medium text-neutral-700 dark:text-neutral-300">
                    Password
                  </label>
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                      <svg className="w-5 h-5 text-neutral-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                        <path strokeLinecap="round" strokeLinejoin="round" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                      </svg>
                    </div>
                    <input
                      id="signup-password"
                      type={showPassword ? "text" : "password"}
                      autoComplete="new-password"
                      placeholder="Create a strong password"
                      className={clsx(
                        "input-field pl-12 pr-12",
                        signupForm.formState.errors.password && "border-error focus:border-error"
                      )}
                      {...signupForm.register("password", {
                        required: "Password is required",
                        minLength: { value: 8, message: "Password must be at least 8 characters" },
                      })}
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute inset-y-0 right-0 pr-4 flex items-center text-neutral-400 hover:text-neutral-600 dark:hover:text-neutral-300"
                    >
                      {showPassword ? (
                        <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                          <path strokeLinecap="round" strokeLinejoin="round" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
                        </svg>
                      ) : (
                        <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                          <path strokeLinecap="round" strokeLinejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                          <path strokeLinecap="round" strokeLinejoin="round" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                        </svg>
                      )}
                    </button>
                  </div>
                  {signupForm.formState.errors.password && (
                    <p className="text-caption text-error">{signupForm.formState.errors.password.message}</p>
                  )}

                  {/* Password Strength */}
                  {signupPassword && (
                    <div className="mt-2 space-y-2">
                      <div className="flex items-center gap-3">
                        <div className="flex-1 h-1.5 bg-neutral-200 dark:bg-neutral-700 rounded-full overflow-hidden">
                          <div
                            className={clsx("h-full transition-all duration-300", passwordStrength.bgColor)}
                            style={{ width: `${(passwordStrength.score / 6) * 100}%` }}
                          />
                        </div>
                        <span className={clsx("text-caption font-medium", passwordStrength.color)}>
                          {passwordStrength.label}
                        </span>
                      </div>
                    </div>
                  )}
                </div>

                {/* Submit */}
                <button type="submit" disabled={isLoading} className="btn-primary w-full py-3">
                  {isLoading ? (
                    <span className="flex items-center justify-center gap-2">
                      <svg className="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                      </svg>
                      Creating account...
                    </span>
                  ) : (
                    "Create Account"
                  )}
                </button>

                {/* Terms */}
                <p className="text-caption text-center text-neutral-500 dark:text-neutral-400">
                  By signing up, you agree to our{" "}
                  <a href="#" className="text-accent-600 dark:text-accent-400 hover:underline">
                    Terms of Service
                  </a>{" "}
                  and{" "}
                  <a href="#" className="text-accent-600 dark:text-accent-400 hover:underline">
                    Privacy Policy
                  </a>
                </p>
              </form>
            )}
          </div>
        </div>
      </div>
    </>
  );
}
