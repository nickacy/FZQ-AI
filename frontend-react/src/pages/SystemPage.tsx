import { Card } from "../components/ui/Card";
import { Panel } from "../components/ui/Panel";
import { SectionTitle } from "../components/ui/SectionTitle";

import { useSystemState } from "../state/systemState";
import { useLanguageStore } from "../state/languageState";
import { useThemeState } from "../state/themeState";

export default function SystemPage() {
  const lang = useLanguageStore((s) => s.language);

  // Theme is an object → must render a field
  const theme = useThemeState((s) => s.theme);

  const systemVersion = useSystemState((s) => s.systemVersion);
  const backendVersion = useSystemState((s) => s.backendVersion);

  const apiStatus = useSystemState((s) => s.apiStatus);
  const systemHealth = useSystemState((s) => s.systemHealth);

  const lastHeartbeat = useSystemState((s) => s.lastHeartbeat);
  const sseStatus = useSystemState((s) => s.sseStatus);

  const featureFlags = useSystemState((s) => s.featureFlags);

  return (
    <div>
      <SectionTitle title={lang === "zh" ? "系统总览" : "System Overview"} />

      {/* Versions */}
      <Panel>
        <h3>{lang === "zh" ? "版本信息" : "Version Info"}</h3>
        <p>Frontend Version: {systemVersion}</p>
        <p>Backend Version: {backendVersion || "N/A"}</p>
      </Panel>

      {/* Status */}
      <Panel>
        <h3>{lang === "zh" ? "系统状态" : "System Status"}</h3>
        <p>API Status: {apiStatus}</p>
        <p>System Health: {systemHealth}</p>
        <p>
          Heartbeat:{" "}
          {lastHeartbeat ? new Date(lastHeartbeat).toLocaleString() : "N/A"}
        </p>
        <p>SSE Status: {sseStatus}</p>
      </Panel>

      {/* Language & Theme */}
      <Panel>
        <h3>{lang === "zh" ? "界面设置" : "UI Settings"}</h3>
        <p>Language: {lang}</p>
        <p>Theme Mode: {theme.mode}</p> {/* ← FIXED */}
      </Panel>

      {/* Feature Flags */}
      <Card>
        <h3>{lang === "zh" ? "功能开关" : "Feature Flags"}</h3>
        <ul>
          <li>SSE: {featureFlags.enableSSE ? "ON" : "OFF"}</li>
          <li>Multi-Agent: {featureFlags.enableMultiAgent ? "ON" : "OFF"}</li>
          <li>Advanced Schema: {featureFlags.enableAdvancedSchema ? "ON" : "OFF"}</li>
          <li>Dynamic Theme: {featureFlags.enableDynamicTheme ? "ON" : "OFF"}</li>
        </ul>
      </Card>
    </div>
  );
}
