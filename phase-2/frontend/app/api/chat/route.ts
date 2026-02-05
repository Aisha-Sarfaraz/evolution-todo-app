/**
 * ChatKit-compatible API route that proxies to our Hugging Face backend.
 * This server-side route allows ChatKit to work without browser-side issues.
 */

import { NextRequest } from "next/server";

const BACKEND_URL = process.env["CHAT_BACKEND_URL"] || process.env["NEXT_PUBLIC_CHAT_API_URL"] || "https://aishayousuf-todo-chatbot-api.hf.space";

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();

    // Get user_id from the request body or authorization header
    const authHeader = request.headers.get("authorization");
    const userId = body.user_id || (authHeader?.startsWith("Bearer ") ? authHeader.slice(7) : "anonymous");

    // Forward to our backend
    const response = await fetch(`${BACKEND_URL}/api/chatkit`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${userId}`,
      },
      body: JSON.stringify({
        ...body,
        user_id: userId,
      }),
    });

    if (!response.ok) {
      return new Response(
        JSON.stringify({ error: "Backend request failed" }),
        { status: response.status, headers: { "Content-Type": "application/json" } }
      );
    }

    // Stream the SSE response back
    const { readable, writable } = new TransformStream();
    const writer = writable.getWriter();

    // Pipe the response
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
        "Connection": "keep-alive",
      },
    });
  } catch (error) {
    console.error("Chat API error:", error);
    return new Response(
      JSON.stringify({ error: "Internal server error" }),
      { status: 500, headers: { "Content-Type": "application/json" } }
    );
  }
}
