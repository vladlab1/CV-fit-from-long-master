---
description: Produce an interview-prep file for a vacancy — TMA opener + candidate questions + theory refresh + per-tech story cards + likely interview questions with anchor bullets. Writes vacancies/<slug>/Research-interview-prep.md.
---

Argument: `$ARGUMENTS` — the vacancy slug (folder name under `vacancies/`), optionally followed by `--round=<stage>` to weight the prep for a specific interview round. Valid stages: `recruiter` / `hiring-manager` / `technical-panel` / `case-round` / `final`. If `--round` is omitted, the command produces a general-purpose prep balanced across stages, with an explicit "Round emphasis" note at the top of the file naming which sections carry Round-1 vs Round-2+ weight.

Slug conventions match `/cv-analyse` / `/cv-draft`.

## Why this command exists

the user's recurring interview failure modes, in his own words:

1. **JD-named methodology in his CV bullet → forgets the theory.** He wrote "JTBD," "propensity," "DiD" into his CV; the interviewer asks a follow-up and he stalls because he hasn't recapped the theory in months. Morning-of top-up needs to be pre-written.
2. **JD-named tech → interviewer asks "what have you used" → he lists names without stories.** He knows the tools are on his CV; he doesn't have a rehearsed 60-second story per tool ready. Story cards need to be pre-written.
3. **Interviewer says "any questions for us?" → he asks political / generic softballs and loses the moment.** He needs 8–12 pre-written questions he can actually ask that reveal he understood the role and probe things he'd want to know if he took the job.
4. **Round-1 opener framing was philosophical, not chronological.** The exact 30-second chronological answer needs to be pre-written.

This command's output must close every one of these gaps. If the resulting file leaves any of the four open, the command failed.

## Resolve the slug

Normalize `$ARGUMENTS` into a slug pointing at a `vacancies/<slug>/` folder that contains `vacancy.md`.

- **Looks like a slug** (e.g. `versuni-2026-07-31-ai-expert`): use as-is. If `vacancies/<slug>/vacancy.md` is missing, stop and tell the user to run `/cv-analyse <slug>` (or `/cv-analyse-draft <slug>`) first — this command is downstream in the pipeline.
- **Empty or unrecognized**: stop and ask the user what input he intended. This command does not resolve file/URL/raw-text inputs — those are handled by `/cv-analyse` and `/cv-draft`.

After resolution, the slug is known and `vacancies/<slug>/vacancy.md` exists.

## What to do

0. **Log pipeline start.** Run:

   ```bash
   python3 bin/cv_log_event.py --slug <slug> --command cv-interview-prep --phase start
   ```

   Appends one line to `vacancies/<slug>/.activity.jsonl`. Silent on success.
1. **Read fresh:**

   - `MASTER_CV.md` — ground truth for what the user has actually delivered. Read the flat Achievements pool per company, not per-framing.
   - `vacancies/<slug>/vacancy.md` — the JD.
   - `vacancies/<slug>/analysis.md` if present — the gap list feeds Section 7 (domain bridges) directly.
   - `vacancies/<slug>/cv.md` if present — the emitted tailored CV. Note: cv.md shows the 3–5 top bullets per company that the drafter picked for THIS vacancy shape; master pool holds 8–15 distinct projects per company. When an interviewer asks *"tell me about a project where…"*, the user reaches into master pool, not into the CV subset. Story cards MUST be enumerated from master pool (per Section 4 / Section 5 scope), not from cv.md. Cv.md is used only for the "verbatim quote" field on cards whose anchor happens to be on the emitted CV — it does NOT gate which cards get produced.
   - `.claude/rules/inputs.md` — input authority order (master wins on facts).
2. **Optional WebSearch** — allowed but not required. Use for:

   - **Section 6** (likely interview questions) — one targeted search on `"<role title> interview questions <industry>"` if you're not confident on shape.
   - **Section 2** (questions to ask them) — one targeted search on `"<company> <team> recent" 2025 2026` to pull one specific "last 6 months" hook per company.

   Do NOT WebSearch for company-culture / benefits / Glassdoor-style intel — the user already has that stream elsewhere. This file is for interview-pass content, not company profile.
3. **Round-shape awareness.** Determine the target interview stage:

   - If `--round=<stage>` was passed, use it verbatim.
   - Otherwise: default to `general` (all-stages-balanced). **Do NOT prompt the user to pick a stage** — validation on the Versuni recruiter transcript (`vacancies/Versuni-2026-07-31-AI-expert/interview1st.md`) showed that even a screening call probes stats-model theory (§3), tech stories (§4), and methodology (§5), so the `general` shape is right-sized across rounds and the ask produces choice-noise without a downstream content change. `--round` remains a CLI opt-in for the rare case where the user genuinely wants a re-ordered file.

   The stage does NOT change which sections are produced — every section still lands in the file. The stage changes emphasis weighting (which sections come FIRST and how much depth per section). Sections 1 (TMA opener) and 2 (Questions to ask) always stay at the top of the file across every stage — those two anchor the user's opening and closing beats and must be immediately findable. The heavy / light re-ordering applies to Sections 3–7 only.

   | Stage                    | Heavy sections (produce full depth, order first among §3–7)                                             | Light sections (produce condensed, order last)                                               |
   | ------------------------ | ------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------- |
   | `recruiter` (fit-screen) | Section 5 methodology stories, Section 6 recruiter-round questions (salary, availability, notice, why-this-role, background walkthrough), Section 6b business-case shape (recruiters name Round-2 case format) | Section 3 theory, Section 4 tech stories, Section 7 gap scripts                              |
   | `hiring-manager`         | Section 5 methodology, Section 4 tech, Section 6 role-specific technical Qs, Section 7 gaps            | Section 3 theory (still present but condensed to top-5-most-likely)                          |
   | `technical-panel`        | Section 3 theory (full depth), Section 4 tech (full depth), Section 7 gaps, Section 6 technical-drill Qs | Section 5 methodology (light — panels tend to drill tech, not methodology), Section 6 fit Qs |
   | `case-round`             | Section 6b (expand into a full case-round playbook: 3–5 case shapes with decision-tree outline per shape), Section 5 methodology stories relevant to the case, Section 3 theory relevant to the case | Section 6 non-case Qs, Section 7 gaps                                                        |
   | `final`                  | Section 6 mutual-fit Qs, Section 5 methodology                                                          | Section 3 theory (skip unless something specific), Section 7 gaps                            |
   | `general` (default)      | All sections at full depth, in canonical order 1–7                                                     | —                                                                                            |

   At the top of the file, emit a **"Round emphasis"** note directly under the header naming the chosen stage and the resulting section order. If `general`, the note names which sections would be prioritized per stage so the user can navigate accordingly. Example:

   ```markdown
   **Round emphasis: recruiter fit-screen.** Sections 1 (TMA opener) and 2 (Questions to ask) pinned to the top as always. Among §3–7: heavy on Section 5 (methodology stories) + Section 6 (fit questions + salary + availability) + Section 6b (case-round shape recruiters preview). Section 3 theory, Section 4 tech deep-drills, and Section 7 gap scripts are light — recruiter rounds don't drill theory. Sections re-ordered accordingly. Original section numbers preserved.
   ```

   **Do not skip sections outright** — every section number 1–7 must appear in the file so downstream re-runs and hand-edits are consistent. "Light" means condensed content, not omitted section.
4. **Produce the file** with the seven sections below, ordered per the round-emphasis table above (Sections 1 and 2 always first). Every section follows the exact micro-format specified. Skip any section that would be padding and say why.

## Output shape — `Research-interview-prep.md`

Header:

```markdown
# Interview prep — <Company> · <Role>

Vacancy: [vacancy.md](vacancy.md) · CV: [cv.md](cv.md) · Analysis: [analysis.md](analysis.md)
Generated: <YYYY-MM-DD>
```

### Readability convention — binding on every card in every section

Cards in every section use `**Label.** value` paragraphs for their subfields (Trigger / Anchor / Direct bridge / Testing for / Mechanism / etc.). **Every labelled subfield must be its own paragraph, separated from the next by a blank line.** Markdown collapses adjacent lines into one paragraph — without the blank line the card renders as a wall of text and the user can't scan it under interview-morning time pressure. This applies uniformly across Section 3 (theory cards), Section 4 (tech story cards), Section 5 (methodology cards), Section 6 (likely questions), Section 6b (case shapes), and Section 7 (domain bridges + scaleup-fit anchor).

Bulleted sub-lists inside a card (e.g. Mechanism bullets, Situation / Action / Outcome bullets, Follow-up traps) also get a blank line above them so the bullet list renders separately from the preceding paragraph.

### Section 1 — Opening 30 seconds (Tell Me About Yourself)

**Always at the top of the file, regardless of `--round`.** This is the anchor the user opens every round with — recruiter, hiring manager, panel, final. Round-1 failure mode was philosophical framing ("I work between product and engineering, AI is shifting the bottleneck…") — the script must be chronological + concrete, not thematic.

Verbatim script for the answer to "walk me through your background." 60–80 words. Structure:

- Chronological anchor (5–10 seconds): "10+ years, currently freelance at Rhodaris, before that <role> at <Company>, before that <role> at <Company>, started as <role> at <Company>."
- One-sentence bridge (5–10 seconds): "Center of gravity now is <X>."
- Invitation (5 seconds): "Happy to go deeper on any of it, where would you like to start?"

Follow the verbatim script with a **Banned openers** block (recurring pattern check, TMA product-transition drift) enumerating the phrases the user has drifted into in prior rounds, and a **Must-name credentials** block (product-credential ghosting pattern) enumerating the credentials the user must voice in-round. Both blocks are Tier 1 morning-of scan surface.

### Section 2 — Questions the user asks them

**Always second in the file, regardless of `--round`.** Placement decision: TMA opens the round, this closes it — these two surfaces bracket every interview and are what the user reaches for cold; keeping them at the top of the file means he doesn't scroll past theory cards to find them the morning of.

8–12 questions the user can actually ask when the interviewer says "any questions for us." Every question must satisfy ALL three criteria:

- Reveals the user understood the specific role — not portable to any job.
- Probes something the user would genuinely want to know if he took the job (backlog shape, decision-making, tooling maturity, team composition, what changed recently).
- Not political ("how do you handle work-life balance"), not flattery ("what makes X great to work at"), not answerable in yes/no.

Group by category with 2–4 questions per group:

```markdown
#### About the role and its backlog

- <question>
- <question>

#### About the team and how decisions get made

- <question>
- <question>

#### About tooling and data maturity

- <question>
- <question>

#### About the last 6 months

- <question>
- <question>
```

The "last 6 months" category produces the highest-signal answers — recent hires, recent org shifts, recent strategy changes. Include at least one question that names something specific (a recent announcement, a recent LinkedIn post from the team, a recent product launch) if WebSearch surfaced any.

After the four groups, emit a **Pre-selected quick-card** block naming 4–5 questions the user plans to voice unprompted (post-it-visible during the call). Recurring pattern check: questions-back pattern has fired at project44, Mondrio, Dyflexis — prep files consistently stage 12+ candidates and <25% land in-round. The quick-card is the live-session intervention.

### Section 3 — Theory refresh cards

Scope: every method, framework, statistical technique, or discovery / experimentation concept mentioned in EITHER the CV or the JD (**union**, not intersection — JD-only ones anchor domain-bridging, CV-only ones anchor recap). One card per concept. Order: most likely to come up first.

Per card:

```markdown
### <Concept>

**One-line definition.** ≤20 words.

**Mechanism.**

- <2–3 bullets: formula / procedure / key steps>

**When to use / when NOT to use.**

- Use when: <one line>
- Avoid when: <one line>

**Classic gotcha.** <the mistake an interviewer probes for>

**My anchor.** <exact verbatim CV bullet that references this>, OR <"JD-only, prep as domain-bridging" if not in CV>
```

### Section 4 — Technology story cards

Scope: every specific technology / tool / library / platform / vendor named in the JD that the user's master pool backs (either explicitly named or as a defensible generalization from a pool bullet). **Enumerate from master pool, not from cv.md.** The tailored CV surfaces only 3–5 top bullets per company for a specific vacancy shape; master pool has 8–15 distinct projects. Interviewers ask *"tell me about a project where you used <X>…"* and the user reaches into master pool, so every JD-relevant tech that master supports gets a card — even if the anchor bullet was not on the emitted cv.md.

**Do NOT invent tech the user doesn't have.** JD-named tech the user has never touched → goes in Section 7, not here.

Per card:

```markdown
### <Technology>

**JD line.** "<verbatim quote from vacancy.md>"

**CV backing.** "<verbatim quote from cv.md bullet, or paraphrase from a master pool bullet if not on the tailored CV — cite which>"

**60-second story.** <written as spoken language, three beats>

- **Situation** — <one sentence: the context>.
- **Action** — <2–3 sentences: the specific technical choice, the WHY-this-tool-not-alternative if defensible>.
- **Outcome** — <one sentence with a quantified number from master>.

**Follow-up traps.**

- <where the interviewer probes next> → <how the user answers>.
- <second probe direction> → <answer>.
```

### Section 5 — Methodology story cards

Same shape as Section 4, but for methodology asks rather than tools — JTBD, causal inference, experimentation design, opportunity sizing, business-case fluency, discovery workflows, etc. Same 60-second-story format. Same anti-invention rule. Same paragraph-per-subfield readability convention.

**Master-pool enumeration is binding here too.** For each JD-named methodology, produce a card for every DISTINCT PROJECT in master pool (across companies) where the user actually applied that methodology — not just the one project the drafter picked for cv.md. Example: if the JD asks about opportunity discovery and master pool has (a) Kosovo JTBD segmentation at Rhodaris, (b) Baker Hughes workflow-automation discovery from user interviews + Salesforce feedback, and (c) Wintershall internal-tooling discovery from stakeholder interviews — produce THREE story cards, not one. the user reaches for whichever project fits the interviewer's setup best; the prep needs all three ready.

### Section 6 — Likely interview questions with anchor bullets

The 12–15 questions most likely to come up given the JD's function, seniority, and industry. Cover the standard opener ("walk me through your background") plus role-specific follow-ups. Per question:

```markdown
### Q: "<the question verbatim, first-person from the interviewer>"

**Testing for.** <one sentence: what signal the interviewer is checking>.

**Anchor.** <exact CV bullet the user leads with — verbatim>.

**Trap to avoid.** <one sentence: the wrong direction the user would instinctively drift toward>.
```

Segment the 12–15 questions by interview round if the JD implies multiple rounds:

- **Recruiter screen** — background walkthrough, why leaving current, salary, availability, notice period, cultural-fit softballs, PLUS two recurring recruiter-round staples that MUST be staged in every prep file's recruiter block:
    - **"Who have been your main stakeholders?"** — cross-vacancy recurrence observed at Dyflexis 2026-08-12 (Laura van Dijk) and JetBrains recruiter round. Distinct from the HM-round "how do you align Sales/Support/Consultancy" — that Q probes conflict-resolution; this Q probes collaboration surface and seniority. Anchor: BH stakeholder taxonomy (clients revenue-weighted, engineering as gatekeeper for anything shipping, designers / SMEs / testers as delivery peers, upper management on quarterly priority setting).
    - **Big-vs-small / scale-fit probe** — recruiters at SME / scaleup companies fire this dressed as a culture question ("in the way of working, do you think there will be a big difference?"). Trigger: vacancy company is <500 employees OR self-identifies as scaleup/startup. Anchor: see Section 7 scaleup-fit script (Roxar).
- **Concept manager / hiring manager technical** — methodology depth, past-project deep-dives, "how would you approach X" thought experiments.
- **Domain / peer / panel** — collaboration, disagreement handling, cross-functional stakeholder management.
- **Business case / take-home** — see Section 6b if relevant.

**Section 6b (conditional).** If the JD or vacancy.md mentions a business case / take-home / whiteboard round, add a mini-section listing the 3 most-likely case-round shapes for THIS role type (opportunity sizing / experimentation design / model architecture / etc.) with a 4-bullet outline of what scores well per shape. If no case round is mentioned, skip 6b and say so ("No case round mentioned in JD — skipping 6b").

### Section 7 — Domain bridges

Any capability / domain the JD names that the user's CV does NOT directly back — but that the user WILL be asked about. Pull from `analysis.md`'s gap list first if it exists; derive from JD-vs-CV diff otherwise. The section's purpose is to give the user **adjacent-project redirects delivered as if they answer the ask** — NOT scripts that voice a gap.

**Binding rule — no deficit-voicing in user-facing scripts.** Any field the user would voice in-round (Anchor / Direct bridge / spoken script / 60-second story) must lead with adjacent-project evidence delivered assertively. **Do NOT write acknowledgment lines the user would say aloud** — no *"I haven't done X"*, no *"my depth is on Y, not X"*, no *"I'd expect to ramp on X"*, no *"I won't pretend to depth I don't have"*. the user's own words (2026-08-23 Nebius pushback): *"I need direct bridging statements. Acknowledging knowledge gap is a decline for me."* Same rule already applies on the JD-pillar walkthrough surface in the JobSearchInterview-template project (`.claude/rules/jd-pillar-walkthrough.md`); this instance extends it to Section 7 here. See [[feedback-direct-bridging-not-gap-acknowledgment]].

Per gap:

```markdown
### <The gap>

**JD line.** "<verbatim quote>"

**Why it's an ask.** <one sentence: what the interviewer expects this capability to prove — drafter-scaffolding, the user won't voice this>.

**Direct bridge.** "<one sentence the user voices when this comes up — leads with the closest adjacent credential (named project, product, program, or transferable discipline), delivered AS IF it answers the ask. No 'I haven't', no 'ramp on', no 'won't pretend'. If the redirect is thin, connect the credential to the ask in one clause instead of expanding to two sentences.>"

**Redirect source.** <exact CV or master pool bullet the Direct bridge draws from — verbatim, so the user can see the credential and voice it in his own words>.
```

Worked example (KVM/QEMU virtualization on a TPM-IaaS vacancy):

- **Right (direct bridge):** *"C# / C++ / .NET engineering underpinned my SDK ownership at Baker Hughes — including the CI/CD estate on Azure DevOps that fed the JewelSuite platform — so I'm comfortable in the conversation adjacent to hypervisor internals, and can pull that thread as fast as the compute team needs."*
- **Wrong (deficit voicing — do NOT emit):** *"My engineering depth is application-layer C# / C++ / Python, not hypervisor internals. I'd expect to ramp on KVM / QEMU fundamentals early so I can hold my end of the compute-team conversations, but I won't pretend to depth I don't have on day 1."*

**Conditional: scaleup-fit anchor.** If `vacancy.md` shows the company is <500 employees OR self-identifies as scaleup / startup (LinkedIn "51–200 employees", "11–50 employees", or JD language like "small team," "founder-adjacent," "no politics," "we move fast"), stage a scaleup-fit script even if `analysis.md` did NOT flag it as a gap. the user's tenure reads as enterprise-heavy (Baker Hughes 14k people, Wintershall enterprise, Shell as client) — recruiters at scaleup companies fire "will you manage at our scale?" probes dressed as culture questions (see Section 6 recruiter-round staples). Default drift under that probe is toward BH / Shell / Wintershall (enterprise anchors), which invites the "will he manage in a 150-person shop?" doubt.

The load-bearing evidence is Roxar — small team + enterprise clients + Solutions Engineer / Customer Success shape, working with real customers before the company grew. Emit as:

```markdown
### Scale-fit — operating in a <NNN>-person company

**Trigger.** <company> is <employee count> per LinkedIn / JD language cue "<verbatim>".

**Recruiter probe shape.** "In the way of working, do you think there will be a big difference?" or equivalent scale-fit-dressed-as-culture question.

**Anchor script.** "Roxar was a scaleup around the time I was there, small team, enterprise clients, Solutions Engineer / Customer Success shape. That delivery discipline, small team, direct customer contact, no bureaucracy between decision and ship, is closer to what <Company> looks like today than either Baker Hughes or Shell."

**Do NOT redirect to.** BH+Shell contrast, Wintershall internal-tooling shipping, or the JewelSuite 14-team program — those are enterprise anchors and invite the exact doubt the probe is testing for. Reserve the BH+Shell contrast for program-scale delivery questions.
```

## Format and anti-patterns for the whole file

- **Blank line between every labelled subfield inside every card.** See the Readability convention above. `**Label.** value` paragraphs collapse into a wall of text without the separator; the file becomes unscannable under interview-morning time pressure.
- **No company culture / benefits / should-take-the-job section.** the user has decided he applies; salary and level are not a concern per user memory. This file is for passing interviews, not for deciding.
- **No coaching platitudes.** No "be confident," "prepare thoughtful questions," "show enthusiasm." Content only.
- **No inventing achievements.** Every story card must trace to a verbatim or paraphrased master bullet. If the JD names something the user doesn't have, it goes in Section 7, not Sections 4 / 5.
- **No deficit-voicing in ANY spoken script.** Applies file-wide, not just Section 7. Anchor fields in Section 6, 60-second-story fields in Sections 4 / 5, Direct-bridge fields in Section 7, and the Section 1 opener are all scripts the user might voice — none may contain *"I haven't"*, *"my depth is on Y not X"*, *"I'd ramp on"*, *"won't pretend to depth I don't have"*, or equivalents. Drafter-scaffolding fields (Testing for / Why it's an ask / Trap to avoid / Follow-up traps) are private prep notes and may freely name gaps for the user's own reading. See [[feedback-direct-bridging-not-gap-acknowledgment]].
    - Question phrasing in Section 6 may naturally include deficit framings ("How do you build engineering credibility on a stack you're new to?") because that's realistic interviewer wording. The Anchor beneath it must still lead with the credential, never with an acknowledgment.
- **Skip padding sections.** If Section 6b has no case round, say so and move on. If Section 7 has no gaps because `analysis.md` was clean, say so. Length is not a virtue.
- **Style-antipatterns still apply.** No em dashes; senior register; concrete delivery numbers; no invented product categories. The prose in the file reads the same way as `cv.md` does.
- **Every anchor is a verbatim quote or a citation.** "My anchor.", "JD line.", "CV backing." fields are quotes, not paraphrases (unless explicitly labelled as such). If a quote can't be found, drop the card and say so.

5. **Write** the output to `vacancies/<slug>/Research-interview-prep.md`. Overwrite if it exists. Immediately after writing, log the artifact:

   ```bash
   python3 bin/cv_log_event.py --slug <slug> --command cv-interview-prep --phase artifact_written --detail '{"path":"Research-interview-prep.md"}'
   ```
6. **Print** a one-line summary in chat: how many concepts / tech / methodology cards / likely-question cards / candidate questions were produced, which round emphasis was applied (or `general` if none passed), and which of the four failure-mode gaps (theory recap / tech stories / candidate questions / opening script) were fully closed vs. partially closed. Do NOT dump the file content — the user opens the file himself.
7. **Log pipeline end.** After printing the summary, run:

   ```bash
   python3 bin/cv_log_event.py --slug <slug> --command cv-interview-prep --phase end --detail '{"result":"success"}'
   ```

   On EARLY EXITS (missing vacancy.md, missing master, WebSearch fallback halted), still emit an end event with `result` describing why: `missing_input`, `awaiting_user`. A start with no end reads as a crashed run.

## Constraints

- Read master FRESH every run. Never reuse prior-session content.
- Read cv.md if present; anchor story cards on the tailored CV's bullets before falling back to unused master pool bullets. The tailored CV is what the user committed to on paper for THIS interview — his stories must match.
- Do NOT edit MASTER_CV.md, cv.md, analysis.md, or vacancy.md from this command. Read-only on all inputs.
- Do NOT open the produced file (no `open`, no `xdg-open`). the user opens it manually. Report the path in chat and stop.
- Idempotent: re-running the command overwrites the prior `Research-interview-prep.md`. the user's hand-edits to the file will be lost on re-run — expected.
