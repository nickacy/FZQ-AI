import { Card } from "../components/ui/Card";
import { Panel } from "../components/ui/Panel";
import { SectionTitle } from "../components/ui/SectionTitle";

import { useSystemState } from "../state/systemState";
import { useLanguageStore } from "../state/languageState";
import { useThemeState } from "../state/themeState";
import { useOutputState } from "../state/outputState";

export default function DebugPage() {
  const lang = useLanguageStore((s) => s.language);
  const theme = useThemeState((s) => s.theme);

  const systemState = useSystemState();
  const outputState = useOutputState();

  return (
    <div>
      <SectionTitle title={lang === "zh" ? "调试中心" : "Debug Center"} />

      {/* System State */}
      <Panel>
        <h3>{lang === "zh" ? "系统状态" : "System State"}</h3>
        <pre
          style={{
            background: "var(--bg-secondary)",
            padding: "12px",
            borderRadius: "6px",
            overflowX: "auto",
          }}
        >
          {JSON.stringify(systemState, null, 2)}
        </pre>
      </Panel>

      {/* Language State */}
      <Panel>
        <h3>{lang === "zh" ? "语言状态" : "Language State"}</h3>
        <pre
          style={{
            background: "var(--bg-secondary)",
            padding: "12px",
            borderRadius: "6px",
            overflowX: "auto",
          }}
        >
          {JSON.stringify({ language: lang }, null, 2)}
        </pre>
      </Panel>

      {/* Theme State */}
      <Panel>
        <h3>{lang === "zh" ? "主题状态" : "Theme State"}</h3>
        <pre
          style={{
            background: "var(--bg-secondary)",
            padding: "12px",
            borderRadius: "6px",
            overflowX: "auto",
          }}
        >
          {JSON.stringify(theme, null, 2)}
        </pre>
      </Panel>

      {/* Output Cards */}
      <Card>
        <h3>{lang === "zh" ? "输出卡片状态" : "Output Cards State"}</h3>
        <pre
          style={{
            background: "var(--bg-secondary)",
            padding: "12px",
            borderRadius: "6px",
            overflowX: "auto",
          }}
        >
          {JSON.stringify(outputState.cards, null, 2)}
        </pre>
      </Card>
    </div>
  );
}
