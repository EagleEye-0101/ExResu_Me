const API_BASE = "/api";
const REQUEST_TIMEOUT_MS = 15_000;

export const API_OFFLINE_MESSAGE =
  "Backend API is not running. Start it from the project root: .\\.venv\\Scripts\\python.exe -m uvicorn api.main:app --reload --host 127.0.0.1 --port 8000";

export const API_CLOUD_OFFLINE_MESSAGE =
  "The API is waking up (Render free tier sleeps after ~15 min idle). Wait ~30 seconds and refresh, or try again.";

const GENERIC_GATEWAY_RE =
  /^(bad gateway|service unavailable|gateway time-?out|internal server error|error 502|error 503|error 504)$/i;

export function isLocalDevHost(): boolean {
  if (typeof window === "undefined") return true;
  const host = window.location.hostname;
  return host === "localhost" || host === "127.0.0.1";
}

function fetchWithTimeout(path: string, options?: RequestInit): Promise<Response> {
  const signal =
    options?.signal ??
    (typeof AbortSignal !== "undefined" && "timeout" in AbortSignal
      ? AbortSignal.timeout(REQUEST_TIMEOUT_MS)
      : undefined);
  return fetch(path, { ...options, signal });
}

function isLikelyOfflineResponse(status: number, detail: unknown, raw: string): boolean {
  const text = (typeof detail === "string" ? detail : raw).trim();
  if (status === 503 && /latex compiler|tectonic/i.test(text)) return false;
  if (status === 502 || status === 503 || status === 504) {
    if (!text || GENERIC_GATEWAY_RE.test(text)) return true;
    return text.length < 24;
  }
  if (status !== 500) return false;
  return (
    text.includes("Internal Server Error") ||
    text.includes("ECONNREFUSED") ||
    text.includes("socket hang up") ||
    raw.length < 80
  );
}

function parseErrorResponse(status: number, raw: string): Error {
  let err: { detail?: unknown; message?: string } = { detail: raw || `HTTP ${status}` };
  try {
    err = JSON.parse(raw);
  } catch {
    err = { detail: raw || `HTTP ${status}` };
  }
  const detail = err.detail;
  if (isLikelyOfflineResponse(status, detail, raw)) {
    return new Error(isLocalDevHost() ? API_OFFLINE_MESSAGE : API_CLOUD_OFFLINE_MESSAGE);
  }
  if (Array.isArray(detail)) return new Error(detail.join("; "));
  if (typeof detail === "object" && detail && "errors" in detail) {
    const d = detail as { errors?: string[]; detail?: string };
    return new Error(d.errors?.join("; ") || d.detail || "Validation failed");
  }
  return new Error(typeof detail === "string" ? detail : err.message || `HTTP ${status}`);
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  let res: Response;
  try {
    res = await fetchWithTimeout(`${API_BASE}${path}`, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...options?.headers,
      },
    });
  } catch {
    throw new Error(isLocalDevHost() ? API_OFFLINE_MESSAGE : API_CLOUD_OFFLINE_MESSAGE);
  }
  if (!res.ok) {
    const raw = await res.text();
    throw parseErrorResponse(res.status, raw);
  }
  return res.json();
}

async function fetchFormData<T>(path: string, form: FormData): Promise<T> {
  let res: Response;
  try {
    res = await fetchWithTimeout(`${API_BASE}${path}`, { method: "POST", body: form });
  } catch {
    throw new Error(isLocalDevHost() ? API_OFFLINE_MESSAGE : API_CLOUD_OFFLINE_MESSAGE);
  }
  if (!res.ok) {
    const raw = await res.text();
    throw parseErrorResponse(res.status, raw);
  }
  return res.json();
}

export interface LatexTemplateMeta {
  id: string;
  name: string;
  description: string;
  engine: string;
  thumbnail: string;
  default?: boolean;
}

export interface CompileLatexResponse {
  success: boolean;
  log: string;
  error?: string | null;
  pdf_base64?: string | null;
}

export interface Profile {
  id: number;
  full_name: string;
  email: string;
  phone: string;
  phone_country_code?: string;
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
  template_id?: string;
  wizard_step: number;
  created_at: string;
  updated_at: string;
}

export interface TemplateMeta {
  id: string;
  name: string;
  description: string;
  thumbnail: string;
}

export interface SkillGroup {
  label: string;
  skills: string[];
}

export interface Project {
  name: string;
  context?: string;
  start_date?: string;
  end_date?: string;
  bullets: string[];
}

export interface Activity {
  title: string;
  bullets: string[];
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
  phone_country_code?: string;
  location: string;
  linkedin: string;
  github?: string;
  headline: string;
  summary: string;
  experience: ExperienceInput[];
  education: EducationInput[];
  skills: string[];
  skill_groups?: SkillGroup[];
  projects?: Project[];
  activities?: Activity[];
  certifications: { name: string; issuer?: string; date?: string }[];
}

export interface AtsCheckResult {
  resume_summary: {
    full_name: string;
    email: string;
    experience_count: number;
    education_count: number;
    skills_count: number;
  };
  ats_report: ATSReport;
}

export const api = {
  health: () => request<{ status: string }>("/health"),
  listTemplates: () => request<TemplateMeta[]>("/templates"),
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
      cover_letter?: string;
      parent_id?: number | null;
      has_diff?: boolean;
      template_id?: string;
    }>(`/resumes/${id}`),
  previewUrl: (id: number, template?: string) => {
    const q = template ? `?template=${encodeURIComponent(template)}` : "";
    return `${API_BASE}/resumes/${id}/preview${q}`;
  },
  setResumeTemplate: (id: number, templateId: string) =>
    request<{ id: number; template_id: string }>(`/resumes/${id}/template`, {
      method: "PATCH",
      body: JSON.stringify({ template_id: templateId }),
    }),
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
    draftId?: number,
    templateId?: string
  ) =>
    request<{ id: number; resume: ResumeData; ats_report: ATSReport }>("/resumes/generate", {
      method: "POST",
      body: JSON.stringify({
        profile_id: profileId,
        job_description: jobDescription,
        provider,
        draft_id: draftId,
        template_id: templateId || "professional",
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
  exportResume: (id: number, format: string, templateId?: string) =>
    request<{ filename: string; path: string; ats_score: number; warnings: string[] }>(
      `/resumes/${id}/export`,
      {
        method: "POST",
        body: JSON.stringify({ format, template_id: templateId }),
      }
    ),
  downloadUrl: (id: number, format: string) => `${API_BASE}/resumes/${id}/download?format=${format}`,
  keywordHeatmap: (id: number) =>
    request<{ matched: string[]; missing: string[]; keywords: string[] }>(
      `/resumes/${id}/keyword-heatmap`
    ),
  cloneResume: (id: number, title?: string) =>
    request<{ id: number; title: string }>(`/resumes/${id}/clone`, {
      method: "POST",
      body: JSON.stringify({ title: title || "" }),
    }),
  getDiff: (id: number) =>
    request<{ previous: ResumeData | null; current: ResumeData | null }>(`/resumes/${id}/diff`),
  generateCoverLetter: (id: number, provider?: string) => {
    const q = provider ? `?provider=${encodeURIComponent(provider)}` : "";
    return request<{ cover_letter: string }>(`/resumes/${id}/cover-letter${q}`, {
      method: "POST",
    });
  },
  getCoverLetter: (id: number) => request<{ cover_letter: string }>(`/resumes/${id}/cover-letter`),
  interviewPrep: (id: number, provider?: string) => {
    const q = provider ? `?provider=${encodeURIComponent(provider)}` : "";
    return request<{ questions: { question: string; tip: string }[] }>(
      `/resumes/${id}/interview-prep${q}`,
      { method: "POST" }
    );
  },
  coachBullet: (bullet: string, role: string, provider?: string) =>
    request<{ question: string; suggestion: string }>("/coach/bullet", {
      method: "POST",
      body: JSON.stringify({ bullet, role, provider }),
    }),
  importResume: async (file: File) => {
    const form = new FormData();
    form.append("file", file);
    return fetchFormData<{ profile_id: number; parsed: Record<string, unknown> }>(
      "/import/resume",
      form
    );
  },
  atsCheck: async (file: File, jobDescription: string) => {
    const form = new FormData();
    form.append("file", file);
    form.append("job_description", jobDescription);
    return fetchFormData<AtsCheckResult>("/ats/check", form);
  },
  listLatexTemplates: () =>
    request<{
      templates: LatexTemplateMeta[];
      default_template_id: string;
      compiler_available: boolean;
    }>("/latex/templates"),
  getLatexDemo: (templateId?: string) => {
    const q = templateId ? `?template=${encodeURIComponent(templateId)}` : "";
    return request<{ template_id: string; source: string }>(`/latex/demo${q}`);
  },
  getLatexFromResume: (resumeId: number, templateId?: string) => {
    const q = templateId ? `?template=${encodeURIComponent(templateId)}` : "";
    return request<{ resume_id: number; template_id: string; source: string }>(
      `/latex/from-resume/${resumeId}${q}`
    );
  },
  compileLatex: (source: string, templateId?: string) =>
    request<CompileLatexResponse>("/latex/compile", {
      method: "POST",
      body: JSON.stringify({ source, template_id: templateId }),
    }),
  demoPdfUrl: (templateId?: string) => {
    const q = templateId ? `?template=${encodeURIComponent(templateId)}` : "";
    return `${API_BASE}/latex/demo/pdf${q}`;
  },
  interviewPrepUpload: async (opts: {
    file?: File;
    resumeId?: number;
    jobDescription: string;
    provider?: string;
  }) => {
    const form = new FormData();
    form.append("job_description", opts.jobDescription);
    if (opts.provider) form.append("provider", opts.provider);
    if (opts.resumeId) form.append("resume_id", String(opts.resumeId));
    if (opts.file) form.append("file", opts.file);
    return fetchFormData<{
      questions: { question: string; tip: string }[];
      resume_id: number | null;
      candidate_name: string;
    }>("/interview/prep", form);
  },
};
