"use client";

import { useEffect, useState } from "react";
import { countSkills, parseSkillsInput } from "@/lib/skills";

export function SkillsInput({
  skills,
  onChange,
  minForGenerate = 3,
}: {
  skills: string[];
  onChange: (skills: string[]) => void;
  minForGenerate?: number;
}) {
  const [draft, setDraft] = useState("");
  const count = countSkills(skills);

  // Fix legacy saves where every skill was stored as one comma-separated string
  useEffect(() => {
    if (skills.length === 1 && /[,;|\n]/.test(skills[0])) {
      onChange(parseSkillsInput(skills[0]));
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps -- run once when loading bad data
  }, []);

  const addFromDraft = () => {
    const parsed = parseSkillsInput(draft);
    if (!parsed.length) return;
    const seen = new Set(skills.map((s) => s.toLowerCase()));
    const merged = [...skills];
    for (const s of parsed) {
      const key = s.toLowerCase();
      if (!seen.has(key)) {
        seen.add(key);
        merged.push(s);
      }
    }
    onChange(merged);
    setDraft("");
  };

  const remove = (index: number) => {
    onChange(skills.filter((_, i) => i !== index));
  };

  const onPaste = (e: React.ClipboardEvent<HTMLInputElement>) => {
    const text = e.clipboardData.getData("text");
    if (!text.includes(",") && !text.includes(";") && !text.includes("\n")) return;
    e.preventDefault();
    const parsed = parseSkillsInput(text);
    if (!parsed.length) return;
    const seen = new Set(skills.map((s) => s.toLowerCase()));
    const merged = [...skills];
    for (const s of parsed) {
      const key = s.toLowerCase();
      if (!seen.has(key)) {
        seen.add(key);
        merged.push(s);
      }
    }
    onChange(merged);
    setDraft("");
  };

  return (
    <div className="space-y-3">
      <div className="flex flex-wrap items-center gap-2">
        <input
          type="text"
          className="input min-w-[12rem] flex-1"
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" || e.key === ",") {
              e.preventDefault();
              addFromDraft();
            }
          }}
          onBlur={() => draft.trim() && addFromDraft()}
          onPaste={onPaste}
          placeholder="Type a skill, then Enter or comma"
        />
        <button type="button" className="manga-btn manga-btn-ghost shrink-0 !py-2 !text-xs" onClick={addFromDraft}>
          Add
        </button>
      </div>
      <p className="text-xs text-manga-muted">
        Separate with <strong>commas</strong>, <strong>semicolons</strong>, or <strong>new lines</strong> — e.g. paste
        &quot;Python, React, AWS&quot; or one skill per line. Count:{" "}
        <span className={count >= minForGenerate ? "text-manga-success font-bold" : "text-manga-warning font-bold"}>
          {count}
        </span>{" "}
        / {minForGenerate} min to generate
      </p>
      {skills.length > 0 ? (
        <ul className="flex flex-wrap gap-2">
          {skills.map((skill, i) => (
            <li key={`${skill}-${i}`}>
              <span className="inline-flex items-center gap-1 rounded-full border-2 border-manga-border bg-manga-card px-3 py-1 text-sm font-bold text-manga-text">
                {skill}
                <button
                  type="button"
                  className="text-manga-danger hover:underline"
                  aria-label={`Remove ${skill}`}
                  onClick={() => remove(i)}
                >
                  ×
                </button>
              </span>
            </li>
          ))}
        </ul>
      ) : (
        <p className="rounded-xl border-2 border-dashed border-manga-border p-4 text-center text-sm text-manga-muted">
          No skills yet — add at least {minForGenerate} before generating
        </p>
      )}
    </div>
  );
}
