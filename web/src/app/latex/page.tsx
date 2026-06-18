"use client";

import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { Suspense, useCallback, useEffect, useRef, useState } from "react";
import { LatexEditorPane } from "@/components/latex/LatexEditorPane";
import { LatexTemplateGallery } from "@/components/latex/LatexTemplateGallery";
import { PdfPreview } from "@/components/latex/PdfPreview";
import { MangaButton } from "@/components/MangaButton";
import { api, LatexTemplateMeta } from "@/lib/api";

function LatexStudioInner() {
  const searchParams = useSearchParams();
  const searchKey = searchParams.toString();
  const demoMode = searchParams.get("demo") === "1";
  const queryTemplate = searchParams.get("template") || "compact";
  const resumeIdParam = searchParams.get("resumeId");
  const resumeId = resumeIdParam ? Number(resumeIdParam) : null;

  const [templates, setTemplates] = useState<LatexTemplateMeta[]>([]);
  const [templateId, setTemplateId] = useState(queryTemplate);
  const [source, setSource] = useState("");
  const [pdfUrl, setPdfUrl] = useState<string | null>(null);
  const [log, setLog] = useState("");
  const [error, setError] = useState("");
  const [compilerOk, setCompilerOk] = useState(true);
  const [loading, setLoading] = useState(true);
  const [compiling, setCompiling] = useState(false);
  const [showLog, setShowLog] = useState(false);
  const pdfBlobRef = useRef<string | null>(null);
  const printFrameRef = useRef<HTMLIFrameElement>(null);
  const autoCompiledRef = useRef(false);

  const revokePdf = useCallback(() => {
    if (pdfBlobRef.current) {
      URL.revokeObjectURL(pdfBlobRef.current);
      pdfBlobRef.current = null;
    }
  }, []);

  const loadSource = useCallback(
    async (tid: string) => {
      setLoading(true);
      setError("");
      revokePdf();
      setPdfUrl(null);
      try {
        if (resumeId && !Number.isNaN(resumeId)) {
          const data = await api.getLatexFromResume(resumeId, tid);
          setSource(data.source);
          setTemplateId(data.template_id);
        } else {
          const data = await api.getLatexDemo(tid);
          setSource(data.source);
          setTemplateId(data.template_id);
        }
      } catch (e) {
        setError(e instanceof Error ? e.message : "Failed to load source");
        setSource("");
      } finally {
        setLoading(false);
      }
    },
    [resumeId, revokePdf]
  );

  const handleCompile = useCallback(async () => {
    if (!source || !compilerOk) return;
    setCompiling(true);
    setError("");
    setLog("");
    revokePdf();
    setPdfUrl(null);
    try {
      const result = await api.compileLatex(source, templateId);
      setLog(result.log || "");
      if (!result.success || !result.pdf_base64) {
        setError(result.error || "Compilation failed");
        setShowLog(true);
        return;
      }
      const bytes = Uint8Array.from(atob(result.pdf_base64), (c) => c.charCodeAt(0));
      const blob = new Blob([bytes], { type: "application/pdf" });
      const url = URL.createObjectURL(blob);
      pdfBlobRef.current = url;
      setPdfUrl(url);
      setShowLog(false);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Compile failed");
      setShowLog(true);
    } finally {
      setCompiling(false);
    }
  }, [source, templateId, compilerOk, revokePdf]);

  useEffect(() => {
    autoCompiledRef.current = false;
    api
      .listLatexTemplates()
      .then((r) => {
        setTemplates(r.templates);
        setCompilerOk(r.compiler_available);
      })
      .catch(() => {});
    loadSource(queryTemplate);
    return () => revokePdf();
  }, [searchKey, queryTemplate, loadSource, revokePdf]);

  useEffect(() => {
    if (
      demoMode &&
      source &&
      compilerOk &&
      !loading &&
      !compiling &&
      !autoCompiledRef.current
    ) {
      autoCompiledRef.current = true;
      handleCompile();
    }
  }, [demoMode, source, compilerOk, loading, compiling, handleCompile]);

  const handleTemplateChange = async (tid: string) => {
    autoCompiledRef.current = false;
    setTemplateId(tid);
    await loadSource(tid);
  };

  const handleDownload = () => {
    if (!pdfUrl) return;
    const a = document.createElement("a");
    a.href = pdfUrl;
    a.download = `resume_${templateId}.pdf`;
    a.click();
  };

  const handlePrint = () => {
    if (!pdfUrl) return;
    const frame = printFrameRef.current;
    if (!frame) return;
    frame.src = pdfUrl;
    frame.onload = () => {
      frame.contentWindow?.focus();
      frame.contentWindow?.print();
    };
  };

  const editorReady = !loading && source.length > 0;

  return (
    <div className="space-y-6">
      <section className="manga-panel-accent">
        <p className="font-display text-lg text-manga-accent">LATEX STUDIO</p>
        <h1 className="font-display text-3xl text-manga-text sm:text-4xl">
          LaTeX resume editor
        </h1>
        <p className="mt-2 text-manga-muted">
          Professional LaTeX templates — edit source, compile, download PDF, or print.
          {resumeId ? (
            <>
              {" "}
              Editing resume #{resumeId}.{" "}
              <Link href={`/resume/${resumeId}`} className="text-manga-accent underline">
                Back to resume
              </Link>
            </>
          ) : demoMode ? (
            compilerOk
              ? " Demo resume loaded — compile runs automatically when ready."
              : " Demo resume loaded — install Tectonic on the API server to compile."
          ) : null}
        </p>
        {!compilerOk && (
          <p className="mt-3 rounded-lg border-2 border-manga-danger/40 bg-manga-danger/10 p-3 text-sm text-manga-danger">
            LaTeX compiler not detected on the API server. Install{" "}
            <a
              href="https://tectonic-typesetting.github.io/"
              className="underline"
              target="_blank"
              rel="noreferrer"
            >
              Tectonic
            </a>{" "}
            and restart the API.
          </p>
        )}
      </section>

      <div className="manga-panel space-y-4">
        <p className="text-sm font-bold text-manga-muted">Template</p>
        <LatexTemplateGallery
          templates={templates}
          value={templateId}
          onChange={handleTemplateChange}
        />
      </div>

      <div className="flex flex-wrap items-center gap-2">
        <MangaButton
          variant="primary"
          onClick={handleCompile}
          disabled={compiling || !source || !compilerOk}
        >
          {compiling ? "Compiling…" : "Compile"}
        </MangaButton>
        <MangaButton variant="teal" onClick={handleDownload} disabled={!pdfUrl}>
          Download PDF
        </MangaButton>
        <MangaButton variant="ghost" onClick={handlePrint} disabled={!pdfUrl}>
          Print
        </MangaButton>
        {log && (
          <MangaButton variant="ghost" onClick={() => setShowLog((s) => !s)}>
            {showLog ? "Hide log" : "Show log"}
          </MangaButton>
        )}
        {!resumeId && (
          <MangaButton
            variant="ghost"
            onClick={() => {
              autoCompiledRef.current = false;
              loadSource(templateId);
            }}
            disabled={loading}
          >
            Reset demo
          </MangaButton>
        )}
      </div>

      {error && (
        <div className="rounded-lg border-2 border-manga-danger/40 bg-manga-danger/10 p-3 text-sm text-manga-danger">
          {error}
        </div>
      )}
      {showLog && log && (
        <pre className="max-h-48 overflow-auto rounded-lg border-2 border-manga-border bg-black/90 p-3 text-xs text-green-300">
          {log}
        </pre>
      )}

      {loading ? (
        <p className="text-manga-muted">Loading LaTeX source…</p>
      ) : !editorReady ? (
        <p className="text-manga-muted">No LaTeX source available.</p>
      ) : (
        <div className="grid gap-4 lg:grid-cols-2 lg:gap-6" style={{ minHeight: "480px" }}>
          <div className="flex flex-col">
            <p className="mb-2 text-sm font-bold text-manga-muted">Source (.tex)</p>
            <LatexEditorPane value={source} onChange={setSource} />
          </div>
          <div className="flex flex-col">
            <p className="mb-2 text-sm font-bold text-manga-muted">PDF preview</p>
            <PdfPreview pdfUrl={pdfUrl} />
          </div>
        </div>
      )}

      <iframe ref={printFrameRef} className="hidden" title="print" />
    </div>
  );
}

export default function LatexStudioPage() {
  return (
    <Suspense fallback={<p className="text-manga-muted">Loading LaTeX studio…</p>}>
      <LatexStudioInner />
    </Suspense>
  );
}
