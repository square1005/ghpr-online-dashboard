"""One-click update pipeline for the GHPR Streamlit dashboard."""

from __future__ import annotations

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
    steps: list[UpdateStepResult] = field(default_factory=list)
    error_message: str = ""

    @property
    def status_text(self) -> str:
        return "success" if self.success else "fail"

    @property
    def failed_step(self) -> UpdateStepResult | None:
        return next((step for step in self.steps if not step.success), None)


def run_update_pipeline(no_download: bool = True) -> UpdatePipelineResult:
    """Run all GHPR refresh steps and write a markdown update log."""
    started_at = datetime.now(timezone.utc)
    steps: list[UpdateStepResult] = []
    error_message = ""

    commands = build_update_commands(no_download=no_download)
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
    pipeline_result = UpdatePipelineResult(
        success=not error_message,
        started_at_utc=started_at,
        finished_at_utc=finished_at,
        log_path=UPDATE_LOG_PATH,
        steps=steps,
        error_message=error_message,
    )
    pipeline_result.log_path = write_update_log(pipeline_result)
    return pipeline_result


def build_update_commands(no_download: bool = True) -> list[tuple[str, list[str]]]:
    python = sys.executable
    build_master = [python, "src/build_master_dataset.py"]
    if no_download:
        build_master.append("--no-download")

    return [
        ("Fetch daily gold OHLC", [python, "src/fetch_gold_daily_ohlc.py"]),
        ("Build master weekly dataset", build_master),
        ("Run single-factor analysis", [python, "src/factor_analysis.py"]),
        ("Regenerate charts", [python, "src/plot_engine.py"]),
        ("Generate factor research report", [python, "src/report_engine.py"]),
        ("Run historical similarity engine", [python, "src/historical_similarity_engine.py"]),
        ("Export hub summary", [python, "src/export_hub_summary.py"]),
    ]


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
        f"- Started UTC: `{result.started_at_utc.isoformat()}`",
        f"- Finished UTC: `{result.finished_at_utc.isoformat()}`",
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


if __name__ == "__main__":
    outcome = run_update_pipeline()
    print(f"Update pipeline status: {outcome.status_text}")
    print(f"Update log: {outcome.log_path}")
    raise SystemExit(0 if outcome.success else 1)
