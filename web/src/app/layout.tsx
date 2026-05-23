import type { Metadata } from "next";
import Link from "next/link";
import { BrandLogo } from "@/components/BrandLogo";
import { ThemeProvider, ThemeToggle } from "@/components/ThemeProvider";
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
              <div className="flex flex-wrap items-center gap-2 text-sm">
                <Link href="/" className="nav-pill">
                  Home
                </Link>
                <Link href="/wizard" className="nav-pill nav-pill-accent !py-1 !text-sm">
                  + New
                </Link>
                <Link href="/ats-check" className="nav-pill !py-1 !text-sm">
                  ATS
                </Link>
                <Link href="/interview-prep" className="nav-pill !py-1 !text-sm">
                  Interview
                </Link>
                <Link href="/settings" className="nav-pill">
                  Settings
                </Link>
                <ThemeToggle />
              </div>
            </div>
          </nav>
          <main className="mx-auto max-w-6xl px-4 py-8">{children}</main>
        </ThemeProvider>
      </body>
    </html>
  );
}
