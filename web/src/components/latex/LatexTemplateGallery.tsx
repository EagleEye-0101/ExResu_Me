"use client";

import Image from "next/image";
import { LatexTemplateMeta } from "@/lib/api";

export function LatexTemplateGallery({
  templates,
  value,
  onChange,
  compact = false,
}: {
  templates: LatexTemplateMeta[];
  value: string;
  onChange: (id: string) => void;
  compact?: boolean;
}) {
  if (!templates.length) {
    return <p className="text-sm text-manga-muted">Loading templates…</p>;
  }

  return (
    <div
      className={
        compact
          ? "flex flex-wrap gap-2"
          : "grid gap-3 sm:grid-cols-2 lg:grid-cols-4"
      }
    >
      {templates.map((t) => {
        const selected = value === t.id;
        return (
          <button
            key={t.id}
            type="button"
            onClick={() => onChange(t.id)}
            className={`manga-panel text-left transition ${
              compact ? "!p-2" : ""
            } ${selected ? "ring-2 ring-manga-accent" : "opacity-90 hover:opacity-100"}`}
          >
            {!compact && (
              <div className="relative mb-2 h-20 w-full overflow-hidden rounded-lg border-2 border-manga-border bg-white">
                <Image
                  src={t.thumbnail}
                  alt={t.name}
                  fill
                  className="object-cover object-top"
                  unoptimized
                />
              </div>
            )}
            <p className={`font-bold text-manga-text ${compact ? "text-xs" : ""}`}>
              {t.name}
            </p>
            {!compact && (
              <p className="text-xs text-manga-muted line-clamp-2">{t.description}</p>
            )}
          </button>
        );
      })}
    </div>
  );
}
