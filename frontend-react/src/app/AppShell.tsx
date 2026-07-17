import { Outlet, Link } from "react-router-dom";
import { t } from "../i18n";
import { useLanguageStore } from "../state/languageState";

export function AppShell() {
  const lang = useLanguageStore((s) => s.language);

  return (
    <div className="app-shell">
      <header className="app-header">
        <h1>{t("app.title", lang)}</h1>
        <p>{t("app.subtitle", lang)}</p>
      </header>

      <nav className="app-nav">
        <Link to="/workspace">{t("nav.workspace", lang)}</Link>
        <Link to="/history">{t("nav.history", lang)}</Link>
        <Link to="/favorites">{t("nav.favorites", lang)}</Link>
        <Link to="/agents">{t("nav.agents", lang)}</Link>
        <Link to="/settings">{t("nav.settings", lang)}</Link>
        <Link to="/debug">{t("nav.debug", lang)}</Link>
        <Link to="/diagnostics">{t("nav.diagnostics", lang)}</Link>
      </nav>

      <main className="app-main">
        <Outlet />
      </main>
    </div>
  );
}
