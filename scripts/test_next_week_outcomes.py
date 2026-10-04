"""Semantic tests for observed-week outcomes; no network or source mutations."""
import csv
import io
import unittest
from datetime import date, datetime, timedelta

from build_next_week_outcomes import (
    NY, UTC, build_outcomes, csv_output, months_before, next_week,
    normalize_prices, parse_time, research_availability,
)


def daily_fixture(start=date(2026, 9, 28)):
    return [{"date": (start + timedelta(days=n)).isoformat(), "symbol": "GC=F",
             "open": 100 + n, "high": 108 + n, "low": 95 + n, "close": 101 + n}
            for n in range(5)]


def hourly_fixture(daily):
    result = []
    for day in daily:
        label = date.fromisoformat(day["date"])
        start = datetime.combine(label - timedelta(days=1), datetime.min.time(), NY).replace(hour=18).astimezone(UTC)
        for h in range(23):
            stamp = start + timedelta(hours=h)
            result.append({"bar_start_utc": stamp.isoformat(), "bar_end_utc_nominal": (stamp + timedelta(hours=1)).isoformat(),
                           "session_date": label.isoformat(), "symbol": "GC=F",
                           "open": day["open"], "high": day["high"] if h == 12 else day["open"] + 1,
                           "low": day["low"] if h == 7 else day["open"] - 1, "close": day["close"]})
    return result


def build(daily=None, hourly=None, cot=date(2026, 9, 22), as_of="2026-10-04T00:00:00+00:00", calendar=None):
    return build_outcomes([cot], daily or [], hourly or [], as_of=parse_time(as_of),
                          cot_start=date(2026, 7, 4), cot_end=date(2026, 10, 4), calendar_data=calendar)


class OutcomeTests(unittest.TestCase):
    def test_observation_date_maps_to_next_calendar_week(self):
        self.assertEqual(next_week(date(2026, 9, 22)), (date(2026, 9, 28), date(2026, 10, 2)))
        self.assertEqual(next_week(date(2026, 9, 29)), (date(2026, 10, 5), date(2026, 10, 9)))

    def test_calendar_month_scope_includes_13_cot_dates(self):
        self.assertEqual(months_before(date(2026, 10, 4), 3), date(2026, 7, 4))
        dates = [date(2026, 6, 30) + timedelta(days=7 * n) for n in range(15)]
        payload = build_outcomes(dates, [], [], as_of=parse_time("2026-10-04T00:00:00Z"),
                                 cot_start=date(2026, 7, 4), cot_end=date(2026, 10, 4))
        self.assertEqual(len(payload["rows"]), 13)
        self.assertEqual(payload["rows"][0]["cot_date"], "2026-07-07")
        self.assertEqual(payload["rows"][-1]["cot_date"], "2026-09-29")

    def test_pending_week_has_no_future_numbers_even_if_input_contains_them(self):
        row = build(daily_fixture(date(2026, 10, 5)), cot=date(2026, 9, 29))["rows"][0]
        self.assertEqual(row["coverage_status"], "PENDING")
        self.assertIsNone(row["open"])
        self.assertIsNone(row["high_date"])
        self.assertEqual(row["bars"], [])

    def test_ohlc_and_percentages_use_first_open_last_vendor_close(self):
        row = build(daily_fixture())["rows"][0]
        self.assertEqual((row["open"], row["close"], row["high"], row["low"]), (100, 105, 112, 95))
        self.assertAlmostEqual(row["change_pct"], 0.05)
        self.assertAlmostEqual(row["range_pct"], 0.17)
        self.assertEqual(row["coverage_status"], "COMPLETE_DAILY")
        self.assertIsNone(row["high_time_utc"])
        self.assertEqual(row["time_precision"], "day")

    def test_same_daily_bar_cannot_establish_extreme_order(self):
        daily = daily_fixture()
        daily[2].update(high=200, low=50)
        row = build(daily)["rows"][0]
        self.assertEqual(row["extreme_order"], "SAME_DAY_UNKNOWN")
        self.assertEqual(row["high_weekday"], "Wednesday")
        self.assertIsNone(row["high_time_range_taipei"])

    def test_full_hour_grid_reconciles_and_locates_hour_bucket(self):
        daily = daily_fixture()
        row = build(daily, hourly_fixture(daily))["rows"][0]
        self.assertEqual(row["hourly_coverage_status"], "COMPLETE_OBSERVED_HOURLY")
        self.assertEqual(row["high_time_precision"], "hour_bucket")
        self.assertTrue(row["high_first_hour_bucket_verified"])
        self.assertTrue(row["high_time_taipei"].endswith("+08:00"))
        start, end = row["high_time_range_utc"].values()
        self.assertEqual(parse_time(end) - parse_time(start), timedelta(hours=1))

    def test_mismatch_preserves_daily_price_and_nulls_only_affected_time(self):
        daily = daily_fixture()
        hourly = hourly_fixture(daily)
        hourly[-11]["high"] = 120
        row = build(daily, hourly)["rows"][0]
        self.assertEqual(row["high"], 112)
        self.assertEqual(row["high_time_reason"], "DAILY_HOURLY_EXTREME_MISMATCH")
        self.assertIsNone(row["high_time_utc"])
        self.assertEqual(row["low_time_precision"], "hour_bucket")
        self.assertEqual(row["time_precision"], "mixed")

    def test_daily_hourly_session_disagreement_nulls_time(self):
        daily = daily_fixture()
        hourly = hourly_fixture(daily)
        hourly[-11]["session_date"] = "2026-10-01"
        row = build(daily, hourly)["rows"][0]
        self.assertEqual(row["high_time_reason"], "DAILY_HOURLY_SESSION_MISMATCH")
        self.assertIsNone(row["high_time_utc"])

    def test_same_hour_bucket_order_is_unknown(self):
        daily = daily_fixture()
        daily[2].update(high=200, low=50)
        hourly = hourly_fixture(daily)
        hourly[2 * 23 + 7]["low"] = daily[2]["open"] - 1
        hourly[2 * 23 + 12]["low"] = 50
        row = build(daily, hourly)["rows"][0]
        self.assertEqual(row["extreme_order"], "SAME_BUCKET_UNKNOWN")

    def test_missing_hour_grid_does_not_prove_first_occurrence(self):
        daily = daily_fixture()
        daily[2].update(high=200, low=50)
        row = build(daily, hourly_fixture(daily)[1:])["rows"][0]
        self.assertEqual(row["hourly_coverage_status"], "PARTIAL")
        self.assertFalse(row["high_first_hour_bucket_verified"])
        self.assertEqual(row["high_time_precision"], "hour_bucket")
        self.assertEqual(row["extreme_order"], "SAME_DAY_UNKNOWN")

    def test_holiday_adjusts_daily_expectations_but_not_intraday_completeness(self):
        daily = daily_fixture(date(2026, 9, 7))[1:]
        calendar = {"holidays": [{"date": "2026-09-07", "exclude_daily": True}]}
        row = build(daily, hourly_fixture(daily), cot=date(2026, 9, 1), calendar=calendar)["rows"][0]
        self.assertEqual(row["expected_sessions"], 4)
        self.assertEqual(row["coverage_status"], "COMPLETE_DAILY")
        self.assertEqual(row["hourly_coverage_status"], "PARTIAL")
        self.assertIsNone(row["expected_hourly_bars"])

    def test_missing_daily_session_is_partial_not_completed(self):
        row = build(daily_fixture()[1:])["rows"][0]
        self.assertEqual(row["coverage_status"], "PARTIAL")
        self.assertEqual(row["missing_session_dates"], ["2026-09-28"])

    def test_in_progress_week_uses_closed_daily_bars_only(self):
        row = build(daily_fixture(), as_of="2026-09-30T13:00:00Z")["rows"][0]
        self.assertEqual(row["coverage_status"], "PARTIAL")
        self.assertEqual(row["observed_session_dates"], ["2026-09-28", "2026-09-29"])

    def test_open_week_before_first_daily_close_is_in_progress_not_missing(self):
        row = build(daily_fixture(), as_of="2026-09-28T02:00:00Z")["rows"][0]
        self.assertEqual(row["coverage_status"], "PARTIAL")
        self.assertEqual(row["week_state"], "IN_PROGRESS")
        self.assertIsNone(row["open"])
        self.assertEqual(row["week_start_at"], "2026-09-27T22:00:00+00:00")
        self.assertEqual(row["week_end_at"], "2026-10-02T21:00:00+00:00")

    def test_old_complete_week_preserved_with_provenance_but_current_gap_not_masked(self):
        dates = [date(2026, 7, 7), date(2026, 9, 22)]
        previous = build_outcomes(dates, daily_fixture(date(2026, 7, 13)) + daily_fixture(), [],
                                  as_of=parse_time("2026-10-04T00:00:00Z"), cot_start=date(2026, 7, 4), cot_end=date(2026, 10, 4),
                                  provenance={"daily": {"sha256": "original-source-hash"}})
        rebuilt = build_outcomes(dates, [], [], as_of=parse_time("2026-10-04T00:00:00Z"),
                                 cot_start=date(2026, 7, 4), cot_end=date(2026, 10, 4), previous_outcomes=previous,
                                 source_window_start=parse_time("2026-08-01T00:00:00Z"))
        old, current = rebuilt["rows"]
        self.assertEqual(old["coverage_status"], "COMPLETE_DAILY")
        self.assertEqual(old["archive_status"], "ARCHIVED_COMPLETE")
        self.assertEqual(old["high"], previous["rows"][0]["high"])
        self.assertEqual(rebuilt["archived_provenance"][old["archive_reference"]["provenance_id"]]["daily"]["sha256"], "original-source-hash")
        self.assertEqual(current["coverage_status"], "MISSING")
        self.assertIsNone(current["high"])
        self.assertEqual(current["archive_status"], "CURRENT_QUERY")
        # A second rotation retains the original evidence, not a growing chain.
        again = build_outcomes(dates, [], [], as_of=parse_time("2026-10-04T00:00:00Z"),
                               cot_start=date(2026, 7, 4), cot_end=date(2026, 10, 4), previous_outcomes=rebuilt,
                               source_window_start=parse_time("2026-08-02T00:00:00Z"))
        self.assertEqual(again["rows"][0]["archive_reference"], old["archive_reference"])
        self.assertEqual(again["archived_provenance"], rebuilt["archived_provenance"])

    def test_preservation_requires_query_boundary_and_never_freezes_partial(self):
        previous = build(daily_fixture()[1:])
        with self.assertRaisesRegex(ValueError, "explicit source query"):
            build_outcomes([date(2026, 9, 22)], [], [], as_of=parse_time("2026-10-04T00:00:00Z"),
                           cot_start=date(2026, 7, 4), cot_end=date(2026, 10, 4), previous_outcomes=previous)
        result = build_outcomes([date(2026, 9, 22)], [], [], as_of=parse_time("2026-10-04T00:00:00Z"),
                                cot_start=date(2026, 7, 4), cot_end=date(2026, 10, 4), previous_outcomes=previous,
                                source_window_start=parse_time("2026-10-03T00:00:00Z"))
        self.assertEqual(result["rows"][0]["coverage_status"], "MISSING")

    def test_utc_fields_are_utc_and_taipei_ranges_are_plus_eight(self):
        daily = daily_fixture()
        row = build(daily, hourly_fixture(daily))["rows"][0]
        for field in ("window_start_utc", "window_end_utc", "week_start_at", "week_end_at", "high_time_utc", "low_time_utc"):
            self.assertTrue(row[field].endswith("+00:00"), field)
        for side in ("high", "low"):
            self.assertTrue(row[f"{side}_time_taipei"].endswith("+08:00"))

    def test_null_and_snapshot_hourly_bars_are_excluded(self):
        daily = daily_fixture()
        hourly = hourly_fixture(daily)
        hourly[0]["open"] = ""
        hourly[1]["bar_start_utc"] = "2026-09-27T23:12:17Z"
        accepted, rejected = normalize_prices(hourly, "1h")
        self.assertEqual(len(accepted), 113)
        self.assertEqual(len(rejected), 2)

    def test_cross_feed_and_conflicting_duplicate_rejected(self):
        bad = daily_fixture()
        bad[0]["symbol"] = "XAUUSD"
        with self.assertRaisesRegex(RuntimeError, "Cross-feed"):
            build(bad)
        daily = daily_fixture()
        daily.append({**daily[0], "high": 200})
        with self.assertRaisesRegex(RuntimeError, "Conflicting duplicate"):
            build(daily)

    def test_ties_preserve_daily_dates_and_first_observed_bucket(self):
        daily = daily_fixture()
        daily[0]["high"] = 112
        row = build(daily, hourly_fixture(daily))["rows"][0]
        self.assertEqual(row["high_dates"], ["2026-09-28", "2026-10-02"])
        self.assertEqual(row["high_daily_tie_count"], 2)
        self.assertEqual(row["high_hour_bucket_tie_count"], 2)
        self.assertEqual(row["high_date"], "2026-09-28")

    def test_csv_preserves_nulls_and_has_no_python_repr_objects(self):
        daily = daily_fixture()
        payload = build(daily, hourly_fixture(daily))
        output = csv_output(payload)
        self.assertNotIn("{'", output)
        csv_row = next(csv.DictReader(io.StringIO(output)))
        self.assertEqual(csv_row["cot_date"], "2026-09-22")

    def test_twelve_calendar_months_and_leap_day_are_not_365_day_subtractions(self):
        self.assertEqual(months_before(date(2026, 10, 4), 12), date(2025, 10, 4))
        self.assertEqual(months_before(date(2024, 2, 29), 12), date(2023, 2, 28))
        dates = [date(2025, 9, 30)] + [date(2025, 10, 7) + timedelta(weeks=n) for n in range(52)]
        dates[dates.index(date(2025, 11, 11))] = date(2025, 11, 10)
        payload = build_outcomes(dates, [], [], as_of=parse_time("2026-10-04T00:00:00Z"))
        self.assertEqual(len(payload["rows"]), 52)
        self.assertEqual(payload["rows"][0]["cot_date"], "2025-10-07")
        self.assertIn("2025-11-10", [r["cot_date"] for r in payload["rows"]])
        self.assertEqual(payload["scope"]["scope_mode"], "ROLLING_CALENDAR_MONTHS")

    def test_all_history_includes_real_master_dates_and_preserves_future_pending(self):
        dates = [date(2009, 9, 1), date(2025, 11, 10), date(2026, 9, 22), date(2026, 9, 29)]
        payload = build_outcomes(dates, daily_fixture(), [], as_of=parse_time("2026-10-04T00:00:00Z"),
                                 all_history=True, cot_start=date(2026, 7, 4))
        self.assertEqual(len(payload["rows"]), 4)
        self.assertEqual(payload["scope"]["coverage_scope"], "ALL_MASTER")
        self.assertEqual(payload["scope"]["cot_start"], "2009-09-01")
        self.assertEqual(payload["rows"][1]["week_start"], "2025-11-17")
        self.assertEqual(payload["rows"][-1]["coverage_status"], "PENDING")
        self.assertIsNone(payload["rows"][-1]["close"])

    def test_half_hour_start_and_shortened_bar_are_valid_but_not_complete_grid(self):
        daily = daily_fixture()
        hourly = hourly_fixture(daily)
        original_start = parse_time(hourly[-11]["bar_start_utc"])
        hourly[-11]["bar_start_utc"] = (original_start + timedelta(minutes=30)).isoformat()
        row = build(daily, hourly)["rows"][0]
        self.assertEqual(row["observed_hourly_bars"], 115)
        self.assertEqual(row["hourly_coverage_status"], "PARTIAL")
        self.assertEqual(row["high_time_precision"], "hour_bucket")
        bounds = row["high_time_range_utc"]
        self.assertEqual(parse_time(bounds["end"]) - parse_time(bounds["start"]), timedelta(minutes=30))
        self.assertFalse(row["high_first_hour_bucket_verified"])

    def test_all_history_recalculates_daily_and_preserves_matching_archived_hourly(self):
        daily = daily_fixture()
        previous = build(daily, hourly_fixture(daily))
        kwargs = dict(as_of=parse_time("2026-10-04T00:00:00Z"), all_history=True,
                      previous_outcomes=previous, hourly_source_window_start=parse_time("2026-10-03T00:00:00Z"))
        result = build_outcomes([date(2026, 9, 22)], daily, [], **kwargs)
        row = result["rows"][0]
        self.assertEqual(row["archive_status"], "CURRENT_DAILY_WITH_ARCHIVED_HOURLY")
        self.assertEqual(row["high_time_utc"], previous["rows"][0]["high_time_utc"])
        self.assertIn(row["hourly_archive_reference"]["provenance_id"], result["archived_provenance"])
        again = build_outcomes([date(2026, 9, 22)], daily, [], **{**kwargs, "previous_outcomes": result})
        self.assertEqual(again["rows"][0]["hourly_archive_reference"], row["hourly_archive_reference"])
        revised = [dict(r) for r in daily]
        revised[-1]["high"] = 200
        changed = build_outcomes([date(2026, 9, 22)], revised, [], **kwargs)["rows"][0]
        self.assertEqual(changed["high"], 200)
        self.assertIsNone(changed["high_time_utc"])
        self.assertEqual(changed["high_time_reason"], "DAILY_CHANGED_ARCHIVED_HOURLY_NOT_REUSED")
        missing = build_outcomes([date(2026, 9, 22)], [], [], **kwargs)["rows"][0]
        self.assertEqual(missing["coverage_status"], "MISSING")
        self.assertIsNone(missing["high"])

    def test_old_daily_only_data_has_explicit_h1_retention_reason(self):
        payload = build_outcomes([date(2026, 9, 22)], daily_fixture(), [], all_history=True,
                                 as_of=parse_time("2026-10-04T00:00:00Z"),
                                 hourly_source_window_start=parse_time("2026-10-03T00:00:00Z"))
        row = payload["rows"][0]
        self.assertEqual(row["high_time_precision"], "day")
        self.assertIsNone(row["high_time_utc"])
        self.assertEqual(row["high_time_reason"], "NO_HOURLY_BARS_OUTSIDE_RETAINED_COVERAGE")

    def test_revised_schedule_does_not_create_actual_publication_timestamp(self):
        cot = date(2025, 10, 7)
        record = {"original_scheduled_release_date": "2025-10-10", "revised_publication_date": "2025-11-21",
                  "evidence_kind": "official_revised_schedule", "publication_delayed": True,
                  "evidence_sources": ["https://www.cftc.gov/PressRoom/PressReleases/9147-25"]}
        payload = build_outcomes([cot], [], [], all_history=True, as_of=parse_time("2026-10-04T00:00:00Z"),
                                 cot_release_calendar={"reports": [{"cot_date": cot.isoformat(), **record}]})
        row = payload["rows"][0]
        self.assertEqual(row["week_start"], "2025-10-13")
        self.assertEqual(row["research_availability_status"], "SCHEDULED_AFTER_WEEK_START")
        self.assertEqual(row["scheduled_release_relation"], "AFTER_OUTCOME_WEEK")
        self.assertFalse(row["no_lookahead_eligible"])
        self.assertIsNone(row["actual_cot_release_at_utc"])
        self.assertEqual(row["original_scheduled_release_date"], "2025-10-10")

    def test_monday_publication_schedule_is_after_sunday_session_open(self):
        record = {"cot_date": "2025-12-23", "scheduled_release_date": "2025-12-29",
                  "evidence_kind": "official_schedule", "evidence_sources": ["https://www.cftc.gov/example"]}
        row = build_outcomes([date(2025, 12, 23)], [], [], all_history=True,
                             as_of=parse_time("2026-10-04T00:00:00Z"), cot_release_calendar={"reports": [record]})["rows"][0]
        self.assertEqual(row["week_start_at"], "2025-12-28T23:00:00+00:00")
        self.assertEqual(row["scheduled_release_relation"], "DURING_OUTCOME_WEEK")
        self.assertTrue(row["not_ex_ante_available"])

    def test_normal_schedule_before_window_still_has_unknown_actual_release(self):
        record = {"cot_date": "2026-09-22", "scheduled_release_date": "2026-09-25",
                  "evidence_sources": ["https://www.cftc.gov/example"]}
        row = build_outcomes([date(2026, 9, 22)], daily_fixture(), [], all_history=True,
                             as_of=parse_time("2026-10-04T00:00:00Z"), cot_release_calendar={"reports": [record]})["rows"][0]
        self.assertEqual(row["research_availability_status"], "RELEASE_TIME_UNVERIFIED")
        self.assertIsNone(row["no_lookahead_eligible"])
        self.assertIsNone(row["actual_cot_release_at_utc"])

    def test_actual_publication_date_is_not_promoted_to_midnight_timestamp(self):
        record = {"cot_date": "2023-01-31", "actual_publication_date": "2023-02-24",
                  "evidence_kind": "official_publication_notice", "evidence_sources": ["https://www.cftc.gov/example"]}
        row = build_outcomes([date(2023, 1, 31)], [], [], all_history=True,
                             as_of=parse_time("2026-10-04T00:00:00Z"), cot_release_calendar={"reports": [record]})["rows"][0]
        self.assertEqual(row["actual_publication_date"], "2023-02-24")
        self.assertIsNone(row["actual_cot_release_at_utc"])
        self.assertEqual(row["research_availability_status"], "ACTUAL_PUBLICATION_DATE_AFTER_WEEK_START")
        self.assertFalse(row["no_lookahead_eligible"])

    def test_revised_release_window_does_not_fall_back_to_original_due_date(self):
        record = {"cot_date": "2013-10-08", "original_scheduled_release_date": "2013-10-11",
                  "planned_release_window_start": "2013-10-28", "planned_release_window_end": "2013-11-01",
                  "evidence_kind": "official_schedule_derived", "evidence_sources": ["https://www.cftc.gov/example"]}
        row = build_outcomes([date(2013, 10, 8)], [], [], all_history=True,
                             as_of=parse_time("2026-10-04T00:00:00Z"), cot_release_calendar={"reports": [record]})["rows"][0]
        self.assertIsNone(row["scheduled_release_date"])
        self.assertEqual(row["scheduled_release_relation"], "AFTER_OUTCOME_WEEK")
        self.assertFalse(row["no_lookahead_eligible"])

    def test_unverified_actual_timestamp_is_rejected(self):
        record = {"cot_date": "2026-09-22", "actual_release_at_utc": "2026-09-25T19:30:00Z"}
        with self.assertRaisesRegex(ValueError, "explicit verification"):
            build_outcomes([date(2026, 9, 22)], [], [], all_history=True,
                           as_of=parse_time("2026-10-04T00:00:00Z"), cot_release_calendar={"reports": [record]})

    def test_revised_historical_vintage_is_not_automatically_ex_ante_eligible(self):
        record = {"cot_date": "2019-03-26", "actual_publication_date": "2019-03-29",
                  "evidence_kind": "official_publication_notice", "evidence_sources": ["https://www.cftc.gov/example"],
                  "revision_risk": True, "revision_note": "Gold positions were revised on April 3."}
        row = build_outcomes([date(2019, 3, 26)], [], [], all_history=True,
                             as_of=parse_time("2026-10-04T00:00:00Z"), cot_release_calendar={"reports": [record]})["rows"][0]
        self.assertEqual(row["research_availability_status"], "ACTUAL_PUBLICATION_DATE_BEFORE_WEEK_START")
        self.assertTrue(row["point_in_time_vintage_unverified"])
        self.assertIsNone(row["no_lookahead_eligible"])

    def test_outside_active_scope_history_retains_original_source_reference(self):
        dates = [date(2025, 10, 7), date(2025, 11, 4)]
        old_daily = daily_fixture(date(2025, 10, 13))
        current_daily = daily_fixture(date(2025, 11, 10))
        previous = build_outcomes(dates, old_daily + current_daily, [],
                                  as_of=parse_time("2026-10-04T00:00:00Z"), provenance={"daily": {"sha256": "first-source"}})
        rotated = build_outcomes(dates, current_daily, [], as_of=parse_time("2026-11-04T00:00:00Z"),
                                 previous_outcomes=previous, source_window_start=parse_time("2025-11-01T00:00:00Z"))
        self.assertEqual([row["cot_date"] for row in rotated["rows"]], ["2025-11-04"])
        retained = rotated["retained_history_rows"][0]
        self.assertEqual(retained["cot_date"], "2025-10-07")
        self.assertEqual(retained["high"], previous["rows"][0]["high"])
        self.assertEqual(rotated["archived_provenance"][retained["archive_reference"]["provenance_id"]]["daily"]["sha256"], "first-source")


    def test_unchanged_partial_daily_keeps_qualified_hourly_without_coverage_promotion(self):
        daily = daily_fixture()[1:]
        previous = build(daily, hourly_fixture(daily))
        kwargs = dict(all_history=True, as_of=parse_time('2026-10-04T00:00:00Z'), previous_outcomes=previous, hourly_source_window_start=parse_time('2026-10-03T00:00:00Z'))
        row = build_outcomes([date(2026,9,22)],daily,[],**kwargs)['rows'][0]
        self.assertEqual(row['archive_status'],'CURRENT_DAILY_WITH_ARCHIVED_HOURLY')
        self.assertEqual(row['coverage_status'],'PARTIAL')
        self.assertEqual(row['hourly_coverage_status'],'PARTIAL')
        self.assertEqual(row['high_time_utc'],previous['rows'][0]['high_time_utc'])
        self.assertFalse(row['high_first_hour_bucket_verified'])
        previous['rows'][0]['expected_session_dates']=['2026-09-29','2026-09-30','2026-10-01','2026-10-02']
        changed=build_outcomes([date(2026,9,22)],daily,[],**kwargs)['rows'][0]
        self.assertEqual(changed['archive_status'],'CURRENT_QUERY')
        self.assertIsNone(changed['high_time_utc'])


class CalendarRecoveryTests(unittest.TestCase):
    def test_normal_trading_or_settlement_missing_bar_is_confirmed_gap(self):
        bars=daily_fixture(); missing=bars.pop(1)['date']
        for proof in [{'settlement_status':'normal_schedule'}, {'normal_trading_confirmed':True}]:
            with self.subTest(proof=proof):
                calendar={'holidays':[{'date':missing,'exclude_daily':False,'source_url':'https://example.invalid/official-notice',**proof}]}
                row=build(bars,calendar=calendar)['rows'][0]
                self.assertEqual(row['coverage_status'],'PARTIAL')
                self.assertEqual(row['daily_coverage_category'],'CONFIRMED_SOURCE_GAP')
                self.assertEqual(row['confirmed_source_gap_dates'],[missing])
                self.assertEqual(row['unverified_missing_session_dates'],[])
                self.assertEqual(row['observed_sessions'],4)
                self.assertEqual(row['expected_sessions'],5)
                self.assertEqual(row['open'],bars[0]['open'])
                self.assertEqual(row['close'],bars[-1]['close'])

    def test_copied_price_holiday_changes_labels_without_filling_prices(self):
        bars=daily_fixture(); missing=bars.pop(1)['date']
        calendar={'holidays':[{'date':missing,'exclude_daily':True,'settlement_status':'copied_from_previous_trade_date','source_url':'https://example.invalid/official-notice'}]}
        row=build(bars,calendar=calendar)['rows'][0]
        self.assertEqual(row['coverage_status'],'COMPLETE_DAILY')
        self.assertEqual(row['daily_coverage_category'],'VERIFIED_HOLIDAY_SHORTENED_COMPLETE')
        self.assertEqual(row['observed_sessions'],4)
        self.assertEqual(row['expected_sessions'],4)
        self.assertEqual(len(row['bars']),4)
        self.assertTrue(all(b['date']!=missing for b in row['bars']))

    def test_future_week_has_no_historical_gap_diagnosis(self):
        row=build(cot=date(2026,9,29))['rows'][0]
        self.assertEqual(row['coverage_status'],'PENDING')
        for field in ['missing_session_dates','quarantined_ohlc_dates','source_null_dates','confirmed_source_gap_dates','unverified_missing_session_dates']:
            self.assertEqual(row[field],[])
        self.assertIsNone(row['open'])


if __name__ == "__main__":
    unittest.main()
