import { Link } from "react-router-dom";
import { useLanguageStore } from "../state/languageState";
import { useSystemState } from "../state/systemState";
import { useThemeState } from "../state/themeState";

export default function NavigationBar() {
  const lang = useLanguageStore((s) => s.language);
  const theme = useThemeState((s) => s.theme);

  const apiStatus = useSystemState((s) => s.apiStatus);
  const sseStatus = useSystemState((s) => s.sseStatus);
  const systemHealth = useSystemState((s) => s.systemHealth);

  const label = (zh: string, en: string) => (lang === "zh" ? zh : en);

  return (
    <nav
      style={{
        display: "flex",
        alignItems: "center",
        padding: "10px 16px",
        background: theme.mode === "dark" ? "#111" : "#f5f5f5",
        borderBottom: "1px solid var(--border)",
        gap: "20px",
      }}
    >
      {/* Logo */}
      <div style={{ fontWeight: "bold", fontSize: "18px" }}>
        FZQ‑AI
      </div>

      {/* Navigation Links */}
      <Link to="/" className="nav-link">
        {label("工作区", "Workspace")}
      </Link>

      <Link to="/diagnostics" className="nav-link">
        {label("诊断", "Diagnostics")}
      </Link>

      <Link to="/system" className="nav-link">
        {label("系统", "System")}
      </Link>

      <Link to="/agents" className="nav-link">
        {label("智能体", "Agents")}
      </Link>

      <Link to="/history" className="nav-link">
        {label("历史", "History")}
      </Link>

      <Link to="/favorites" className="nav-link">
        {label("收藏", "Favorites")}
      </Link>

      <Link to="/debug" className="nav-link">
        {label("调试", "Debug")}
      </Link>

      <Link to="/settings" className="nav-link">
        {label("设置", "Settings")}
      </Link>

      {/* Status Indicators */}
      <div style={{ marginLeft: "auto", display: "flex", gap: "16px" }}>
        <span>
          {label("API：", "API:")}{" "}
          <strong>{apiStatus}</strong>
        </span>

        <span>
          {label("SSE：", "SSE:")}{" "}
          <strong>{sseStatus}</strong>
        </span>

        <span>
          {label("系统：", "Health:")}{" "}
          <strong>{systemHealth}</strong>
        </span>
      </div>
    </nav>
  );
}
