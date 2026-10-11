"""Regression for the 2026-10-06 GHPR similarity cutoff, without runtime data.

The four feature triples and current vector below were copied verbatim from the
failed 20261011T011707Z-51845eda master CSV. No test reads that run or publishes
outputs. All CSV fixtures and matplotlib caches stay on the D: test volume.
"""
from __future__ import annotations

import csv
import math
import os
from pathlib import Path
import sys
import tempfile
import unittest

sys.dont_write_bytecode = True
PROJECT_ROOT = Path(__file__).resolve().parents[1]
TEST_TMP = Path(os.environ.get("GHPR_TEST_TMP", PROJECT_ROOT.parent / "test-tmp"))
if os.name == "nt" and TEST_TMP.resolve().drive.upper() != "D:":
    raise RuntimeError("GHPR similarity test temporary files must stay on D:")
TEST_TMP.mkdir(parents=True, exist_ok=True)
os.environ["TMP"] = str(TEST_TMP)
os.environ["TEMP"] = str(TEST_TMP)
os.environ["MPLCONFIGDIR"] = str(TEST_TMP / "matplotlib")
sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd
from src import historical_similarity_engine as engine

# Date, actual gold close, MM percentile, Producer percentile, OI percentile.
ACTUAL_TIES = (
    ("2014-02-11", "1290.0999755859375", "0.21794871794871795", "0.9166666666666666", "0.038461538461538464"),
    ("2014-04-15", "1300.0", "0.358974358974359", "0.8525641025641025", "0.02564102564102564"),
    ("2014-04-29", "1296.0", "0.391025641025641", "0.8269230769230769", "0.08333333333333333"),
    ("2021-10-12", "1759.300048828125", "0.28205128205128205", "0.9423076923076923", "0.2564102564102564"),
)
CURRENT_FEATURES = ("0.3269230769230769", "0.9166666666666666", "0.1282051282051282")
CURRENT_DATE = "2026-10-06"
TIE_DATES = [row[0] for row in ACTUAL_TIES]


class SimilarityRankingTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="similarity-ranking-", dir=TEST_TMP)
        self.addCleanup(self.temporary.cleanup)
        self.master_path = Path(self.temporary.name) / "master.csv"
        self.control_rows = []
        for index, day in enumerate(pd.date_range("2010-01-05", periods=19, freq="W-TUE")):
            features = [float(value) for value in CURRENT_FEATURES]
            features[0] += (index + 1) * 0.0001
            self.control_rows.append((day.strftime("%Y-%m-%d"), "1500.0", *map(repr, features)))
        # These 52 perfect matches would dominate if recent-row exclusion broke.
        self.excluded_rows = [(day.strftime("%Y-%m-%d"), "4187.10009765625", *CURRENT_FEATURES)
                              for day in pd.date_range(end=CURRENT_DATE, periods=52, freq="W-TUE")]
        self.write_fixture()

    def write_fixture(self, extra=()):
        rows = [*self.control_rows, *ACTUAL_TIES, *extra, *self.excluded_rows]
        # Deliberately reverse input order: date order must be explicit.
        with self.master_path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(["date", "gold_close", *engine.FEATURE_COLUMNS])
            writer.writerows(reversed(rows))

    def compute(self, top_n):
        return engine.compute_current_similarity(self.master_path, top_n=top_n, exclude_recent_weeks=52)

    def test_all_four_real_cutoff_ties_are_in_ascending_date_order(self):
        result, _, _, metadata = self.compute(23)
        self.assertEqual(result.iloc[19:]["date"].dt.strftime("%Y-%m-%d").tolist(), TIE_DATES)
        self.assertEqual(result["rank"].tolist(), list(range(1, 24)))
        self.assertEqual(metadata["candidate_rows_after_feature_drop"], 23)
        self.assertEqual(metadata["exclude_recent_weeks"], 52)
        self.assertEqual(metadata["latest_date"], CURRENT_DATE)
        keys = [engine.similarity_rank_key(score) for score in result.iloc[19:]["similarity_score"]]
        self.assertEqual(len(set(keys)), 1, "Actual cutoff cases must share the agreed precision key")
        excluded_dates = {row[0] for row in self.excluded_rows}
        self.assertTrue(excluded_dates.isdisjoint(result["date"].dt.strftime("%Y-%m-%d")))

    def test_top_twenty_contains_the_earliest_real_tie_after_nineteen_closer_controls(self):
        result, _, _, _ = self.compute(20)
        actual = result["date"].dt.strftime("%Y-%m-%d").tolist()
        expected = {row[0] for row in self.control_rows} | {"2014-02-11"}
        self.assertEqual(len(actual), 20)
        self.assertEqual(set(actual), expected)
        self.assertEqual(actual[-1], "2014-02-11")
        self.assertTrue(set(TIE_DATES[1:]).isdisjoint(actual))

    def test_sort_quantization_preserves_raw_distances_scores_and_report_schema(self):
        result, current_vector, _, metadata = self.compute(23)
        loaded = engine.load_master_dataset(self.master_path).set_index("date")
        current = loaded.loc[pd.Timestamp(CURRENT_DATE)]
        # Preserve the original pandas vectorized arithmetic exactly. A Python
        # scalar sum can differ by one ULP even before any ranking takes place.
        difference_points = pd.DataFrame({column: ((loaded[column] - current[column]) * 100).abs()
                                          for column in engine.FEATURE_COLUMNS})
        legacy_distance = difference_points.sum(axis=1)
        legacy_normalized = (legacy_distance / 300 * 100).clip(lower=0, upper=100)
        legacy_score = 100 - legacy_normalized
        saw_unrounded_score = False
        for row in result.itertuples(index=False):
            raw_distance = legacy_distance.loc[row.date]
            raw_normalized = legacy_normalized.loc[row.date]
            raw_score = legacy_score.loc[row.date]
            self.assertEqual(row.distance, raw_distance)
            self.assertEqual(row.normalized_distance, raw_normalized)
            self.assertEqual(row.similarity_score, raw_score)
            saw_unrounded_score |= row.similarity_score != round(row.similarity_score, 10)
        self.assertTrue(saw_unrounded_score, "Fixture must detect accidental rounding of displayed scores")
        self.assertNotIn("_similarity_rank_key", result.columns)
        report = engine.build_historical_similarity_report(result, current_vector, metadata)
        self.assertNotIn("_similarity_rank_key", report.columns)
        self.assertEqual(report["similarity_score"].tolist(), result.head(20)["similarity_score"].tolist())
        self.assertEqual(report.iloc[-1]["historical_date"], "2014-02-11")

    def test_genuinely_higher_neighbor_outranks_earlier_dates_beyond_key_resolution(self):
        first_tie = [float(value) for value in ACTUAL_TIES[0][2:]]
        current = [float(value) for value in CURRENT_FEATURES]
        tied_distance = sum(abs(old - present) * 100 for old, present in zip(first_tie, current))
        # Improve the score by about 1e-8: roughly 100 precision bins, yet close
        # enough to catch a coarser rounding rule that would wrongly use date.
        better = current.copy()
        better[0] += tied_distance / 100 - 3e-10
        neighbor_date = "2024-01-02"
        self.write_fixture(extra=[(neighbor_date, "1600.0", *map(repr, better))])
        result, _, _, _ = self.compute(24)
        dates = result["date"].dt.strftime("%Y-%m-%d").tolist()
        self.assertEqual(dates[19], neighbor_date)
        self.assertEqual(dates[20:], TIE_DATES)
        score = result.loc[result["date"] == pd.Timestamp(neighbor_date), "similarity_score"].iloc[0]
        tie_scores = result.loc[result["date"].isin(pd.to_datetime(TIE_DATES)), "similarity_score"]
        self.assertGreater(score - tie_scores.max(), 1e-10)
        self.assertGreater(engine.similarity_rank_key(score), max(map(engine.similarity_rank_key, tie_scores)))

    def test_rank_key_uses_half_up_at_boundary_instead_of_bankers_rounding(self):
        self.assertEqual(engine.SIMILARITY_RANK_SCALE, 10**10)
        boundary = 2.5 / 10**10
        self.assertEqual(boundary * 10**10, 2.5)
        self.assertEqual(round(boundary * 10**10), 2)
        self.assertEqual(engine.similarity_rank_key(boundary), 3)
        self.assertEqual(engine.similarity_rank_key(math.nextafter(boundary, -math.inf)), 2)
        self.assertEqual(engine.similarity_rank_key(math.nextafter(boundary, math.inf)), 3)


if __name__ == "__main__":
    unittest.main()

