#!/usr/bin/env python3
"""Append one activity event to vacancies/<slug>/.activity.jsonl.

Called by bin/cv_pipeline.sh (pipeline-level events) and by
.claude/commands/*.md (in-command milestone events). Stdlib only so any
python3 on PATH works — no uv / no deps.

Usage:
    cv_log_event.py --slug <slug> --command <cmd> --phase <phase>
                    [--attempt N] [--detail '{"key":"value"}']

Fields written per line:
    ts       — ISO8601 second-precision local timestamp
    command  — e.g. "cv-analyse", "cv-draft", "cv-pipeline", "draft-critic"
    phase    — free-form; see command files for the vocabulary
    attempt  — optional, retry attempt counter from the shell wrapper
    detail   — optional, JSON object (or string fallback if not valid JSON)

Creates vacancies/<slug>/.activity.jsonl on first write; parent dir must
already exist (i.e. the slug folder itself — we don't create vacancy
folders here). Line-buffered single-write append; safe for concurrent
appenders on POSIX.
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    p.add_argument("--slug", required=True)
    p.add_argument("--command", required=True)
    p.add_argument("--phase", required=True)
    p.add_argument("--attempt", type=int, default=None)
    p.add_argument("--detail", default=None, help="JSON object as string; falls back to raw string if not valid JSON")
    args = p.parse_args()

    repo_root = Path(__file__).resolve().parent.parent
    vac_dir = repo_root / "vacancies" / args.slug
    if not vac_dir.is_dir():
        print(f"cv_log_event: vacancies/{args.slug} does not exist; refusing to create", file=sys.stderr)
        return 2

    log_path = vac_dir / ".activity.jsonl"

    event: dict = {
        "ts": datetime.now().isoformat(timespec="seconds"),
        "command": args.command,
        "phase": args.phase,
    }
    if args.attempt is not None:
        event["attempt"] = args.attempt
    if args.detail is not None:
        try:
            event["detail"] = json.loads(args.detail)
        except json.JSONDecodeError:
            event["detail"] = args.detail

    with log_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
