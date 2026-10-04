"""Pure weekly scheduling regressions; never start a scheduler or worker."""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timedelta, timezone
from pathlib import Path
import sys
import unittest

sys.dont_write_bytecode = True
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
import auto_scheduler as scheduler

UTC = timezone.utc
TAIPEI = timezone(timedelta(hours=8))
TODAY = datetime(2026, 10, 4, 16, 30, tzinfo=UTC)
THIS_DUE = datetime(2026, 10, 4, 0, 0, tzinfo=UTC)
NEXT_DUE = datetime(2026, 10, 11, 0, 0, tzinfo=UTC)


def published_success(verified_at="2026-10-04T16:00:00+00:00", reason="manual"):
    return {
        "status": "success", "run_id": "verified-run-123",
        "published_commit": "123456789abcdef", "publication_verified_at_utc": verified_at,
        "publication_state": "verified_on_github_main", "trigger_reason": reason,
        "scheduler_invocation": reason != "manual",
    }


class WeeklyCalendarTests(unittest.TestCase):
    def test_october_4_after_slot_has_october_11_as_next_run(self):
        self.assertEqual(scheduler.latest_due(TODAY), THIS_DUE)
        self.assertEqual(scheduler.next_slot(TODAY), NEXT_DUE)

    def test_exact_slot_returns_strictly_next_sunday(self):
        self.assertEqual(scheduler.latest_due(THIS_DUE), THIS_DUE)
        self.assertEqual(scheduler.next_slot(THIS_DUE), NEXT_DUE)

    def test_taipei_sunday_eight_am_is_the_utc_week_boundary(self):
        before = datetime(2026, 10, 4, 7, 59, 59, tzinfo=TAIPEI)
        at_slot = datetime(2026, 10, 4, 8, 0, tzinfo=TAIPEI)
        self.assertEqual(scheduler.latest_due(before), datetime(2026, 9, 27, tzinfo=UTC))
        self.assertEqual(scheduler.next_slot(before), THIS_DUE)
        self.assertEqual(scheduler.latest_due(at_slot), THIS_DUE)
        self.assertEqual(scheduler.next_slot(at_slot), NEXT_DUE)
        self.assertEqual(scheduler.latest_due(at_slot).tzinfo, UTC)

    def test_year_boundary_keeps_sunday_calendar_semantics(self):
        saturday = datetime(2027, 1, 2, 23, 59, tzinfo=UTC)
        self.assertEqual(scheduler.latest_due(saturday), datetime(2026, 12, 27, tzinfo=UTC))
        self.assertEqual(scheduler.next_slot(saturday), datetime(2027, 1, 3, tzinfo=UTC))

    def test_naive_scheduler_time_is_rejected(self):
        for function in (scheduler.latest_due, scheduler.next_slot):
            with self.subTest(function=function.__name__), self.assertRaises(ValueError):
                function(datetime(2026, 10, 4, 8))
        with self.assertRaises(ValueError):
            scheduler.weekly_plan(datetime(2026, 10, 4, 8), {}, {})


class VerifiedCompletionTests(unittest.TestCase):
    def test_manual_publication_can_satisfy_week_without_becoming_scheduled(self):
        evidence = scheduler.verified_completion(published_success(), TODAY)
        self.assertIsNotNone(evidence)
        self.assertEqual(evidence["week_key"], "2026-10-04")
        self.assertEqual(evidence["run_id"], "verified-run-123")
        self.assertEqual(evidence["trigger_reason"], "manual")
        self.assertEqual(evidence["published_commit"], "123456789abcdef")

    def test_only_verified_successful_publication_can_seed_completion(self):
        invalid_cases = {
            "failed_run": {"status": "failed"},
            "missing_commit": {"published_commit": None},
            "empty_commit": {"published_commit": ""},
            "missing_verification": {"publication_verified_at_utc": None},
            "invalid_timestamp": {"publication_verified_at_utc": "not a timestamp"},
            "naive_timestamp": {"publication_verified_at_utc": "2026-10-04T16:00:00"},
            "future_verification": {"publication_verified_at_utc": "2026-10-04T17:00:00+00:00"},
        }
        for label, override in invalid_cases.items():
            last_good = {**published_success(), **override}
            with self.subTest(case=label):
                self.assertIsNone(scheduler.verified_completion(last_good, TODAY))
        self.assertIsNone(scheduler.verified_completion({}, TODAY))

    def test_local_only_success_is_not_a_verified_publication(self):
        local = {"status": "success", "run_id": "dry-run", "trigger_reason": "manual",
                 "last_success_at_utc": "2026-10-04T16:00:00+00:00",
                 "publication_state": "not_requested_local_validation_only"}
        self.assertIsNone(scheduler.verified_completion(local, TODAY))
        self.assertTrue(scheduler.weekly_plan(TODAY, {}, local)["should_run"])

    def test_publication_timestamp_is_converted_before_assigning_completion_week(self):
        before = scheduler.verified_completion(published_success("2026-10-04T07:59:59+08:00"), TODAY)
        after = scheduler.verified_completion(published_success("2026-10-04T08:00:00+08:00"), TODAY)
        self.assertEqual(before["week_key"], "2026-09-27")
        self.assertEqual(after["week_key"], "2026-10-04")
        self.assertEqual(after["verified_at_utc"], THIS_DUE.isoformat())


class WeeklyPlanningTests(unittest.TestCase):
    def test_today_manual_success_seeds_completion_and_defers_to_october_11(self):
        last_good = published_success()
        original = deepcopy(last_good)
        plan = scheduler.weekly_plan(TODAY, {}, last_good)
        self.assertEqual(plan["week_key"], "2026-10-04")
        self.assertFalse(plan["should_run"])
        self.assertEqual(plan["last_completed_week_key"], "2026-10-04")
        self.assertEqual(plan["planned_next_run_utc"], NEXT_DUE.isoformat())
        self.assertEqual(plan["completion_evidence"]["trigger_reason"], "manual")
        self.assertEqual(last_good, original, "Planning must not relabel the saved manual run")

    def test_persisted_completion_survives_restart_without_last_good_file(self):
        evidence = {"week_key": "2026-10-04", "run_id": "persisted-run", "trigger_reason": "manual"}
        previous = {"last_completed_week_key": "2026-10-04", "completion_evidence": evidence}
        original = deepcopy(previous)
        plan = scheduler.weekly_plan(TODAY, previous, {}, attempted_week_key=None)
        self.assertFalse(plan["should_run"])
        self.assertEqual(plan["planned_next_run_utc"], NEXT_DUE.isoformat())
        self.assertEqual(plan["completion_evidence"], evidence)
        self.assertEqual(previous, original)

    def test_offline_catchup_runs_only_the_latest_due_week(self):
        previous = {"last_completed_week_key": "2026-09-13"}
        old_success = published_success("2026-09-13T01:00:00+00:00", "scheduled_slot")
        plan = scheduler.weekly_plan(TODAY, previous, old_success)
        self.assertTrue(plan["should_run"])
        self.assertEqual(plan["due"], THIS_DUE)
        self.assertEqual(plan["week_key"], "2026-10-04")
        self.assertEqual(plan["planned_next_run_utc"], THIS_DUE.isoformat())
        self.assertEqual(plan["last_completed_week_key"], "2026-09-13")

    def test_failed_attempt_is_not_repeated_in_a_tight_loop_but_restart_can_catch_up(self):
        previous = {"last_completed_week_key": "2026-09-27"}
        failed = {**published_success(), "status": "failed"}
        same_process = scheduler.weekly_plan(TODAY, previous, failed, attempted_week_key="2026-10-04")
        restarted = scheduler.weekly_plan(TODAY, previous, failed, attempted_week_key=None)
        self.assertFalse(same_process["should_run"])
        self.assertEqual(same_process["planned_next_run_utc"], NEXT_DUE.isoformat())
        self.assertEqual(same_process["last_completed_week_key"], "2026-09-27")
        self.assertTrue(restarted["should_run"])
        self.assertEqual(restarted["due"], THIS_DUE)

    def test_last_weeks_attempt_does_not_suppress_new_weeks_due_run(self):
        plan = scheduler.weekly_plan(NEXT_DUE, {"last_completed_week_key": "2026-10-04"},
                                     published_success(), attempted_week_key="2026-10-04")
        self.assertTrue(plan["should_run"])
        self.assertEqual(plan["week_key"], "2026-10-11")
        self.assertEqual(plan["due"], NEXT_DUE)

    def test_older_last_good_does_not_overwrite_newer_persisted_completion(self):
        evidence = {"week_key": "2026-10-04", "run_id": "newer", "trigger_reason": "scheduled_slot"}
        previous = {"last_completed_week_key": "2026-10-04", "completion_evidence": evidence}
        plan = scheduler.weekly_plan(TODAY, previous, published_success("2026-09-27T02:00:00+00:00"))
        self.assertFalse(plan["should_run"])
        self.assertEqual(plan["completion_evidence"], evidence)
        self.assertEqual(plan["last_completed_week_key"], "2026-10-04")


if __name__ == "__main__":
    unittest.main()
