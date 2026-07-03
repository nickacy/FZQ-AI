import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";

import { useThemeState } from "./state/themeState";
import { useLanguageStore } from "./state/languageState";

import "./styles/global.css";

function Root() {
  const theme = useThemeState((s) => s.theme);
  const lang = useLanguageStore((s) => s.language);

  const rootStyle =
    theme.mode === "dark"
      ? {
          "--bg-primary": "#0d0d0d",
          "--bg-secondary": "#1a1a1a",
          "--text-primary": "#ffffff",
          "--text-secondary": "#cccccc",
          "--border": "#333333",
          "--accent": "#0077ff",
        }
      : {
          "--bg-primary": "#ffffff",
          "--bg-secondary": "#f5f5f5",
          "--text-primary": "#000000",
          "--text-secondary": "#444444",
          "--border": "#dddddd",
          "--accent": "#0066dd",
        };

  return (
    <div style={rootStyle as any}>
      <App />
    </div>
  );
}

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <Root />
  </React.StrictMode>
);
