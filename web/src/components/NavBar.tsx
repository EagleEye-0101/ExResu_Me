"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { ThemeToggle } from "@/components/ThemeProvider";

const LINKS: { href: string; label: string; small?: boolean }[] = [
  { href: "/", label: "Home" },
  { href: "/latex", label: "LaTeX", small: true },
  { href: "/wizard", label: "+ New", small: true },
  { href: "/ats-check", label: "ATS", small: true },
  { href: "/interview-prep", label: "Interview", small: true },
  { href: "/settings", label: "Settings" },
];

function isNavActive(pathname: string, href: string): boolean {
  if (href === "/") return pathname === "/";
  return pathname === href || pathname.startsWith(`${href}/`);
}

export function NavBar() {
  const pathname = usePathname();

  return (
    <div className="flex flex-wrap items-center gap-2 text-sm">
      {LINKS.map(({ href, label, small }) => {
        const active = isNavActive(pathname, href);
        return (
          <Link
            key={href}
            href={href}
            className={`nav-pill ${active ? "nav-pill-accent" : ""} ${small ? "!py-1 !text-sm" : ""}`}
          >
            {label}
          </Link>
        );
      })}
      <ThemeToggle />
    </div>
  );
}
