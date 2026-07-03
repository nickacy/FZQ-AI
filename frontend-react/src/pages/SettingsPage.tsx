import { SectionTitle } from "../components/ui/SectionTitle";
import { Panel } from "../components/ui/Panel";
import { Card } from "../components/ui/Card";

import { useLanguageStore } from "../state/languageState";
import { useThemeState } from "../state/themeState";
import { useSystemState } from "../state/systemState";

export default function SettingsPage() {
  const lang = useLanguageStore((s) => s.language);
  const setLanguage = useLanguageStore((s) => s.setLanguage);

  // theme 是一个对象，比如 { mode: "light", ... }
  const theme = useThemeState((s) => s.theme);
  const setTheme = useThemeState((s) => s.setTheme); // 接受 ThemeMode: "light" | "dark"

  const featureFlags = useSystemState((s) => s.featureFlags);
  const setFeatureFlags = useSystemState((s) => s.setFeatureFlags);

  const resetSystem = useSystemState((s) => s.resetSystem);

  return (
    <div>
      <SectionTitle title={lang === "zh" ? "系统设置" : "Settings"} />

      {/* Language */}
      <Panel>
        <h3>{lang === "zh" ? "语言设置" : "Language"}</h3>
        <button
          style={{
            marginRight: "10px",
            padding: "8px 12px",
            borderRadius: "6px",
            background: lang === "zh" ? "var(--accent)" : "var(--bg-secondary)",
            color: "white",
            border: "none",
            cursor: "pointer",
          }}
          onClick={() => setLanguage("zh")}
        >
          中文
        </button>

        <button
          style={{
            padding: "8px 12px",
            borderRadius: "6px",
            background: lang === "en" ? "var(--accent)" : "var(--bg-secondary)",
            color: "white",
            border: "none",
            cursor: "pointer",
          }}
          onClick={() => setLanguage("en")}
        >
          English
        </button>
      </Panel>

      {/* Theme */}
      <Panel>
        <h3>{lang === "zh" ? "主题设置" : "Theme"}</h3>
        <button
          style={{
            marginRight: "10px",
            padding: "8px 12px",
            borderRadius: "6px",
            // ✅ 用 theme.mode 做比较，而不是 theme 本身
            background: theme.mode === "light" ? "var(--accent)" : "var(--bg-secondary)",
            color: "white",
            border: "none",
            cursor: "pointer",
          }}
          // ✅ setTheme 传入字符串 ThemeMode
          onClick={() => setTheme("light")}
        >
          {lang === "zh" ? "亮色主题" : "Light Theme"}
        </button>

        <button
          style={{
            padding: "8px 12px",
            borderRadius: "6px",
            background: theme.mode === "dark" ? "var(--accent)" : "var(--bg-secondary)",
            color: "white",
            border: "none",
            cursor: "pointer",
          }}
          onClick={() => setTheme("dark")}
        >
          {lang === "zh" ? "暗色主题" : "Dark Theme"}
        </button>
      </Panel>

      {/* Feature Flags */}
      <Card>
        <h3>{lang === "zh" ? "功能开关" : "Feature Flags"}</h3>

        <ul>
          <li>
            SSE:{" "}
            <button
              onClick={() =>
                setFeatureFlags({ enableSSE: !featureFlags.enableSSE })
              }
            >
              {featureFlags.enableSSE ? "ON" : "OFF"}
            </button>
          </li>

          <li>
            Multi-Agent:{" "}
            <button
              onClick={() =>
                setFeatureFlags({
                  enableMultiAgent: !featureFlags.enableMultiAgent,
                })
              }
            >
              {featureFlags.enableMultiAgent ? "ON" : "OFF"}
            </button>
          </li>

          <li>
            Advanced Schema:{" "}
            <button
              onClick={() =>
                setFeatureFlags({
                  enableAdvancedSchema: !featureFlags.enableAdvancedSchema,
                })
              }
            >
              {featureFlags.enableAdvancedSchema ? "ON" : "OFF"}
            </button>
          </li>

          <li>
            Dynamic Theme:{" "}
            <button
              onClick={() =>
                setFeatureFlags({
                  enableDynamicTheme: !featureFlags.enableDynamicTheme,
                })
              }
            >
              {featureFlags.enableDynamicTheme ? "ON" : "OFF"}
            </button>
          </li>
        </ul>
      </Card>

      {/* Reset System */}
      <Panel>
        <h3>{lang === "zh" ? "系统重置" : "Reset System"}</h3>
        <button
          style={{
            padding: "10px 14px",
            borderRadius: "6px",
            background: "red",
            color: "white",
            border: "none",
            cursor: "pointer",
          }}
          onClick={() => resetSystem()}
        >
          {lang === "zh" ? "重置系统" : "Reset System"}
        </button>
      </Panel>
    </div>
  );
}
