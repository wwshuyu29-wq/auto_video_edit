import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./lib/**/*.{ts,tsx}"
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: [
          "\"Avenir Next\"",
          "\"Helvetica Neue\"",
          "-apple-system",
          "BlinkMacSystemFont",
          "system-ui",
          "sans-serif"
        ],
        mono: [
          "\"SFMono-Regular\"",
          "ui-monospace",
          "Menlo",
          "Monaco",
          "\"Cascadia Mono\"",
          "\"Segoe UI Mono\"",
          "monospace"
        ]
      },
      colors: {
        ink: "#111111",
        mist: "#f3f3f1",
        smoke: "#d8d8d2",
        steel: "#8d8d87",
        panel: "#fbfbf8",
        border: "var(--border)",
        input: "var(--input)",
        ring: "var(--ring)",
        background: "var(--background)",
        foreground: "var(--foreground)",
        primary: {
          DEFAULT: "var(--primary)",
          foreground: "var(--primary-foreground)"
        },
        secondary: {
          DEFAULT: "var(--secondary)",
          foreground: "var(--secondary-foreground)"
        },
        destructive: {
          DEFAULT: "var(--destructive)",
          foreground: "var(--destructive-foreground)"
        },
        muted: {
          DEFAULT: "var(--muted)",
          foreground: "var(--muted-foreground)"
        },
        accent: {
          DEFAULT: "var(--accent)",
          foreground: "var(--accent-foreground)"
        },
        popover: {
          DEFAULT: "var(--popover)",
          foreground: "var(--popover-foreground)"
        },
        card: {
          DEFAULT: "var(--card)",
          foreground: "var(--card-foreground)"
        }
      },
      boxShadow: {
        panel: "0 10px 30px rgba(17,17,17,0.03)"
      }
    }
  },
  plugins: []
};

export default config;
