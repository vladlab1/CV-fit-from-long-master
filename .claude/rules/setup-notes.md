# Setup notes

- Python dependencies for the renderer and pipeline helpers are managed via `uv` — see `pyproject.toml` (or the PEP 723 inline metadata in `bin/render_cv.py`). You don't need a separate virtualenv; `uv run bin/render_cv.py ...` resolves deps automatically.
- `template.docx` at the repo root ships with the named styles the renderer expects (`CV Title`, `CV Contact`, `CV Section`, `CV Company`, `CV Role`, `CV Role Context`, `CV Tagline`, `CV Bullet`, `CV Skill Line`, `CV Education courses`, `Hyperlink`). You can tune their visual settings in Word — the renderer picks up whatever the template defines.
- Edit `MASTER_CV.md` at the repo root to describe your own career. The structure (Role framings catalog + flat Achievements pool per company, function tags like `[pm]` / `[ds]` / `[ai]`, keyword parentheticals `*(...)*` on each bullet, `## NOTES — not for export` block at the bottom) is binding — slash commands rely on it.
- Rule files in `.claude/rules/` are living documents. Edit them as you learn what framing works for your own interviews; iterations get logged in `rule_iterations_state.json`.
