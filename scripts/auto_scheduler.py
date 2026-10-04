"""GHPR weekly user-session scheduler: Sunday 08:00 Asia/Taipei (00:00 UTC).

Publication requires the explicit --publish flag. This file alone does not
register startup entries, launch a background service, or publish anything.
User authorized implementation and automatic updates on 2026-10-04 14:34:05 UTC,
then approved tested publication and activation at 14:35:22 UTC ("可以").
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from auto_update import AlreadyRunning, RunLock, write_json

SCHEDULE_DESCRIPTION = "Every Sunday 08:00 Asia/Taipei (Sunday 00:00 UTC)"


def latest_due(now: datetime) -> datetime:
    if now.tzinfo is None:
        raise ValueError("Scheduler time must include a timezone")
    now = now.astimezone(timezone.utc)
    return (now - timedelta(days=(now.weekday() + 1) % 7)).replace(hour=0, minute=0, second=0, microsecond=0)


def next_slot(now: datetime) -> datetime:
    return latest_due(now) + timedelta(days=7)


def verified_completion(last_good: dict, now: datetime) -> dict | None:
    """A verified manual publication may satisfy its due week without relabeling it."""
    if last_good.get("status") != "success" or not last_good.get("published_commit"):
        return None
    try:
        verified = datetime.fromisoformat(last_good["publication_verified_at_utc"])
        if verified.tzinfo is None or verified > now:
            return None
        return {"week_key": latest_due(verified).date().isoformat(),
                "run_id": last_good.get("run_id"), "trigger_reason": last_good.get("trigger_reason", "unknown"),
                "published_commit": last_good["published_commit"], "verified_at_utc": verified.astimezone(timezone.utc).isoformat(),
                "kind": "existing_verified_publication"}
    except (KeyError, TypeError, ValueError):
        return None


def weekly_plan(now: datetime, previous: dict, last_good: dict, attempted_week_key: str | None = None) -> dict:
    due = latest_due(now)
    week_key = due.date().isoformat()
    completed = previous.get("last_completed_week_key")
    evidence = previous.get("completion_evidence")
    verified = verified_completion(last_good, now)
    if verified and (not completed or verified["week_key"] >= completed):
        completed, evidence = verified["week_key"], verified
    done = bool(completed and completed >= week_key)
    should_run = not done and attempted_week_key != week_key
    return {"due": due, "week_key": week_key, "should_run": should_run,
            "planned_next_run_utc": (due if should_run else next_slot(now)).isoformat(),
            "last_completed_week_key": completed, "completion_evidence": evidence}


def read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def scheduler_env(runtime: Path) -> dict:
    temporary = runtime / "scheduler-tmp"
    temporary.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env.update({"TMP": str(temporary), "TEMP": str(temporary), "TMPDIR": str(temporary),
                "PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8", "PYTHONDONTWRITEBYTECODE": "1",
                "MPLCONFIGDIR": str(temporary / "matplotlib"), "XDG_CACHE_HOME": str(temporary / "cache"),
                "GIT_TERMINAL_PROMPT": "0", "GCM_INTERACTIVE": "Never"})
    return env


def run_scheduler(config_path: Path, publish: bool = False) -> int:
    config_path = config_path.resolve()
    config = json.loads(config_path.read_text(encoding="utf-8-sig"))
    runtime = Path(config["runtime_root"]).resolve()
    repo = Path(config["source_repo"]).resolve()
    if os.name == "nt" and (runtime.drive.upper() != "D:" or repo.drive.upper() != "D:"):
        raise ValueError("GHPR source/runtime must remain on D:")
    runtime.mkdir(parents=True, exist_ok=True)
    status_path = runtime / "scheduler-status.json"
    with RunLock(runtime / "supervisor.lock"):
        previous = read_json(status_path)
        now = datetime.now(timezone.utc)
        initial = weekly_plan(now, previous, read_json(runtime / "last_good.json"))
        status = {
            "schema": "ghpr.weekly-user-session-scheduler.v2", "pid": os.getpid(), "enabled": True,
            "publish_enabled": publish, "started_at_utc": now.isoformat(), "last_heartbeat": now.isoformat(),
            "scheduler_code_sha256_at_start": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "update_entrypoint_sha256_at_start": hashlib.sha256((repo / "scripts/auto_update.py").read_bytes()).hexdigest(),
            "planned_next_run_utc": initial["planned_next_run_utc"], "schedule": SCHEDULE_DESCRIPTION,
            "schedule_timezone": "Asia/Taipei", "weekly_due_weekday_utc": "Sunday", "weekly_due_time_utc": "00:00",
            "last_completed_week_key": initial["last_completed_week_key"], "completion_evidence": initial["completion_evidence"],
            "last_trigger_slot": previous.get("last_trigger_slot"),
            "last_trigger_reason": previous.get("last_trigger_reason"),
            "last_trigger_at_utc": previous.get("last_trigger_at_utc"),
            "last_worker_exit_code": previous.get("last_worker_exit_code"),
            "last_worker_finished_at_utc": previous.get("last_worker_finished_at_utc"),
            "last_error": previous.get("last_error"), "worker_pid": None,
            "retry_policy": "One attempt per due week in this session; an unsuccessful due week is retried on next login. Successful weeks are not repeated.",
            "dependency": "Windows host on, Administrator user session running, network and existing Git credential manager available",
        }
        env = scheduler_env(runtime)
        worker = None
        worker_log = None
        startup = True
        attempted_week_key = None
        worker_week_key = None
        try:
            while True:
                now = datetime.now(timezone.utc)
                status["last_heartbeat"] = now.isoformat()
                plan = weekly_plan(now, status, read_json(runtime / "last_good.json"), attempted_week_key)
                status["last_completed_week_key"] = plan["last_completed_week_key"]
                status["completion_evidence"] = plan["completion_evidence"]
                status["planned_next_run_utc"] = plan["planned_next_run_utc"]
                evidence = plan["completion_evidence"] or {}
                status["last_success_at_utc"] = evidence.get("verified_at_utc")
                status["last_success_run_id"] = evidence.get("run_id")
                status["last_success_trigger_reason"] = evidence.get("trigger_reason")
                if worker is not None and worker.poll() is not None:
                    code = worker.returncode
                    status["last_worker_exit_code"] = code
                    status["last_worker_finished_at_utc"] = now.isoformat()
                    status["worker_pid"] = None
                    completed = plan["last_completed_week_key"]
                    verified_week = bool(worker_week_key and completed and completed >= worker_week_key)
                    status["last_error"] = None if code == 0 and verified_week else (
                        f"GHPR update exited {code}; this week's publication is not verified. Inspect runtime/status.json and run logs")
                    worker_log.close()
                    worker_log = None
                    worker = None
                reason = "startup_catchup" if startup else "scheduled_slot"
                startup = False
                if plan["should_run"] and worker is None:
                    due = plan["due"]
                    attempted_week_key = worker_week_key = plan["week_key"]
                    status.update({"last_trigger_slot": due.isoformat(), "last_trigger_reason": reason,
                                   "last_trigger_at_utc": now.isoformat(), "last_error": None,
                                   "last_attempted_week_key": attempted_week_key,
                                   "trigger_delay_seconds": round((now - due).total_seconds(), 3)})
                    status["planned_next_run_utc"] = next_slot(now).isoformat()
                    write_json(status_path, status)
                    try:
                        log_dir = runtime / "scheduler-logs"
                        log_dir.mkdir(parents=True, exist_ok=True)
                        log_path = log_dir / (due.strftime("%Y%m%dT%H%M%SZ") + ".log")
                        worker_log = log_path.open("a", encoding="utf-8")
                        worker_log.write(f"\nTrigger {reason} at {now.isoformat()} for slot {due.isoformat()}\n")
                        worker_log.flush()
                        worker_env = env.copy()
                        worker_env["GHPR_SCHEDULER_TRIGGER_REASON"] = reason
                        worker_env["GHPR_SCHEDULER_SLOT_UTC"] = due.isoformat()
                        command = [config.get("python", sys.executable), "-B", str(repo / "scripts/auto_update.py"),
                                   "--config", str(config_path), "--scheduled"]
                        if publish:
                            command.append("--publish")
                        worker = subprocess.Popen(command, cwd=repo, env=worker_env, stdin=subprocess.DEVNULL,
                                                  stdout=worker_log, stderr=subprocess.STDOUT,
                                                  creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
                        status["worker_pid"] = worker.pid
                        status["worker_log"] = str(log_path)
                    except Exception as exc:
                        status["last_error"] = f"{type(exc).__name__}: {exc}"
                        if worker_log is not None:
                            worker_log.close()
                            worker_log = None
                write_json(status_path, status)
                planned = datetime.fromisoformat(status["planned_next_run_utc"])
                delay = 30.0 if worker is not None else min(30.0, (planned - datetime.now(timezone.utc)).total_seconds())
                time.sleep(max(0.1, delay))
        except KeyboardInterrupt:
            status.update({"enabled": False, "last_heartbeat": datetime.now(timezone.utc).isoformat(),
                           "last_error": "Supervisor interrupted; any existing update worker was left running"})
            write_json(status_path, status)
            return 0
        except Exception as exc:
            status.update({"enabled": False, "last_heartbeat": datetime.now(timezone.utc).isoformat(),
                           "last_error": f"{type(exc).__name__}: {exc}"})
            write_json(status_path, status)
            raise
        finally:
            if worker_log is not None:
                worker_log.close()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--publish", action="store_true", help="Enable the previously authorized GitHub publication")
    args = parser.parse_args(argv)
    try:
        return run_scheduler(args.config, publish=args.publish)
    except AlreadyRunning:
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
