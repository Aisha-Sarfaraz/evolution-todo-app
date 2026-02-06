/**
 * ChatKit-compatible API route that proxies to the Hugging Face backend.
 * Passes through the raw request body without modification.
 */

import { NextRequest } from "next/server";

const BACKEND_URL =
  process.env["CHAT_BACKEND_URL"] ||
  process.env["NEXT_PUBLIC_CHAT_API_URL"] ||
  "https://aishayousuf-todo-chatbot-api.hf.space";

export async function POST(request: NextRequest) {
  try {
    // Read raw body to pass through as-is
    const rawBody = await request.text();

    // Try to inject user_id if body is JSON
    let forwardBody = rawBody;
    let userId = "anonymous";
    try {
      const parsed = JSON.parse(rawBody);
      const authHeader = request.headers.get("authorization");
      userId =
        parsed.user_id ||
        (authHeader?.startsWith("Bearer ") ? authHeader.slice(7) : "anonymous");
      parsed.user_id = userId;
      forwardBody = JSON.stringify(parsed);
    } catch {
      // Not JSON - forward as-is
    }

    console.log("[/api/chat] Forwarding to:", `${BACKEND_URL}/api/chatkit`);
    console.log("[/api/chat] Body preview:", forwardBody.slice(0, 500));

    const response = await fetch(`${BACKEND_URL}/api/chatkit`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${userId}`,
      },
      body: forwardBody,
    });

    console.log("[/api/chat] Backend status:", response.status);

    if (!response.ok) {
      const errorText = await response.text();
      console.error("[/api/chat] Backend error:", errorText);
      return new Response(errorText, {
        status: response.status,
        headers: { "Content-Type": "application/json" },
      });
    }

    // Pass through the backend response with its original content type
    const contentType = response.headers.get("Content-Type") || "application/json";

    if (contentType.includes("text/event-stream")) {
      // Stream the SSE response back to the client
      const { readable, writable } = new TransformStream();
      const writer = writable.getWriter();

      const reader = response.body?.getReader();
      if (reader) {
        (async () => {
          try {
            while (true) {
              const { done, value } = await reader.read();
              if (done) break;
              await writer.write(value);
            }
          } finally {
            await writer.close();
          }
        })();
      }

      return new Response(readable, {
        headers: {
          "Content-Type": "text/event-stream",
          "Cache-Control": "no-cache",
          Connection: "keep-alive",
        },
      });
    } else {
      // Non-streaming response (threads.list, threads.get_by_id, etc.)
      const body = await response.text();
      return new Response(body, {
        status: response.status,
        headers: { "Content-Type": contentType },
      });
    }
  } catch (error) {
    console.error("[/api/chat] Error:", error);
    return new Response(
      JSON.stringify({ error: "Internal server error" }),
      { status: 500, headers: { "Content-Type": "application/json" } }
    );
  }
}
