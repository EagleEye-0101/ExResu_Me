import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        manga: {
          bg: "#fff8f0",
          dots: "#ffe4d6",
          card: "#ffffff",
          border: "#1a1a1a",
          text: "#1a1a1a",
          muted: "#5c4a4a",
          accent: "#ff6b9d",
          teal: "#4ecdc4",
          yellow: "#ffe66d",
          success: "#2dd4a8",
          warning: "#ffb347",
          danger: "#ff4757",
        },
      },
      fontFamily: {
        comic: ['"Comic Neue"', '"Comic Sans MS"', "cursive"],
        display: ['"Bangers"', "cursive"],
      },
      boxShadow: {
        manga: "4px 4px 0 #1a1a1a",
        "manga-lg": "6px 6px 0 #1a1a1a",
      },
    },
  },
  plugins: [],
};
export default config;
