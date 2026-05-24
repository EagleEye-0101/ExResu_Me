import Link from "next/link";

export function BrandLogo({ showTagline = true }: { showTagline?: boolean }) {
  return (
    <Link href="/" className="brand-logo group inline-block leading-none">
      <span className="brand-logo-text" aria-label="ExResu_Me">
        <span className="brand-ex">Ex</span>
        <span className="brand-resu">Resu</span>
        <span className="brand-me">_Me</span>
      </span>
      {showTagline && (
        <span className="brand-tagline mt-0.5 hidden text-xs font-bold tracking-widest text-manga-muted sm:block">
          ATS RESUME
        </span>
      )}
    </Link>
  );
}
