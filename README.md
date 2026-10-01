# CV-fit-from-long-master

Tailor one long master CV into vacancy-specific CVs with Claude Code. ATS gap analysis, bullet selection by vacancy fit, and `.docx` rendering against a Word template — all driven by slash commands.

**Status:** working template. Forked from a private CV-automation repo and depersonalized. The included `MASTER_CV.md` is a fictional "Alex Rivera" persona — **replace it with your own career before using**.

---

## What this does

You keep ONE long "master" CV with everything you've ever done, structured as a *framings catalog* (ways you can present each tenure) + *flat achievements pool* (all your bullets, tagged by function and keywords) per company. For each new job you want:

1. Drop the JD into `vacancies/<slug>/vacancy.md`.
2. `/cv-analyse <slug>` → ATS matrix + brutal gap list → `analysis.md`.
3. `/cv-draft <slug>` → tailored CV markdown (framings picked per vacancy, bullets selected by relevance) → `cv.md`.
4. `/cv-render <slug>` → `cv.docx` (and `.pdf` if LibreOffice is installed) using `template.docx`.

The automation reads your master fresh every time, never invents experience, and runs a critic loop over the draft before you see it.

---

## Requirements

- [Claude Code](https://docs.claude.com/en/docs/claude-code) (desktop app or CLI)
- [uv](https://docs.astral.sh/uv/) — Python package manager
- [LibreOffice](https://www.libreoffice.org/) — optional, for `.docx` → `.pdf` export (`brew install --cask libreoffice` on macOS, or your distro's equivalent)

That's it. Everything else (python-docx, template.docx) ships with the repo.

---

## Quick start

```bash
git clone <this-repo> my-cv
cd my-cv
uv sync                          # installs python-docx into .venv/
```

Then in Claude Code (point it at this directory):

```
/cv-analyse apply-ai-labs-2026-10-15-staff-ml-engineer   # creates folder + runs analysis
/cv-draft apply-ai-labs-2026-10-15-staff-ml-engineer
/cv-render apply-ai-labs-2026-10-15-staff-ml-engineer
```

(The slash commands also accept raw JD text, a URL, or a path to a PDF/DOCX — they'll derive a slug automatically. See `.claude/commands/cv-analyse.md`.)

---

## Make it yours — before the first real run

1. **Rewrite `MASTER_CV.md`** — this is the biggest and most important step. The included persona ("Alex Rivera") is fictional; keep the *structure* (role framings catalog + flat achievements pool per company + binding `NOTES` block at the bottom) but replace every bullet with your own concrete work. Read `.claude/rules/variant-and-bullet-selection.md` for the format rules.

2. **Edit the contact line** at the top of `MASTER_CV.md` with your name, email, location, LinkedIn, and any product/project links you want on the CV. These flow through to every rendered output.

3. **Optional: tune `template.docx`** — the Word template ships with named styles (`CV Title`, `CV Company`, `CV Role`, `CV Bullet`, `CV Skill Line`, `CV Education courses`, `CV Tagline`, `CV Role Context`). Open it in Word to adjust fonts, spacing, or colors. Do NOT rename the styles — the renderer looks them up by name.

4. **Read the rules at least once**: `.claude/rules/project.md` is the entry point (auto-loaded via `CLAUDE.md`). The deep rules live alongside it — `variant-and-bullet-selection.md` is the biggest and most load-bearing.

---

## Repo layout

```
.
├── CLAUDE.md                 # Thin manifest — auto-loads project rules
├── MASTER_CV.md              # Your long canonical CV (edit me first)
├── STATUS.md                 # Session-persistence file (per global convention)
├── pyproject.toml            # uv-managed deps (python-docx only)
├── template.docx             # Word template — ships with named styles
├── bin/
│   ├── render_cv.py          # Markdown → .docx renderer (uv run)
│   ├── cv_pipeline.sh        # Optional end-to-end runner with retry/resume
│   ├── cv_log_event.py       # Activity logger for the pipeline
│   ├── cv_draft_resume_state.py  # Mid-run resume classifier
│   ├── build_applications_chart.py  # Stats dashboard (optional)
│   └── applications-chart-template.html
├── vacancies/                # One folder per application
│   └── example-corp-2026-01-15-product-manager/
│       ├── vacancy.md        # JD (input)
│       ├── analysis.md       # /cv-analyse output
│       ├── cv.md             # /cv-draft output
│       └── cv.docx           # /cv-render output
└── .claude/
    ├── rules/                # On-demand rule files, one per topic
    ├── commands/             # Slash-command definitions
    └── agents/               # draft-critic subagents (post-draft review)
```

---

## Slash commands

| Command | Purpose |
|---|---|
| `/cv-analyse <slug\|path\|url\|text>` | ATS matrix + industry fit + gap list. Writes `analysis.md`. |
| `/cv-draft <slug>` | Pick framings + select bullets + emit tailored CV. Writes `cv.md`. Runs a mandatory critic loop before returning. |
| `/cv-draft-light <slug>` | Delta-patch an existing nearby `cv.md` instead of drafting from scratch — cheaper when a prior application is close in shape. |
| `/cv-analyse-draft <slug\|path\|url\|text>` | End-to-end pipeline (analyse → draft) via `bin/cv_pipeline.sh` with retry + rate-limit handling. |
| `/cv-render <slug>` | Render `cv.md` → `cv.docx` (and `.pdf` if LibreOffice is installed). |
| `/cv-applications-stats` | Rebuild `applications.csv` + chart dashboard from the `vacancies/` folder. |
| `/cv-interview-prep-plan <slug>` | Produce a prep-doc for an upcoming interview round. |

---

## Design principles

- **Master wins on conflict.** The commands never invent experience; a vacancy requirement with no master backing goes in the gap list, not the CV.
- **One vacancy = one folder.** `vacancies/<company>-<YYYY-MM-DD>-<position>/` holds the full history of one application. Folders sort by company in the tree.
- **Rules are the surface.** Behavior lives in `.claude/rules/`. Slash commands read specific rules on demand. The root `CLAUDE.md` is a thin manifest; edit the rules, not the manifest.
- **Critic gate is mandatory.** `/cv-draft` always invokes `draft-critic` and writes `.critic-log.json`. `/cv-render` refuses to run without that breadcrumb — the discipline is enforced structurally.
- **Append-only iteration log.** When you change a rule or the master's structural convention, append an entry to `rule_iterations_state.json`. Scan it periodically to detect rule churn and overfit.

---

## Credits

Forked from a private CV automation project. Depersonalized and shared under the (fictional-persona) name "Alex Rivera" — all examples in `MASTER_CV.md` are made up. Many of the rule files still carry worked examples from the original author's career (consulting, oil & gas, mapping, satellite imagery) — treat these as *patterns* and substitute your own.

Contributions welcome: new rules, renderer improvements, or depersonalization fixes.
