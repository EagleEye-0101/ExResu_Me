"use client";

import { useId } from "react";

export function FileUpload({
  label,
  accept,
  file,
  onChange,
  hint,
}: {
  label: string;
  accept: string;
  file: File | null;
  onChange: (file: File | null) => void;
  hint?: string;
}) {
  const inputId = useId();

  return (
    <div>
      <span className="text-sm font-bold text-manga-text">{label}</span>
      <div className="mt-2 flex flex-wrap items-center gap-3">
        <label htmlFor={inputId} className="file-upload-btn manga-btn manga-btn-ghost cursor-pointer">
          Choose file
        </label>
        <input
          id={inputId}
          type="file"
          accept={accept}
          className="sr-only"
          onChange={(e) => onChange(e.target.files?.[0] ?? null)}
        />
        {file ? (
          <span className="text-xs text-manga-muted">
            {file.name} ({(file.size / 1024).toFixed(1)} KB)
          </span>
        ) : (
          <span className="text-xs text-manga-muted">No file selected</span>
        )}
      </div>
      {hint && <p className="mt-1 text-xs text-manga-muted">{hint}</p>}
    </div>
  );
}
