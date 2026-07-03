import { Card } from "../components/ui/Card";
import { Panel } from "../components/ui/Panel";
import { SectionTitle } from "../components/ui/SectionTitle";

import { useSystemState } from "../state/systemState";
import { useLanguageStore } from "../state/languageState";

export default function DiagnosticsPage() {
  const lang = useLanguageStore((s) => s.language);

  const apiStatus = useSystemState((s) => s.apiStatus);
  const systemHealth = useSystemState((s) => s.systemHealth);
  const backendVersion = useSystemState((s) => s.backendVersion);
  const heartbeat = useSystemState((s) => s.lastHeartbeat);
  const sseStatus = useSystemState((s) => s.sseStatus);

  return (
    <div>
      <SectionTitle title={lang === "zh" ? "系统诊断" : "Diagnostics"} />

      <Panel>
        <h3>{lang === "zh" ? "API 状态" : "API Status"}</h3>
        <p>{apiStatus}</p>
      </Panel>

      <Panel>
        <h3>{lang === "zh" ? "系统健康" : "System Health"}</h3>
        <p>{systemHealth}</p>
      </Panel>

      <Panel>
        <h3>{lang === "zh" ? "后端版本" : "Backend Version"}</h3>
        <p>{backendVersion ?? "N/A"}</p>
      </Panel>

      <Panel>
        <h3>{lang === "zh" ? "心跳时间" : "Heartbeat"}</h3>
        <p>{heartbeat ? new Date(heartbeat).toLocaleString() : "N/A"}</p>
      </Panel>

      <Panel>
        <h3>{lang === "zh" ? "SSE 状态" : "SSE Status"}</h3>
        <p>{sseStatus}</p>
      </Panel>

      <Card>
        <h4>{lang === "zh" ? "说明" : "Notes"}</h4>
        <p>
          {lang === "zh"
            ? "此页面显示系统运行状态、API 连接情况、后端版本和心跳信息。"
            : "This page shows system runtime status, API connectivity, backend version, and heartbeat information."}
        </p>
      </Card>
    </div>
  );
}
