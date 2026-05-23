"use client";

import { COUNTRIES } from "@/lib/countries";

/** Country dial code + national number in one combined field (single border). */
export function PhoneInput({
  countryCode,
  phone,
  onCountryChange,
  onPhoneChange,
}: {
  countryCode: string;
  phone: string;
  onCountryChange: (dial: string) => void;
  onPhoneChange: (national: string) => void;
}) {
  return (
    <div className="phone-input-combo flex w-full max-w-full items-stretch overflow-hidden rounded-xl border-[3px] border-manga-border bg-manga-card shadow-[2px_2px_0_var(--shadow)] focus-within:ring-[3px] focus-within:ring-manga-teal">
      <select
        className="min-w-0 max-w-[7.5rem] shrink-0 cursor-pointer border-0 border-r-[3px] border-manga-border bg-manga-card px-2 py-2.5 text-sm font-bold text-manga-text focus:outline-none focus:ring-0 sm:max-w-[8.5rem]"
        value={countryCode}
        onChange={(e) => onCountryChange(e.target.value)}
        aria-label="Country code"
      >
        {COUNTRIES.map((c) => (
          <option key={c.code + c.dial} value={c.dial}>
            {c.flag} {c.dial}
          </option>
        ))}
      </select>
      <input
        type="tel"
        className="min-w-0 flex-1 border-0 bg-transparent px-3 py-2.5 font-comic text-manga-text focus:outline-none focus:ring-0"
        value={phone}
        onChange={(e) => onPhoneChange(e.target.value.replace(/[^\d\s\-()]/g, ""))}
        placeholder="Phone number"
        aria-label="Phone number"
      />
    </div>
  );
}
