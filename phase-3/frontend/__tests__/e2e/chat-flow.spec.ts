/**
 * T101: E2E test — Chat flow (create task via NL).
 *
 * Tests the full user journey: sign in → send message → see AI response
 * with tool call confirmation → verify task created.
 */
import { test, expect } from "@playwright/test";

test.describe("Chat Flow E2E", () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to chat page (assumes auth session set via storage state)
    await page.goto("/chat");
  });

  test("should display chat interface after auth", async ({ page }) => {
    await expect(page.getByText("Todo Assistant")).toBeVisible();
    await expect(page.getByRole("textbox")).toBeVisible();
  });

  test("should send a message and receive AI response", async ({ page }) => {
    const input = page.getByRole("textbox");
    await input.fill("Create a task called Buy groceries with high priority");
    await input.press("Enter");

    // Wait for assistant response (may take several seconds with real LLM)
    const response = page.locator('[data-role="assistant"]').first();
    await expect(response).toBeVisible({ timeout: 30000 });

    // Response should mention the task creation
    await expect(response).toContainText(/created|buy groceries/i);
  });

  test("should show tool call confirmation for task creation", async ({
    page,
  }) => {
    const input = page.getByRole("textbox");
    await input.fill("Add a task: Clean the kitchen");
    await input.press("Enter");

    // Wait for tool call display
    const toolCall = page.locator("[data-testid='tool-call']").first();
    await expect(toolCall).toBeVisible({ timeout: 30000 });
  });

  test("should list tasks after creation", async ({ page }) => {
    const input = page.getByRole("textbox");

    // Create a task first
    await input.fill("Create a task: Test E2E task");
    await input.press("Enter");
    await page.waitForTimeout(5000);

    // List tasks
    await input.fill("Show my tasks");
    await input.press("Enter");

    const response = page.locator('[data-role="assistant"]').last();
    await expect(response).toBeVisible({ timeout: 30000 });
    await expect(response).toContainText(/test e2e task/i);
  });
});
