import { BrowserRouter as Router, Routes, Route } from "react-router-dom";

import NavigationBar from "./components/NavigationBar";

import WorkspacePage from "./pages/WorkspacePage";
import DiagnosticsPage from "./pages/DiagnosticsPage";
import SystemPage from "./pages/SystemPage";
import AgentsPage from "./pages/AgentsPage";
import HistoryPage from "./pages/HistoryPage";
import FavoritesPage from "./pages/FavoritesPage";
import DebugPage from "./pages/DebugPage";
import SettingsPage from "./pages/SettingsPage";

export default function App() {
  return (
    <Router>
      <NavigationBar />

      <div style={{ padding: "20px" }}>
        <Routes>
          <Route path="/" element={<WorkspacePage />} />
          <Route path="/diagnostics" element={<DiagnosticsPage />} />
          <Route path="/system" element={<SystemPage />} />
          <Route path="/agents" element={<AgentsPage />} />
          <Route path="/history" element={<HistoryPage />} />
          <Route path="/favorites" element={<FavoritesPage />} />
          <Route path="/debug" element={<DebugPage />} />
          <Route path="/settings" element={<SettingsPage />} />
        </Routes>
      </div>
    </Router>
  );
}
