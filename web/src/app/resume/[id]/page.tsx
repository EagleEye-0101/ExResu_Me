"use client";

import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { useCallback, useEffect, useState } from "react";
import { ATSReportPanel } from "@/components/ATSReport";
import { KeywordHeatmap } from "@/components/KeywordHeatmap";
import { MangaButton } from "@/components/MangaButton";
import { ResumeEditor } from "@/components/ResumeEditor";
import { ResumePreview } from "@/components/ResumePreview";
import { TemplatePicker } from "@/components/TemplatePicker";
import { api, ATSReport, ResumeData } from "@/lib/api";

type Tab = "edit" | "preview" | "score" | "keywords" | "cover" | "diff" | "interview";

function Stickers({ score }: { score: number }) {
  const stickers = [];
  if (score >= 80) stickers.push({ label: "ATS 80+", emoji: "🔥" });
  if (score >= 90) stickers.push({ label: "Elite 90+", emoji: "⚡" });
  if (score >= 95) stickers.push({ label: "Max 95+", emoji: "👑" });
  if (!stickers.length) return null;
  return (
    <div className="flex flex-wrap gap-2">
      {stickers.map((s) => (
        <span key={s.label} className="sticker bg-manga-yellow">
          {s.emoji} {s.label}
        </span>
      ))}
    </div>
  );
}

export default function ResumePage() {
  const params = useParams();
  const router = useRouter();
  const id = Number(params.id);
  const [title, setTitle] = useState("");
  const [resume, setResume] = useState<ResumeData | null>(null);
  const [report, setReport] = useState<ATSReport | null>(null);
  const [coverLetter, setCoverLetter] = useState("");
  const [provider, setProvider] = useState("ollama");
  const [tab, setTab] = useState<Tab>("edit");
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState("");
  const [saveMsg, setSaveMsg] = useState("");
  const [dirty, setDirty] = useState(false);
  const [diff, setDiff] = useState<{ previous: ResumeData | null; current: ResumeData | null } | null>(null);
  const [questions, setQuestions] = useState<{ question: string; tip: string }[]>([]);
  const [loadError, setLoadError] = useState("");
  const [templateId, setTemplateId] = useState("professional");

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
        setTemplateId(data.template_id || "professional");
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
      setSaveMsg("Saved! ATS score updated.");
      setTimeout(() => setSaveMsg(""), 4000);
    } catch (e) {
      setSaveMsg(e instanceof Error ? e.message : "Save failed");
    } finally {
      setActionLoading("");
    }
  };

  const optimize = async () => {
    if (dirty && !confirm("Save edits before re-optimize?")) return;
    if (dirty) await saveChanges();
    setActionLoading("optimize");
    try {
      const result = await api.optimize(id, provider);
      setResume(result.resume);
      setReport(result.ats_report);
      setDirty(false);
      const d = await api.getDiff(id);
      setDiff(d);
      setTab("diff");
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
      setTab("cover");
    } catch (e) {
      alert(e instanceof Error ? e.message : "Failed");
    } finally {
      setActionLoading("");
    }
  };

  const loadInterview = async () => {
    setActionLoading("interview");
    try {
      const r = await api.interviewPrep(id, provider);
      setQuestions(r.questions);
      setTab("interview");
    } catch (e) {
      alert(e instanceof Error ? e.message : "Failed");
    } finally {
      setActionLoading("");
    }
  };

  const copyHeadline = () => {
    if (resume?.headline) navigator.clipboard.writeText(resume.headline);
  };

  const cloneVersion = async () => {
    const r = await api.cloneResume(id);
    router.push(`/resume/${r.id}`);
  };

  if (loading) return <div className="speech-bubble">Loading...</div>;
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

  const tabs: { key: Tab; label: string }[] = [
    { key: "edit", label: "Edit" },
    { key: "preview", label: "Preview" },
    { key: "score", label: "ATS" },
    { key: "keywords", label: "Keywords" },
    { key: "cover", label: "Cover letter" },
    { key: "diff", label: "Diff" },
    { key: "interview", label: "Interview" },
  ];

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <Link href="/" className="text-sm font-bold text-manga-accent hover:underline">
            ← Home
          </Link>
          <h1 className="mt-1 font-display text-4xl">{title || resume.full_name}</h1>
          <Stickers score={report.composite_score} />
          {dirty && <span className="badge-draft mt-2 ml-2">Unsaved</span>}
        </div>
        <div className="flex max-w-md flex-wrap justify-end gap-2">
          <MangaButton variant="primary" onClick={saveChanges} disabled={!!actionLoading || !dirty}>
            {actionLoading === "save" ? "Saving..." : "Save"}
          </MangaButton>
          <MangaButton variant="teal" onClick={optimize} disabled={!!actionLoading}>
            Re-optimize
          </MangaButton>
          <MangaButton variant="ghost" onClick={() => exportFmt("pdf")} disabled={!!actionLoading}>
            {actionLoading === "pdf" ? "…" : "PDF"}
          </MangaButton>
          <MangaButton variant="ghost" onClick={() => exportFmt("docx")} disabled={!!actionLoading}>
            {actionLoading === "docx" ? "…" : "DOCX"}
          </MangaButton>
          <MangaButton variant="ghost" onClick={cloneVersion}>
            Clone
          </MangaButton>
          <MangaButton variant="ghost" onClick={copyHeadline}>
            Copy headline
          </MangaButton>
        </div>
      </div>

      {saveMsg && <p className="manga-panel bg-manga-teal/20 text-center font-bold">{saveMsg}</p>}

      <div className="flex flex-wrap gap-2 border-b-2 border-manga-border pb-2">
        {tabs.map((t) => (
          <MangaButton
            key={t.key}
            variant={tab === t.key ? "primary" : "ghost"}
            onClick={() => setTab(t.key)}
            className="!py-1 !text-xs"
          >
            {t.label}
          </MangaButton>
        ))}
      </div>

      {tab === "edit" && (
        <div className="manga-panel">
          <ResumeEditor resume={resume} onChange={handleResumeChange} />
        </div>
      )}
      {tab === "preview" && (
        <div className="manga-panel space-y-4">
          <div>
            <p className="mb-2 text-sm font-bold text-manga-muted">Layout template</p>
            <TemplatePicker
              value={templateId}
              onChange={async (tid) => {
                setTemplateId(tid);
                await api.setResumeTemplate(id, tid).catch(() => {});
              }}
            />
          </div>
          <ResumePreview resumeId={id} templateId={templateId} />
          <div className="flex flex-wrap gap-2 pt-2">
            <MangaButton
              variant="primary"
              onClick={() => exportFmt("pdf")}
              disabled={!!actionLoading}
            >
              Download PDF
            </MangaButton>
            <MangaButton variant="ghost" onClick={() => exportFmt("docx")} disabled={!!actionLoading}>
              Download DOCX
            </MangaButton>
          </div>
        </div>
      )}
      {tab === "score" && <ATSReportPanel report={report} />}
      {tab === "keywords" && (
        <div className="manga-panel">
          <KeywordHeatmap resumeId={id} />
        </div>
      )}
      {tab === "cover" && (
        <div className="manga-panel space-y-4">
          <MangaButton variant="primary" burst onClick={genCover} disabled={!!actionLoading}>
            Generate cover letter
          </MangaButton>
          <textarea
            className="input min-h-[300px]"
            value={coverLetter}
            onChange={(e) => setCoverLetter(e.target.value)}
            placeholder="Generate a cover letter, then edit it here before copying."
          />
        </div>
      )}
      {tab === "diff" && (
        <div className="manga-panel space-y-4">
          {!diff?.previous ? (
            <p className="text-manga-muted">Run Re-optimize to capture a before/after diff.</p>
          ) : (
            <>
              <h4 className="font-display text-xl">Before summary</h4>
              <pre className="text-xs opacity-70">{diff.previous.summary}</pre>
              <h4 className="font-display text-xl">After summary</h4>
              <pre className="text-xs">{diff.current?.summary}</pre>
            </>
          )}
        </div>
      )}
      {tab === "interview" && (
        <div className="manga-panel space-y-4">
          <MangaButton variant="teal" onClick={loadInterview} disabled={!!actionLoading}>
            Generate 10 questions
          </MangaButton>
          <ol className="list-decimal space-y-3 pl-5">
            {questions.map((q, i) => (
              <li key={i}>
                <p className="font-bold">{q.question}</p>
                <p className="text-sm text-manga-muted">{q.tip}</p>
              </li>
            ))}
          </ol>
        </div>
      )}
    </div>
  );
}

function formatResumeText(r: ResumeData): string {
  const end = (e?: string) => e || "—";
  const phone = r.phone_country_code ? `${r.phone_country_code} ${r.phone}` : r.phone;
  const lines = [r.full_name, `${r.email} | ${phone}`, r.headline, "", "SUMMARY", r.summary, "", "EXPERIENCE"];
  for (const exp of r.experience) {
    lines.push(`${exp.title} — ${exp.company} (${exp.start_date} – ${end(exp.end_date)})`);
    exp.bullets.forEach((b) => b.trim() && lines.push(`  • ${b}`));
    lines.push("");
  }
  lines.push("EDUCATION");
  r.education.forEach((e) => lines.push(`${e.degree} — ${e.institution}`));
  lines.push("", "SKILLS", r.skills.join(", "));
  return lines.join("\n");
}
