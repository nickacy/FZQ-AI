import { Outlet } from "react-router-dom";
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
        <a href="/workspace">{t("nav.workspace", lang)}</a>
        <a href="/history">{t("nav.history", lang)}</a>
        <a href="/favorites">{t("nav.favorites", lang)}</a>
        <a href="/agents">{t("nav.agents", lang)}</a>
        <a href="/settings">{t("nav.settings", lang)}</a>
        <a href="/debug">{t("nav.debug", lang)}</a>
        <a href="/diagnostics">{t("nav.diagnostics", lang)}</a>
      </nav>

      <main className="app-main">
        <Outlet />
      </main>
    </div>
  );
}
