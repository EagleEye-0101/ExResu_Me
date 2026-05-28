"use client";

export type SegmentedTab<T extends string> = { key: T; label: string };

export function SegmentedTabs<T extends string>({
  tabs,
  active,
  onChange,
}: {
  tabs: SegmentedTab<T>[];
  active: T;
  onChange: (key: T) => void;
}) {
  return (
    <div className="segmented-tabs" role="tablist">
      {tabs.map((t) => (
        <button
          key={t.key}
          type="button"
          role="tab"
          aria-selected={active === t.key}
          className={`segmented-tab ${active === t.key ? "segmented-tab-active" : ""}`}
          onClick={() => onChange(t.key)}
        >
          {t.label}
        </button>
      ))}
    </div>
  );
}
