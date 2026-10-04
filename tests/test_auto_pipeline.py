"""Isolated regressions for GHPR pipeline orchestration and publication safety."""
from __future__ import annotations

import os
import json
import hashlib
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.dont_write_bytecode = True
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))
from src import update_pipeline as pipeline
from scripts import auto_update as automatic


class PipelineCommandTests(unittest.TestCase):
    def test_full_mode_downloads_sources_and_enforces_diagnostics(self):
        commands = pipeline.build_update_commands(mode="full")
        master = next(command for _, command in commands if "src/build_master_dataset.py" in command)
        diagnostics = next(command for _, command in commands if "src/data_freshness_diagnostics.py" in command)
        self.assertNotIn("--no-download", master)
        self.assertIn("--strict", diagnostics)
        self.assertLess(commands.index(next(item for item in commands if item[1] is master)),
                        commands.index(next(item for item in commands if item[1] is diagnostics)))

    def test_local_mode_explicitly_avoids_source_download(self):
        commands = pipeline.build_update_commands(mode="local")
        master = next(command for _, command in commands if "src/build_master_dataset.py" in command)
        self.assertIn("--no-download", master)

    def test_invalid_mode_cannot_start_a_subprocess(self):
        with patch.object(pipeline.subprocess, "run") as run:
            with self.assertRaises(ValueError):
                pipeline.run_update_pipeline(mode="publish_anyway")
        run.assert_not_called()


class PipelineFailureTests(unittest.TestCase):
    def setUp(self):
        scratch = Path(os.environ.get("GHPR_TEST_TMP", PROJECT_ROOT.parent / "test-tmp"))
        scratch.mkdir(parents=True, exist_ok=True)
        self.temporary = tempfile.TemporaryDirectory(prefix="ghpr-pipeline-", dir=scratch)
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)

    def test_failed_diagnostic_stops_before_any_following_publish_stage(self):
        commands = [("source", ["python", "source.py"]),
                    ("strict diagnostics", ["python", "diagnostic.py", "--strict"]),
                    ("publish", ["python", "must_not_run.py"])]
        results = [subprocess.CompletedProcess(commands[0][1], 0, "downloaded", ""),
                   subprocess.CompletedProcess(commands[1][1], 1, "", "master lags CFTC")]
        with patch.object(pipeline, "build_update_commands", return_value=commands), patch.object(
            pipeline, "latest_dataset_date", return_value="2026-09-22"
        ), patch.object(pipeline, "latest_cftc_available_date_from_current_file", return_value="2026-09-29"), patch.object(
            pipeline.subprocess, "run", side_effect=results
        ) as run, patch.object(pipeline, "write_update_log", return_value=self.root / "update_log.md"):
            result = pipeline.run_update_pipeline(mode="full")
        self.assertFalse(result.success)
        self.assertFalse(result.data_is_current)
        self.assertEqual(run.call_count, 2)
        self.assertEqual(result.failed_step.name, "strict diagnostics")
        self.assertIn("master lags CFTC", result.failed_step.stderr)

    def test_provider_timeout_is_reported_and_no_next_stage_runs(self):
        commands = [("download CFTC", ["python", "source.py"]),
                    ("recalculate", ["python", "must_not_run.py"])]
        with patch.object(pipeline, "build_update_commands", return_value=commands), patch.object(
            pipeline, "latest_dataset_date", return_value="2026-09-22"
        ), patch.object(pipeline, "latest_cftc_available_date_from_current_file", return_value="2026-09-22"), patch.object(
            pipeline.subprocess, "run", side_effect=subprocess.TimeoutExpired(commands[0][1], 900)
        ) as run, patch.object(pipeline, "write_update_log", return_value=self.root / "update_log.md"):
            result = pipeline.run_update_pipeline(mode="full")
        self.assertFalse(result.success)
        self.assertEqual(run.call_count, 1)
        self.assertIn("timed out", result.failed_step.stderr)
        self.assertIn("download CFTC", result.error_message)


class AutomaticUpdateSafetyTests(unittest.TestCase):
    GENERATION = "verified-generation-20260929"

    def setUp(self):
        scratch = Path(os.environ.get("GHPR_TEST_TMP", PROJECT_ROOT.parent / "test-tmp"))
        scratch.mkdir(parents=True, exist_ok=True)
        self.temporary = tempfile.TemporaryDirectory(prefix="ghpr-auto-", dir=scratch)
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.repo = self.root / "repo"
        self.runtime = self.root / "runtime"
        self.repo.mkdir()
        self.runtime.mkdir()
        automatic.write_json(self.repo / "outputs/reports/source_status.json", {
            "cftc": {"observation_date": "2026-09-29"},
            "gold": {"observation_date": "2026-10-02"},
        })
        self.build_release(self.repo, generation="previous-generation")
        self.config = {
            "source_repo": str(self.repo), "runtime_root": str(self.runtime),
            "pipeline_commands": [["test-pipeline"]],
            "after_pipeline_commands": [["test-build-release"]],
            "publish": False,
        }

    def build_release(self, directory, generation=None, bundle=b"new bundle"):
        web = directory / "web-data"
        web.mkdir(parents=True, exist_ok=True)
        (web / "bundle.json").write_bytes(bundle)
        (web / "outcomes.json").write_bytes(b"next-week outcomes")
        if not (web / "update-status.json").exists():
            automatic.write_json(web / "update-status.json", {"status": "success"})
        manifest = {"generation_id": generation or self.GENERATION, "as_of": "2026-09-29", "files": {}}
        for key, name in (("bundle", "bundle.json"), ("outcomes", "outcomes.json"), ("status", "update-status.json")):
            manifest["files"][key] = {"path": name, "sha256": hashlib.sha256((web / name).read_bytes()).hexdigest()}
        automatic.write_json(web / "manifest.json", manifest)
        return manifest

    def execute_successfully(self, command, cwd, env, log, timeout=1800):
        if command[:3] == ["git", "rev-parse", "HEAD"]:
            return "0123456789abcdef"
        self.assertTrue(Path(env["TMP"]).is_relative_to(self.runtime))
        self.assertTrue(Path(env["TEMP"]).is_relative_to(self.runtime))
        if command == ["test-build-release"]:
            self.build_release(cwd)
        return ""

    def previous_good(self, publication_state="verified_on_github_main", generation="previous-generation"):
        value = {"run_id": "last-known-good", "generation_id": generation,
                 "last_success_at_utc": "2026-10-03T12:00:00+00:00", "status": "success",
                 "publication_state": publication_state}
        if publication_state == "verified_on_github_main":
            value["published_commit"] = "previous-verified-commit"
        automatic.write_json(self.runtime / "last_good.json", value)
        return (self.runtime / "last_good.json").read_bytes()

    def test_lock_blocks_concurrent_run_and_is_reusable_after_release(self):
        lock_path = self.runtime / "update.lock"
        with automatic.RunLock(lock_path):
            with self.assertRaises(automatic.AlreadyRunning), patch.object(automatic, "execute") as execute:
                automatic.run_once(self.config)
            execute.assert_not_called()
        with automatic.RunLock(lock_path):
            self.assertTrue(lock_path.exists())

    def test_lock_is_released_after_exception(self):
        lock_path = self.runtime / "update.lock"
        with self.assertRaisesRegex(RuntimeError, "simulated crash"):
            with automatic.RunLock(lock_path):
                raise RuntimeError("simulated crash")
        with automatic.RunLock(lock_path):
            pass

    def test_failed_pipeline_retains_last_good_pointer_and_records_failure(self):
        previous = self.previous_good()
        def fail_provider(command, cwd, env, log, timeout=1800):
            if command == ["test-pipeline"]:
                raise RuntimeError("CFTC download unavailable")
            return self.execute_successfully(command, cwd, env, log, timeout)
        with patch.object(automatic, "execute", side_effect=fail_provider), patch.object(automatic, "publish_files") as publish:
            status = automatic.run_once(self.config)
        self.assertEqual(status["status"], "failed")
        self.assertIn("CFTC download unavailable", status["error"])
        self.assertTrue(status["retained_previous_snapshot"])
        self.assertEqual((self.runtime / "last_good.json").read_bytes(), previous)
        self.assertEqual(json.loads((self.runtime / "status.json").read_text())["status"], "failed")
        self.assertEqual(json.loads((self.runtime / "last_failure.json").read_text())["run_id"], status["run_id"])
        publish.assert_not_called()

    def test_local_validation_is_not_mistaken_for_a_previous_published_generation(self):
        self.previous_good(publication_state="not_requested_local_validation_only", generation=self.GENERATION)
        self.config["publish"] = True
        with patch.object(automatic, "execute", side_effect=self.execute_successfully), patch.object(
            automatic, "publish_files", return_value="published-commit"
        ) as publish:
            status = automatic.run_once(self.config)
        self.assertEqual(status["status"], "success")
        self.assertEqual(status["publication_state"], "verified_on_github_main")
        publish.assert_called_once()
        self.assertFalse(publish.call_args.kwargs["status_only"], "First real publication must include data after a local-only validation")

    def test_unchanged_published_generation_preserves_published_bundle_hashes(self):
        previous_manifest = self.build_release(self.repo, generation=self.GENERATION, bundle=b"previous published bundle")
        self.previous_good(generation=self.GENERATION)
        self.config["publish"] = True
        captured = {}
        def capture_publish(repo, stage, env, log, run_id, status_only=False):
            captured["status_only"] = status_only
            captured["manifest"] = json.loads((stage / "web-data/manifest.json").read_text())
            return "published-status-commit"
        with patch.object(automatic, "execute", side_effect=self.execute_successfully), patch.object(
            automatic, "publish_files", side_effect=capture_publish
        ):
            status = automatic.run_once(self.config)
        self.assertEqual(status["status"], "success")
        self.assertTrue(captured["status_only"])
        for name in ("bundle", "outcomes"):
            self.assertEqual(captured["manifest"]["files"][name], previous_manifest["files"][name])

    def test_status_only_release_matches_git_blobs_with_windows_autocrlf(self):
        previous = self.build_release(self.repo, generation=self.GENERATION, bundle=b"retained published bundle")
        stage = self.root / "same-generation-stage"
        self.build_release(stage, generation=self.GENERATION, bundle=b"new metadata must not replace retained bytes")
        self.assertTrue(automatic.failure_release(self.repo, stage, {"status": "data_ready", "trigger_reason": "startup_catchup"}))
        manifest = automatic.validated_release(stage)
        self.assertEqual(manifest["files"]["bundle"], previous["files"]["bundle"])
        self.assertNotIn(b"\r\n", (stage / "web-data/update-status.json").read_bytes())
        for args in (("init",), ("config", "core.autocrlf", "true"), ("add", "--", "web-data")):
            subprocess.run(["git", *args], cwd=stage, check=True, capture_output=True)
        self.assertEqual(automatic.validated_git_index(stage, os.environ.copy())["files"], manifest["files"])

    def test_git_index_gate_blocks_crlf_hash_that_git_would_publish_as_lf(self):
        stage = self.root / "crlf-stage"
        manifest = self.build_release(stage)
        status_path = stage / "web-data/update-status.json"
        status_path.write_bytes(status_path.read_bytes().replace(b"\n", b"\r\n"))
        manifest["files"]["status"]["sha256"] = hashlib.sha256(status_path.read_bytes()).hexdigest()
        automatic.write_json(stage / "web-data/manifest.json", manifest)
        automatic.validated_release(stage)  # Local-only checks miss Git's clean conversion.
        for args in (("init",), ("config", "core.autocrlf", "true"), ("add", "--", "web-data")):
            subprocess.run(["git", *args], cwd=stage, check=True, capture_output=True)
        with self.assertRaisesRegex(ValueError, "Staged Git release hash mismatch: status"):
            automatic.validated_git_index(stage, os.environ.copy())

    def test_publish_failure_never_retries_push_through_failure_status_path(self):
        previous = self.previous_good()
        self.config["publish"] = True
        with patch.object(automatic, "execute", side_effect=self.execute_successfully), patch.object(
            automatic, "publish_files", side_effect=RuntimeError("GitHub readback unavailable")
        ) as publish:
            status = automatic.run_once(self.config)
        self.assertEqual(status["status"], "failed")
        self.assertEqual(publish.call_count, 1, "A second status push could accidentally publish an unverified data commit")
        self.assertEqual((self.runtime / "last_good.json").read_bytes(), previous)
        self.assertIn("GitHub readback unavailable", status["error"])

    def test_release_hash_failure_blocks_validation(self):
        self.build_release(self.repo)
        (self.repo / "web-data/bundle.json").write_bytes(b"corrupt after manifest build")
        with self.assertRaisesRegex(ValueError, "hash mismatch: bundle"):
            automatic.validated_release(self.repo)

    def test_release_manifest_cannot_reference_file_outside_web_data(self):
        manifest = self.build_release(self.repo)
        outside = self.repo / "outside.json"
        outside.write_bytes(b"outside payload")
        manifest["files"]["bundle"] = {"path": "../outside.json", "sha256": hashlib.sha256(outside.read_bytes()).hexdigest()}
        automatic.write_json(self.repo / "web-data/manifest.json", manifest)
        with self.assertRaisesRegex(ValueError, "Invalid release file path: bundle"):
            automatic.validated_release(self.repo)


if __name__ == "__main__":
    unittest.main()


