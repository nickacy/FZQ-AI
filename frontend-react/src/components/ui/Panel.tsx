import React from "react";

export function Panel({ children }: { children: React.ReactNode }) {
  return (
    <div
      className="panel"
      style={{
        background: "var(--bg-secondary)",
        padding: "16px",
        borderRadius: "8px",
        border: "1px solid var(--border)",
        marginBottom: "20px",
      }}
    >
      {children}
    </div>
  );
}
