/**
 * Streaming client for Server-Sent Events (SSE) chat responses.
 */
import { getAccessToken } from "./auth";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface StreamChunk {
  type: "token" | "tool_call" | "done" | "error";
  content?: string;
  tool?: string;
  result?: any;
  tokens_used?: number;
  message?: string;
}

/**
 * Stream chat response from the backend via SSE.
 *
 * @param conversationId - ID of the conversation
 * @param message - User message content
 * @param onToken - Callback for each token received
 * @param onComplete - Callback when streaming completes
 * @param onError - Callback for errors
 */
export async function streamChatResponse(
  conversationId: number,
  message: string,
  onToken: (token: string) => void,
  onComplete: (fullMessage: string) => void,
  onError: (error: Error) => void
): Promise<void> {
  try {
    const token = await getAccessToken();

    if (!token) {
      throw new Error("Not authenticated");
    }

    const response = await fetch(
      `${API_URL}/api/conversations/${conversationId}/stream`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ content: message }),
      }
    );

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`HTTP ${response.status}: ${errorText}`);
    }

    const reader = response.body?.getReader();
    const decoder = new TextDecoder();
    let fullMessage = "";

    if (!reader) {
      throw new Error("No response body");
    }

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      const chunk = decoder.decode(value);
      const lines = chunk.split("\n");

      for (const line of lines) {
        if (line.startsWith("data: ")) {
          const data = line.slice(6);

          if (data === "[DONE]") {
            onComplete(fullMessage);
            return;
          }

          try {
            const parsed: StreamChunk = JSON.parse(data);

            if (parsed.type === "token" && parsed.content) {
              fullMessage += parsed.content;
              onToken(parsed.content);
            } else if (parsed.type === "tool_call") {
              // Tool call executed - could show in UI
              console.log("Tool executed:", parsed.tool, parsed.result);
            } else if (parsed.type === "done") {
              onComplete(fullMessage);
              return;
            } else if (parsed.type === "error") {
              throw new Error(parsed.message || "Streaming error");
            }
          } catch (e) {
            // Skip invalid JSON lines
            if (e instanceof SyntaxError) {
              continue;
            }
            throw e;
          }
        }
      }
    }

    onComplete(fullMessage);
  } catch (error) {
    onError(error as Error);
  }
}
