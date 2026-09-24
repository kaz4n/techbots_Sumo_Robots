"""Independent D127 contract probes; only synthetic temporary local evidence."""
from contextlib import redirect_stdout
import builtins
import hashlib
import importlib
import io
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'tests/tooling'))
sys.path.insert(0, str(ROOT / 'tools'))
import test_csv_bundle as wire

HOLD = 5100000
MASK = (1 << 32) - 1


class PrivateCountdown(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.analyzer = importlib.import_module('analyze_countdown')

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='d127_private_')
        self.addCleanup(self.temporary.cleanup)
        self.folder = Path(self.temporary.name)
        self.sequence = 0

    def bundle(self, release=0, go=HOLD, first=HOLD, events=None, **summary_changes):
        self.sequence += 1
        number = self.sequence
        prefix = self.folder / str(number)
        if events is None:
            events = [(1, release, 0, 1, 0)]
            if go is not None:
                events.append((2, (release + go) & MASK, 1, 1, 0))
            if first is not None:
                events.append((3, (release + first) & MASK, 2, 3, 0))
        summary = dict(epoch_token=number, release_us=release, mode=1, phase=3,
                       go_seen=1, frame_count=0, event_count=len(events))
        summary.update(summary_changes)
        blobs = {
            'frames': wire.header('frames'),
            'events': wire.header('events') + b''.join(
                wire.event(t_us=time, ordinal=ordinal, kind=kind, detail=detail, value=value)
                for ordinal, time, kind, detail, value in events),
            'summary': wire.header('summary') + wire.summary(**summary),
        }
        entry = {'id': 'trial_' + str(number)}
        for role, data in blobs.items():
            path = Path(str(prefix) + '_' + role + '.csv')
            path.write_bytes(data)
            entry[role] = path.name
        manifest = {key: None for key in ('session_id', 'origin', 'firmware_revision',
            'source_sha256', 'config_sha256', 'log_hz', 'frame_capacity', 'event_capacity', 'target')}
        manifest.update(schema_version=1, origin='synthetic', closure='closed',
            files={role: {'sha256': hashlib.sha256(data).hexdigest(),
                'rows': {'frames': 0, 'events': len(events), 'summary': 1}[role]}
                for role, data in blobs.items()})
        path = Path(str(prefix) + '_manifest.json')
        path.write_text(json.dumps(manifest))
        entry['manifest'] = path.name
        return entry

    def cohort(self, entries):
        path = self.folder / 'cohort.json'
        path.write_text(json.dumps(dict(schema_version=1, countdown_ms=5000,
            countdown_margin_ms=100, attempts=entries)))
        return path

    def analyze(self, entries):
        result = self.analyzer.analyze_cohort(self.cohort(entries))
        self.assertEqual(result['input_status'], 'VALID')
        for field in ('common_attempt_verified', 'transport_verified', 'hardware_acceptance'):
            self.assertIs(result[field], False)
        return result

    def test_partial_early_and_half_range_chronology_remain_distinct(self):
        cases = [
            (0, 5000000, HOLD - 1, 'QUALIFIED', 'FAIL', 5000000, HOLD - 1),
            (MASK - 100, HOLD, HOLD + 1, 'QUALIFIED', 'PASS', HOLD, HOLD + 1),
            (0, HOLD, (1 << 31) - 1, 'QUALIFIED', 'PASS', HOLD, (1 << 31) - 1),
            (0, HOLD, (1 << 31), 'INCOMPLETE', 'NOT_EVALUATED', None, None),
            (0, HOLD, HOLD - 1, 'INCOMPLETE', 'NOT_EVALUATED', None, None),
            (0, (1 << 31), HOLD, 'INCOMPLETE', 'NOT_EVALUATED', None, None),
            (0, None, HOLD - 1, 'INCOMPLETE', 'FAIL', None, HOLD - 1),
        ]
        for release, go, first, qualified, hold, expected_go, expected_first in cases:
            with self.subTest(release=release, go=go, first=first):
                result = self.analyze([self.bundle(release=release, go=go, first=first)])
                attempt = result['attempts'][0]
                self.assertEqual(attempt['qualification'], qualified)
                self.assertEqual(attempt['hold_status'], hold)
                self.assertEqual(attempt['release_us'], release)
                self.assertEqual(attempt['go_delay_us'], expected_go)
                self.assertEqual(attempt['first_delay_us'], expected_first)
                self.assertEqual(result['timing_status'], 'NOT_QUALIFIED')

    def test_partial_loss_and_closure_do_not_erase_valid_early_interval(self):
        for condition in ('loss', 'unsealed', 'absent_manifest', 'open', 'unknown'):
            with self.subTest(condition=condition):
                changes = {'missing_results': 1, 'incomplete': 1} if condition == 'loss' else {}
                if condition == 'unsealed': changes['phase'] = 1
                entry = self.bundle(go=5000000, first=HOLD - 1, **changes)
                if condition == 'absent_manifest': entry['manifest'] = None
                if condition in ('open', 'unknown'):
                    path = self.folder / entry['manifest']
                    data = json.loads(path.read_text()); data['closure'] = condition
                    path.write_text(json.dumps(data))
                report = self.analyze([entry]); row = report['attempts'][0]
                self.assertEqual(row['qualification'], 'INCOMPLETE')
                self.assertEqual(row['hold_status'], 'FAIL')
                self.assertEqual(row['first_delay_us'], HOLD - 1)
                self.assertEqual(report['qualified_attempts'], 0)
                self.assertIsNone(report['minimum_delay_us'])
                self.assertEqual(report['timing_status'], 'NOT_QUALIFIED')

    def test_first_payload_partition_including_zero_quantization_and_signed_bytes(self):
        for detail in (1, 2, 3):
            for left in (0, 1, 127, 128, 129, 255):
                for right in (0, 1, 127, 128, 129, 255):
                    with self.subTest(detail=detail, left=left, right=right):
                        events = [(0, MASK, 254, 128, 65535),
                            (1, 0, 0, 1, 0), (2, HOLD, 1, 1, 0),
                            (3, HOLD, 2, detail, left | (right << 8))]
                        valid = (left != 128 and right != 128 and
                            (detail & 1 or left == 0) and (detail & 2 or right == 0))
                        row = self.analyze([self.bundle(events=events)])['attempts'][0]
                        self.assertEqual(row['qualification'], 'QUALIFIED' if valid else 'INVALID')
                        self.assertEqual(row['validation']['format_integrity'], 'PASS')

    def test_reused_bundle_invalidates_all_members_and_excludes_them_from_statistics(self):
        original = self.bundle(first=HOLD)
        reused = dict(original, id='separate_label_same_bundle')
        separate = self.bundle(first=HOLD + 300)
        result = self.analyze([original, separate, reused])
        self.assertEqual([r['qualification'] for r in result['attempts']],
                         ['INVALID', 'QUALIFIED', 'INVALID'])
        self.assertEqual(result['evidence_status'], 'INVALID')
        self.assertEqual(result['qualified_attempts'], 1)
        self.assertEqual(result['minimum_delay_us'], HOLD + 300)
        self.assertEqual(result['maximum_delay_us'], HOLD + 300)
        self.assertEqual(result['spread_us'], 0)

    def test_fifty_unique_bundles_strict_spread_and_receipt_only_hold(self):
        for first_low, first_high, expected in ((HOLD, HOLD + 4999, 'PASS'),
                (HOLD, HOLD + 5000, 'FAIL'), (HOLD - 1, HOLD - 1, 'FAIL')):
            with self.subTest(low=first_low, high=first_high):
                entries = [self.bundle(go=0, first=first_low if i < 49 else first_high)
                           for i in range(50)]
                result = self.analyze(entries)
                self.assertEqual(result['evidence_status'], 'COMPLETE')
                self.assertEqual(result['qualified_attempts'], 50)
                self.assertEqual(result['timing_status'], expected)
                self.assertEqual(result['spread_us'], first_high - first_low)
                self.assertEqual(result['minimum_delay_us'], first_low)
                self.assertEqual(result['maximum_delay_us'], first_high)

    def test_validated_snapshot_rejects_same_size_and_restored_mtime_substitution(self):
        real_open = builtins.open
        real_io_open = io.open
        for role in ('events', 'summary'):
            entry = self.bundle()
            target = self.folder / entry[role]
            cohort = self.cohort([entry])
            counts = {}
            def instrument(original, file, *args, **kwargs):
                name = os.fspath(file) if isinstance(file, (str, Path)) else ''
                path = Path(name) if name else None
                if path is not None:
                    counts[path.name] = counts.get(path.name, 0) + 1
                if path == target and counts[path.name] == 2:
                    prior = target.stat()
                    with real_open(target, 'rb') as source: data = source.read()
                    if role == 'events':
                        old = wire.event(t_us=HOLD, ordinal=3, kind=2, detail=3, value=0)
                        new = wire.event(t_us=HOLD - 1, ordinal=3, kind=2, detail=3, value=0)
                        self.assertEqual(data.count(old), 1)
                        changed = data.replace(old, new)
                    else:
                        lines = data.splitlines(keepends=True)
                        changed = lines[0] + wire.replace_field(lines[1], wire.SUMMARY_NAMES,
                                                               'epoch_token', self.sequence + 1)
                    self.assertEqual(len(data), len(changed))
                    with real_open(target, 'wb') as destination: destination.write(changed)
                    os.utime(target, ns=(prior.st_atime_ns, prior.st_mtime_ns))
                return original(file, *args, **kwargs)
            with mock.patch('builtins.open', side_effect=lambda *a, **kw: instrument(real_open, *a, **kw)), \
                    mock.patch('io.open', side_effect=lambda *a, **kw: instrument(real_io_open, *a, **kw)):
                result = self.analyzer.analyze_cohort(cohort)
            self.assertEqual(counts.get(target.name), 2)
            self.assertEqual(counts.get(entry['manifest']), 1)
            self.assertEqual(counts.get(entry['frames']), 1)
            self.assertEqual(result['attempts'][0]['qualification'], 'INVALID')
            self.assertEqual(result['attempts'][0]['validation']['format_integrity'], 'PASS')
            self.assertEqual(result['evidence_status'], 'INVALID')
            self.assertEqual(result['timing_status'], 'NOT_QUALIFIED')

    def test_owner_contradictions_and_all_event_ordinals_are_not_hidden_by_missing_markers(self):
        for changes in ({'go_seen': 0}, {'epoch_token': 0}):
            report = self.analyze([self.bundle(**changes)])
            self.assertEqual(report['attempts'][0]['qualification'], 'INVALID')
        for events in (
            [(1, 0, 0, 1, 0), (2, HOLD, 1, 1, 0), (2, HOLD, 254, 0, 0), (3, HOLD, 2, 1, 0)],
            [(1, 0, 0, 1, 0), (2, 0, 0, 1, 0)],
            [(1, 0, 0, 1, 0), (2, HOLD, 2, 1, 0), (3, HOLD, 1, 1, 0)],
        ):
            result = self.analyze([self.bundle(events=events)])
            self.assertEqual(result['attempts'][0]['qualification'], 'INVALID')


if __name__ == '__main__':
    output = Path(__file__).resolve().parent
    stream = io.StringIO()
    result = unittest.TextTestRunner(stream=stream, verbosity=2).run(
        unittest.defaultTestLoader.loadTestsFromTestCase(PrivateCountdown))
    (output / 'private_tests.txt').write_text(stream.getvalue())
    (output / 'private_tests.json').write_text(json.dumps(dict(
        result='PASS' if result.wasSuccessful() else 'FAIL', tests=result.testsRun,
        failures=len(result.failures), errors=len(result.errors),
        limits='Synthetic local evidence only; no physical origin or common-run claim.'), indent=2)+'\n')
    print(stream.getvalue())
    raise SystemExit(0 if result.wasSuccessful() else 1)
