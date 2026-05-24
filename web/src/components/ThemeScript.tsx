/** Runs before paint to apply saved theme and avoid flash / hydration mismatch. */
export function ThemeScript() {
  const script = `(function(){try{var t=localStorage.getItem("exresu-me-theme")||localStorage.getItem("resume-hero-theme");if(t==="dark"||t==="light")document.documentElement.setAttribute("data-theme",t);}catch(e){}})();`;
  return <script dangerouslySetInnerHTML={{ __html: script }} />;
}
