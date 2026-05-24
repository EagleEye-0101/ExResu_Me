import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        manga: {
          bg: "var(--bg)",
          dots: "var(--bg-dots)",
          card: "var(--card)",
          border: "var(--border)",
          text: "var(--text)",
          muted: "var(--muted)",
          accent: "var(--accent)",
          teal: "var(--accent-2)",
          yellow: "var(--accent-3)",
          success: "var(--success)",
          warning: "var(--warning)",
          danger: "var(--danger)",
        },
      },
      fontFamily: {
        comic: ['"Comic Neue"', '"Comic Sans MS"', "cursive"],
        display: ['"Bangers"', "cursive"],
      },
      boxShadow: {
        manga: "4px 4px 0 var(--shadow)",
        "manga-lg": "6px 6px 0 var(--shadow)",
      },
    },
  },
  plugins: [],
};
export default config;
