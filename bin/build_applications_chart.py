#!/usr/bin/env python3
"""Build applications.csv and applications-chart.html from job-search folder names.

Sources:
  1. <JobSearch root>/            legacy folders, "YYYY MM DD <name>" prefix
  2. vacancies/                   in-flight applications (top-level, excludes archive/)
  3. vacancies/archive/           new slug format "Company-YYYY-MM-DD-Position"

Inputs (at repo root, optional):
  interviews.csv              folder, interview_date, note  (curated by hand)
  role_overrides.csv          folder, role                  (per-folder classifier override
                              for cases where the folder name doesn't reflect the true role)

Outputs (at repo root):
  applications.csv            date, role, source, source_folder
  applications-chart.html     self-contained interactive chart (opens in browser)

Interview detection (any one signal is sufficient):
  - `.git/` subdirectory (one convention for marking interviewed-and-committed folders)
  - filename matches transcript*, *.wav, or contains "interview" (case-insensitive)
  - application.md file exists and its content contains "interview"

Excludes: folders explicitly not-applied / on-hold / dry-run / template, meta
folders, dateless folders, non-directory entries.

Usage:
  python3 bin/build_applications_chart.py            # regenerate + open in browser
  python3 bin/build_applications_chart.py --no-open  # regenerate without opening
  python3 bin/build_applications_chart.py --quiet    # regenerate, no exclusion report
"""

import argparse
import csv
import json
import os
import re
import sys
import webbrowser
from datetime import datetime
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
JOBSEARCH_ROOT = REPO.parent          # <JobSearch>/CV-fit-automate/../  →  <JobSearch>
VACANCIES = REPO / "vacancies"
ARCHIVE = REPO / "vacancies" / "archive"

CSV_OUT = REPO / "applications.csv"
HTML_OUT = REPO / "applications-chart.html"
TEMPLATE = REPO / "bin" / "applications-chart-template.html"
INTERVIEWS_IN = REPO / "interviews.csv"
ROLE_OVERRIDES_IN = REPO / "role_overrides.csv"

# ── date extraction ─────────────────────────────────────────────────────────
DATE_DASHED = re.compile(r"(20\d{2})-(\d{2})-(\d{2})")
DATE_SPACED = re.compile(r"(20\d{2})\s+(\d{2})\s+(\d{2})")

# ── skip patterns (lowercase; matched against name.lower()) ─────────────────
SKIP_SUBSTRINGS = [
    "not applied", "did not apply", "not_applied", "on hold",
    "dont use", "template", "dry run", "scan vacancies", "discuss cv",
    "candidate examples", "salary survey", "publications", "references",
    "cv-fit-automate", "dream job", "job search 2025",
    "refocus linked", "job search refocus",
    "job search programming", "untitled folder",
    "untitled.m4a",
    # Add project-specific skip substrings here (folder-name fragments that
    # should never be counted as applications — personal residence folders,
    # placeholder names, meta folders, etc.).
]

SKIP_SUFFIXES = (".pdf", ".png", ".jpeg", ".jpg", ".gdoc", ".m4a", ".gif")

# ── role classification ─────────────────────────────────────────────────────
# Priority order: check most specific first. Names are normalized so that
# dashes and underscores are treated as spaces (matches slug-style folders).
ROLE_RULES = [
    ("Geologist", [
        r"\bgeolog", r"\bgeophys", r"\bgeomech", r"\bgeotech", r"\bgeomodel",
        r"\bpetroph", r"\breservoir", r"\bwellsite", r"\bccus\b", r"\bseismic",
        r"\bhydrolog", r"\bground water", r"\bgroundwater",
        r"\brvo geophysics", r"\bexploration team lead", r"\bres geo",
        r"\bgeo\-data\b", r"\bgeology qa\b", r"\bshell geomechanics\b",
        r"\baramco decarbonization\b", r"\bpanterra\b", r"\benergilink\b",
    ]),
    # AI Engineer = "applied engineers who assemble LLM systems" (Python + LangChain +
    # Azure + client-facing). Definition and aliases derived from an NL AI-Eng
    # job-market analysis (310 postings classified against a canonical title map).
    #
    # Title / work + domain qualifier decides:
    #   - Explicit engineering-role titles → AI Engineer regardless of domain.
    #   - Implementer-title + genai combo (DS + genai) → AI Engineer (rule from
    #     that analysis: GenAI-flavored DS is a GenAI-implementer, not a data-
    #     science role).
    #   - Management-title + genai (PM GenAI, PO GenAI) → PM/PO wins — bare `\bgenai\b`
    #     is NOT a trigger below, that would misclassify "PM GenAI".
    #   - AI Trainer is a DATA-LABELER role in the market map, NOT an engineer.
    ("AI Engineer", [
        # ── Explicit AI/ML/LLM/GenAI engineering titles ──
        r"\bai\s+eng", r"\bai\s+engineer", r"\bai\s+developer",
        r"\bai\s+architect", r"\bai\s+deployment", r"\bai\s+consultant",
        r"\bai\s+evangelist", r"\bai\s+lead\b",
        r"\bai\s+storyteller", r"\bai\s+app\s+eng", r"\bai\s+agent\b",
        r"\bai\s+product\s+builder", r"\bai\s+native\b", r"\bai\s+operator",
        r"\bai\s+acquisition", r"\bai\s+governance",
        r"\bai\s+specialist",            # per repo canonical map: "ai specialist" → "ai engineer"
        r"\bai\s+platform",              # AI Platform Engineer
        r"\bai\s+ml\s+eng",              # AI/ML Engineer (after dash normalization)
        r"\bai\s+devops",                # AI DevOps Engineer / AI-DevOps
        r"\bml\s+eng", r"\bml\s+engineer",
        r"\bllm\s+eng", r"\bllm\s+engineer",
        r"\bgenai\s+eng", r"\bgenai\s+developer",
        r"\bgenerative\s+ai\s+eng",
        # Full spellings and Dutch (per repo LANGUAGE_MAP: ingenieur ≡ engineer):
        r"\bartificial intelligence\s+eng",
        r"\bartificial intelligence\s+ingenieur",
        r"\bmachine learning\s+ingenieur",
        # ── DS + genai combo (implementer + GenAI domain = AI Engineer) ──
        r"\bds\s+genai", r"\bds\s+gen\s+ai",
        # ── Forward-deployed / customer-embedded engineering ──
        r"\bforward\s+deployed", r"\bfde\b",
        # ── Named project / product patterns that are AI-Eng-flavored ──
        r"\bcopilot studio", r"\bagentgym", r"\bnext gen ai",
        r"\bpython software engineer", r"\bdevops\s+genai",
        r"\bsolvinity\b", r"\bdura vermeer\b", r"\bconsultant\s+genai",
        r"\baiq\b", r"\bkickstart\s+ai\b",
        # ── Bare "ML" as engineering token (folder like "Remco ML") ──
        r"(?<![a-z])ml(?![a-z])",
    ]),
    ("Data Scientist", [
        r"\bdata scientist", r"\bdata science\b", r"\bdata sсience",  # cyrillic 'с' typo
        r"\bapplied scientist", r"\bdata analyst", r"\bdata engineer",
        r"\bdata specialist", r"\bml scientist", r"\bmachine learning\b",
        r"\bproduct data analyst", r"\banalytics\b",
        r"\bpm\s+ai\s+ml\b", r"\bsenior scientist", r"\bscience manager",
        r"\bresearch engineer", r"\bscientist maps", r"\bpm\s+maps\b",
        r"\bmeteorologic forecaster",
        r"(?<![a-z])ds(?![a-z])", r"(?<![a-z])da(?![a-z])",
        r"\bdsr\b", r"\brabobank ds\b", r"\bkinesso ds\b", r"\bbi\b",
        r"\bbusiness analyst\b", r"\bmanager insights\b",
        r"\bresearcher\b", r"\bresearch manager\b",
    ]),
    ("Project Manager", [
        r"\bproject manager", r"\bproject mngr", r"\bproject lead",
        r"\bproject controller", r"\bprogram manager", r"\bprogram mngr",
        r"\bprogram leader", r"\bproject/program", r"\bproject program manager",
        r"\bproject-mngr", r"\bchange manager",
        r"\bengagement lead", r"\bengagement manager",
        r"\bdelivery manager", r"\bdelivery mngr",
    ]),
    ("Product Owner", [
        r"\bproduct owner", r"\bproduct ower",     # typo variant
        r"(?<![a-z])po(?![a-z])",
    ]),
    ("Product Manager", [
        r"\bproduct manager", r"\bproductmanager",
        r"\bproduct lead", r"\bproduct leader",
        r"\bproduct engineer", r"\bproduct eng\b", r"\bproducteng\b",
        r"\bproduct evangelist", r"\bproduct analyst", r"\bproduct team analyst",
        r"\bpmngr\b", r"\bpm\b",
        r"\btechnical pm", r"\bpre sales", r"\bpresales",
        r"\bsolutions? consultant", r"\bsolutions? engineer",
        r"\bsolutions? eng\b", r"\bsolutions? architect",
        r"\bsolutions? strategist",
        r"\binnovation manager", r"\bengagement",
    ]),
]


def classify_role(name):
    normalized = re.sub(r"[-_]", " ", name).lower()
    normalized = re.sub(r"\s+", " ", normalized)
    for label, patterns in ROLE_RULES:
        for pat in patterns:
            if re.search(pat, normalized):
                return label
    return "Unknown"


def extract_date(name):
    for pattern in (DATE_DASHED, DATE_SPACED):
        m = pattern.search(name)
        if m:
            y, mo, d = m.groups()
            return f"{y}-{mo}-{d}"
    return None


def should_skip(name):
    lower = name.lower()
    if any(sub in lower for sub in SKIP_SUBSTRINGS):
        return True
    if lower.endswith(SKIP_SUFFIXES):
        return True
    if name.startswith("SCR-") or name.startswith("ai-eng-roadmap"):
        return True
    return False


INTERVIEW_FILENAME_PATTERNS = (
    re.compile(r"^transcript", re.IGNORECASE),
    re.compile(r"\.wav$", re.IGNORECASE),
    re.compile(r"interview", re.IGNORECASE),
)


def interview_signal_files(path):
    """Return list of (full_path, source) tuples for files inside `path` that
    trigger the interview signal. Empty list = no interview signal."""
    hits = []
    git_dir = path / ".git"
    if git_dir.is_dir():
        hits.append((git_dir, "git"))
    try:
        names = os.listdir(path)
    except OSError:
        return hits
    for name in names:
        full = path / name
        if not full.is_file():
            continue
        if any(p.search(name) for p in INTERVIEW_FILENAME_PATTERNS):
            hits.append((full, "filename"))
            continue
        if name == "application.md":
            try:
                if "interview" in full.read_text(encoding="utf-8", errors="replace").lower():
                    hits.append((full, "application.md content"))
            except OSError:
                pass
    return hits


def has_interview_signal(path):
    """Any of these fires → the folder reached interview stage:
      - `.git/` subdirectory (one convention for marking interviewed-and-committed folders)
      - filename matches transcript*, *.wav, or contains "interview" (case-insensitive)
      - application.md exists and its content contains "interview" (case-insensitive)
    """
    return bool(interview_signal_files(path))


def detect_interview_date(path):
    """Estimate interview date from mtime of the earliest interview-signal file.
    Prefers filename-matched files (transcript*/*.wav/*interview*) over
    application.md-content or .git/ (weaker date signals). Returns YYYY-MM-DD or None."""
    hits = interview_signal_files(path)
    if not hits:
        return None
    strong = [h for h in hits if h[1] == "filename"]
    candidates = strong if strong else hits
    mtimes = []
    for full, _ in candidates:
        try:
            mtimes.append(full.stat().st_mtime)
        except OSError:
            pass
    if not mtimes:
        return None
    return datetime.fromtimestamp(min(mtimes)).strftime("%Y-%m-%d")


# Folders that trigger a signal but aren't real interviews (tooling, templates, misc):
NOT_INTERVIEW = {
    "CV-fit-automate",
    "JobSearchInterview-template",
}


def dedupe_rows(rows):
    """Collapse cross-source duplicates and case-collisions on `source_folder`.

    Same folder can land in multiple sources when it's moved between locations
    (e.g. `<JobSearch>/` → `vacancies/archive/`, or `<JobSearch>/` + a per-vacancy
    repo under `vacancies/`). Case-collisions (Adyen-... vs adyen-...) happen when
    the Google Drive sync preserves both capitalizations.

    Keeps ONE row per canonical folder key (`source_folder.strip().lower()`),
    preferring the source with highest priority: jobsearch > vacancies > archive.
    Within a source, first-seen wins (stable given upstream sort).

    Returns (deduped_rows, dropped_rows). Callers can use `dropped_rows` for
    reporting.
    """
    priority = {"jobsearch": 0, "vacancies": 1, "archive": 2}
    by_key = {}
    dropped = []
    for r in rows:
        key = r["source_folder"].strip().lower()
        keep = by_key.get(key)
        if keep is None:
            by_key[key] = r
            continue
        # Same key already seen — pick the higher-priority (lower number) row.
        keep_prio = priority.get(keep["source"], 99)
        r_prio = priority.get(r["source"], 99)
        if r_prio < keep_prio:
            dropped.append(keep)
            by_key[key] = r
        else:
            dropped.append(r)
    return list(by_key.values()), dropped


def collect_from(directory, source_tag, skip_names=()):
    rows, excluded = [], []
    try:
        entries = sorted(os.listdir(directory))
    except OSError as e:
        print(f"WARN: cannot list {directory}: {e}", file=sys.stderr)
        return rows, excluded

    skip_set = set(skip_names)
    for name in entries:
        if name in skip_set:
            continue
        full = directory / name
        if not full.is_dir():
            continue
        stripped = name.strip()
        if should_skip(stripped):
            excluded.append((stripped, "skip-pattern", source_tag))
            continue
        date = extract_date(stripped)
        if not date:
            excluded.append((stripped, "no-date", source_tag))
            continue
        role = classify_role(stripped)
        rows.append({
            "date": date,
            "role": role,
            "source": source_tag,
            "source_folder": stripped,
            "interviewed": has_interview_signal(full) and stripped not in NOT_INTERVIEW,
            "path": full,
        })
    return rows, excluded


def write_csv(rows, path):
    rows_sorted = sorted(rows, key=lambda r: (r["date"], r["source_folder"]))
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(
            f,
            fieldnames=["date", "role", "source", "source_folder"],
            extrasaction="ignore",   # rows carry `interviewed` for in-memory use, not for CSV
        )
        w.writeheader()
        for r in rows_sorted:
            w.writerow(r)
    return rows_sorted


def load_role_overrides(path):
    """Read role_overrides.csv → {folder: role}. Missing file → {}."""
    if not path.exists():
        return {}
    out = {}
    with open(path, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            folder = (row.get("folder") or "").strip()
            role = (row.get("role") or "").strip()
            if not folder or not role:
                continue
            out[folder] = role
    return out


def apply_role_overrides(rows, overrides):
    """Overlay per-folder role overrides on top of the classifier's output.
    Prints a warning for override rows whose folder doesn't exist on disk."""
    known = {r["source_folder"] for r in rows}
    unmatched = [f for f in overrides if f not in known]
    if unmatched:
        print(f"\nWARN: {len(unmatched)} role_overrides.csv rows don't match any application folder:", file=sys.stderr)
        for f in unmatched:
            print(f"  {f}", file=sys.stderr)
    for r in rows:
        if r["source_folder"] in overrides:
            r["role"] = overrides[r["source_folder"]]


def load_interviews(path):
    """Read interviews.csv → list of dicts. Missing file → [] (interviews are optional)."""
    if not path.exists():
        return []
    out = []
    with open(path, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            folder = (row.get("folder") or "").strip()
            date = (row.get("interview_date") or "").strip()
            note = (row.get("note") or "").strip()
            if not folder or not date:
                continue
            if not DATE_DASHED.fullmatch(date):
                print(f"WARN: interviews.csv skipping malformed date '{date}' for {folder}", file=sys.stderr)
                continue
            out.append({"folder": folder, "date": date, "note": note})
    return out


def validate_interviews(interviews, app_rows):
    """Warn on interview rows whose folder doesn't match any application folder."""
    known = {r["source_folder"] for r in app_rows}
    unmatched = [iv for iv in interviews if iv["folder"] not in known]
    if unmatched:
        print(f"\nWARN: {len(unmatched)} interviews.csv rows don't match any application folder:", file=sys.stderr)
        for iv in unmatched:
            print(f"  {iv['date']}  {iv['folder']}", file=sys.stderr)


def hint_missing_interview_dates(app_rows, interviews):
    """Surface interview-signal folders (see has_interview_signal) that lack date
    rows in interviews.csv. Prints the auto-detected date (from file mtime) so
    the user can copy it into interviews.csv."""
    dated_folders = {iv["folder"] for iv in interviews}
    hints = [r for r in app_rows if r["interviewed"] and r["source_folder"] not in dated_folders]
    if not hints:
        return
    hints.sort(key=lambda r: r["date"])
    print(f"\nHint: {len(hints)} folder(s) have an interview signal but no date rows in interviews.csv:")
    for r in hints:
        detected = detect_interview_date(r["path"])
        date_str = detected if detected else f"{r['date']} (from application date)"
        print(f"  applied {r['date']}  →  interview {date_str}  {r['source_folder']}")
    print("  → Estimated dates come from earliest interview-signal file mtime. Add rows to interviews.csv to override.")


def synthesize_undated_interviews(app_rows, interviews):
    """For interview-signal folders not in interviews.csv, add a synthetic entry.
    Estimates the date from the earliest interview-signal file's mtime; falls
    back to the application date if no filesystem signal available."""
    dated_folders = {iv["folder"] for iv in interviews}
    out = list(interviews)
    for r in app_rows:
        if r["interviewed"] and r["source_folder"] not in dated_folders:
            detected = detect_interview_date(r["path"])
            if detected:
                out.append({
                    "folder": r["source_folder"],
                    "date": detected,
                    "note": "interview date estimated from file mtime",
                    "undated": False,
                })
            else:
                out.append({
                    "folder": r["source_folder"],
                    "date": r["date"],
                    "note": "interview signal detected (date not yet logged)",
                    "undated": True,
                })
    return out


def compute_role_stats(rows, interviews):
    """Per-role funnel: applications and unique folders that reached interview stage.
    Interviewed = folder is git-tracked OR appears in interviews.csv (dated or synthesized)."""
    interviewed_folders = {iv["folder"] for iv in interviews}
    stats = {}
    for r in rows:
        s = stats.setdefault(r["role"], {"applications": 0, "interviewed": 0})
        s["applications"] += 1
        if r["source_folder"] in interviewed_folders or r["interviewed"]:
            s["interviewed"] += 1
    return [{"role": role, **s} for role, s in stats.items()]


def compute_monthly_stats(rows, interviews):
    """Per-application-month funnel: how many applications sent in month X eventually
    reached the interview stage. Same 'interviewed' definition as compute_role_stats
    (git-tracked or in interviews.csv). This is cohort attribution — an app from
    January that led to a March interview counts against January, not March."""
    interviewed_folders = {iv["folder"] for iv in interviews}
    stats = {}
    for r in rows:
        month = r["date"][:7]
        s = stats.setdefault(month, {"applications": 0, "interviewed": 0})
        s["applications"] += 1
        if r["source_folder"] in interviewed_folders or r["interviewed"]:
            s["interviewed"] += 1
    return [{"month": m, **s} for m, s in sorted(stats.items())]


def write_html(rows, interviews, template_path, out_path):
    if not template_path.exists():
        raise SystemExit(f"Template not found: {template_path}")
    template = template_path.read_text()
    for token in ("__RAW_PLACEHOLDER__", "__INTERVIEWS_PLACEHOLDER__", "__ROLE_STATS_PLACEHOLDER__", "__MONTHLY_STATS_PLACEHOLDER__"):
        if token not in template:
            raise SystemExit(f"Template missing {token}: {template_path}")
    compact = [[r["date"], r["role"]] for r in rows]
    role_stats = compute_role_stats(rows, interviews)
    monthly_stats = compute_monthly_stats(rows, interviews)
    apps_payload = json.dumps(compact, separators=(",", ":"))
    intv_payload = json.dumps(interviews, separators=(",", ":"))
    stats_payload = json.dumps(role_stats, separators=(",", ":"))
    monthly_payload = json.dumps(monthly_stats, separators=(",", ":"))
    html = template.replace("__RAW_PLACEHOLDER__", apps_payload)
    html = html.replace("__INTERVIEWS_PLACEHOLDER__", intv_payload)
    html = html.replace("__ROLE_STATS_PLACEHOLDER__", stats_payload)
    html = html.replace("__MONTHLY_STATS_PLACEHOLDER__", monthly_payload)
    out_path.write_text(html)


def report(rows, interviews, excluded, quiet):
    print(f"→ {CSV_OUT.relative_to(REPO)}  ({len(rows)} rows)")
    print(f"→ {HTML_OUT.relative_to(REPO)}  (rendered from bin/applications-chart-template.html)")

    role_counts = {}
    for r in rows:
        role_counts[r["role"]] = role_counts.get(r["role"], 0) + 1
    print("\nRole counts:")
    for role, count in sorted(role_counts.items(), key=lambda x: -x[1]):
        print(f"  {role:20} {count}")

    signal_marked = sum(1 for r in rows if r["interviewed"])
    dated_interviews = sum(1 for iv in interviews if not iv.get("undated"))
    interviewed_folders = len({iv["folder"] for iv in interviews})
    print(f"\nInterviews: {signal_marked} folders with interview signal ({interviewed_folders} in interviews.csv, "
          f"{dated_interviews} dated events)")

    unknown = [r for r in rows if r["role"] == "Unknown"]
    if unknown:
        print(f"\n{len(unknown)} folders classified as Unknown (fix by hand if needed):")
        for r in unknown:
            print(f"  {r['date']}  {r['source_folder']}")

    if quiet:
        return
    print(f"\nExcluded {len(excluded)} folders (skip-pattern or no-date):")
    for name, reason, src in excluded:
        print(f"  [{reason:14}] ({src}) {name}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-open", action="store_true", help="Do not open the rendered chart in a browser.")
    parser.add_argument("--quiet", action="store_true", help="Suppress the excluded-folders list.")
    args = parser.parse_args()

    js_rows, js_excl = collect_from(JOBSEARCH_ROOT, "jobsearch")
    vc_rows, vc_excl = collect_from(VACANCIES, "vacancies", skip_names=("archive",))
    ar_rows, ar_excl = collect_from(ARCHIVE, "archive")
    rows = js_rows + vc_rows + ar_rows
    excluded = js_excl + vc_excl + ar_excl

    rows, dropped = dedupe_rows(rows)
    if dropped:
        by_src = {}
        for r in dropped:
            by_src[r["source"]] = by_src.get(r["source"], 0) + 1
        summary = ", ".join(f"{n} from {s}" for s, n in sorted(by_src.items()))
        print(f"Deduped {len(dropped)} cross-source / case-collision row(s): {summary}", file=sys.stderr)

    overrides = load_role_overrides(ROLE_OVERRIDES_IN)
    apply_role_overrides(rows, overrides)

    rows_sorted = write_csv(rows, CSV_OUT)

    interviews = load_interviews(INTERVIEWS_IN)
    validate_interviews(interviews, rows_sorted)
    interviews_full = synthesize_undated_interviews(rows_sorted, interviews)

    write_html(rows_sorted, interviews_full, TEMPLATE, HTML_OUT)
    report(rows_sorted, interviews_full, excluded, args.quiet)
    hint_missing_interview_dates(rows_sorted, interviews)

    if not args.no_open:
        webbrowser.open(f"file://{HTML_OUT}")


if __name__ == "__main__":
    main()
