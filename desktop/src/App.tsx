import { useState } from "react";
import { Layout, Typography } from "antd";

const { Header, Content, Sider } = Layout;
const { Title } = Typography;

function App() {
  const [sessions, setSessions] = useState<{ id: string; title: string }[]>([]);

  return (
    <Layout style={{ height: "100vh" }}>
      <Sider width={280} theme="light" style={{ borderRight: "1px solid #f0f0f0" }}>
        <div style={{ padding: 16 }}>
          <Title level={4} style={{ margin: 0 }}>JWBuddy</Title>
        </div>
      </Sider>
      <Layout>
        <Content style={{ display: "flex", flexDirection: "column", height: "100%" }}>
          <div style={{ flex: 1, padding: 24, overflow: "auto" }}>
            <p style={{ color: "#999", textAlign: "center", marginTop: 200 }}>
              欢迎使用 JWBuddy — 纪检监察智能助手
            </p>
          </div>
        </Content>
      </Layout>
    </Layout>
  );
}

export default App;
