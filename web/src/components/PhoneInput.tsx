"use client";

import { COUNTRIES } from "@/lib/countries";

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
    <div className="flex gap-2">
      <select
        className="input w-36 shrink-0"
        value={countryCode}
        onChange={(e) => onCountryChange(e.target.value)}
        aria-label="Country code"
      >
        {COUNTRIES.map((c) => (
          <option key={c.code + c.dial} value={c.dial}>
            {c.flag} {c.dial} {c.name}
          </option>
        ))}
      </select>
      <input
        type="tel"
        className="input flex-1"
        value={phone}
        onChange={(e) => onPhoneChange(e.target.value.replace(/[^\d\s\-()]/g, ""))}
        placeholder="Phone number"
      />
    </div>
  );
}
