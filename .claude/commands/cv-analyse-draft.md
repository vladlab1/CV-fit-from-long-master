---
description: End-to-end CV pipeline for one vacancy. Resolves the input (slug / dropped JD file / URL / raw text) into a vacancies/<slug>/ folder, then hands off to bin/cv_pipeline.sh, which runs /cv-analyse and /cv-draft as fresh 'claude -p' subprocesses with per-step timeout, artifact verification, and retry. All activity is logged to vacancies/<slug>/.activity.jsonl.
---

Argument: `$ARGUMENTS` — a slug, a dropped file path (`.pdf`/`.docx`/`.txt`/`.md`), a URL, or raw vacancy text. Same input shapes as `/cv-analyse`.

## Why this command exists

the user's workflow: drag a JD (usually a PDF) into a fresh chat, run one command, walk away. `/cv-analyse` and `/cv-draft` run back-to-back sometimes fail mid-run — token cap, hung subagent, silently-skipped critique gate. In-chat retry can't rescue a session that ran out of context because the turn itself ends. The fix is subprocess-per-step: each attempt is a fresh `claude -p` invocation with its own context window, wrapped in `timeout` + retry, driven by `bin/cv_pipeline.sh`. This command is the chat-side entry point that resolves the input, then hands off to that shell script.

## Step 1 — Resolve the input into a slug + `vacancy.md` on disk

The shell wrapper does NOT do input resolution — it expects `vacancies/<slug>/vacancy.md` to exist. So Claude does this step in-chat before shelling out.

Follow the "Resolve the slug" section of `.claude/commands/cv-analyse.md` verbatim. Handle every input shape:

- **Looks like a slug** — use as-is, verify `vacancies/<slug>/vacancy.md` exists.
- **Path to a file** (`.pdf`/`.docx`/`.txt`/`.md`) — extract the vacancy text, derive slug as `<company>-<YYYY-MM-DD>-<position>` (today's date, lowercase kebab-case), create `vacancies/<slug>/`, save text as `vacancy.md`.
- **URL** — fetch, extract, then same as file path.
- **Raw text** — treat as vacancy text, derive slug, save as above.
- **Empty / unrecognized** — stop and ask.

After this step: the slug is known, `vacancies/<slug>/` exists, and `vacancies/<slug>/vacancy.md` is populated.

**Do NOT proceed to Step 2 without a valid slug + vacancy.md on disk** — the shell wrapper's precondition check will fail loudly and useless.

**Tell the user the slug you used** if you derived it (from a file/URL/raw text) — he may want to rename the folder before the pipeline runs.

## Step 2 — Hand off to bin/cv_pipeline.sh

Run this exact Bash command (substituting the resolved slug):

```bash
bin/cv_pipeline.sh --slug <slug>
```

Defaults: `--steps both`, `--timeout-sec 1200` (20 min per step), `--max-retries 2` (3 total attempts per step). Override if the vacancy is known to be unusually large / slow:

- `--timeout-sec 1800` — 30 min per step; for JDs with dense stack lists or heavy analysis rounds.
- `--max-retries 1` — 2 attempts total per step; for cost-sensitive runs.
- `--steps analyse` or `--steps draft` — run only one step (e.g. `analyse` already succeeded in a prior chat, only draft needs to re-run).

The wrapper does all the real work: for each step it spawns `claude -p '/cv-<step> <slug>'`, times it out at `--timeout-sec`, checks the expected artifact after each attempt, and retries on timeout / non-zero exit / artifact-check failure. Per-attempt stdout / stderr from the subprocess is captured to `vacancies/<slug>/.logs/<step>-attempt-<N>.log` so failures can be inspected. All pipeline events (attempt_start, attempt_end, timeout, artifact_check, retry, step_failed, end) are appended to `vacancies/<slug>/.activity.jsonl`.

Artifact checks the wrapper enforces:

- **After /cv-analyse**: `analysis.md` exists, size ≥ 500 bytes, contains `## Company product context` heading (iter #15), contains a gap-list marker.
- **After /cv-draft**: `cv.md` exists, size ≥ 1000 bytes, `.critic-log.json` exists, is valid JSON, `decision` is one of `CLEAN` / `SHOW-WITH-FLAGS` / `FORCED-SHOW-AFTER-3-LOOPS`, `rewrite_loops` is an integer.

The wrapper's exit code:
- `0` — all requested steps succeeded.
- `1` — a step failed after all retries.
- `2` — invalid usage / environment (missing `claude` CLI, missing `timeout`/`gtimeout`, missing `vacancy.md`, etc.).

## Step 3 — Report to the user

After the wrapper returns, do the following in order.

1. **On exit code 2** (usage / environment): the wrapper's stderr explains what's wrong. Repeat that verbatim to the user and stop — this is a machine setup issue, not a pipeline failure.

2. **On exit code 1** (step failed after retries): read the tail of `vacancies/<slug>/.activity.jsonl` (last ~10 lines) and the failed attempt's per-attempt log at `vacancies/<slug>/.logs/<step>-attempt-<N>.log`. Summarize in chat:
   - Which step failed (`analyse` or `draft`).
   - Number of attempts made and why each failed (timeout / non-zero exit / artifact check).
   - Which artifact check failed on the final attempt (from the wrapper's stderr, mirrored in the JSONL log).
   - Recommend the user's next move: run `/cv-<step> <slug>` manually in a fresh chat to isolate the failure, then re-run this command with `--steps <remaining-step>` once the failing step is fixed.

3. **On exit code 0** (success): read `vacancies/<slug>/analysis.md` and `vacancies/<slug>/cv.md` briefly (top of each) and `vacancies/<slug>/.critic-log.json` fully, then print one block:

   ```
   /cv-analyse-draft complete — <slug>

   Analysis (vacancies/<slug>/analysis.md):
   - Top fit signal: <one-liner from analysis.md top section>
   - Biggest gap: <one-liner from GAP LIST>

   Draft (vacancies/<slug>/cv.md):
   - Framing per company: <inferred from cv.md structure>
   - Bullet count: <total bullets under PROFESSIONAL EXPERIENCE>
   - Critic decision: <decision> after <rewrite_loops> rewrite loop(s)

   Attempts summary (from .activity.jsonl):
   - /cv-analyse: <N attempts, T total seconds>
   - /cv-draft: <N attempts, T total seconds>

   Next: /cv-render <slug> to produce docx + PDF.
   ```

   If the critic log's decision is `SHOW-WITH-FLAGS` or `FORCED-SHOW-AFTER-3-LOOPS`, note that the user should review the flags (the wrapper does NOT surface them — that responsibility stayed inside `/cv-draft`'s original Step 7 output, captured in the per-attempt log at `vacancies/<slug>/.logs/draft-attempt-<N>.log`).

## Constraints

- **Do NOT try to reimplement the retry logic in-chat.** The whole point of this command is that the shell script owns retries — with real `timeout` and fresh subprocess context per attempt. In-chat retry can't rescue context-cap failures because the turn dies with the context. If the wrapper isn't there or doesn't run, stop and tell the user — do not fall back to in-chat orchestration.
- **Do NOT skip Step 1's slug resolution.** The wrapper's precondition is `vacancies/<slug>/vacancy.md` on disk. Passing a raw path or URL directly to the wrapper fails the precondition check.
- **Do NOT stub artifacts to make the check pass.** If `/cv-draft` skips the critique gate (that's the failure mode this whole system exists to catch), do NOT hand-write `.critic-log.json` to satisfy the wrapper's check. The check exists to detect that skip; papering over it defeats the discipline.
- Universal rules from `.claude/rules/project.md` (auto-loaded via `CLAUDE.md`) apply — master read fresh in each subprocess (each fresh `claude -p` starts from cold anyway), never invent experience, senior register, NOTES-block binding.
