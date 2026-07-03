import React from "react";

export const Panel: React.FC<React.PropsWithChildren> = ({ children }) => {
  return (
    <div
      style={{
        background: "var(--bg-secondary)",
        padding: "20px",
        borderRadius: "10px",
        border: "1px solid var(--border-color)",
        boxShadow: "var(--shadow)",
        marginBottom: "20px"
      }}
    >
      {children}
    </div>
  );
};
