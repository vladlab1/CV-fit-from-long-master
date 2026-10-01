---
description: Rebuild applications.csv from folder listings, re-render applications-chart.html, and republish the hosted artifact so the shared URL shows fresh data.
---

## What to do

1. Run the extractor from the repo root:

   ```bash
   python3 bin/build_applications_chart.py --no-open
   ```

   `--no-open` because we're refreshing the *hosted* artifact — the user will reload the shared URL, not the local file. The script:
   - scans the sibling `JobSearch/` folder tree AND `vacancies/archive/`;
   - writes `applications.csv` at the repo root;
   - re-renders `applications-chart.html` at the repo root from `bin/applications-chart-template.html`, with the fresh data inlined.

2. Surface the script's role histogram and Unknown list verbatim — new folder patterns in Unknown are the signal to extend the classifier.

3. **Republish the hosted artifact** so the shared URL reflects the new data. Use the Artifact tool:

   ```
   Artifact({
     file_path: "applications-chart.html",
     url: "https://claude.ai/code/artifact/3073cf9d-6f65-44ed-802b-bee8392186c6",
     description: "Interactive daily bar chart of the user's job applications, stacked by role.",
     favicon: "📊"
   })
   ```

   Passing `url` targets the same hosted page — the URL stays stable across regenerations. Never omit `url` in this command: without it, a fresh session mints a new URL, and the previously shared link goes stale.

4. Print the URL back to the user so he can (re-)open it.

## Interview overlay

The chart draws vertical hairlines at every interview date and top-tick markers on days where an interviewed folder appears.

**Two sources feed the overlay:**

1. **`interviews.csv`** at repo root — the user's curated log. Columns: `folder,interview_date,note`. One row per interview event; multiple events per folder = multiple rows. Dates must be `YYYY-MM-DD`. the user edits this file by hand.
2. **git-tracked application folders** in `<JobSearch>/` and `vacancies/archive/` — the user's convention is to `git init` inside an application folder once it advances to interview. The script auto-detects any `.git/` subdirectory and treats that folder as "interview happened."

**When a folder is git-tracked but has no rows in `interviews.csv`**, the script synthesizes an "undated" interview marker on the application-date column (rendered as a hollow top-tick, no vertical line). The tooltip labels them clearly. The `Hint:` block in the script's output lists these folders — invite the user to add real interview date rows.

**When `interviews.csv` references a folder that no longer exists on disk**, the script prints a `WARN:` line. the user's call whether to fix the folder path or delete the row.

## Conversion-by-role section

Below the table view sits a collapsible "Conversion by role" section (hidden by default). It shows applications, interviewed-folder count, and interview rate per role, sorted by rate. Interviewed = has `.git/` OR appears in `interviews.csv`. Server-side (Python) computes the per-role counts so the JOIN on folder name is authoritative — the HTML template just renders the passed-through JSON. Bars are scaled to the top-rate role for visual comparison.

## When Unknown count grows

If a new vacancy folder lands in Unknown and the user flags it, add its keyword pattern to `ROLE_RULES` in `bin/build_applications_chart.py`. Do NOT rename folders to fit the classifier — the classifier is the derived artefact, the folders are the source of truth.

## Constraints

- Never mint a new artifact URL for this chart. If the `url` above ever 404s (artifact deleted), stop and ask the user before publishing a new one.
- The script is idempotent — running twice produces the same output.
- `applications-chart.html` is `.gitignore`d (derived); `applications.csv` is a tracked snapshot.

## Local-browser alternative (not for this command)

If the user wants to preview locally instead of updating the hosted artifact, he can run `python3 bin/build_applications_chart.py` directly — that opens the freshly-rendered HTML in the default browser without touching the artifact URL.
