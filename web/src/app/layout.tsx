import type { Metadata } from "next";
import Link from "next/link";
import "./globals.css";

export const metadata: Metadata = {
  title: "Resume Hero — ATS Builder",
  description: "Build ATS-optimized resumes with AI",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="text-manga-text antialiased">
        <nav className="sticky top-0 z-50 border-b-[3px] border-manga-border bg-white/95 backdrop-blur-sm">
          <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-3">
            <Link href="/" className="font-display text-2xl tracking-wide text-manga-accent">
              RESUME HERO
            </Link>
            <div className="flex gap-2 text-sm font-bold sm:gap-4">
              <Link href="/" className="btn-ghost px-3 py-1.5 text-sm">
                Home
              </Link>
              <Link href="/wizard" className="btn-primary px-3 py-1.5 text-sm">
                + New
              </Link>
              <Link href="/settings" className="btn-ghost px-3 py-1.5 text-sm">
                Settings
              </Link>
            </div>
          </div>
        </nav>
        <main className="mx-auto max-w-6xl px-4 py-8">{children}</main>
      </body>
    </html>
  );
}
