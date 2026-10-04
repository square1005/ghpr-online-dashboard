"""Regression tests for authoritative freshness and source isolation.

These tests never contact a data provider.  Disposable fixtures stay on the
same data volume as the candidate checkout (or GHPR_TEST_TMP).
"""
from __future__ import annotations

import json
import hashlib
import io
from contextlib import redirect_stdout
from datetime import datetime, timedelta, timezone
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch

sys.dont_write_bytecode = True
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd
import requests
from src import build_master_dataset as master
from src import data_freshness_diagnostics as freshness

SOURCE_META = {"symbol": "GC=F", "instrumentType": "FUTURE", "dataGranularity": "1d",
               "exchangeTimezoneName": "America/New_York"}


class DataVolumeFixtures(unittest.TestCase):
    def setUp(self):
        scratch = Path(os.environ.get("GHPR_TEST_TMP", PROJECT_ROOT.parent / "test-tmp"))
        scratch.mkdir(parents=True, exist_ok=True)
        self.temporary = tempfile.TemporaryDirectory(prefix="ghpr-sources-", dir=scratch)
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)


class RawSourceRefreshTests(DataVolumeFixtures):
    def test_current_cftc_network_failure_rejects_stale_cache_and_preserves_it(self):
        cached = self.root / master.CFTC_CURRENT_FILE
        original = b"previous verified CFTC snapshot\n"
        cached.write_bytes(original)
        with patch.object(master, "COT_RAW_DIR", self.root), patch.object(
            master.requests, "get", side_effect=requests.ConnectionError("provider unavailable")
        ):
            with self.assertRaises(RuntimeError):
                master.ensure_current_cot_report(force=True)
        self.assertEqual(cached.read_bytes(), original)

    def test_current_cftc_html_rejects_stale_cache_and_preserves_it(self):
        cached = self.root / master.CFTC_CURRENT_FILE
        original = b"previous verified CFTC snapshot\n"
        cached.write_bytes(original)
        response = Mock(content=b"<html>service unavailable</html>")
        response.raise_for_status.return_value = None
        with patch.object(master, "COT_RAW_DIR", self.root), patch.object(
            master.requests, "get", return_value=response
        ):
            with self.assertRaises(RuntimeError):
                master.ensure_current_cot_report(force=True)
        self.assertEqual(cached.read_bytes(), original)

    def test_forced_gold_refresh_does_not_call_spot_or_benchmark_fallbacks(self):
        def successful_gc_download(output, end_year, errors):
            output.write_text("Date,Close,Source\n2026-10-02,3900,Yahoo Finance GC=F\n", encoding="utf-8")
            return True

        with patch.object(master, "GOLD_RAW_DIR", self.root), patch.object(
            master, "download_yahoo_chart", side_effect=successful_gc_download
        ) as yahoo, patch.object(master, "download_csv", create=True) as alternate:
            path = master.ensure_gold_price_csv(end_year=2026, force=True)
        yahoo.assert_called_once()
        alternate.assert_not_called()
        self.assertEqual(path.name, "gold_price.csv")
        self.assertIn("GC=F", path.read_text(encoding="utf-8"))

    def test_failed_forced_gold_refresh_does_not_report_cached_file_as_success(self):
        cached = self.root / "gold_price.csv"
        original = "Date,Close,Source\n2026-09-22,3700,Yahoo Finance GC=F\n"
        cached.write_text(original, encoding="utf-8")
        with patch.object(master, "GOLD_RAW_DIR", self.root), patch.object(
            master, "download_yahoo_chart", return_value=False
        ), patch.object(master, "download_csv", return_value=False, create=True), patch.object(
            master, "csv_is_daily_enough", return_value=True
        ):
            with self.assertRaises(RuntimeError):
                master.ensure_gold_price_csv(end_year=2026, force=True)
        self.assertEqual(cached.read_text(encoding="utf-8"), original)

    def test_raw_gold_selection_is_not_changed_by_alphabetically_earlier_feed(self):
        target = self.root / "gold_price.csv"
        target.write_text("Date,Close,Source\n2026-10-02,3900,Yahoo Finance GC=F\n", encoding="utf-8")
        (self.root / "000_xauusd.csv").write_text("Date,Close,Source\n2026-10-02,3850,XAUUSD\n", encoding="utf-8")
        with patch.object(master, "GOLD_RAW_DIR", self.root):
            self.assertEqual(master.find_gold_price_csv(), target)


class ProviderPayloadValidationTests(DataVolumeFixtures):
    CFTC_HEADER = [
        "Market_and_Exchange_Names", "Report_Date_as_YYYY-MM-DD", "Open_Interest_All",
        "M_Money_Positions_Long_All", "M_Money_Positions_Short_All",
        "Prod_Merc_Positions_Long_All", "Prod_Merc_Positions_Short_All",
        "Swap_Positions_Long_All", "Swap__Positions_Short_All", "FutOnly_or_Combined",
    ]

    def test_current_cftc_records_observation_separately_from_unverified_publication_time(self):
        response = Mock(content=(master.GOLD_MARKET_NAME + ",2026-09-29,1000,300,100,100,300,100,100,FutOnly\n").encode("latin1"),
                        headers={"Last-Modified": "Fri, 02 Oct 2026 19:32:00 GMT"})
        response.raise_for_status.return_value = None
        with patch.object(master, "COT_RAW_DIR", self.root), patch.object(
            master, "current_cot_header", return_value=self.CFTC_HEADER
        ), patch.object(master.requests, "get", return_value=response), patch.object(master, "record_source") as record:
            output = master.ensure_current_cot_report(force=True)
        self.assertIn("2026-09-29", output.read_text(encoding="latin1"))
        source_name, metadata = record.call_args.args
        self.assertEqual(source_name, "cftc")
        self.assertEqual(metadata["observation_date"], "2026-09-29")
        self.assertIsNone(metadata["actual_publication_at_utc"])
        self.assertEqual(metadata["sha256"], hashlib.sha256(output.read_bytes()).hexdigest())

    def test_combined_cftc_report_cannot_replace_futures_only_snapshot(self):
        output = self.root / master.CFTC_CURRENT_FILE
        output.write_bytes(b"previous futures-only snapshot")
        response = Mock(content=(master.GOLD_MARKET_NAME + ",2026-09-29,1000,300,100,100,300,100,100,Combined\n").encode("latin1"))
        response.raise_for_status.return_value = None
        with patch.object(master, "COT_RAW_DIR", self.root), patch.object(
            master, "current_cot_header", return_value=self.CFTC_HEADER
        ), patch.object(master.requests, "get", return_value=response), patch.object(master, "record_source") as record:
            with self.assertRaisesRegex(RuntimeError, "futures-only"):
                master.ensure_current_cot_report(force=True)
        self.assertEqual(output.read_bytes(), b"previous futures-only snapshot")
        record.assert_not_called()

    def test_yahoo_response_for_wrong_symbol_is_rejected_before_replacing_cache(self):
        output = self.root / "gold_price.csv"
        output.write_bytes(b"verified GC cache")
        response = Mock()
        response.raise_for_status.return_value = None
        response.json.return_value = {"chart": {"result": [{"meta": {**SOURCE_META, "symbol": "XAUUSD=X"}}]}}
        errors = []
        with patch.object(master.requests, "get", return_value=response):
            self.assertFalse(master.download_yahoo_chart(output, 2026, errors))
        self.assertEqual(output.read_bytes(), b"verified GC cache")
        self.assertTrue(any("GC=F" in error and "FUTURE" in error for error in errors))

    def test_impossible_ohlc_is_rejected_before_replacing_gc_cache(self):
        output = self.root / "gold_price.csv"
        output.write_bytes(b"verified GC cache")
        response = Mock()
        response.raise_for_status.return_value = None
        response.json.return_value = {"chart": {"result": [{
            "meta": dict(SOURCE_META), "timestamp": [int(datetime(2026, 9, 22, 12, tzinfo=timezone.utc).timestamp())],
            "indicators": {"quote": [{"open": [100], "high": [99], "low": [98], "close": [101], "volume": [1]}]},
        }]}}
        errors = []
        with patch.object(master.requests, "get", return_value=response):
            self.assertFalse(master.download_yahoo_chart(output, 2026, errors))
        self.assertEqual(output.read_bytes(), b"verified GC cache")
        self.assertTrue(any("invalid OHLC" in error for error in errors))


class PriceAlignmentTests(unittest.TestCase):
    @staticmethod
    def cot(report_date):
        return pd.DataFrame({"date": pd.to_datetime([report_date]), "mm_long": [100]})

    @staticmethod
    def gold(dates, closes):
        return pd.DataFrame({"date": pd.to_datetime(dates), "gold_close": closes})

    def test_alignment_allows_four_calendar_day_holiday_gap_without_future_leakage(self):
        result = master.align_gold_price(
            self.cot("2026-09-22"), self.gold(["2026-09-18", "2026-09-23"], [3900.0, 9999.0])
        )
        self.assertEqual(result.loc[0, "gold_close"], 3900.0)
        self.assertEqual(result.loc[0, "date"], pd.Timestamp("2026-09-22"))

    def test_alignment_rejects_repeating_a_five_day_old_close(self):
        with self.assertRaises((ValueError, RuntimeError)):
            master.align_gold_price(self.cot("2026-09-22"), self.gold(["2026-09-17"], [3900.0]))

    def test_alignment_rejects_only_available_future_close(self):
        with self.assertRaises((ValueError, RuntimeError)):
            master.align_gold_price(self.cot("2026-09-22"), self.gold(["2026-09-23"], [9999.0]))


class SourceFreshnessTests(DataVolumeFixtures):
    NOW = datetime(2026, 10, 4, 14, 35, tzinfo=timezone.utc)

    def setUp(self):
        super().setUp()
        self.status_path = self.root / "source_status.json"
        self.master_path = self.root / "master.csv"
        self.hub_path = self.root / "hub.json"
        self.sources = {}
        for name, relative in (("cftc", "data/raw/cot/fut_disagg_txt_current.csv"),
                               ("gold", "data/raw/gold_price/gold_price.csv")):
            path = self.root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(f"verified {name} provider response\n".encode("utf-8"))
            self.sources[name] = {
                "observation_date": "2026-09-29" if name == "cftc" else "2026-10-02",
                "fetched_at_utc": self.NOW.isoformat(),
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            }
        self.write_status()
        self.write_components("2026-09-29")
        self.addCleanup(patch.stopall)
        patch.object(freshness, "PROJECT_ROOT", self.root).start()
        patch.object(freshness, "SOURCE_STATUS_PATH", self.status_path).start()
        patch.object(freshness, "MASTER_PATH", self.master_path).start()
        patch.object(freshness, "component_specs", return_value=[
            freshness.ComponentSpec("master", self.master_path, freshness.latest_csv_date),
            freshness.ComponentSpec("hub_summary", self.hub_path, freshness.hub_summary_date),
        ]).start()

    def write_status(self):
        self.status_path.write_text(json.dumps(self.sources), encoding="utf-8")

    def write_components(self, day):
        self.master_path.write_text(f"date\n{day}\n", encoding="utf-8")
        self.hub_path.write_text(json.dumps({"date": day}), encoding="utf-8")

    def diagnostics_at(self, now=None):
        source_check = freshness.source_freshness(now=now or self.NOW)
        with patch.object(freshness, "source_freshness", return_value=source_check):
            return freshness.build_diagnostics()

    def test_self_consistent_old_outputs_do_not_hide_newer_official_cftc(self):
        self.write_components("2026-09-22")
        diagnostics = self.diagnostics_at()
        self.assertEqual(diagnostics["expected_latest_date"], "2026-09-29")
        self.assertEqual(diagnostics["overall_status"], "STALE")
        self.assertTrue(all(not row["is_current"] for row in diagnostics["components"]))

    def test_recent_verified_official_source_and_matching_outputs_are_current(self):
        diagnostics = self.diagnostics_at()
        self.assertEqual(diagnostics["overall_status"], "OK")
        self.assertEqual(diagnostics["source_check"]["errors"], [])

    def test_source_check_older_than_36_hours_is_unverified_even_when_dates_match(self):
        self.sources["cftc"]["fetched_at_utc"] = (self.NOW - timedelta(hours=37)).isoformat()
        self.write_status()
        diagnostics = self.diagnostics_at()
        self.assertEqual(diagnostics["overall_status"], "SOURCE_UNVERIFIED")
        self.assertTrue(any("cftc" in error and "not recent" in error
                            for error in diagnostics["source_check"]["errors"]))

    def test_changed_raw_file_invalidates_download_verification(self):
        (self.root / "data/raw/gold_price/gold_price.csv").write_bytes(b"changed after download")
        diagnostics = self.diagnostics_at()
        self.assertEqual(diagnostics["overall_status"], "SOURCE_UNVERIFIED")
        self.assertTrue(any("gold" in error and "hash" in error
                            for error in diagnostics["source_check"]["errors"]))

    def test_missing_source_metadata_does_not_fall_back_to_master_as_authority(self):
        self.status_path.unlink()
        diagnostics = self.diagnostics_at()
        self.assertIsNone(diagnostics["expected_latest_date"])
        self.assertEqual(diagnostics["overall_status"], "SOURCE_UNVERIFIED")
        self.assertTrue(all(not row["is_current"] for row in diagnostics["components"]))

    def test_just_fetched_old_official_report_is_marked_awaiting_release(self):
        self.sources["cftc"]["observation_date"] = "2026-09-22"
        self.write_status()
        self.write_components("2026-09-22")
        diagnostics = self.diagnostics_at()
        self.assertEqual(diagnostics["expected_latest_date"], "2026-09-22")
        self.assertEqual(diagnostics["overall_status"], "AWAITING_RELEASE")
        self.assertEqual(diagnostics["source_check"]["release_state"], "awaiting_scheduled_release")
        self.assertEqual(diagnostics["source_check"]["normal_schedule_observation_date"], "2026-09-29")

    def test_normal_release_expectation_changes_at_friday_1530_new_york(self):
        before = datetime(2026, 10, 2, 19, 29, tzinfo=timezone.utc)
        after = datetime(2026, 10, 2, 19, 30, tzinfo=timezone.utc)
        self.sources["cftc"]["observation_date"] = "2026-09-22"
        for source in self.sources.values():
            source["fetched_at_utc"] = before.isoformat()
        self.write_status()
        early = freshness.source_freshness(before)
        late = freshness.source_freshness(after)
        self.assertEqual(early["normal_schedule_observation_date"], "2026-09-22")
        self.assertEqual(early["release_state"], "available")
        self.assertEqual(late["normal_schedule_observation_date"], "2026-09-29")
        self.assertEqual(late["release_state"], "awaiting_scheduled_release")

    def test_future_clock_skew_does_not_pass_recent_verification(self):
        self.sources["gold"]["fetched_at_utc"] = (self.NOW + timedelta(hours=1)).isoformat()
        self.write_status()
        self.assertEqual(self.diagnostics_at()["overall_status"], "SOURCE_UNVERIFIED")

    def test_strict_cli_rejects_unverified_or_inconsistent_data_but_allows_verified_delay(self):
        for status in ("OK", "AWAITING_RELEASE", "STALE", "PARTIAL_STALE", "SOURCE_UNVERIFIED", "ERROR"):
            with self.subTest(status=status), patch.object(
                freshness, "write_diagnostics", return_value={"overall_status": status}
            ), redirect_stdout(io.StringIO()):
                self.assertEqual(freshness.main(["--strict"]),
                                 0 if status in {"OK", "AWAITING_RELEASE"} else 1)


if __name__ == "__main__":
    unittest.main()


