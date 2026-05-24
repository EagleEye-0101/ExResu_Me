"""LaTeX editor API — templates, demo source, compile to PDF."""

from __future__ import annotations

import base64

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from resume_engine.db import crud
from resume_engine.db.database import get_db
from resume_engine.latex.compiler import compile_latex, is_latex_available
from resume_engine.latex.generate import render_resume_latex
from resume_engine.latex.registry import (
    DEFAULT_LATEX_TEMPLATE_ID,
    get_demo_source,
    list_latex_templates,
    resolve_latex_template_id,
)

router = APIRouter(tags=["latex"])


def get_session():
    yield from get_db()


class CompileLatexRequest(BaseModel):
    source: str = Field(..., min_length=10, max_length=250_000)
    template_id: str | None = None


class CompileLatexResponse(BaseModel):
    success: bool
    log: str
    error: str | None = None
    pdf_base64: str | None = None


@router.get("/latex/templates")
def latex_templates_list():
    return {
        "templates": list_latex_templates(),
        "default_template_id": DEFAULT_LATEX_TEMPLATE_ID,
        "compiler_available": is_latex_available(),
    }


@router.get("/latex/demo")
def latex_demo_source(template: str = Query(DEFAULT_LATEX_TEMPLATE_ID)):
    tid = resolve_latex_template_id(template)
    return {"template_id": tid, "source": get_demo_source(tid)}


@router.post("/latex/compile", response_model=CompileLatexResponse)
def latex_compile(req: CompileLatexRequest):
    if not is_latex_available():
        raise HTTPException(
            503,
            detail=(
                "LaTeX compiler not installed. Install Tectonic from "
                "https://tectonic-typesetting.github.io/ or set TECTONIC_PATH in .env"
            ),
        )
    result = compile_latex(req.source)
    if not result.success:
        return CompileLatexResponse(
            success=False,
            log=result.log,
            error=result.error or "Compilation failed",
            pdf_base64=None,
        )
    assert result.pdf_bytes is not None
    return CompileLatexResponse(
        success=True,
        log=result.log,
        error=None,
        pdf_base64=base64.b64encode(result.pdf_bytes).decode("ascii"),
    )


@router.get("/latex/from-resume/{resume_id}")
def latex_from_resume(
    resume_id: int,
    template: str = Query(DEFAULT_LATEX_TEMPLATE_ID),
    db: Session = Depends(get_session),
):
    result = crud.get_resume(db, resume_id)
    if not result:
        raise HTTPException(404, "Resume not found")
    _row, resume = result
    if resume is None:
        raise HTTPException(400, "Resume has no generated content yet (finish or generate first)")
    tid = resolve_latex_template_id(template)
    return {
        "resume_id": resume_id,
        "template_id": tid,
        "source": render_resume_latex(resume, tid),
    }


@router.get("/latex/demo/pdf")
def latex_demo_pdf(template: str = Query(DEFAULT_LATEX_TEMPLATE_ID)):
    if not is_latex_available():
        raise HTTPException(
            503,
            detail="LaTeX compiler not installed. See README for Tectonic setup.",
        )
    tid = resolve_latex_template_id(template)
    source = get_demo_source(tid)
    result = compile_latex(source)
    if not result.success or not result.pdf_bytes:
        raise HTTPException(
            422,
            detail={"error": result.error, "log": result.log[-3000:]},
        )
    return Response(
        content=result.pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'inline; filename="demo_resume_{tid}.pdf"',
        },
    )
