"""Offline regressions for verified incremental GC=F prices and private cache continuity."""
from __future__ import annotations
import csv
import hashlib
import importlib.util
import json
from contextlib import ExitStack
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch
from urllib.parse import parse_qs, urlparse

sys.dont_write_bytecode = True
DRAFT = Path(__file__).resolve().parents[1]
CANDIDATE = DRAFT
SOURCE_META = {'symbol': 'GC=F', 'instrumentType': 'FUTURE', 'dataGranularity': '1d', 'exchangeTimezoneName': 'America/New_York'}
sys.path.insert(0, str(CANDIDATE / 'src'))


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


master = load_module('daily_incremental_master_draft', DRAFT / 'src/build_master_dataset.py')
automatic = load_module('daily_incremental_auto_draft', DRAFT / 'scripts/auto_update.py')


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes((json.dumps(data) + '\n').encode())


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_csv(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', newline='', encoding='utf-8') as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


class DailyIncrementalTests(unittest.TestCase):
    def setUp(self):
        scratch = DRAFT / 'test-tmp'
        scratch.mkdir(parents=True, exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(prefix='offline-', dir=scratch)
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.latest = date.today() - timedelta(days=3)
        self.overlap = self.latest - timedelta(days=100)
        self.newest = self.latest + timedelta(days=1)
        self.legacy = date(2009, 9, 1)
        self.bad_legacy = date(2009, 9, 2)

    def make_cache(self, root):
        output = root / 'data/raw/gold_price/gold_price.csv'
        ohlc = root / 'data/processed/gold_daily_ohlc.csv'
        days = [self.legacy, self.bad_legacy, self.overlap, self.latest]
        closes = [{'Date': day.isoformat(), 'Close': 101 + i, 'Source': master.GOLD_SOURCE_DEFAULT}
                  for i, day in enumerate(days)]
        ohlcs = [{'date': row['Date'], 'open': row['Close']-1, 'high': row['Close']+1,
                  'low': row['Close']-2, 'close': row['Close'], 'volume': 10,
                  'source': 'Yahoo Finance GC=F futures proxy'}
                 for row in closes if row['Date'] != self.bad_legacy.isoformat()]
        write_csv(output, closes)
        write_csv(ohlc, ohlcs)
        quarantine = [{'date': self.bad_legacy.isoformat(), 'reason': 'OHLC bounds inconsistent'}]
        write_json(output.parent / 'gc_daily_ohlc_quarantine.json', quarantine)
        write_json(output.parent / 'gc_daily_yahoo.json', {'chart': {'result': [{'meta': dict(SOURCE_META)}]}})
        metadata = {'symbol': 'GC=F', 'instrument': 'COMEX gold futures proxy', 'bar_interval': '1d',
                    'exchange_timezone': 'America/New_York', 'observation_date': self.latest.isoformat(),
                    'sha256': digest(output), 'ohlc_sha256': digest(ohlc),
                    'response_sha256': digest(output.parent / 'gc_daily_yahoo.json'),
                    'ohlc_quarantined_count': 1, 'ohlc_quarantined_records': quarantine,
                    'fetched_at_utc': datetime.now(timezone.utc).isoformat()}
        write_json(root / 'outputs/reports/source_status.json', {'schema_version': 1, 'gold': metadata, 'cftc': {'keep': 'original-cftc'}})
        return output, ohlc, metadata

    def patch_master(self, root):
        stack = ExitStack()
        stack.enter_context(patch.object(master, 'PROJECT_ROOT', root))
        stack.enter_context(patch.object(master, 'SOURCE_STATUS_PATH', root / 'outputs/reports/source_status.json'))
        stack.enter_context(patch.object(master, 'GOLD_RAW_DIR', root / 'data/raw/gold_price'))
        return stack

    def response(self, missing=None, invalid_ohlc=None, cold=False):
        days = [self.overlap, self.latest, self.newest]
        if cold:
            days.insert(0, date.fromisoformat(master.START_DATE) - timedelta(days=14))
        if missing:
            days.remove(missing)
        quote = {'open': [], 'high': [], 'low': [], 'close': [], 'volume': []}
        for i, day in enumerate(days):
            values = {'open': 200+i, 'high': 205+i, 'low': 198+i, 'close': 202+i, 'volume': 20}
            if day == invalid_ohlc:
                values['high'] = 100
            for key in quote:
                quote[key].append(values[key])
        payload = {'chart': {'result': [{'meta': dict(SOURCE_META),
                  'timestamp': [int(datetime(day.year, day.month, day.day, 12, tzinfo=timezone.utc).timestamp()) for day in days],
                  'indicators': {'quote': [quote]}}], 'error': None}}
        response = Mock(content=json.dumps(payload).encode(), headers={})
        response.raise_for_status.return_value = None
        response.json.return_value = payload
        return response

    def all_bytes(self, root):
        return {path.relative_to(root).as_posix(): path.read_bytes() for path in root.rglob('*') if path.is_file()}

    def test_warm_request_merges_overlap_and_preserves_old_history_and_quarantine(self):
        output, ohlc, previous = self.make_cache(self.root)
        response = self.response()
        errors = []
        with self.patch_master(self.root), patch.object(master.requests, 'get', return_value=response) as get:
            self.assertIsNotNone(master.verified_gold_cache(output, ohlc))
            self.assertTrue(master.download_yahoo_chart(output, date.today().year, errors), errors)
        period1 = int(parse_qs(urlparse(get.call_args.args[0]).query)['period1'][0])
        self.assertEqual(datetime.fromtimestamp(period1, timezone.utc).date(), self.latest - timedelta(days=120))
        with output.open(newline='', encoding='utf-8') as handle:
            rows = list(csv.DictReader(handle))
        self.assertEqual(len(rows), 5)
        dates = {row['Date'] for row in rows}
        self.assertIn(self.legacy.isoformat(), dates)
        self.assertIn(self.bad_legacy.isoformat(), dates)
        self.assertIn(self.newest.isoformat(), dates)
        with ohlc.open(newline='', encoding='utf-8') as handle:
            ohlcs = list(csv.DictReader(handle))
        self.assertNotIn(self.bad_legacy.isoformat(), {row['date'] for row in ohlcs})
        metadata = json.loads((self.root / 'outputs/reports/source_status.json').read_text())['gold']
        self.assertEqual(metadata['dataset_mode'], 'incremental_merge')
        self.assertEqual(metadata['ohlc_quarantined_records'], previous['ohlc_quarantined_records'])
        self.assertEqual(metadata['ohlc_quarantined_count'], 1)
        self.assertEqual(metadata['sha256'], digest(output))
        self.assertEqual(metadata['ohlc_sha256'], digest(ohlc))
        self.assertEqual(metadata['response_sha256'], hashlib.sha256(response.content).hexdigest())
        self.assertEqual((output.parent / 'gc_daily_yahoo.json').read_bytes(), response.content)
        self.assertIn(previous['sha256'], json.dumps(metadata))
        self.assertIn(previous['ohlc_sha256'], json.dumps(metadata))
        second_errors = []
        with self.patch_master(self.root), patch.object(master.requests, 'get', return_value=response) as second_get:
            self.assertIsNotNone(master.verified_gold_cache(output, ohlc))
            self.assertTrue(master.download_yahoo_chart(output, date.today().year, second_errors), second_errors)
        second_period1 = int(parse_qs(urlparse(second_get.call_args.args[0]).query)['period1'][0])
        self.assertEqual(datetime.fromtimestamp(second_period1, timezone.utc).date(), self.newest - timedelta(days=120))
        second_metadata = json.loads((self.root / 'outputs/reports/source_status.json').read_text())['gold']
        self.assertEqual(second_metadata['dataset_mode'], 'incremental_merge')
        self.assertEqual(len(second_metadata['capture_ledger']), 3)

    def test_missing_overlap_close_or_ohlc_rejects_without_changing_any_saved_bytes(self):
        for case in ('close_missing', 'ohlc_invalid'):
            with self.subTest(case=case):
                root = self.root / case
                output, ohlc, _ = self.make_cache(root)
                before = self.all_bytes(root)
                response = self.response(missing=self.overlap) if case == 'close_missing' else self.response(invalid_ohlc=self.overlap)
                errors = []
                with self.patch_master(root), patch.object(master.requests, 'get', return_value=response):
                    self.assertFalse(master.download_yahoo_chart(output, date.today().year, errors))
                self.assertTrue(errors)
                self.assertEqual(self.all_bytes(root), before)

    def test_loader_refuses_tampered_or_different_feed_cache(self):
        for case in ('hash', 'feed'):
            with self.subTest(case=case):
                root = self.root / case
                output, ohlc, metadata = self.make_cache(root)
                with self.patch_master(root):
                    self.assertIsNotNone(master.verified_gold_cache(output, ohlc))
                    if case == 'hash':
                        output.write_bytes(output.read_bytes() + b'changed')
                    else:
                        path = root / 'outputs/reports/source_status.json'
                        source = json.loads(path.read_text())
                        source['gold']['symbol'] = 'XAUUSD=X'
                        write_json(path, source)
                    self.assertIsNone(master.verified_gold_cache(output, ohlc))

    def test_new_uncached_date_with_invalid_close_rejects_without_overwriting_snapshot(self):
        output, _, _ = self.make_cache(self.root)
        before = self.all_bytes(self.root)
        response = self.response()
        payload = response.json.return_value
        payload['chart']['result'][0]['indicators']['quote'][0]['close'][-1] = None
        response.content = json.dumps(payload).encode()
        errors = []
        with self.patch_master(self.root), patch.object(master.requests, 'get', return_value=response):
            self.assertFalse(master.download_yahoo_chart(output, date.today().year, errors))
        self.assertTrue(errors)
        self.assertEqual(self.all_bytes(self.root), before)

    def test_truncated_close_array_rejects_without_silently_zipping_away_new_dates(self):
        output, _, _ = self.make_cache(self.root)
        before = self.all_bytes(self.root)
        response = self.response()
        payload = response.json.return_value
        quote = payload['chart']['result'][0]['indicators']['quote'][0]
        quote['close'] = quote['close'][:-1]
        response.content = json.dumps(payload).encode()
        errors = []
        with self.patch_master(self.root), patch.object(master.requests, 'get', return_value=response):
            self.assertFalse(master.download_yahoo_chart(output, date.today().year, errors))
        self.assertTrue(errors)
        self.assertEqual(self.all_bytes(self.root), before)

    def test_hash_valid_cache_with_unexplained_close_only_date_is_rejected(self):
        output, ohlc, _ = self.make_cache(self.root)
        with ohlc.open(newline='', encoding='utf-8') as handle:
            rows = list(csv.DictReader(handle))
        write_csv(ohlc, [row for row in rows if row['date'] != self.latest.isoformat()])
        source_path = self.root / 'outputs/reports/source_status.json'
        source = json.loads(source_path.read_text())
        source['gold']['ohlc_sha256'] = digest(ohlc)
        write_json(source_path, source)
        before = self.all_bytes(self.root)
        with self.patch_master(self.root):
            self.assertIsNone(master.verified_gold_cache(output, ohlc))
        self.assertEqual(self.all_bytes(self.root), before)

    def test_wrong_instrument_timezone_or_interval_is_rejected_in_response_and_cache(self):
        for key, bad_value in (('instrumentType', 'ETF'), ('exchangeTimezoneName', 'Europe/London'), ('dataGranularity', '1h')):
            for target in ('response', 'cache'):
                with self.subTest(field=key, target=target):
                    root = self.root / key / target
                    output, ohlc, _ = self.make_cache(root)
                    if target == 'response':
                        response = self.response()
                        payload = response.json.return_value
                        payload['chart']['result'][0]['meta'][key] = bad_value
                        response.content = json.dumps(payload).encode()
                        before = self.all_bytes(root)
                        errors = []
                        with self.patch_master(root), patch.object(master.requests, 'get', return_value=response):
                            self.assertFalse(master.download_yahoo_chart(output, date.today().year, errors))
                        self.assertTrue(errors)
                        self.assertEqual(self.all_bytes(root), before)
                    else:
                        raw = output.parent / 'gc_daily_yahoo.json'
                        payload = json.loads(raw.read_text())
                        payload['chart']['result'][0]['meta'][key] = bad_value
                        write_json(raw, payload)
                        metadata_path = root / 'outputs/reports/source_status.json'
                        source = json.loads(metadata_path.read_text())
                        source['gold']['response_sha256'] = digest(raw)
                        write_json(metadata_path, source)
                        with self.patch_master(root):
                            self.assertIsNone(master.verified_gold_cache(output, ohlc))

    def test_cold_request_still_fetches_full_history(self):
        output = self.root / 'data/raw/gold_price/gold_price.csv'
        errors = []
        with self.patch_master(self.root), patch.object(master.requests, 'get', return_value=self.response(cold=True)) as get:
            self.assertTrue(master.download_yahoo_chart(output, date.today().year, errors), errors)
        period1 = int(parse_qs(urlparse(get.call_args.args[0]).query)['period1'][0])
        self.assertEqual(datetime.fromtimestamp(period1, timezone.utc).date(), date.fromisoformat(master.START_DATE) - timedelta(days=14))

    def test_restore_copies_verified_success_cache_only_into_new_stage(self):
        runtime = self.root / 'runtime'
        old = runtime / 'runs/previous/stage'
        stage = runtime / 'runs/current/stage'
        output, ohlc, metadata = self.make_cache(old)
        stage.mkdir(parents=True)
        write_json(stage / 'outputs/reports/source_status.json', {'cftc': {'keep': 'new-stage-cftc'}, 'unrelated': 'keep'})
        repo = self.root / 'repo'
        repo.mkdir()
        (repo / 'untouched.txt').write_bytes(b'repository must not change')
        before_repo = self.all_bytes(repo)
        previous = {'status': 'success', 'run_id': 'previous', 'stage_path': str(old)}
        result = automatic.restore_daily_cache(stage, runtime, previous)
        self.assertTrue(result['restored'], result)
        for relative in ('data/raw/gold_price/gold_price.csv', 'data/raw/gold_price/gc_daily_yahoo.json',
                         'data/raw/gold_price/gc_daily_ohlc_quarantine.json', 'data/processed/gold_daily_ohlc.csv'):
            self.assertEqual((stage / relative).read_bytes(), (old / relative).read_bytes())
        sources = json.loads((stage / 'outputs/reports/source_status.json').read_text())
        self.assertEqual(sources['gold'], metadata)
        self.assertEqual(sources['cftc'], {'keep': 'new-stage-cftc'})
        self.assertEqual(sources['unrelated'], 'keep')
        self.assertEqual(self.all_bytes(repo), before_repo)

    def test_restore_rejects_outside_failed_or_hash_tampered_stage_without_overlay(self):
        for case in ('outside', 'failed', 'hash', 'target_outside'):
            with self.subTest(case=case):
                runtime = self.root / case / 'runtime'
                old = self.root / case / 'outside' if case == 'outside' else runtime / 'runs/previous/stage'
                stage = self.root / case / 'repo' if case == 'target_outside' else runtime / 'runs/current/stage'
                output, ohlc, _ = self.make_cache(old)
                stage.mkdir(parents=True)
                (stage / 'sentinel').write_bytes(b'keep current stage')
                before = self.all_bytes(stage)
                previous = {'status': 'failed' if case == 'failed' else 'success', 'run_id': 'previous', 'stage_path': str(old)}
                if case == 'hash':
                    ohlc.write_bytes(ohlc.read_bytes() + b'changed')
                result = automatic.restore_daily_cache(stage, runtime, previous)
                self.assertFalse(result['restored'], result)
                self.assertEqual(self.all_bytes(stage), before)


if __name__ == '__main__':
    unittest.main()





