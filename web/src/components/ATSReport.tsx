"use client";

import { ATSReport as ATSReportType } from "@/lib/api";

export function ATSReportPanel({ report }: { report: ATSReportType }) {
  const score = report.composite_score;
  const color =
    score >= 80 ? "var(--success)" : score >= 60 ? "var(--warning)" : "var(--danger)";

  return (
    <div className="space-y-6">
      <div className="manga-panel flex flex-wrap items-center gap-8">
        <div
          className="flex h-32 w-32 flex-shrink-0 items-center justify-center rounded-full border-[4px] border-[var(--border)] font-display text-4xl"
          style={{ background: `conic-gradient(${color} ${score}%, var(--accent-3) 0)` }}
        >
          <div className="flex h-24 w-24 items-center justify-center rounded-full bg-white text-3xl">
            {score.toFixed(0)}
          </div>
        </div>
        <div>
          <h3 className="font-display text-3xl">ATS Power Level</h3>
          <p className="text-[var(--muted)]">Keyword match · structure · format · content</p>
          {report.export_blocked && (
            <p className="mt-2 font-bold text-[var(--danger)]">Fix errors before exporting!</p>
          )}
        </div>
      </div>

      <div className="grid gap-4 sm:grid-cols-2">
        {report.categories.map((c) => (
          <div key={c.name} className="manga-panel">
            <div className="flex justify-between font-bold">
              <span>{c.name}</span>
              <span>{c.score.toFixed(0)}</span>
            </div>
            <div className="mt-2 h-3 overflow-hidden rounded-full border-2 border-[var(--border)] bg-white">
              <div
                className="h-full bg-[var(--accent)]"
                style={{ width: `${c.score}%` }}
              />
            </div>
            {c.details.map((d, i) => (
              <p key={i} className="mt-1 text-xs text-[var(--muted)]">
                {d}
              </p>
            ))}
          </div>
        ))}
      </div>

      {report.missing_keywords.length > 0 && (
        <div className="manga-panel border-[var(--warning)]">
          <h4 className="font-display text-lg text-[var(--warning)]">Missing keywords</h4>
          <div className="mt-2 flex flex-wrap gap-2">
            {report.missing_keywords.map((kw) => (
              <span key={kw} className="badge bg-[var(--warning)]/30">
                {kw}
              </span>
            ))}
          </div>
        </div>
      )}

      {report.matched_keywords.length > 0 && (
        <div className="manga-panel">
          <h4 className="font-display text-lg text-[var(--success)]">Matched</h4>
          <div className="mt-2 flex flex-wrap gap-2">
            {report.matched_keywords.slice(0, 24).map((kw) => (
              <span key={kw} className="badge bg-[var(--accent-2)]/40">
                {kw}
              </span>
            ))}
          </div>
        </div>
      )}

      {report.fixes.length > 0 && (
        <div className="speech-bubble">
          <h4 className="font-display text-xl">Quest objectives</h4>
          <ul className="mt-3 space-y-2">
            {report.fixes.map((f, i) => (
              <li key={i} className="flex gap-2 text-sm">
                <SeverityBadge severity={f.severity} />
                <span>{f.message}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

function SeverityBadge({ severity }: { severity: string }) {
  const colors: Record<string, string> = {
    error: "var(--danger)",
    warning: "var(--warning)",
    info: "var(--muted)",
  };
  const c = colors[severity] || colors.info;
  return (
    <span className="badge shrink-0 uppercase" style={{ background: `${c}33`, borderColor: c }}>
      {severity}
    </span>
  );
}
