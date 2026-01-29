"use client";

import { clsx } from "clsx";

export interface SkeletonProps {
  className?: string;
  variant?: "default" | "shimmer";
}

export function Skeleton({ className, variant = "shimmer" }: SkeletonProps) {
  return (
    <div
      className={clsx(
        variant === "shimmer"
          ? "bg-gradient-to-r from-neutral-200 via-neutral-100 to-neutral-200 dark:from-neutral-800 dark:via-neutral-700 dark:to-neutral-800 bg-[length:200%_100%] animate-shimmer"
          : "bg-neutral-200 dark:bg-neutral-800 animate-pulse",
        "rounded-lg",
        className
      )}
    />
  );
}

// Pre-built skeleton components
export function SkeletonText({
  lines = 1,
  className,
}: {
  lines?: number;
  className?: string;
}) {
  return (
    <div className={clsx("space-y-2", className)}>
      {Array.from({ length: lines }).map((_, i) => (
        <Skeleton
          key={i}
          className={clsx("h-4", i === lines - 1 && lines > 1 ? "w-3/4" : "w-full")}
        />
      ))}
    </div>
  );
}

export function SkeletonAvatar({
  size = "md",
  className,
}: {
  size?: "sm" | "md" | "lg";
  className?: string;
}) {
  const sizes = {
    sm: "w-8 h-8",
    md: "w-10 h-10",
    lg: "w-12 h-12",
  };

  return <Skeleton className={clsx("rounded-full", sizes[size], className)} />;
}

export function SkeletonCard({ className }: { className?: string }) {
  return (
    <div
      className={clsx(
        "p-5 rounded-2xl border border-neutral-200 dark:border-neutral-800",
        className
      )}
    >
      <div className="flex items-start gap-4">
        <Skeleton className="w-6 h-6 rounded-full" />
        <div className="flex-1 space-y-3">
          <Skeleton className="h-5 w-3/4" />
          <Skeleton className="h-4 w-full" />
          <Skeleton className="h-4 w-1/2" />
          <div className="flex gap-2 pt-2">
            <Skeleton className="h-6 w-16 rounded-full" />
            <Skeleton className="h-6 w-20 rounded-full" />
          </div>
        </div>
      </div>
    </div>
  );
}

export function SkeletonTaskList({
  count = 3,
  className,
}: {
  count?: number;
  className?: string;
}) {
  return (
    <div className={clsx("space-y-3", className)}>
      {Array.from({ length: count }).map((_, i) => (
        <SkeletonCard key={i} />
      ))}
    </div>
  );
}

export function SkeletonForm({ className }: { className?: string }) {
  return (
    <div className={clsx("space-y-5", className)}>
      <div className="space-y-2">
        <Skeleton className="h-4 w-20" />
        <Skeleton className="h-12 w-full rounded-xl" />
      </div>
      <div className="space-y-2">
        <Skeleton className="h-4 w-24" />
        <Skeleton className="h-12 w-full rounded-xl" />
      </div>
      <div className="space-y-2">
        <Skeleton className="h-4 w-16" />
        <Skeleton className="h-24 w-full rounded-xl" />
      </div>
      <Skeleton className="h-12 w-full rounded-xl" />
    </div>
  );
}
