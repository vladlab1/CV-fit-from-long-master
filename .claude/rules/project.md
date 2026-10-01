# Project conventions — CV-fit-from-long-master

> **Note on examples**: Worked examples in this file reference the author's original use case (consulting, oil & gas, mapping, satellite imagery). Read them as *patterns* and substitute your own companies, products, and vacancies. The rules themselves are domain-agnostic.

This repo iterates the candidate's CV against incoming vacancies. Master CV is canonical; vacancies live one-per-folder; rendered output mirrors a fixed Word template.

## Files

- `MASTER_CV.md` — canonical CV source. Each company is a **Role framings catalog** (tagged: `[pm]`, `[pm-eng]`, `[ds]`, `[geo]`, `[fde]`, …) listing the role shapes the company's tenure can be presented as, plus a **flat Achievements pool** where every bullet carries a function tag (`[pm]`, `[ai]`, `[eng]`, `[fde]`, `[ds]`, `[geo]`) and a `*(keywords)*` parenthetical. The `## NOTES — not for export` section at the bottom is **binding** — never drift those facts.
- `template.docx` — Word template with named styles (`CV Title`, `CV Company`, `CV Role`, `CV Bullet`, …). The renderer maps markdown elements to these styles.
- `bin/render_cv.py` — markdown→docx renderer. Ported from the old `mcp-pandoc` server, now lives here. Run via `uv run` (PEP 723 inline metadata declares python-docx).
- `.claude/rules/` — runtime rules, one file per topic. Slash commands (`/cv-analyse`, `/cv-draft`, `/cv-render`) reference specific rules; this `project.md` is the entry point and is auto-loaded via the root `CLAUDE.md` manifest.

## Workflow — one vacancy = one folder under `vacancies/<slug>/`

Slug = `<company>-<YYYY-MM-DD>-<position>` (e.g. `cognite-2026-06-08-data-scientist-manager`). Company-first so folders sort by company in the file tree. Each folder holds the full history of one application:

```
vacancies/<slug>/
├── vacancy.md   — pasted JD + your notes  (input)
├── analysis.md  — output of /cv-analyse
├── cv.md        — output of /cv-draft, then edited by hand
└── cv.docx      — output of /cv-render
```

Steps:

1. Drop the vacancy into a new `vacancies/<slug>/vacancy.md`.
2. `/cv-analyse <slug>` — ATS matrix, industry fit, gap list. Edits nothing outside the slug folder.
3. Review `analysis.md`. If gaps point to real experience missing from master, **you** edit `MASTER_CV.md` by hand — commands never touch master.
4. `/cv-draft <slug>` — produces `cv.md`. Picks a role framing per company, selects bullets from the company's flat pool by keyword/content match, places each bullet under whichever role slot of the framing tells the strongest story, and strips function tags and `*(keywords)*` annotations.
5. Edit `cv.md` by hand.
6. `/cv-render <slug>` — produces `cv.docx` and opens it.

## Universal rules — apply to every command

- **Read master fresh.** Every run re-reads `MASTER_CV.md`. Never cache prior-session content.
- **Never invent experience.** If the vacancy needs something not in master, it goes in the gap list, not in the CV. A tight CV with high-fit bullets beats a long CV padded with adjacent ones.
- **Senior register.** "Explored X" / "investigated Y" framing does not survive senior screening. Every advised bullet must reference concrete delivery — a number, a named product, or a measurable outcome.
- **Brutal, no empathy** in analysis. Flag inconsistencies, role-name mismatches, weak headlines, GenAI-vs-DS-vs-PM emphasis drift.
- **Strip annotations on draft output.** Function tags `[pm]`/`[ai]`/etc., framings-catalog metadata, and trailing `*(keywords)*` on bullets are master-only annotations — they must NOT appear in `cv.md`. The renderer also strips defensively, but `/cv-draft` must produce clean markdown.
- **NOTES is binding.** The `## NOTES — not for export` block at the bottom of `MASTER_CV.md` is the disambiguation guard (bevra.app stack details, Kosovo scope, Baker Hughes continuous tenure, etc.). Never drift those facts.

## Rule index

Deeper, on-demand rules live alongside this file:

- `inputs.md` — input authority order, master-CV-wins rule, surface-aware reading guidance.
- `ats-analysis.md` — Deliverable A (ATS matrix + gap list).
- `variant-and-bullet-selection.md` — Deliverable B framing-catalog + flat-pool selection logic (two-step: pick framing, then pick bullets from pool).
- `cv-markdown-format.md` — Deliverable B required markdown structure for `cv.md` (renderer convention).
- `style-antipatterns.md` — Deliverable B prose rules the user has rejected (append-only as new patterns surface; binding on every emitted line).
- `delivery.md` — surface-specific delivery (file in Claude Code vs. artifact in Claude.ai).
- `cover-letter.md` — Deliverable C (cover letter).
- `rule-iterations-log.md` — when and how to append to `rule_iterations_state.json` (the longitudinal log of system-level changes at the repo root; scan it before proposing rule edits to detect overfit and rule churn).
- `setup-notes.md` — humans-only setup notes, ignore at runtime.
