"""Build auditable GC=F outcomes for the calendar week after each COT date.

Inputs are immutable normalized Yahoo daily/hourly CSVs. Daily bars determine
prices. An hourly bar may locate an extremum only when the weekly extrema and
session dates reconcile; its start is a bucket boundary, never an exact tick.
Uses only the standard library (the host must provide the IANA time-zone data).
"""
from __future__ import annotations

import argparse
import calendar as month_calendar
import copy
import csv
import hashlib
import io
import json
import math
import os
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

UTC = timezone.utc
NY = ZoneInfo("America/New_York")
TAIPEI = ZoneInfo("Asia/Taipei")
WEEKDAYS = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")
PRICE_TOLERANCE = 0.0005  # Float serialization tolerance, well below a GC tick.
PRICE_KEYS = ("open", "high", "low", "close")
SCHEMA_VERSION = 1


def iso_time(value: datetime | None) -> str | None:
    return value.isoformat() if value else None


def parse_time(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError(f"Timestamp requires an explicit UTC offset: {value}")
    return parsed.astimezone(UTC)


def next_week(cot_date: date) -> tuple[date, date]:
    monday = cot_date - timedelta(days=cot_date.weekday()) + timedelta(days=7)
    return monday, monday + timedelta(days=4)


def months_before(value: date, months: int) -> date:
    absolute = value.year * 12 + value.month - 1 - months
    year, month0 = divmod(absolute, 12)
    month = month0 + 1
    return date(year, month, min(value.day, month_calendar.monthrange(year, month)[1]))


def finite_price(value: object) -> float:
    if value in (None, "", "null", "None"):
        raise ValueError("missing OHLC")
    number = float(value)
    if not math.isfinite(number) or number <= 0:
        raise ValueError("non-finite or non-positive OHLC")
    return number


def normalize_prices(rows: list[dict], interval: str) -> tuple[list[dict], list[dict]]:
    """Fail on conflicting duplicate bars; explicitly audit rejected source rows."""
    accepted, rejected, seen = [], [], {}
    for index, original in enumerate(rows):
        row = dict(original)
        try:
            if row.get("symbol", "GC=F") != "GC=F":
                raise RuntimeError("Cross-feed input rejected: expected GC=F")
            if row.get("source_interval", interval) != interval:
                raise RuntimeError(f"Unexpected source interval: expected {interval}")
            row.update({key: finite_price(row.get(key)) for key in PRICE_KEYS})
            if row["low"] > min(row["open"], row["close"]) or row["high"] < max(row["open"], row["close"]) or row["low"] > row["high"]:
                raise ValueError("invalid OHLC bounds")
            if interval == "1d":
                key = date.fromisoformat(row["date"]).isoformat()
                row["date"] = key
            else:
                start = parse_time(row["bar_start_utc"])
                if start.minute or start.second or start.microsecond:
                    raise ValueError("non-grid quote snapshot")
                local = start.astimezone(NY)
                if local.hour == 17:
                    raise ValueError("CME daily maintenance break")
                end = parse_time(row["bar_end_utc_nominal"]) if row.get("bar_end_utc_nominal") else start + timedelta(hours=1)
                if end - start != timedelta(hours=1):
                    raise ValueError("not a nominal one-hour bar")
                candidate = local.date() + timedelta(days=int(local.hour >= 18))
                session = row.get("session_date") or row.get("session_date_candidate") or candidate.isoformat()
                row["session_date"] = date.fromisoformat(session).isoformat()
                row["_start"], row["_end"] = start, end
                key = start.isoformat()
            if key in seen:
                if any(abs(row[k] - seen[key][k]) > PRICE_TOLERANCE for k in PRICE_KEYS):
                    raise RuntimeError(f"Conflicting duplicate {interval} bar: {key}")
                rejected.append({"input_index": index, "key": key, "reason": "identical_duplicate"})
                continue
            seen[key] = row
            accepted.append(row)
        except (ValueError, KeyError, TypeError) as exc:
            rejected.append({"input_index": index, "reason": str(exc)})
    accepted.sort(key=lambda r: r["date"] if interval == "1d" else r["_start"])
    return accepted, rejected


def calendar_rules(calendar_data: dict | None) -> tuple[set[str], dict, list]:
    data = calendar_data or {}
    excluded = set(data.get("no_daily_bar_dates", []) + data.get("daily_excluded_dates", []))
    overrides = data.get("weekly_overrides", {})
    for entry in data.get("holidays", []):
        if entry.get("daily_bar_expected") is False or entry.get("exclude_daily") is True:
            excluded.add(entry["date"])
    sources = list(data.get("sources", []))
    for source in [data.get("normal_session", {}).get("source_url"), data.get("override_source_url")]:
        if source and source not in sources:
            sources.append(source)
    for entry in data.get("holidays", []):
        if entry.get("source_url") and entry["source_url"] not in sources:
            sources.append(entry["source_url"])
    return excluded, overrides, sources


def week_expectations(start: date, end: date, calendar_data: dict | None) -> dict:
    excluded, overrides, sources = calendar_rules(calendar_data)
    expected = [(start + timedelta(days=n)).isoformat() for n in range(5) if (start + timedelta(days=n)).isoformat() not in excluded]
    override = overrides.get(start.isoformat(), {})
    if "expected_daily_dates" in override:
        expected = override["expected_daily_dates"]
    holiday = len(expected) != 5 or bool(override.get("holiday_affected"))
    # Unknown holiday hours are deliberately not replaced by the 115-hour norm.
    expected_hours = override.get("expected_hourly_bars", None if holiday else 115)
    return {
        "dates": expected,
        "hours": expected_hours,
        "holiday_affected": holiday,
        "note": override.get("note", "Holiday-adjusted vendor daily labels; four daily labels do not prove complete intraday trading coverage." if holiday else "Weekday daily-bar labels; normal COMEX 18:00–17:00 America/New_York sessions."),
        "sources": sources,
        "hourly_coverage_known_partial": bool(override.get("hourly_coverage_known_partial", holiday and expected_hours is None)),
    }


def observed_hour_coverage(hours: list[dict], expected: dict, start: date) -> str:
    if not hours:
        return "MISSING"
    if expected["hourly_coverage_known_partial"] or expected["hours"] is None:
        return "PARTIAL"
    if len(hours) != expected["hours"]:
        return "PARTIAL"
    # Count alone cannot prove normal-week coverage: verify every session bucket.
    if expected["hours"] == 115 and not expected["holiday_affected"]:
        actual = {row["_start"] for row in hours}
        wanted = set()
        for n in range(5):
            session_day = start + timedelta(days=n)
            first = datetime.combine(session_day - timedelta(days=1), time(18), NY).astimezone(UTC)
            wanted.update(first + timedelta(hours=h) for h in range(23))
        if actual != wanted:
            return "PARTIAL"
    return "COMPLETE_OBSERVED_HOURLY"


def extreme_details(kind: str, daily: list[dict], hours: list[dict], hourly_coverage: str) -> dict:
    result = {
        f"{kind}_date": None, f"{kind}_weekday": None,
        f"{kind}_dates": [], f"{kind}_daily_tie_count": 0,
        f"{kind}_time_utc": None, f"{kind}_time_taipei": None,
        f"{kind}_time_range_taipei": None, f"{kind}_time_range_utc": None,
        f"{kind}_time_precision": "unavailable", f"{kind}_time_reason": "NO_DAILY_BARS",
        f"{kind}_hour_bucket_tie_count": 0, f"{kind}_observed_hour_buckets": [],
        f"{kind}_first_hour_bucket_verified": False,
    }
    if not daily:
        return result
    extremum = (max if kind == "high" else min)(row[kind] for row in daily)
    days = [row["date"] for row in daily if abs(row[kind] - extremum) <= PRICE_TOLERANCE]
    result.update({f"{kind}_date": days[0], f"{kind}_weekday": WEEKDAYS[date.fromisoformat(days[0]).weekday()],
                   f"{kind}_dates": days, f"{kind}_daily_tie_count": len(days),
                   f"{kind}_time_precision": "day", f"{kind}_time_reason": "NO_HOURLY_BARS"})
    if not hours:
        return result
    hourly_extremum = (max if kind == "high" else min)(row[kind] for row in hours)
    if abs(hourly_extremum - extremum) > PRICE_TOLERANCE:
        result[f"{kind}_time_reason"] = "DAILY_HOURLY_EXTREME_MISMATCH"
        result[f"{kind}_hourly_comparison_price"] = hourly_extremum
        return result
    matching = [row for row in hours if abs(row[kind] - extremum) <= PRICE_TOLERANCE]
    # Daily labels are authoritative, including the first tied daily occurrence.
    if any(row["session_date"] not in days for row in matching) or matching[0]["session_date"] != days[0]:
        result[f"{kind}_time_reason"] = "DAILY_HOURLY_SESSION_MISMATCH"
        return result
    buckets = [{"start_utc": iso_time(row["_start"]), "end_utc": iso_time(row["_end"]),
                "start_taipei": iso_time(row["_start"].astimezone(TAIPEI)),
                "end_taipei": iso_time(row["_end"].astimezone(TAIPEI)),
                "session_date": row["session_date"]} for row in matching]
    first = buckets[0]
    complete = hourly_coverage == "COMPLETE_OBSERVED_HOURLY"
    result.update({
        f"{kind}_time_utc": first["start_utc"], f"{kind}_time_taipei": first["start_taipei"],
        f"{kind}_time_range_taipei": {"start": first["start_taipei"], "end": first["end_taipei"]},
        f"{kind}_time_range_utc": {"start": first["start_utc"], "end": first["end_utc"]},
        f"{kind}_time_precision": "hour_bucket",
        f"{kind}_time_reason": "MATCHED_FIRST_OBSERVED_HOUR_BUCKET" if complete else "MATCHED_OBSERVED_BUCKET_INCOMPLETE_HOURLY_COVERAGE",
        f"{kind}_hour_bucket_tie_count": len(buckets), f"{kind}_observed_hour_buckets": buckets,
        f"{kind}_first_hour_bucket_verified": complete,
        f"{kind}_weekday_taipei": WEEKDAYS[parse_time(first["start_utc"]).astimezone(TAIPEI).weekday()],
    })
    return result


def extreme_order(row: dict) -> str:
    if row["high_date"] is None or row["low_date"] is None:
        return "UNKNOWN"
    if row["high_date"] < row["low_date"]:
        return "HIGH_THEN_LOW"
    if row["low_date"] < row["high_date"]:
        return "LOW_THEN_HIGH"
    if not (row["high_first_hour_bucket_verified"] and row["low_first_hour_bucket_verified"]):
        return "SAME_DAY_UNKNOWN"
    high, low = row["high_time_range_utc"], row["low_time_range_utc"]
    if high["end"] <= low["start"]:
        return "HIGH_THEN_LOW"
    if low["end"] <= high["start"]:
        return "LOW_THEN_HIGH"
    return "SAME_BUCKET_UNKNOWN"


def build_outcomes(cot_dates: list[date], daily_input: list[dict], hourly_input: list[dict], *,
                   as_of: datetime, cot_start: date, cot_end: date,
                   calendar_data: dict | None = None, provenance: dict | None = None,
                   previous_outcomes: dict | None = None, source_window_start: datetime | None = None,
                   previous_fingerprint: dict | None = None) -> dict:
    if previous_outcomes and (previous_outcomes.get("price_feed") != "GC=F" or previous_outcomes.get("schema_version") != SCHEMA_VERSION):
        raise RuntimeError("Previous outcome feed/schema must match GC=F schema 1")
    if previous_outcomes and source_window_start is None:
        raise ValueError("Preservation requires the explicit source query window start, not the first valid bar")
    if source_window_start and source_window_start > as_of:
        raise ValueError("Source query window start cannot be after as-of")
    daily, daily_rejections = normalize_prices(daily_input, "1d")
    hourly, hourly_rejections = normalize_prices(hourly_input, "1h")
    rows = []
    previous_rows = {r["cot_date"]: r for r in (previous_outcomes or {}).get("rows", [])}
    archived_provenance = {}
    for cot in sorted(set(cot_dates)):
        if not cot_start <= cot <= cot_end:
            continue
        start, end = next_week(cot)
        expected = week_expectations(start, end, calendar_data)
        session_open = datetime.combine(start - timedelta(days=1), time(18), NY).astimezone(UTC)
        session_close = datetime.combine(end, time(17), NY).astimezone(UTC)
        previous = previous_rows.get(cot.isoformat())
        if (previous and source_window_start and session_close < source_window_start
                and previous.get("coverage_status") == "COMPLETE_DAILY"):
            if previous.get("price_feed") != "GC=F" or previous.get("week_start") != start.isoformat() or previous.get("week_end") != end.isoformat():
                raise RuntimeError(f"Archived outcome feed/window mismatch for {cot}")
            for key in PRICE_KEYS:
                finite_price(previous.get(key))
            preserved = copy.deepcopy(previous)
            preserved.update({"archive_status": "ARCHIVED_COMPLETE", "week_state": "ENDED",
                              "week_start_at": iso_time(session_open), "week_end_at": iso_time(session_close)})
            reference = previous.get("archive_reference")
            if reference:
                provenance_id = reference["provenance_id"]
                source_provenance = (previous_outcomes or {}).get("archived_provenance", {}).get(provenance_id)
                if source_provenance is None:
                    raise RuntimeError(f"Archived provenance missing for {cot}")
            else:
                previous_sha = (previous_fingerprint or {}).get("sha256") or hashlib.sha256(
                    json.dumps(previous_outcomes, sort_keys=True, ensure_ascii=False, allow_nan=False).encode()).hexdigest()
                provenance_id = previous_sha
                reference = {"provenance_id": provenance_id, "source_snapshot_sha256": previous_sha,
                             "source_snapshot_as_of": previous_outcomes.get("scope", {}).get("as_of")}
                source_provenance = previous_outcomes.get("provenance", {})
            archived_provenance[provenance_id] = copy.deepcopy(source_provenance)
            preserved["archive_reference"] = copy.deepcopy(reference)
            rows.append(preserved)
            continue
        pending = as_of < session_open
        # A date label is usable only after the session close; this also prevents
        # current daily bars and future-dated fixture values from leaking forward.
        week_daily = [r for r in daily if start.isoformat() <= r["date"] <= end.isoformat()
                      and datetime.combine(date.fromisoformat(r["date"]), time(17), NY).astimezone(UTC) <= as_of] if not pending else []
        week_hourly = [r for r in hourly if start.isoformat() <= r["session_date"] <= end.isoformat()
                       and r["_end"] <= as_of] if not pending else []
        observed_dates = [r["date"] for r in week_daily]
        missing_dates = sorted(set(expected["dates"]) - set(observed_dates))
        extra_dates = sorted(set(observed_dates) - set(expected["dates"]))
        status = "PENDING" if pending else ("PARTIAL" if as_of < session_close else
                  "MISSING" if not week_daily else "COMPLETE_DAILY" if not missing_dates and not extra_dates else "PARTIAL")
        hour_coverage = "PENDING" if pending else observed_hour_coverage(week_hourly, expected, start)
        row = {
            "cot_date": cot.isoformat(), "week_start": start.isoformat(), "week_end": end.isoformat(),
            **{key: None for key in (*PRICE_KEYS, "change", "change_pct", "range", "range_pct")},
            "coverage_status": status, "observed_sessions": len(week_daily), "expected_sessions": len(expected["dates"]),
            "week_state": "PENDING" if pending else "ENDED" if as_of >= session_close else "IN_PROGRESS",
            "archive_status": "CURRENT_QUERY",
            "observed_session_dates": observed_dates, "expected_session_dates": expected["dates"],
            "missing_session_dates": missing_dates, "unexpected_session_dates": extra_dates,
            "hourly_coverage_status": hour_coverage, "observed_hourly_bars": len(week_hourly),
            "expected_hourly_bars": expected["hours"], "holiday_affected": expected["holiday_affected"],
            "calendar_note": expected["note"], "calendar_sources": expected["sources"],
            "source": "Yahoo Finance GC=F", "price_feed": "GC=F", "currency": "USD",
            "price_semantics": "First daily session open and last daily vendor close; not an official CME settlement series.",
            "time_semantics": "One-hour bucket start/end, not the exact minute of an extremum. First matching observed bucket only when daily prices reconcile.",
            "week_timezone": "America/New_York", "display_timezone": "Asia/Taipei",
            "window_start_utc": iso_time(session_open), "window_end_utc": iso_time(session_close),
            "week_start_at": iso_time(session_open), "week_end_at": iso_time(session_close),
            "bars": [{"date": r["date"], **{key: r[key] for key in PRICE_KEYS}} for r in week_daily],
            "actual_cot_release_at_utc": None,
            "research_availability_note": "Observation-next-calendar-week rule. Actual CFTC publication time must be checked separately before claiming a no-look-ahead study.",
        }
        if week_daily:
            opening, closing = week_daily[0]["open"], week_daily[-1]["close"]
            high, low = max(r["high"] for r in week_daily), min(r["low"] for r in week_daily)
            row.update({"open": opening, "high": high, "low": low, "close": closing,
                        "change": closing - opening, "change_pct": closing / opening - 1,
                        "range": high - low, "range_pct": (high - low) / opening})
        row.update(extreme_details("high", week_daily, week_hourly, hour_coverage))
        row.update(extreme_details("low", week_daily, week_hourly, hour_coverage))
        precisions = {row["high_time_precision"], row["low_time_precision"]}
        row["time_precision"] = next(iter(precisions)) if len(precisions) == 1 else "mixed"
        row["extreme_order"] = extreme_order(row)
        rows.append(row)
    counts = {status: sum(r["coverage_status"] == status for r in rows)
              for status in ("COMPLETE_DAILY", "PARTIAL", "PENDING", "MISSING")}
    return {
        "schema_version": SCHEMA_VERSION, "price_feed": "GC=F", "source": "Yahoo Finance chart",
        "scope": {"cot_start": cot_start.isoformat(), "cot_end": cot_end.isoformat(), "as_of": iso_time(as_of),
                  "window_rule": "COT observation date -> following calendar Monday–Friday, COMEX session-date labels in America/New_York",
                  "selection_rule": "Inclusive COT observation dates; outcome weeks may cross the scope boundary."},
        "percent_units": "ratio (0.01 means 1%)", "price_tolerance": PRICE_TOLERANCE,
        "rows": rows, "coverage_summary": {"rows": len(rows), **counts,
            "hour_bucket_highs": sum(r["high_time_precision"] == "hour_bucket" for r in rows),
            "hour_bucket_lows": sum(r["low_time_precision"] == "hour_bucket" for r in rows)},
        "provenance": provenance or {}, "calendar": calendar_data or {},
        "source_window_start": iso_time(source_window_start),
        "archived_provenance": archived_provenance,
        "archive_summary": {"preserved_complete_rows": sum(r["archive_status"] == "ARCHIVED_COMPLETE" for r in rows),
                            "rule": "Only previously COMPLETE_DAILY weeks ending strictly before the explicit source query start are preserved. Current-window gaps are never masked."},
        "input_audit": {"daily_accepted": len(daily), "hourly_accepted": len(hourly),
                        "daily_rejections": daily_rejections, "hourly_rejections": hourly_rejections},
    }


def read_csv(path: Path | None) -> list[dict]:
    if path is None:
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def fingerprint(path: Path | None) -> dict | None:
    if path is None:
        return None
    return {"file": path.name, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}


def write_atomic(path: Path, content: str) -> bool:
    """Idempotent derived-output replacement; never modifies price inputs."""
    path.parent.mkdir(parents=True, exist_ok=True)
    encoded = content.encode("utf-8")
    if path.exists() and path.read_bytes() == encoded:
        return False
    temporary = path.with_name(path.name + f".{os.getpid()}.tmp")
    try:
        temporary.write_bytes(encoded)
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()
    return True


def csv_output(payload: dict) -> str:
    all_fields = dict.fromkeys(key for row in payload["rows"] for key in row)
    nested_fields = {key for row in payload["rows"] for key, value in row.items() if isinstance(value, (dict, list))}
    scalar_fields = [key for key in all_fields if key not in nested_fields] if payload["rows"] else ["cot_date", "week_start", "week_end", "coverage_status"]
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=scalar_fields, extrasaction="ignore", lineterminator="\n")
    writer.writeheader()
    writer.writerows(payload["rows"])
    return output.getvalue()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--master", type=Path, required=True, help="COT master CSV containing date or cot_date")
    parser.add_argument("--daily", type=Path, required=True)
    parser.add_argument("--hourly", type=Path)
    parser.add_argument("--calendar", type=Path)
    parser.add_argument("--price-coverage", type=Path)
    parser.add_argument("--previous-outcomes", "--previous-json", dest="previous_outcomes", type=Path,
                        help="Previous same-feed outcomes, read before replacing output; may equal --output-json")
    parser.add_argument("--source-window-start", help="Actual source query start date/aware ISO; required when preserving previous outcomes")
    parser.add_argument("--as-of", default=None, help="UTC-aware ISO datetime, or date interpreted as 00:00 UTC")
    parser.add_argument("--scope-months", type=int, default=3)
    parser.add_argument("--cot-start", type=date.fromisoformat)
    parser.add_argument("--cot-end", type=date.fromisoformat)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-csv", type=Path, required=True)
    args = parser.parse_args()
    as_of = (parse_time(args.as_of + "T00:00:00+00:00" if len(args.as_of) == 10 else args.as_of)
             if args.as_of else datetime.now(UTC))
    cot_start = args.cot_start or months_before(as_of.date(), args.scope_months)
    cot_end = args.cot_end or as_of.date()
    if cot_start > cot_end or args.scope_months < 0:
        parser.error("Invalid COT date range")
    if args.previous_outcomes and not args.source_window_start:
        parser.error("--previous-outcomes requires --source-window-start")
    source_window_start = (parse_time(args.source_window_start + "T00:00:00+00:00" if len(args.source_window_start) == 10 else args.source_window_start)
                           if args.source_window_start else None)
    inputs = [args.master, args.daily, args.hourly, args.calendar, args.price_coverage]
    outputs = [args.output_json.resolve(), args.output_csv.resolve()]
    if len(set(outputs)) != len(outputs) or any(p and p.resolve() in outputs for p in inputs):
        parser.error("Output paths must be distinct from each other and every source input")
    master = read_csv(args.master)
    cot_dates = [date.fromisoformat(row.get("cot_date") or row["date"]) for row in master]
    calendar_data = json.loads(args.calendar.read_text(encoding="utf-8-sig")) if args.calendar else {}
    provenance = {"master": fingerprint(args.master), "daily": fingerprint(args.daily),
                  "hourly": fingerprint(args.hourly), "calendar": fingerprint(args.calendar)}
    if args.price_coverage:
        provenance["price_coverage"] = json.loads(args.price_coverage.read_text(encoding="utf-8-sig"))
    previous = json.loads(args.previous_outcomes.read_text(encoding="utf-8-sig")) if args.previous_outcomes else None
    result = build_outcomes(cot_dates, read_csv(args.daily), read_csv(args.hourly), as_of=as_of,
                            cot_start=cot_start, cot_end=cot_end, calendar_data=calendar_data, provenance=provenance,
                            previous_outcomes=previous, source_window_start=source_window_start,
                            previous_fingerprint=fingerprint(args.previous_outcomes))
    changed_json = write_atomic(args.output_json, json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False) + "\n")
    changed_csv = write_atomic(args.output_csv, csv_output(result))
    print(json.dumps({"coverage": result["coverage_summary"], "output_json": str(args.output_json),
                      "output_csv": str(args.output_csv), "changed_json": changed_json, "changed_csv": changed_csv}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
