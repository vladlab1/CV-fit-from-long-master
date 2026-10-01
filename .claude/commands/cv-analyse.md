---
description: Analyse a vacancy against MASTER_CV — ATS matrix, industry fit, brutal gap list. Writes vacancies/<slug>/analysis.md.
---

Argument: `$ARGUMENTS` — normally the vacancy slug (folder name under `vacancies/`). Other input shapes are accepted; see below.

## Resolve the slug

Before doing the analysis, normalize `$ARGUMENTS` into a slug pointing at a `vacancies/<slug>/` folder that contains `vacancy.md`.

- **Looks like a slug** (e.g. `cognite-2026-06-08-data-scientist-manager`): use as-is. If `vacancies/<slug>/` doesn't exist, create it. If `vacancy.md` is missing inside it, stop and ask the user to drop the vacancy text in.
- **Path to a file** (`.pdf`, `.docx`, `.txt`, `.md`): extract the vacancy text from the file. Derive a slug as `<company>-<YYYY-MM-DD>-<position>` (today's date, company and position from the vacancy contents — lowercase, kebab-case, no special chars). Create `vacancies/<slug>/`. Save the extracted text as `vacancies/<slug>/vacancy.md`. Then proceed.
- **URL**: fetch the page, extract the vacancy text, then same as above.
- **Raw vacancy text** (a long string, not a path or URL): treat the argument itself as the vacancy text. Derive slug. Create folder. Save as `vacancy.md`. Then proceed.
- **Empty or unrecognized**: stop and ask the user what input he intended.

After this step, the slug is known and `vacancies/<slug>/vacancy.md` exists. Use that slug for the rest of the command.

## Duplicate-application check

the user applies fast and needs a guard against re-applying to the same posting. Run this check BEFORE any analysis work — it is a hard-stop, not a soft-warn.

1. **Extract company and position tokens** from the resolved slug. Slug shape is `<company>-<YYYY-MM-DD>-<position>`; split on the first `-\d{4}-\d{2}-\d{2}-` boundary — the substrings before and after are the company and position tokens respectively. Lowercase both; keep hyphens as token separators.
2. **Glob candidate slugs** from `vacancies/*/` (top-level subfolders). Also scan `vacancies/archive/*/` and `arcvhive/*/` (typo variant present in this repo) if either exists. Exclude the just-resolved slug itself.
3. **Canonicalize each position string into a comparable token set:**
   - Split on `-`, lowercase.
   - **Drop seniority stopwords**: `senior`, `sr`, `staff`, `principal`, `lead`, `expert`, `junior`, `jr`, `associate`.
   - **Expand known abbreviations** to their long-form token set — each expanded token then counts as a normal token from that point on. Table (extend when a new pattern surfaces):
     - `pm` → `{product, manager}`
     - `po` → `{product, owner}`
     - `pe` → `{product, engineer}`
     - `ds` → `{data, scientist}`
     - `dsm` → `{data, scientist, manager}`
     - `de` → `{data, engineer}`
     - `ml` → `{machine, learning}`
     - `mle` → `{machine, learning, engineer}`
     - `swe` → `{software, engineer}`
     - `sre` → `{reliability, engineer}`
     - `tpm` → `{technical, product, manager}`
     - `tam` → `{technical, account, manager}`
     - `eng` → `{engineer}`
     - `mgr` → `{manager}`
     - `mngr` → `{manager}`
     - `sln` → `{solutions}`
     - `prod` → `{product}`
   - **Keep any remaining token ≥ 4 chars**; drop shorter unknown tokens (`ai`, `it`, `js`, etc. — too ambiguous alone, but the abbrev table above catches meaningful short ones).
4. **Match a candidate as a probable duplicate** when BOTH hold:
   - **Company token equality** — candidate company token equals the current company token after normalization (lowercase; strip surrounding whitespace; treat `-` and `_` as equivalent separators).
   - **Position token-set intersection is non-empty** on the canonicalized token sets from Step 3. Worked cases: `senior-product-owner` matches `product-owner` (overlap `{product, owner}`); `product-owner` does NOT match `data-scientist` (empty overlap); `pm` matches `product-manager` (overlap `{product, manager}` after expanding `pm`); `ai-pm` matches `ai-product-manager` (overlap `{product, manager}`; `ai` is dropped both sides); `pe` matches `product-engineer` (overlap `{product, engineer}`); `pm` matches `po` (overlap `{product}` — narrowly matches; presented for the user to confirm since Product Manager and Product Owner are often the same posting re-classified).
5. **On any match**: STOP. First, print a context block to chat so the user can see what matched:

   ```
   ⚠️  DUPLICATE-APPLICATION CHECK

   Prior applications at <company> that may be the SAME posting:

   - vacancies/<matching-slug>/  — <first non-empty line of that vacancy.md, truncated to ~100 chars>
   - vacancies/archive/<matching-slug>/  — <first non-empty line…>   (if in archive)
   ```

   Then invoke the `AskUserQuestion` tool with a single question:
   - `question`: `"Duplicate application to <company>? Prior match(es): <slug-list>. Continue with the new analysis?"`
   - `header`: `"Duplicate"`
   - `options`:
     - label `"Stop — same posting"` · description `"Abort. Don't overwrite existing analysis; don't touch master."` (RECOMMEND as the first option — this is the safer default)
     - label `"Proceed — different posting"` · description `"Continue with /cv-analyse. the user has verified the prior application is a different role or a legitimate re-apply."`

   On `"Stop — same posting"` (or any user "Other" answer indicating same/duplicate/abort) → stop; do not overwrite the existing analysis and do not touch master. On `"Proceed — different posting"` → continue with the analysis.
6. **On no match**: continue silently to the "Reuse-candidate scan" section — do not print a "no duplicates found" line, it's noise.

## Reuse-candidate scan

After the duplicate-application check clears, re-use the same glob + tokenization pass to identify DIFFERENT-COMPANY vacancies whose position-token set overlaps this one. These are potential `cv.md` clone targets — the user may prefer hand-patching a close prior draft over running the drafter from scratch.

This scan is informational only. It does NOT gate the analysis run; it feeds the `## Reuse candidates` section that Step 3 of "What to do" emits at the top of `analysis.md`.

1. **Re-scan candidate slugs** — same glob as the duplicate check (`vacancies/*/` + `vacancies/archive/*/` + `arcvhive/*/` if present). Exclude the just-resolved slug.
2. **Filter to reuse candidates**, keeping only those where ALL hold:
   - **DIFFERENT** company token (same-company matches were already handled by the duplicate check).
   - **Non-empty** position token-set intersection (canonicalization from the duplicate check's Step 3 applies — same seniority-stopword drop, same abbrev expansion, same ≥4-char threshold).
   - **Candidate folder contains `cv.md`** at its root (`vacancies/<candidate-slug>/cv.md`). Folders with only `analysis.md` are excluded — nothing to clone.
3. **Sort** by overlap-set size descending. Break ties by folder mtime descending (newest wins).
4. **Cap** the surfaced list at 5.
5. **Store** the result for Step 3 of "What to do".

Empty result is silent — the `## Reuse candidates` section is OMITTED from `analysis.md` entirely (not emitted with a "no candidates" line). Do not print anything to chat about the scan either way — the analysis.md section is the only surface.

## What to do

0. **Log pipeline start.** Run:

   ```bash
   python3 bin/cv_log_event.py --slug <slug> --command cv-analyse --phase start
   ```

   Appends one line to `vacancies/<slug>/.activity.jsonl`. Silent on success; do not report to the user. This is the per-JD activity trace read by `/cv-analyse-draft` and useful for post-hoc debugging when a run partially fails.

1. **Read fresh:**
   - `MASTER_CV.md` (the `## NOTES — not for export` block at the bottom is binding). Each company is a Role framings catalog + a flat Achievements pool — read the pool flat, not per-framing, when matching against vacancy requirements.
   - `vacancies/<slug>/vacancy.md` (slug from the resolution step above).
   - `.claude/rules/inputs.md` — input authority order.
   - `.claude/rules/ats-analysis.md` — Deliverable A behavior (matrix, inconsistencies, gap list, senior register).

2. **Establish company product context.** Vacancy nice-to-have lists are noisy — a JD may list "AI, computer vision, LLM, IoT, edge computing" while the company's actual product uses only a narrow subset. Without a company anchor, downstream drafting has no way to rank adjacent capabilities against each other and defaults to whichever bullet carries the sharpest numbers (often off-axis). This step establishes the anchor.

   Source order — first source that fires wins:

   - **Local research file** (preferred). Look for any sibling file in `vacancies/<slug>/` whose name matches (case-insensitive) `*research*` / `*company*` / `*due-diligence*` / `*context*` in `.md` / `.txt`. If found, read it end-to-end. This is the user's own research and outranks a web search.
   - **WebSearch** (fallback). One or two targeted queries on the company name — e.g. `"<company> product what they build"` and `"<company> technical stack"`. Read the top 2–3 hits (company site, Crunchbase, press coverage, StartupTicker / EU-Startups for EU seed-stage). Cap at ~5 fetches — this is a domain anchor, not a due-diligence report.
   - **Ask the user** (last resort). If WebSearch is unavailable (non-interactive session, offline, tool disabled) and no research file exists, stop and ask the user for a one-paragraph company context OR to drop a research file into the slug folder.

   Produce a one-paragraph section capturing:

   - **Core product** — what does the company actually build, in concrete nouns? Not marketing ("AI-powered solutions") — concrete outputs (waste-bunker hazard-detection + calorific-value dashboards, sovereign LLM platform for regulated docs, delivery-slot optimization SaaS).
   - **Technical stack the product is built on** — computer vision / LLM+RAG / classical ML / dashboards / hardware / edge / IoT / autonomous control / geospatial / etc. Name the STACK, not a generic label. This is the axis of primary alignment for the drafter.
   - **Named customers or market segment** — pins the domain (waste operators, mid-market NL retailers, enterprise banks) so bullet-selection can gate on it.

   Keep it to a single paragraph. This section is a domain anchor for the drafter, not a full company profile — the interview-prep write-up (if any) is separate and stays in its own file.

3. **Produce the analysis** exactly per `ats-analysis.md`. Sections in order (Reuse candidates comes FIRST — reader-facing meta-section, omitted when empty; Company product context comes SECOND — it anchors every downstream section):
   - **Reuse candidates** (from the reuse-candidate scan above). OMIT this section entirely when the scan produced no candidates. When candidates exist, emit one line per candidate:

     ```
     - `vacancies/<slug>/` — <company>, <position>, <YYYY-MM-DD>. Overlap: `{token1, token2}`. `cv.md` present.
     ```

     End the section with a one-line reader hint: `Consider hand-patching the highest-overlap candidate before running /cv-draft.` This is the only surface where the reuse scan reports out.
   - **Company product context** (from step 2 — one paragraph).
   - Required skills (extracted from the vacancy).
   - Side-by-side matrix — vacancy requirement → CV evidence → ✅ / ⚠️ / ❌.
   - Industry inference and fit.
   - Inconsistencies to fix — CV emphasis mismatched to the vacancy, role-name divergence, generic headline that needs a vacancy-specific edit, non-relevant functional expertise.
   - **GAP LIST** at the end — vacancy requirements with no matching bullet in master. Be specific. Do NOT invent experience.

4. **Write the output** to `vacancies/<slug>/analysis.md`. Overwrite if it exists. After the write, log the milestone:

   ```bash
   python3 bin/cv_log_event.py --slug <slug> --command cv-analyse --phase artifact_written --detail '{"path":"analysis.md"}'
   ```

5. **Print** a 1–2 sentence summary in chat: top fit signal, biggest gap, and which gaps (if any) the user should consider backfilling into master before `/cv-draft`. Do NOT edit master yourself — that's the user's call. If step 2 fell back to WebSearch, name the sources; if it stopped for a manual fill, say so.

6. **Log pipeline end.** After printing the summary, run:

   ```bash
   python3 bin/cv_log_event.py --slug <slug> --command cv-analyse --phase end --detail '{"result":"success"}'
   ```

   On EARLY EXITS (duplicate-check hit, missing vacancy.md, WebSearch fallback halted for manual fill), still emit an end event with a `result` describing why: `duplicate_confirmed`, `missing_input`, `awaiting_user`. The activity log should always terminate — a start with no end reads as a crashed run to the pipeline wrapper.

## Constraints

- Apply universal rules from `.claude/rules/project.md` (already auto-loaded via `CLAUDE.md`) and the specific rules above. Don't duplicate them in chat.
- Brutal, direct, no empathy. Senior screening register.
- After slug resolution, tell the user the slug you used (especially if you derived it from a file/URL/text) — he may want to rename the folder.
- Don't produce a tailored CV in this step — `/cv-draft` does that.
