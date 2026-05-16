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
          "Inter",
          "-apple-system",
          "BlinkMacSystemFont",
          "\"Segoe UI\"",
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
        panel: "#fbfbf8"
      },
      boxShadow: {
        panel: "0 10px 30px rgba(17,17,17,0.03)"
      }
    }
  },
  plugins: []
};

export default config;
