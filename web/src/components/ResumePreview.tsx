"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";

export function ResumePreview({
  resumeId,
  templateId,
}: {
  resumeId: number;
  templateId: string;
}) {
  const [html, setHtml] = useState<string>("");
  const [error, setError] = useState("");

  useEffect(() => {
    setError("");
    fetch(api.previewUrl(resumeId, templateId))
      .then(async (res) => {
        if (!res.ok) throw new Error(await res.text());
        return res.text();
      })
      .then(setHtml)
      .catch((e) => setError(e instanceof Error ? e.message : "Preview failed"));
  }, [resumeId, templateId]);

  if (error) {
    return <p className="text-manga-danger">{error}</p>;
  }
  if (!html) {
    return <p className="text-manga-muted">Loading preview…</p>;
  }

  return (
    <div
      className="resume-preview overflow-auto rounded-xl border-2 border-manga-border bg-white p-6 text-black shadow-inner"
      dangerouslySetInnerHTML={{ __html: html }}
    />
  );
}
