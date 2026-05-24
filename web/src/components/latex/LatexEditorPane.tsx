"use client";

import dynamic from "next/dynamic";

const EDITOR_HEIGHT_PX = 420;

const Monaco = dynamic(
  () => import("@monaco-editor/react").then((mod) => mod.default),
  {
    ssr: false,
    loading: () => (
      <div
        className="flex min-h-[420px] items-center justify-center rounded-xl border-2 border-manga-border bg-black/90 text-sm text-manga-muted"
        style={{ height: EDITOR_HEIGHT_PX }}
      >
        Loading editor…
      </div>
    ),
  }
);

export function LatexEditorPane({
  value,
  onChange,
}: {
  value: string;
  onChange: (v: string) => void;
}) {
  return (
    <div
      className="overflow-hidden rounded-xl border-2 border-manga-border"
      style={{ minHeight: EDITOR_HEIGHT_PX, height: EDITOR_HEIGHT_PX }}
    >
      <Monaco
        height={EDITOR_HEIGHT_PX}
        defaultLanguage="latex"
        theme="vs-dark"
        value={value}
        onChange={(v) => onChange(v ?? "")}
        options={{
          minimap: { enabled: false },
          fontSize: 13,
          wordWrap: "on",
          scrollBeyondLastLine: false,
          automaticLayout: true,
        }}
      />
    </div>
  );
}
