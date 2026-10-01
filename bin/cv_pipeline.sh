#!/usr/bin/env bash
# bin/cv_pipeline.sh — resilient retry engine for the CV pipeline.
#
# Runs /cv-analyse and /cv-draft as fresh `claude -p` subprocesses. Each
# subprocess is streamed line-by-line so the wrapper can react to two
# signals in real time:
#
#   1. Anthropic session/usage limit hit ("You've hit your session limit
#      · resets 7:20pm (Europe/Amsterdam)"). The wrapper parses the reset
#      time, kills the subprocess, sleeps until reset + buffer, then
#      re-spawns. No retry slot is consumed.
#
#   2. Silence watchdog. If the subprocess emits no output for
#      SILENCE_SEC seconds (default 480 = 8 min), it is presumed stuck.
#      Killed and re-spawned; a retry slot IS consumed.
#
# The wrapper is stateless. Every re-spawn is `claude -p '/cv-<step>
# <slug>'` — the slash command reads .activity.jsonl on start and
# resumes from wherever the last run died (drafter side — see
# .claude/commands/cv-draft.md, Step 0).
#
# Usage:
#   bin/cv_pipeline.sh --slug <slug> [--steps analyse|draft|both]
#                      [--silence-sec N] [--max-retries N]
#                      [--rate-limit-buffer-sec N]
#
# Defaults: --steps both, --silence-sec 480, --max-retries 10,
#           --rate-limit-buffer-sec 120.
#
# Exit codes:
#   0 — all requested steps produced valid artifacts
#   1 — a step failed after all retries
#   2 — invalid usage / environment

set -u
set -o pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
LOG_HELPER="$SCRIPT_DIR/cv_log_event.py"

SLUG=""
STEPS="both"
SILENCE_SEC=480
MAX_RETRIES=10
RATE_LIMIT_BUFFER_SEC=120

usage() {
  cat >&2 <<EOF
Usage: $(basename "$0") --slug <slug> [--steps analyse|draft|both]
                       [--silence-sec N] [--max-retries N]
                       [--rate-limit-buffer-sec N]

Streams claude -p line-by-line. Auto-pauses on Anthropic rate limits
(parsed from stderr) and resumes at the announced reset time. Kills
stuck subprocesses (no output for --silence-sec).

Defaults: --steps both, --silence-sec 480, --max-retries 10,
          --rate-limit-buffer-sec 120.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --slug) SLUG="$2"; shift 2 ;;
    --steps) STEPS="$2"; shift 2 ;;
    --silence-sec) SILENCE_SEC="$2"; shift 2 ;;
    --max-retries) MAX_RETRIES="$2"; shift 2 ;;
    --rate-limit-buffer-sec) RATE_LIMIT_BUFFER_SEC="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown arg: $1" >&2; usage; exit 2 ;;
  esac
done

[[ -z "$SLUG" ]] && { echo "ERROR: --slug required" >&2; usage; exit 2; }
case "$STEPS" in analyse|draft|both) ;; *) echo "ERROR: --steps must be one of: analyse, draft, both (got: $STEPS)" >&2; exit 2 ;; esac
[[ "$SILENCE_SEC" =~ ^[0-9]+$ ]] || { echo "ERROR: --silence-sec must be a positive integer" >&2; exit 2; }
[[ "$MAX_RETRIES" =~ ^[0-9]+$ ]] || { echo "ERROR: --max-retries must be a non-negative integer" >&2; exit 2; }
[[ "$RATE_LIMIT_BUFFER_SEC" =~ ^[0-9]+$ ]] || { echo "ERROR: --rate-limit-buffer-sec must be a non-negative integer" >&2; exit 2; }

VAC_DIR="$REPO_ROOT/vacancies/$SLUG"
[[ ! -d "$VAC_DIR" ]] && { echo "ERROR: $VAC_DIR does not exist" >&2; exit 2; }
[[ ! -f "$VAC_DIR/vacancy.md" ]] && { echo "ERROR: $VAC_DIR/vacancy.md missing — drop the JD in first" >&2; exit 2; }
command -v claude >/dev/null 2>&1 || { echo "ERROR: 'claude' CLI not on PATH" >&2; exit 2; }
command -v python3 >/dev/null 2>&1 || { echo "ERROR: 'python3' not on PATH" >&2; exit 2; }

LOGS_DIR="$VAC_DIR/.logs"
mkdir -p "$LOGS_DIR"

log_event() {
  # log_event <command> <phase> [attempt] [detail-json]
  local cmd="$1" phase="$2" attempt="${3:-}" detail="${4:-}"
  local args=(--slug "$SLUG" --command "$cmd" --phase "$phase")
  [[ -n "$attempt" ]] && args+=(--attempt "$attempt")
  [[ -n "$detail" ]] && args+=(--detail "$detail")
  python3 "$LOG_HELPER" "${args[@]}" 2>/dev/null || true
}

verify_analyse() {
  local f="$VAC_DIR/analysis.md"
  local ok=1
  if [[ ! -f "$f" ]]; then
    echo "  x analysis.md missing" >&2; ok=0
  else
    local sz
    sz=$(wc -c <"$f" | tr -d ' ')
    if [[ $sz -lt 500 ]]; then
      echo "  x analysis.md too small ($sz bytes, need >=500)" >&2; ok=0
    fi
    if ! grep -q "Company product context" "$f"; then
      echo "  x analysis.md missing '## Company product context' heading (iter #15)" >&2; ok=0
    fi
    if ! grep -qi "gap list" "$f"; then
      echo "  x analysis.md missing gap-list marker" >&2; ok=0
    fi
  fi
  [[ $ok -eq 1 ]]
}

verify_draft() {
  local cv="$VAC_DIR/cv.md"
  local log="$VAC_DIR/.critic-log.json"
  local ok=1
  if [[ ! -f "$cv" ]]; then
    echo "  x cv.md missing" >&2; ok=0
  else
    local sz
    sz=$(wc -c <"$cv" | tr -d ' ')
    if [[ $sz -lt 1000 ]]; then
      echo "  x cv.md too small ($sz bytes, need >=1000)" >&2; ok=0
    fi
  fi
  if [[ ! -f "$log" ]]; then
    echo "  x .critic-log.json missing (critique gate skipped?)" >&2; ok=0
  else
    local py_out py_rc
    py_out=$(python3 - "$log" 2>&1 <<'PYEOF'
import json, sys
try:
    d = json.load(open(sys.argv[1]))
except Exception as e:
    print(f".critic-log.json not valid JSON: {e}"); sys.exit(1)
if d.get("decision") not in ("CLEAN", "SHOW-WITH-FLAGS", "FORCED-SHOW-AFTER-3-LOOPS"):
    print(f".critic-log.json decision invalid: {d.get('decision')!r}"); sys.exit(1)
if not isinstance(d.get("rewrite_loops"), int):
    print(f".critic-log.json rewrite_loops not int: {d.get('rewrite_loops')!r}"); sys.exit(1)
PYEOF
)
    py_rc=$?
    if [[ $py_rc -ne 0 ]]; then
      echo "  x $py_out" >&2; ok=0
    fi
  fi
  [[ $ok -eq 1 ]]
}

# spawn_and_watch runs one `claude -p '/cv-<step> <slug>'` invocation
# with streaming and returns one of:
#   0 — subprocess exited 0
#   1 — subprocess exited non-zero (real error, not rate-limit)
#   3 — rate limit hit, subprocess killed; wrapper should sleep until
#        the reset time recorded in $RATE_LIMIT_RESUME_AT (unix epoch)
#   4 — silence watchdog fired, subprocess killed
#
# stdout+stderr of the subprocess are streamed to $out_log AND scanned
# for the rate-limit and silence signals. The subprocess is launched
# via `setsid` (via python) so we can kill the whole process group.
RATE_LIMIT_RESUME_AT=""

spawn_and_watch() {
  local step="$1" attempt="$2" out_log="$3"

  # Clear the sentinel; only the rate-limit branch sets it.
  RATE_LIMIT_RESUME_AT=""

  # Truncate the per-attempt log.
  : > "$out_log"

  # Pipe FD for claude's merged stdout+stderr. We use a FIFO so we can
  # read line-by-line while the subprocess writes freely.
  local fifo="$LOGS_DIR/.stream-$$-$step-$attempt.fifo"
  rm -f "$fifo"
  mkfifo "$fifo"

  # Launch claude in its own process group via python setsid, so we
  # can kill the whole group if we detect a rate limit or silence.
  local pid
  python3 -c "
import os, sys, subprocess
os.setsid()
p = subprocess.Popen(['claude', '-p', '/cv-${step} ${SLUG}'],
                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                    bufsize=1, text=True)
# Print our PGID (== our own PID after setsid) so the parent can kill us.
sys.stderr.write(f'__PGID__={os.getpid()}\n')
sys.stderr.flush()
try:
    for line in p.stdout:
        sys.stdout.write(line)
        sys.stdout.flush()
finally:
    p.wait()
    sys.exit(p.returncode)
" >"$fifo" 2>&1 &
  pid=$!

  # Reader loop: read lines from FIFO, scan each, honor silence timeout.
  local pgid=""
  local last_line_ts
  last_line_ts=$(date +%s)
  local rate_limited=0
  local watchdog_fired=0

  # Open FIFO for reading via FD 3.
  exec 3<"$fifo"

  while true; do
    local now
    now=$(date +%s)

    # Silence check.
    local elapsed=$((now - last_line_ts))
    if [[ $elapsed -ge $SILENCE_SEC ]]; then
      echo "  ! silence watchdog fired: no output for ${elapsed}s (limit ${SILENCE_SEC}s)" >&2
      watchdog_fired=1
      break
    fi

    # Read one line with a 5s timeout so we can re-check silence + child status.
    local line read_rc
    IFS= read -r -t 5 line <&3
    read_rc=$?

    if [[ $read_rc -eq 0 ]]; then
      last_line_ts=$(date +%s)
      # Persist to per-attempt log AND echo to our stderr (visible to the user).
      printf '%s\n' "$line" >>"$out_log"
      printf '%s\n' "$line" >&2

      # Capture PGID marker.
      if [[ -z "$pgid" && "$line" == __PGID__=* ]]; then
        pgid="${line#__PGID__=}"
        continue
      fi

      # Rate-limit detection.
      if _match_rate_limit "$line"; then
        # _match_rate_limit sets RATE_LIMIT_RESUME_AT if it can parse.
        rate_limited=1
        break
      fi
    elif [[ $read_rc -gt 128 ]]; then
      # Timeout on read (no line in 5s). Loop re-checks silence + child status.
      :
    else
      # EOF (read_rc == 1) or other error — subprocess closed its output.
      break
    fi
  done

  exec 3<&-

  # If we broke out due to rate-limit or watchdog, kill the process group.
  if [[ $rate_limited -eq 1 || $watchdog_fired -eq 1 ]]; then
    if [[ -n "$pgid" ]]; then
      kill -TERM -"$pgid" 2>/dev/null || true
      sleep 2
      kill -KILL -"$pgid" 2>/dev/null || true
    else
      kill -TERM "$pid" 2>/dev/null || true
      sleep 2
      kill -KILL "$pid" 2>/dev/null || true
    fi
  fi

  # Reap the wrapper python.
  wait "$pid" 2>/dev/null
  local wrapper_rc=$?

  rm -f "$fifo"

  if [[ $rate_limited -eq 1 ]]; then
    return 3
  fi
  if [[ $watchdog_fired -eq 1 ]]; then
    return 4
  fi
  # Normal exit — propagate the subprocess exit code as 0 or 1.
  if [[ $wrapper_rc -eq 0 ]]; then
    return 0
  fi
  return 1
}

# _match_rate_limit <line>
# Returns 0 (true) if the line looks like an Anthropic rate-limit
# message and sets RATE_LIMIT_RESUME_AT to a unix epoch. Non-zero
# otherwise. Falls back to a 60-min pause if the time cannot be parsed.
_match_rate_limit() {
  local line="$1"
  # Fast path: require a LIMIT phrase AND a TIME phrase in the same
  # line. Either alone (e.g. a log message that mentions "rate limit"
  # without a reset time) is not enough — that produced false positives.
  local ll="${line,,}"  # lowercase (bash 4+)
  local has_limit=0 has_time=0
  case "$ll" in
    *"session limit"*|*"usage limit"*|*"rate limit"*|*"limit reached"*|*"limit hit"*)
      has_limit=1 ;;
  esac
  case "$ll" in
    *"resets"*|*"try again"*|*"retry after"*|*"retry in"*)
      has_time=1 ;;
  esac
  if [[ $has_limit -eq 0 || $has_time -eq 0 ]]; then
    return 1
  fi
  # Try to parse a reset time out of the line. Delegate to python for
  # robustness (dateparser-style handling with stdlib only).
  local parsed
  parsed=$(python3 - "$line" <<'PYEOF'
import sys, re
from datetime import datetime, timedelta, timezone
try:
    from zoneinfo import ZoneInfo
except ImportError:
    ZoneInfo = None

line = sys.argv[1]

# Patterns observed so far:
#   "You've hit your session limit · resets 7:20pm (Europe/Amsterdam)"
#   "Claude AI usage limit reached · Try again at Nov 5, 2:00 PM"
#   "Please try again in 3 hours"
#   "resets at 19:20"
now = datetime.now().astimezone()

def _apply_tz(dt, tzname):
    if not tzname:
        return dt.replace(tzinfo=now.tzinfo) if dt.tzinfo is None else dt
    if ZoneInfo is None:
        return dt.replace(tzinfo=now.tzinfo) if dt.tzinfo is None else dt
    try:
        return dt.replace(tzinfo=ZoneInfo(tzname))
    except Exception:
        return dt.replace(tzinfo=now.tzinfo) if dt.tzinfo is None else dt

# Pattern A: "resets <H>[:<M>][am|pm] (<TZ>)"
m = re.search(r'resets(?:\s+at)?\s+(\d{1,2})(?::(\d{2}))?\s*([ap]m|AM|PM)?(?:\s*\(([A-Za-z/_+\-]+)\))?', line)
if m:
    hh = int(m.group(1))
    mm = int(m.group(2) or 0)
    ampm = (m.group(3) or "").lower()
    tzname = m.group(4)
    if ampm == "pm" and hh < 12:
        hh += 12
    if ampm == "am" and hh == 12:
        hh = 0
    target = now.replace(hour=hh, minute=mm, second=0, microsecond=0)
    target = _apply_tz(target, tzname)
    now_in_tz = now.astimezone(target.tzinfo) if target.tzinfo else now
    if target <= now_in_tz:
        target = target + timedelta(days=1)
    print(int(target.timestamp()))
    sys.exit(0)

# Pattern B: "try again in <N> (hour|hours|minute|minutes)"
m = re.search(r'try again in\s+(\d+)\s*(hour|hours|minute|minutes|min|mins|hr|hrs)', line, re.IGNORECASE)
if m:
    n = int(m.group(1))
    unit = m.group(2).lower()
    if unit.startswith('h'):
        delta = timedelta(hours=n)
    else:
        delta = timedelta(minutes=n)
    print(int((now + delta).timestamp()))
    sys.exit(0)

# Pattern C: "Try again at <Month> <day>, <H>:<M> [AM|PM]"
m = re.search(r'[Tt]ry again at\s+([A-Za-z]{3,9})\s+(\d{1,2}),\s*(\d{1,2}):(\d{2})\s*([AP]M)?', line)
if m:
    months = {"jan":1,"feb":2,"mar":3,"apr":4,"may":5,"jun":6,"jul":7,"aug":8,"sep":9,"oct":10,"nov":11,"dec":12}
    mo = months.get(m.group(1).lower()[:3])
    day = int(m.group(2))
    hh = int(m.group(3))
    mm = int(m.group(4))
    ampm = (m.group(5) or "").lower()
    if ampm == "pm" and hh < 12: hh += 12
    if ampm == "am" and hh == 12: hh = 0
    if mo:
        year = now.year
        target = datetime(year, mo, day, hh, mm, tzinfo=now.tzinfo)
        if target <= now:
            target = target.replace(year=year + 1)
        print(int(target.timestamp()))
        sys.exit(0)

# Fallback: unknown format.
sys.exit(1)
PYEOF
)
  local rc=$?
  if [[ $rc -eq 0 && -n "$parsed" ]]; then
    RATE_LIMIT_RESUME_AT="$parsed"
    return 0
  fi
  # Fallback: 60-min pause.
  RATE_LIMIT_RESUME_AT=$(( $(date +%s) + 3600 ))
  return 0
}

_sleep_until_rate_limit_resume() {
  local resume_at="$1"
  local now target_secs total_wait
  now=$(date +%s)
  target_secs=$(( resume_at + RATE_LIMIT_BUFFER_SEC ))
  total_wait=$(( target_secs - now ))
  if [[ $total_wait -le 0 ]]; then
    return 0
  fi
  local human_target
  human_target=$(python3 -c "
import sys
from datetime import datetime
ts = int(sys.argv[1])
print(datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S %Z').strip())
" "$target_secs" 2>/dev/null || echo "$target_secs")
  echo "  ! rate limit hit; sleeping ${total_wait}s (until ${human_target}, +${RATE_LIMIT_BUFFER_SEC}s buffer)" >&2

  # Sleep in short slices so Ctrl-C is responsive and we can print
  # periodic progress every ~5 min.
  local elapsed=0
  local slice=60
  while [[ $elapsed -lt $total_wait ]]; do
    local remaining=$(( total_wait - elapsed ))
    if [[ $remaining -lt $slice ]]; then
      slice=$remaining
    fi
    sleep "$slice"
    elapsed=$(( elapsed + slice ))
    if [[ $(( elapsed % 300 )) -eq 0 && $elapsed -gt 0 && $remaining -gt 60 ]]; then
      echo "    ... $(( total_wait - elapsed ))s remaining" >&2
    fi
  done
}

run_step() {
  local step="$1"
  local verify_fn="verify_$step"
  local attempt=1
  local total_attempts=$(( MAX_RETRIES + 1 ))

  while [[ $attempt -le $total_attempts ]]; do
    local out_log="$LOGS_DIR/$step-attempt-$attempt.log"
    echo "[$(date +%H:%M:%S)] /cv-$step attempt $attempt/$total_attempts (silence limit ${SILENCE_SEC}s) -> $out_log" >&2
    log_event "cv-$step" "attempt_start" "$attempt" "{\"silence_sec\":$SILENCE_SEC}"

    local start_ts end_ts duration
    start_ts=$(date +%s)
    set +e
    spawn_and_watch "$step" "$attempt" "$out_log"
    local rc=$?
    set -e 2>/dev/null || true
    end_ts=$(date +%s)
    duration=$(( end_ts - start_ts ))

    case "$rc" in
      0)
        log_event "cv-$step" "attempt_end" "$attempt" "{\"exit_code\":0,\"duration_sec\":$duration}"
        echo "  exit=0 duration=${duration}s" >&2
        ;;
      1)
        log_event "cv-$step" "attempt_end" "$attempt" "{\"exit_code\":1,\"duration_sec\":$duration}"
        echo "  exit=1 duration=${duration}s (subprocess error)" >&2
        ;;
      3)
        log_event "cv-$step" "rate_limited_pause" "$attempt" "{\"duration_sec\":$duration,\"resume_at\":$RATE_LIMIT_RESUME_AT}"
        echo "  rate limit hit (subprocess killed) duration=${duration}s resume_at=$RATE_LIMIT_RESUME_AT" >&2
        _sleep_until_rate_limit_resume "$RATE_LIMIT_RESUME_AT"
        log_event "cv-$step" "rate_limited_resumed" "$attempt"
        # Rate-limit pauses do NOT consume a retry slot.
        continue
        ;;
      4)
        log_event "cv-$step" "silence_watchdog" "$attempt" "{\"duration_sec\":$duration,\"silence_sec\":$SILENCE_SEC}"
        echo "  silence watchdog killed subprocess duration=${duration}s" >&2
        ;;
      *)
        log_event "cv-$step" "attempt_end" "$attempt" "{\"exit_code\":$rc,\"duration_sec\":$duration}"
        echo "  exit=$rc duration=${duration}s (unexpected)" >&2
        ;;
    esac

    echo "[$(date +%H:%M:%S)] verifying /cv-$step artifacts..." >&2
    if $verify_fn; then
      log_event "cv-$step" "artifact_check" "$attempt" "{\"result\":\"pass\"}"
      echo "  ok" >&2
      return 0
    else
      log_event "cv-$step" "artifact_check" "$attempt" "{\"result\":\"fail\"}"
      if [[ $attempt -lt $total_attempts ]]; then
        echo "  retrying (next attempt $((attempt + 1))/$total_attempts) — drafter will read .activity.jsonl and resume" >&2
        log_event "cv-$step" "retry" "$attempt"
      fi
    fi

    attempt=$(( attempt + 1 ))
  done

  echo "  /cv-$step failed after $total_attempts attempts. See $LOGS_DIR/$step-attempt-*.log" >&2
  log_event "cv-$step" "step_failed" $(( attempt - 1 ))
  return 1
}

log_event "cv-pipeline" "start" "" "{\"steps\":\"$STEPS\",\"silence_sec\":$SILENCE_SEC,\"max_retries\":$MAX_RETRIES,\"rate_limit_buffer_sec\":$RATE_LIMIT_BUFFER_SEC}"
echo "[$(date +%H:%M:%S)] cv-pipeline start: slug=$SLUG steps=$STEPS silence=${SILENCE_SEC}s max_retries=$MAX_RETRIES rate_limit_buffer=${RATE_LIMIT_BUFFER_SEC}s" >&2

if [[ "$STEPS" == "analyse" || "$STEPS" == "both" ]]; then
  if ! run_step "analyse"; then
    log_event "cv-pipeline" "end" "" "{\"result\":\"failed_at_analyse\"}"
    exit 1
  fi
fi

if [[ "$STEPS" == "draft" || "$STEPS" == "both" ]]; then
  if ! run_step "draft"; then
    log_event "cv-pipeline" "end" "" "{\"result\":\"failed_at_draft\"}"
    exit 1
  fi
fi

log_event "cv-pipeline" "end" "" "{\"result\":\"success\"}"
echo "[$(date +%H:%M:%S)] cv-pipeline done" >&2
exit 0
