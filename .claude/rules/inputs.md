# Inputs — authority order

When facts conflict, **master CV wins**.

1. **MASTER_CV.md** — the live canonical source for all CV facts, bullets, variant rules, and disambiguation guards. Located at `./MASTER_CV.md` at the repo root. Read fresh at the start of every run; never cache.
   - **Filesystem-available surfaces** (Claude Code, Claude Desktop session): read the file directly.
   - **Other surfaces** (web, mobile, or filesystem unavailable): ask the user to paste the master into chat before producing any tailored CV. Do not proceed from memory or from a prior session's content.

   The `## NOTES — not for export` section at the bottom of the master is binding. Never drift those facts.
2. **Vacancy** — attached or pasted (or read from `vacancies/<slug>/vacancy.md` in Claude Code).
3. **Provided CV** (optional) — if uploaded, the current tailored version. Use for the ATS comparison; not authoritative for facts.
4. **Historic chats** — the user's prior conversations. Use for context on preferences, recent application targets, prior framing decisions. Do NOT use historic chats as a source of CV facts that aren't in the master.
