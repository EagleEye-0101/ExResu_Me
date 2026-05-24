export interface CountryDial {
  code: string;
  dial: string;
  name: string;
  flag: string;
}

export const COUNTRIES: CountryDial[] = [
  { code: "US", dial: "+1", name: "United States", flag: "🇺🇸" },
  { code: "IN", dial: "+91", name: "India", flag: "🇮🇳" },
  { code: "GB", dial: "+44", name: "United Kingdom", flag: "🇬🇧" },
  { code: "CA", dial: "+1", name: "Canada", flag: "🇨🇦" },
  { code: "AU", dial: "+61", name: "Australia", flag: "🇦🇺" },
  { code: "DE", dial: "+49", name: "Germany", flag: "🇩🇪" },
  { code: "FR", dial: "+33", name: "France", flag: "🇫🇷" },
  { code: "AE", dial: "+971", name: "UAE", flag: "🇦🇪" },
  { code: "SG", dial: "+65", name: "Singapore", flag: "🇸🇬" },
  { code: "PK", dial: "+92", name: "Pakistan", flag: "🇵🇰" },
  { code: "BD", dial: "+880", name: "Bangladesh", flag: "🇧🇩" },
  { code: "PH", dial: "+63", name: "Philippines", flag: "🇵🇭" },
  { code: "MY", dial: "+60", name: "Malaysia", flag: "🇲🇾" },
  { code: "NG", dial: "+234", name: "Nigeria", flag: "🇳🇬" },
  { code: "ZA", dial: "+27", name: "South Africa", flag: "🇿🇦" },
  { code: "BR", dial: "+55", name: "Brazil", flag: "🇧🇷" },
  { code: "MX", dial: "+52", name: "Mexico", flag: "🇲🇽" },
  { code: "JP", dial: "+81", name: "Japan", flag: "🇯🇵" },
  { code: "KR", dial: "+82", name: "South Korea", flag: "🇰🇷" },
  { code: "CN", dial: "+86", name: "China", flag: "🇨🇳" },
  { code: "IT", dial: "+39", name: "Italy", flag: "🇮🇹" },
  { code: "ES", dial: "+34", name: "Spain", flag: "🇪🇸" },
  { code: "NL", dial: "+31", name: "Netherlands", flag: "🇳🇱" },
  { code: "SE", dial: "+46", name: "Sweden", flag: "🇸🇪" },
  { code: "CH", dial: "+41", name: "Switzerland", flag: "🇨🇭" },
  { code: "IE", dial: "+353", name: "Ireland", flag: "🇮🇪" },
  { code: "NZ", dial: "+64", name: "New Zealand", flag: "🇳🇿" },
  { code: "SA", dial: "+966", name: "Saudi Arabia", flag: "🇸🇦" },
  { code: "EG", dial: "+20", name: "Egypt", flag: "🇪🇬" },
  { code: "TR", dial: "+90", name: "Turkey", flag: "🇹🇷" },
];

export function guessDefaultDial(): string {
  if (typeof navigator === "undefined") return "+1";
  const lang = navigator.language || "";
  if (lang.includes("IN")) return "+91";
  if (lang.includes("GB")) return "+44";
  if (lang.includes("AU")) return "+61";
  if (lang.includes("DE")) return "+49";
  return "+1";
}
