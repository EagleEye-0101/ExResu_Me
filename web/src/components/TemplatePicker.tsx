"use client";

import Image from "next/image";
import { useEffect, useState } from "react";
import { api, TemplateMeta } from "@/lib/api";

export function TemplatePicker({
  value,
  onChange,
}: {
  value: string;
  onChange: (templateId: string) => void;
}) {
  const [templates, setTemplates] = useState<TemplateMeta[]>([]);

  useEffect(() => {
    api.listTemplates().then(setTemplates).catch(() => {});
  }, []);

  if (!templates.length) {
    return (
      <p className="text-sm text-manga-muted">Loading templates…</p>
    );
  }

  return (
    <div className="grid gap-3 sm:grid-cols-2">
      {templates.map((t) => {
        const selected = value === t.id;
        return (
          <button
            key={t.id}
            type="button"
            onClick={() => onChange(t.id)}
            className={`manga-panel text-left transition ${
              selected ? "ring-2 ring-manga-accent" : "opacity-90 hover:opacity-100"
            }`}
          >
            <div className="relative mb-2 h-24 w-full overflow-hidden rounded-lg border-2 border-manga-border bg-white">
              <Image
                src={t.thumbnail}
                alt={t.name}
                fill
                className="object-cover object-top"
                unoptimized
              />
            </div>
            <p className="font-bold text-manga-text">{t.name}</p>
            <p className="text-xs text-manga-muted">{t.description}</p>
          </button>
        );
      })}
    </div>
  );
}
