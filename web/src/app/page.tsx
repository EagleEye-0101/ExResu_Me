"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { MangaButton } from "@/components/MangaButton";
import { api, Profile, ResumeListItem, ResumeStats } from "@/lib/api";

type Tab = "all" | "finished" | "draft";

export default function DashboardPage() {
  const [profiles, setProfiles] = useState<Profile[]>([]);
  const [resumes, setResumes] = useState<ResumeListItem[]>([]);
  const [stats, setStats] = useState<ResumeStats | null>(null);
  const [tab, setTab] = useState<Tab>("all");
  const [loading, setLoading] = useState(true);
  const [apiOk, setApiOk] = useState(false);
  const [latexTemplates, setLatexTemplates] = useState<{ id: string; name: string }[]>([]);

  const load = () => {
    Promise.all([
      api.health().then(() => setApiOk(true)).catch(() => setApiOk(false)),
      api.listProfiles().catch(() => []),
      api.listResumes().catch(() => []),
      api.resumeStats().catch(() => ({ total: 0, drafts: 0, finished: 0 })),
      api.listLatexTemplates().catch(() => ({ templates: [] })),
    ])
      .then(([, p, r, s, lt]) => {
        setProfiles(p as Profile[]);
        setResumes(r as ResumeListItem[]);
        setStats(s as ResumeStats);
        const templates = (lt as { templates?: { id: string; name: string }[] }).templates ?? [];
        setLatexTemplates(templates.map((t) => ({ id: t.id, name: t.name })));
      })
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    load();
  }, []);

  const filtered = resumes.filter((r) => {
    if (tab === "draft") return r.status === "draft";
    if (tab === "finished") return r.status === "finished";
    return true;
  });

  if (loading) {
    return (
      <div className="speech-bubble text-center font-display text-2xl text-manga-text">
        Loading your quest log...
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <section className="manga-panel-accent overflow-hidden">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
          <div className="relative z-10 max-w-xl">
            <p className="font-display text-lg text-manga-accent">LEVEL UP YOUR CAREER</p>
            <h1 className="font-display text-4xl leading-tight text-manga-text sm:text-5xl">
              Your Resume Arsenal
            </h1>
            <p className="mt-2 text-lg text-manga-muted">
              Build, edit anytime, score for ATS, export when ready. Professional LaTeX
              templates — edit, compile, download PDF.
            </p>
            <div className="mt-5 flex flex-wrap gap-3">
              <MangaButton href="/latex?demo=1" variant="primary" burst>
                Try demo resume
              </MangaButton>
              <MangaButton href="/latex" variant="teal">
                Browse LaTeX templates
              </MangaButton>
              <MangaButton href="/wizard" variant="ghost">
                Start New Resume
              </MangaButton>
              <MangaButton href="/ats-check" variant="ghost">
                ATS Checker
              </MangaButton>
              <MangaButton href="/interview-prep" variant="ghost">
                Interview Prep
              </MangaButton>
            </div>
          </div>
          <div
            className="hidden shrink-0 font-display text-6xl text-manga-accent/25 sm:block sm:text-7xl"
            aria-hidden
          >
            POW!
          </div>
        </div>
      </section>

      <section className="manga-panel">
        <p className="mb-3 text-sm font-bold text-manga-muted">LaTeX template previews</p>
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          {(latexTemplates.length
            ? latexTemplates
            : [
                { id: "compact", name: "Compact" },
                { id: "jake", name: "Jake" },
                { id: "alta", name: "Alta" },
                { id: "executive", name: "Executive" },
              ]
          ).map((t) => (
            <Link
              key={t.id}
              href={`/latex?demo=1&template=${t.id}`}
              className="manga-panel block text-center transition hover:ring-2 hover:ring-manga-accent"
            >
              <p className="font-bold text-manga-text">{t.name}</p>
              <p className="text-xs text-manga-muted">Open demo & compile</p>
            </Link>
          ))}
        </div>
      </section>

      {!apiOk && (
        <div className="manga-panel space-y-2 border-manga-danger bg-manga-danger/15 text-manga-danger">
          <p className="font-bold">Backend API is offline</p>
          <p className="text-sm text-manga-text">
            The website (port 3000) needs the Python API (port 8000) for resumes, AI, and settings.
            Keep <code className="text-xs">npm run dev</code> running, then start the API in a{" "}
            <strong>second</strong> terminal:
          </p>
          <pre className="overflow-x-auto rounded-lg border-2 border-manga-border bg-manga-card p-3 text-xs text-manga-text">
            {`cd d:\\RESUMEPROJECT
.\\.venv\\Scripts\\python.exe -m uvicorn api.main:app --reload --host 127.0.0.1 --port 8000`}
          </pre>
          <p className="text-xs text-manga-muted">Refresh this page after the API shows “Application startup complete”.</p>
        </div>
      )}

      <section className="grid gap-4 sm:grid-cols-3">
        <HubCard
          title="Create Resume"
          description="Wizard-guided builder with AI and multiple layouts."
          href="/wizard"
          accent="manga-panel-accent"
        />
        <HubCard
          title="ATS Checker"
          description="Upload any resume and see if it passes ATS — with optional JD match."
          href="/ats-check"
          accent="bg-manga-teal/20"
        />
        <HubCard
          title="Interview Prep"
          description="10 role-specific questions from your resume + job posting."
          href="/interview-prep"
          accent="bg-manga-yellow/25"
        />
      </section>

      {stats && (
        <div className="grid grid-cols-3 gap-3 sm:gap-4">
          <StatCard label="Total" value={stats.total} accent="bg-manga-yellow" />
          <StatCard label="Finished" value={stats.finished} accent="bg-manga-teal" />
          <StatCard label="Drafts" value={stats.drafts} accent="bg-manga-accent/30" />
        </div>
      )}

      <section>
        <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
          <h2 className="font-display text-3xl text-manga-text">My Resumes</h2>
          <div className="flex flex-wrap gap-2">
            {(["all", "finished", "draft"] as Tab[]).map((t) => (
              <MangaButton
                key={t}
                variant={tab === t ? "primary" : "ghost"}
                onClick={() => setTab(t)}
                className="!text-xs capitalize"
              >
                {t}
              </MangaButton>
            ))}
          </div>
        </div>

        {filtered.length === 0 ? (
          <div className="speech-bubble text-center">
            <p className="font-display text-xl text-manga-text">
              {tab === "draft" ? "No drafts yet — save progress in the wizard!" : "No resumes here yet."}
            </p>
            <MangaButton href="/wizard" variant="teal" className="mt-4">
              Create one now
            </MangaButton>
          </div>
        ) : (
          <div className="grid gap-4 sm:grid-cols-2">
            {filtered.map((r) => (
              <ResumeCard key={r.id} item={r} onDelete={load} />
            ))}
          </div>
        )}
      </section>

      {profiles.length > 0 && (
        <section>
          <h2 className="mb-4 font-display text-2xl text-manga-text">Profiles</h2>
          <div className="grid gap-3">
            {profiles.map((p) => (
              <div key={p.id} className="manga-panel flex items-center justify-between gap-3">
                <div>
                  <p className="font-bold text-manga-text">{p.full_name}</p>
                  <p className="text-sm text-manga-muted">
                    {p.target_role || "No role"} · {p.email}
                  </p>
                </div>
                <Link href={`/wizard?profile=${p.id}`} className="btn-ghost shrink-0 text-sm">
                  Edit
                </Link>
              </div>
            ))}
          </div>
        </section>
      )}
    </div>
  );
}

function HubCard({
  title,
  description,
  href,
  accent,
}: {
  title: string;
  description: string;
  href: string;
  accent: string;
}) {
  return (
    <Link href={href} className={`manga-panel block transition hover:-translate-y-1 ${accent}`}>
      <h2 className="font-display text-2xl text-manga-text">{title}</h2>
      <p className="mt-2 text-sm text-manga-muted">{description}</p>
      <p className="mt-3 text-xs font-bold text-manga-teal">Open →</p>
    </Link>
  );
}

function StatCard({
  label,
  value,
  accent,
}: {
  label: string;
  value: number;
  accent: string;
}) {
  return (
    <div className={`manga-panel text-center ${accent}`}>
      <p className="font-display text-4xl text-manga-text">{value}</p>
      <p className="text-sm font-bold uppercase tracking-wide text-manga-muted">{label}</p>
    </div>
  );
}

function ResumeCard({ item, onDelete }: { item: ResumeListItem; onDelete: () => void }) {
  const href = item.status === "draft" ? `/wizard?draft=${item.id}` : `/resume/${item.id}`;

  const handleDelete = async (e: React.MouseEvent) => {
    e.preventDefault();
    if (!confirm(`Delete "${item.title}"?`)) return;
    await api.deleteResume(item.id);
    onDelete();
  };

  return (
    <div className="manga-panel group transition hover:-translate-y-1">
      <Link href={href} className="block">
        <div className="flex items-start justify-between gap-2">
          <div className="min-w-0 flex-1">
            <span className={item.status === "draft" ? "badge-draft" : "badge-finished"}>
              {item.status}
            </span>
            <h3 className="mt-2 truncate font-bold text-manga-text">{item.title}</h3>
            <p className="text-xs text-manga-muted">
              Updated {new Date(item.updated_at).toLocaleDateString()}
              {item.status === "draft" && ` · Step ${(item.wizard_step ?? 0) + 1}`}
            </p>
          </div>
          {item.status === "finished" && <ScoreBadge score={item.ats_score} />}
        </div>
        <p className="mt-2 text-xs font-bold text-manga-teal opacity-0 group-hover:opacity-100">
          {item.status === "finished" ? "Open to edit & export →" : "Continue wizard →"}
        </p>
      </Link>
      <button
        type="button"
        onClick={handleDelete}
        className="mt-2 text-xs font-bold text-manga-danger hover:underline"
      >
        Delete
      </button>
    </div>
  );
}

function ScoreBadge({ score }: { score: number }) {
  const bg =
    score >= 80 ? "bg-manga-success/40" : score >= 60 ? "bg-manga-warning/40" : "bg-manga-danger/30";
  return <span className={`badge ${bg}`}>{score.toFixed(0)} ATS</span>;
}
