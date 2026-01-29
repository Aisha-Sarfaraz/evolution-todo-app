"use client";

/**
 * Profile edit form component with Flowspace styling.
 *
 * T057: [US1] Create profile edit component
 * Client component for updating display_name and changing password.
 */

import { useState, useEffect } from "react";
import { useForm } from "react-hook-form";
import { useSession } from "@/lib/auth/better-auth";
import { api } from "@/lib/api/client";

interface ProfileFormData {
  displayName: string;
}

interface PasswordFormData {
  currentPassword: string;
  newPassword: string;
  confirmPassword: string;
}

interface UserProfile {
  id: string;
  email: string;
  display_name: string | null;
  email_verified: boolean;
  created_at: string;
  last_signin_at: string | null;
}

export function ProfileEditForm() {
  const { data: session, isPending } = useSession();
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [isLoadingProfile, setIsLoadingProfile] = useState(true);
  const [isSavingProfile, setIsSavingProfile] = useState(false);
  const [isSavingPassword, setIsSavingPassword] = useState(false);
  const [profileError, setProfileError] = useState<string | null>(null);
  const [passwordError, setPasswordError] = useState<string | null>(null);
  const [profileSuccess, setProfileSuccess] = useState<string | null>(null);
  const [passwordSuccess, setPasswordSuccess] = useState<string | null>(null);

  const profileForm = useForm<ProfileFormData>();
  const passwordForm = useForm<PasswordFormData>();

  const newPassword = passwordForm.watch("newPassword", "");

  // Fetch profile on mount
  useEffect(() => {
    async function fetchProfile() {
      if (!session?.user?.id) return;

      try {
        const { data, error } = await api.get<UserProfile>(
          `/${session.user.id}/profile`
        );

        if (error) {
          setProfileError("Failed to load profile");
          return;
        }

        setProfile(data);
        profileForm.setValue("displayName", data.display_name || "");
      } catch {
        setProfileError("Failed to load profile");
      } finally {
        setIsLoadingProfile(false);
      }
    }

    if (!isPending && session) {
      fetchProfile();
    } else if (!isPending && !session) {
      setIsLoadingProfile(false);
    }
  }, [session, isPending, profileForm]);

  const onSaveProfile = async (data: ProfileFormData) => {
    if (!session?.user?.id) return;

    setIsSavingProfile(true);
    setProfileError(null);
    setProfileSuccess(null);

    try {
      const { data: updatedProfile, error } = await api.put<UserProfile>(
        `/${session.user.id}/profile`,
        { display_name: data.displayName }
      );

      if (error) {
        setProfileError(error.detail || "Failed to update profile");
        return;
      }

      setProfile(updatedProfile);
      setProfileSuccess("Profile updated successfully!");
    } catch {
      setProfileError("An unexpected error occurred");
    } finally {
      setIsSavingProfile(false);
    }
  };

  const onChangePassword = async (data: PasswordFormData) => {
    if (!session?.user?.id) return;

    setIsSavingPassword(true);
    setPasswordError(null);
    setPasswordSuccess(null);

    try {
      const { error } = await api.put<UserProfile>(
        `/${session.user.id}/profile`,
        {
          current_password: data.currentPassword,
          new_password: data.newPassword,
        }
      );

      if (error) {
        if (error.error_code === "INVALID_CREDENTIALS") {
          setPasswordError("Current password is incorrect");
        } else {
          setPasswordError(error.detail || "Failed to change password");
        }
        return;
      }

      setPasswordSuccess("Password changed successfully!");
      passwordForm.reset();
    } catch {
      setPasswordError("An unexpected error occurred");
    } finally {
      setIsSavingPassword(false);
    }
  };

  if (isPending || isLoadingProfile) {
    return (
      <div className="p-6 space-y-6">
        <div className="animate-pulse space-y-4">
          <div className="h-4 bg-neutral-200 dark:bg-neutral-700 rounded-lg w-1/4" />
          <div className="h-12 bg-neutral-200 dark:bg-neutral-700 rounded-xl" />
          <div className="h-4 bg-neutral-200 dark:bg-neutral-700 rounded-lg w-1/4" />
          <div className="h-12 bg-neutral-200 dark:bg-neutral-700 rounded-xl" />
        </div>
      </div>
    );
  }

  if (!session) {
    return (
      <div className="p-8 text-center">
        <div className="w-16 h-16 rounded-2xl bg-neutral-100 dark:bg-neutral-800 flex items-center justify-center mx-auto mb-4">
          <svg className="w-8 h-8 text-neutral-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
          </svg>
        </div>
        <h3 className="text-h4 font-display font-semibold text-neutral-900 dark:text-neutral-100 mb-2">
          Sign in required
        </h3>
        <p className="text-body-sm text-neutral-500 dark:text-neutral-400">
          Please sign in to view your profile.
        </p>
      </div>
    );
  }

  return (
    <div className="divide-y divide-neutral-100 dark:divide-neutral-800">
      {/* Account Information (Read-only) */}
      <section className="p-6">
        <h2 className="text-h4 font-display font-semibold text-neutral-900 dark:text-neutral-100 mb-4 flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-accent-100 dark:bg-accent-900/30 flex items-center justify-center">
            <svg className="w-4 h-4 text-accent-600 dark:text-accent-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
          </div>
          Account Information
        </h2>
        <dl className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div className="p-4 rounded-xl bg-neutral-50 dark:bg-neutral-800/50 border border-neutral-100 dark:border-neutral-800">
            <dt className="text-caption text-neutral-500 dark:text-neutral-400 mb-1">Email</dt>
            <dd className="text-body-sm font-medium text-neutral-900 dark:text-neutral-100">
              {profile?.email || session.user?.email}
            </dd>
          </div>
          <div className="p-4 rounded-xl bg-neutral-50 dark:bg-neutral-800/50 border border-neutral-100 dark:border-neutral-800">
            <dt className="text-caption text-neutral-500 dark:text-neutral-400 mb-1">Status</dt>
            <dd>
              {profile?.email_verified ? (
                <span className="inline-flex items-center gap-1.5 text-green-600 dark:text-green-400 text-body-sm font-medium">
                  <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                  Verified
                </span>
              ) : (
                <span className="inline-flex items-center gap-1.5 text-amber-600 dark:text-amber-400 text-body-sm font-medium">
                  <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                  </svg>
                  Not verified
                </span>
              )}
            </dd>
          </div>
          <div className="p-4 rounded-xl bg-neutral-50 dark:bg-neutral-800/50 border border-neutral-100 dark:border-neutral-800">
            <dt className="text-caption text-neutral-500 dark:text-neutral-400 mb-1">Member Since</dt>
            <dd className="text-body-sm font-medium text-neutral-900 dark:text-neutral-100">
              {profile?.created_at
                ? new Date(profile.created_at).toLocaleDateString("en-US", {
                    month: "long",
                    day: "numeric",
                    year: "numeric",
                  })
                : "—"}
            </dd>
          </div>
          <div className="p-4 rounded-xl bg-neutral-50 dark:bg-neutral-800/50 border border-neutral-100 dark:border-neutral-800">
            <dt className="text-caption text-neutral-500 dark:text-neutral-400 mb-1">Last Sign In</dt>
            <dd className="text-body-sm font-medium text-neutral-900 dark:text-neutral-100">
              {profile?.last_signin_at
                ? new Date(profile.last_signin_at).toLocaleString("en-US", {
                    month: "short",
                    day: "numeric",
                    year: "numeric",
                    hour: "numeric",
                    minute: "2-digit",
                  })
                : "—"}
            </dd>
          </div>
        </dl>
      </section>

      {/* Profile Settings */}
      <section className="p-6">
        <h2 className="text-h4 font-display font-semibold text-neutral-900 dark:text-neutral-100 mb-4 flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center">
            <svg className="w-4 h-4 text-blue-600 dark:text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
            </svg>
          </div>
          Profile Settings
        </h2>

        <form onSubmit={profileForm.handleSubmit(onSaveProfile)} className="space-y-4">
          {profileError && (
            <div className="flex items-start gap-3 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl">
              <svg className="w-5 h-5 text-error flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <p className="text-body-sm text-red-700 dark:text-red-400">{profileError}</p>
            </div>
          )}

          {profileSuccess && (
            <div className="flex items-start gap-3 p-4 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-xl">
              <svg className="w-5 h-5 text-green-600 dark:text-green-400 flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <p className="text-body-sm text-green-700 dark:text-green-400">{profileSuccess}</p>
            </div>
          )}

          <div className="space-y-2">
            <label
              htmlFor="displayName"
              className="text-body-sm font-medium text-neutral-700 dark:text-neutral-300"
            >
              Display Name
            </label>
            <input
              id="displayName"
              type="text"
              placeholder="Enter your display name"
              {...profileForm.register("displayName", {
                required: "Display name is required",
                minLength: { value: 2, message: "Display name must be at least 2 characters" },
              })}
              className="input-field"
            />
            {profileForm.formState.errors.displayName && (
              <p className="text-caption text-error">
                {profileForm.formState.errors.displayName.message}
              </p>
            )}
          </div>

          <button
            type="submit"
            disabled={isSavingProfile}
            className="btn-primary"
          >
            {isSavingProfile ? (
              <span className="flex items-center gap-2">
                <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                </svg>
                Saving...
              </span>
            ) : (
              "Save Profile"
            )}
          </button>
        </form>
      </section>

      {/* Change Password */}
      <section className="p-6">
        <h2 className="text-h4 font-display font-semibold text-neutral-900 dark:text-neutral-100 mb-4 flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-orange-100 dark:bg-orange-900/30 flex items-center justify-center">
            <svg className="w-4 h-4 text-orange-600 dark:text-orange-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
            </svg>
          </div>
          Change Password
        </h2>

        <form onSubmit={passwordForm.handleSubmit(onChangePassword)} className="space-y-4">
          {passwordError && (
            <div className="flex items-start gap-3 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl">
              <svg className="w-5 h-5 text-error flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <p className="text-body-sm text-red-700 dark:text-red-400">{passwordError}</p>
            </div>
          )}

          {passwordSuccess && (
            <div className="flex items-start gap-3 p-4 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-xl">
              <svg className="w-5 h-5 text-green-600 dark:text-green-400 flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <p className="text-body-sm text-green-700 dark:text-green-400">{passwordSuccess}</p>
            </div>
          )}

          <div className="space-y-2">
            <label
              htmlFor="currentPassword"
              className="text-body-sm font-medium text-neutral-700 dark:text-neutral-300"
            >
              Current Password
            </label>
            <input
              id="currentPassword"
              type="password"
              autoComplete="current-password"
              placeholder="Enter current password"
              {...passwordForm.register("currentPassword", {
                required: "Current password is required",
              })}
              className="input-field"
            />
            {passwordForm.formState.errors.currentPassword && (
              <p className="text-caption text-error">
                {passwordForm.formState.errors.currentPassword.message}
              </p>
            )}
          </div>

          <div className="space-y-2">
            <label
              htmlFor="newPassword"
              className="text-body-sm font-medium text-neutral-700 dark:text-neutral-300"
            >
              New Password
            </label>
            <input
              id="newPassword"
              type="password"
              autoComplete="new-password"
              placeholder="Enter new password"
              {...passwordForm.register("newPassword", {
                required: "New password is required",
                minLength: { value: 8, message: "Password must be at least 8 characters" },
                pattern: {
                  value: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$/,
                  message: "Password must include uppercase, lowercase, and number",
                },
              })}
              className="input-field"
            />
            {passwordForm.formState.errors.newPassword && (
              <p className="text-caption text-error">
                {passwordForm.formState.errors.newPassword.message}
              </p>
            )}
          </div>

          <div className="space-y-2">
            <label
              htmlFor="confirmPassword"
              className="text-body-sm font-medium text-neutral-700 dark:text-neutral-300"
            >
              Confirm New Password
            </label>
            <input
              id="confirmPassword"
              type="password"
              autoComplete="new-password"
              placeholder="Confirm new password"
              {...passwordForm.register("confirmPassword", {
                required: "Please confirm your password",
                validate: (value) => value === newPassword || "Passwords do not match",
              })}
              className="input-field"
            />
            {passwordForm.formState.errors.confirmPassword && (
              <p className="text-caption text-error">
                {passwordForm.formState.errors.confirmPassword.message}
              </p>
            )}
          </div>

          <button
            type="submit"
            disabled={isSavingPassword}
            className="btn-primary"
          >
            {isSavingPassword ? (
              <span className="flex items-center gap-2">
                <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                </svg>
                Changing Password...
              </span>
            ) : (
              "Change Password"
            )}
          </button>
        </form>
      </section>
    </div>
  );
}
