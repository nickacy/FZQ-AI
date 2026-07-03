import { useState } from "react";

import { Card } from "../components/ui/Card";
import { Panel } from "../components/ui/Panel";
import { SectionTitle } from "../components/ui/SectionTitle";
import { Button } from "../components/ui/Button";
import { Input } from "../components/ui/Input";

import { t } from "../i18n";
import { useLanguageStore } from "../state/languageState";
import { useOutputState } from "../state/outputState";
import { useSystemState } from "../state/systemState";

import { apiClient } from "../services/apiClient";
import { schemaAdapter } from "../services/schemaAdapter";

export default function WorkspacePage() {
  const lang = useLanguageStore((s) => s.language);
  const { cards, setCards, resetOutputs } = useOutputState();
  const { apiStatus, systemHealth } = useSystemState();

  const [input, setInput] = useState("");
  const [isRunning, setRunning] = useState(false);

  const handleExecute = async () => {
    if (!input.trim()) return;

    resetOutputs();
    setRunning(true);

    try {
      const data = await apiClient.post("/entry", { query: input });

      if (data.ui_schema) {
        const mapped = schemaAdapter.toOutputCards(data.ui_schema) as any;
        setCards(mapped);
      }
    } catch (err) {
      console.error("Execution error:", err);
    } finally {
      setRunning(false);
    }
  };

  return (
    <div>
      <SectionTitle title={t("nav.workspace", lang)} />

      {/* Input Panel */}
      <Panel>
        <h3>{t("execution.running", lang)}</h3>
        <Input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Enter your query..."
        />
        <Button
          variant="primary"
          onClick={handleExecute}
          disabled={isRunning}
        >
          {isRunning ? "Running..." : "Run Pipeline"}
        </Button>
      </Panel>

      {/* System Status */}
      <Card>
        <h4>System Status</h4>
        <p>API: {apiStatus}</p>
        <p>Health: {systemHealth}</p>
      </Card>

      {/* Output Cards */}
      {cards.map((card, idx) => (
        <Card key={idx}>
          <h4>{card.title?.[lang] ?? ""}</h4>
          <p>{card.content?.[lang] ?? ""}</p>
        </Card>
      ))}
    </div>
  );
}
