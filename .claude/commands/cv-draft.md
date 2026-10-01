---
description: Produce a tailored CV markdown from MASTER_CV + vacancy. Writes vacancies/<slug>/cv.md.
---

Argument: `$ARGUMENTS` — normally the vacancy slug. Other input shapes are accepted; see below.

## Resolve the slug

Before drafting, normalize `$ARGUMENTS` into a slug pointing at a `vacancies/<slug>/` folder that contains `vacancy.md`.

- **Looks like a slug** (e.g. `cognite-2026-06-08-data-scientist-manager`): use as-is. If `vacancies/<slug>/vacancy.md` is missing, check the folder for a vacancy-like file (`.pdf`, `.docx`, `.txt`, `.md`). If one is present, extract its text into `vacancies/<slug>/vacancy.md` before proceeding (same behaviour as the Path-to-a-file branch below — vacancy.md is the pipeline's authoritative vacancy text; downstream steps read from it). If nothing vacancy-like is in the folder, stop and ask the user to drop the vacancy text in.
- **Path to a file** (`.pdf`, `.docx`, `.txt`, `.md`): extract vacancy text. Derive slug as `<company>-<YYYY-MM-DD>-<position>` (today's date, lowercase kebab-case). Create `vacancies/<slug>/`. Save extracted text as `vacancy.md`. Note in chat that `/cv-analyse <slug>` is recommended before drafting (gap list anchors the bullet selection), but `/cv-draft` will still proceed without it.
- **URL**: fetch, extract, then same as above.
- **Raw vacancy text**: treat the argument as the vacancy. Derive slug. Create folder. Save as `vacancy.md`. Same note about `/cv-analyse` first.
- **Empty or unrecognized**: stop and ask the user what input he intended.

After this step, the slug is known and `vacancies/<slug>/vacancy.md` exists. Use that slug for the rest of the command.

## What to do

0. **Log pipeline start.** Run:

   ```bash
   python3 bin/cv_log_event.py --slug <slug> --command cv-draft --phase start
   ```

   Appends one line to `vacancies/<slug>/.activity.jsonl`. Silent on success; do not report to the user. Rest of the command's per-milestone events (critic invocations, terminal decision) are noted at the relevant steps below and MUST be emitted alongside the existing behavior — the wrapper reads this log as the ground truth of "what actually happened during draft."

0.5. **Resume classifier.** BEFORE Step 1, decide whether this invocation is a fresh run or a resume of a prior invocation that died mid-run (Anthropic rate-limit kill, wrapper silence-watchdog kill, subprocess crash). The shell wrapper `bin/cv_pipeline.sh` is stateless — every re-spawn is a plain `claude -p '/cv-draft <slug>'`. The resume decision lives HERE.

   **Read the resume state.** Run:

   ```bash
   python3 bin/cv_draft_resume_state.py --slug <slug>
   ```

   Prints a single JSON line to stdout describing what to do. Shape:

   ```json
   {
     "action": "fresh_start | resume_at_critic | resume_at_rewrite | already_done",
     "resume_loop": <integer or null>,
     "last_findings_path": "<relative path or null>",
     "reason": "<one-line human summary>"
   }
   ```

   Action semantics:

   - **`fresh_start`** — no prior in-flight state, or the prior run terminated successfully. Proceed to Step 1 normally.
   - **`already_done`** — `.critic-log.json` exists with a valid terminal decision AND matches the current `cv.md`. Log an end event with `result:"noop_already_done"` and exit. Do NOT rewrite `cv.md`.
   - **`resume_at_critic`** — `cv.md` on disk is the drafter's own output from a prior run at loop `resume_loop`. Skip Steps 1–6 (framing, bullet selection, emit) and jump straight to Step 7 with the current `cv.md`, invoking critic loop `resume_loop`. Emit a log event `python3 bin/cv_log_event.py --slug <slug> --command cv-draft --phase resumed --detail '{"action":"resume_at_critic","loop":<N>}'` before Step 7.
   - **`resume_at_rewrite`** — the prior run got a REWRITE decision from critic loop `resume_loop - 1` and died before finishing the rewrite. `last_findings_path` points at the saved findings JSON. Skip Steps 1–5. Read the findings from `last_findings_path`. Restore `cv.md` from the snapshot `.cv.md.after-loop-<resume_loop - 1>` if present (otherwise use current `cv.md`). Apply the rewrite per the findings. Then proceed to Step 7 to invoke critic loop `resume_loop`. Emit `resumed` log event as above with `action:"resume_at_rewrite","loop":<N>`.

   The classifier reads `.activity.jsonl` and the snapshot / findings files under `vacancies/<slug>/`; you do NOT re-implement its logic in prompt. Trust its output.

**MANDATORY: Step 7 (critique gate) MUST run on every invocation.** Not "usually", not "when the CV looks off", not "unless we're in a multi-command chain". Every time. `/cv-draft` is INCOMPLETE without the critic call and the `.critic-log.json` breadcrumb it produces. `/cv-render` refuses to run without the breadcrumb — so if you skip Step 7, the pipeline breaks by design. Skipping this gate has been flagged before (Gymdesk-2026-07-07-PM-AI iteration).

1. **Read fresh:**
   - `MASTER_CV.md` — ground truth. The `## NOTES — not for export` block is binding.
   - `vacancies/<slug>/vacancy.md` (slug from the resolution step above).
   - `vacancies/<slug>/analysis.md` if present — use it to anchor priorities. If it opens with a `## Company product context` section, treat that section as binding per the "Company product context — binding on the domain axis" subsection of `variant-and-bullet-selection.md`. It names the axis for bullet ranking and the SUMMARY closing clause.
   - `.claude/rules/inputs.md` — input authority order.
   - `.claude/rules/variant-and-bullet-selection.md` — Deliverable B variant + bullet selection logic.
   - `.claude/rules/cv-markdown-format.md` — required markdown structure the renderer expects.
   - `.claude/rules/style-antipatterns.md` — prose patterns the user has rejected; binding on every line of output.
   - `.claude/rules/delivery.md` — Claude Code delivery branch (writes to `cv.md`, not artifact).

2. **Framing selection.** Per company per `variant-and-bullet-selection.md`, map vacancy primary function to a tag (`[pm]` / `[pm-eng]` / `[ds]` / `[geo]` / etc.) and pick ONE framing from the company's Role framings catalog. Paraphrase the role title(s) to vacancy language if factually accurate (e.g. "Data Scientist" → "Senior Data Scientist" when the vacancy targets that level). The `## NOTES — not for export` section reconciles framing choices against the public LinkedIn profile — honor it. Honor inline `[instruction]` lines in master for parallel-track exclusions and conditional-company rules.

3. **Bullet selection from the pool.** Scan the entire company's Achievements pool — every bullet is in scope regardless of its function tag prefix (the function tag is an author note, not a filter). Match by:
   - Keyword parenthetical *(…)* — primary signal against vacancy keywords.
   - Bullet text — secondary signal against vacancy language and required skills.

   Order by relevance to the vacancy, not by chronology. Prefer concrete numbers / named products / measurable outcomes. When in doubt, leave a bullet out.

4. **Fill the framing's role slots.** Single-role framings: all selected bullets go under the one header. Multi-role framings: for each selected bullet, pick the role slot it best fits — using role title + bullet content + function tag as soft hints. Coherent narrative beats factual placement: a bullet doesn't need to live where it factually happened if it tells a stronger story under a different role of the same framing.

5. **Emit the tailored CV** in the exact structure documented in `cv-markdown-format.md`:
   - `# Alex Rivera` + contact line.
   - `## SUMMARY` — one paragraph: bold vacancy-aligned headline + one-sentence pitch.
   - `## PROFESSIONAL EXPERIENCE` then `## COMPANY` blocks (location line, italic tagline, `### Role` with dates line, bullets).
   - `## EDUCATION & CERTIFICATIONS` and `## SKILLS` last.
   - **STRIP** the function tag `[pm]`/`[ai]`/etc. and trailing `*(keywords)*` from every bullet. Output must be clean markdown — no master-only annotations leak through.
   - **APPLY `style-antipatterns.md` to every emitted line.** Rewrite master bullets/taglines/headlines that contain a listed antipattern. The rules override master phrasing.

6. **Write** to `vacancies/<slug>/cv.md`. Overwrite if it exists. Immediately after writing, log an artifact event AND snapshot the file so mid-rewrite kills are recoverable:

   ```bash
   python3 bin/cv_log_event.py --slug <slug> --command cv-draft --phase artifact_written --detail '{"path":"cv.md","state":"initial"}'
   cp vacancies/<slug>/cv.md vacancies/<slug>/.cv.md.after-loop-0
   ```

   The snapshot filename encodes which loop's *output* it captures. `after-loop-0` = initial draft (loop 0 output, pre-any-critic). After a Step 7 REWRITE that produces loop-N-rewrite output, snapshot again as `.cv.md.after-loop-<N>` (documented in Step 7 REWRITE branch below).

7. **Critique gate — MANDATORY on every run.** Before invoking the critic, log the invocation:

   ```bash
   python3 bin/cv_log_event.py --slug <slug> --command cv-draft --phase critic_invoked --detail '{"loop":<N>}'
   ```

   where `<N>` is the current rewrite loop number (0 for the first pass, 1 for the first rewrite, etc.). Emit this event BEFORE every critic invocation, including inside the REWRITE loop below. After the critic returns, log the outcome AND persist the critic's structured findings to disk for resume:

   ```bash
   # 1) Log the terminal event for this loop.
   python3 bin/cv_log_event.py --slug <slug> --command cv-draft --phase critic_returned --detail '{"loop":<N>,"decision":"<CLEAN|SHOW-WITH-FLAGS|REWRITE>","must_fix":<count>,"should_fix":<count>,"flag_to_user":<count>,"findings_path":".critic-findings-loop-<N>.json"}'

   # 2) Save the full critic output (the structured Findings + Decision the critic returned) as JSON.
   #    Write it with the Write tool, path: vacancies/<slug>/.critic-findings-loop-<N>.json
   #    Shape: {"loop": <N>, "decision": "...", "findings": [ ... verbatim critic Findings list ... ], "checked_at": "<ISO>"}
   ```

   The findings JSON is the RESUME PIVOT — if the wrapper kills the drafter mid-rewrite after this loop, the next invocation's resume classifier (Step 0.5) reads this file to reproduce the rewrite deterministically. Without it, mid-rewrite kills lose the critic's feedback and force a full restart.

   These events are the finest-grained trace the pipeline captures — they let the wrapper (and post-hoc debugging) see how many rewrite loops actually happened even if the run crashed before writing `.critic-log.json`. Now invoke the `draft-critic` subagent via the Agent tool (`subagent_type: draft-critic`) with the following invocation prompt:

   ```
   Inputs:
   - draft: vacancies/<slug>/cv.md
   - vacancy: vacancies/<slug>/vacancy.md
   - rule paths: .claude/rules/style-antipatterns.md, .claude/rules/cv-markdown-format.md, .claude/rules/variant-and-bullet-selection.md
   - master: MASTER_CV.md
   - analysis (optional): vacancies/<slug>/analysis.md   # omit if not present

   Return the structured Findings + Decision per your output format.
   ```

   Then act on the returned decision. **Every branch below is a TERMINAL branch — its last action MUST be to write `vacancies/<slug>/.critic-log.json` with the breadcrumb shape defined at the bottom of this step.** There is no exit path from Step 7 that does not write the log. Iteration #8 (Gymdesk) and iteration #13 (project44) both surfaced this exact failure — a "Write the breadcrumb" instruction placed AFTER the decision branches sits in a structural blind spot when a branch says "proceed to Step 8" because that reads as a jump past the write. Embedding the write inside each branch closes the blind spot; do not restructure this back to a trailing paragraph.

   - **REWRITE** — rewrite `cv.md` addressing every must-fix AND every should-fix finding (apply the proposed fix text — should-fix has a single recommended action per the critic format, not a menu). If a must-fix points at a master / rule defect rather than a draft defect, surface it to the user per `feedback_cv_pushback_means_system_fix` rather than papering over in `cv.md`. After the rewrite is written to disk, snapshot the new state so a subsequent mid-loop kill can roll back:

     ```bash
     cp vacancies/<slug>/cv.md vacancies/<slug>/.cv.md.after-loop-<M>
     ```

     where `<M>` is the loop that just produced this rewrite (i.e. the loop number in the `critic_returned` event that triggered the rewrite, plus one — the rewrite's own loop number). Then re-invoke `draft-critic` (which starts loop `<M>` — log `critic_invoked` for loop `<M>` first per the format above). Loop until CLEAN or SHOW-WITH-FLAGS. **Cap: 3 rewrite loops.** If still REWRITE after 3 loops, treat the terminal state as `FORCED-SHOW-AFTER-3-LOOPS`, surface the unresolved must-fixes to the user as flags, **then write `.critic-log.json` with `decision` set to the terminal state (`CLEAN` / `SHOW-WITH-FLAGS` / `FORCED-SHOW-AFTER-3-LOOPS`) and `rewrite_loops` set to the number of REWRITE rounds actually executed. Proceed to Step 8.**
   - **SHOW-WITH-FLAGS** — FIRST: apply every should-fix finding using the critic's single recommended action. Only escalate a should-fix to the user inline if the drafter has a specific rule-grounded reason to disagree with the critic's fix. THEN: surface every `flag-to-user` finding in chat verbatim with the trade-off and the critic's single recommended action. Do not present `option A | option B | option C` menus — the critic outputs one recommended action per flag, with at most one named alternative. the user decides on the flags only. **THEN write `.critic-log.json` with `decision: "SHOW-WITH-FLAGS"`, `rewrite_loops` set to the number of REWRITE rounds executed before this terminal state (0 if SHOW-WITH-FLAGS landed on the first critic pass), and the final finding counts. Proceed to Step 8.**
   - **CLEAN** — **write `.critic-log.json` with `decision: "CLEAN"`, `rewrite_loops` set to the number of REWRITE rounds executed before CLEAN (0 if CLEAN on first pass), and counts all zero. Proceed to Step 8.**

   Breadcrumb shape (used by all three branches):

   ```json
   {
     "cv_md_path": "vacancies/<slug>/cv.md",
     "decision": "CLEAN | SHOW-WITH-FLAGS | FORCED-SHOW-AFTER-3-LOOPS",
     "rewrite_loops": <integer, 0 if CLEAN on first pass>,
     "must_fix_count_final": <integer>,
     "should_fix_count_final": <integer>,
     "flag_to_user_count_final": <integer>,
     "critic_agent": "draft-critic",
     "checked_at": "<YYYY-MM-DDTHH:MM:SS>"
   }
   ```

   This file is `/cv-render`'s precondition — without it, render refuses to fire. Do NOT skip writing it. Do NOT stub a fake log to bypass the gate — that defeats the whole discipline. Truthful post-hoc writes (critic actually ran, values reflect real terminal state) are NOT stubs — stubs are fabricated values written to bypass a critic that never ran.

8. **Print** a one-line summary in chat: framing chosen per company (and any role-title paraphrase applied), total bullet count, which `analysis.md` gaps were intentionally left unaddressed (because the pool has nothing credible to back them), and the `draft-critic` decision (CLEAN / SHOW-WITH-FLAGS-after-N-loops / forced-show-after-3-loops).

9. **Log pipeline end.** After printing the summary, run:

   ```bash
   python3 bin/cv_log_event.py --slug <slug> --command cv-draft --phase end --detail '{"result":"success","decision":"<terminal decision>","rewrite_loops":<N>}'
   ```

   On EARLY EXITS (missing input, master defect surfaced via `feedback_cv_pushback_means_system_fix`, forced 3-loop cap hit), still emit an end event with `result` describing why: `awaiting_user`, `master_defect_surfaced`, `forced_show_after_3_loops`. A start with no end reads as a crashed run to the wrapper.

## Constraints

- Read master FRESH every run. Never reuse prior-session content.
- Never invent experience. If a vacancy keyword has no support in master, it stays in the gap list — don't paper over it with a paraphrased bullet.
- Senior register: every bullet must reference concrete delivery.
- The `## NOTES — not for export` block is binding — never drift bevra.app stack, Kosovo scope, Baker Hughes tenure, etc.
- This command produces markdown only. `/cv-render` turns it into docx.
