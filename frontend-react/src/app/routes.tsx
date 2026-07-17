import React, { Suspense } from "react";
import { Routes, Route, Navigate } from "react-router-dom";

import { ErrorBoundary } from "../components/layout/ErrorBoundary";
import { LoadingSpinner } from "../components/ui/LoadingSpinner";
import { AppShell } from "./AppShell";

// Lazy-loaded pages (must have default export)
const WorkspacePage = React.lazy(() => import("../pages/WorkspacePage"));
const HistoryPage = React.lazy(() => import("../pages/HistoryPage"));
const FavoritesPage = React.lazy(() => import("../pages/FavoritesPage"));
const AgentsPage = React.lazy(() => import("../pages/AgentsPage"));
const SettingsPage = React.lazy(() => import("../pages/SettingsPage"));
const SystemPage = React.lazy(() => import("../pages/SystemPage"));
const DebugPage = React.lazy(() => import("../pages/DebugPage"));
const DiagnosticsPage = React.lazy(() => import("../pages/DiagnosticsPage"));
const NotFoundPage = React.lazy(() => import("../pages/NotFoundPage"));

export const AppRoutes: React.FC = () => {
  return (
    <Suspense fallback={<LoadingSpinner />}>
      <Routes>
        <Route element={<AppShell />}>
        {/* Redirect root → /workspace */}
        <Route path="/" element={<Navigate to="/workspace" replace />} />

        <Route
          path="/workspace"
          element={
            <ErrorBoundary>
              <WorkspacePage />
            </ErrorBoundary>
          }
        />

        <Route
          path="/history"
          element={
            <ErrorBoundary>
              <HistoryPage />
            </ErrorBoundary>
          }
        />

        <Route
          path="/favorites"
          element={
            <ErrorBoundary>
              <FavoritesPage />
            </ErrorBoundary>
          }
        />

        <Route
          path="/agents"
          element={
            <ErrorBoundary>
              <AgentsPage />
            </ErrorBoundary>
          }
        />

        <Route
          path="/settings"
          element={
            <ErrorBoundary>
              <SettingsPage />
            </ErrorBoundary>
          }
        />

        {/* System-level pages */}
        <Route
          path="/system"
          element={
            <ErrorBoundary>
              <SystemPage />
            </ErrorBoundary>
          }
        />

        <Route
          path="/debug"
          element={
            <ErrorBoundary>
              <DebugPage />
            </ErrorBoundary>
          }
        />

        <Route
          path="/diagnostics"
          element={
            <ErrorBoundary>
              <DiagnosticsPage />
            </ErrorBoundary>
          }
        />

        {/* 404 */}
        <Route
          path="*"
          element={
            <ErrorBoundary>
              <NotFoundPage />
            </ErrorBoundary>
          }
        />
        </Route>
      </Routes>
    </Suspense>
  );
};
