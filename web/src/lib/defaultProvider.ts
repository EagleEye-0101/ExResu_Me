export const DEFAULT_PROVIDER = "google_ai_studio";

export function resolveProviderFromSettings(s?: { default_ai_provider?: string }): string {
  const p = s?.default_ai_provider?.trim();
  if (!p || p === "ollama") return DEFAULT_PROVIDER;
  return p;
}
