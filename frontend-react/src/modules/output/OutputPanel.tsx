import React from "react";
import { useOutputState } from "../../state/outputState";
import { useLanguageStore } from "../../state/languageState";
import { Card } from "../../components/ui/Card";

export default function OutputPanel() {
  const { cards } = useOutputState();
  const lang = useLanguageStore((s) => s.language);

  if (!cards || cards.length === 0) {
    return (
      <Card>
        <p style={{ opacity: 0.6 }}>
          {lang === "zh" ? "暂无输出" : "No output yet"}
        </p>
      </Card>
    );
  }

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
                <p style={{ lineHeight: "1.6" }}>{content}</p>
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
                              border: "1px solid var(--border)",
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
                    marginTop: "10px",
                  }}
                >
                  <code>{card.code}</code>
                </pre>
              </Card>
            );

          case "chart":
            return (
              <Card key={idx}>
                <h3>{title}</h3>
                <p style={{ opacity: 0.7 }}>
                  {lang === "zh"
                    ? "图表渲染占位符（可选集成 chart.js）"
                    : "Chart rendering placeholder (chart.js optional)"}
                </p>
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
}
