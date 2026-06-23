import { useState } from "react";
import { Input, Spin } from "antd";
import { SendOutlined } from "@ant-design/icons";
import { MessageBubble } from "./MessageBubble";
import { useChat } from "../hooks/useChat";

export function ChatPanel() {
  const [input, setInput] = useState("");
  const { messages, loading, sendMessage } = useChat();

  const handleSend = () => {
    if (!input.trim() || loading) return;
    sendMessage(input.trim());
    setInput("");
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100%" }}>
      <div style={{ flex: 1, overflow: "auto", padding: 16 }}>
        {messages.map(msg => (
          <MessageBubble key={msg.id} message={msg} />
        ))}
        {loading && <Spin style={{ display: "block", margin: "16px auto" }} />}
      </div>
      <div style={{ padding: "8px 16px", borderTop: "1px solid #f0f0f0" }}>
        <Input.Search
          value={input}
          onChange={e => setInput(e.target.value)}
          onSearch={handleSend}
          placeholder="输入你的问题..."
          enterButton={<SendOutlined />}
          size="large"
          loading={loading}
        />
      </div>
    </div>
  );
}
