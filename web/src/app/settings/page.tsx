"use client";

import { useEffect, useState } from "react";
import { FormField, TextInput } from "@/components/FormField";
import { MangaButton } from "@/components/MangaButton";
import { api, AppSettings } from "@/lib/api";

const PROVIDER_FIELDS: {
  id: string;
  label: string;
  keyField?: keyof AppSettings;
  modelField: keyof AppSettings;
  keySetField?: keyof AppSettings;
  setupHint?: string;
  modelPlaceholder?: string;
}[] = [
  { id: "ollama", label: "Ollama (Local)", modelField: "ollama_model" },
  {
    id: "gemini",
    label: "Google AI Studio (Gemini — free API)",
    keyField: "gemini_api_key",
    keySetField: "gemini_api_key_set",
    modelField: "gemini_model",
    modelPlaceholder: "gemini-3-flash-preview",
    setupHint: "Default: Gemini 3 Flash (gemini-3-flash-preview). Fallback: gemini-2.5-flash.",
  },
  {
    id: "openai",
    label: "OpenAI",
    keyField: "openai_api_key",
    keySetField: "openai_api_key_set",
    modelField: "openai_model",
  },
  {
    id: "anthropic",
    label: "Anthropic",
    keyField: "anthropic_api_key",
    keySetField: "anthropic_api_key_set",
    modelField: "anthropic_model",
  },
  {
    id: "openrouter",
    label: "OpenRouter",
    keyField: "openrouter_api_key",
    keySetField: "openrouter_api_key_set",
    modelField: "openrouter_model",
  },
];

const GEMINI_FLASH_MODELS = [
  { id: "gemini-3-flash-preview", label: "Gemini 3 Flash (recommended)" },
  { id: "gemini-2.5-flash", label: "Gemini 2.5 Flash" },
  { id: "gemini-flash-latest", label: "Gemini Flash Latest" },
  { id: "gemini-2.5-flash-lite", label: "Gemini 2.5 Flash Lite" },
  { id: "gemini-3.1-flash-lite-preview", label: "Gemini 3.1 Flash Lite Preview" },
];

const GEMINI_HIGH_MODELS = [
  { id: "gemini-2.5-pro", label: "Gemini 2.5 Pro (high — may need billing)" },
  { id: "gemini-3.1-pro-preview", label: "Gemini 3.1 Pro Preview (latest high)" },
  { id: "gemini-pro-latest", label: "Gemini Pro Latest" },
  { id: "gemini-3-pro-preview", label: "Gemini 3 Pro Preview (legacy)" },
];

export default function SettingsPage() {
  const [settings, setSettings] = useState<Partial<AppSettings>>({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [testProvider, setTestProvider] = useState("ollama");
  const [testResult, setTestResult] = useState("");
  const [message, setMessage] = useState("");

  useEffect(() => {
    api.getSettings().then(setSettings).finally(() => setLoading(false));
  }, []);

  const save = async () => {
    setSaving(true);
    setMessage("");
    try {
      const updated = await api.updateSettings(settings);
      setSettings(updated);
      setMessage("Settings saved!");
    } catch (e) {
      setMessage(e instanceof Error ? e.message : "Save failed");
    } finally {
      setSaving(false);
    }
  };

  const runTest = async () => {
    setTestResult("Testing...");
    try {
      const r = await api.testProvider(testProvider);
      setTestResult(r.success ? "Connection OK!" : r.error || "Failed");
    } catch (e) {
      setTestResult(e instanceof Error ? e.message : "Test failed");
    }
  };

  if (loading) return <div className="speech-bubble">Loading settings...</div>;

  return (
    <div className="max-w-2xl space-y-8">
      <div className="speech-bubble">
        <h1 className="font-display text-4xl">Power-Ups</h1>
        <p className="text-manga-muted">
          API keys are stored locally on your machine (SQLite). Never sent anywhere except the AI provider.
        </p>
      </div>

      <div className="manga-panel space-y-6">
        <FormField label="Default AI provider">
          <select
            className="input"
            value={settings.default_ai_provider || "ollama"}
            onChange={(e) =>
              setSettings((s) => ({ ...s, default_ai_provider: e.target.value }))
            }
          >
            {PROVIDER_FIELDS.map((p) => (
              <option key={p.id} value={p.id}>
                {p.label}
              </option>
            ))}
          </select>
        </FormField>

        {PROVIDER_FIELDS.map((p) => (
          <div key={p.id} className="provider-card rounded-xl border-2 border-manga-border p-4 space-y-3">
            <h3 className="font-display text-xl">{p.label}</h3>
            {p.setupHint && (
              <p className="text-sm text-manga-muted">
                {p.setupHint.includes("aistudio.google.com") ? (
                  <>
                    Get a free API key at{" "}
                    <a
                      href="https://aistudio.google.com/apikey"
                      target="_blank"
                      rel="noopener noreferrer"
                      className="font-bold text-manga-accent underline"
                    >
                      Google AI Studio
                    </a>{" "}
                    and paste it below.
                  </>
                ) : (
                  p.setupHint
                )}
              </p>
            )}
            {p.id === "ollama" ? (
              <>
                <FormField label="Base URL">
                  <TextInput
                    value={String(settings.ollama_base_url || "")}
                    onChange={(v) => setSettings((s) => ({ ...s, ollama_base_url: v }))}
                    placeholder="http://localhost:11434"
                  />
                </FormField>
                <FormField label="Model">
                  <TextInput
                    value={String(settings.ollama_model || "")}
                    onChange={(v) => setSettings((s) => ({ ...s, ollama_model: v }))}
                    placeholder="llama3.1"
                  />
                </FormField>
              </>
            ) : p.keyField ? (
              <>
                <FormField
                  label="API key"
                  hint={
                    p.keySetField && settings[p.keySetField]
                      ? "Key saved — enter new value to replace"
                      : "paste key"
                  }
                >
                  <input
                    type="password"
                    className="input"
                    onChange={(e) =>
                      setSettings((s) => ({ ...s, [p.keyField!]: e.target.value }))
                    }
                    placeholder={
                      settings[p.keySetField!]
                        ? "•••••••• (saved — type to replace)"
                        : "Paste API key"
                    }
                  />
                </FormField>
                {p.id === "gemini" ? (
                  <>
                    <FormField label="Model (Flash — free tier)">
                      <select
                        className="input"
                        value={String(settings.gemini_model || "gemini-3-flash-preview")}
                        onChange={(e) =>
                          setSettings((s) => ({ ...s, gemini_model: e.target.value }))
                        }
                      >
                        {GEMINI_FLASH_MODELS.map((m) => (
                          <option key={m.id} value={m.id}>
                            {m.label}
                          </option>
                        ))}
                      </select>
                    </FormField>
                    <FormField
                      label="Model (High / Pro — reasoning)"
                      hint="Often 429 on free keys; enable billing in AI Studio for Pro"
                    >
                      <select
                        className="input"
                        onChange={(e) =>
                          setSettings((s) => ({ ...s, gemini_model: e.target.value }))
                        }
                        value={
                          GEMINI_HIGH_MODELS.some((m) => m.id === settings.gemini_model)
                            ? String(settings.gemini_model)
                            : ""
                        }
                      >
                        <option value="">— use Flash model above —</option>
                        {GEMINI_HIGH_MODELS.map((m) => (
                          <option key={m.id} value={m.id}>
                            {m.label}
                          </option>
                        ))}
                      </select>
                    </FormField>
                  </>
                ) : (
                  <FormField label="Model" hint={p.modelPlaceholder ? `e.g. ${p.modelPlaceholder}` : undefined}>
                    <TextInput
                      value={String(settings[p.modelField] || "")}
                      onChange={(v) => setSettings((s) => ({ ...s, [p.modelField]: v }))}
                      placeholder={p.modelPlaceholder || ""}
                    />
                  </FormField>
                )}
              </>
            ) : null}
          </div>
        ))}

        <MangaButton variant="primary" burst className="w-full" onClick={save} disabled={saving}>
          {saving ? "Saving..." : "Save All Settings"}
        </MangaButton>
        {message && (
          <p
            className={`text-center font-bold ${
              message.includes("failed") ? "text-manga-danger" : "text-manga-success"
            }`}
          >
            {message}
          </p>
        )}
      </div>

      <div className="manga-panel space-y-4">
        <h2 className="font-display text-2xl">Test connection</h2>
        <select
          className="input"
          value={testProvider}
          onChange={(e) => setTestProvider(e.target.value)}
        >
          {PROVIDER_FIELDS.map((p) => (
            <option key={p.id} value={p.id}>
              {p.label}
            </option>
          ))}
        </select>
        <MangaButton variant="teal" className="w-full" onClick={runTest}>
          {testResult === "Testing..." ? "Testing..." : "Test Provider"}
        </MangaButton>
        {testResult && testResult !== "Testing..." && (
          <p
            className={`text-center font-bold ${
              testResult.includes("OK") ? "text-manga-success" : "text-manga-danger"
            }`}
          >
            {testResult}
          </p>
        )}
      </div>
    </div>
  );
}
