/** Split pasted or typed skills into separate items (comma, semicolon, newline, pipe, bullet). */
export function parseSkillsInput(raw: string): string[] {
  const seen = new Set<string>();
  const out: string[] = [];
  for (const part of raw.split(/[,;|\n]+/)) {
    const skill = part.replace(/^[\s•\-*]+/, "").trim();
    if (!skill) continue;
    const key = skill.toLowerCase();
    if (!seen.has(key)) {
      seen.add(key);
      out.push(skill);
    }
  }
  return out;
}

export function countSkills(skills: string[]): number {
  return skills.filter((s) => s.trim()).length;
}
