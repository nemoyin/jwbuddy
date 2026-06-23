const API_BASE = "http://localhost:8000";

export interface SessionData {
  id: string;
  title: string;
  created_at: string;
  message_count: number;
}

export async function createSession(title = "新会话"): Promise<SessionData> {
  const resp = await fetch(`${API_BASE}/sessions`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ title }),
  });
  return resp.json();
}

export async function listSessions(): Promise<SessionData[]> {
  const resp = await fetch(`${API_BASE}/sessions`);
  return resp.json();
}

// Use POST-based SSE for longer messages
export async function* streamChat(
  sessionId: string,
  message: string
): AsyncGenerator<{ type: string; content?: string; data?: unknown; format?: string }> {
  const resp = await fetch(`${API_BASE}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ session_id: sessionId, message }),
  });

  if (!resp.body) return;

  const reader = resp.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n");
    buffer = lines.pop() || "";

    for (const line of lines) {
      if (line.startsWith("data: ")) {
        try {
          yield JSON.parse(line.slice(6));
        } catch { /* skip malformed */ }
      }
    }
  }
}
