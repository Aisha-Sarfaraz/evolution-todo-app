/**
 * T044: API client module for backend communication.
 *
 * Centralized HTTP client for interacting with the Phase III FastAPI backend.
 */

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8002/api";
const API_TIMEOUT = Number(process.env.NEXT_PUBLIC_API_TIMEOUT) || 30000;

interface ChatMessage {
  conversation_id?: string;
  message: string;
  timezone?: string;
}

interface ChatResponse {
  conversation_id: string;
  response: string;
  tool_calls: Array<{
    tool: string;
    input: Record<string, unknown>;
    output: Record<string, unknown>;
  }>;
}

interface Conversation {
  id: string;
  title: string | null;
  last_message_preview: string | null;
  updated_at: string;
}

class ApiClient {
  private baseUrl: string;
  private authToken: string | null = null;

  constructor(baseUrl: string = API_URL) {
    this.baseUrl = baseUrl;
  }

  setAuthToken(token: string) {
    this.authToken = token;
  }

  private async request<T>(
    path: string,
    options: RequestInit = {}
  ): Promise<T> {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), API_TIMEOUT);

    try {
      const response = await fetch(`${this.baseUrl}${path}`, {
        ...options,
        signal: controller.signal,
        headers: {
          "Content-Type": "application/json",
          ...(this.authToken
            ? { Authorization: `Bearer ${this.authToken}` }
            : {}),
          ...options.headers,
        },
      });

      if (!response.ok) {
        const error = await response.json().catch(() => ({
          detail: "Request failed",
        }));
        throw new ApiError(response.status, error.detail || "Request failed");
      }

      return response.json();
    } finally {
      clearTimeout(timeout);
    }
  }

  async sendMessage(
    userId: string,
    payload: ChatMessage
  ): Promise<ChatResponse> {
    return this.request<ChatResponse>(`/${userId}/chat`, {
      method: "POST",
      body: JSON.stringify(payload),
    });
  }

  async getConversations(userId: string): Promise<{ conversations: Conversation[] }> {
    return this.request(`/${userId}/conversations`);
  }

  async getMessages(
    userId: string,
    conversationId: string,
    limit = 50,
    before?: string
  ) {
    const params = new URLSearchParams({ limit: String(limit) });
    if (before) params.set("before", before);
    return this.request(
      `/${userId}/conversations/${conversationId}/messages?${params}`
    );
  }

  async deleteConversation(
    userId: string,
    conversationId: string
  ): Promise<{ deleted: boolean }> {
    return this.request(`/${userId}/conversations/${conversationId}`, {
      method: "DELETE",
    });
  }
}

export class ApiError extends Error {
  constructor(
    public status: number,
    message: string
  ) {
    super(message);
    this.name = "ApiError";
  }
}

export const apiClient = new ApiClient();
export type { ChatMessage, ChatResponse, Conversation };
