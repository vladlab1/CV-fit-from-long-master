# Framing and bullet selection — Deliverable B

> **Note on examples**: Worked examples in this file reference the author's original use case (consulting, oil & gas, mapping, satellite imagery). Read them as *patterns* and substitute your own companies, products, and vacancies. The rules themselves are domain-agnostic.

How to pick role framings and bullets from `MASTER_CV.md` when producing a tailored CV.

The master CV stores each company as two parts:

1. **Role framings catalog** — one or more framings the company's tenure can be presented as. Each framing is a tagged label, e.g. `[pm]` Product Manager · Oct 2019 – Dec 2024 (single role), or `[ds]` Data Scientist · Oct 2019 – Jun 2023 **+** Product Manager · Jul 2023 – Dec 2024 (two sub-roles spanning the same tenure). Untagged framings exist for companies with only one realistic shape.
2. **Achievements pool** — a flat list of bullets that happened at the company. Every pool bullet carries two annotations:
   - **Function tag** `[pm]` / `[ai]` / `[ds]` / `[eng]` / `[geo]` / `[fde]` — author note recording the kind of work the bullet describes. Useful as a soft hint for slot placement under a multi-role framing. **Do NOT use as a retrieval filter.**
   - **Keyword parenthetical** *(…)* at end — primary retrieval signal.

Drafting tailors the company onto a CV in two independent steps.

## Step 1 — Framing selection

Per company, pick ONE framing from the catalog based on the vacancy's primary function:

- PM vacancy (any flavor — Senior PM, AI PM, Group PM, Product Lead) → `[pm]` framing
- Data Science / ML Scientist vacancy → `[ds]` framing
- Engineering / hybrid technical-PM / Solutions vacancy → `[pm-eng]` framing
- Geology / geoscience vacancy → `[geo]` framing
- New tags can be added to the master as patterns emerge.

**Paraphrase the role title to vacancy language if factually accurate.** E.g. master's `[ds]` Data Scientist may be rendered as "Senior Data Scientist" if the vacancy targets that level and seniority is defensible. NOTES section is binding — must reconcile to LinkedIn's public profile.

**Paraphrase to the vacancy's GENERIC FUNCTION, not the JD TITLE verbatim.** A JD title typically bundles two things: (a) a generic function label ("Data and AI Specialist", "Product Manager", "Machine Learning Engineer") and (b) a scope specifier the JD adds to describe THIS posting ("Reporting", "Marketing", "Platform", "Growth"). The CV role label carries the generic function only. Bullets under the role carry the scope. Mirroring the JD title verbatim reads as ATS keyword-stuffing and produces a title engineered for one posting rather than a genuine tenure label — both cost credibility on a senior screen.

**Test:** strip the JD title of its scope words. What remains is the generic function label to emit. If the strip yields nothing sensible, the JD title is already generic — use as-is.

Worked example (Destinus 2026-08-05, JD title "Data Reporting & AI Specialist"):
- **Wrong**: `Data Reporting & AI Lead` — mirrored the JD's scope word "Reporting" verbatim AND unilaterally uplifted seniority "Specialist" → "Lead".
- **Right**: `Data and AI Specialist` — dropped the scope specifier "Reporting" (bullets prove the reporting focus); kept the JD's seniority level "Specialist".

Companion to the existing seniority-uplift rule (paraphrase seniority only when defensible): the combined discipline is *don't mirror JD scope, don't uplift JD seniority unilaterally*. Both distortions push the emitted role label away from a defensible tenure title toward a JD-optimized copy — a pattern senior screens flag.

Honor inline `[instruction]` lines in master (e.g. "ONE framing per company per CV", "include this entry only for `[geo]` CVs", "`[geo]` is mutually exclusive with `[ds]`/`[pm]` at this company").

### Tenure coverage — framing choice must cover the company's full tenure

Before finalizing a framing per company, verify the framing spans the company's LinkedIn-verified tenure (per master's `## NOTES — not for export`). A framing that covers only a sub-period creates a chronology gap on the printed CV — the recruiter sees the truncated dates for a company where LinkedIn shows a longer run, reads it as career-hiding or padding elsewhere, and discounts the whole tenure. This gate operates BEFORE bullet selection: the wrong framing at Step 1 cannot be fixed by clever bullet choice at Step 2.

Some single-role framings in master's catalog are targeted at specific vacancy shapes and cover only a sub-period. Wintershall's `[pm]` Product Owner (Operations) · Nov 2018 – Sep 2019 is such a framing — master's `[instruction]` line marks it as "surfaces the drilling/well operations framing of the late-Wintershall tenure for operations-PM vacancies". It is NOT a general-purpose Wintershall framing. Pool bullets outside Nov 2018 – Sep 2019 have no role slot on it, and the 6+ years before Nov 2018 disappear from the CV.

**Priority order for framing choice:**

1. **Prefer a merged-role framing that covers the full tenure** if master offers one. Baker Hughes' `[pm]` Product Manager · Oct 2019 – Dec 2024 (single merged role) is the canonical example — one role header, full-tenure dates, all pool bullets fit.
2. **Otherwise pick a multi-role framing that covers the full tenure**, and apply the "Empty role slot fallback" (Step 3) to any off-axis sub-role — one tight domain-neutral bullet is a lower cost than a chronology gap.
3. **Only pick a narrow single-role framing** when master's `[instruction]` line explicitly targets it at the current vacancy shape (e.g. operations-PM framing on an operations-PM vacancy). A narrow framing on the wrong vacancy shape is worse than a full-tenure framing with one off-axis sub-role, because it hides tenure.
4. **Never accept a chronology gap silently.** If master lacks both a merged full-tenure framing AND a multi-role full-tenure framing that fits the vacancy shape, escalate to the user — the fix is a master-catalog gap that requires LinkedIn reconciliation, not a drafter judgment call.

Worked example (Wintershall on a non-operations PO / integrations vacancy): master currently offers no merged `[pm]` full-tenure framing for Wintershall (open master-catalog gap, per iteration #9 follow-up). Available options are multi-role: `[ds]` Product Manager + Data Scientist (default), `[ds]` PM + Business Analyst (BA/ERP-leaning paraphrase), `[pm]` Project Manager + Data Analyst, `[ds]` Project Manager + Project Engineer — plus the narrow single-role `[pm]` Product Owner (Operations). On an integrations PO vacancy the correct pick is `[ds]` PM + Business Analyst (BA sub-role maps onto "translate customer business processes into technical specifications") — paraphrase the late sub-role to "Product Owner" for ATS title match, keep "Business Analyst" for the early sub-role, fill the early slot per the Empty role slot fallback if bullets are thin. Do NOT default to `[pm]` Product Owner (Operations) — it hides 6+ years of Wintershall on a vacancy shape the narrow framing was not designed for.

## Step 2 — Bullet selection from the pool

**Bullet selection is INDEPENDENT of which framing was picked.** Scan the entire company's Achievements pool — every bullet is fair game regardless of the function tag prefix.

Match by:

- **Keyword parenthetical** *(…)* — primary signal. Match against vacancy keywords.
- **Bullet text** — secondary signal. Match against vacancy language and required skills.

Ignore the function tag prefix when picking — it's an author note recording the bullet's original role context, not a filter. A `[pm]`-tagged bullet may be the highest-fit signal for a DS vacancy if its content is. A `[geo]`-tagged mentoring bullet may belong on a PM CV if mentoring is what the vacancy is screening for.

Order selected bullets by relevance to the vacancy, NOT by chronology within a role. Prefer concrete numbers, named products, or measurable outcomes. When in doubt, leave a bullet OUT — a tight CV with high-fit bullets beats a long CV padded with adjacent ones.

**Vacancy-load-bearing bullets go FIRST.** Within each role's bullet list, rank by vacancy fit — strongest signal at the top, weakest at the bottom. Recruiters skim top-down; a relevant bullet at position 5 is invisible. "Vacancy fit" is judged by which signals are SCARCE in the CV vs. the vacancy's load-bearing requirements:

- A unique domain bridge (e.g. the ONLY sustainability bullet on an ESG vacancy, the ONLY GenAI bullet on an AI PM vacancy) ranks above a strong-but-replaceable generic builder bullet — even when the generic bullet is technically more impressive — because the domain bridge is the one signal the recruiter is actively hunting for.
- A bullet that names a vacancy keyword verbatim (e.g. `Claude Code`, `n8n`, `RAG`, `CSRD`) ranks above a paraphrased one with the same content.
- If `analysis.md` flags a load-bearing domain gap and the master has ONE or TWO adjacent bullets, those bullets must appear in the FIRST 2 positions of the relevant role's bullet list — moving them lower hides the only signal the audience cares about.

The same logic applies to the SUMMARY's proof clause: when the analysis flags a load-bearing domain gap, the proof sentence leads with the domain-bridge bullet's content (sustainability ML, compliance-grade LLM, etc.), not with the universal "ships SaaS" credential. The universal credential anchors the headline; the domain bridge anchors the screen.

The same logic applies to the company tagline: when the vacancy's primary domain is rare in master, tailor the tagline to surface what IS there (e.g. Rhodaris on an ESG SaaS vacancy — surface "sustainability ML" + "compliance-grade LLM pipelines" within accuracy bounds — rather than the generic "AI-first product engineering for clients" preset).

### Reader-visible vacancy link — binding on every retained bullet

A bullet earns its slot only if a first-read recruiter can point to the vacancy line it serves within about three seconds. Not "the drafter can defend the connection" — "the reader sees it immediately."

**The test is reader-first, not drafter-defensibility.** A bullet may pass every other check on this page (domain-axis on-axis, voice matches framing, artifact cap respected, keyword hits a JD nice-to-have) and still fail this one — because passing on paper is not the same as landing on a fast read. Fail if any of these hold:

- **Technical mechanics without a business outcome.** The bullet lists what was implemented (framework names, timeout values, table schemas, error-handler routes) but no measurable delivery, adoption, or decision the work drove. Example failure — "Shipped HITL and observability for `content-advisor`: Telegram Approve/Decline via n8n `sendAndWait` with 24h timeout; per-execution runs table (counts, scores, tokens, errors); workflow-error handler routing to Telegram." The recruiter has to infer that this is "feature performance monitoring" — the bullet doesn't say so. CUT.
- **Personal-tool detail without a client anchor.** The bullet describes a candidate-authored side project or personal AI workflow (content-advisor, an internal Claude Code / MCP setup) without naming a client outcome, a downstream user, or a measurable business result. Reads as "internal tinkering," not "product the user shipped for a customer." CUT unless a client / user-count / outcome anchor exists in the same bullet.
- **Abstract methodology without domain context.** The bullet names a method or technique (`PCA`, `numerical optimization`, `stochastic modelling`, `visual anomaly detection on 2D spatial datasets`) without an outcome tying it to a delivered product or business decision. Fail *unless* there is a concrete outcome clause in the same bullet — a revenue delta, an investment-decision, an issue found and acted on. If the outcome exists, the bullet passes; if the bullet reads purely as method-name plus dataset-name, CUT.
- **Nice-to-have redundancy without unique signal.** When two or more bullets on the same CV hit the same JD nice-to-have and one lacks a measurable outcome or a distinct scarce keyword, keep the strongest and CUT the rest. This applies even when each bullet passes on its own — three AI bullets hitting the same "AI" nice-to-have, one lacking a measurable outcome, means the outcome-less one is padding regardless of what its keyword parenthetical says.

**Sparse role is a legitimate signal.** When a company's Achievements pool has no bullet that passes this test for the current vacancy, the company gets 1 bullet, or 0. Do NOT pad to look proportional to calendar duration. A one-bullet Baker Hughes or a zero-bullet Roxar tells the reader "at this employer, my work did not overlap with your requirements," and lets the on-target tenures carry the signal without noise. Padding to proportion produces word salad and dilutes the on-target bullets elsewhere on the CV. If the user's manual post-draft review reveals a real overlap the drafter missed, the user backfills master and re-drafts — that flow is the safety net, not padding.

**Drafter default: CUT when the reader-visible link isn't obvious.** Do not soften a weak bullet by tacking on a JD-adjacent phrase to make the connection more visible — that produces drafter-authored language on top of master, and the user has rejected that pattern before. The bullet as it stands in master either lands on this vacancy on a first read, or it doesn't. If it doesn't, cut and move on.

**Critic default: enumerate the JD line per retained bullet.** On every draft-critic pass, for each retained bullet, name the specific vacancy line the bullet serves in one clause. If the critic cannot name a line without paraphrasing or making an inference chain, the bullet fails and must be flagged must-fix.

### Single-artifact saturation guard

**Cap at 1 bullet per named artifact in a CV.** Master stores multiple bullets on the same artifact (a product, repo, side project — e.g. `bevra.app`, `content-advisor`, the Kosovo CV pipeline, Offset Well Analyzer) to give the drafter variety ACROSS vacancies, not to be selected together. Two or more bullets naming the same artifact reads as "that's all this person did" on the rendered CV, even when each bullet covers a distinct technical axis (stack vs. UX vs. evals vs. observability). Side projects and repos are *hooks*. One mention per CV is enough to anchor the credential; a second mention spends real-estate the recruiter would rather see go to a different engagement, product, or domain.

**Counting rule.** A bullet counts toward an artifact's cap if it names the artifact anywhere in its body — primary subject AND secondary cross-references both count. A bullet that names two artifacts counts toward BOTH caps. Tagline and SUMMARY mentions do NOT count toward the bullet cap (they set up the section); only bullet-body mentions do.

**Carve-out — tenure-platform.** When the artifact IS the platform / product the role is built around (named in the company tagline, OR the company is unambiguously known externally for it — e.g. `JewelSuite` under Baker Hughes), the cap does NOT apply. The audience expects multiple bullets to talk about the role's subject; capping it would suppress natural platform-PM language. The cap targets side projects and peripheral artifacts a recruiter might over-weight as the candidate's only output. Apply the carve-out narrowly — it covers the named tenure platform, not every product the candidate happened to ship at that company.

When the pool has more than 1 high-fit bullet on the same capped artifact for the current vacancy, either (a) pick the 1 strongest and drop the rest, or (b) collapse multiple bullets into one tight bullet that names the artifact once and lists the technical axes in a comma-separated or semicolon-separated clause. Then use the freed slots to surface bullets from a different client engagement, project, or product. Breadth across artifacts beats depth on one, especially at companies (e.g. Rhodaris consultancy) where the audience expects multiple distinct engagements.

Worked example of the failure mode (Rhodaris, AI PM vacancy): three bullets selected — (1) "Took bevra.app 0→1 as sole product owner", (2) "Shipped HITL for content-advisor, the agentic engine *for* bevra.app", (3) "Ran bevra.app in production solo: FastAPI on Fly.io..." — has THREE bullets naming `bevra.app` (the secondary "for bevra.app" reference in #2 counts under the counting rule above) and reads as "the whole consultancy is bevra.app." Cap fix: keep #1 (strongest PM signal); strip the secondary "for bevra.app" reference from #2; drop #3 entirely OR replace it with a non-bevra.app pool bullet that surfaces a different engagement. `content-advisor` mentions get the same cap=1 treatment — if both an HITL/observability bullet and an eval-harness bullet are vacancy-load-bearing, collapse them into one bullet covering both axes (option b).

### Domain-axis guard — gate on domain coherence, not just keyword match

Bullet selection has TWO axes. The function axis (DS / PM / geo / FDE) is already handled by Step 1's framing choice. The **domain axis** must be gated explicitly at bullet selection — keyword matches that ignore domain coherence produce bullets that read off-axis on the final CV.

Read the vacancy's domain (the *what*, not the *who*) before mining the pool:

- **GenAI / LLM domain** — explicit mentions of LLM, RAG, agents, agentic workflows, vector retrieval, prompt engineering, LangChain, GenAI.
- **Classical ML domain** — supervised, unsupervised, dimensionality reduction, anomaly detection, time-series forecasting, computer vision, geospatial ML, on production data. Often signalled by "Applied Scientist," "ML Scientist," "Data Scientist" titles without "GenAI" / "LLM" in the JD.
- **Marketing analytics domain** — A/B testing, marketing ROI, attribution, marketing-mix modelling, funnel analysis, CRM data.
- **Industrial / geospatial / subsurface domain** — sensor telemetry, geospatial features, road networks, satellite imagery, asset performance.
- **Product-management domain** — roadmap, OKRs, stakeholder coordination, release management. (Not technical-bullet content, but a domain a PM CV may emphasize.)

**The rule:** if a bullet's **keywords** match the vacancy but its **domain** is off-axis from the vacancy's domain, drop it — unless the vacancy explicitly invites that domain. **This gate applies to bullets selected for ANY framing** (`[pm]`, `[ds]`, `[pm-eng]`, `[fde]`, etc.) — a PM-track bullet at an off-domain company is just as off-axis as a DS-track bullet, even when the bullet itself reads as role-coherent. A €10M–€90M capital-project decision-support bullet from an oil & gas PM tenure on an ESG SaaS Product Engineer CV: function axis matches (PM ownership), domain axis off (capital-intensive energy ops vs. compliance-first B2B SaaS) → DROP or reframe to strip the off-axis domain anchor (e.g. lead on "internal tooling as a product" without the €10M-project framing). This is must-fix at draft time AND at critic gate time.

Worked examples (TomTom Expert Applied Scientist — domain is classical ML + geospatial + production pipelines):

- "Built an LLM document-review pipeline with Pinecone RAG, golden-set evals, LLMOps controls." Keywords match (production pipeline, evaluation). Domain is GenAI/RAG, off-axis. **DROP.**
- "Lifted marketing ROI 20% for Giro555 with primary/supporting/counter-metrics framework." Keywords match (segmented metrics, evaluation framework). Domain is marketing analytics, off-axis. **DROP.**
- "Shipped a geospatial XGBoost classifier into the Kosovo consumer-facing maps product, predicting from OpenStreetMap road network features." Keywords match (geospatial, road network, XGBoost). Domain is classical ML + geospatial, on-axis. **KEEP.**

Worked example of an explicit invite (vacancy mentions "experience with LLM / RAG pipelines is a plus"): the LLM doc-review bullet is now on-axis as a nice-to-have. Include with one tight bullet — don't pad the CV with three LLM bullets just because the gate opened.

**When the vacancy domain is mixed** (e.g. "production ML AND GenAI tooling"), include bullets from both domains but keep proportion. The dominant domain in the JD body, not the nice-to-have section, sets the CV's center of gravity.

### Company product context — binding on the domain axis

The Domain-axis guard above operates off vacancy wording. Vacancy nice-to-haves are noisy — a JD may list "AI, computer vision, industrial automation, IoT, edge computing" while the company's actual product only uses CV + edge (no LLM, no autonomous). Without a company anchor, the drafter treats every listed adjacency as equally valid and defaults to whichever bullet has the sharpest numbers — often the LLM doc-review bullet, since Rhodaris' LLM work carries the cleanest deltas (70% cut, 30→10% error). The SUMMARY closing clause then anchors on a capability the company doesn't actually build. This subsection closes that gap.

**The rule.** If `vacancies/<slug>/analysis.md` opens with a `## Company product context` section (produced by `/cv-analyse` per its Step 2), that section names the AXIS OF PRIMARY ALIGNMENT for this vacancy. Bullets whose domain matches the company's PRODUCT stack — not just the vacancy's nice-to-have list — win top-3 placement per company and the SUMMARY closing clause. Bullets that hit a vacancy nice-to-have but are OFF the company's product stack rank last, or CUT entirely when the pool has a company-axis alternative.

Read the "Company product context" section end-to-end before mining the pool. The paragraph names (a) the concrete product, (b) the technical stack (CV / LLM / classical ML / dashboards / hardware / edge / IoT / autonomous / geospatial), (c) named customers or market segment. Item (b) is the axis; (a) and (c) sharpen edge cases.

**Worked example (Jaipur Robotics — waste-to-energy CV + edge + dashboards):**

- Vacancy nice-to-have: "AI, computer vision, industrial automation, IoT, edge computing, or data-intensive products."
- Company product context (from `/cv-analyse`): RGB cameras + edge computers in waste bunkers; semantic-CV models for hazard detection, calorific-value mapping, crane analytics; web-app dashboard for plant operators. **No LLM, no RAG, no agent components.**
- **Kosovo satellite-segmentation bullet** — company axis CV + geospatial + production pipeline. ON company product stack. Load-bearing. **Top-3 per company, SUMMARY anchor candidate.**
- **Isolation Forest anomaly detection on streaming sensor data** — company axis classical-ML + streaming edge sensor telemetry. ON company product stack (edge + sensor). **Top-3.**
- **XMAC 3D hardware-sensor integration** — hardware-sensor integration into a dashboard product. ON company product stack (hardware + dashboards). **Top-3.**
- **LLM document-review bullet** — matches vacancy's `AI` umbrella. OFF company product stack (company builds no LLM component). Vacancy explicit list does NOT name LLM/RAG. **DROP** or rank dead-last. Do NOT anchor SUMMARY on it.

**Absent-section fallback.** When analysis.md has no `## Company product context` section (older analysis file, or `/cv-analyse` skipped), the guard falls back to vacancy-only anchoring per the paragraphs above. The rule is additive — no regression on pre-existing analyses.

**Critic default.** On every draft-critic pass, cross-check (a) the SUMMARY closing clause and (b) the first bullet of every company against the company product context. A SUMMARY anchor that names a technology the company doesn't build (LLM on a CV-only company; classical-ML on a pure-LLM startup; dashboards on a hardware-first company) is a **must-fix**, not a should-fix — the SUMMARY closing clause is the most exposed surface in the CV and mis-anchoring it is the single most visible failure mode. First-bullet mis-anchoring is should-fix (still visible, but recoverable on a scan past the SUMMARY).

### Bullet-body scrubbing on emit — strip vacancy-off-axis specifics from kept bullets

The Domain-axis guard operates at the *selection* layer — decide whether the bullet as a whole belongs on the CV. This guard operates at the *phrasing* layer — decide which specifics inside a kept bullet survive the trip from master to `cv.md`. Master bullets are stored generously (concrete tech names, vendor names, language names, domain acronyms) so one master bullet re-uses across many vacancy shapes. On emit, strip the specifics that (a) are off-axis for this vacancy AND (b) are not the bullet's load-bearing signal for this vacancy.

**Test per specific:** would removing it make the bullet *weaker* for THIS vacancy? If no, cut. If yes (the specific IS the signal the audience is buying), keep.

Applies to: language names (C#, C++, Kotlin, Scala, Ruby), vendor / product names (Salesforce, Petrel, JewelSuite, Databricks), domain acronyms (WITSML, SODM, FWL, DSWI, GIIP), industry-specific proper nouns (K18-Golf, Q1D2xx, Aramco, ADNOC), release-cadence specifics (`over 4 quarterly releases`, `in a fixed release cadence`, `quarterly release`, `bi-weekly cadence`), and any concrete detail that pulls the bullet toward a domain — or a delivery culture — the vacancy is not in.

**Worked example (Freeday Forward Deployed Engineer — Python / JavaScript scale-up):**

Master bullet — `"Diagnosed and root-caused production issues by debugging in C# and C++ and using git history analysis to support QA and incremental release sign-off."`

- Load-bearing signal for Freeday: *troubleshooting / root-cause / debug depth*. The audience is buying "this person can walk into a production issue and diagnose it."
- Off-axis specifics: `"in C# and C++"` — the vacancy names Python and JavaScript; C# / C++ are neither JD-named nor implied by any vacancy noun. Removing them does NOT weaken the troubleshooting signal.
- Emit: `"Diagnosed and root-caused production issues through runtime debugging and git history analysis, supporting QA and incremental release sign-off."`

**Worked example where the language IS the load-bearing signal (hypothetical Django backend vacancy):**

Master bullet — `"Shipped a Python microservice on FastAPI serving 10k req/sec."`

- Load-bearing signal: *Python + FastAPI production experience*. The audience is buying language / framework specifics.
- The language names ARE the signal. Do not strip.
- Emit as-is.

**Worked example — release-cadence specifics on SaaS-native / DevOps-mature vacancies:**

Master bullet — `"delivered JewelSuite within the 14-team Shell–Baker Hughes Scrum program over 4 quarterly releases, managing scope, blockers, release readiness, and stakeholder communication in a fixed release cadence."`

- Load-bearing signal for a SaaS-native or DevOps-mature vacancy: *cross-team program coordination + release-readiness discipline*. The audience is buying "operates at multi-team scale and keeps releases predictable."
- Off-axis specifics for that audience: `"over 4 quarterly releases"` + `"in a fixed release cadence"` — SaaS-native and DevOps-mature audiences expect continuous / multi-daily / weekly deploys as the baseline. Quarterly-cadence framing reads as *slow-team signal* on that audience even though the underlying coordination work is on-axis. Removing them does NOT weaken the coordination signal.
- Emit: `"delivered JewelSuite within the 14-team Shell–Baker Hughes Scrum program, managing scope, blockers, release readiness, and stakeholder communication."`

Same logic applies to `"bi-weekly cadence"` on continuous-deploy audiences and `"quarterly release"` anywhere the vacancy company ships continuously. Test: what's the vacancy company's own release cadence? If continuous / weekly, strip. If quarterly / semi-annual / on-prem-installed, keep.

**Companion rule to the Skills-side Nostrion cut.** If a language / vendor / acronym is off-axis enough to drop from Skills (per the "Skills selection — single vacancy-driven gate" below, and the exclusion-list rule for umbrella nouns), it is off-axis enough to strip from bullet bodies too. A CV that omits `C#` from Skills but keeps `"in C# and C++"` inside a bullet body contradicts itself — bullet says "I know C#", Skills silently omits it, reads as an oversight to a screener. Skills and bullet body must agree on which specifics are load-bearing for the vacancy.

**Do NOT strip when:**

- The specific is the bullet's load-bearing signal for THIS vacancy (as in the Django-vacancy example above).
- The specific is the *name of the tenure platform* the audience is unambiguously buying (JewelSuite under Baker Hughes on a subsurface-software vacancy — the platform is the tenure, stripping the platform hollows the bullet).
- The specific is JD-named verbatim in the vacancy body (the vacancy explicitly asked for it).
- The vacancy company's own product ships as desktop / on-prem / enterprise-installed software with periodic release cycles (e.g. JewelSuite-style installed enterprise apps, subsurface-software vendors, IDE / plugin vendors, industrial-desktop shops) — that audience reads quarterly / bi-weekly cadence as normal enterprise-software discipline, not slow-team signal. Cadence specifics stay.

**Scrubbing is drafter default, not critic escape hatch.** The drafter scrubs on emit; the critic verifies. The critic MUST flag surviving off-axis specifics under Check 4 (JD-axis relevance) — do NOT punt to a "drafter will fix on rewrite" mentality that lets the specific leak into `cv.md`.

## Step 3 — Output assembly: fill the framing's role slots

Treat each role in the chosen framing as a slot. Place each selected bullet under the slot where it tells the strongest story.

**Role order on output: reverse chronological — newest sub-role first.** The framings catalog in master lists sub-roles newest-first to mirror the output order; preserve that order on `cv.md`.

- **Single-role framing**: all selected bullets go under the single role header. No placement decision to make.
- **Multi-role framing** (e.g. Data Scientist + Product Manager): for each bullet, pick the role slot it best belongs to — judging by:
  - The role title (Sr. PSE / Data Scientist → engineering/ML bullets; Product Manager → product/roadmap/stakeholder bullets; Geomechanics Specialist → geo bullets).
  - The bullet's content (a roadmap bullet naturally fits PM; an SDK bullet naturally fits Sr. PSE; a "Western Siberia" bullet fits the Moscow sub-role of Wintershall's `[geo]` framing).
  - The function tag prefix as a soft hint (`[pm]` leans PM, `[ds]` leans DS, etc.) — but content overrides the tag if the story is stronger elsewhere.
- **Overlapping or parallel timelines** (e.g. Wintershall's Geoscientist `[geo]` track running parallel to the Data Scientist `[ds]` track for the same calendar years): the inline `[instruction]` line on the company picks which framing is shown. Bullets from the unused track stay in the pool but are not surfaced on this CV.
- **Empty role slot fallback.** If one sub-role of a multi-role framing has no high-fit bullets for the vacancy, do NOT pad the slot with adjacent bullets to look symmetrical. Two acceptable moves: (a) switch the company's framing to a single-role catalog entry that covers the same tenure — preferred when the off-target sub-role is short or its content is filler for this vacancy; (b) keep the multi-role framing but emit the off-target sub-role with one tight bullet maximum. Filler bullets on a sub-role to look balanced will leak off-vacancy noise (regulator names, marketing jargon, sector-specific acronyms) and weaken the CV. Symmetry of bullet count across sub-roles is never a goal.

When a bullet could plausibly fit two slots, pick the one that produces a more coherent narrative for the chosen framing. A mentoring bullet doesn't need to live where it factually happened — it can land under whichever role makes the strongest senior-screening signal.

### Sparse-slot narrative anchor — sparse role slots need role-level framing

When a role slot has 0 or 1 bullets (single-role framing OR one sub-role of a multi-role framing that lands sparse for a given vacancy), the bullet (or empty header) cannot rely on surrounding context that isn't there. In a multi-bullet role, the reader builds an emergent picture from the collection (what platform, what team, what customers); in a sparse slot that picture never forms and the CV reads as floating — even when the bullet has an outcome clause, the reader has no answer to "shipped WHERE, for WHOM, on WHAT?"

**The rule:** every sparse role slot (0 or 1 bullets) must carry a grounded anchor. Two mechanisms, in preference order:

**Preferred — role-level pre-text sentence.** An italic paragraph inserted DIRECTLY UNDER THE ROLE DATES LINE, before the first bullet (or standalone after the dates line for 0-bullet slots). Carries a one-sentence framing of the role's scope: what the user worked on, on what platform / product / system / team / customer set, over what tenure. Renders as `CV Tagline` style (same as the company italic tagline). This is the primary mechanism because (a) it separates role framing (pre-text) from delivery outcome (bullet), keeping the bullet outcome-focused, and (b) it works uniformly whether the slot has 1 bullet or 0. See `cv-markdown-format.md` "Optional role-context pre-text" convention for the format.

**Fallback — in-body anchor inside the bullet.** If pre-text would repeat the company tagline verbatim (adding no new signal), OR the bullet already carries a named anchor naturally (e.g. `Deployed to a 200-user pilot for Total`), the sparse-slot rule can be satisfied by a bullet-body anchor without pre-text. The in-body anchor may override the Bullet-body scrubbing rule (Step 2) for THAT specific — audience isn't buying anything without an anchor; a truthful platform / client / team name beats a floating claim.

**Valid anchors** (both mechanisms):

- **Named platform / product / system** — JewelSuite, content-advisor, bevra.app: a specific named artifact.
- **Named client / counterparty** — Total, ADNOC, Shell, Giro555.
- **Named team / scope reference** — 14-team program, team of 5, 50 users, 4-week MVP, JV asset.
- **Named project / engagement** — Radiant project, Kosovo pipeline, Big Loop.
- **Named asset / system context** — K18-Golf, Q1D2xx, JewelEarth SDK (when defensible for the vacancy).

Domain-genre phrases ("streaming sensor data", "unstructured documents", "the data-product portfolio") are NOT anchors — an anchor is a named specific. The outcome clause itself (percentages, €M figures, adoption lift) counts as an OUTCOME, not an ANCHOR.

**Anchor-type preference on cross-domain screens.** When multiple defensible anchors are available and the vacancy's audience is culturally distant from the company's domain (e.g. a GenAI-native startup screen reading a Baker Hughes subsurface bullet), prefer scope-anchors (team, program, JV, cohort size) over platform-anchors (product/system names). "14-team enterprise program" reads audience-neutral; "JewelSuite platform" carries subsurface signal that the audience actively isn't buying. On audience-aligned screens (energy-adjacent for the BH example) the platform-anchor is fine and often preferred for its specificity.

**Worked examples:**

FAIL (no anchor anywhere — 1-bullet slot with only outcome):

```
### Product Manager
Jul 2023 – Dec 2024

- Shipped GenAI (GANs) into production, lifting product adoption.
```

Reader can't picture WHAT product. Outcome clause without scope framing.

PASS — pre-text mechanism (preferred):

```
### Product Manager
Jul 2023 – Dec 2024

*Product ownership on the JewelSuite subsurface platform across a 14-team Shell–Baker Hughes Scrum program.*

- Shipped GenAI (GANs) into production, lifting product adoption.
```

Role scope framed at role level; bullet stays outcome-focused; clean separation.

PASS — in-body anchor (fallback):

```
### Product Manager
Jul 2023 – Dec 2024

- Shipped GenAI (GANs) into the JewelSuite platform, lifting product adoption.
```

Anchor lives inside the bullet. Weaker than pre-text (bullet does double duty as framing + outcome); use when pre-text would repeat the company tagline verbatim or the bullet naturally names its anchor.

PASS — pre-text on 0-bullet sub-role:

```
### Product Manager
Nov 2018 – Sep 2019

*Product operations on internal decision-support tooling for capital-intensive operations.*
```

0-bullet sub-role kept for tenure coverage; pre-text prevents the empty-header render. Reader knows what the role was even without proof-bullets underneath.

**Fallback if no anchor can truthfully be added:** drop the bullet, accept the 0-bullet sub-role per the Empty role slot fallback, and consider whether a pre-text can still frame the empty sub-role. A 1-bullet floating slot with no framing is worse than a 0-bullet slot; a 0-bullet slot WITH pre-text is better than either.

Strip the function tag and keyword parenthetical when emitting the bullet on `cv.md` — those annotations are master-only metadata. See `cv-markdown-format.md` for the renderer-expected output shape.

## Step 4 — Education, certifications, and skills

Function tags on Education and Skills entries are author notes, not retrieval filters — same rule as the Achievements pool. Match by content fit to the vacancy, not by tag prefix.

- **Education & Certifications: default INCLUDE.** Drop an entry only if it's narrowly off-domain (e.g. SPE membership on a fintech CV) or master NOTES flags it as unverified.
- **Read the vacancy on two axes, not one.** Function axis (DS / PM / geo / FDE) picks the framing. Seniority/scope axis (IC / Senior / Lead / Manager / Director) drives which management and delivery credentials are relevant. **Gate cross-axis credentials on the vacancy title, NOT on the responsibility list:**
  - **PMP and PSPO II**: keep ONLY when the vacancy title carries explicit line-management or hybrid-PM signal (Manager, Director, Head, Group PM, PM + X). Drop on pure IC titles ("Senior Data Scientist", "Expert / Staff / Principal Applied Scientist", "Senior MLE", "Lead DS" without management line) *even when the JD body mentions mentoring, coordination, or planning*. IC mentoring does not justify a PM credential — it dilutes the technical signal and reads as off-axis on a pure-IC technical CV.
  - **Heavy-industry technical-lead carve-out for PMP.** "Lead [discipline]", "Principal [discipline]", or "Senior Tech Lead" titles in regulated heavy-industry operator settings (oil & gas, mining, energy, utilities, nuclear, regulated medical) — KEEP PMP. In those sectors the Lead/Principal title implies project coordination (study scope, schedule, contract / vendor management) and peer coordination across geoscience / reservoir / drilling / production teams, plus JV and regulator-facing deliverables. The audience reads PMP as the credential that goes with running studies and reporting upward, not as a PM-pivot signal. Worked examples: KEEP for "Lead Geologist", "Lead Reservoir Engineer", "Principal Geologist", "Senior Tech Lead — Subsurface". Still DROP for adjacent IC titles in the same sectors that don't carry the lead/principal scope ("Senior Geologist", "Geomodeller", "Petrophysicist"). PSPO II and Stanford School of Engineering — Certificate, Product Management stay gated on the original rule — heavy industry doesn't read those as on-axis the way it reads PMP.
  - **Stanford School of Engineering — Certificate, Product Management**: keep on PM, Manager, and Director titles. Drop on pure IC Applied-Scientist / DS / MLE titles for the same reason — executive-PM education on an IC technical CV signals career-pivot ambiguity and dilutes the technical headline.
  - When in doubt on a borderline title, drop. The tech-side credentials (MSc, ML coursework, vendor / cloud certs, publications) carry the screen on IC technical CVs.
- **Education sub-bullets — apply the same domain-axis logic as the Achievements pool.** Master tags multi-detail education entries (e.g. Gubkin MSc) with `[ai]` / `[ds]` / `[geo]` / untagged sub-bullets covering thesis facets, coursework, hardware, and field work. Pick sub-bullets by vacancy domain match, not by tag prefix as a filter. The tag is a soft hint; the content drives selection:
  - **DS / Applied Scientist / ML / Data Scientist vacancies:** surface the AI/CV thesis (e.g. neural-network image classifier) and the Statistics & Mathematical Modeling / Programming & Algorithms / Physics-Based Modeling coursework. Drop generic-coursework one-liners. 2–3 sub-bullets.
  - **Geology / geoscience / subsurface vacancies:** surface the geology thesis (e.g. Lower Permian carbonates, Timan-Pechora), hardware coursework (MWD / petrophysics measurements / metrology), and the 3D seismic acquisition + well perforation field work. Drop the AI/CV thesis or keep as a secondary one-liner only if the vacancy is hybrid. 3–4 sub-bullets.
  - **PM / Manager / Director vacancies (including AI PM, Group PM, Product Lead):** keep the MSc line and at most ONE short sub-bullet showing relevant technical foundation — AI thesis for AI PM, generic coursework otherwise. No multi-line sub-detail block — it crowds the PM headline credentials and reads off-axis. 1–2 sub-bullets max.
  - **Hybrid / cross-axis (e.g. AI PM, ML PM, Engineering Manager):** AI/CV thesis + one Statistics-emphasis coursework one-liner. 2 sub-bullets max.
  - **Hardware / Robotics / IoT PM (product involves hardware, robotics, IoT, edge computing, or industrial-sensor systems as core capability):** AI/CV thesis + one hardware-coursework-and-field-work one-liner (MWD telemetry hardware design + laboratory petrophysical measurement + metrology + 3D seismic acquisition field work + well perforation field work). Hardware coursework REPLACES the Statistics one-liner as the "relevant technical foundation" for this vacancy shape — the recruiter reads hardware credentials as on-axis for a robotics/hardware screen where Statistics reads as universal-PM. 2 sub-bullets max. **Anchor test — apply when ANY of these hold:** (1) the company name explicitly signals hardware / robotics / sensors (e.g. `Jaipur Robotics`, `Innatera`, `IWELL`), (2) the JD names hardware / robotics / IoT / edge computing / industrial automation / sensors as a required (not merely nice-to-have) capability, (3) the primary product is fundamentally hardware-driven (physical devices, industrial control systems, edge-deployed CV on physical sensor streams). If none of the three anchor tests fire, fall back to the standard PM or Hybrid sub-bullet case.
  - **Untagged sub-bullets** (e.g. generic Coursework) are neutral — keep on any framing where the content fits; drop when they dilute a sharper sub-bullet selection.
- **Skills: pick categories by content match to vacancy keywords.** Aggressive trim discipline:
  - Drop a category entirely when it has zero relevant items OR fewer than 2 items with strong vacancy fit. A 1-item category usually folds into a more relevant category.
  - Recategorize items when the master's label doesn't match the vacancy's framing. Example: "primary / supporting / counter-metrics" is a model-evaluation framework — it belongs under AI/ML or MLOps on an Applied-Scientist CV, NOT under "Analytics & experimentation" which reads marketing-flavoured on a technical screen.
  - **Skills selection — single vacancy-driven gate.** For each candidate Skill item, the entry question is: **does the vacancy need this skill?** "Need" is satisfied by ONE of three buckets:
    1. **JD-named** — the skill appears verbatim in the JD body (required-skills, nice-to-have, responsibilities, OR product description).
    2. **Domain-implied (narrow)** — the JD names a specific product / vertical / system noun, and the skill is the canonical capability for that exact noun. *Maps platform → geospatial ML. LLM platform → RAG. Vision platform → computer vision.* The implication must trace to a specific JD noun, NOT a general "AI" / "ML" / "data" framing.

        **Landscape-breadth sub-anchor.** When the JD names *landscape awareness itself* as a required capability — e.g. "Up to speed on the landscape," "Know what's shipping across the AI tooling ecosystem," "familiarity with the current tooling ecosystem" — an entire Skills category showcasing breadth-of-tooling (LLM providers, foundation models, IDE plugins, PM SaaS platforms) gets a category-level bucket-2 anchor from that JD line, and individual items in that category do NOT need per-item verbatim naming. This is a narrow carve-out for breadth-not-depth screens: it applies to CATEGORIES surfacing a landscape (Models & providers, AI-native tools), not to per-item padding elsewhere. Cap the category at ≤8 items to keep it a legible landscape signal, not a keyword dump. Individual items still must be defensible from master.

        **Exclusion list — these umbrella nouns are NEVER valid bucket-2 anchors, even when used verbatim in the JD:** `AI`, `ML`, `AI products`, `AI capabilities`, `data`, `data-driven`, `data-driven platforms`, `enterprise software`, `platform`, `software`, `technical`, `quantitative`. They are too broad to imply any specific skill — they require a narrower noun (vision platform / LLM platform / maps platform / risk-modelling platform / forecasting platform / RAG platform) before the canonical-capability mapping fires. The exclusion list is binding even when the umbrella term is named under "required skills" — it means the JD has not named a specific skill, not that everything AI-shaped passes the gate. If the only JD line a Skill item points at is an umbrella term on the exclusion list → the item fails bucket 2 and must clear bucket 1 (verbatim) or bucket 3 (generalization) to survive.
    3. **Generalization of selected bullets on THIS CV** — multiple bullets demonstrate the capability; the Skill item is the umbrella term. See "Two valid sources" #2 below for the existing rule.

    If none of the three apply, the item is NOT vacancy-needed — drop, regardless of whether it's in master, bullets, or the user's broader toolkit. A "strong quantitative profile" must-have is carried by Education + DS bullets — it does NOT license importing every ML library in master under that umbrella.

    Worked example (Nostrion sovereign-AI / GenAI platform vacancy): the JD's domain noun is *"sovereign AI platform for organizations that work with sensitive data."* The data is text / documents / structured records, not imagery — so vision is NOT domain-implied. `computer vision (segmentation, detection)` → DROP. `XGBoost`, `scikit-learn`, `Isolation Forest`, `numerical optimization`, `risk-scoring models` → DROP (none JD-named, none narrowly domain-implied, none needed as a generalization of bullets selected for this CV). `model explainability` → KEEP (JD: *"explainability… essential"* verbatim). `responsible AI` and `telemetry-driven iteration` → KEEP if narrowly domain-implied by the JD's "trusted / auditable / data-driven" language.
  - **Two valid sources for a vacancy-needed Skill:**
    1. **Explicit in master / bullets** — verbatim or near-verbatim. Skills line is the ATS keyword anchor — KEEP EVEN WHEN A BULLET ALSO NAMES IT. Recruiters and ATS scrapers read Skills as the credential roster; bullets prove the credentials. Both surfaces serve different purposes; redundancy between them is a feature, not a bug.
    2. **Generalization of bullets that don't spell it out.** Multiple bullets demonstrate a capability the vacancy names; the Skill item is the umbrella term not literally said in any bullet. Examples: bullets show XGBoost + Isolation Forest + GANs → Skill `supervised / unsupervised learning` when the vacancy uses that phrase; bullets show OCR + RAG + prompt chains → Skill `NLP`; bullets show model-monitoring + eval gates + HITL → Skill `model governance`. The generalization must be defensible from concrete bullet evidence — not invented to bridge a gap.
  - **Drop for any of these:**
    - **Low value for THIS vacancy** — item is in master but the vacancy doesn't ask for it or imply it. Example: dropping `Workflow orchestration`, `BI dashboards`, `marketing analytics`, `JV governance`, `node-graph workflows` on a maritime AI PM vacancy. Be ruthless — the vacancy is the only lens.
    - **Padding a gap** — vacancy-named item with no master backing and no bullet evidence (e.g. `AWS SageMaker` if the user has never touched it). Goes in the gap list, not in Skills.
    - **Synonymous with another kept item** — `interpretability` when `model explainability` already kept; `vector retrieval` when `embeddings` already kept.
  - **Items-per-category cap: ~8 target, 12 hard.** Past 12 items the line wraps to a paragraph and stops reading as a skill block; signals padding. When a category is over the cap, cut order is: (a) items the vacancy implies most weakly, (b) synonymous items, (c) least-recognizable items.
  - **Critique check (binding on draft-critic):**
    - **Missing essentials (must-fix).** Any skill the vacancy NAMES BY NAME (required or nice-to-have) that has defensible master backing AND is NOT present in the Skills block → missed ATS anchor, must-fix. The critic should enumerate vacancy-named skills and check each against the rendered Skills block.
    - **Low-value padding (must-fix).** Any Skills item NOT mapped to a specific vacancy need (named or implied) → must-fix; cut. The single-vacancy-driven gate is binding: drafter applies it at draft time; critic re-applies it at gate time. No "answer or cut" second-chance — if the drafter cannot point at a vacancy line (named or implied) that needs the item, it drops. Worked example: `C#, .NET` on a Python/AI-first startup vacancy — defensible master backing (Baker Hughes, Roxar) but the vacancy doesn't need it → must-fix, cut.
    - **Category overrun (must-fix).** Any Skills category with >12 items → must-fix (line wraps to a paragraph; defeats the format).
    - **Padded gap (must-fix).** Any Skills item that has no master backing AND is vacancy-named (i.e. surfaced only to match the ATS) → must-fix; goes back to the gap list.
  - **Apply the Step-2 Domain-axis guard to Skills too, not just bullets.** Keyword match without domain coherence is what produces a "GenAI stack: LangChain, Pinecone, LLM-as-judge" category on a classical-ML vacancy — every item is real, every item is in master, but the *domain* is off-axis from the vacancy and surfaces career-pivot ambiguity. Read the vacancy's domain first, then gate Skills categories and individual items on it the same way you gate bullets.
    - Whole-category drop examples (classical-ML / geospatial / production-ML vacancy, e.g. TomTom Applied Scientist):
      - **GenAI stack** (LangChain, embeddings, vector retrieval, LLM-as-judge, LLMOps tracing) — drop entirely unless the JD body or required-skills section explicitly mentions LLM / RAG / agentic / GenAI. Nice-to-have buried two scrolls down is not an invite.
      - **CRM / SaaS / Design** — drop on any IC technical CV unless the vacancy explicitly references the tools.
      - **Risk & Compliance** (PM-flavoured) — drop on pure IC vacancies; the technical credentials carry the screen.
    - Within-category item drop examples (item is keyword-match but domain-off):
      - `Pinecone` in **Databases & storage** on a classical-ML vacancy — vector DB belongs to LLM / RAG. Drop even if the category itself stays for Postgres.
      - `BDD (SpecFlow)` in **Testing & QA** on a Python DS vacancy — SpecFlow is .NET-only. Drop and keep the Python-flavoured QA items.
      - `C++ / C# debugging` in **Testing & QA** on a Python DS vacancy — the JVM-adjacency to a Java nice-to-have is better surfaced in **Languages & frameworks**, not by stressing C++/C# debugging in a Python role.
    - **Don't pad to bridge a gap.** If the vacancy demands X (e.g. Spark / Databricks / drift detection) and master has no shipped bullet for X, surfacing X as a skill keyword without backing is keyword padding on a load-bearing requirement — exactly the signal a senior screen flags. Leave the keyword in if it's defensibly in master Skills, but expect the gap to stay flagged in `analysis.md` until a real bullet covers it.
  - Default-out on borderline items. A tight 8-category skills block beats a 14-category block padded with adjacent items — filler categories make every category look weaker.
- **Citizenship line:** Master may carry an explanatory parenthetical (e.g. "Citizenship: Dutch (no sponsorship required for NL / EU work)"). Drop the parenthetical when applying within NL as a Dutch citizen — it's tautological for a NL employer reading a NL applicant. Keep the parenthetical for EU non-NL or international vacancies where the work-eligibility signal is non-obvious. The citizenship line itself is always retained.
- **Spoken languages:** Surface only languages with positive screening signal for the vacancy's working environment. NL-based vacancy: English + Dutch only. EU non-NL vacancy: English + the local working language if mastered. Drop heritage / mother-tongue languages with no relevance to the role or its market — they are noise on a Western-Europe technical screen and may carry off-axis signal. Add other languages only when the vacancy explicitly references them as working languages or relevant markets.

Strip function tags from output — same as bullets.
