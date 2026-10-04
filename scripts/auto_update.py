"""Isolated, locked GHPR refresh and optional publication to its existing repo.

No credentials are created. Use --publish only after the existing repository and
its configured Git credential manager have been approved for unattended use.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from uuid import uuid4

PUBLISH_PATHS = ("data/processed", "outputs/reports", "web-data")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    temporary.replace(path)


class AlreadyRunning(RuntimeError):
    pass


class RunLock:
    """OS-backed lock, automatically released after a killed/crashed process."""
    def __init__(self, path: Path):
        self.path = path
        self.handle = None

    def __enter__(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.handle = self.path.open("a+b")
        try:
            self.handle.seek(0, os.SEEK_END)
            if self.handle.tell() == 0:
                self.handle.write(b"0")
                self.handle.flush()
            self.handle.seek(0)
            if os.name == "nt":
                import msvcrt
                msvcrt.locking(self.handle.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(self.handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except (OSError, BlockingIOError) as exc:
            self.handle.close()
            self.handle = None
            raise AlreadyRunning("Another GHPR update owns this runtime lock") from exc
        return self

    def __exit__(self, *_):
        if self.handle:
            self.handle.close()


def execute(command: list[str], cwd: Path, env: dict, log: Path, timeout: int = 1800) -> str:
    result = subprocess.run(command, cwd=cwd, env=env, capture_output=True,
                            text=True, encoding="utf-8", errors="replace", timeout=timeout)
    with log.open("a", encoding="utf-8") as output:
        output.write(f"\n[{utc_now()}] {json.dumps(command)}\n{result.stdout}\n{result.stderr}\nexit={result.returncode}\n")
    if result.returncode:
        raise RuntimeError(f"Command failed with exit {result.returncode}: {command[0]} {command[1] if len(command) > 1 else ''}; see {log.name}")
    return result.stdout.strip()


def validated_release(stage: Path) -> dict:
    web = stage / "web-data"
    manifest = json.loads((web / "manifest.json").read_text(encoding="utf-8"))
    for key in ("bundle", "outcomes", "status"):
        item = manifest["files"][key]
        path = (web / item["path"]).resolve()
        if not path.is_relative_to(web.resolve()) or not path.is_file():
            raise ValueError(f"Invalid release file path: {key}")
        if hashlib.sha256(path.read_bytes()).hexdigest() != item["sha256"]:
            raise ValueError(f"Release hash mismatch: {key}")
    return manifest


def publish_files(repo: Path, stage: Path, env: dict, log: Path, run_id: str, status_only: bool = False) -> str:
    # Refuse to mix an operator's uncommitted changes into an automated release.
    dirty = execute(["git", "status", "--porcelain", "--untracked-files=no"], repo, env, log)
    if dirty:
        raise RuntimeError("GHPR repository has uncommitted tracked changes; publication deferred")
    branch = execute(["git", "branch", "--show-current"], repo, env, log)
    if branch != "main":
        raise RuntimeError("GHPR publication requires its main branch")
    if status_only:
        for name in ("manifest.json", "update-status.json"):
            target = repo / "web-data" / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(stage / "web-data" / name, target)
        paths = ["web-data/manifest.json", "web-data/update-status.json"]
    else:
        for relative in PUBLISH_PATHS:
            src, dst = stage / relative, repo / relative
            if src.exists():
                shutil.copytree(src, dst, dirs_exist_ok=True)
        paths = list(PUBLISH_PATHS)
    execute(["git", "add", "-f", "--", *paths], repo, env, log)
    changed = execute(["git", "diff", "--cached", "--name-only"], repo, env, log)
    if changed:
        # No caller-supplied shell text or credentials appear in this command.
        execute(["git", "commit", "-m", f"GHPR automated {'status' if status_only else 'data'} update {run_id}"], repo, env, log)
    commit = execute(["git", "rev-parse", "HEAD"], repo, env, log)
    execute(["git", "push", "origin", "HEAD:main"], repo, env, log)
    remote = execute(["git", "ls-remote", "origin", "refs/heads/main"], repo, env, log)
    if not remote or remote.split()[0] != commit:
        raise RuntimeError("GitHub main did not read back the pushed release commit")
    return commit


def failure_release(repo: Path, stage: Path, status: dict) -> bool:
    source = repo / "web-data"
    if not (source / "manifest.json").exists():
        return False
    web = stage / "web-data"
    web.mkdir(parents=True, exist_ok=True)
    manifest = json.loads((source / "manifest.json").read_text(encoding="utf-8"))
    write_json(web / "update-status.json", status)
    manifest["files"]["status"] = {
        "path": "update-status.json", "sha256": hashlib.sha256((web / "update-status.json").read_bytes()).hexdigest()
    }
    # Leave data generation/as_of and bundle/outcomes hashes untouched.
    write_json(web / "manifest.json", manifest)
    return True


def prune_runs(runtime: Path, keep: int = 14) -> None:
    root = (runtime / "runs").resolve()
    if not root.exists():
        return
    protected = set()
    for name in ("last_good.json", "last_failure.json"):
        try:
            protected.add(json.loads((runtime / name).read_text(encoding="utf-8"))["run_id"])
        except (OSError, ValueError, KeyError):
            pass
    runs = sorted((p for p in root.iterdir() if p.is_dir()), key=lambda p: p.name, reverse=True)
    for path in runs[max(2, keep):]:
        resolved = path.resolve()
        if path.name in protected:
            continue
        if not resolved.is_relative_to(root) or resolved == root:
            raise RuntimeError("Unsafe retention path")
        shutil.rmtree(resolved)


def run_once(config: dict) -> dict:
    repo = Path(config["source_repo"]).resolve()
    runtime = Path(config["runtime_root"]).resolve()
    if os.name == "nt" and (repo.drive.upper() != "D:" or runtime.drive.upper() != "D:"):
        raise ValueError("GHPR source and runtime must remain on D:")
    if runtime == repo or runtime.is_relative_to(repo):
        raise ValueError("Runtime must be outside the source repository")
    runtime.mkdir(parents=True, exist_ok=True)
    with RunLock(runtime / "update.lock"):
        run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid4().hex[:8]
        run = runtime / "runs" / run_id
        stage = run / "stage"
        temp = run / "tmp"
        temp.mkdir(parents=True)
        env = os.environ.copy()
        env.update({"TMP": str(temp), "TEMP": str(temp), "TMPDIR": str(temp),
                    "PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8", "PYTHONDONTWRITEBYTECODE": "1",
                    "MPLCONFIGDIR": str(temp / "matplotlib"), "XDG_CACHE_HOME": str(temp / "cache"),
                    "GIT_TERMINAL_PROMPT": "0", "GCM_INTERACTIVE": "Never", "GHPR_RUN_ID": run_id})
        log = run / "run.log"
        previous = {}
        try:
            previous = json.loads((runtime / "last_good.json").read_text(encoding="utf-8"))
        except (OSError, ValueError):
            pass
        publication_started = False
        status = {"schema": "ghpr.auto-update.v1", "run_id": run_id, "status": "running",
                  "started_at_utc": utc_now(), "last_success_at_utc": previous.get("last_success_at_utc"),
                  "previous_good_run_id": previous.get("run_id"), "error": None,
                  "host_dependency": "Windows host on, Administrator logged in, network and existing Git credential manager available",
                  "schedule": config.get("schedule", "not configured"), "scheduler_invocation": bool(config.get("scheduled", False)),
                  "trigger_reason": os.environ.get("GHPR_SCHEDULER_TRIGGER_REASON", "manual"),
                  "trigger_slot_utc": os.environ.get("GHPR_SCHEDULER_SLOT_UTC"),
                  "natural_schedule_note": "Verify scheduler-status.json heartbeat, trigger reason, slot and published GitHub commit; startup_catchup is not a later scheduled_slot."}
        write_json(runtime / "status.json", status)
        try:
            source_commit = execute(["git", "rev-parse", "HEAD"], repo, env, log)
            status["source_commit"] = source_commit
            env["GHPR_SOURCE_COMMIT"] = source_commit
            shutil.copytree(repo, stage, ignore=shutil.ignore_patterns(".git", ".venv", "venv", "__pycache__", "node_modules", ".pytest_cache", ".env", ".env.*", "secrets.toml", "*.pem", "*.key"))
            values = {"python": config.get("python", sys.executable), "stage": str(stage),
                      "repo": str(repo), "runtime": str(runtime), "run_id": run_id,
                      "today_utc": datetime.now(timezone.utc).date().isoformat(), "now_utc": utc_now()}
            earliest = date.fromisoformat(config.get("initial_price_start", "2026-07-01"))
            rolling_start = datetime.now(timezone.utc).date() - timedelta(days=120)
            # Include the entire Sunday-open trading week at the rolling edge.
            rolling_start -= timedelta(days=(rolling_start.weekday() + 1) % 7)
            values["price_start"] = max(earliest, rolling_start).isoformat()
            commands = config.get("pipeline_commands", [["{python}", "-B", "src/update_pipeline.py", "--mode", "full"]])
            for command in commands:
                execute([str(value).format(**values) for value in command], stage, env, log, config.get("command_timeout_seconds", 3600))
            execute([values["python"], "-B", "src/data_freshness_diagnostics.py", "--strict"], stage, env, log)
            status.update({"status": "data_ready", "last_success_at_utc": utc_now(),
                           "last_success_kind": "source retrieval and data validation; publication verified separately by GitHub commit",
                           "source_status": json.loads((stage / "outputs/reports/source_status.json").read_text(encoding="utf-8"))})
            write_json(stage / "outputs/reports/auto_update_status.json", status)
            write_json(stage / "web-data/update-status.json", status)
            commands = config.get("after_pipeline_commands", [["{python}", "-B", "scripts/build_next_week_outcomes.py"], ["{python}", "-B", "scripts/build_web_release.py"]])
            for command in commands:
                execute([str(value).format(**values) for value in command], stage, env, log, config.get("command_timeout_seconds", 3600))
            manifest = validated_release(stage)
            status["generation_id"] = manifest["generation_id"]
            status["as_of"] = manifest["as_of"]
            status["stage_path"] = str(stage)
            same_data = bool(previous.get("published_commit") and previous.get("generation_id") == manifest["generation_id"])
            status["data_changed"] = not same_data
            if config.get("publish", False):
                if same_data:
                    # New fetch timestamps can change bytes while semantic data
                    # stays identical. Retain old bundle hashes with old bytes.
                    failure_release(repo, stage, status)
                publication_started = True
                status["published_commit"] = publish_files(repo, stage, env, log, run_id, status_only=same_data)
                status["publication_verified_at_utc"] = utc_now()
                status["publication_state"] = "verified_on_github_main"
            else:
                status["publication_state"] = "not_requested_local_validation_only"
            status["status"] = "success"
            status["finished_at_utc"] = utc_now()
            write_json(runtime / "last_good.json", status)
            write_json(runtime / "status.json", status)
        except Exception as exc:
            status.update({"status": "failed", "finished_at_utc": utc_now(),
                           "last_success_at_utc": previous.get("last_success_at_utc"),
                           "error": f"{type(exc).__name__}: {exc}", "retained_previous_snapshot": True})
            write_json(runtime / "last_failure.json", status)
            write_json(runtime / "status.json", status)
            if config.get("publish", False) and not publication_started:
                try:
                    local_head = execute(["git", "rev-parse", "HEAD"], repo, env, log)
                    remote_head = execute(["git", "ls-remote", "origin", "refs/heads/main"], repo, env, log)
                    if not remote_head or remote_head.split()[0] != local_head:
                        raise RuntimeError("Status-only publication deferred because local and remote main differ")
                    if failure_release(repo, stage, status):
                        status["failure_status_commit"] = publish_files(repo, stage, env, log, run_id, status_only=True)
                except Exception as publish_error:
                    status["status_publication_error"] = f"{type(publish_error).__name__}: {publish_error}"
                write_json(runtime / "status.json", status)
                write_json(runtime / "last_failure.json", status)
        prune_runs(runtime, config.get("keep_runs", 14))
        return status


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--publish", action="store_true", help="Publish validated artifacts using the existing Git credential manager")
    parser.add_argument("--scheduled", action="store_true", help="Record that Windows Task Scheduler invoked this run")
    args = parser.parse_args(argv)
    config = json.loads(args.config.read_text(encoding="utf-8-sig"))
    config.update({"publish": args.publish, "scheduled": args.scheduled})
    try:
        result = run_once(config)
    except AlreadyRunning as exc:
        print(f"Skipped: {exc}")
        return 0
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] == "success" else 1


if __name__ == "__main__":
    raise SystemExit(main())
