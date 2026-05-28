"use client";

import { useEffect, useRef, useState } from "react";

export function ActionMenu({
  label,
  variant = "ghost",
  disabled,
  children,
}: {
  label: string;
  variant?: "ghost" | "primary" | "teal";
  disabled?: boolean;
  children: React.ReactNode;
}) {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!open) return;
    const close = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    };
    document.addEventListener("mousedown", close);
    return () => document.removeEventListener("mousedown", close);
  }, [open]);

  const btnClass =
    variant === "primary"
      ? "manga-btn manga-btn-primary"
      : variant === "teal"
        ? "manga-btn manga-btn-teal"
        : "manga-btn manga-btn-ghost";

  return (
    <div className="action-menu" ref={ref}>
      <button
        type="button"
        className={`${btnClass} !text-sm`}
        disabled={disabled}
        aria-expanded={open}
        onClick={() => setOpen((o) => !o)}
      >
        {label} ▾
      </button>
      {open && (
        <div className="action-menu-panel" role="menu">
          <div
            className="action-menu-items"
            onClick={() => setOpen(false)}
            onKeyDown={() => {}}
          >
            {children}
          </div>
        </div>
      )}
    </div>
  );
}

export function ActionMenuItem({
  onClick,
  href,
  disabled,
  children,
}: {
  onClick?: () => void;
  href?: string;
  disabled?: boolean;
  children: React.ReactNode;
}) {
  if (href) {
    return (
      <a className="action-menu-item" href={href} role="menuitem">
        {children}
      </a>
    );
  }
  return (
    <button
      type="button"
      className="action-menu-item"
      role="menuitem"
      disabled={disabled}
      onClick={onClick}
    >
      {children}
    </button>
  );
}
