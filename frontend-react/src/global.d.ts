// Allow importing CSS files
declare module "*.css";

// Allow CSS variables in React style objects
// The import makes this file a module, so declare module becomes an augmentation
import "react";
declare module "react" {
  interface CSSProperties {
    [key: `--${string}`]: string | number;
  }
}
