/**
 * T102: E2E test — Conversation CRUD.
 *
 * Tests conversation creation, switching, and deletion via sidebar.
 */
import { test, expect } from "@playwright/test";

test.describe("Conversation CRUD E2E", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/chat");
  });

  test("should create a new conversation on first message", async ({
    page,
  }) => {
    const input = page.getByRole("textbox");
    await input.fill("Hello, create a task for me");
    await input.press("Enter");

    // Wait for response
    await page.waitForTimeout(5000);

    // Sidebar should show the new conversation
    const sidebar = page.locator("[data-testid='conversation-list']");
    await expect(sidebar.locator("[data-testid='conversation-item']")).toHaveCount(1, { timeout: 10000 });
  });

  test("should switch between conversations", async ({ page }) => {
    const input = page.getByRole("textbox");

    // Create first conversation
    await input.fill("First conversation message");
    await input.press("Enter");
    await page.waitForTimeout(5000);

    // Start new chat
    await page.getByRole("button", { name: /new chat/i }).click();

    // Create second conversation
    await input.fill("Second conversation message");
    await input.press("Enter");
    await page.waitForTimeout(5000);

    // Should have 2 conversations in sidebar
    const items = page.locator("[data-testid='conversation-item']");
    await expect(items).toHaveCount(2, { timeout: 10000 });

    // Click first conversation
    await items.first().click();

    // Should see the first conversation's messages
    const messages = page.locator('[data-role="user"]');
    await expect(messages.first()).toContainText("First conversation");
  });

  test("should toggle sidebar visibility", async ({ page }) => {
    const sidebar = page.locator("[data-testid='conversation-list']");
    await expect(sidebar).toBeVisible();

    // Toggle sidebar
    await page.getByLabel("Toggle sidebar").click();
    await expect(sidebar).not.toBeVisible();

    // Toggle back
    await page.getByLabel("Toggle sidebar").click();
    await expect(sidebar).toBeVisible();
  });
});
