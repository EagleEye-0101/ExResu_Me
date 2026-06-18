"use client";

import { useState } from "react";
import { ATSReportPanel } from "@/components/ATSReport";
import { FileUpload } from "@/components/FileUpload";
import { MangaButton } from "@/components/MangaButton";
import { api, ATSReport } from "@/lib/api";

export default function AtsCheckPage() {
  const [file, setFile] = useState<File | null>(null);
  const [jobDescription, setJobDescription] = useState("");
  const [report, setReport] = useState<ATSReport | null>(null);
  const [summary, setSummary] = useState<{
    full_name: string;
    experience_count: number;
    skills_count: number;
  } | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const runCheck = async () => {
    if (!file) {
      setError("Upload a resume file first.");
      return;
    }
    setLoading(true);
    setError("");
    try {
      const result = await api.atsCheck(file, jobDescription);
      setReport(result.ats_report);
      setSummary({
        full_name: result.resume_summary.full_name,
        experience_count: result.resume_summary.experience_count,
        skills_count: result.resume_summary.skills_count,
      });
    } catch (e) {
      setError(e instanceof Error ? e.message : "Check failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-8">
      <section className="manga-panel-accent">
        <h1 className="font-display text-4xl text-manga-text">ATS Checker</h1>
        <p className="mt-2 text-manga-muted">
          Upload your resume (PDF, DOCX, or TXT) and optionally paste a job description to see if it
          will pass ATS filters.
        </p>
      </section>

      <div className="manga-panel space-y-4">
        <FileUpload
          label="Resume file"
          accept=".pdf,.docx,.txt"
          file={file}
          onChange={setFile}
        />
        <label className="block">
          <span className="text-sm font-bold text-manga-text">
            Job description <span className="font-normal text-manga-muted">(optional, improves keyword score)</span>
          </span>
          <textarea
            className="input mt-2 min-h-[160px] font-mono text-sm"
            value={jobDescription}
            onChange={(e) => setJobDescription(e.target.value)}
            placeholder="Paste the job posting for keyword matching…"
          />
        </label>
        {error && <p className="text-sm font-bold text-manga-danger">{error}</p>}
        <MangaButton variant="primary" burst onClick={runCheck} disabled={loading || !file}>
          {loading ? "Analyzing…" : "Check ATS score"}
        </MangaButton>
      </div>

      {summary && (
        <div className="manga-panel text-sm text-manga-muted">
          Parsed <strong className="text-manga-text">{summary.full_name}</strong> —{" "}
          {summary.experience_count} experience entries, {summary.skills_count} skills detected.
        </div>
      )}

      {report && <ATSReportPanel report={report} />}
    </div>
  );
}
