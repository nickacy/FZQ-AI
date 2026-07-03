import React from "react";
import ReactDOM from "react-dom/client";
import { RouterProvider } from "react-router-dom";
import { router } from "./app/routes";

// 全局样式（如果你有）
import "./theme/lightTheme.ts";
import "./theme/darkTheme.ts";

const root = ReactDOM.createRoot(
  document.getElementById("root") as HTMLElement
);

root.render(
  <React.StrictMode>
    <RouterProvider router={router} />
  </React.StrictMode>
);

// 注册 Service Worker（PWA）
if ("serviceWorker" in navigator) {
  navigator.serviceWorker.register("/service-worker.js");
}
