#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["python-docx>=1.1"]
# ///
"""Render a Markdown CV to .docx (and PDF) with template fidelity.

Usage:
    uv run bin/render_cv.py <input.md> <output.docx | output_dir> <template.docx>

If the second arg is an existing directory, the output filename is auto-computed
from the H1 name and the SUMMARY headline role, e.g. for `# Jane Doe` with a
SUMMARY headline naming "Product Manager" the output is
"JDoe - Product Manager.docx" (falls back to "cv.docx" if either part can't
be parsed cleanly). Passing an explicit .docx file path preserves the original
one-arg-one-output behaviour.

PDF export: after writing the .docx the renderer runs LibreOffice headless
(`soffice --headless --convert-to pdf`) to produce a .pdf alongside it. If
LibreOffice isn't on PATH the PDF step is skipped with a stderr warning and
the .docx still lands. Pass --no-pdf to skip explicitly.

Markdown convention:
    # Name                              -> CV Title
    <contact line with '·' and '@'>     -> CV Contact
    <other text>                        -> CV Target Title
    ## SUMMARY / PROFESSIONAL EXPERIENCE / EDUCATION & CERTIFICATIONS / SKILLS
                                        -> CV Section
    ## COMPANY                          -> CV Company
        <location>                         (right-tab; trailing ' · YYYY...' auto-dropped)
        <company dates>                    (ignored; role dates win)
        *tagline*                       -> CV Tagline
    ### Role title                      -> CV Role
        <role dates>                       (right-tab on role line)
        *role-context pre-text*         -> CV Role Context
                                           (distinct style from CV Tagline
                                           so template.docx can style role
                                           pre-texts differently from
                                           company taglines; auto-created
                                           if template lacks it)
    - bullet                            -> CV Bullet
    bullets under ## SKILLS             -> CV Skill Line
    indented `  - ` under EDUCATION     -> CV Education courses
                                           (no bullet marker; nested sub-detail)
    bullet under EDUCATION + dates line -> CV Bullet two-column (title | dates)
        - <Institution + degree>
        <Dates>
          - <Optional indented sub-detail>           (CV Education courses)

Inline markup recognized in any paragraph:
    **bold**, *italic*, `code`, [label](url) → real docx hyperlink (w:hyperlink,
    "Hyperlink" character style if present in template). URL must not contain
    unbalanced parentheses.

Defensive stripping: backtick tag markers (`[pm]`, `[ai]`, ...) on roles and
bullets, and trailing *(keywords)* on bullets, are removed.

Ported from mcp-pandoc/cv_render_server.py — same parsing logic, no MCP wrapper.
"""
import argparse
import os
import re
import shutil
import subprocess
import sys

from docx import Document
from docx.enum.style import WD_STYLE_TYPE
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import RGBColor

STYLE_TITLE        = "CV Title"
STYLE_CONTACT      = "CV Contact"
STYLE_TARGET       = "CV Target Title"
STYLE_SECTION      = "CV Section"
STYLE_COMPANY      = "CV Company"
STYLE_TAGLINE      = "CV Tagline"
STYLE_ROLE         = "CV Role"
STYLE_ROLE_CONTEXT = "CV Role Context"
STYLE_BULLET       = "CV Bullet"
STYLE_SKILL        = "CV Skill Line"
STYLE_EDUCATION    = "CV Education courses"

SECTION_H2 = {
    "SUMMARY",
    "PROFESSIONAL EXPERIENCE",
    "EXPERIENCE",
    "EDUCATION",
    "EDUCATION & CERTIFICATIONS",
    "CERTIFICATIONS",
    "SKILLS",
}

_TAG_PREFIX   = re.compile(r"^\s*(`\[[\w\-]+\]`\s*)+")
_TAG_TRAIL    = re.compile(r"\s*\*\([^)]+\)\*\s*$")
_INLINE       = re.compile(r"(\[[^\]]+\]\([^)]+\)|\*\*[^*]+\*\*|\*[^*]+\*|`[^`]+`)")
_YEAR_PATTERN = re.compile(r"\b\d{4}\b")

_SUMMARY_STOPWORDS = (" focused ", " with ", " · ", ".", ",", ":", ";")
_FS_UNSAFE = re.compile(r'[/\\:\*\?"<>|\x00-\x1f]')

# Candidate-stance adjectival prefixes to strip from the filename role.
# "AI-first Product Engineer" → "Product Engineer"; "AI-native Solutions
# Architect" → "Solutions Architect"; "compliance-first Product Manager"
# → "Product Manager". These are candidate-orientation modifiers, not part
# of any real job title. Plain-word prefixes ("AI", "Senior", "Sr.",
# "Staff", "Principal", "Lead") stay — they ARE title components.
_STANCE_PREFIX = re.compile(
    r"^\S+-(?:first|native|fluent|driven|led|forward|centric|powered|enabled)\s+",
    re.IGNORECASE,
)


def _extract_name_shorthand(md_path: str) -> str | None:
    """Parse the markdown H1 (`# <Name>`) and return an initial-lastname shorthand.

    Returns e.g. "JDoe" for `# Jane Doe`, "JvdB" for `# Jan van der Berg`
    (keeping lowercase particles between initial and last name), or None if
    the H1 is missing, empty, or sanitizes to nothing filesystem-safe.
    """
    try:
        with open(md_path, encoding="utf-8") as f:
            content = f.read()
    except OSError:
        return None
    m = re.search(r"^#\s+([^\n#].*)$", content, re.MULTILINE)
    if not m:
        return None
    raw = m.group(1).strip()
    raw = re.sub(r"\*\*(.+?)\*\*", r"\1", raw)
    raw = _FS_UNSAFE.sub("", raw).strip()
    if not raw:
        return None
    parts = raw.split()
    if len(parts) == 1:
        token = parts[0]
    else:
        first_initial = parts[0][0]
        middle = [p for p in parts[1:-1] if p and p[0].islower()]
        last = parts[-1]
        token = first_initial + "".join(middle) + last
    token = token.strip()
    if not (1 <= len(token) <= 40):
        return None
    return token


def _extract_summary_role(md_path: str) -> str | None:
    """Parse SUMMARY headline → vacancy-aligned role for filename use.

    Returns the role string (e.g. "Product Owner") when the headline parses
    cleanly to a 2-50 char sanitized token; returns None on ambiguity so the
    caller can fall back. Strips candidate-stance adjectival prefixes like
    "AI-first" / "compliance-first" so the filename tracks the real job
    title rather than the CV's rhetorical framing.
    """
    try:
        with open(md_path, encoding="utf-8") as f:
            content = f.read()
    except OSError:
        return None
    m = re.search(r"^##\s+SUMMARY\s*$", content, re.MULTILINE)
    if not m:
        return None
    tail = content[m.end():]
    headline = None
    for raw in tail.split("\n"):
        s = raw.strip()
        if not s:
            continue
        if s.startswith("#"):
            return None
        headline = s
        break
    if not headline:
        return None
    headline = re.sub(r"\*\*(.+?)\*\*", r"\1", headline)
    cut = len(headline)
    for sw in _SUMMARY_STOPWORDS:
        pos = headline.find(sw)
        if 0 <= pos < cut:
            cut = pos
    role = _FS_UNSAFE.sub("", headline[:cut]).strip()
    role = _STANCE_PREFIX.sub("", role).strip()
    if not (2 <= len(role) <= 50):
        return None
    return role


def _strip_bullet_tags(text: str) -> str:
    text = _TAG_PREFIX.sub("", text)
    text = _TAG_TRAIL.sub("", text)
    return text.strip()


def _strip_role_tags(text: str) -> str:
    return _TAG_PREFIX.sub("", text).strip()


def _drop_trailing_dates(text: str) -> str:
    if " · " not in text:
        return text
    parts = text.split(" · ")
    while len(parts) > 1 and _YEAR_PATTERN.search(parts[-1]):
        parts.pop()
    return " · ".join(parts).strip()


def _parse_blocks(md: str):
    blocks = []
    for raw in md.splitlines():
        line = raw.rstrip()
        if not line.strip():
            blocks.append(("blank", ""))
            continue
        if line.startswith("# ") and not line.startswith("## "):
            blocks.append(("h1", line[2:].strip()))
        elif line.startswith("## "):
            blocks.append(("h2", line[3:].strip()))
        elif line.startswith("### "):
            blocks.append(("h3", _strip_role_tags(line[4:])))
        elif line.lstrip().startswith("- "):
            indent = len(line) - len(line.lstrip())
            text = _strip_bullet_tags(line.lstrip()[2:])
            blocks.append(("subbullet" if indent > 0 else "bullet", text))
        elif line.strip().startswith("---"):
            blocks.append(("hr", ""))
        elif re.fullmatch(r"\*[^*].*[^*]\*", line.strip()):
            blocks.append(("italic", line.strip()[1:-1].strip()))
        else:
            blocks.append(("text", line.strip()))
    return blocks


def _add_hyperlink(paragraph, url: str, text: str):
    part = paragraph.part
    r_id = part.relate_to(
        url,
        "http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink",
        is_external=True,
    )
    hyperlink = OxmlElement("w:hyperlink")
    hyperlink.set(qn("r:id"), r_id)
    new_run = OxmlElement("w:r")
    rPr = OxmlElement("w:rPr")
    rStyle = OxmlElement("w:rStyle")
    rStyle.set(qn("w:val"), "Hyperlink")
    rPr.append(rStyle)
    color = OxmlElement("w:color")
    color.set(qn("w:val"), "0563C1")
    rPr.append(color)
    underline = OxmlElement("w:u")
    underline.set(qn("w:val"), "single")
    rPr.append(underline)
    new_run.append(rPr)
    t = OxmlElement("w:t")
    t.text = text
    t.set(qn("xml:space"), "preserve")
    new_run.append(t)
    hyperlink.append(new_run)
    paragraph._p.append(hyperlink)


def _add_runs(paragraph, text: str, default_bold=None):
    for part in _INLINE.split(text):
        if not part:
            continue
        if part.startswith("[") and "](" in part and part.endswith(")"):
            label, url = part[1:-1].split("](", 1)
            _add_hyperlink(paragraph, url, label)
        elif part.startswith("**") and part.endswith("**"):
            r = paragraph.add_run(part[2:-2]); r.bold = True
        elif part.startswith("*") and part.endswith("*"):
            r = paragraph.add_run(part[1:-1]); r.italic = True
            if default_bold is not None:
                r.bold = default_bold
        elif part.startswith("`") and part.endswith("`"):
            r = paragraph.add_run(part[1:-1])
            if default_bold is not None:
                r.bold = default_bold
        else:
            r = paragraph.add_run(part)
            if default_bold is not None:
                r.bold = default_bold


def _add_para(doc, style: str, text: str = "", default_bold=None, keep_with_next: bool = False):
    p = doc.add_paragraph(style=style)
    if text:
        _add_runs(p, text, default_bold=default_bold)
    if keep_with_next:
        p.paragraph_format.keep_with_next = True
    return p


def _add_two_col(doc, style: str, left: str, right: str, keep_with_next: bool = False):
    p = doc.add_paragraph(style=style)
    _add_runs(p, left)
    p.add_run("\t")
    _add_runs(p, right)
    if keep_with_next:
        p.paragraph_format.keep_with_next = True
    return p


def _clear_body(doc):
    body = doc.element.body
    for child in list(body):
        tag = child.tag.split("}")[-1]
        if tag in ("p", "tbl"):
            body.remove(child)


def _ensure_role_context_style(doc):
    """Create `CV Role Context` if the template doesn't ship one.

    Role-context italic pre-texts (a paragraph directly under `### Role` +
    dates) render under a paragraph style distinct from company-tagline
    italics so template.docx can style them differently. If the template
    already defines `CV Role Context` (customized in Word by the user), we do
    not touch it. Otherwise clone from `CV Tagline` and override the font
    colour to auto/black so the rendered pre-text is IMMEDIATELY visually
    distinct from the (typically grey) company tagline; the user can tune the
    auto-created style further in Word later.
    """
    styles = doc.styles
    existing = {s.name for s in styles}
    if STYLE_ROLE_CONTEXT in existing:
        return
    new_style = styles.add_style(STYLE_ROLE_CONTEXT, WD_STYLE_TYPE.PARAGRAPH)
    if STYLE_TAGLINE in existing:
        new_style.base_style = styles[STYLE_TAGLINE]
    new_style.font.italic = True
    new_style.font.color.rgb = RGBColor(0x00, 0x00, 0x00)


def render(input_md: str, output_docx: str, template_docx: str) -> None:
    with open(input_md, encoding="utf-8") as f:
        md = f.read()

    blocks = _parse_blocks(md)
    doc = Document(template_docx)
    _ensure_role_context_style(doc)
    _clear_body(doc)

    current_section = None
    section_emitted = False
    n = len(blocks)
    i = 0

    while i < n:
        kind, content = blocks[i]

        if kind in ("blank", "hr"):
            i += 1
            continue

        if kind == "h1":
            _add_para(doc, STYLE_TITLE, content)
            i += 1
            continue

        if kind == "h2":
            label = content.upper()
            if label in SECTION_H2:
                _add_para(doc, STYLE_SECTION, content, keep_with_next=True)
                section_emitted = True
                if "SKILL" in label:
                    current_section = "skills"
                elif "EDUC" in label or "CERT" in label:
                    current_section = "education"
                else:
                    current_section = None
                i += 1
                continue

            if not section_emitted:
                _add_para(doc, STYLE_SECTION, "PROFESSIONAL EXPERIENCE", keep_with_next=True)
                section_emitted = True

            current_section = None
            company = content
            j = i + 1
            while j < n and blocks[j][0] == "blank":
                j += 1

            location = None
            if j < n and blocks[j][0] == "text":
                location = _drop_trailing_dates(blocks[j][1])
                j += 1
                while j < n and blocks[j][0] == "blank":
                    j += 1
                if j < n and blocks[j][0] == "text":
                    j += 1

            while j < n and blocks[j][0] == "blank":
                j += 1

            tagline = None
            if j < n and blocks[j][0] == "italic":
                tagline = blocks[j][1]
                j += 1

            if location:
                _add_two_col(doc, STYLE_COMPANY, company, location, keep_with_next=True)
            else:
                _add_para(doc, STYLE_COMPANY, company, keep_with_next=True)
            if tagline:
                _add_para(doc, STYLE_TAGLINE, tagline, keep_with_next=True)
            i = j
            continue

        if kind == "h3":
            role = content
            j = i + 1
            while j < n and blocks[j][0] == "blank":
                j += 1
            dates = None
            if j < n and blocks[j][0] == "text":
                dates = blocks[j][1]
                j += 1
            while j < n and blocks[j][0] == "blank":
                j += 1
            role_context = None
            if j < n and blocks[j][0] == "italic":
                role_context = blocks[j][1]
                j += 1
            if dates:
                _add_two_col(doc, STYLE_ROLE, role, dates, keep_with_next=True)
            else:
                _add_para(doc, STYLE_ROLE, role, keep_with_next=True)
            if role_context:
                _add_para(doc, STYLE_ROLE_CONTEXT, role_context, keep_with_next=True)
            i = j
            continue

        if kind in ("bullet", "subbullet"):
            j = i + 1
            dates = None
            if kind == "bullet" and current_section == "education":
                jj = j
                while jj < n and blocks[jj][0] == "blank":
                    jj += 1
                if jj < n and blocks[jj][0] == "text":
                    dates = blocks[jj][1]
                    j = jj + 1
            k = j
            while k < n and blocks[k][0] in ("blank", "hr"):
                k += 1
            next_glues = k < n and blocks[k][0] in ("bullet", "subbullet")
            if current_section == "skills":
                _add_para(doc, STYLE_SKILL, content, default_bold=False, keep_with_next=next_glues)
            elif current_section == "education" and kind == "subbullet":
                _add_para(doc, STYLE_EDUCATION, content, keep_with_next=next_glues)
            elif dates is not None:
                _add_two_col(doc, STYLE_BULLET, content, dates, keep_with_next=next_glues)
            else:
                _add_para(doc, STYLE_BULLET, content, keep_with_next=next_glues)
            i = j
            continue

        if kind == "italic":
            _add_para(doc, STYLE_TAGLINE, content, keep_with_next=True)
            i += 1
            continue

        if kind == "text":
            if "·" in content and "@" in content:
                _add_para(doc, STYLE_CONTACT, content)
            else:
                _add_para(doc, STYLE_TARGET, content)
            i += 1
            continue

        i += 1

    doc.save(output_docx)


def _docx_to_pdf(docx_path: str) -> str | None:
    """Convert docx to PDF via LibreOffice headless. Returns PDF path on success, None on skip/fail (docx still valid)."""
    soffice = shutil.which("soffice") or shutil.which("libreoffice")
    if not soffice:
        print("PDF skipped: 'soffice' / 'libreoffice' not on PATH (install LibreOffice to enable).", file=sys.stderr)
        return None
    outdir = os.path.dirname(os.path.abspath(docx_path)) or "."
    try:
        result = subprocess.run(
            [soffice, "--headless", "--convert-to", "pdf", "--outdir", outdir, docx_path],
            capture_output=True, text=True, timeout=120,
        )
    except subprocess.TimeoutExpired:
        print("PDF skipped: LibreOffice conversion timed out after 120s.", file=sys.stderr)
        return None
    if result.returncode != 0:
        print(f"PDF skipped: soffice exit {result.returncode}: {result.stderr.strip()}", file=sys.stderr)
        return None
    pdf_path = os.path.splitext(docx_path)[0] + ".pdf"
    if not os.path.exists(pdf_path):
        print(f"PDF skipped: expected {pdf_path} not produced (soffice stdout: {result.stdout.strip()})", file=sys.stderr)
        return None
    return pdf_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Render a Markdown CV to .docx (and PDF) with template fidelity.")
    parser.add_argument("input_md")
    parser.add_argument("output_docx", help="Output .docx path OR an existing directory (auto-names as '<InitialLast> - <Role>.docx' derived from the markdown H1 + SUMMARY headline).")
    parser.add_argument("template_docx")
    parser.add_argument("--no-pdf", action="store_true", help="Skip the docx→PDF LibreOffice step.")
    args = parser.parse_args()
    if os.path.isdir(args.output_docx):
        name_token = _extract_name_shorthand(args.input_md)
        role = _extract_summary_role(args.input_md)
        if name_token and role:
            filename = f"{name_token} - {role}.docx"
        elif name_token:
            filename = f"{name_token}.docx"
        else:
            filename = "cv.docx"
        output_path = os.path.join(args.output_docx, filename)
    else:
        output_path = args.output_docx
    render(args.input_md, output_path, args.template_docx)
    print(f"Wrote {output_path}")
    if not args.no_pdf:
        pdf_path = _docx_to_pdf(output_path)
        if pdf_path:
            print(f"Wrote {pdf_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
