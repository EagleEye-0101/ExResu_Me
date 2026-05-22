"use client";

import { useEffect, useState } from "react";
import { FormField, TextInput } from "@/components/FormField";
import { api, AppSettings } from "@/lib/api";

const PROVIDER_FIELDS: {
  id: string;
  label: string;
  keyField?: keyof AppSettings;
  modelField: keyof AppSettings;
  keySetField?: keyof AppSettings;
}[] = [
  {
    id: "ollama",
    label: "Ollama (Local)",
    modelField: "ollama_model",
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
    id: "gemini",
    label: "Google Gemini",
    keyField: "gemini_api_key",
    keySetField: "gemini_api_key_set",
    modelField: "gemini_model",
  },
  {
    id: "openrouter",
    label: "OpenRouter",
    keyField: "openrouter_api_key",
    keySetField: "openrouter_api_key_set",
    modelField: "openrouter_model",
  },
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
      setMessage("Settings saved! Restart not needed.");
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
        <p className="text-[var(--muted)]">
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
          <div
            key={p.id}
            className="rounded-xl border-2 border-[var(--border)] bg-[var(--accent-3)]/10 p-4 space-y-3"
          >
            <h3 className="font-display text-xl">{p.label}</h3>
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
                    value=""
                    onChange={(e) =>
                      setSettings((s) => ({ ...s, [p.keyField!]: e.target.value }))
                    }
                    placeholder={settings[p.keySetField!] ? "•••••••• (saved — type to replace)" : "Paste API key"}
                  />
                </FormField>
                <FormField label="Model">
                  <TextInput
                    value={String(settings[p.modelField] || "")}
                    onChange={(v) => setSettings((s) => ({ ...s, [p.modelField]: v }))}
                  />
                </FormField>
              </>
            ) : null}
          </div>
        ))}

        <button onClick={save} disabled={saving} className="btn-primary w-full">
          {saving ? "Saving..." : "Save All Settings"}
        </button>
        {message && (
          <p className={`text-center font-bold ${message.includes("failed") ? "text-[var(--danger)]" : "text-[var(--success)]"}`}>
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
        <button onClick={runTest} className="btn-teal w-full">
          Test provider
        </button>
        {testResult && <p className="text-center font-bold">{testResult}</p>}
      </div>
    </div>
  );
}
