"""Check GHPR derived-data freshness against the master weekly dataset."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MASTER_PATH = PROJECT_ROOT / "data" / "processed" / "ghpr_master_weekly.csv"
HUB_SUMMARY_PATH = PROJECT_ROOT / "outputs" / "reports" / "ghpr_summary_for_hub.json"
HSE_REPORT_PATH = PROJECT_ROOT / "outputs" / "reports" / "historical_similarity_report.csv"
HSE_FEATURE_VECTOR_PATH = PROJECT_ROOT / "outputs" / "reports" / "hse_current_feature_vector.csv"
MM_LIFECYCLE_DATASET_PATH = PROJECT_ROOT / "data" / "processed" / "mm_lifecycle_dataset.csv"
MM_STRUCTURE_DATASET_PATH = PROJECT_ROOT / "data" / "processed" / "mm_structure_lifecycle_dataset.csv"
MM_VELOCITY_READING_LAYER_PATH = PROJECT_ROOT / "data" / "processed" / "mm_velocity_reading_layer.csv"
DIAGNOSTICS_JSON_PATH = PROJECT_ROOT / "outputs" / "reports" / "data_freshness_diagnostics.json"
DIAGNOSTICS_MD_PATH = PROJECT_ROOT / "outputs" / "reports" / "data_freshness_diagnostics.md"


@dataclass(frozen=True)
class ComponentSpec:
    name: str
    path: Path
    reader: Callable[[Path], str | None]
    fallback_path: Path | None = None
    fallback_reader: Callable[[Path], str | None] | None = None


def latest_csv_date(path: Path, column: str = "date") -> str | None:
    if not path.exists():
        return None
    frame = pd.read_csv(path, usecols=lambda name: name == column)
    if column not in frame.columns:
        return None
    dates = pd.to_datetime(frame[column], errors="coerce").dropna()
    if dates.empty:
        return None
    return dates.max().strftime("%Y-%m-%d")


def first_csv_date(path: Path, column: str) -> str | None:
    if not path.exists():
        return None
    frame = pd.read_csv(path, usecols=lambda name: name == column)
    if column not in frame.columns or frame.empty:
        return None
    dates = pd.to_datetime(frame[column], errors="coerce").dropna()
    if dates.empty:
        return None
    return dates.iloc[0].strftime("%Y-%m-%d")


def hub_summary_date(path: Path) -> str | None:
    if not path.exists():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    value = data.get("date")
    if value is None:
        return None
    parsed = pd.to_datetime(value, errors="coerce")
    if pd.isna(parsed):
        return None
    return parsed.strftime("%Y-%m-%d")


def relative_path(path: Path) -> str:
    try:
        return path.relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def compare_component(
    spec: ComponentSpec,
    expected_latest_date: str | None,
) -> dict[str, Any]:
    path_used = spec.path
    latest_date: str | None = None
    error: str | None = None

    try:
        latest_date = spec.reader(spec.path)
        if latest_date is None and spec.fallback_path is not None and spec.fallback_reader is not None:
            path_used = spec.fallback_path
            latest_date = spec.fallback_reader(spec.fallback_path)
    except Exception as exc:
        error = f"{type(exc).__name__}: {exc}"

    is_current = bool(expected_latest_date and latest_date == expected_latest_date)
    if error is not None:
        stale_reason = error
    elif expected_latest_date is None:
        stale_reason = "missing expected latest date from master dataset"
    elif not path_used.exists():
        stale_reason = "file missing"
    elif latest_date is None:
        stale_reason = "latest date unavailable"
    elif latest_date < expected_latest_date:
        stale_reason = f"latest_date {latest_date} is before expected_latest_date {expected_latest_date}"
    elif latest_date > expected_latest_date:
        stale_reason = f"latest_date {latest_date} is after expected_latest_date {expected_latest_date}"
    else:
        stale_reason = ""

    return {
        "component": spec.name,
        "file": relative_path(path_used),
        "latest_date": latest_date,
        "expected_latest_date": expected_latest_date,
        "is_current": is_current,
        "stale_reason": stale_reason,
    }


def component_specs() -> list[ComponentSpec]:
    return [
        ComponentSpec("master", MASTER_PATH, lambda path: latest_csv_date(path, "date")),
        ComponentSpec("hub_summary", HUB_SUMMARY_PATH, hub_summary_date),
        ComponentSpec(
            "historical_similarity",
            HSE_REPORT_PATH,
            lambda path: first_csv_date(path, "current_date"),
            fallback_path=HSE_FEATURE_VECTOR_PATH,
            fallback_reader=lambda path: latest_csv_date(path, "date"),
        ),
        ComponentSpec("mm_lifecycle", MM_LIFECYCLE_DATASET_PATH, lambda path: latest_csv_date(path, "date")),
        ComponentSpec("mm_structure", MM_STRUCTURE_DATASET_PATH, lambda path: latest_csv_date(path, "date")),
        ComponentSpec(
            "velocity_reading",
            MM_VELOCITY_READING_LAYER_PATH,
            lambda path: latest_csv_date(path, "date"),
        ),
    ]


def overall_status(records: list[dict[str, Any]]) -> str:
    if any(not record["stale_reason"] == "" and record["latest_date"] is None for record in records):
        return "ERROR"
    hub_record = next((record for record in records if record["component"] == "hub_summary"), None)
    if hub_record is not None and not hub_record["is_current"]:
        return "STALE"
    if any(not record["is_current"] for record in records):
        return "PARTIAL_STALE"
    return "OK"


def build_diagnostics() -> dict[str, Any]:
    expected_latest_date = latest_csv_date(MASTER_PATH, "date")
    records = [compare_component(spec, expected_latest_date) for spec in component_specs()]
    status = overall_status(records)
    stale_components = [
        record["component"]
        for record in records
        if record["component"] != "master" and not record["is_current"]
    ]
    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "expected_latest_date": expected_latest_date,
        "overall_status": status,
        "stale_components": stale_components,
        "components": records,
        "scope": "Historical statistics / research reference only. Not a trading signal.",
    }


def render_markdown(diagnostics: dict[str, Any]) -> str:
    lines = [
        "# GHPR Data Freshness Diagnostics",
        "",
        f"- Generated UTC: `{diagnostics.get('generated_at_utc', 'N/A')}`",
        f"- Expected latest date: `{diagnostics.get('expected_latest_date') or 'N/A'}`",
        f"- Overall freshness status: `{diagnostics.get('overall_status', 'ERROR')}`",
        "- Scope: Historical statistics / research reference only.",
        "",
        "| Component | File | Latest Date | Expected Latest Date | Current | Stale Reason |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for record in diagnostics.get("components", []):
        lines.append(
            "| {component} | `{file}` | `{latest}` | `{expected}` | `{current}` | {reason} |".format(
                component=record.get("component", "N/A"),
                file=record.get("file", "N/A"),
                latest=record.get("latest_date") or "N/A",
                expected=record.get("expected_latest_date") or "N/A",
                current=str(record.get("is_current", False)).lower(),
                reason=record.get("stale_reason") or "",
            )
        )
    lines.append("")
    if diagnostics.get("stale_components"):
        lines.append("## Stale Components")
        lines.append("")
        for component in diagnostics["stale_components"]:
            lines.append(f"- {component}")
        lines.append("")
    return "\n".join(lines)


def write_diagnostics(
    json_path: Path = DIAGNOSTICS_JSON_PATH,
    markdown_path: Path = DIAGNOSTICS_MD_PATH,
) -> dict[str, Any]:
    diagnostics = build_diagnostics()
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(
        json.dumps(diagnostics, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    markdown_path.write_text(render_markdown(diagnostics), encoding="utf-8")
    return diagnostics


def main() -> int:
    diagnostics = write_diagnostics()
    print(f"Wrote diagnostics: {DIAGNOSTICS_JSON_PATH}")
    print(f"Wrote diagnostics: {DIAGNOSTICS_MD_PATH}")
    print(f"Overall freshness status: {diagnostics['overall_status']}")
    print(f"Expected latest date: {diagnostics.get('expected_latest_date') or 'N/A'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
