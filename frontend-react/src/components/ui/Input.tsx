import React from "react";

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {}

export const Input: React.FC<InputProps> = (props) => {
  return (
    <input
      {...props}
      style={{
        width: "100%",
        padding: "8px 10px",
        borderRadius: "6px",
        border: "1px solid var(--border-color)",
        background: "var(--bg-secondary)",
        color: "var(--text-primary)",
        fontSize: "14px"
      }}
    />
  );
};
