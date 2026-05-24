import asyncio
import json
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from resume_engine.ai.generator import generate_resume, optimize_resume
from resume_engine.ats.scorer import score_resume
from resume_engine.config import settings
from resume_engine.db import crud
from resume_engine.db.database import init_db
from resume_engine.export.docx_export import export_docx
from resume_engine.export.pdf_export import export_pdf
from resume_engine.export.txt_export import export_txt
from resume_engine.schemas.profile import ProfileCreate, ExperienceInput, EducationInput
from resume_engine.schemas.resume import ResumeData

app = typer.Typer(help="ATS Resume Builder CLI", no_args_is_help=True)
console = Console()


def _get_db():
    init_db()
    from resume_engine.db.database import _SessionLocal

    if _SessionLocal is None:
        raise RuntimeError("Database not initialized")
    return _SessionLocal()


@app.command("init")
def init_profile(
    name: str = typer.Option(..., "--name", help="Full name"),
    email: str = typer.Option(..., "--email"),
    phone: str = typer.Option(..., "--phone"),
    role: str = typer.Option("", "--role", help="Target role"),
):
    """Create a new profile."""
    db = _get_db()
    try:
        profile = crud.create_profile(
            db,
            ProfileCreate(
                full_name=name,
                email=email,
                phone=phone,
                target_role=role,
            ),
        )
        console.print(f"[green]Profile created: ID {profile.id}[/green]")
        console.print(f"  {profile.full_name} <{profile.email}>")
    finally:
        db.close()


@app.command("list")
def list_profiles_cmd():
    """List all profiles."""
    db = _get_db()
    try:
        profiles = crud.list_profiles(db)
        if not profiles:
            console.print("[yellow]No profiles yet. Run: resume init[/yellow]")
            return
        table = Table(title="Profiles")
        table.add_column("ID")
        table.add_column("Name")
        table.add_column("Email")
        table.add_column("Role")
        for p in profiles:
            table.add_row(str(p.id), p.full_name, p.email, p.target_role or "-")
        console.print(table)
    finally:
        db.close()


@app.command("import-profile")
def import_profile(
    file: Path = typer.Argument(..., help="JSON profile file"),
):
    """Import profile from JSON file."""
    data = json.loads(file.read_text(encoding="utf-8"))
    db = _get_db()
    try:
        profile = crud.create_profile(db, ProfileCreate(**data))
        console.print(f"[green]Imported profile ID {profile.id}[/green]")
    finally:
        db.close()


@app.command("generate")
def generate_cmd(
    profile_id: int = typer.Option(..., "--profile-id", "-p"),
    jd: Path = typer.Option(..., "--jd", help="Job description text file"),
    provider: str = typer.Option("ollama", "--provider"),
    model: Optional[str] = typer.Option(None, "--model"),
):
    """Generate ATS-optimized resume with AI."""
    job_description = jd.read_text(encoding="utf-8")
    db = _get_db()
    try:
        profile = crud.get_profile(db, profile_id)
        if not profile:
            console.print("[red]Profile not found[/red]")
            raise typer.Exit(1)

        console.print(f"[cyan]Generating with {provider}...[/cyan]")
        resume = asyncio.run(
            generate_resume(profile, job_description, provider, model)
        )
        report = score_resume(resume, job_description)
        row = crud.save_resume(
            db, profile_id, resume, job_description, report.composite_score, provider
        )
        _print_ats_report(report)
        console.print(f"[green]Resume saved: ID {row.id}[/green]")
    finally:
        db.close()


@app.command("score")
def score_cmd(
    resume_file: Path = typer.Argument(..., help="Resume JSON file"),
    jd: Optional[Path] = typer.Option(None, "--jd", help="Job description file"),
):
    """Score a resume JSON file against a job description."""
    resume = ResumeData.model_validate(json.loads(resume_file.read_text(encoding="utf-8")))
    job_description = jd.read_text(encoding="utf-8") if jd else ""
    report = score_resume(resume, job_description)
    _print_ats_report(report)


@app.command("optimize")
def optimize_cmd(
    resume_id: int = typer.Option(..., "--resume-id", "-r"),
    provider: str = typer.Option("ollama", "--provider"),
    model: Optional[str] = typer.Option(None, "--model"),
):
    """Re-optimize resume for missing JD keywords."""
    db = _get_db()
    try:
        result = crud.get_resume(db, resume_id)
        if not result:
            console.print("[red]Resume not found[/red]")
            raise typer.Exit(1)
        row, resume = result
        report = score_resume(resume, row.job_description or "")
        if not report.missing_keywords:
            console.print("[yellow]No missing keywords[/yellow]")
            return
        console.print(f"[cyan]Optimizing {len(report.missing_keywords)} keywords...[/cyan]")
        improved = asyncio.run(
            optimize_resume(
                resume,
                row.job_description or "",
                report.missing_keywords,
                provider,
                model,
            )
        )
        new_report = score_resume(improved, row.job_description or "")
        crud.update_resume_record(db, resume_id, improved, new_report.composite_score)
        _print_ats_report(new_report)
        console.print(f"[green]Resume {resume_id} updated[/green]")
    finally:
        db.close()


@app.command("export")
def export_cmd(
    resume_id: int = typer.Option(..., "--resume-id", "-r"),
    format: str = typer.Option("docx", "--format", "-f", help="docx, pdf, or txt"),
    output: Optional[Path] = typer.Option(None, "--output", "-o"),
):
    """Export resume to DOCX, PDF, or TXT."""
    db = _get_db()
    try:
        result = crud.get_resume(db, resume_id)
        if not result:
            console.print("[red]Resume not found[/red]")
            raise typer.Exit(1)
        _, resume = result
        fmt = format.lower()
        ext = {"docx": "docx", "pdf": "pdf", "txt": "txt"}.get(fmt, "docx")
        if output:
            out_path = output
        else:
            safe = "".join(c if c.isalnum() else "_" for c in resume.full_name)[:40]
            out_path = settings.export_path / f"{safe}_resume_{resume_id}.{ext}"

        if fmt == "pdf":
            export_pdf(resume, out_path)
        elif fmt == "txt":
            export_txt(resume, out_path)
        else:
            export_docx(resume, out_path)
        console.print(f"[green]Exported: {out_path}[/green]")
    finally:
        db.close()


def _print_ats_report(report):
    color = "green" if report.composite_score >= 80 else "yellow" if report.composite_score >= 60 else "red"
    console.print(
        Panel(
            f"[bold {color}]{report.composite_score}/100[/bold {color}]",
            title="ATS Score",
        )
    )
    table = Table(title="Categories")
    table.add_column("Category")
    table.add_column("Score")
    table.add_column("Weight")
    for c in report.categories:
        table.add_row(c.name, f"{c.score}", f"{c.weight:.0%}")
    console.print(table)
    if report.missing_keywords:
        console.print(f"[yellow]Missing keywords:[/yellow] {', '.join(report.missing_keywords[:10])}")
    if report.fixes:
        console.print("\n[bold]Fixes:[/bold]")
        for f in report.fixes[:8]:
            console.print(f"  [{f.severity}] {f.message}")


if __name__ == "__main__":
    app()
