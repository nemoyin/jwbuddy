import { useState, useCallback, useRef } from "react";
import { streamChat, createSession } from "../api/client";

export interface ChatMessage {
  id: string;
  role: "user" | "assistant" | "tool";
  content: string;
  data?: unknown;
  format?: string;
}

export function useChat() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [loading, setLoading] = useState(false);
  const sessionIdRef = useRef<string>("");

  const sendMessage = useCallback(async (text: string) => {
    if (!sessionIdRef.current) {
      const session = await createSession();
      sessionIdRef.current = session.id;
    }

    const userMsg: ChatMessage = {
      id: Date.now().toString(),
      role: "user",
      content: text,
    };
    setMessages(prev => [...prev, userMsg]);
    setLoading(true);

    try {
      let assistantContent = "";
      const assistantId = (Date.now() + 1).toString();

      for await (const event of streamChat(sessionIdRef.current, text)) {
        if (event.type === "text") {
          assistantContent += event.content || "";
          setMessages(prev => {
            const next = [...prev];
            const last = next[next.length - 1];
            if (last?.id === assistantId) {
              last.content = assistantContent;
            } else {
              next.push({ id: assistantId, role: "assistant", content: assistantContent, format: "markdown" });
            }
            return [...next];
          });
        } else if (event.type === "tool_result") {
          setMessages(prev => [...prev, {
            id: Date.now().toString(),
            role: "tool",
            content: "",
            data: event.data,
            format: (event.format as string) || "table",
          }]);
        }
      }
    } finally {
      setLoading(false);
    }
  }, []);

  return { messages, loading, sendMessage };
}
