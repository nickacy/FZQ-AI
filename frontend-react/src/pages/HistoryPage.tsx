import { useLanguageStore } from "../state/languageState";
import { useOutputState } from "../state/outputState";
import { useSystemState } from "../state/systemState";

import { Card } from "../components/ui/Card";
import { Panel } from "../components/ui/Panel";
import { SectionTitle } from "../components/ui/SectionTitle";

interface HistoryEntry {
  id: string;
  timestamp: number;
  input: string;
  outputCards: any[];
  usedSSE: boolean;
  usedMultiAgent: boolean;
}

export default function HistoryPage() {
  const lang = useLanguageStore((s) => s.language);
  const { cards, setCards } = useOutputState();
  const featureFlags = useSystemState((s) => s.featureFlags);

  // Mock history data — replace with backend later
  const history: HistoryEntry[] = [
    {
      id: "h1",
      timestamp: Date.now() - 1000 * 60 * 5,
      input: "Explain the policy matrix of EU vs China",
      outputCards: cards,
      usedSSE: true,
      usedMultiAgent: true,
    },
    {
      id: "h2",
      timestamp: Date.now() - 1000 * 60 * 60,
      input: "Generate a table of GDP growth",
      outputCards: [],
      usedSSE: false,
      usedMultiAgent: false,
    },
  ];

  const restoreHistory = (entry: HistoryEntry) => {
    setCards(entry.outputCards);
  };

  return (
    <div>
      <SectionTitle title={lang === "zh" ? "执行历史" : "Execution History"} />

      {history.map((entry) => (
        <Card key={entry.id}>
          <h3>
            {lang === "zh" ? "任务：" : "Task:"} {entry.input}
          </h3>

          <p>
            {lang === "zh" ? "时间：" : "Time:"}{" "}
            {new Date(entry.timestamp).toLocaleString()}
          </p>

          <p>
            {lang === "zh" ? "使用 SSE：" : "Used SSE:"}{" "}
            {entry.usedSSE ? "Yes" : "No"}
          </p>

          <p>
            {lang === "zh" ? "使用多智能体：" : "Used Multi-Agent:"}{" "}
            {entry.usedMultiAgent ? "Yes" : "No"}
          </p>

          <button
            style={{
              marginTop: "10px",
              padding: "8px 12px",
              borderRadius: "6px",
              background: "var(--accent)",
              color: "white",
              border: "none",
              cursor: "pointer",
            }}
            onClick={() => restoreHistory(entry)}
          >
            {lang === "zh" ? "恢复输出" : "Restore Output"}
          </button>
        </Card>
      ))}
    </div>
  );
}
