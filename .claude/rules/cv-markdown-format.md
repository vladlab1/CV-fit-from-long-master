# CV markdown format

> **Note on examples**: Worked examples in this file reference the author's original use case (consulting, oil & gas, mapping, satellite imagery). Read them as *patterns* and substitute your own companies, products, and vacancies. The rules themselves are domain-agnostic.

The tailored CV is a markdown document that the downstream renderer (`bin/render_cv.py`) converts into `.docx` using `./template.docx`. The structure below is the exact convention the renderer expects — deviating from it produces a broken docx.

**Master vs. output:** `MASTER_CV.md` stores each company as a **Role framings catalog** + a **flat Achievements pool** (see `variant-and-bullet-selection.md`). The output `cv.md` is the collapsed, renderer-shaped version — one framing is picked per company, pool bullets are selected by vacancy fit, each bullet is placed under whichever role slot of the framing tells the strongest story, and the result is emitted in the structure below. The master's framings catalog, function tags, and keyword parentheticals never appear on output.

## Required markdown structure

```markdown
# Alex Rivera

Your City, Your Country · +00 000 000 000 · your.email@example.com · [linkedin.com/in/your-handle/](https://linkedin.com/in/your-handle/) · [example-product.com](https://example-product.com)

## SUMMARY

<Vacancy-aligned headline>. <One-sentence pitch tying experience to the vacancy's primary signals.>

## PROFESSIONAL EXPERIENCE

## COMPANY NAME
Location

*Italic one-sentence company / context summary, optionally rewritten to align with vacancy framing.*

### Role Title
Role dates

- Bullet 1.
- Bullet 2.

### Optional Second Role
Role dates

*Optional italic role-context sentence — REQUIRED for sparse role slots (0-bullet or 1-bullet). Renders as CV Tagline style, same as the company tagline.*

- Bullet 1.

## NEXT COMPANY
Location

*Italic company tagline.*

### Role Title
Role dates

- Bullets...

## EDUCATION & CERTIFICATIONS

- Item 1
- Item 2
- Gubkin University, MSc in Petrophysics
Sep 2004 – Jul 2009
  - Optional indented sub-detail rendered as `CV Education courses` (no bullet, deeper indent).

## SKILLS

- **Category:** items, comma-separated
- **Next category:** ...
```

## Conventions — every one is required

- `# Alex Rivera` is the name. Always present.
- The line directly under the name is the contact line (with ` · ` separators and the email). Always present.
- **Tailor the contact line per vacancy.** Each slot is gated by vacancy fit:
    - **LinkedIn, email, phone:** always stay.
    - **Product / project links** (e.g. `[bevra.app](https://bevra.app)`): keep on PM, SaaS, or AI-builder vacancies where the product is on-axis evidence. Drop on Applied Scientist / pure DS / non-builder vacancies — costs a slot, signals off-target.
    - **GitHub profile** (`[github.com/rhodaris](https://github.com/rhodaris)`): keep on any technical IC framing where the audience expects to see code — `[pe]`, `[eng]`, `[ds]`, `[ai]`, `[pm-eng]`, `[fde]`, hybrid technical-PM, senior-IC PM. Drop on pure non-technical framings — `[pm]` pure (no shipping signal expected), Director / Head / exec, `[geo]`, sales / CS / marketing.
    - When in doubt, drop. Contact-line slots are scarce; off-target slots dilute the on-target ones.
- `## SUMMARY` is mandatory. Under it: a single paragraph — vacancy-aligned headline plus a one-sentence pitch tied to the vacancy. Plain text, no bold (the section header carries the visual weight; bolding the headline made it visually noisy). No bullets.
- `## PROFESSIONAL EXPERIENCE` is mandatory and comes before the first company. (Renderer auto-inserts it if missing, but include it explicitly.)
- Each company is `## COMPANY NAME`. The first non-blank line under it is the **location only** (city / country / remote). No company-level dates line — dates live on the role.
- The italic line under the location is the company tagline. **Tailor it per vacancy.** Master lists tagline alternatives per company via inline `[instruction]` lines (e.g. Baker Hughes default vs. geospatial-flavour). Pick the closest preset; if no preset cleanly fits, rewrite the tagline inline to align with the vacancy — facts must remain accurate (no inventing scale, scope, or domain). When a preset bundles relevant *and* irrelevant claims (e.g. "2D mapping AND 3D geological modelling" on a maps-only vacancy), trim to the relevant half rather than keep the noise.
- Each role is `### Role Title`. The line directly under it is the role's dates (e.g., `Jul 2023 – Dec 2024`, `Jan 2025 – present`).
- **Optional role-context pre-text.** An italic paragraph directly under the role dates line renders as `CV Role Context` — a paragraph style DISTINCT from the company italic tagline's `CV Tagline`. The renderer detects role-position italics inside the `h3` branch and emits them under `CV Role Context`; `CV Tagline` remains reserved for the italic paragraph directly under a `## COMPANY` header. If `template.docx` doesn't ship a `CV Role Context` style, the renderer auto-creates it (based on `CV Tagline`, italic, font colour = black) so role pre-texts land IMMEDIATELY visually distinct from the (typically grey) company taglines. `template.docx` can override the auto-created default — customize `CV Role Context` in Word and the renderer preserves it. Use the pre-text to carry a one-sentence framing of the role's scope: what the user worked on, on what platform / product / system / team / customer set. **REQUIRED** per `variant-and-bullet-selection.md` "Sparse-slot narrative anchor" rule when a role slot has 0 or 1 bullets; **OPTIONAL** on multi-bullet slots (emergent context from the bullet collection generally suffices). Content rules from `style-antipatterns.md` and the accuracy bounds from `variant-and-bullet-selection.md` apply — every pre-text must be defensible from `MASTER_CV.md` context.
- **Reverse chronological order throughout.** Companies appear newest-tenure first (Rhodaris → Baker Hughes → Wintershall → … → Roxar). Within a multi-role framing for one company, the same applies — the newer sub-role appears BEFORE the older one (e.g. `### Sr. Product Manager` / `Jul 2023 – Dec 2024` BEFORE `### Senior Data Scientist` / `Oct 2019 – Jun 2023`).
- Bullets are `- ` items under their role. STRIP the master's function tag (`` `[pm]` ``) and trailing `*(keywords)*` from every bullet. Those are master-only annotations and must NOT appear in the output.
- `## EDUCATION & CERTIFICATIONS` and `## SKILLS` are H2 section headers at the end. Education entries render as standard `CV Bullet` paragraphs (bulleted). Skills entries render as `CV Skill Line` paragraphs (label/body, `**Category:**` is bold, body is plain — set by the renderer to override the style's baseline bold).
- **Markdown links `[label](url)` are emitted as real docx hyperlinks** (Word's `Hyperlink` character style if present in the template). Works in any paragraph — contact line, bullets, taglines. URLs must not contain unbalanced parentheses; if you need one with `)` inside, percent-encode it as `%29`.
- **Link every body mention of a master-linked term.** If a term carries a markdown link in *any* master bullet (e.g. `[content-advisor](https://github.com/rhodaris/content-advisor)`, `[bevra.app](https://bevra.app)`), **every** mention of that term **in the document body** must carry the link, even if the *selected* bullet wasn't the one that originally held the link in master. Body starts at `## SUMMARY` and includes SUMMARY paragraph, company taglines, role headers, and bullets. The contact line is a separate registry slot — link presence there is independent of body links. Treat the master as the authoritative link registry for project / product / repo names — never emit a known linkable term as plain text in the body. *Reason: linking only the first mention produced visual inconsistency on the rendered docx (one underlined `bevra.app`, two plain ones); the user asked for every-mention linking on 2026-06-19.*
- **Nested sub-detail under an education entry** uses an indented sub-bullet — `  - <text>` (two spaces, dash, space). The renderer maps any indented `- ` line inside EDUCATION to the `CV Education courses` style (no bullet marker, deeper indent — used for thesis facets, coursework breakdown, etc.). Outside EDUCATION, indented `- ` lines fall back to `CV Bullet`.
- **Dates on an education entry** use the same two-line shape as `### Role` / dates. Put the dates on the line directly under the bullet, column-0, no `- ` prefix. The renderer right-aligns them at the page margin via a tab stop on `CV Bullet`. Example:
  ```
  - Gubkin University, MSc in Petrophysics
  Sep 2004 – Jul 2009
    - Optional indented sub-detail.
  ```

## Source of truth

`bin/render_cv.py` is the source of truth for the parsing convention. If the renderer changes, update this file in lockstep.
