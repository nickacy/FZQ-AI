import React from "react";

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary";
}

export const Button: React.FC<ButtonProps> = ({
  variant = "primary",
  children,
  ...rest
}) => {
  const styles =
    variant === "primary"
      ? {
          background: "var(--button-primary)",
          color: "var(--button-text)"
        }
      : {
          background: "var(--bg-secondary)",
          color: "var(--text-primary)",
          border: "1px solid var(--border-color)"
        };

  return (
    <button
      {...rest}
      style={{
        padding: "8px 14px",
        borderRadius: "6px",
        fontSize: "14px",
        cursor: "pointer",
        ...styles
      }}
    >
      {children}
    </button>
  );
};
