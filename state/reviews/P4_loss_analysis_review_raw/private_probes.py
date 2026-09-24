# Checks D130 target-loss reports using independent synthetic CSV fixtures.
# Keeps arithmetic and declared evidence separate from any physical claim.
# Frozen before analyzer execution; run with Python's unittest runner.
import contextlib
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import stat
import struct
import sys
import tempfile
import types
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[3]
FH = ('schema_version,ordinal,pack_status,t_ms,state,mode,line_mask,opp_mask,'
      'heading_cdeg,gyro_z_dps10,ax_mg,ay_mg,duty_l_127,duty_r_127,vbat_cv,flags,tick_max_us,raw_hex')
EH = 'schema_version,ordinal,t_us,type,detail,value,raw_hex'
SH = ('schema_version,epoch_token,last_frame_token,release_us,mode,phase,observed_results,'
      'missing_results,rejected_results,identity_rejected,malformed_batches,event_semantic_rejected,'
      'upstream_event_rejected,upstream_event_invalid,source_regressions,skipped_frames,ticks,'
      'overruns,tick_max_us,ticks_saturated,upstream_event_overflow,timing_incomplete,'
      'recording_incomplete,go_seen,final_frame_missing,interrupted,terminal_exhausted,frame_count,'
      'frame_overwritten,frame_rejected_status,frame_clamped,frame_invalid,event_count,'
      'event_overflow,event_rejected,incomplete').split(',')
MASK = (1 << 32) - 1


def load_analyzer():
    path = ROOT / 'tools/analyze_target_loss.py'
    spec = importlib.util.spec_from_file_location('review_target_loss', path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


class PrivateProbes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.analyzer = load_analyzer()

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='d130-review-')
        self.base = Path(self.temporary.name)

    def tearDown(self):
        self.temporary.cleanup()

    def bundle(self, index=0, sequence=(0, 1, 2, 3, 4), release=None,
               source=(6000000, 6000010), decision=6029999, applied=6035000,
               motors=True, owner=None, closed='closed', explicit_events=None):
        release = 100000 + index if release is None else release
        stamp = lambda offset: (release + offset) & MASK
        times = {0: release, 1: stamp(source[0]), 2: stamp(source[1]),
                 3: stamp(decision), 4: stamp(applied)}
        events = [(release, 0, 1, 0)]
        if sequence and sequence[0] == 0:
            events.append((release, 10, 0, 0x105 if motors else 0x101))
        events.append((stamp(5100000), 1, 1, 0))
        for detail in sequence:
            if detail != 0:
                events.append((times.get(detail, stamp(6040000)), 10, detail, 1))
        if explicit_events is not None:
            events = explicit_events(events, stamp)
        directory = self.base / ('attempt' + str(index))
        directory.mkdir(exist_ok=True)
        frames = (FH + '\n').encode()
        rows = [EH]
        for ordinal, (time, code, detail, value) in enumerate(events):
            raw = struct.pack('<IBBH', time, code, detail, value).hex()
            rows.append(','.join(map(str, (1, ordinal, time, code, detail, value, raw))))
        event_bytes = ('\n'.join(rows) + '\n').encode()
        summary = dict.fromkeys(SH, 0)
        summary.update(schema_version=1, epoch_token=index + 1, release_us=release,
                       mode=1, phase=3, go_seen=1, event_count=len(events))
        summary.update(owner or {})
        summary_bytes = (','.join(SH) + '\n' + ','.join(str(summary[k]) for k in SH) + '\n').encode()
        file_bytes = {'frames': frames, 'events': event_bytes, 'summary': summary_bytes}
        result = {'id': 'trial-' + str(index)}
        for role, raw in file_bytes.items():
            path = directory / (role + '.csv')
            path.write_bytes(raw)
            result[role] = str(path)
        declaration = {key: None for key in ('session_id', 'origin', 'firmware_revision',
                       'source_sha256', 'config_sha256', 'log_hz', 'frame_capacity',
                       'event_capacity', 'target')}
        declaration.update(schema_version=1, closure=closed,
                           origin='synthetic', files={role: {'sha256': hashlib.sha256(raw).hexdigest(),
                           'rows': len(raw.splitlines()) - 1} for role, raw in file_bytes.items()})
        manifest = directory / 'manifest.json'
        manifest.write_text(json.dumps(declaration), encoding='utf-8')
        result['manifest'] = str(manifest)
        return result

    def cohort(self, attempts):
        path = self.base / 'cohort.json'
        path.write_text(json.dumps({'schema_version': 1, 'opp_clear_ms': 30,
                                    'extra_margin_ms': 5, 'attempts': attempts}), encoding='utf-8')
        return path

    def analyze(self, attempts):
        report = self.analyzer.analyze_cohort(self.cohort(attempts))
        for key in ('hardware_acceptance', 'transport_verified', 'common_attempt_verified'):
            self.assertIs(report[key], False)
        return report

    def attempt(self, **kwargs):
        return self.analyze([self.bundle(**kwargs)])['attempts'][0]

    def assert_scrubbed(self, attempt, trace=None):
        self.assertEqual(attempt['qualification'], 'INVALID')
        self.assertEqual(attempt['timing_status'], 'NOT_EVALUATED')
        for key in ('source_start_us', 'source_end_us', 'brake_decision_us',
                    'zero_applied_us', 'lower_delay_us', 'upper_delay_us'):
            self.assertIsNone(attempt[key], key)
        if trace:
            self.assertEqual(attempt['trace_status'], trace)

    def test_closed_cohort_inclusive_bound_and_worst_trial(self):
        attempts = [self.bundle(i) for i in range(10)]
        result = self.analyze(attempts)
        self.assertEqual((result['input_status'], result['evidence_status'], result['timing_status']),
                         ('VALID', 'COMPLETE', 'PASS'))
        self.assertEqual((result['qualified_attempts'], result['minimum_lower_delay_us'],
                          result['maximum_upper_delay_us']), (10, 34990, 35000))
        attempts[-1] = self.bundle(9, applied=6035001)
        self.assertEqual(self.analyze(attempts)['timing_status'], 'INDETERMINATE')
        attempts[-1] = self.bundle(9, applied=6035011)
        self.assertEqual(self.analyze(attempts)['timing_status'], 'FAIL')

    def test_normal_wrap_zero_equal_and_ambiguous_offsets(self):
        result = self.attempt(release=(1 << 32) - 6035000)
        self.assertEqual((result['zero_applied_us'], result['upper_delay_us']), (0, 35000))
        result = self.attempt(source=(5100000, 5100000), decision=5100000, applied=5100000)
        self.assertEqual((result['lower_delay_us'], result['upper_delay_us']), (0, 0))
        for params in ({'applied': 1 << 31}, {'source': (5099999, 6000010)},
                       {'source': (6000011, 6000010)}, {'decision': 6000009},
                       {'applied': 6029998}, {'source': (1 << 31, 1 << 31)}):
            with self.subTest(params=params):
                self.assert_scrubbed(self.attempt(**params), 'INVALID')

    def test_all_legal_and_illegal_grammar_shapes(self):
        legal = [((0,), 'NOT_EXERCISED'), ((0, 1), 'INCOMPLETE'),
                 ((0, 1, 2), 'INCOMPLETE'), ((0, 1, 2, 3), 'INCOMPLETE')]
        legal += [((0, n), 'EXCLUDED') for n in range(6, 11)]
        legal += [((0, 1, 2, n), 'EXCLUDED') for n in (*range(5, 11), 12)]
        legal += [((0, 1, 2, 3, 11), 'EXCLUDED')]
        for sequence, status in legal:
            with self.subTest(sequence=sequence):
                item = self.attempt(sequence=sequence)
                self.assertEqual(item['trace_status'], status)
                self.assertEqual(item['qualification'], status)
                self.assertEqual(item['timing_status'], 'NOT_EVALUATED')
        for sequence in ((1,), (0, 5), (0, 11), (0, 12), (0, 2), (0, 1, 3),
                         (0, 1, 2, 4), (0, 1, 2, 3, 5), (0, 1, 2, 3, 4, 6),
                         (0, 1, 2, 2), (0, 1, 2, 3, 4, 4), (0, 13)):
            with self.subTest(sequence=sequence):
                self.assert_scrubbed(self.attempt(sequence=sequence), 'INVALID')
        self.assertEqual(self.attempt(sequence=())['qualification'], 'NOT_RECORDED')

    def test_prefix_times_and_ignored_exclusion_terminal_times(self):
        for sequence in ((0, 1), (0, 1, 2), (0, 1, 2, 6), (0, 1, 2, 3, 11)):
            with self.subTest(sequence=sequence):
                self.assert_scrubbed(self.attempt(sequence=sequence, source=(1 << 31, 1 << 31)), 'INVALID')
        def early_terminal(events, stamp):
            time, code, detail, value = events[-1]
            events[-1] = (stamp((1 << 31) + 1), code, detail, value)
            return events
        for sequence in ((0, 10), (0, 1, 2, 10), (0, 1, 2, 3, 11)):
            item = self.attempt(sequence=sequence, explicit_events=early_terminal)
            self.assertEqual(item['trace_status'], 'EXCLUDED')
            self.assertEqual(item['exclusion_detail'], sequence[-1])

    def test_missing_go_late_go_and_metadata_identity(self):
        missing_go = lambda events, stamp: [event for event in events if event[1] != 1]
        item = self.attempt(explicit_events=missing_go)
        self.assertEqual((item['qualification'], item['trace_status']), ('INCOMPLETE', 'INCOMPLETE'))
        self.assertIsNone(item['upper_delay_us'])
        def late_go(events, stamp):
            return events[:2] + events[3:] + [events[2]]
        self.assert_scrubbed(self.attempt(explicit_events=late_go), 'INVALID')
        for target, column, value in ((0, 2, 2), (0, 3, 1), (1, 3, 0x0107),
                                      (1, 0, 100001), (2, 2, 7), (2, 3, 1), (3, 3, 2)):
            def wrong(events, stamp, target=target, column=column, value=value):
                row = list(events[target]); row[column] = value; events[target] = tuple(row)
                return events
            with self.subTest(target=target, column=column, value=value):
                self.assert_scrubbed(self.attempt(explicit_events=wrong), 'INVALID')

    def test_full_event_order_and_arbitrary_other_events(self):
        odd = (7, 249, 253, 65535)
        valid = lambda events, stamp: events[:3] + [odd] + events[3:5] + [odd] + events[5:]
        self.assertEqual(self.attempt(explicit_events=valid)['qualification'], 'QUALIFIED')
        between_pair = lambda events, stamp: events[:4] + [odd] + events[4:]
        before_header = lambda events, stamp: events[:1] + [odd] + events[1:]
        for mutation in (between_pair, before_header):
            self.assert_scrubbed(self.attempt(explicit_events=mutation), 'INVALID')

    def test_ownership_scrub_and_trusted_trace_preservation(self):
        for owner in ({'epoch_token': 0}, {'go_seen': 0}, {'epoch_token': 0, 'phase': 1}):
            with self.subTest(owner=owner):
                self.assert_scrubbed(self.attempt(owner=owner), 'COMPLETE')
        canceled = lambda events, stamp: events[:2]
        item = self.attempt(sequence=(0,), owner={'go_seen': 0}, explicit_events=canceled)
        self.assertEqual(item['trace_status'], 'NOT_EXERCISED')
        self.assertEqual(item['qualification'], 'NOT_EXERCISED')
        self.assert_scrubbed(self.attempt(sequence=(0,), owner={'epoch_token': 0, 'go_seen': 0},
                                          explicit_events=canceled), 'NOT_EXERCISED')

    def test_incomplete_owner_retains_diagnostic_interval(self):
        for args in ({'motors': False}, {'closed': 'open'}, {'closed': 'unknown'},
                     {'owner': {'phase': 2}}, {'owner': {'missing_results': 1, 'incomplete': 1}}):
            with self.subTest(args=args):
                item = self.attempt(**args)
                self.assertEqual((item['qualification'], item['trace_status'], item['timing_status']),
                                 ('INCOMPLETE', 'COMPLETE', 'PASS'))
                self.assertEqual(item['upper_delay_us'], 35000)
        entry = self.bundle(); entry['manifest'] = None
        self.assertEqual(self.analyze([entry])['attempts'][0]['qualification'], 'INCOMPLETE')

    def test_start_go_order_and_offset_even_without_trace(self):
        for sequence in ((), (0,), (0, 10), (0, 1)):
            def ambiguous_go(events, stamp):
                return [(stamp(1 << 31), code, detail, value) if code == 1 else (time, code, detail, value)
                        for time, code, detail, value in events]
            with self.subTest(sequence=sequence):
                self.assert_scrubbed(self.attempt(sequence=sequence, explicit_events=ambiguous_go), 'INVALID')
        def go_first(events, stamp):
            return [events[-1]] + events[:-1]
        self.assert_scrubbed(self.attempt(sequence=(), explicit_events=go_first), 'INVALID')

    def test_duplicate_triples_scrub_every_reused_member(self):
        first = self.bundle(); second = dict(first, id='another')
        unique = self.bundle(2)
        result = self.analyze([first, unique, second, dict(first, id='third')])
        self.assertEqual(result['evidence_status'], 'INVALID')
        self.assertEqual(result['qualified_attempts'], 1)
        for n in (0, 2, 3):
            self.assert_scrubbed(result['attempts'][n], 'COMPLETE')
        self.assertEqual(result['maximum_upper_delay_us'], 35000)

    def test_cohort_schema_paths_and_cli(self):
        path = self.cohort([self.bundle(i) for i in range(10)])
        with contextlib.redirect_stdout(io.StringIO()) as capture:
            self.assertEqual(self.analyzer.main([str(path)]), 0)
        self.assertEqual(json.loads(capture.getvalue())['timing_status'], 'PASS')
        path = self.cohort([])
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(self.analyzer.main([str(path)]), 1)
        original = json.loads(path.read_text())
        for key, value in (('schema_version', True), ('schema_version', 1.0),
                           ('opp_clear_ms', 31), ('extra_margin_ms', 5.0),
                           ('attempts', [self.bundle()] * 11), ('unknown', 0)):
            data = dict(original); data[key] = value
            path.write_text(json.dumps(data))
            self.assertEqual(self.analyzer.analyze_cohort(path)['input_status'], 'INVALID')
        path.write_text('{"schema_version":1,"schema_version":1,"opp_clear_ms":30,"extra_margin_ms":5,"attempts":[]}')
        self.assertEqual(self.analyzer.analyze_cohort(path)['input_status'], 'INVALID')
        self.assertEqual(self.analyzer.analyze_cohort(self.base)['input_status'], 'INVALID')
        entry = self.bundle(); entry['frames'] = '../' + self.base.name + '/attempt0/frames.csv'
        self.assertEqual(self.analyze([entry])['attempts'][0]['qualification'], 'QUALIFIED')
        for name in ('//server/share/f.csv', '\\\\server\\share\\f.csv'):
            entry['frames'] = name
            self.assertEqual(self.analyze([entry])['input_status'], 'INVALID')

    def validator_module(self):
        expected = (ROOT / 'tools/validate_csv_bundle.py').resolve()
        candidates = [value for value in vars(self.analyzer).values()
                      if isinstance(value, types.ModuleType) and getattr(value, '__file__', None)
                      and Path(value.__file__).resolve() == expected and callable(getattr(value, 'validate_bundle', None))]
        self.assertEqual(len(candidates), 1, 'must intercept actual public validator boundary')
        return candidates[0]

    def test_hash_bound_same_size_restored_mtime_and_no_manifest_reread(self):
        validator = self.validator_module()
        real = validator.validate_bundle
        for role in ('events', 'summary'):
            entry = self.bundle()
            path = Path(entry[role]); original = path.read_bytes(); before = path.stat()
            count = []
            def swapped(*args, **kwargs):
                report = real(*args, **kwargs); count.append(1)
                old, new = (b'6035000', b'6035001') if role == 'events' else (b'100000', b'100001')
                if role == 'events':
                    old, new = b'6135000', b'6135001'
                    raw_old = struct.pack('<IBBH', 6135000, 10, 4, 1).hex().encode()
                    raw_new = struct.pack('<IBBH', 6135001, 10, 4, 1).hex().encode()
                    changed = original.replace(old, new).replace(raw_old, raw_new)
                else:
                    changed = original.replace(old, new)
                self.assertNotEqual(changed, original)
                self.assertEqual(len(changed), len(original))
                path.write_bytes(changed); os.utime(path, ns=(before.st_atime_ns, before.st_mtime_ns))
                return report
            with patch.object(validator, 'validate_bundle', swapped):
                self.assert_scrubbed(self.analyze([entry])['attempts'][0], 'INVALID')
            self.assertEqual(count, [1])
        entry = self.bundle(); count = []
        def remove_manifest(*args, **kwargs):
            report = real(*args, **kwargs); count.append(1)
            Path(entry['manifest']).unlink()
            return report
        with patch.object(validator, 'validate_bundle', remove_manifest):
            self.assertEqual(self.analyze([entry])['attempts'][0]['qualification'], 'QUALIFIED')
        self.assertEqual(count, [1])

    def test_cohort_symlink_and_oversize(self):
        target = self.cohort([])
        link = self.base / 'link.json'
        link.symlink_to(target)
        self.assertEqual(self.analyzer.analyze_cohort(link)['input_status'], 'INVALID')
        target.write_bytes(b' ' * (256 * 1024 + 1))
        self.assertEqual(self.analyzer.analyze_cohort(target)['input_status'], 'INVALID')


if __name__ == '__main__':
    unittest.main(verbosity=2)
