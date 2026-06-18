"use client";

import { useRouter, useSearchParams } from "next/navigation";
import { Suspense, useEffect, useState } from "react";
import { EndDateInput } from "@/components/EndDateInput";
import { FormField, MonthInput, TextInput } from "@/components/FormField";
import { MangaButton } from "@/components/MangaButton";
import { PhoneInput } from "@/components/PhoneInput";
import { SkillsInput } from "@/components/SkillsInput";
import { TemplatePicker } from "@/components/TemplatePicker";
import { guessDefaultDial } from "@/lib/countries";
import {
  api,
  EducationInput,
  ExperienceInput,
  Profile,
} from "@/lib/api";
import { DEFAULT_PROVIDER, resolveProviderFromSettings } from "@/lib/defaultProvider";
import { validateStep } from "@/lib/validation";

const STEPS = ["Profile", "Experience", "Education", "Skills", "Job Posting", "Generate"];
const STEP_HINTS = [
  "Name & contact required. Rest is optional but helps ATS.",
  "Add jobs you've actually held. Required before generate.",
  "Optional — skip if you prefer.",
  "At least 3 skills required to generate.",
  "Paste the full job ad — required to generate.",
  "Pick AI & create your resume!",
];

const emptyProfile = (): Omit<Profile, "id"> => ({
  full_name: "",
  email: "",
  phone: "",
  phone_country_code: "+1",
  location: "",
  linkedin: "",
  target_role: "",
  years_experience: 0,
  headline: "",
  summary_notes: "",
  experience: [],
  education: [],
  skills: [],
  certifications: [],
});

function WizardContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const editProfileId = searchParams.get("profile");
  const draftIdParam = searchParams.get("draft");

  const [step, setStep] = useState(0);
  const [profile, setProfile] = useState<Omit<Profile, "id">>(emptyProfile());
  const [profileId, setProfileId] = useState<number | null>(null);
  const [draftId, setDraftId] = useState<number | null>(null);
  const [jobDescription, setJobDescription] = useState("");
  const [provider, setProvider] = useState(DEFAULT_PROVIDER);
  const [templateId, setTemplateId] = useState("compact");
  const [loading, setLoading] = useState(false);
  const [savingDraft, setSavingDraft] = useState(false);
  const [errors, setErrors] = useState<string[]>([]);
  const [toast, setToast] = useState("");

  useEffect(() => {
    if (draftIdParam) {
      const id = Number(draftIdParam);
      api.getDraft(id).then((d) => {
        const draft = d as {
          profile?: Omit<Profile, "id">;
          job_description?: string;
          wizard_step?: number;
          provider?: string;
          profile_id?: number;
        };
        if (draft.profile) setProfile(draft.profile);
        if (draft.job_description) setJobDescription(draft.job_description);
        if (draft.wizard_step != null) setStep(draft.wizard_step);
        if (draft.provider) setProvider(draft.provider);
        if (draft.profile_id) setProfileId(draft.profile_id);
        setDraftId(id);
      }).catch(() => {});
    } else if (editProfileId) {
      api.getProfile(Number(editProfileId)).then((p) => {
        const { id, ...rest } = p;
        setProfile(rest);
        setProfileId(id);
      }).catch(() => {});
    }
  }, [editProfileId, draftIdParam]);

  useEffect(() => {
    setProfile((p) => ({ ...p, phone_country_code: p.phone_country_code || guessDefaultDial() }));
    api.getSettings().then((s) => {
      setProvider(resolveProviderFromSettings(s));
    }).catch(() => {});
  }, []);

  const update = (patch: Partial<Omit<Profile, "id">>) =>
    setProfile((p) => ({ ...p, ...patch }));

  const runValidation = (forGenerate = false) => {
    const errs = validateStep(step, profile, jobDescription, forGenerate);
    setErrors(errs);
    return errs.length === 0;
  };

  const next = () => {
    if (!runValidation(false)) return;
    setStep((s) => Math.min(s + 1, STEPS.length - 1));
    setErrors([]);
  };

  const back = () => {
    setStep((s) => Math.max(s - 1, 0));
    setErrors([]);
  };

  const saveDraft = async () => {
    if (!profile.full_name.trim()) {
      setErrors(["Enter your name to save a draft"]);
      return;
    }
    setSavingDraft(true);
    setErrors([]);
    try {
      const res = await api.saveDraft({
        profile,
        job_description: jobDescription,
        wizard_step: step,
        provider,
        draft_id: draftId ?? undefined,
      });
      setDraftId(res.id);
      setProfileId(res.profile_id);
      setToast(`Draft saved! (#${res.id})`);
      setTimeout(() => setToast(""), 3000);
    } catch (e) {
      setErrors([e instanceof Error ? e.message : "Save failed"]);
    } finally {
      setSavingDraft(false);
    }
  };

  const handleGenerate = async () => {
    if (!validateStep(5, profile, jobDescription, true)) {
      setErrors(validateStep(5, profile, jobDescription, true));
      return;
    }
    setLoading(true);
    setErrors([]);
    try {
      let pid = profileId;
      if (pid) {
        await api.updateProfile(pid, profile);
      } else {
        const created = await api.createProfile(profile);
        pid = created.id;
        setProfileId(pid);
      }
      const result = await api.generate(
        pid!,
        jobDescription,
        provider,
        draftId ?? undefined,
        templateId
      );
      router.push(`/resume/${result.id}?tab=preview`);
    } catch (e) {
      setErrors([e instanceof Error ? e.message : "Generation failed"]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="speech-bubble">
        <h1 className="font-display text-4xl">Resume Quest</h1>
        <p className="text-manga-muted">{STEP_HINTS[step]}</p>
        {step === 0 && (
          <label className="mt-2 inline-block cursor-pointer text-xs font-bold text-manga-accent underline">
            <input
              type="file"
              accept=".txt,.docx,.pdf"
              className="hidden"
              onChange={async (e) => {
                const f = e.target.files?.[0];
                if (!f) return;
                try {
                  const r = await api.importResume(f);
                  router.push(`/wizard?profile=${r.profile_id}`);
                } catch (err) {
                  setErrors([err instanceof Error ? err.message : "Import failed"]);
                }
              }}
            />
            Import existing resume (PDF / DOCX / TXT)
          </label>
        )}
      </div>

      <div className="flex items-center justify-between gap-2 overflow-x-auto pb-2">
        {STEPS.map((s, i) => (
          <div key={s} className="flex flex-col items-center gap-1 min-w-[4rem]">
            <div
              className={
                i < step ? "step-pill-done" : i === step ? "step-pill-active" : "step-pill-todo"
              }
            >
              {i + 1}
            </div>
            <span className="text-[10px] font-bold uppercase hidden sm:block">{s}</span>
          </div>
        ))}
      </div>

      <div className="manga-panel">
        {step === 0 && <StepProfile profile={profile} update={update} />}
        {step === 1 && <StepExperience profile={profile} update={update} />}
        {step === 2 && <StepEducation profile={profile} update={update} />}
        {step === 3 && <StepSkills profile={profile} update={update} />}
        {step === 4 && (
          <StepJobDescription jobDescription={jobDescription} setJobDescription={setJobDescription} />
        )}
        {step === 5 && (
          <StepGenerate
            provider={provider}
            setProvider={setProvider}
            templateId={templateId}
            setTemplateId={setTemplateId}
          />
        )}

        {errors.length > 0 && (
          <ul className="error-list">
            {errors.map((e, i) => (
              <li key={i}>• {e}</li>
            ))}
          </ul>
        )}
        {toast && (
          <p className="mt-3 rounded-xl bg-[var(--accent-2)]/30 px-4 py-2 font-bold text-[var(--text)]">
            {toast}
          </p>
        )}
      </div>

      <div className="flex flex-wrap justify-between gap-3">
        <MangaButton variant="ghost" onClick={back} disabled={step === 0}>
          ← Back
        </MangaButton>
        <div className="flex flex-wrap gap-2">
          {step < STEPS.length - 1 && (
            <MangaButton variant="secondary" onClick={saveDraft} disabled={savingDraft}>
              {savingDraft ? "Saving..." : "Save draft"}
            </MangaButton>
          )}
          {step < STEPS.length - 1 ? (
            <MangaButton variant="primary" onClick={next}>
              Next →
            </MangaButton>
          ) : (
            <MangaButton variant="primary" burst onClick={handleGenerate} disabled={loading}>
              {loading ? "Summoning AI..." : "Generate!"}
            </MangaButton>
          )}
        </div>
      </div>
    </div>
  );
}

export default function WizardPage() {
  return (
    <Suspense fallback={<div className="speech-bubble">Loading quest...</div>}>
      <WizardContent />
    </Suspense>
  );
}

function StepProfile({
  profile,
  update,
}: {
  profile: Omit<Profile, "id">;
  update: (p: Partial<Omit<Profile, "id">>) => void;
}) {
  return (
    <div className="grid gap-4 sm:grid-cols-2">
      <FormField label="Full name" required>
        <TextInput value={profile.full_name} onChange={(v) => update({ full_name: v })} required />
      </FormField>
      <FormField label="Email" required hint="for recruiters">
        <TextInput value={profile.email} onChange={(v) => update({ email: v })} type="email" required />
      </FormField>
      <div className="sm:col-span-2">
        <FormField label="Phone" required hint="country code + number in one field">
          <PhoneInput
            countryCode={profile.phone_country_code || "+1"}
            phone={profile.phone}
            onCountryChange={(v) => update({ phone_country_code: v })}
            onPhoneChange={(v) => update({ phone: v })}
          />
        </FormField>
      </div>
      <FormField label="Location" hint="optional">
        <TextInput value={profile.location} onChange={(v) => update({ location: v })} />
      </FormField>
      <FormField label="LinkedIn" hint="optional">
        <TextInput value={profile.linkedin} onChange={(v) => update({ linkedin: v })} placeholder="https://linkedin.com/in/..." />
      </FormField>
      <FormField label="GitHub" hint="optional — used in Professional layout">
        <TextInput
          value={(profile as { github?: string }).github || ""}
          onChange={(v) => update({ github: v } as Partial<Omit<Profile, "id">>)}
          placeholder="github.com/username"
        />
      </FormField>
      <FormField label="Target role" hint="optional">
        <TextInput value={profile.target_role} onChange={(v) => update({ target_role: v })} />
      </FormField>
      <FormField label="Years of experience" hint="optional">
        <TextInput
          value={String(profile.years_experience)}
          onChange={(v) => update({ years_experience: Math.min(60, Math.max(0, parseInt(v) || 0)) })}
          type="number"
        />
      </FormField>
      <FormField label="Headline" hint="optional">
        <TextInput value={profile.headline} onChange={(v) => update({ headline: v })} />
      </FormField>
      <div className="sm:col-span-2">
        <FormField label="Notes for AI summary" hint="optional">
          <textarea
            className="input min-h-[90px]"
            value={profile.summary_notes}
            onChange={(e) => update({ summary_notes: e.target.value })}
            placeholder="Wins, strengths, goals..."
          />
        </FormField>
      </div>
    </div>
  );
}

function StepExperience({
  profile,
  update,
}: {
  profile: Omit<Profile, "id">;
  update: (p: Partial<Omit<Profile, "id">>) => void;
}) {
  const addJob = () =>
    update({
      experience: [
        ...profile.experience,
        { company: "", title: "", start_date: "", end_date: "", bullets: [""] },
      ],
    });

  const updateJob = (i: number, job: ExperienceInput) => {
    const exp = [...profile.experience];
    exp[i] = job;
    update({ experience: exp });
  };

  const removeJob = (i: number) => {
    update({ experience: profile.experience.filter((_, idx) => idx !== i) });
  };

  return (
    <div className="space-y-4">
      <p className="text-sm text-[var(--muted)]">
        Optional while drafting. <strong>Required</strong> before generating (min. 1 job).
      </p>
      {profile.experience.length === 0 && (
        <p className="rounded-xl border-2 border-dashed border-[var(--border)] p-6 text-center text-[var(--muted)]">
          No jobs yet — add your first role below
        </p>
      )}
      {profile.experience.map((job, i) => (
        <div key={i} className="rounded-xl border-[3px] border-[var(--border)] bg-[var(--accent-3)]/20 p-4">
          <div className="mb-3 flex justify-between">
            <h4 className="font-display text-xl">Job {i + 1}</h4>
            <button type="button" onClick={() => removeJob(i)} className="text-sm font-bold text-[var(--danger)]">
              Remove
            </button>
          </div>
          <div className="grid gap-3 sm:grid-cols-2">
            <FormField label="Company" required>
              <TextInput value={job.company} onChange={(v) => updateJob(i, { ...job, company: v })} />
            </FormField>
            <FormField label="Job title" required>
              <TextInput value={job.title} onChange={(v) => updateJob(i, { ...job, title: v })} />
            </FormField>
            <FormField label="Start date" required>
              <MonthInput value={job.start_date} onChange={(v) => updateJob(i, { ...job, start_date: v })} />
            </FormField>
            <FormField label="End date" hint="Present or pick month">
              <EndDateInput
                value={job.end_date || ""}
                onChange={(v) => updateJob(i, { ...job, end_date: v })}
              />
            </FormField>
          </div>
          <FormField label="Bullet points" hint="one per line" required>
            <textarea
              className="input mt-1 min-h-[100px]"
              value={job.bullets.join("\n")}
              onChange={(e) =>
                updateJob(i, {
                  ...job,
                  bullets: e.target.value.split("\n").filter((l) => l.trim()),
                })
              }
              placeholder="Led team of 5...&#10;Increased revenue 20%..."
            />
          </FormField>
        </div>
      ))}
      <MangaButton variant="teal" onClick={addJob}>
        + Add job
      </MangaButton>
    </div>
  );
}

function StepEducation({ profile, update }: { profile: Omit<Profile, "id">; update: (p: Partial<Omit<Profile, "id">>) => void }) {
  const add = () =>
    update({ education: [...profile.education, { institution: "", degree: "", graduation_date: "" }] });

  const updateEdu = (i: number, edu: EducationInput) => {
    const ed = [...profile.education];
    ed[i] = edu;
    update({ education: ed });
  };

  return (
    <div className="space-y-4">
      <p className="text-sm text-[var(--muted)]">Fully optional — leave empty to skip.</p>
      {profile.education.map((edu, i) => (
        <div key={i} className="grid gap-3 sm:grid-cols-2 rounded-xl border-2 border-[var(--border)] p-4">
          <FormField label="Institution" hint="if adding">
            <TextInput value={edu.institution} onChange={(v) => updateEdu(i, { ...edu, institution: v })} />
          </FormField>
          <FormField label="Degree" hint="if adding">
            <TextInput value={edu.degree} onChange={(v) => updateEdu(i, { ...edu, degree: v })} />
          </FormField>
          <FormField label="Field" hint="optional">
            <TextInput value={edu.field || ""} onChange={(v) => updateEdu(i, { ...edu, field: v })} />
          </FormField>
          <FormField label="Graduation" hint="YYYY or month">
            <MonthInput
              value={edu.graduation_date || ""}
              onChange={(v) => updateEdu(i, { ...edu, graduation_date: v })}
            />
          </FormField>
        </div>
      ))}
      <button type="button" onClick={add} className="btn-ghost">
        + Add education
      </button>
    </div>
  );
}

function StepSkills({ profile, update }: { profile: Omit<Profile, "id">; update: (p: Partial<Omit<Profile, "id">>) => void }) {
  return (
    <div>
      <FormField label="Skills" hint="each skill is counted separately">
        <SkillsInput skills={profile.skills} onChange={(skills) => update({ skills })} minForGenerate={3} />
      </FormField>
    </div>
  );
}

function StepJobDescription({
  jobDescription,
  setJobDescription,
}: {
  jobDescription: string;
  setJobDescription: (v: string) => void;
}) {
  return (
    <FormField label="Job description" required hint="paste entire posting">
      <textarea
        className="input min-h-[260px] font-mono text-sm"
        value={jobDescription}
        onChange={(e) => setJobDescription(e.target.value)}
        placeholder="Paste the full job posting here (50+ characters)..."
      />
      <p className="mt-2 text-xs text-[var(--muted)]">
        {jobDescription.length} characters {jobDescription.length < 50 && "(need 50+ to generate)"}
      </p>
    </FormField>
  );
}

function StepGenerate({
  provider,
  setProvider,
  templateId,
  setTemplateId,
}: {
  provider: string;
  setProvider: (v: string) => void;
  templateId: string;
  setTemplateId: (v: string) => void;
}) {
  const [providers, setProviders] = useState<{ id: string; name: string; requires_key: boolean }[]>([]);

  useEffect(() => {
    api.providers().then(setProviders).catch(() => {});
  }, []);

  return (
    <div className="space-y-6">
      <p className="rounded-xl bg-[var(--accent-2)]/20 p-4 text-sm">
        AI uses <strong>only your facts</strong> — no fake employers. Keys from Settings apply here.
      </p>
      <FormField label="Resume layout">
        <TemplatePicker value={templateId} onChange={setTemplateId} />
      </FormField>
      <FormField label="AI provider">
        <select className="input" value={provider} onChange={(e) => setProvider(e.target.value)}>
          {providers.map((p) => (
            <option key={p.id} value={p.id}>
              {p.name} {p.requires_key ? "(API key)" : ""}
            </option>
          ))}
        </select>
      </FormField>
    </div>
  );
}
