/**
 * Profile page with Flowspace styling.
 *
 * T056: [US1] Create profile page
 * Server component that displays user profile settings.
 */

import { Metadata } from "next";
import { ProfileEditForm } from "@/components/auth/profile-edit-form";

export const metadata: Metadata = {
  title: "Profile | Flowspace",
  description: "Manage your Flowspace account settings and profile",
};

export default function ProfilePage() {
  return (
    <div className="max-w-2xl mx-auto space-y-8">
      {/* Page Header */}
      <div>
        <h1 className="text-h1 font-display font-bold text-neutral-900 dark:text-neutral-50">
          Profile Settings
        </h1>
        <p className="mt-1 text-body text-neutral-500 dark:text-neutral-400">
          Manage your account information and security settings
        </p>
      </div>

      {/* Profile Card */}
      <div className="card overflow-hidden">
        <ProfileEditForm />
      </div>
    </div>
  );
}
