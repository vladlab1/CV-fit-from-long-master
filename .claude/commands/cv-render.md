---
description: Render vacancies/<slug>/cv.md to cv.docx (and cv.pdf) using template.docx.
---

Argument: `$ARGUMENTS` — the vacancy slug.

## What to do

0. **Log pipeline start.** Run:

   ```bash
   python3 bin/cv_log_event.py --slug $ARGUMENTS --command cv-render --phase start
   ```

   Appends one line to `vacancies/$ARGUMENTS/.activity.jsonl`. Silent on success; do not report to the user.

1. Confirm `vacancies/$ARGUMENTS/cv.md` exists. If missing, tell the user to run `/cv-draft $ARGUMENTS` first and stop.

1a. **Critic-gate precondition.** Confirm `vacancies/$ARGUMENTS/.critic-log.json` exists. This file is the breadcrumb written by `/cv-draft` after `draft-critic` runs. If it is MISSING, `/cv-draft` was invoked without the mandatory critique gate — the CV has not been reviewed by the critic. Do NOT render. Do NOT stub the log. Do NOT proceed by invoking the critic yourself as a shortcut. Instead:

- Tell the user the log is missing, name the failure mode ("`/cv-draft` was run without the mandatory critique gate"), and stop.
- The remediation is: re-run `/cv-draft $ARGUMENTS` — that command MUST invoke the critic and produce the log.

   the user hand-editing `cv.md` after the critic ran is NOT a violation — the log remains valid (the user's edits are trusted per the workflow). Only a MISSING log blocks render.

2. Run the renderer:

   ```bash
   uv run bin/render_cv.py "vacancies/$ARGUMENTS/cv.md" "vacancies/$ARGUMENTS" "template.docx"
   ```

   Passing the slug FOLDER (not a `.docx` file) as the second arg lets the renderer auto-name the output from `cv.md`'s SUMMARY headline — e.g. `ARivera - Product Manager.docx`. When the headline can't be parsed cleanly (empty, ambiguous, too long, non-standard), it falls back to `cv.docx` inside the same folder. The renderer prints the actual output paths — report both verbatim.

   After the .docx lands the renderer runs `soffice --headless --convert-to pdf` to emit a .pdf alongside it. If LibreOffice isn't on PATH the PDF step is skipped with a stderr warning and the docx still lands (report the warning). Pass `--no-pdf` to skip explicitly.

   `uv run` resolves `python-docx` automatically from the script's PEP 723 inline metadata — no global install needed, no venv to manage.
3. If the renderer errors, surface the error verbatim and stop. Common causes:

   - Markdown deviates from the structure required by `.claude/rules/cv-markdown-format.md` (e.g. company H2 without a location line, role H3 without a dates line, missing `## SUMMARY` / `## PROFESSIONAL EXPERIENCE` headers).
   - `template.docx` is missing one of the named styles (`CV Title`, `CV Company`, `CV Role`, `CV Bullet`, `CV Skill Line`, `CV Education courses`, …).
   - PDF step failures are non-fatal (the docx still lands with a stderr warning) — do NOT treat them as a renderer error.

   Don't paper over markdown issues in the renderer — fix them in `cv.md` (or `bin/render_cv.py` if the convention itself changed) and tell the user what was off. On a hard render error, log an end event with `result: "render_failed"`:

   ```bash
   python3 bin/cv_log_event.py --slug $ARGUMENTS --command cv-render --phase end --detail '{"result":"render_failed"}'
   ```

4. **Log artifacts + pipeline end.** After the renderer prints its output paths, run one event per artifact and then the end event:

   ```bash
   python3 bin/cv_log_event.py --slug $ARGUMENTS --command cv-render --phase artifact_written --detail '{"path":"<docx filename from renderer>","kind":"docx"}'
   python3 bin/cv_log_event.py --slug $ARGUMENTS --command cv-render --phase artifact_written --detail '{"path":"<pdf filename from renderer>","kind":"pdf"}'   # skip this line if the PDF step was skipped (soffice missing / --no-pdf)
   python3 bin/cv_log_event.py --slug $ARGUMENTS --command cv-render --phase end --detail '{"result":"success","pdf":<true|false>}'
   ```

   A start with no end reads as a crashed run to any log-tail reader.

## Constraints

- Don't edit `cv.md` from this command.
- Don't edit `template.docx` from this command.
- The renderer reads from the repo root (`template.docx`) and writes inside the slug folder. Run from the repo root.
- **Do NOT open the rendered docx or PDF** (no `open`, no `xdg-open`, no `start`). the user opens them manually. Report the output paths in chat and stop.