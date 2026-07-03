import React from "react";

export const Card: React.FC<React.PropsWithChildren> = ({ children }) => {
  return (
    <div
      style={{
        background: "var(--card-bg)",
        padding: "16px",
        borderRadius: "8px",
        border: "1px solid var(--border-color)",
        boxShadow: "var(--shadow)",
        marginBottom: "16px"
      }}
    >
      {children}
    </div>
  );
};
