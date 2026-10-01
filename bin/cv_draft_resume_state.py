#!/usr/bin/env python3
"""Classify the resume state for a /cv-draft invocation.

Reads vacancies/<slug>/.activity.jsonl and the on-disk artifacts
(.critic-log.json, .critic-findings-loop-<N>.json, .cv.md.after-loop-<N>,
cv.md) to decide whether this invocation should start fresh, resume at
the critic step, resume mid-rewrite, or no-op because the last run
already completed successfully.

Prints one JSON object to stdout:
    {
      "action": "fresh_start | resume_at_critic | resume_at_rewrite | already_done",
      "resume_loop": <int or null>,
      "last_findings_path": "<path or null>",
      "reason": "<one-line summary>"
    }

Exit code 0 on success; 2 on missing slug or bad args. Never fails
with a stack trace to callers — an unparseable log falls back to
fresh_start.
"""

import argparse
import json
import sys
from pathlib import Path


def _tail_draft_events(log_path: Path) -> list[dict]:
    """Return cv-draft events from the CURRENT (most-recent) attempt.

    An 'attempt' starts at a `cv-draft phase:start` event and ends at
    the next `cv-draft phase:end` OR at end-of-file. Returns events
    from the start of the most recent unfinished attempt (inclusive)
    to end-of-file. If the last attempt ended cleanly, returns an
    empty list (fresh_start applies).
    """
    if not log_path.exists():
        return []
    events: list[dict] = []
    try:
        with log_path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    events.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    except OSError:
        return []

    # Walk backwards to find the boundaries of the last cv-draft attempt.
    # "Attempt" boundary = a `cv-draft phase:start` event. We slice from
    # the last such start onward, then check if the slice contains a
    # terminal `end` — if so, this attempt already finished.
    last_start_idx = None
    for i in range(len(events) - 1, -1, -1):
        e = events[i]
        if e.get("command") == "cv-draft" and e.get("phase") == "start":
            last_start_idx = i
            break
    if last_start_idx is None:
        return []
    tail = events[last_start_idx:]
    # If the tail contains a cv-draft `end` event, the attempt finished.
    for e in tail:
        if e.get("command") == "cv-draft" and e.get("phase") == "end":
            # Ended — but was it a success?
            result = (e.get("detail") or {}).get("result", "") if isinstance(e.get("detail"), dict) else ""
            if result == "success" or result == "noop_already_done":
                # Return empty to signal already-done handling upstream.
                return [{"__terminal__": True, "result": result}]
            # Non-success end (awaiting_user, master_defect_surfaced, forced_show_after_3_loops)
            # — treat as terminal too. Caller decides whether to no-op.
            return [{"__terminal__": True, "result": result or "unknown"}]
    return tail


def _classify(slug: str, vac_dir: Path) -> dict:
    log_path = vac_dir / ".activity.jsonl"
    critic_log_path = vac_dir / ".critic-log.json"
    cv_md_path = vac_dir / "cv.md"

    events = _tail_draft_events(log_path)

    # already_done: valid .critic-log.json + cv.md both present, and the
    # log's last cv-draft attempt terminated. This handles the case where
    # the wrapper re-invoked us after a completed run.
    if events and events[0].get("__terminal__"):
        if critic_log_path.exists() and cv_md_path.exists():
            try:
                d = json.loads(critic_log_path.read_text(encoding="utf-8"))
                if d.get("decision") in ("CLEAN", "SHOW-WITH-FLAGS", "FORCED-SHOW-AFTER-3-LOOPS"):
                    return {
                        "action": "already_done",
                        "resume_loop": None,
                        "last_findings_path": None,
                        "reason": f"last attempt ended ({events[0].get('result')}); .critic-log.json valid; cv.md present",
                    }
            except (OSError, json.JSONDecodeError):
                pass
        # Terminal but no valid critic log — fall through to fresh_start.
        return {
            "action": "fresh_start",
            "resume_loop": None,
            "last_findings_path": None,
            "reason": "prior attempt terminated but .critic-log.json missing/invalid",
        }

    # No prior attempt at all (or last one ended). Fresh start.
    if not events:
        return {
            "action": "fresh_start",
            "resume_loop": None,
            "last_findings_path": None,
            "reason": "no in-flight cv-draft attempt in .activity.jsonl",
        }

    # We have an in-flight attempt (start with no end). Determine the
    # last relevant event.
    # Filter to cv-draft events only.
    d_events = [e for e in events if e.get("command") == "cv-draft"]

    # Find last critic_invoked / critic_returned / artifact_written.
    last_ci = None  # (idx, loop)
    last_cr = None  # (idx, loop, decision)
    last_aw = None  # (idx, state)
    for i, e in enumerate(d_events):
        phase = e.get("phase")
        detail = e.get("detail") if isinstance(e.get("detail"), dict) else {}
        if phase == "critic_invoked":
            last_ci = (i, detail.get("loop"))
        elif phase == "critic_returned":
            last_cr = (i, detail.get("loop"), detail.get("decision"))
        elif phase == "artifact_written":
            last_aw = (i, detail.get("state"))

    # State machine.
    #
    # Case A: last event is `critic_invoked N` with no matching
    # `critic_returned N` → critic was killed. Re-run critic at loop N
    # on the current cv.md. cv.md is the post-loop-(N-1)-rewrite state
    # (or the initial draft if N==0), which is what the critic wants.
    if last_ci is not None:
        ci_idx, ci_loop = last_ci
        cr_matches = last_cr is not None and last_cr[0] > ci_idx and last_cr[1] == ci_loop
        if not cr_matches:
            if cv_md_path.exists():
                return {
                    "action": "resume_at_critic",
                    "resume_loop": ci_loop,
                    "last_findings_path": None,
                    "reason": f"critic_invoked loop {ci_loop} had no matching critic_returned; cv.md present, re-run critic",
                }
            # cv.md missing — can't resume-at-critic; fall through to fresh.
            return {
                "action": "fresh_start",
                "resume_loop": None,
                "last_findings_path": None,
                "reason": f"critic_invoked loop {ci_loop} in log but cv.md missing on disk",
            }

    # Case B: last critic_returned is REWRITE at loop N with no
    # subsequent critic_invoked N+1 → the drafter was killed
    # mid-rewrite (or before invoking the next critic). Resume by
    # applying the saved findings on the pre-rewrite snapshot.
    if last_cr is not None:
        cr_idx, cr_loop, cr_decision = last_cr
        ci_after = last_ci is not None and last_ci[0] > cr_idx
        if cr_decision == "REWRITE" and not ci_after:
            findings_path = vac_dir / f".critic-findings-loop-{cr_loop}.json"
            baseline_snapshot = vac_dir / f".cv.md.after-loop-{cr_loop}"
            if findings_path.exists() and cv_md_path.exists():
                # Loop about to run = cr_loop + 1
                return {
                    "action": "resume_at_rewrite",
                    "resume_loop": cr_loop + 1,
                    "last_findings_path": str(findings_path.relative_to(vac_dir.parent.parent)),
                    "reason": (
                        f"critic_returned loop {cr_loop} REWRITE; no subsequent critic_invoked; "
                        f"findings JSON present"
                        + (f"; baseline snapshot {baseline_snapshot.name} present" if baseline_snapshot.exists() else "; no baseline snapshot (will use current cv.md)")
                    ),
                }
            # Missing findings JSON — cannot deterministically resume.
            # Fall back to resume_at_critic on current cv.md so the
            # next loop's critic re-surfaces the same must-fix issues.
            if cv_md_path.exists():
                return {
                    "action": "resume_at_critic",
                    "resume_loop": cr_loop + 1,
                    "last_findings_path": None,
                    "reason": f"critic_returned loop {cr_loop} REWRITE but findings JSON missing; re-invoking critic to re-surface findings",
                }
            return {
                "action": "fresh_start",
                "resume_loop": None,
                "last_findings_path": None,
                "reason": "REWRITE decision recorded but neither findings JSON nor cv.md present",
            }
        # Case C: last critic_returned is CLEAN / SHOW-WITH-FLAGS / etc.
        # but no `end` event — the drafter died AFTER the terminal
        # decision but BEFORE writing .critic-log.json. Re-run at
        # critic (loop cr_loop) which will hit the same decision and
        # write the log this time.
        if cr_decision in ("CLEAN", "SHOW-WITH-FLAGS", "FORCED-SHOW-AFTER-3-LOOPS"):
            if cv_md_path.exists():
                return {
                    "action": "resume_at_critic",
                    "resume_loop": cr_loop,
                    "last_findings_path": None,
                    "reason": f"critic_returned loop {cr_loop} {cr_decision}; drafter died before writing .critic-log.json; re-run terminal branch",
                }

    # Case D: artifact_written but no critic_invoked yet → drafter
    # wrote cv.md then died before Step 7. Resume at critic loop 0.
    if last_aw is not None and last_ci is None:
        aw_idx, aw_state = last_aw
        if cv_md_path.exists():
            return {
                "action": "resume_at_critic",
                "resume_loop": 0,
                "last_findings_path": None,
                "reason": "artifact_written for initial draft but no critic_invoked yet; jump to Step 7 loop 0",
            }

    # Case E: only `start` (or `start` + `resumed`) — drafter died
    # mid-drafting before writing cv.md. Fresh restart of Steps 1-6.
    return {
        "action": "fresh_start",
        "resume_loop": None,
        "last_findings_path": None,
        "reason": "cv-draft start recorded but no artifact_written / critic events yet — restart drafting",
    }


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    p.add_argument("--slug", required=True)
    args = p.parse_args()

    repo_root = Path(__file__).resolve().parent.parent
    vac_dir = repo_root / "vacancies" / args.slug
    if not vac_dir.is_dir():
        print(json.dumps({
            "action": "fresh_start",
            "resume_loop": None,
            "last_findings_path": None,
            "reason": f"vacancies/{args.slug} does not exist",
        }))
        return 2

    result = _classify(args.slug, vac_dir)
    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
