"use client";

import Link from "next/link";
import { useParams, useRouter, useSearchParams } from "next/navigation";
import { Suspense, useCallback, useEffect, useState } from "react";
import { ActionMenu, ActionMenuItem } from "@/components/ActionMenu";
import { ATSReportPanel } from "@/components/ATSReport";
import { KeywordHeatmap } from "@/components/KeywordHeatmap";
import { MangaButton } from "@/components/MangaButton";
import { ResumeEditor } from "@/components/ResumeEditor";
import { ResumePreview } from "@/components/ResumePreview";
import { SegmentedTabs } from "@/components/SegmentedTabs";
import { TemplatePicker } from "@/components/TemplatePicker";
import { api, ATSReport, ResumeData } from "@/lib/api";

type Tab = "edit" | "preview" | "ats" | "tools";

const TABS: { key: Tab; label: string }[] = [
  { key: "edit", label: "Edit" },
  { key: "preview", label: "Preview" },
  { key: "ats", label: "ATS" },
  { key: "tools", label: "Tools" },
];

function ResumePageInner() {
  const params = useParams();
  const router = useRouter();
  const searchParams = useSearchParams();
  const id = Number(params.id);
  const initialTab = (searchParams.get("tab") as Tab) || "edit";
  const [title, setTitle] = useState("");
  const [resume, setResume] = useState<ResumeData | null>(null);
  const [report, setReport] = useState<ATSReport | null>(null);
  const [coverLetter, setCoverLetter] = useState("");
  const [provider, setProvider] = useState("ollama");
  const [tab, setTab] = useState<Tab>(
    TABS.some((t) => t.key === initialTab) ? initialTab : "edit"
  );
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState("");
  const [saveMsg, setSaveMsg] = useState("");
  const [dirty, setDirty] = useState(false);
  const [diff, setDiff] = useState<{ previous: ResumeData | null; current: ResumeData | null } | null>(
    null
  );
  const [loadError, setLoadError] = useState("");
  const [templateId, setTemplateId] = useState("compact");

  const load = useCallback(() => {
    if (!Number.isFinite(id) || id <= 0) {
      setLoadError("Invalid resume ID");
      setLoading(false);
      return;
    }
    setLoadError("");
    api
      .getResume(id)
      .then(async (data) => {
        if (data.status === "draft") {
          router.replace(`/wizard?draft=${id}`);
          return;
        }
        setTitle(data.title || "");
        const r = data.resume ?? null;
        setResume(r);
        setReport(data.ats_report ?? null);
        setProvider(data.provider || "ollama");
        setTemplateId(data.template_id || "compact");
        setDirty(false);
        const cl = await api.getCoverLetter(id).catch(() => ({ cover_letter: "" }));
        setCoverLetter(cl.cover_letter || data.cover_letter || "");
        if (data.has_diff) {
          const d = await api.getDiff(id).catch(() => null);
          setDiff(d);
        }
      })
      .catch((e) => setLoadError(e instanceof Error ? e.message : "Failed to load resume"))
      .finally(() => setLoading(false));
  }, [id, router]);

  useEffect(() => {
    load();
  }, [load]);

  const handleResumeChange = (r: ResumeData) => {
    setResume(r);
    setDirty(true);
  };

  const saveChanges = async () => {
    if (!resume) return;
    setActionLoading("save");
    try {
      const result = await api.updateResume(id, resume);
      setResume(result.resume);
      setReport(result.ats_report);
      setDirty(false);
      setSaveMsg("Saved — ATS score updated.");
      setTimeout(() => setSaveMsg(""), 4000);
    } catch (e) {
      setSaveMsg(e instanceof Error ? e.message : "Save failed");
    } finally {
      setActionLoading("");
    }
  };

  const optimize = async () => {
    if (dirty && !confirm("Save edits before re-optimizing?")) return;
    if (dirty) await saveChanges();
    setActionLoading("optimize");
    try {
      const result = await api.optimize(id, provider);
      setResume(result.resume);
      setReport(result.ats_report);
      setDirty(false);
      const d = await api.getDiff(id);
      setDiff(d);
      setTab("tools");
    } catch (e) {
      alert(e instanceof Error ? e.message : "Optimize failed");
    } finally {
      setActionLoading("");
    }
  };

  const exportFmt = async (format: string) => {
    if (dirty) {
      if (!confirm("Save unsaved edits before export?")) return;
      await saveChanges();
    }
    setActionLoading(format);
    try {
      await api.exportResume(id, format, templateId);
      window.open(api.downloadUrl(id, format), "_blank");
    } catch (e) {
      alert(e instanceof Error ? e.message : "Export failed");
    } finally {
      setActionLoading("");
    }
  };

  const genCover = async () => {
    setActionLoading("cover");
    try {
      const r = await api.generateCoverLetter(id, provider);
      setCoverLetter(r.cover_letter);
    } catch (e) {
      alert(e instanceof Error ? e.message : "Failed");
    } finally {
      setActionLoading("");
    }
  };

  const cloneVersion = async () => {
    const r = await api.cloneResume(id);
    router.push(`/resume/${r.id}`);
  };

  if (loading) return <div className="speech-bubble">Loading…</div>;
  if (loadError || !resume || !report) {
    return (
      <div className="speech-bubble space-y-3">
        <p className="font-bold text-manga-danger">{loadError || "Resume not found"}</p>
        <MangaButton href="/" variant="ghost">
          ← Home
        </MangaButton>
      </div>
    );
  }

  const score = Math.round(report.composite_score);

  return (
    <div className="space-y-5">
      <header className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div className="min-w-0">
          <Link href="/" className="text-sm font-bold text-manga-accent hover:underline">
            ← Home
          </Link>
          <div className="mt-1 flex flex-wrap items-center gap-2">
            <h1 className="font-display text-3xl sm:text-4xl">{title || resume.full_name}</h1>
            <span className="resume-score-chip" title="ATS composite score">
              ATS {score}
            </span>
            {dirty && <span className="badge badge-draft">Unsaved</span>}
          </div>
        </div>

        <div className="flex flex-shrink-0 flex-wrap items-center gap-2">
          <MangaButton
            variant="primary"
            onClick={saveChanges}
            disabled={!!actionLoading || !dirty}
            className="!text-sm"
          >
            {actionLoading === "save" ? "Saving…" : "Save"}
          </MangaButton>
          <MangaButton
            variant="secondary"
            onClick={optimize}
            disabled={!!actionLoading}
            className="!text-sm"
          >
            Re-optimize
          </MangaButton>
          <ActionMenu label="Export" variant="teal" disabled={!!actionLoading}>
            <ActionMenuItem onClick={() => exportFmt("pdf")} disabled={actionLoading === "pdf"}>
              {actionLoading === "pdf" ? "Exporting PDF…" : "PDF (ReportLab)"}
            </ActionMenuItem>
            <ActionMenuItem onClick={() => exportFmt("docx")} disabled={actionLoading === "docx"}>
              DOCX
            </ActionMenuItem>
            <ActionMenuItem href={`/latex?resumeId=${id}&template=${templateId}`}>
              LaTeX studio (best PDF)
            </ActionMenuItem>
          </ActionMenu>
          <ActionMenu label="More" disabled={!!actionLoading}>
            <ActionMenuItem onClick={cloneVersion}>Clone resume</ActionMenuItem>
            <ActionMenuItem
              onClick={() => resume.headline && navigator.clipboard.writeText(resume.headline)}
              disabled={!resume.headline}
            >
              Copy headline
            </ActionMenuItem>
          </ActionMenu>
        </div>
      </header>

      {saveMsg && (
        <p className="rounded-xl border-2 border-manga-border bg-manga-teal/15 px-4 py-2 text-center text-sm font-bold">
          {saveMsg}
        </p>
      )}

      <SegmentedTabs tabs={TABS} active={tab} onChange={setTab} />

      {tab === "edit" && (
        <div className="manga-panel">
          <ResumeEditor resume={resume} onChange={handleResumeChange} />
        </div>
      )}

      {tab === "preview" && (
        <div className="manga-panel space-y-4">
          <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
            <p className="text-sm font-bold text-manga-muted">Layout</p>
            <TemplatePicker
              compact
              value={templateId}
              onChange={async (tid) => {
                setTemplateId(tid);
                await api.setResumeTemplate(id, tid).catch(() => {});
              }}
            />
          </div>
          <ResumePreview resumeId={id} templateId={templateId} />
          <p className="text-center text-xs text-manga-muted">
            For print-quality PDF, use{" "}
            <Link href={`/latex?resumeId=${id}`} className="font-bold text-manga-accent underline">
              LaTeX studio
            </Link>
            .
          </p>
        </div>
      )}

      {tab === "ats" && (
        <div className="space-y-4">
          <ATSReportPanel report={report} />
          <div className="manga-panel">
            <h3 className="mb-3 font-display text-xl">Keyword heatmap</h3>
            <KeywordHeatmap resumeId={id} />
          </div>
        </div>
      )}

      {tab === "tools" && (
        <div className="manga-panel space-y-6">
          <section className="tools-section space-y-3">
            <h3 className="font-display text-xl">Cover letter</h3>
            <p className="text-sm text-manga-muted">Generate from this resume, then edit before sending.</p>
            <MangaButton variant="primary" onClick={genCover} disabled={!!actionLoading} className="!text-sm">
              {actionLoading === "cover" ? "Generating…" : "Generate cover letter"}
            </MangaButton>
            <textarea
              className="input min-h-[220px]"
              value={coverLetter}
              onChange={(e) => setCoverLetter(e.target.value)}
              placeholder="Your cover letter appears here…"
            />
          </section>

          <section className="tools-section space-y-3">
            <h3 className="font-display text-xl">Optimization diff</h3>
            {!diff?.previous ? (
              <p className="text-sm text-manga-muted">
                Run <strong>Re-optimize</strong> to compare summary before and after.
              </p>
            ) : (
              <div className="grid gap-4 sm:grid-cols-2">
                <div>
                  <p className="mb-1 text-xs font-bold uppercase text-manga-muted">Before</p>
                  <pre className="rounded-lg border-2 border-manga-border bg-black/5 p-3 text-xs dark:bg-white/5">
                    {diff.previous.summary}
                  </pre>
                </div>
                <div>
                  <p className="mb-1 text-xs font-bold uppercase text-manga-muted">After</p>
                  <pre className="rounded-lg border-2 border-manga-border bg-black/5 p-3 text-xs dark:bg-white/5">
                    {diff.current?.summary}
                  </pre>
                </div>
              </div>
            )}
          </section>

          <section className="tools-section space-y-2">
            <h3 className="font-display text-xl">Interview prep</h3>
            <p className="text-sm text-manga-muted">
              Full question generator with job posting — opens in a dedicated flow.
            </p>
            <MangaButton href={`/interview-prep?resumeId=${id}`} variant="teal" className="!text-sm">
              Open interview prep →
            </MangaButton>
          </section>
        </div>
      )}
    </div>
  );
}

export default function ResumePage() {
  return (
    <Suspense fallback={<div className="speech-bubble">Loading…</div>}>
      <ResumePageInner />
    </Suspense>
  );
}
