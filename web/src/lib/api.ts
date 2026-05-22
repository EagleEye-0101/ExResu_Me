const API_BASE = "/api";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    const detail = err.detail;
    if (Array.isArray(detail)) throw new Error(detail.join("; "));
    if (typeof detail === "object" && detail?.errors) {
      throw new Error((detail.errors as string[]).join("; ") || detail.detail || "Validation failed");
    }
    throw new Error(
      typeof detail === "string" ? detail : err.message || `HTTP ${res.status}`
    );
  }
  return res.json();
}

export interface Profile {
  id: number;
  full_name: string;
  email: string;
  phone: string;
  location: string;
  linkedin: string;
  target_role: string;
  years_experience: number;
  headline: string;
  summary_notes: string;
  experience: ExperienceInput[];
  education: EducationInput[];
  skills: string[];
  certifications: { name: string; issuer?: string; date?: string }[];
}

export interface ExperienceInput {
  company: string;
  title: string;
  location?: string;
  start_date: string;
  end_date?: string;
  bullets: string[];
}

export interface EducationInput {
  institution: string;
  degree: string;
  field?: string;
  graduation_date?: string;
  gpa?: string;
}

export interface ResumeListItem {
  id: number;
  profile_id: number;
  title: string;
  status: "draft" | "finished";
  ats_score: number;
  provider: string;
  wizard_step: number;
  created_at: string;
  updated_at: string;
}

export interface ResumeStats {
  total: number;
  drafts: number;
  finished: number;
}

export interface AppSettings {
  default_ai_provider: string;
  openai_api_key: string;
  openai_api_key_set?: boolean;
  openai_model: string;
  anthropic_api_key: string;
  anthropic_api_key_set?: boolean;
  anthropic_model: string;
  gemini_api_key: string;
  gemini_api_key_set?: boolean;
  gemini_model: string;
  openrouter_api_key: string;
  openrouter_api_key_set?: boolean;
  openrouter_model: string;
  ollama_base_url: string;
  ollama_model: string;
}

export interface ATSReport {
  composite_score: number;
  categories: { name: string; score: number; weight: number; weighted_score: number; details: string[] }[];
  fixes: { category: string; severity: string; message: string; action: string }[];
  matched_keywords: string[];
  missing_keywords: string[];
  export_blocked: boolean;
  export_warnings: string[];
}

export interface ResumeData {
  full_name: string;
  email: string;
  phone: string;
  location: string;
  linkedin: string;
  headline: string;
  summary: string;
  experience: ExperienceInput[];
  education: EducationInput[];
  skills: string[];
  certifications: { name: string; issuer?: string; date?: string }[];
}

export const api = {
  health: () => request<{ status: string }>("/health"),
  providers: () => request<{ id: string; name: string; requires_key: boolean }[]>("/providers"),
  testProvider: (provider: string, model?: string) =>
    request<{ success: boolean; error?: string }>("/providers/test", {
      method: "POST",
      body: JSON.stringify({ provider, model }),
    }),
  getSettings: () => request<AppSettings>("/settings"),
  updateSettings: (data: Partial<AppSettings>) =>
    request<AppSettings>("/settings", { method: "PUT", body: JSON.stringify(data) }),
  resumeStats: () => request<ResumeStats>("/resumes/stats"),
  listProfiles: () => request<Profile[]>("/profiles"),
  getProfile: (id: number) => request<Profile>(`/profiles/${id}`),
  createProfile: (data: Omit<Profile, "id">) =>
    request<Profile>("/profiles", { method: "POST", body: JSON.stringify(data) }),
  updateProfile: (id: number, data: Omit<Profile, "id">) =>
    request<Profile>(`/profiles/${id}`, { method: "PUT", body: JSON.stringify(data) }),
  deleteProfile: (id: number) =>
    request<{ ok: boolean }>(`/profiles/${id}`, { method: "DELETE" }),
  listResumes: (opts?: { profileId?: number; status?: string }) => {
    const q = new URLSearchParams();
    if (opts?.profileId) q.set("profile_id", String(opts.profileId));
    if (opts?.status) q.set("status", opts.status);
    const qs = q.toString();
    return request<ResumeListItem[]>(`/resumes${qs ? `?${qs}` : ""}`);
  },
  getResume: (id: number) =>
    request<{
      id: number;
      profile_id: number;
      title: string;
      status: string;
      job_description: string;
      resume?: ResumeData;
      ats_report?: ATSReport;
      provider: string;
      draft?: Record<string, unknown>;
      wizard_step?: number;
    }>(`/resumes/${id}`),
  getDraft: (id: number) => request<Record<string, unknown>>(`/resumes/draft/${id}`),
  saveDraft: (data: {
    profile: Omit<Profile, "id">;
    job_description: string;
    wizard_step: number;
    provider: string;
    draft_id?: number;
    title?: string;
  }) =>
    request<{ id: number; profile_id: number; title: string; status: string }>("/resumes/draft", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  deleteResume: (id: number) =>
    request<{ ok: boolean }>(`/resumes/${id}`, { method: "DELETE" }),
  setResumeStatus: (id: number, status: "draft" | "finished") =>
    request<{ id: number; status: string }>(`/resumes/${id}/status?status=${status}`, {
      method: "PATCH",
    }),
  generate: (
    profileId: number,
    jobDescription: string,
    provider?: string,
    draftId?: number
  ) =>
    request<{ id: number; resume: ResumeData; ats_report: ATSReport }>("/resumes/generate", {
      method: "POST",
      body: JSON.stringify({
        profile_id: profileId,
        job_description: jobDescription,
        provider,
        draft_id: draftId,
      }),
    }),
  optimize: (resumeId: number, provider?: string) =>
    request<{ id: number; resume: ResumeData; ats_report: ATSReport }>("/resumes/optimize", {
      method: "POST",
      body: JSON.stringify({ resume_id: resumeId, provider }),
    }),
  updateResume: (id: number, resume: ResumeData) =>
    request<{ id: number; resume: ResumeData; ats_report: ATSReport }>(`/resumes/${id}`, {
      method: "PUT",
      body: JSON.stringify({ resume }),
    }),
  exportResume: (id: number, format: string) =>
    request<{ filename: string; path: string; ats_score: number; warnings: string[] }>(
      `/resumes/${id}/export`,
      { method: "POST", body: JSON.stringify({ format }) }
    ),
  downloadUrl: (id: number, format: string) => `${API_BASE}/resumes/${id}/download?format=${format}`,
};
