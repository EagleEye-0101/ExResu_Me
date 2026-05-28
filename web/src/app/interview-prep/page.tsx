"use client";

import { useSearchParams } from "next/navigation";
import { Suspense, useEffect, useState } from "react";
import { MangaButton } from "@/components/MangaButton";
import { api, ResumeListItem } from "@/lib/api";

type Mode = "upload" | "saved";

function InterviewPrepContent() {
  const searchParams = useSearchParams();
  const presetResumeId = searchParams.get("resumeId");
  const [mode, setMode] = useState<Mode>(presetResumeId ? "saved" : "upload");
  const [file, setFile] = useState<File | null>(null);
  const [resumeId, setResumeId] = useState<number | "">(
    presetResumeId ? Number(presetResumeId) : ""
  );
  const [resumes, setResumes] = useState<ResumeListItem[]>([]);
  const [jobDescription, setJobDescription] = useState("");
  const [provider, setProvider] = useState("ollama");
  const [providers, setProviders] = useState<{ id: string; name: string }[]>([]);
  const [questions, setQuestions] = useState<{ question: string; tip: string }[]>([]);
  const [candidateName, setCandidateName] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    api.listResumes({ status: "finished" }).then(setResumes).catch(() => []);
    api.providers().then(setProviders).catch(() => []);
    api.getSettings().then((s) => {
      if (s.default_ai_provider) setProvider(s.default_ai_provider);
    }).catch(() => {});
  }, []);

  const generate = async () => {
    if (!jobDescription.trim()) {
      setError("Paste a job description so questions match the role.");
      return;
    }
    if (mode === "upload" && !file) {
      setError("Upload a resume or switch to a saved resume.");
      return;
    }
    if (mode === "saved" && !resumeId) {
      setError("Select a saved resume.");
      return;
    }
    setLoading(true);
    setError("");
    try {
      const result = await api.interviewPrepUpload({
        file: mode === "upload" ? file ?? undefined : undefined,
        resumeId: mode === "saved" ? Number(resumeId) : undefined,
        jobDescription,
        provider,
      });
      setQuestions(result.questions);
      setCandidateName(result.candidate_name);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to generate questions");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-8">
      <section className="manga-panel-accent">
        <h1 className="font-display text-4xl text-manga-text">Interview Prep</h1>
        <p className="mt-2 text-manga-muted">
          Get 10 tailored interview questions and tips based on your resume and the job posting.
        </p>
      </section>

      <div className="manga-panel space-y-4">
        <div className="flex flex-wrap gap-2">
          <MangaButton
            variant={mode === "upload" ? "primary" : "ghost"}
            onClick={() => setMode("upload")}
            className="!text-xs"
          >
            Upload resume
          </MangaButton>
          <MangaButton
            variant={mode === "saved" ? "primary" : "ghost"}
            onClick={() => setMode("saved")}
            className="!text-xs"
          >
            Use saved resume
          </MangaButton>
        </div>

        {mode === "upload" ? (
          <input
            type="file"
            accept=".pdf,.docx,.txt"
            className="block w-full text-sm"
            onChange={(e) => setFile(e.target.files?.[0] ?? null)}
          />
        ) : (
          <select
            className="input"
            value={resumeId}
            onChange={(e) => setResumeId(e.target.value ? Number(e.target.value) : "")}
          >
            <option value="">Select a finished resume…</option>
            {resumes.map((r) => (
              <option key={r.id} value={r.id}>
                {r.title} (ATS {r.ats_score.toFixed(0)})
              </option>
            ))}
          </select>
        )}

        <label className="block">
          <span className="text-sm font-bold">AI provider</span>
          <select
            className="input mt-1"
            value={provider}
            onChange={(e) => setProvider(e.target.value)}
          >
            {providers.map((p) => (
              <option key={p.id} value={p.id}>
                {p.name}
              </option>
            ))}
          </select>
          <p className="mt-1 text-xs text-manga-muted">Configure API keys in Settings.</p>
        </label>

        <label className="block">
          <span className="text-sm font-bold">Job description</span>
          <textarea
            className="input mt-2 min-h-[200px] font-mono text-sm"
            value={jobDescription}
            onChange={(e) => setJobDescription(e.target.value)}
            placeholder="Paste the job posting…"
          />
        </label>

        {error && <p className="text-sm font-bold text-manga-danger">{error}</p>}
        <MangaButton variant="teal" onClick={generate} disabled={loading}>
          {loading ? "Generating…" : "Generate 10 questions"}
        </MangaButton>
      </div>

      {candidateName && (
        <p className="text-sm text-manga-muted">
          Questions for <strong className="text-manga-text">{candidateName}</strong>
        </p>
      )}

      {questions.length > 0 && (
        <ol className="manga-panel list-decimal space-y-4 pl-6">
          {questions.map((q, i) => (
            <li key={i}>
              <p className="font-bold text-manga-text">{q.question}</p>
              <p className="text-sm text-manga-muted">{q.tip}</p>
            </li>
          ))}
        </ol>
      )}
    </div>
  );
}

export default function InterviewPrepPage() {
  return (
    <Suspense fallback={<p className="text-manga-muted">Loading…</p>}>
      <InterviewPrepContent />
    </Suspense>
  );
}
