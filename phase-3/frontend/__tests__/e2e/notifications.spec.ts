/**
 * T103: E2E test — Notification banner behavior.
 *
 * Tests the notification permission banner display and dismissal.
 * Note: Actual push notification testing requires browser permission mocking.
 */
import { test, expect } from "@playwright/test";

test.describe("Notification Banner E2E", () => {
  test("should show notification banner when permission is denied", async ({
    page,
    context,
  }) => {
    // Mock Notification API to return 'denied'
    await context.grantPermissions([], { origin: "http://localhost:3000" });
    await page.addInitScript(() => {
      Object.defineProperty(window, "Notification", {
        value: {
          permission: "denied",
          requestPermission: () => Promise.resolve("denied"),
        },
        writable: true,
      });
    });

    await page.goto("/chat");

    // Banner should be visible
    const banner = page.getByText(/enable notifications/i);
    await expect(banner).toBeVisible({ timeout: 5000 });
  });

  test("should dismiss notification banner on click", async ({
    page,
    context,
  }) => {
    await context.grantPermissions([], { origin: "http://localhost:3000" });
    await page.addInitScript(() => {
      Object.defineProperty(window, "Notification", {
        value: {
          permission: "denied",
          requestPermission: () => Promise.resolve("denied"),
        },
        writable: true,
      });
    });

    await page.goto("/chat");

    const banner = page.getByText(/enable notifications/i);
    await expect(banner).toBeVisible({ timeout: 5000 });

    // Dismiss
    await page.getByLabel("Dismiss notification banner").click();
    await expect(banner).not.toBeVisible();
  });

  test("should not show banner when notification permission is granted", async ({
    page,
  }) => {
    await page.addInitScript(() => {
      Object.defineProperty(window, "Notification", {
        value: {
          permission: "granted",
          requestPermission: () => Promise.resolve("granted"),
        },
        writable: true,
      });
      // Mock service worker
      if (!navigator.serviceWorker) {
        Object.defineProperty(navigator, "serviceWorker", {
          value: {
            register: () => Promise.resolve({ pushManager: { getSubscription: () => Promise.resolve(null) } }),
            ready: Promise.resolve({ pushManager: { getSubscription: () => Promise.resolve(null) } }),
          },
        });
      }
    });

    await page.goto("/chat");

    const banner = page.getByText(/enable notifications/i);
    await expect(banner).not.toBeVisible({ timeout: 3000 });
  });
});
