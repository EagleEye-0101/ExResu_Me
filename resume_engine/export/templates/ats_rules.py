"""Shared ATS-safe typography and spacing constants."""

from dataclasses import dataclass

FONT_BODY_PT = 10
FONT_SMALL_PT = 9
FONT_NAME_PT = 16
FONT_NAME_COMPACT_PT = 13
FONT_SECTION_PT = 11
FONT_SECTION_MODERN_PT = 11

MARGIN_INCH = 0.75
MARGIN_COMPACT_INCH = 0.6

MODERN_ACCENT_RGB = (0x0D, 0x94, 0x88)


@dataclass(frozen=True)
class TemplateLayout:
    id: str
    contact_style: str  # grid | inline | compact_inline
    section_order: tuple[str, ...]
    centered_header: bool = False


LAYOUTS: dict[str, TemplateLayout] = {
    "professional": TemplateLayout(
        id="professional",
        contact_style="grid",
        section_order=("summary", "education", "skills", "experience", "projects", "activities", "certifications"),
    ),
    "classic": TemplateLayout(
        id="classic",
        contact_style="inline",
        section_order=("summary", "experience", "education", "skills", "certifications"),
        centered_header=True,
    ),
    "modern": TemplateLayout(
        id="modern",
        contact_style="inline",
        section_order=("summary", "experience", "education", "skills", "projects", "certifications"),
    ),
    "compact": TemplateLayout(
        id="compact",
        contact_style="compact_inline",
        section_order=("summary", "experience", "education", "skills"),
    ),
}


def get_layout(template_id: str) -> TemplateLayout:
    return LAYOUTS.get(template_id, LAYOUTS["professional"])
