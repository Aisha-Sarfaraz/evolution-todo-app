/**
 * T075: Frontend unit test for NotificationBanner component.
 */
import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import React from "react";

describe("NotificationBanner", () => {
  it("renders when push permission denied", async () => {
    const { NotificationBanner } = await import(
      "@/components/chat/NotificationBanner"
    );
    render(<NotificationBanner show={true} onDismiss={vi.fn()} />);

    expect(
      screen.getByText(/notification/i)
    ).toBeInTheDocument();
  });

  it("calls onDismiss when close button clicked", async () => {
    const { NotificationBanner } = await import(
      "@/components/chat/NotificationBanner"
    );
    const onDismiss = vi.fn();
    render(<NotificationBanner show={true} onDismiss={onDismiss} />);

    const closeBtn = screen.getByRole("button");
    fireEvent.click(closeBtn);
    expect(onDismiss).toHaveBeenCalled();
  });

  it("does not render when show is false", async () => {
    const { NotificationBanner } = await import(
      "@/components/chat/NotificationBanner"
    );
    const { container } = render(
      <NotificationBanner show={false} onDismiss={vi.fn()} />
    );

    expect(container.children.length).toBe(0);
  });
});
