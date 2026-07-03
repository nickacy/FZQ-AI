import React from "react";
import { Card } from "../../components/ui/Card";
import { useLanguageStore } from "../../state/languageState";

interface OutputCard {
  title?: { zh: string; en: string };
  content?: { zh: string; en: string };
  type: string;
  rows?: any[];
  code?: string;
}

export const OutputPanel: React.FC<{ cards: OutputCard[] }> = ({ cards }) => {
  const lang = useLanguageStore((s) => s.language);

  return (
    <div style={{ marginTop: "20px" }}>
      {cards.map((card, idx) => {
        const title = card.title?.[lang] ?? "";
        const content = card.content?.[lang] ?? "";

        switch (card.type) {
          case "text":
            return (
              <Card key={idx}>
                <h3>{title}</h3>
                <p>{content}</p>
              </Card>
            );

          case "table":
            return (
              <Card key={idx}>
                <h3>{title}</h3>
                <table
                  style={{
                    width: "100%",
                    borderCollapse: "collapse",
                    marginTop: "10px",
                  }}
                >
                  <tbody>
                    {card.rows?.map((row, rIdx) => (
                      <tr key={rIdx}>
                        {row.map((cell: any, cIdx: number) => (
                          <td
                            key={cIdx}
                            style={{
                              border: "1px solid var(--border-color)",
                              padding: "6px 10px",
                            }}
                          >
                            {cell}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </Card>
            );

          case "code":
            return (
              <Card key={idx}>
                <h3>{title}</h3>
                <pre
                  style={{
                    background: "var(--bg-secondary)",
                    padding: "12px",
                    borderRadius: "6px",
                    overflowX: "auto",
                  }}
                >
                  {card.code}
                </pre>
              </Card>
            );

          case "chart":
            return (
              <Card key={idx}>
                <h3>{title}</h3>
                <p>Chart rendering placeholder (chart.js integration optional)</p>
              </Card>
            );

          default:
            return (
              <Card key={idx}>
                <h3>{title}</h3>
                <p>{content}</p>
              </Card>
            );
        }
      })}
    </div>
  );
};
