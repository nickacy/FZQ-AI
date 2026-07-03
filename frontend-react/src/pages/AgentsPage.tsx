import { useLanguageStore } from "../state/languageState";
import { useSystemState } from "../state/systemState";

import { Card } from "../components/ui/Card";
import { Panel } from "../components/ui/Panel";
import { SectionTitle } from "../components/ui/SectionTitle";

interface AgentInfo {
  id: string;
  name: { zh: string; en: string };
  description: { zh: string; en: string };
  version: string;
  status: "active" | "idle" | "error";
  capabilities: string[];
}

const mockAgents: AgentInfo[] = [
  {
    id: "agent-policy",
    name: { zh: "政策分析智能体", en: "Policy Analysis Agent" },
    description: {
      zh: "负责政策矩阵、跨文明政策比较、战略推演。",
      en: "Handles policy matrices, cross-civilization comparisons, and strategic simulations."
    },
    version: "1.4.2",
    status: "active",
    capabilities: ["policy_matrix", "simulation", "cross_civilization"]
  },
  {
    id: "agent-data",
    name: { zh: "数据智能体", en: "Data Intelligence Agent" },
    description: {
      zh: "负责数据清洗、结构化、表格生成、图表生成。",
      en: "Handles data cleaning, structuring, table generation, and chart generation."
    },
    version: "2.1.0",
    status: "idle",
    capabilities: ["table", "chart", "data_cleaning"]
  },
  {
    id: "agent-language",
    name: { zh: "语言智能体", en: "Language Agent" },
    description: {
      zh: "负责双语生成、翻译、跨文明叙事风格转换。",
      en: "Handles bilingual generation, translation, and cross-civilization narrative transformation."
    },
    version: "3.0.1",
    status: "active",
    capabilities: ["translation", "bilingual", "narrative_style"]
  }
];

export default function AgentsPage() {
  const lang = useLanguageStore((s) => s.language);
  const featureFlags = useSystemState((s) => s.featureFlags);

  if (!featureFlags.enableMultiAgent) {
    return (
      <Panel>
        <h3>{lang === "zh" ? "多智能体功能已关闭" : "Multi-Agent Feature Disabled"}</h3>
        <p>
          {lang === "zh"
            ? "请在系统设置中启用多智能体功能。"
            : "Enable multi-agent mode in system settings."}
        </p>
      </Panel>
    );
  }

  return (
    <div>
      <SectionTitle title={lang === "zh" ? "智能体管理中心" : "Agents Center"} />

      {mockAgents.map((agent) => (
        <Card key={agent.id}>
          <h3>{agent.name[lang]}</h3>
          <p>{agent.description[lang]}</p>

          <p>
            <strong>{lang === "zh" ? "版本：" : "Version:"}</strong> {agent.version}
          </p>

          <p>
            <strong>{lang === "zh" ? "状态：" : "Status:"}</strong>{" "}
            {agent.status === "active"
              ? lang === "zh"
                ? "活跃"
                : "Active"
              : agent.status === "idle"
              ? lang === "zh"
                ? "空闲"
                : "Idle"
              : lang === "zh"
              ? "错误"
              : "Error"}
          </p>

          <p>
            <strong>{lang === "zh" ? "能力：" : "Capabilities:"}</strong>
          </p>
          <ul>
            {agent.capabilities.map((cap) => (
              <li key={cap}>{cap}</li>
            ))}
          </ul>
        </Card>
      ))}
    </div>
  );
}
