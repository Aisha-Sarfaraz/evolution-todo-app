/**
 * T076: Frontend unit test for push subscription logic.
 */
import { describe, it, expect, vi, beforeEach } from "vitest";

describe("Push Subscription", () => {
  beforeEach(() => {
    // Mock the Notification API
    Object.defineProperty(global, "Notification", {
      value: {
        permission: "default",
        requestPermission: vi.fn().mockResolvedValue("granted"),
      },
      writable: true,
    });

    // Mock navigator.serviceWorker
    Object.defineProperty(global.navigator, "serviceWorker", {
      value: {
        ready: Promise.resolve({
          pushManager: {
            subscribe: vi.fn().mockResolvedValue({
              endpoint: "https://push.example.com/sub/123",
              toJSON: () => ({
                endpoint: "https://push.example.com/sub/123",
                keys: {
                  p256dh: "test-p256dh-key",
                  auth: "test-auth-key",
                },
              }),
            }),
            getSubscription: vi.fn().mockResolvedValue(null),
          },
        }),
        register: vi.fn().mockResolvedValue({}),
      },
      writable: true,
      configurable: true,
    });
  });

  it("module exports subscribeToPush function", async () => {
    const pushModule = await import("@/lib/push");
    expect(typeof pushModule.subscribeToPush).toBe("function");
  });

  it("module exports requestNotificationPermission function", async () => {
    const pushModule = await import("@/lib/push");
    expect(typeof pushModule.requestNotificationPermission).toBe("function");
  });
});
