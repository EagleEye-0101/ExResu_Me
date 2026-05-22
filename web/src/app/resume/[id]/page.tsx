"use client";

import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { useCallback, useEffect, useState } from "react";
import { ATSReportPanel } from "@/components/ATSReport";
import { ResumeEditor } from "@/components/ResumeEditor";
import { api, ATSReport, ResumeData } from "@/lib/api";

type Tab = "edit" | "preview" | "score";

export default function ResumePage() {
  const params = useParams();
  const router = useRouter();
  const id = Number(params.id);
  const [title, setTitle] = useState("");
  const [resume, setResume] = useState<ResumeData | null>(null);
  const [report, setReport] = useState<ATSReport | null>(null);
  const [jobDescription, setJobDescription] = useState("");
  const [provider, setProvider] = useState("ollama");
  const [tab, setTab] = useState<Tab>("edit");
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState("");
  const [saveMsg, setSaveMsg] = useState("");
  const [dirty, setDirty] = useState(false);

  const load = useCallback(() => {
    api
      .getResume(id)
      .then((data) => {
        if (data.status === "draft") {
          router.replace(`/wizard?draft=${id}`);
          return;
        }
        setTitle(data.title || "");
        const r = data.resume ?? null;
        setResume(r);
        setReport(data.ats_report ?? null);
        setJobDescription(data.job_description || "");
        setProvider(data.provider || "ollama");
        setDirty(false);
      })
      .catch(console.error)
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
    setSaveMsg("");
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
    if (dirty) {
      const ok = confirm("Save your edits before re-optimizing?");
      if (ok) await saveChanges();
    }
    setActionLoading("optimize");
    try {
      const result = await api.optimize(id, provider);
      setResume(result.resume);
      setReport(result.ats_report);
      setDirty(false);
    } catch (e) {
      alert(e instanceof Error ? e.message : "Optimize failed");
    } finally {
      setActionLoading("");
    }
  };

  const exportFmt = async (format: string) => {
    if (dirty) {
      const ok = confirm("You have unsaved edits. Save before exporting?");
      if (!ok) return;
      await saveChanges();
    }
    setActionLoading(format);
    try {
      await api.exportResume(id, format);
      window.open(api.downloadUrl(id, format), "_blank");
    } catch (e) {
      alert(e instanceof Error ? e.message : "Export failed");
    } finally {
      setActionLoading("");
    }
  };

  if (loading) return <div className="speech-bubble text-manga-text">Loading...</div>;
  if (!resume || !report) {
    return <p className="font-bold text-manga-danger">Resume not found</p>;
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <Link href="/" className="text-sm font-bold text-manga-accent hover:underline">
            ← Home
          </Link>
          <h1 className="mt-1 font-display text-4xl text-manga-text">{title || resume.full_name}</h1>
          {dirty && (
            <span className="badge-draft mt-1">Unsaved changes</span>
          )}
        </div>
        <div className="flex flex-wrap gap-2">
          <button
            type="button"
            onClick={saveChanges}
            disabled={!!actionLoading || !dirty}
            className="btn-primary"
          >
            {actionLoading === "save" ? "Saving..." : "Save edits"}
          </button>
          <button type="button" onClick={optimize} disabled={!!actionLoading} className="btn-teal">
            Re-optimize
          </button>
          <button type="button" onClick={() => exportFmt("docx")} disabled={!!actionLoading} className="btn-ghost">
            DOCX
          </button>
          <button type="button" onClick={() => exportFmt("pdf")} disabled={!!actionLoading} className="btn-ghost">
            PDF
          </button>
        </div>
      </div>

      {saveMsg && (
        <p className="manga-panel bg-manga-teal/20 text-center font-bold text-manga-text">{saveMsg}</p>
      )}

      <div className="flex flex-wrap gap-2 border-b-2 border-manga-border pb-2">
        {(
          [
            ["edit", "✎ Edit"],
            ["preview", "Preview"],
            ["score", "ATS Score"],
          ] as const
        ).map(([key, label]) => (
          <button
            key={key}
            type="button"
            onClick={() => setTab(key)}
            className={`btn text-sm ${tab === key ? "btn-primary" : "btn-ghost"}`}
          >
            {label}
          </button>
        ))}
      </div>

      {tab === "edit" && (
        <div className="manga-panel">
          <ResumeEditor resume={resume} onChange={handleResumeChange} />
        </div>
      )}

      {tab === "preview" && (
        <div className="manga-panel">
          <pre className="whitespace-pre-wrap rounded-xl border-2 border-manga-border bg-white p-4 font-mono text-sm text-manga-muted">
            {formatResumeText(resume)}
          </pre>
        </div>
      )}

      {tab === "score" && <ATSReportPanel report={report} />}

      <p className="text-center text-sm text-manga-muted">
        Edit here anytime → Save → Export again for an updated DOCX/PDF file.
      </p>
    </div>
  );
}

function formatResumeText(r: ResumeData): string {
  const end = (e: string | undefined) => e || "—";
  const lines = [
    r.full_name,
    `${r.email} | ${r.phone}${r.location ? ` | ${r.location}` : ""}`,
    r.headline,
    "",
    "SUMMARY",
    r.summary,
    "",
    "EXPERIENCE",
  ];
  for (const exp of r.experience) {
    lines.push(`${exp.title} — ${exp.company} (${exp.start_date} – ${end(exp.end_date)})`);
    exp.bullets.forEach((b) => b.trim() && lines.push(`  • ${b}`));
    lines.push("");
  }
  lines.push("EDUCATION");
  r.education.forEach((e) =>
    lines.push(`${e.degree} — ${e.institution} (${e.graduation_date || "—"})`)
  );
  lines.push("", "SKILLS", r.skills.join(", "));
  return lines.join("\n");
}
