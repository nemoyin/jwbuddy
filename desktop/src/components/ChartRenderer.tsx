import ReactEChartsCore from "echarts-for-react";

interface ChartConfig {
  chart_type: string;
  title: string;
  option: Record<string, unknown>;
}

interface Props {
  config: ChartConfig;
  height?: number;
}

export function ChartRenderer({ config, height = 400 }: Props) {
  if (!config || !config.option) {
    return <p style={{ color: "#999" }}>图表配置为空</p>;
  }

  return (
    <div style={{ padding: 16, background: "#fff", borderRadius: 8 }}>
      <ReactEChartsCore
        option={{
          title: { text: config.title, left: "center" },
          tooltip: { trigger: "axis" },
          ...config.option,
        }}
        style={{ height }}
        notMerge
        lazyUpdate
      />
    </div>
  );
}
