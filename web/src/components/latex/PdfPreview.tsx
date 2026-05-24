"use client";

import { useEffect, useRef } from "react";

export function PdfPreview({
  pdfUrl,
  title = "Resume PDF",
}: {
  pdfUrl: string | null;
  title?: string;
}) {
  const iframeRef = useRef<HTMLIFrameElement>(null);

  useEffect(() => {
    if (iframeRef.current && pdfUrl) {
      iframeRef.current.src = pdfUrl;
    }
  }, [pdfUrl]);

  if (!pdfUrl) {
    return (
      <div className="flex h-full min-h-[420px] items-center justify-center rounded-xl border-2 border-dashed border-manga-border bg-white/80 p-8 text-center text-manga-muted">
        <p>Compile your LaTeX to see the PDF preview here.</p>
      </div>
    );
  }

  return (
    <iframe
      ref={iframeRef}
      title={title}
      className="h-full min-h-[420px] w-full rounded-xl border-2 border-manga-border bg-white"
      src={pdfUrl}
    />
  );
}
