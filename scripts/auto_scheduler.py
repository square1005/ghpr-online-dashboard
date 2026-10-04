"""GHPR user-session scheduler. Registration and launch are separate operations.

Publication requires the explicit --publish flag. This file alone does not
register startup entries, launch a background service, or publish anything.
User authorized implementation and automatic updates on 2026-10-04 14:34:05 UTC,
then approved tested publication and activation at 14:35:22 UTC ("可以").
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from auto_update import AlreadyRunning, RunLock, write_json

SLOT_HOURS = (3, 9, 15, 21)


def next_slot(now: datetime) -> datetime:
    if now.tzinfo is None:
        raise ValueError("Scheduler time must include a timezone")
    now = now.astimezone(timezone.utc)
    for hour in SLOT_HOURS:
        candidate = now.replace(hour=hour, minute=0, second=0, microsecond=0)
        if candidate > now:
            return candidate
    return (now + timedelta(days=1)).replace(hour=3, minute=0, second=0, microsecond=0)


def latest_due_today(now: datetime) -> datetime | None:
    if now.tzinfo is None:
        raise ValueError("Scheduler time must include a timezone")
    now = now.astimezone(timezone.utc)
    due = [now.replace(hour=h, minute=0, second=0, microsecond=0)
           for h in SLOT_HOURS if h <= now.hour]
    return due[-1] if due else None


def already_triggered(slot: datetime, last_trigger_slot: str | None) -> bool:
    if not last_trigger_slot:
        return False
    try:
        return datetime.fromisoformat(last_trigger_slot).astimezone(timezone.utc) >= slot
    except (TypeError, ValueError):
        return False


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
        try:
            previous = json.loads(status_path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            previous = {}
        now = datetime.now(timezone.utc)
        planned = next_slot(now)
        status = {
            "schema": "ghpr.user-session-scheduler.v1", "pid": os.getpid(), "enabled": True,
            "publish_enabled": publish, "started_at_utc": now.isoformat(), "last_heartbeat": now.isoformat(),
            "planned_next_run_utc": planned.isoformat(), "slots_utc": ["03:00", "09:00", "15:00", "21:00"],
            "last_trigger_slot": previous.get("last_trigger_slot"),
            "last_trigger_reason": previous.get("last_trigger_reason"),
            "last_trigger_at_utc": previous.get("last_trigger_at_utc"),
            "last_worker_exit_code": previous.get("last_worker_exit_code"),
            "last_worker_finished_at_utc": previous.get("last_worker_finished_at_utc"),
            "last_error": None, "worker_pid": None,
            "dependency": "Windows host on, Administrator user session running, network and existing Git credential manager available",
        }
        env = scheduler_env(runtime)
        worker = None
        worker_log = None
        startup = True
        try:
            while True:
                now = datetime.now(timezone.utc)
                status["last_heartbeat"] = now.isoformat()
                if worker is not None and worker.poll() is not None:
                    code = worker.returncode
                    status["last_worker_exit_code"] = code
                    status["last_worker_finished_at_utc"] = now.isoformat()
                    status["worker_pid"] = None
                    status["last_error"] = None if code == 0 else f"GHPR update exited {code}; inspect runtime/status.json and run logs"
                    worker_log.close()
                    worker_log = None
                    worker = None
                due = latest_due_today(now) if startup or now >= planned else None
                reason = "startup_catchup" if startup else "scheduled_slot"
                startup = False
                if due is not None and worker is None and not already_triggered(due, status["last_trigger_slot"]):
                    status.update({"last_trigger_slot": due.isoformat(), "last_trigger_reason": reason,
                                   "last_trigger_at_utc": now.isoformat(), "last_error": None,
                                   "trigger_delay_seconds": round((now - due).total_seconds(), 3)})
                    planned = next_slot(now)
                    status["planned_next_run_utc"] = planned.isoformat()
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
                elif now >= planned and worker is None:
                    planned = next_slot(now)
                    status["planned_next_run_utc"] = planned.isoformat()
                write_json(status_path, status)
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
