import { Profile } from "./api";

const MONTH_YEAR = /^(0[1-9]|1[0-2])\/\d{4}$/;
const EMAIL = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
const PHONE = /^[\d\s\-+().]{7,20}$/;

export function monthInputToDisplay(value: string): string {
  if (!value) return "";
  if (MONTH_YEAR.test(value)) return value;
  if (/^\d{4}-\d{2}$/.test(value)) {
    const [y, m] = value.split("-");
    return `${m}/${y}`;
  }
  return value;
}

export function monthInputFromDisplay(value: string): string {
  const v = value.trim();
  if (!v) return "";
  if (/^\d{4}-\d{2}$/.test(v)) return v;
  if (MONTH_YEAR.test(v)) {
    const [m, y] = v.split("/");
    return `${y}-${m}`;
  }
  return v;
}

export function validateStep(
  step: number,
  profile: Omit<Profile, "id">,
  jobDescription: string,
  forGenerate = false
): string[] {
  const errors: string[] = [];

  if (step === 0 || forGenerate) {
    if (!profile.full_name.trim()) errors.push("Full name is required");
    if (!profile.email.trim()) errors.push("Email is required");
    else if (!EMAIL.test(profile.email)) errors.push("Enter a valid email");
    if (!profile.phone.trim()) errors.push("Phone is required");
    else if (!PHONE.test(profile.phone.replace(/\s/g, "")))
      errors.push("Enter a valid phone number for your country");
    if (profile.linkedin.trim() && !profile.linkedin.toLowerCase().includes("linkedin.com")) {
      errors.push("LinkedIn should be a linkedin.com URL");
    }
    if (profile.years_experience < 0 || profile.years_experience > 60) {
      errors.push("Years of experience: 0–60");
    }
    if (forGenerate && step !== 0) return errors;
    if (!forGenerate && step === 0) return errors;
  }

  if (step === 1 || forGenerate) {
    if (forGenerate && profile.experience.length === 0) {
      errors.push("Add at least one job");
    }
    profile.experience.forEach((job, i) => {
      const n = i + 1;
      if (!forGenerate && !job.company && !job.title) return;
      if (!job.company.trim()) errors.push(`Job ${n}: Company required`);
      if (!job.title.trim()) errors.push(`Job ${n}: Title required`);
      if (job.start_date && !MONTH_YEAR.test(job.start_date) && !/^\d{4}-\d{2}$/.test(job.start_date)) {
        errors.push(`Job ${n}: Start date → MM/YYYY`);
      }
      if (forGenerate && !job.start_date.trim()) errors.push(`Job ${n}: Start date required`);
      const end = (job.end_date || "").trim();
      if (
        end &&
        end.toLowerCase() !== "present" &&
        !MONTH_YEAR.test(end) &&
        !/^\d{4}-\d{2}$/.test(end)
      ) {
        errors.push(`Job ${n}: End → Present, MM/YYYY, or leave empty`);
      }
      if (forGenerate) {
        const bullets = job.bullets.filter((b) => b.trim());
        if (!bullets.length) errors.push(`Job ${n}: At least one bullet`);
      }
    });
    if (!forGenerate && step === 1) return errors;
  }

  if (step === 2) {
    profile.education.forEach((edu, i) => {
      if (!edu.institution && !edu.degree) return;
      if (!edu.institution.trim()) errors.push(`Education ${i + 1}: Institution required`);
      if (!edu.degree.trim()) errors.push(`Education ${i + 1}: Degree required`);
    });
    return errors;
  }

  if (step === 3 || forGenerate) {
    if (forGenerate && profile.skills.filter((s) => s.trim()).length < 3) {
      errors.push("Add at least 3 skills");
    }
    if (!forGenerate && step === 3) return errors;
  }

  if (step === 4 || forGenerate) {
    if (forGenerate && jobDescription.trim().length < 50) {
      errors.push("Paste full job description (50+ characters)");
    }
  }

  return errors;
}
