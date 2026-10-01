# CV-fit-from-long-master — implementation status

Last updated: 2026-10-01 (initial bootstrap)
Plan file: none
Test command: none — non-code project (one small Python renderer; no test suite yet)
Branch model: trunk

## Current focus

Fresh public template, forked from a private CV-automation repo. Not yet exercised against a real vacancy by any user other than the author.

## Next action on resume

- Edit `MASTER_CV.md` to replace the fictional "Alex Rivera" persona with your own career.
- Drop a job description into `vacancies/<company>-<YYYY-MM-DD>-<position>/vacancy.md`.
- Run `/cv-analyse <slug>` → review `analysis.md` → run `/cv-draft <slug>` → `/cv-render <slug>`.
- See `README.md` for the full workflow.

## Checklist

- [x] Repo scaffold (rules + commands + agents + renderer)
- [x] Fictional MASTER_CV.md template
- [x] `pyproject.toml` + `uv` toolchain
- [x] Example vacancy under `vacancies/example-corp-2026-01-15-product-manager/`
- [ ] First real-world run by a user other than the author

## Test status

n/a — no test suite. The renderer is validated by eye against `template.docx`.

## Notes

- The private source repo (CV-fit-automate) keeps evolving. If you ported this from there, decide whether you want to pull new rules back periodically. The rule files are the live surface; the renderer and commands drift slower.
