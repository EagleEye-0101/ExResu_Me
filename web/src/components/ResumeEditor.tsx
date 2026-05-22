"use client";

import { FormField, TextInput } from "@/components/FormField";
import { EndDateInput } from "@/components/EndDateInput";
import { MonthInput } from "@/components/FormField";
import { ResumeData, ExperienceInput, EducationInput } from "@/lib/api";

export function ResumeEditor({
  resume,
  onChange,
}: {
  resume: ResumeData;
  onChange: (r: ResumeData) => void;
}) {
  const patch = (p: Partial<ResumeData>) => onChange({ ...resume, ...p });

  const updateExp = (i: number, job: ExperienceInput) => {
    const experience = [...resume.experience];
    experience[i] = job;
    patch({ experience });
  };

  const updateEdu = (i: number, edu: EducationInput) => {
    const education = [...resume.education];
    education[i] = edu;
    patch({ education });
  };

  return (
    <div className="space-y-8">
      <p className="rounded-xl bg-manga-teal/20 px-4 py-2 text-sm font-bold">
        ✎ Everything below is editable. Save changes, then export again for an updated file.
      </p>

      <section className="grid gap-4 sm:grid-cols-2">
        <FormField label="Full name" required>
          <TextInput value={resume.full_name} onChange={(v) => patch({ full_name: v })} />
        </FormField>
        <FormField label="Headline">
          <TextInput value={resume.headline} onChange={(v) => patch({ headline: v })} />
        </FormField>
        <FormField label="Email" required>
          <TextInput value={resume.email} onChange={(v) => patch({ email: v })} type="email" />
        </FormField>
        <FormField label="Phone" required>
          <TextInput value={resume.phone} onChange={(v) => patch({ phone: v })} />
        </FormField>
        <FormField label="Location">
          <TextInput value={resume.location} onChange={(v) => patch({ location: v })} />
        </FormField>
        <FormField label="LinkedIn">
          <TextInput value={resume.linkedin} onChange={(v) => patch({ linkedin: v })} />
        </FormField>
      </section>

      <section>
        <h4 className="font-display mb-3 text-2xl">Summary</h4>
        <textarea
          className="input min-h-[100px]"
          value={resume.summary}
          onChange={(e) => patch({ summary: e.target.value })}
        />
      </section>

      <section>
        <div className="mb-3 flex items-center justify-between">
          <h4 className="font-display text-2xl">Experience</h4>
          <button
            type="button"
            className="btn-teal text-sm"
            onClick={() =>
              patch({
                experience: [
                  ...resume.experience,
                  { company: "", title: "", start_date: "", end_date: "", bullets: [""] },
                ],
              })
            }
          >
            + Job
          </button>
        </div>
        {resume.experience.map((job, i) => (
          <div
            key={i}
            className="mb-4 rounded-xl border-2 border-manga-border bg-manga-yellow/15 p-4"
          >
            <div className="mb-2 flex justify-end">
              <button
                type="button"
                className="text-sm font-bold text-manga-danger"
                onClick={() =>
                  patch({ experience: resume.experience.filter((_, idx) => idx !== i) })
                }
              >
                Remove job
              </button>
            </div>
            <div className="grid gap-3 sm:grid-cols-2">
              <FormField label="Company">
                <TextInput value={job.company} onChange={(v) => updateExp(i, { ...job, company: v })} />
              </FormField>
              <FormField label="Title">
                <TextInput value={job.title} onChange={(v) => updateExp(i, { ...job, title: v })} />
              </FormField>
              <FormField label="Start">
                <MonthInput value={job.start_date} onChange={(v) => updateExp(i, { ...job, start_date: v })} />
              </FormField>
              <FormField label="End">
                <EndDateInput
                  value={job.end_date || ""}
                  onChange={(v) => updateExp(i, { ...job, end_date: v })}
                />
              </FormField>
            </div>
            <FormField label="Bullets (one per line)">
              <textarea
                className="input mt-1 min-h-[90px]"
                value={job.bullets.join("\n")}
                onChange={(e) =>
                  updateExp(i, {
                    ...job,
                    bullets: e.target.value.split("\n"),
                  })
                }
              />
            </FormField>
          </div>
        ))}
      </section>

      <section>
        <div className="mb-3 flex items-center justify-between">
          <h4 className="font-display text-2xl">Education</h4>
          <button
            type="button"
            className="btn-ghost text-sm"
            onClick={() =>
              patch({
                education: [
                  ...resume.education,
                  { institution: "", degree: "", graduation_date: "" },
                ],
              })
            }
          >
            + School
          </button>
        </div>
        {resume.education.map((edu, i) => (
          <div key={i} className="mb-3 grid gap-3 sm:grid-cols-2 rounded-lg border border-manga-border p-3">
            <FormField label="Institution">
              <TextInput value={edu.institution} onChange={(v) => updateEdu(i, { ...edu, institution: v })} />
            </FormField>
            <FormField label="Degree">
              <TextInput value={edu.degree} onChange={(v) => updateEdu(i, { ...edu, degree: v })} />
            </FormField>
            <FormField label="Graduation">
              <MonthInput
                value={edu.graduation_date || ""}
                onChange={(v) => updateEdu(i, { ...edu, graduation_date: v })}
              />
            </FormField>
          </div>
        ))}
      </section>

      <section>
        <h4 className="font-display mb-3 text-2xl">Skills</h4>
        <textarea
          className="input min-h-[80px]"
          value={resume.skills.join(", ")}
          onChange={(e) =>
            patch({
              skills: e.target.value.split(",").map((s) => s.trim()).filter(Boolean),
            })
          }
        />
      </section>
    </div>
  );
}
