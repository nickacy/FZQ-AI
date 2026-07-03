// Allow importing CSS files
declare module "*.css";

// Allow CSS variables in React style objects
declare module "react" {
  interface CSSProperties {
    [key: `--${string}`]: string | number;
  }
}
