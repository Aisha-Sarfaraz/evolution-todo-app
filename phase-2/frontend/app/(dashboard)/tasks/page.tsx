/**
 * Tasks list page.
 *
 * T071: [US2] Create tasks list page
 * T132: [US6] URL query parameter sync
 * T133: [US6] Apply filters to task list
 */

import { Metadata } from "next";
import { TasksPageClient } from "./tasks-page-client";

export const metadata: Metadata = {
  title: "Tasks - Todo App",
  description: "Manage your tasks",
};

export default function TasksPage() {
  return <TasksPageClient />;
}
