"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";

export function KeywordHeatmap({ resumeId }: { resumeId: number }) {
  const [data, setData] = useState<{
    matched: string[];
    missing: string[];
    keywords: string[];
  } | null>(null);

  useEffect(() => {
    api.keywordHeatmap(resumeId).then(setData).catch(() => {});
  }, [resumeId]);

  if (!data) return <p className="text-manga-muted">Loading keywords...</p>;

  return (
    <div className="space-y-4">
      <div>
        <h4 className="font-display text-lg text-manga-success">Matched ({data.matched.length})</h4>
        <div className="mt-2 flex flex-wrap gap-2">
          {data.matched.map((k) => (
            <span key={k} className="badge bg-manga-teal/40">
              {k}
            </span>
          ))}
        </div>
      </div>
      <div>
        <h4 className="font-display text-lg text-manga-danger">Missing ({data.missing.length})</h4>
        <div className="mt-2 flex flex-wrap gap-2">
          {data.missing.map((k) => (
            <span key={k} className="badge kw-miss">
              {k}
            </span>
          ))}
        </div>
      </div>
      <p className="text-sm text-manga-muted">
        Add missing words naturally in Edit tab, then Save and Re-optimize.
      </p>
    </div>
  );
}
