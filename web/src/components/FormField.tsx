"use client";

export function FormField({
  label,
  hint,
  required,
  error,
  children,
}: {
  label: string;
  hint?: string;
  required?: boolean;
  error?: string;
  children: React.ReactNode;
}) {
  return (
    <div>
      <label className="label">
        {label}
        {required && <span className="text-manga-accent"> *</span>}
        {hint && <span className="label-hint ml-2">({hint})</span>}
      </label>
      {children}
      {error && <p className="mt-1 text-xs font-bold text-manga-danger">{error}</p>}
    </div>
  );
}

export function TextInput({
  value,
  onChange,
  type = "text",
  placeholder,
  error,
  required,
}: {
  value: string;
  onChange: (v: string) => void;
  type?: string;
  placeholder?: string;
  error?: boolean;
  required?: boolean;
}) {
  return (
    <input
      type={type}
      className={`input ${error ? "input-error" : ""}`}
      value={value}
      onChange={(e) => onChange(e.target.value)}
      placeholder={placeholder}
      required={required}
    />
  );
}

export function MonthInput({
  value,
  onChange,
  error,
  allowPresent,
  presentValue,
}: {
  value: string;
  onChange: (mmYyyy: string) => void;
  error?: boolean;
  allowPresent?: boolean;
  presentValue?: boolean;
}) {
  if (allowPresent && presentValue) {
    return (
      <div className="flex gap-2">
        <span className="input flex items-center bg-[var(--accent-2)]/30 font-bold">Present</span>
        <button
          type="button"
          className="btn-ghost text-sm"
          onClick={() => onChange("")}
        >
          Set date
        </button>
      </div>
    );
  }

  const htmlValue =
    value && /^\d{2}\/\d{4}$/.test(value)
      ? `${value.split("/")[1]}-${value.split("/")[0]}`
      : value && /^\d{4}-\d{2}$/.test(value)
        ? value
        : "";

  return (
    <div className="space-y-2">
      <input
        type="month"
        className={`input ${error ? "input-error" : ""}`}
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
      {allowPresent && (
        <button
          type="button"
          className="text-sm font-bold text-[var(--accent)] underline"
          onClick={() => onChange("Present")}
        >
          Currently working here → Present
        </button>
      )}
      <p className="text-xs text-[var(--muted)]">Format: MM/YYYY</p>
    </div>
  );
}
