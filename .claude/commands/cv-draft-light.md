---
description: Delta-patch a reuse-target cv.md into a tailored cv.md for the current vacancy. Runs draft-critic-light (delta-scoped, ~5 checks vs draft-critic's 10+) and produces .critic-log.json (same shape as /cv-draft's gate). Reuse path when /cv-analyse surfaced strong candidates — cheaper than /cv-draft's full-drafter + full-critic run.
---

Argument: `$ARGUMENTS` — normally the vacancy slug. Optionally followed by `--from <reuse-slug>` to override the reuse target.

## When to use this instead of /cv-draft

- `/cv-analyse` has run and `vacancies/<slug>/analysis.md` contains a non-empty `## Reuse candidates` section.
- The top candidate's function-axis + domain-axis are close enough that a delta patch will cost less than a full drafter run.
- If NO reuse candidate exists (empty section) OR the top candidate's domain axis diverges materially from the current vacancy's, fall back to `/cv-draft`. This command STOPS when it cannot resolve a reuse target.

Do NOT use this command to bypass the critic. It runs the critic exactly as `/cv-draft` does — same gate, same `.critic-log.json` shape, same 3-loop cap.

## Preflight — required inputs

- `vacancies/<slug>/vacancy.md` must exist.
- `vacancies/<slug>/analysis.md` must exist AND contain a `## Reuse candidates` section with at least one row.
- If either is missing, STOP. Tell the user to run `/cv-analyse <slug>` first, then this command.

## What to do

0. **Log pipeline start.** Run:

   ```bash
   python3 bin/cv_log_event.py --slug <slug> --command cv-draft-light --phase start
   ```

   Silent on success. Same activity-log convention as `/cv-draft`.

**MANDATORY: Step 6 (critique gate) MUST run on every invocation.** Same discipline as `/cv-draft`. `/cv-render` refuses to run without `.critic-log.json`; skipping the gate breaks the pipeline by design.

1. **Read fresh:**
   - `vacancies/<slug>/vacancy.md`.
   - `vacancies/<slug>/analysis.md`. Both the `## Reuse candidates` section (used in Step 2) AND the `## Company product context`, `## ATS matrix`, `## Inconsistencies to fix on the tailored CV`, and `## GAP LIST` sections (they anchor the delta in Step 4).
   - `MASTER_CV.md` — ground truth. The `## NOTES — not for export` block is binding. Needed for two things: (a) verifying any bullet the delta adds is truly in master, (b) reaching into the Achievements pool when analysis.md flags a load-bearing dimension the reuse target didn't cover.
   - `.claude/rules/inputs.md`, `variant-and-bullet-selection.md`, `cv-markdown-format.md`, `style-antipatterns.md`, `delivery.md`.

2. **Resolve the reuse target.**

   - If `$ARGUMENTS` contains `--from <reuse-slug>`, use that slug. Verify `vacancies/<reuse-slug>/cv.md` exists (top-level OR under `vacancies/archive/`). If it does not, STOP — tell the user the override target has no cv.md and offer to fall back to the top-ranked candidate.
   - Otherwise, parse the `## Reuse candidates` section in `analysis.md`. Each row is:
     ```
     - `vacancies/<candidate-path>/` — <company>, <position>, <YYYY-MM-DD>. Overlap: `{token1, token2}`. `cv.md` present.
     ```
     Take the FIRST row (top-ranked per the scan's overlap-size × mtime sort in `/cv-analyse`).
   - If the section is empty (no rows below the section header) OR entirely absent, STOP. Tell the user the reuse path does not apply and to run `/cv-draft <slug>` for the full-drafter path. Log an end event with `result:"no_reuse_target"`.
   - Print one line to chat: `reuse target: vacancies/<candidate-path>/cv.md`.

3. **Read the reuse target's `cv.md`** end-to-end. Also read `vacancies/<candidate-path>/vacancy.md` and `analysis.md` if present — the reuse target's vacancy anchors what the reuse cv.md was tuned for, and the delta pivots on the difference between THAT and the current vacancy.

4. **Delta-patch the CV.** Start from the reuse target's `cv.md` as the base. Apply changes in this order:

   1. **SUMMARY headline.** Paraphrase to the current vacancy's generic function (one level up from the JD title's scope specifier per `style-antipatterns.md § "SUMMARY headline must not letter-mirror the JD title"`). Do not adopt the reuse target's headline verbatim if the current vacancy names a different function label.
   2. **SUMMARY closing anchor.** Verify against the recognized-anchor rule (`style-antipatterns.md § "SUMMARY closing clause must carry a recognized anchor, audience-relative"`). If the reuse target's anchor is off-axis for the current vacancy (e.g. reuse cited a domain-recognized employer that the current audience will not recognize; reuse's headline credential is not on-axis for the current vacancy), swap to a self-contained-proof anchor drawn from master that matches the current vacancy's axis of primary alignment (per analysis.md `## Company product context`).
   3. **Contact line.** Adjust product / project links (`bevra.app`, GitHub) per `cv-markdown-format.md` — keep on PM / SaaS / AI-builder / hybrid technical-PM; drop on pure DS / Applied Scientist. Preserve LinkedIn + email + phone unconditionally.
   4. **Company taglines.** Per `variant-and-bullet-selection.md`, the tagline is vacancy-tunable. If the current vacancy's domain axis differs from the reuse target's, swap the tagline to a master preset closer to the current domain — or write one inline within accuracy bounds. Common swaps: contract/consulting-flavored tagline for contract roles; industrial-operations tagline for manufacturing / industrial vacancies; energy tagline for oil & gas.
   5. **Framing per company.** Usually inherited from the reuse target — the whole point of the reuse path is that the function axis matches. Adjust ONLY if analysis.md flags a framing mismatch (e.g. reuse target chose PO framing at BH but current vacancy is DS-first and analysis.md points at the `[ds]` framing).
   6. **Bullets per role slot.** For each role, run the delta:
      - **Keep** bullets that serve both the reuse target's vacancy AND the current vacancy (most bullets typically survive).
      - **Swap in** bullets from master's Achievements pool when analysis.md's ATS matrix flags a vacancy requirement the reuse target's bullet did not cover.
      - **Cut** bullets that were load-bearing for the reuse target's vacancy but not for the current one (e.g. reuse target emphasized a domain the current vacancy doesn't need).
      - **Reorder** per the "vacancy-load-bearing bullets go FIRST" rule from `variant-and-bullet-selection.md § Bullet selection`. The order in the reuse target's cv.md was tuned for THAT vacancy; the current vacancy may want a different ordering.
      - Apply the single-artifact saturation guard, sparse-slot narrative anchor, reader-visible vacancy link test, bullet-body scrubbing, and domain-axis guard to every kept bullet — every check that binds in `/cv-draft` binds here too.
   7. **Skills.** Reorder items within each category so the vacancy's load-bearing capabilities lead. Trim to the 12-hard / 8-target cap per category. Add / drop categories per the current vacancy's ATS matrix (single-vacancy-driven gate from `variant-and-bullet-selection.md § Skills selection`). Do not import categories or items from the reuse target that don't pass the current vacancy's gate.
   8. **Education & Certifications.** Usually unchanged. Only touch if the current vacancy's shape shifts the sub-bullet selection under Gubkin MSc (hardware carve-out for hardware / robotics / IoT PM; AI thesis for AI PM; etc.) OR the PMP / PSPO II / Stanford PM certificate gating changes (management-signal titles keep them; pure IC technical titles drop them per the seniority/scope axis rule).

   **Universal rules apply on every emitted line** — strip master annotations (function tags, keyword parentheticals), no em dashes, senior register, every product-name-in-body markdown-linked when master carries a link registry entry for that term, no invented experience, no drift on the `## NOTES — not for export` guards.

5. **Write** to `vacancies/<slug>/cv.md`. Overwrite if it exists (the user's hand-patch to a `cv.md` from another path is intentionally discarded here — the reuse+delta+critic pass produces the authoritative version). Immediately after writing, log an artifact event AND snapshot the file for the resume classifier used by Step 6's rewrite loop:

   ```bash
   python3 bin/cv_log_event.py --slug <slug> --command cv-draft-light --phase artifact_written --detail '{"path":"cv.md","state":"initial"}'
   cp "vacancies/<slug>/cv.md" "vacancies/<slug>/.cv.md.after-loop-0"
   ```

6. **Critique gate — MANDATORY on every run.** Same discipline as `/cv-draft § Step 7`. Do not paraphrase the gate mechanics here — the shape is:

   - Before every critic invocation:
     ```bash
     python3 bin/cv_log_event.py --slug <slug> --command cv-draft-light --phase critic_invoked --detail '{"loop":<N>}'
     ```
   - Invoke the `draft-critic-light` subagent via the Agent tool (`subagent_type: draft-critic-light`) with a delta-scoped input:

     ```
     Inputs:
     - draft: vacancies/<slug>/cv.md
     - reuse_base: vacancies/<reuse-slug>/cv.md   # from Step 2 — REQUIRED
     - vacancy: vacancies/<slug>/vacancy.md
     - analysis: vacancies/<slug>/analysis.md   # if present
     - rule paths: .claude/rules/style-antipatterns.md

     Return structured Findings + Decision per your output format. Scope is the diff between reuse_base and draft — do NOT re-do the full draft-critic pass.
     ```

     Note: `draft-critic-light` intentionally does NOT read `MASTER_CV.md`, `variant-and-bullet-selection.md`, or `cv-markdown-format.md` — those were applied when the reuse target was originally drafted, and their verdict carries. If a delta change requires one of those rules, the light critic escalates as a `flag-to-user`. If the finding pattern shows persistent light-critic gaps (e.g. delta-added bullets bypassing the domain-axis guard), that's a rule-file/subagent iteration signal, not an ad-hoc file load.
   - After critic returns, log the terminal event for the loop AND persist the findings to `vacancies/<slug>/.critic-findings-loop-<N>.json`:
     ```bash
     python3 bin/cv_log_event.py --slug <slug> --command cv-draft-light --phase critic_returned --detail '{"loop":<N>,"decision":"<CLEAN|SHOW-WITH-FLAGS|REWRITE>","must_fix":<count>,"should_fix":<count>,"flag_to_user":<count>,"findings_path":".critic-findings-loop-<N>.json"}'
     ```
   - Act on the decision. Every branch below is TERMINAL — every branch MUST write `vacancies/<slug>/.critic-log.json` before exiting Step 6.
     - **REWRITE** — apply every must-fix AND every should-fix. Snapshot the new state as `.cv.md.after-loop-<M>` where `<M>` is the rewrite's own loop number. Re-invoke critic. Cap at 3 rewrite loops; on cap-hit, set terminal state to `FORCED-SHOW-AFTER-3-LOOPS`, surface unresolved must-fixes to the user as flags, then write `.critic-log.json` and proceed to Step 7.
     - **SHOW-WITH-FLAGS** — apply every should-fix (single recommended action per finding, no menus). Surface every `flag-to-user` finding to the user verbatim with the trade-off and the critic's single recommended action. Write `.critic-log.json` with `decision: "SHOW-WITH-FLAGS"` and `rewrite_loops` set to the number of REWRITE rounds executed before this terminal state. Proceed to Step 7.
     - **CLEAN** — write `.critic-log.json` with `decision: "CLEAN"` and counts all zero. Proceed to Step 7.

   Breadcrumb shape (identical to `/cv-draft`):

   ```json
   {
     "cv_md_path": "vacancies/<slug>/cv.md",
     "decision": "CLEAN | SHOW-WITH-FLAGS | FORCED-SHOW-AFTER-3-LOOPS",
     "rewrite_loops": <integer, 0 if CLEAN on first pass>,
     "must_fix_count_final": <integer>,
     "should_fix_count_final": <integer>,
     "flag_to_user_count_final": <integer>,
     "critic_agent": "draft-critic-light",
     "checked_at": "<YYYY-MM-DDTHH:MM:SS>"
   }
   ```

   Do NOT stub a fake log to bypass the gate — same rule as `/cv-draft`. Truthful post-hoc writes are NOT stubs; stubs are fabricated values written to bypass a critic that never ran.

7. **Print** a one-line summary in chat: reuse target used, delta scope (SUMMARY-only / SUMMARY + N bullets / SUMMARY + N bullets + skills + tagline / …), `analysis.md` gaps left unaddressed (because the pool has nothing credible to back them), and the critic decision (CLEAN / SHOW-WITH-FLAGS-after-N-loops / forced-show-after-3-loops).

8. **Log pipeline end.**

   ```bash
   python3 bin/cv_log_event.py --slug <slug> --command cv-draft-light --phase end --detail '{"result":"success","decision":"<terminal decision>","rewrite_loops":<N>}'
   ```

   Early-exit results: `no_reuse_target`, `missing_input`, `master_defect_surfaced`, `forced_show_after_3_loops`. A start with no end reads as a crashed run.

## Constraints

- The reuse target is a starting POINT, not the ceiling. Do not preserve reuse-target choices that violate the current vacancy's rules — the delta is unbounded when the current vacancy demands it.
- Every rule that binds `/cv-draft` binds here: no em dashes, senior register, no invented experience, NOTES guards, function tag + keyword parenthetical strip on emit, style-antipatterns applied to every emitted line.
- The critic gate is the design contract, not a suggestion. Skipping it defeats the whole point of this command being safe to use in place of `/cv-draft`.
- This command produces markdown only. `/cv-render` turns it into docx.
