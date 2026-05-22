"use client";

import Link from "next/link";

type Variant = "primary" | "secondary" | "ghost" | "teal";

const VARIANT_CLASS: Record<Variant, string> = {
  primary: "manga-btn manga-btn-primary",
  secondary: "manga-btn manga-btn-secondary",
  ghost: "manga-btn manga-btn-ghost",
  teal: "manga-btn manga-btn-teal",
};

export function MangaButton({
  children,
  variant = "primary",
  href,
  onClick,
  disabled,
  type = "button",
  className = "",
  burst,
}: {
  children: React.ReactNode;
  variant?: Variant;
  href?: string;
  onClick?: () => void;
  disabled?: boolean;
  type?: "button" | "submit";
  className?: string;
  burst?: boolean;
}) {
  const cls = `${VARIANT_CLASS[variant]} ${burst ? "manga-btn-burst" : ""} ${className}`.trim();

  if (href) {
    return (
      <Link href={href} className={cls}>
        {children}
      </Link>
    );
  }

  return (
    <button type={type} className={cls} onClick={onClick} disabled={disabled}>
      {children}
    </button>
  );
}
