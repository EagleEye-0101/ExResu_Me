"use client";

import { createContext, useContext, useEffect, useState } from "react";

const STORAGE_KEY = "exresu-me-theme";
const LEGACY_KEY = "resume-hero-theme";

const ThemeContext = createContext({
  theme: "light" as "light" | "dark",
  toggle: () => {},
});

function applyTheme(theme: "light" | "dark") {
  document.documentElement.setAttribute("data-theme", theme);
}

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const [theme, setTheme] = useState<"light" | "dark">("light");

  useEffect(() => {
    const saved =
      (localStorage.getItem(STORAGE_KEY) as "light" | "dark" | null) ||
      (localStorage.getItem(LEGACY_KEY) as "light" | "dark" | null);
    const fromDom = document.documentElement.getAttribute("data-theme") as "light" | "dark" | null;
    const initial =
      saved === "light" || saved === "dark"
        ? saved
        : fromDom === "light" || fromDom === "dark"
          ? fromDom
          : null;
    if (initial) {
      setTheme(initial);
      applyTheme(initial);
      localStorage.setItem(STORAGE_KEY, initial);
    }
  }, []);

  const toggle = () => {
    setTheme((t) => {
      const next = t === "light" ? "dark" : "light";
      localStorage.setItem(STORAGE_KEY, next);
      applyTheme(next);
      return next;
    });
  };

  return (
    <ThemeContext.Provider value={{ theme, toggle }}>{children}</ThemeContext.Provider>
  );
}

export function useTheme() {
  return useContext(ThemeContext);
}

export function ThemeToggle() {
  const { theme, toggle } = useTheme();
  return (
    <button
      type="button"
      className="manga-btn manga-btn-ghost !py-1 !text-xs"
      onClick={toggle}
      aria-label="Toggle dark mode"
    >
      {theme === "light" ? "Dark" : "Light"}
    </button>
  );
}
