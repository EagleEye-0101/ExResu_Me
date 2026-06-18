import type { Metadata } from "next";
import { BrandLogo } from "@/components/BrandLogo";
import { NavBar } from "@/components/NavBar";
import { ThemeProvider } from "@/components/ThemeProvider";
import { ThemeScript } from "@/components/ThemeScript";
import "./globals.css";

export const metadata: Metadata = {
  title: "ExResu_Me — ATS Resume Builder",
  description: "Build ATS-optimized resumes with AI — ExResu_Me",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <ThemeScript />
      </head>
      <body className="antialiased">
        <ThemeProvider>
          <nav className="site-nav sticky top-0 z-50 backdrop-blur-sm">
            <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-3">
              <BrandLogo />
              <NavBar />
            </div>
          </nav>
          <main className="mx-auto max-w-6xl px-4 py-8">{children}</main>
        </ThemeProvider>
      </body>
    </html>
  );
}
