# Rule iterations log — when to update `rule_iterations_state.json`

`rule_iterations_state.json` at the repo root is an append-only log of every change to the system's rules, agents, commands, or master-CV structural conventions. It exists so you can scan over time and detect:

- **Rule churn** — same rule re-edited N times in K iterations → the rule is mis-shaped, not just the wording.
- **Vacancy overfit** — same vacancy slug driving multiple iterations → that vacancy is overfitting the system. Anchor changes in vacancy *shape*, not the specific company.
- **Recurring failure modes** — same root cause across iterations → systemic problem in drafter / critic discipline, not solvable by another patch.
- **Regression risk on a change** — explicit field per entry, so we can later check whether a feared regression materialized.

The whole point of this repo is a repeatable pipeline that keeps improving. Without the log, every iteration is discharged in isolation and patterns are invisible.

## When to append an entry

Append a new entry to `rule_iterations_state.json` whenever the current task changes any of:

- `.claude/rules/**/*.md` — rule files.
- `.claude/agents/**/*.md` — subagent prompts.
- `.claude/commands/**/*.md` — slash-command prompts.
- `CLAUDE.md` — root manifest.
- `MASTER_CV.md` **structural conventions only** — format changes (new framing-catalog shape, new tag, new pool structure). NOT content edits (a new bullet, a fixed typo, an updated NOTES line are content, not structural).

Always append BEFORE marking the iteration done.

## When NOT to append

- Per-vacancy artifacts: `vacancies/<slug>/vacancy.md`, `analysis.md`, `cv.md`, `cv.docx`.
- Master-CV content edits (adding a bullet, fixing a number, removing an outdated note).
- Renderer / tooling edits (`bin/render_cv.py`, `template.docx`) — log informally via commit history.
- Memory updates under `.claude/projects/*/memory/`.

## Entry schema

Each entry is a JSON object inside the `iterations` array. Fields:

```json
{
  "id": <integer, monotonic — next-highest of existing ids + 1>,
  "date": "YYYY-MM-DD",
  "trigger": {
    "kind": "vacancy_pushback | proactive | user_request",
    "vacancy_slug": "<slug or null if proactive / cross-vacancy>",
    "what_user_flagged": "<one-sentence: the failure mode the user named, or 'n/a' if proactive>"
  },
  "files_changed": ["<repo-relative path>", "..."],
  "change_summary": "<one-sentence: what was changed>",
  "failure_mode_fixed": "<one-sentence: the underlying root cause the change addresses>",
  "regression_risk": "<one-sentence: which vacancy shapes this change might overfit / break, or 'none' if low-risk>",
  "follow_up": "<one-sentence: open question, planned next iteration, or null>"
}
```

Field discipline:

- **`change_summary`** — what changed at the rule layer. Not what changed in `cv.md`.
- **`failure_mode_fixed`** — the *root cause*, not the surface symptom. "Drafter padded Skills" is a symptom; "Drafter rationalized 'AI products' as a domain noun licensing every ML library" is a root cause.
- **`regression_risk`** — name the *shape* of vacancy that might break. "Vacancies where the candidate's only credential is one repo" beats "some other vacancy."
- **`follow_up`** — the next iteration's likely trigger, if predictable. Otherwise `null`.

## How to scan the log

Before starting a new vacancy or before proposing a new rule change:

1. Read `rule_iterations_state.json`.
2. Group by `files_changed`. Any file appearing in > 3 iterations is at structural-rework risk, not patch risk.
3. Group by `trigger.vacancy_slug`. A single vacancy with > 3 iterations is the overfit signal — future changes must justify how they generalize beyond that vacancy.
4. Scan `failure_mode_fixed` for repeat root causes. The same root cause appearing twice means the prior fix didn't work; the third occurrence is a system-design problem (drafter or critic prompt shape), not a per-rule fix.

If a proposed change would push any file past 3 iterations or any vacancy past 3 iterations, surface this to the user before editing.

## Format conventions

- JSON object: `{ "schema": "v1", "purpose": "...", "schema_doc": "...", "iterations": [ ... ] }`.
- Append new entries to the END of the `iterations` array.
- Pretty-print with 2-space indent so the file is readable in diffs.
- Never reorder, edit, or delete a historical entry — append-only. To correct a historical entry, append a new entry that supersedes it and link via the `follow_up` field.
- The file IS editable by the user — if they amend a `regression_risk` or `follow_up` post-hoc, that's allowed; the append-only discipline is about the historical record of *what changed when*, not about preventing field refinement.
