import { useLanguageStore } from "../state/languageState";
import { useOutputState } from "../state/outputState";

import { Card } from "../components/ui/Card";
import { Panel } from "../components/ui/Panel";
import { SectionTitle } from "../components/ui/SectionTitle";

interface FavoriteEntry {
  id: string;
  type: "prompt" | "agent" | "output";
  title: string;
  timestamp: number;
  payload: any;
}

export default function FavoritesPage() {
  const lang = useLanguageStore((s) => s.language);
  const { setCards } = useOutputState();

  // Mock favorites — replace with backend later
  const favorites: FavoriteEntry[] = [
    {
      id: "fav1",
      type: "prompt",
      title: "EU vs China policy matrix",
      timestamp: Date.now() - 1000 * 60 * 10,
      payload: { query: "Explain the policy matrix of EU vs China" },
    },
    {
      id: "fav2",
      type: "agent",
      title: "Policy Analysis Agent",
      timestamp: Date.now() - 1000 * 60 * 60,
      payload: { agentId: "agent-policy" },
    },
    {
      id: "fav3",
      type: "output",
      title: "GDP Growth Table",
      timestamp: Date.now() - 1000 * 60 * 120,
      payload: {
        cards: [
          {
            type: "table",
            title: { zh: "GDP 增长表", en: "GDP Growth Table" },
            rows: [
              ["Year", "GDP Growth"],
              ["2023", "5.2%"],
              ["2024", "5.5%"],
            ],
          },
        ],
      },
    },
  ];

  const restoreFavorite = (fav: FavoriteEntry) => {
    if (fav.type === "output") {
      setCards(fav.payload.cards);
    }
  };

  return (
    <div>
      <SectionTitle title={lang === "zh" ? "收藏夹" : "Favorites"} />

      {favorites.map((fav) => (
        <Card key={fav.id}>
          <h3>
            {lang === "zh" ? "标题：" : "Title:"} {fav.title}
          </h3>

          <p>
            {lang === "zh" ? "类型：" : "Type:"}{" "}
            {fav.type === "prompt"
              ? lang === "zh"
                ? "提示词"
                : "Prompt"
              : fav.type === "agent"
              ? lang === "zh"
                ? "智能体"
                : "Agent"
              : lang === "zh"
              ? "输出卡片"
              : "Output"}
          </p>

          <p>
            {lang === "zh" ? "时间：" : "Time:"}{" "}
            {new Date(fav.timestamp).toLocaleString()}
          </p>

          {fav.type === "output" && (
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
              onClick={() => restoreFavorite(fav)}
            >
              {lang === "zh" ? "恢复输出" : "Restore Output"}
            </button>
          )}
        </Card>
      ))}
    </div>
  );
}
