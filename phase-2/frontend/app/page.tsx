"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useSession } from "@/lib/auth/better-auth";
import { AuthModal } from "@/components/auth/auth-modal";
import { Button } from "@/components/ui/button";

export default function HomePage() {
  const router = useRouter();
  const { data: session, isPending } = useSession();
  const [authModal, setAuthModal] = useState<{
    isOpen: boolean;
    defaultTab: "signin" | "signup";
  }>({ isOpen: false, defaultTab: "signin" });

  useEffect(() => {
    if (!isPending && session?.user) {
      router.push("/tasks");
    }
  }, [session, isPending, router]);

  if (isPending) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-canvas dark:bg-canvas-dark">
        <div className="flex flex-col items-center gap-4">
          <div className="w-10 h-10 border-3 border-accent-600 border-t-transparent rounded-full animate-spin" />
          <p className="text-body-sm text-neutral-500">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-canvas dark:bg-canvas-dark">
      {/* Header */}
      <header className="fixed top-0 left-0 right-0 z-40">
        <div className="mx-auto px-4 sm:px-6 lg:px-8">
          <nav className="flex items-center justify-between h-18 mt-4">
            {/* Logo */}
            <Link
              href="/"
              className="flex items-center gap-2 group no-underline"
            >
              <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-accent-500 to-purple-600 flex items-center justify-center shadow-soft group-hover:shadow-glow transition-shadow">
                <svg
                  className="w-5 h-5 text-white"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  strokeWidth={2.5}
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M5 13l4 4L19 7"
                  />
                </svg>
              </div>
              <span className="font-display font-bold text-xl text-neutral-900 dark:text-neutral-50">
                Flowspace
              </span>
            </Link>

            {/* Nav Actions */}
            <div className="flex items-center gap-3">
              <Button
                variant="ghost"
                onClick={() =>
                  setAuthModal({ isOpen: true, defaultTab: "signin" })
                }
              >
                Sign in
              </Button>
              <Button
                variant="primary"
                onClick={() =>
                  setAuthModal({ isOpen: true, defaultTab: "signup" })
                }
              >
                Get Started
              </Button>
            </div>
          </nav>
        </div>
      </header>

      {/* Hero Section */}
      <main>
        <section className="relative pt-32 pb-24 overflow-hidden">
          {/* Background decoration */}
          <div className="absolute inset-0 pointer-events-none">
            <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[600px] bg-gradient-to-br from-accent-200/40 via-purple-200/30 to-pink-200/40 dark:from-accent-900/20 dark:via-purple-900/15 dark:to-pink-900/20 rounded-full blur-3xl opacity-60" />
            <div className="absolute bottom-0 right-0 w-[400px] h-[400px] bg-gradient-to-tl from-accent-100/50 to-transparent dark:from-accent-950/30 rounded-full blur-3xl" />
          </div>

          {/* Grid pattern */}
          <div className="absolute inset-0 opacity-[0.015] dark:opacity-[0.03] pattern-grid text-neutral-900 dark:text-neutral-100" />

          <div className="relative mx-auto max-w-5xl px-4 sm:px-6 lg:px-8 text-center">
            {/* Badge */}
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-accent-50 dark:bg-accent-900/30 text-accent-700 dark:text-accent-300 text-caption font-medium mb-8 animate-fade-in-down">
              <span className="w-2 h-2 rounded-full bg-accent-500 animate-pulse-soft" />
              Free to use, forever
            </div>

            {/* Headline */}
            <h1 className="text-display sm:text-[3.5rem] lg:text-[4rem] font-display font-bold text-neutral-900 dark:text-neutral-50 mb-6 animate-fade-in-up">
              Task management
              <br />
              <span className="gradient-text">made simple</span>
            </h1>

            {/* Subheadline */}
            <p className="text-lg sm:text-xl text-neutral-600 dark:text-neutral-400 max-w-2xl mx-auto mb-10 animate-fade-in-up animation-delay-100">
              Flowspace helps you organize tasks, track progress, and achieve
              more with an intuitive interface designed for seamless
              productivity.
            </p>

            {/* CTA Buttons */}
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4 animate-fade-in-up animation-delay-200">
              <Button
                variant="primary"
                size="lg"
                onClick={() =>
                  setAuthModal({ isOpen: true, defaultTab: "signup" })
                }
                rightIcon={
                  <svg
                    className="w-5 h-5"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M13 7l5 5m0 0l-5 5m5-5H6"
                    />
                  </svg>
                }
              >
                Start for free
              </Button>
              <Button
                variant="outline"
                size="lg"
                onClick={() =>
                  setAuthModal({ isOpen: true, defaultTab: "signin" })
                }
              >
                Sign in to continue
              </Button>
            </div>

            {/* Trust indicators */}
            <div className="mt-16 flex flex-wrap items-center justify-center gap-8 text-caption text-neutral-400 dark:text-neutral-500 animate-fade-in-up animation-delay-300">
              <div className="flex items-center gap-2">
                <svg
                  className="w-4 h-4"
                  fill="currentColor"
                  viewBox="0 0 20 20"
                >
                  <path
                    fillRule="evenodd"
                    d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                    clipRule="evenodd"
                  />
                </svg>
                <span>No credit card required</span>
              </div>
              <div className="flex items-center gap-2">
                <svg
                  className="w-4 h-4"
                  fill="currentColor"
                  viewBox="0 0 20 20"
                >
                  <path
                    fillRule="evenodd"
                    d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z"
                    clipRule="evenodd"
                  />
                </svg>
                <span>Secure by design</span>
              </div>
              <div className="flex items-center gap-2">
                <svg
                  className="w-4 h-4"
                  fill="currentColor"
                  viewBox="0 0 20 20"
                >
                  <path
                    fillRule="evenodd"
                    d="M11.3 1.046A1 1 0 0112 2v5h4a1 1 0 01.82 1.573l-7 10A1 1 0 018 18v-5H4a1 1 0 01-.82-1.573l7-10a1 1 0 011.12-.38z"
                    clipRule="evenodd"
                  />
                </svg>
                <span>Lightning fast</span>
              </div>
            </div>
          </div>
        </section>

        {/* Features Section */}
        <section className="py-24 bg-white dark:bg-neutral-900/50">
          <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-16">
              <h2 className="text-h1 font-display font-bold text-neutral-900 dark:text-neutral-50 mb-4">
                Everything you need
              </h2>
              <p className="text-lg text-neutral-600 dark:text-neutral-400 max-w-xl mx-auto">
                Powerful features wrapped in a simple interface. Focus on what
                matters.
              </p>
            </div>

            <div className="grid md:grid-cols-3 gap-8">
              {/* Feature 1 */}
              <div className="group p-8 rounded-3xl bg-canvas dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-800 hover:border-accent-200 dark:hover:border-accent-800 hover:shadow-soft-lg transition-all duration-300">
                <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-accent-500 to-accent-600 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300">
                  <svg
                    className="w-7 h-7 text-white"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                    strokeWidth={2}
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4"
                    />
                  </svg>
                </div>
                <h3 className="text-h3 font-display font-semibold text-neutral-900 dark:text-neutral-50 mb-3">
                  Smart Tasks
                </h3>
                <p className="text-body text-neutral-600 dark:text-neutral-400">
                  Organize with categories, tags, and priorities. Find what you
                  need instantly with powerful filters.
                </p>
              </div>

              {/* Feature 2 */}
              <div className="group p-8 rounded-3xl bg-canvas dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-800 hover:border-purple-200 dark:hover:border-purple-800 hover:shadow-soft-lg transition-all duration-300">
                <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-purple-500 to-purple-600 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300">
                  <svg
                    className="w-7 h-7 text-white"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                    strokeWidth={2}
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                    />
                  </svg>
                </div>
                <h3 className="text-h3 font-display font-semibold text-neutral-900 dark:text-neutral-50 mb-3">
                  Quick Search
                </h3>
                <p className="text-body text-neutral-600 dark:text-neutral-400">
                  Find anything instantly with powerful full-text search across
                  all your tasks and descriptions.
                </p>
              </div>

              {/* Feature 3 */}
              <div className="group p-8 rounded-3xl bg-canvas dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-800 hover:border-pink-200 dark:hover:border-pink-800 hover:shadow-soft-lg transition-all duration-300">
                <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-pink-500 to-pink-600 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300">
                  <svg
                    className="w-7 h-7 text-white"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                    strokeWidth={2}
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      d="M13 10V3L4 14h7v7l9-11h-7z"
                    />
                  </svg>
                </div>
                <h3 className="text-h3 font-display font-semibold text-neutral-900 dark:text-neutral-50 mb-3">
                  Fast & Fluid
                </h3>
                <p className="text-body text-neutral-600 dark:text-neutral-400">
                  Lightning-fast interface with instant updates. No waiting,
                  just pure productivity.
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* CTA Section */}
        <section className="py-24">
          <div className="mx-auto max-w-4xl px-4 sm:px-6 lg:px-8">
            <div className="relative overflow-hidden rounded-4xl bg-gradient-to-br from-accent-600 via-purple-600 to-pink-600 p-12 md:p-16 text-center">
              {/* Pattern overlay */}
              <div className="absolute inset-0 opacity-10 pattern-dots text-white" />

              <div className="relative">
                <h2 className="text-h1 md:text-display font-display font-bold text-white mb-4">
                  Ready to get started?
                </h2>
                <p className="text-lg text-white/80 max-w-lg mx-auto mb-8">
                  Join thousands of users who trust Flowspace to manage their
                  tasks efficiently.
                </p>
                <Button
                  variant="secondary"
                  size="lg"
                  onClick={() =>
                    setAuthModal({ isOpen: true, defaultTab: "signup" })
                  }
                  className="bg-white text-accent-700 hover:bg-neutral-100"
                  rightIcon={
                    <svg
                      className="w-5 h-5"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M13 7l5 5m0 0l-5 5m5-5H6"
                      />
                    </svg>
                  }
                >
                  Create free account
                </Button>
              </div>
            </div>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="py-12 border-t border-neutral-200 dark:border-neutral-800">
        <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col md:flex-row items-center justify-between gap-6">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-accent-500 to-purple-600 flex items-center justify-center">
                <svg
                  className="w-4 h-4 text-white"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  strokeWidth={2.5}
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M5 13l4 4L19 7"
                  />
                </svg>
              </div>
              <span className="font-display font-semibold text-neutral-900 dark:text-neutral-50">
                Flowspace
              </span>
            </div>
            <p className="text-body-sm text-neutral-500 dark:text-neutral-400">
              © 2026 Flowspace. Built with Next.js.
            </p>
          </div>
        </div>
      </footer>

      {/* Auth Modal */}
      <AuthModal
        isOpen={authModal.isOpen}
        onClose={() => setAuthModal({ ...authModal, isOpen: false })}
        defaultTab={authModal.defaultTab}
      />
    </div>
  );
}
