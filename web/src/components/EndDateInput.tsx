"use client";

/** End date: explicit Present chip above month picker, or pick a month. */
export function EndDateInput({
  value,
  onChange,
}: {
  value: string;
  onChange: (v: string) => void;
}) {
  const isPresent = value === "Present";
  const htmlValue =
    value && /^\d{2}\/\d{4}$/.test(value)
      ? `${value.split("/")[1]}-${value.split("/")[0]}`
      : "";

  return (
    <div className="rounded-xl border-2 border-dashed border-manga-border bg-manga-yellow/20 p-3">
      <button
        type="button"
        onClick={() => onChange("Present")}
        className={`present-chip ${isPresent ? "present-chip-active" : "present-chip-inactive"}`}
      >
        ✦ Present — I still work here
      </button>

      <p className="mb-1 text-center text-xs font-bold text-manga-muted">— or pick end month —</p>

      <input
        type="month"
        className="input"
        disabled={isPresent}
        value={htmlValue}
        onChange={(e) => {
          if (!e.target.value) {
            onChange("");
            return;
          }
          const [y, m] = e.target.value.split("-");
          onChange(`${m}/${y}`);
        }}
      />
      {!isPresent && !value && (
        <p className="mt-1 text-xs text-manga-muted">Leave empty if unknown</p>
      )}
      {isPresent && (
        <button
          type="button"
          className="mt-2 w-full text-xs font-bold text-manga-accent underline"
          onClick={() => onChange("")}
        >
          Switch to specific end date
        </button>
      )}
    </div>
  );
}
