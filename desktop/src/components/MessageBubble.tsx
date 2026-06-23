import { Typography, Card, Table, Tag } from "antd";
import { UserOutlined, RobotOutlined, ToolOutlined } from "@ant-design/icons";
import type { ChatMessage } from "../hooks/useChat";

interface Props {
  message: ChatMessage;
}

export function MessageBubble({ message }: Props) {
  const isUser = message.role === "user";
  const isTool = message.role === "tool";

  const icon = isUser ? <UserOutlined /> : isTool ? <ToolOutlined /> : <RobotOutlined />;
  const color = isUser ? "#e6f4ff" : isTool ? "#f6ffed" : "#fff";

  return (
    <div style={{ display: "flex", gap: 12, marginBottom: 16, flexDirection: isUser ? "row-reverse" : "row" }}>
      <Tag style={{ borderRadius: "50%", width: 32, height: 32, display: "flex", alignItems: "center", justifyContent: "center" }}>
        {icon}
      </Tag>
      <Card
        style={{
          maxWidth: "70%",
          background: color,
          borderRadius: 12,
        }}
        styles={{ body: { padding: "8px 16px" } }}
      >
        {message.content && <Typography.Paragraph style={{ margin: 0 }}>{message.content}</Typography.Paragraph>}
        {message.format === "table" && message.data != null && (
          <Table
            dataSource={Array.isArray(message.data) ? (message.data as Record<string, unknown>[]).slice(0, 20) : []}
            columns={Array.isArray(message.data) && (message.data as Record<string, unknown>[]).length > 0
              ? Object.keys((message.data as Record<string, unknown>[])[0]).map(k => ({ title: k, dataIndex: k, key: k }))
              : []}
            size="small"
            pagination={false}
          />
        )}
      </Card>
    </div>
  );
}
