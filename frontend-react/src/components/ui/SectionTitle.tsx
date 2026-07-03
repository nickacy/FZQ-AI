import React from "react";

export const SectionTitle: React.FC<{ title: string }> = ({ title }) => {
  return (
    <h2
      style={{
        marginBottom: "12px",
        color: "var(--text-primary)",
        fontSize: "20px",
        fontWeight: 600
      }}
    >
      {title}
    </h2>
  );
};
