/**
 * Tasks list page.
 *
 * T071: [US2] Create tasks list page
 * T132: [US6] URL query parameter sync
 * T133: [US6] Apply filters to task list
 */

import { Suspense } from "react";
import { Metadata } from "next";
import { TasksPageClient } from "./tasks-page-client";

export const metadata: Metadata = {
  title: "Tasks - Todo App",
  description: "Manage your tasks",
};

export default function TasksPage() {
  return (
    <Suspense fallback={<div className="animate-pulse h-96 bg-neutral-100 dark:bg-neutral-800 rounded-lg" />}>
      <TasksPageClient />
    </Suspense>
  );
}
