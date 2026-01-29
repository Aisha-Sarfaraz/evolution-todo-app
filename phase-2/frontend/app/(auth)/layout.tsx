"use client";

import type { ReactNode } from "react";
import Link from "next/link";

interface AuthLayoutProps {
  children: ReactNode;
}

export default function AuthLayout({ children }: AuthLayoutProps) {
  return (
    <div className="min-h-screen flex bg-canvas dark:bg-canvas-dark">
      {/* Left Panel - Decorative */}
      <div className="hidden lg:flex lg:w-1/2 relative overflow-hidden">
        {/* Background gradient */}
        <div className="absolute inset-0 bg-gradient-to-br from-accent-600 via-purple-600 to-pink-600" />

        {/* Pattern overlay */}
        <div className="absolute inset-0 opacity-10">
          <svg className="w-full h-full" viewBox="0 0 100 100" preserveAspectRatio="none">
            <defs>
              <pattern id="auth-grid" width="10" height="10" patternUnits="userSpaceOnUse">
                <path d="M 10 0 L 0 0 0 10" fill="none" stroke="white" strokeWidth="0.5" />
              </pattern>
            </defs>
            <rect width="100" height="100" fill="url(#auth-grid)" />
          </svg>
        </div>

        {/* Floating shapes */}
        <div className="absolute top-20 left-20 w-32 h-32 rounded-full bg-white/10 blur-xl animate-pulse-soft" />
        <div className="absolute bottom-32 right-20 w-48 h-48 rounded-full bg-white/10 blur-xl animate-pulse-soft animation-delay-200" />
        <div className="absolute top-1/2 left-1/3 w-24 h-24 rounded-full bg-white/5 blur-lg" />

        {/* Content */}
        <div className="relative z-10 flex flex-col justify-between p-12 text-white">
          {/* Logo */}
          <Link href="/" className="flex items-center gap-3 no-underline">
            <div className="w-10 h-10 rounded-xl bg-white/20 backdrop-blur-sm flex items-center justify-center">
              <svg
                className="w-6 h-6 text-white"
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
            <span className="font-display font-bold text-2xl text-white">
              Flowspace
            </span>
          </Link>

          {/* Main content */}
          <div className="max-w-md">
            <h1 className="text-4xl font-display font-bold mb-6 leading-tight">
              Organize your life,
              <br />
              one task at a time
            </h1>
            <p className="text-lg text-white/80 leading-relaxed">
              Join thousands of professionals who trust Flowspace to manage
              their tasks and boost productivity.
            </p>

            {/* Feature highlights */}
            <div className="mt-10 space-y-4">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-lg bg-white/20 flex items-center justify-center">
                  <svg
                    className="w-4 h-4"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                    strokeWidth={2}
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      d="M5 13l4 4L19 7"
                    />
                  </svg>
                </div>
                <span className="text-white/90">Smart task organization</span>
              </div>
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-lg bg-white/20 flex items-center justify-center">
                  <svg
                    className="w-4 h-4"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                    strokeWidth={2}
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      d="M5 13l4 4L19 7"
                    />
                  </svg>
                </div>
                <span className="text-white/90">Powerful search & filters</span>
              </div>
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-lg bg-white/20 flex items-center justify-center">
                  <svg
                    className="w-4 h-4"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                    strokeWidth={2}
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      d="M5 13l4 4L19 7"
                    />
                  </svg>
                </div>
                <span className="text-white/90">Free forever, no limits</span>
              </div>
            </div>
          </div>

          {/* Footer */}
          <p className="text-sm text-white/60">
            © 2026 Flowspace. All rights reserved.
          </p>
        </div>
      </div>

      {/* Right Panel - Form */}
      <div className="flex-1 flex flex-col">
        {/* Mobile header */}
        <div className="lg:hidden p-6">
          <Link href="/" className="flex items-center gap-2 no-underline">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-accent-500 to-purple-600 flex items-center justify-center">
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
        </div>

        {/* Form container */}
        <div className="flex-1 flex items-center justify-center px-6 py-12 lg:px-12">
          <div className="w-full max-w-md">
            {children}
          </div>
        </div>

        {/* Mobile footer */}
        <div className="lg:hidden p-6 text-center">
          <p className="text-caption text-neutral-500 dark:text-neutral-400">
            © 2026 Flowspace. All rights reserved.
          </p>
        </div>
      </div>
    </div>
  );
}
