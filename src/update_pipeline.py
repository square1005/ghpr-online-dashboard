"""One-click update pipeline for the GHPR Streamlit dashboard."""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPORTS_DIR = PROJECT_ROOT / "outputs" / "reports"
UPDATE_LOG_PATH = REPORTS_DIR / "update_log.md"
FALLBACK_LOG_PATH = Path(tempfile.gettempdir()) / "ghpr_outputs" / "reports" / "update_log.md"
MASTER_PATH = PROJECT_ROOT / "data" / "processed" / "ghpr_master_weekly.csv"
CURRENT_COT_PATH = PROJECT_ROOT / "data" / "raw" / "cot" / "fut_disagg_txt_current.csv"
VALID_UPDATE_MODES = {"local", "full"}


@dataclass
class UpdateStepResult:
    name: str
    command: list[str]
    return_code: int
    elapsed_seconds: float
    stdout: str = ""
    stderr: str = ""

    @property
    def success(self) -> bool:
        return self.return_code == 0


@dataclass
class UpdatePipelineResult:
    success: bool
    started_at_utc: datetime
    finished_at_utc: datetime
    log_path: Path
    mode: str = "local"
    latest_dataset_date_before: str | None = None
    latest_dataset_date_after: str | None = None
    latest_cftc_available_date: str | None = None
    data_is_current: bool = False
    stale_reason: str = "not_checked"
    steps: list[UpdateStepResult] = field(default_factory=list)
    error_message: str = ""

    @property
    def status_text(self) -> str:
        return "success" if self.success else "fail"

    @property
    def failed_step(self) -> UpdateStepResult | None:
        return next((step for step in self.steps if not step.success), None)


def run_update_pipeline(mode: str = "local", no_download: bool | None = None) -> UpdatePipelineResult:
    """Run all GHPR refresh steps and write a markdown update log."""
    if no_download is not None:
        mode = "local" if no_download else "full"
    if mode not in VALID_UPDATE_MODES:
        raise ValueError(f"Invalid update mode: {mode}. Expected one of: {sorted(VALID_UPDATE_MODES)}")

    started_at = datetime.now(timezone.utc)
    steps: list[UpdateStepResult] = []
    error_message = ""
    latest_dataset_date_before = latest_dataset_date()

    commands = build_update_commands(mode=mode)
    env = os.environ.copy()
    env["PYTHONUTF8"] = "1"
    env["PYTHONIOENCODING"] = "utf-8:replace"

    for name, command in commands:
        step_started = time.perf_counter()
        try:
            completed = subprocess.run(
                command,
                cwd=PROJECT_ROOT,
                env=env,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=900,
            )
            elapsed = time.perf_counter() - step_started
            result = UpdateStepResult(
                name=name,
                command=command,
                return_code=completed.returncode,
                elapsed_seconds=elapsed,
                stdout=sanitize_output(completed.stdout or ""),
                stderr=sanitize_output(completed.stderr or ""),
            )
        except subprocess.TimeoutExpired as error:
            elapsed = time.perf_counter() - step_started
            result = UpdateStepResult(
                name=name,
                command=command,
                return_code=-1,
                elapsed_seconds=elapsed,
                stdout=sanitize_output((error.stdout or "") if isinstance(error.stdout, str) else ""),
                stderr=sanitize_output(
                    f"Command timed out after {error.timeout} seconds.\n{error.stderr or ''}"
                ),
            )
        except Exception as error:
            elapsed = time.perf_counter() - step_started
            result = UpdateStepResult(
                name=name,
                command=command,
                return_code=-1,
                elapsed_seconds=elapsed,
                stderr=sanitize_output(f"{type(error).__name__}: {error}"),
            )
        steps.append(result)
        if not result.success:
            error_message = f"{name} failed with exit code {result.return_code}"
            break

    finished_at = datetime.now(timezone.utc)
    latest_dataset_date_after = latest_dataset_date()
    latest_cftc_available_date = latest_cftc_available_date_from_current_file()
    data_is_current, stale_reason = build_freshness_status(
        latest_dataset_date_after,
        latest_cftc_available_date,
    )
    pipeline_result = UpdatePipelineResult(
        success=not error_message,
        started_at_utc=started_at,
        finished_at_utc=finished_at,
        log_path=UPDATE_LOG_PATH,
        mode=mode,
        latest_dataset_date_before=latest_dataset_date_before,
        latest_dataset_date_after=latest_dataset_date_after,
        latest_cftc_available_date=latest_cftc_available_date,
        data_is_current=data_is_current,
        stale_reason=stale_reason,
        steps=steps,
        error_message=error_message,
    )
    pipeline_result.log_path = write_update_log(pipeline_result)
    return pipeline_result


def build_update_commands(mode: str = "local", no_download: bool | None = None) -> list[tuple[str, list[str]]]:
    if no_download is not None:
        mode = "local" if no_download else "full"
    if mode not in VALID_UPDATE_MODES:
        raise ValueError(f"Invalid update mode: {mode}. Expected one of: {sorted(VALID_UPDATE_MODES)}")

    python = sys.executable
    build_master = [python, "src/build_master_dataset.py"]
    if mode == "local":
        build_master.append("--no-download")

    return [
        ("Build master weekly dataset", build_master),
        ("Run single-factor analysis", [python, "src/factor_analysis.py"]),
        ("Regenerate charts", [python, "src/plot_engine.py"]),
        ("Generate factor research report", [python, "src/report_engine.py"]),
        ("Run historical similarity engine", [python, "src/historical_similarity_engine.py"]),
        ("Run MM lifecycle research", [python, "src/mm_lifecycle_research.py"]),
        ("Run MM structure lifecycle research", [python, "src/mm_structure_lifecycle_research.py"]),
        ("Run MM velocity window discovery", [python, "src/mm_velocity_window_discovery.py"]),
        ("Run MM velocity reading layer", [python, "src/mm_velocity_reading_layer.py"]),
        ("Export hub summary", [python, "src/export_hub_summary.py"]),
        ("Run data freshness diagnostics", [python, "src/data_freshness_diagnostics.py"]),
    ]


def latest_dataset_date() -> str | None:
    if not MASTER_PATH.exists():
        return None
    try:
        import pandas as pd

        frame = pd.read_csv(MASTER_PATH, usecols=["date"])
        dates = pd.to_datetime(frame["date"], errors="coerce").dropna()
    except Exception:
        return None
    if dates.empty:
        return None
    return dates.max().strftime("%Y-%m-%d")


def latest_cftc_available_date_from_current_file() -> str | None:
    if not CURRENT_COT_PATH.exists():
        return None
    try:
        import pandas as pd

        frame = pd.read_csv(
            CURRENT_COT_PATH,
            encoding="latin1",
            usecols=["Report_Date_as_YYYY-MM-DD"],
        )
        dates = pd.to_datetime(frame["Report_Date_as_YYYY-MM-DD"], errors="coerce").dropna()
    except Exception:
        return None
    if dates.empty:
        return None
    return dates.max().strftime("%Y-%m-%d")


def build_freshness_status(
    latest_dataset_date_value: str | None,
    latest_cftc_available_date_value: str | None,
) -> tuple[bool, str]:
    if latest_dataset_date_value is None:
        return False, "missing latest dataset date"
    if latest_cftc_available_date_value is None:
        return False, "latest CFTC available date unavailable"
    dataset_date = datetime.fromisoformat(latest_dataset_date_value)
    cftc_date = datetime.fromisoformat(latest_cftc_available_date_value)
    if dataset_date >= cftc_date:
        return True, ""
    return (
        False,
        f"latest_dataset_date {latest_dataset_date_value} is before latest_cftc_available_date {latest_cftc_available_date_value}",
    )


def write_update_log(result: UpdatePipelineResult) -> Path:
    log_path = UPDATE_LOG_PATH
    try:
        log_path.parent.mkdir(parents=True, exist_ok=True)
        log_path.write_text(render_update_log(result), encoding="utf-8")
    except OSError:
        log_path = FALLBACK_LOG_PATH
        log_path.parent.mkdir(parents=True, exist_ok=True)
        log_path.write_text(render_update_log(result), encoding="utf-8")
    return log_path


def render_update_log(result: UpdatePipelineResult) -> str:
    lines = [
        "# GHPR Update Log",
        "",
        f"- Status: `{result.status_text}`",
        f"- Update mode: `{result.mode}`",
        f"- Started UTC: `{result.started_at_utc.isoformat()}`",
        f"- Finished UTC: `{result.finished_at_utc.isoformat()}`",
        f"- Latest dataset date before update: `{result.latest_dataset_date_before or 'N/A'}`",
        f"- Latest dataset date after update: `{result.latest_dataset_date_after or 'N/A'}`",
        f"- Latest CFTC available date: `{result.latest_cftc_available_date or 'N/A'}`",
        f"- Data is current: `{str(result.data_is_current).lower()}`",
        f"- Stale reason: `{result.stale_reason or 'N/A'}`",
        f"- Runtime note: `Cloud runtime file writes may be ephemeral; commit refreshed outputs to GitHub for durable deployment data.`",
        f"- Scope: `Historical statistics / research reference only.`",
        "",
    ]
    if result.failed_step is not None:
        step = result.failed_step
        lines.extend(
            [
                "## Failure Summary",
                "",
                f"- Failed step: `{step.name}`",
                f"- Command: `{format_command(step.command)}`",
                f"- Exit code: `{step.return_code}`",
                "",
                "### stderr",
                "",
                "```text",
                step.stderr or "N/A",
                "```",
                "",
            ]
        )
    lines.extend(["## Steps", ""])
    for step in result.steps:
        lines.extend(
            [
                f"### {step.name}",
                "",
                f"- Command: `{format_command(step.command)}`",
                f"- Exit code: `{step.return_code}`",
                f"- Elapsed seconds: `{step.elapsed_seconds:.2f}`",
                "",
                "#### stdout",
                "",
                "```text",
                step.stdout or "N/A",
                "```",
                "",
                "#### stderr",
                "",
                "```text",
                step.stderr or "N/A",
                "```",
                "",
            ]
        )
    if result.error_message:
        lines.extend(["## Error", "", result.error_message, ""])
    return "\n".join(lines)


def format_command(command: list[str]) -> str:
    return " ".join(command)


def sanitize_output(output: str) -> str:
    cleaned = output.strip()
    if not cleaned:
        return ""
    return re.sub(
        r"(?<![A-Za-z])[A-Za-z]:[\\/][^\r\n`]*?GHPR_Engine[\\/]",
        "PROJECT_ROOT/",
        cleaned,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run GHPR update pipeline.")
    parser.add_argument(
        "--mode",
        choices=sorted(VALID_UPDATE_MODES),
        default="local",
        help="local uses existing raw files; full downloads latest data then rebuilds.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    outcome = run_update_pipeline(mode=args.mode)
    print(f"Update pipeline status: {outcome.status_text}")
    print(f"Update mode: {outcome.mode}")
    print(f"Latest dataset date before update: {outcome.latest_dataset_date_before or 'N/A'}")
    print(f"Latest dataset date after update: {outcome.latest_dataset_date_after or 'N/A'}")
    print(f"Latest CFTC available date: {outcome.latest_cftc_available_date or 'N/A'}")
    print(f"Data is current: {str(outcome.data_is_current).lower()}")
    print(f"Stale reason: {outcome.stale_reason or 'N/A'}")
    print(f"Update log: {outcome.log_path}")
    return 0 if outcome.success else 1


if __name__ == "__main__":
    raise SystemExit(main())
