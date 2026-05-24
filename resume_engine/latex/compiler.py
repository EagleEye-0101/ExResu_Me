"""Compile LaTeX source to PDF via Tectonic or system TeX."""

from __future__ import annotations

import re
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path

from resume_engine.config import settings

_FORBIDDEN = re.compile(
    r"\\(?:write18|immediate\\write18|input\{\s*/|openin|openout|shell)",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class CompileResult:
    success: bool
    pdf_bytes: bytes | None
    log: str
    error: str | None = None


def is_latex_available() -> bool:
    return _resolve_compiler_command() is not None


def _resolve_compiler_command() -> list[str] | None:
    kind = (settings.latex_compiler or "tectonic").strip().lower()
    if kind == "tectonic":
        if settings.tectonic_path:
            p = Path(settings.tectonic_path)
            if p.is_file():
                return [str(p)]
        found = shutil.which("tectonic")
        if found:
            return [found]
        return None
    for name in (kind, "pdflatex", "xelatex", "lualatex"):
        found = shutil.which(name)
        if found:
            return [found]
    return None


def _validate_source(source: str) -> str | None:
    if len(source.encode("utf-8")) > settings.latex_max_source_bytes:
        return f"Source exceeds {settings.latex_max_source_bytes} bytes"
    if _FORBIDDEN.search(source):
        return "Source contains disallowed LaTeX commands"
    if "\\begin{document}" not in source:
        return "Source must include \\begin{document}"
    return None


def compile_latex(
    source: str,
    *,
    work_dir: Path | None = None,
    main_file: str = "main.tex",
    extra_files: dict[str, bytes] | None = None,
) -> CompileResult:
    """Compile LaTeX source; returns PDF bytes on success."""
    err = _validate_source(source)
    if err:
        return CompileResult(success=False, pdf_bytes=None, log="", error=err)

    cmd = _resolve_compiler_command()
    if not cmd:
        return CompileResult(
            success=False,
            pdf_bytes=None,
            log="",
            error=(
                "LaTeX compiler not found. Install Tectonic "
                "(https://tectonic-typesetting.github.io/) or set TECTONIC_PATH in .env"
            ),
        )

    owns_dir = work_dir is None
    if owns_dir:
        work_dir = Path(tempfile.mkdtemp(prefix="resume_latex_"))
    assert work_dir is not None

    try:
        work_dir.mkdir(parents=True, exist_ok=True)
        tex_path = work_dir / main_file
        tex_path.write_text(source, encoding="utf-8")
        if extra_files:
            for name, data in extra_files.items():
                (work_dir / name).write_bytes(data)

        kind = (settings.latex_compiler or "tectonic").strip().lower()
        if kind == "tectonic" or cmd[0].endswith("tectonic"):
            run_cmd = [
                *cmd,
                "--synctex",
                "--keep-logs",
                "--outdir",
                str(work_dir),
                str(tex_path),
            ]
        else:
            run_cmd = [
                *cmd,
                "-interaction=nonstopmode",
                "-output-directory",
                str(work_dir),
                str(tex_path),
            ]

        proc = subprocess.run(
            run_cmd,
            capture_output=True,
            text=True,
            timeout=settings.latex_compile_timeout,
            cwd=work_dir,
        )
        log = (proc.stdout or "") + "\n" + (proc.stderr or "")
        pdf_path = work_dir / Path(main_file).with_suffix(".pdf")
        if not pdf_path.is_file():
            pdf_path = work_dir / "main.pdf"
        if proc.returncode != 0 or not pdf_path.is_file():
            tail = log[-4000:] if len(log) > 4000 else log
            return CompileResult(
                success=False,
                pdf_bytes=None,
                log=tail,
                error="LaTeX compilation failed. See log for details.",
            )
        return CompileResult(success=True, pdf_bytes=pdf_path.read_bytes(), log=log[-2000:])
    except subprocess.TimeoutExpired:
        return CompileResult(
            success=False,
            pdf_bytes=None,
            log="",
            error=f"Compilation timed out after {settings.latex_compile_timeout}s",
        )
    except OSError as e:
        return CompileResult(success=False, pdf_bytes=None, log="", error=str(e))
    finally:
        if owns_dir and work_dir and work_dir.exists():
            shutil.rmtree(work_dir, ignore_errors=True)
