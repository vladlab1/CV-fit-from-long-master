# Delivery — surface-specific

Where the tailored CV and ATS analysis end up depends on the surface.

## Claude Code (filesystem available, slash-command driven)

- `/cv-analyse <slug>` writes the ATS analysis (Deliverable A + gap list) to `vacancies/<slug>/analysis.md`. Print a 1–2 sentence summary in chat — full content goes to the file.
- `/cv-draft <slug>` writes the tailored CV (Deliverable B) to `vacancies/<slug>/cv.md`. Print a one-line variant/bullet-count summary in chat — the full CV goes to the file.
- See `project.md` for the `vacancies/<slug>/` folder convention (one folder per application: `vacancy.md`, `analysis.md`, `cv.md`, `cv.docx`).

## Claude.ai (Claude Project / Claude Desktop / web)

- Always output the tailored CV as an **artifact** (type: text/markdown). This gives the user a dedicated readable panel with copy support, and keeps the CV separate from the surrounding analysis. Do NOT output the CV inline in the response body.
- If the surface does not support artifacts (e.g., some mobile or API contexts), fall back to rendered markdown inline — without a triple-backtick code fence, so the client renders it instead of displaying raw source.
- The ATS analysis (Deliverable A) and gap list stay in the chat response as normal prose. Only the tailored CV itself is the artifact.

## Both surfaces

- No PDF, no docx in the LLM output. The user runs `render_cv` downstream against the markdown and the fixed template (`./template.docx` at the repo root) to produce the docx.
