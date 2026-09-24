# Independent D136 private expectations, frozen before companion implementation reads.
# Generates only temporary synthetic D073/D074 evidence, never observed hardware data.
# Public API tests exercise contract-derived chronology, grammar, binding and reports.
import contextlib
import hashlib
import importlib
import importlib.util
import io
import json
import os
from pathlib import Path
import struct
import sys
import tempfile
import unittest
from unittest import mock

ROOT = None
CSV = None
U32 = (1 << 32) - 1
PROFILE = '-DMATCH=0 -DMOTORS_ALLOWED={} -DSUMOX_P5_ABORT_TIMING=1'
TOP_KEYS = set('schema_version input_status evidence_status timing_status mode source required_attempts qualified_attempts passing_attempts logical_failures minimum_elapsed_us maximum_elapsed_us attempts errors declared_physical_trials_status hardware_acceptance transport_verified common_attempt_verified producer_semantics_verified'.split())
ATTEMPT_KEYS = set('id qualification trace_status motors_allowed binding_status read_start_us read_end_us qualified_us handover_us applied_us elapsed_us cue handover_state logical_status timing_status terminal_detail terminal_value errors validation'.split())
VALUES = {'TICK_US': 1000, 'ATTACK_ENTER_TICKS': 3, 'MODE_ARC_ENABLED': 1,
          'MODE_WAIT_ENABLED': 1, 'LOG_HZ': 25, 'LOG_EVENT_CAPACITY': 4096,
          'LOG_FRAME_WINDOW_MS': 200000}


def initialize(root):
    global ROOT, CSV
    ROOT = Path(root).resolve()
    sys.path.insert(0, str(ROOT / 'tools'))
    CSV = importlib.import_module('validate_csv_bundle')
    # Bind both conventional import spellings to the unchanged public validator.
    sys.modules['tools.validate_csv_bundle'] = CSV


def load_subject():
    spec = importlib.util.spec_from_file_location(
        'd136_private_subject', ROOT / 'tools/analyze_opener_abort.py')
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def digest(data):
    return hashlib.sha256(data).hexdigest()


def cue(mode=3, phase=0, cause=1, mask=2, snapshot=False):
    return mode | phase << 3 | cause << 6 | mask << 8 | int(snapshot) << 15


class Fixture:
    def __init__(self, directory, mode=3, motors=1, values=None):
        self.path = Path(directory)
        self.mode, self.motors = mode, motors
        self.values = dict(VALUES, **(values or {}))
        self.config = self.path / 'historical.h'
        text = '#include <cstdint>\nnamespace config {\n'
        text += ''.join('inline constexpr std::uint32_t {} = {}U;\n'.format(k, v)
                        for k, v in self.values.items())
        self.config.write_text(text + '}\n', encoding='ascii', newline='\n')
        self.attempts, self.rows, self.summaries, self.manifests = [], {}, {}, {}

    def write_events(self, name):
        lines = [','.join(CSV.EVENT_FIELDS)]
        for ordinal, (time, kind, detail, value) in enumerate(self.rows[name]):
            time &= U32
            raw = struct.pack('<IBBH', time, kind, detail, value).hex()
            lines.append(','.join(map(str, (1, ordinal, time, kind, detail, value, raw))))
        (self.path / (name + '.events.csv')).write_bytes(('\n'.join(lines) + '\n').encode('ascii'))

    def refresh(self, name):
        self.write_events(name)
        summary = self.summaries[name]
        summary['event_count'] = len(self.rows[name])
        body = ','.join(CSV.SUMMARY_FIELDS) + '\n'
        body += ','.join(str(summary[k]) for k in CSV.SUMMARY_FIELDS) + '\n'
        (self.path / (name + '.summary.csv')).write_bytes(body.encode('ascii'))
        manifest = self.manifests[name]
        for role in ('frames', 'events', 'summary'):
            raw = (self.path / (name + '.' + role + '.csv')).read_bytes()
            manifest['files'][role] = {'sha256': digest(raw), 'rows': raw.count(b'\n') - 1}
        (self.path / (name + '.manifest.json')).write_text(json.dumps(manifest), encoding='utf-8')

    def add(self, name=None, elapsed=1000, sequence=None, packed=None, state=5,
            go=None, go_present=True, go_seen=1, origin='synthetic'):
        index = len(self.attempts)
        name = name or 'trial_{:02d}'.format(index)
        go = ((index * 10000000 + 5100000) if go is None else go) & U32
        release = (go - 5100000) & U32
        times = {0: release, 16: (go - 20) & U32, 17: (go - 10) & U32,
                 18: go, 19: go, 20: (go + elapsed) & U32,
                 21: go, 22: go, 23: go, 24: go, 25: go}
        payloads = {0: 0x0205 if self.motors else 0x0201, 16: 1, 17: 1,
                    18: cue(self.mode) if packed is None else packed, 19: state,
                    20: 1, 21: 1, 22: 2, 23: 1, 24: 1, 25: state}
        sequence = [0, 16, 17, 18, 19, 20] if sequence is None else sequence
        rows = [(release, 0, self.mode, 0)]
        for detail in sequence:
            rows.append((times.get(detail, go), 10, detail, payloads.get(detail, 1)))
            if detail == 0 and go_present:
                rows.append((go, 1, self.mode, 0))
        self.rows[name] = rows
        payload = (go // 1000, 0, self.mode, 0, 0, 0, 0, 0, 0, 0, 0, 1200, 0, 1000)
        raw = struct.pack('<IBBBBihhhbbHBH', *payload).hex()
        frame = ','.join(CSV.FRAME_FIELDS) + '\n'
        frame += ','.join(map(str, (1, 0, 0, *payload, raw))) + '\n'
        (self.path / (name + '.frames.csv')).write_bytes(frame.encode('ascii'))
        summary = dict.fromkeys(CSV.SUMMARY_FIELDS, 0)
        summary.update(schema_version=1, epoch_token=index + 1, last_frame_token=index + 2,
                       release_us=release, mode=self.mode, phase=3, observed_results=2,
                       ticks=2, tick_max_us=1000, go_seen=go_seen, frame_count=1)
        self.summaries[name] = summary
        self.manifests[name] = {
            'schema_version': 1, 'closure': 'closed', 'session_id': name,
            'origin': origin, 'firmware_revision': 'a' * 40,
            'source_sha256': 'b' * 64, 'config_sha256': digest(self.config.read_bytes()),
            'log_hz': 25, 'frame_capacity': 5001, 'event_capacity': 4096,
            'target': 'synthetic-private-fixture-not-observed-hardware', 'files': {}}
        self.refresh(name)
        self.attempts.append(dict(id=name, **{
            role: name + '.' + role + ('.json' if role == 'manifest' else '.csv')
            for role in ('frames', 'events', 'summary', 'manifest')}))
        return name

    def cohort(self):
        return {'schema_version': 1, 'mode': self.mode,
                'source': {'firmware_revision': 'a' * 40, 'source_sha256': 'b' * 64,
                           'config': self.config.name,
                           'config_sha256': digest(self.config.read_bytes()),
                           'flags': PROFILE.format(self.motors)},
                'attempts': self.attempts}

    def save(self, data=None):
        path = self.path / 'cohort.json'
        path.write_text(json.dumps(self.cohort() if data is None else data), encoding='utf-8')
        return path


class PrivateContract(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='d136_private_')
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name)
        self.serial = 0

    def fixture(self, **kwargs):
        self.serial += 1
        folder = self.base / str(self.serial)
        folder.mkdir()
        return Fixture(folder, **kwargs)

    def analyze(self, fixture, data=None):
        path = fixture.save(data)
        before = {p.name: digest(p.read_bytes()) for p in fixture.path.iterdir() if p.is_file()}
        report = load_subject().analyze_cohort(path)
        after = {p.name: digest(p.read_bytes()) for p in fixture.path.iterdir() if p.is_file()}
        self.assertEqual(after, before, 'Analyzer changed or added local evidence files')
        self.assertEqual(set(report), TOP_KEYS)
        for field in ('hardware_acceptance', 'transport_verified',
                      'common_attempt_verified', 'producer_semantics_verified'):
            self.assertIs(report[field], False)
        for attempt in report['attempts']:
            self.assertEqual(set(attempt), ATTEMPT_KEYS)
        return report

    def invalid_attempt(self, report):
        self.assertEqual(report['evidence_status'], 'INVALID')
        self.assertEqual(report['timing_status'], 'NOT_QUALIFIED')
        for attempt in report['attempts']:
            if attempt['qualification'] == 'INVALID':
                for key in ('read_start_us', 'read_end_us', 'qualified_us',
                            'handover_us', 'applied_us', 'elapsed_us'):
                    self.assertIsNone(attempt[key])
                self.assertEqual(attempt['logical_status'], 'NOT_EVALUATED')
                self.assertEqual(attempt['timing_status'], 'NOT_EVALUATED')

    def test_01_ten_distinct_synthetic_passes_are_not_physical(self):
        f = self.fixture()
        for _ in range(10):
            f.add()
        r = self.analyze(f)
        self.assertEqual((r['input_status'], r['evidence_status'], r['timing_status']),
                         ('VALID', 'COMPLETE', 'PASS'))
        self.assertEqual((r['qualified_attempts'], r['passing_attempts'], r['logical_failures']), (10, 10, 0))
        self.assertEqual((r['minimum_elapsed_us'], r['maximum_elapsed_us']), (1000, 1000))
        self.assertEqual(r['declared_physical_trials_status'], 'NOT_QUALIFIED')
        self.assertEqual(r['source']['config_values'], VALUES)
        self.assertEqual(r['source']['binding_status'], 'DECLARED_MATCH')
        self.assertTrue(all(a['read_end_us'] < a['qualified_us'] for a in r['attempts']))

    def test_02_exact_bound_and_historical_tick_override(self):
        for bound in (1000, 750):
            f = self.fixture(values={'TICK_US': bound})
            for elapsed in (bound - 1, bound, bound + 1):
                f.add(elapsed=elapsed)
            r = self.analyze(f)
            self.assertEqual([a['timing_status'] for a in r['attempts']], ['PASS', 'PASS', 'FAIL'])
            self.assertEqual([a['elapsed_us'] for a in r['attempts']], [bound - 1, bound, bound + 1])
            self.assertEqual((r['qualified_attempts'], r['passing_attempts']), (3, 2))
            self.assertEqual((r['evidence_status'], r['timing_status']), ('INCOMPLETE', 'NOT_QUALIFIED'))

    def test_03_complete_late_block_fails_without_clamping(self):
        f = self.fixture()
        for index in range(10):
            f.add(elapsed=2000000 if index == 9 else 999)
        r = self.analyze(f)
        self.assertEqual((r['evidence_status'], r['timing_status']), ('COMPLETE', 'FAIL'))
        self.assertEqual((r['qualified_attempts'], r['passing_attempts']), (10, 9))
        self.assertEqual(r['maximum_elapsed_us'], 2000000)

    def test_04_handover_failure_is_evaluated_even_if_state_looks_right(self):
        f = self.fixture()
        failed = f.add(sequence=[0, 16, 17, 18, 25], state=5)
        for _ in range(9):
            f.add()
        r = self.analyze(f)
        self.assertEqual((r['evidence_status'], r['timing_status']), ('COMPLETE', 'FAIL'))
        self.assertEqual((r['qualified_attempts'], r['passing_attempts'], r['logical_failures']), (10, 9, 1))
        a = r['attempts'][0]
        self.assertEqual((a['trace_status'], a['logical_status'], a['timing_status']),
                         ('HANDOVER_FAILED', 'FAIL', 'NOT_EVALUATED'))
        self.assertIsNone(a['applied_us'])
        self.assertIsNone(a['elapsed_us'])
        self.assertEqual(a['handover_state'], 5)
        other = f.attempts[1]['id']
        f.summaries[other]['upstream_event_overflow'] = 1
        f.summaries[other]['incomplete'] = 1
        f.refresh(other)
        r = self.analyze(f)
        self.assertEqual((r['evidence_status'], r['timing_status'], r['logical_failures']),
                         ('INCOMPLETE', 'NOT_QUALIFIED', 1))
        self.assertEqual(r['attempts'][0]['id'], failed)

    def test_05_m0_and_hardware_origin_declarations_remain_distinct(self):
        f = self.fixture(motors=0)
        f.add()
        f.add(sequence=[0, 16, 17, 18, 25])
        r = self.analyze(f)
        self.assertEqual((r['qualified_attempts'], r['passing_attempts'], r['logical_failures']), (0, 0, 1))
        self.assertEqual(r['attempts'][0]['timing_status'], 'PASS')
        self.assertIs(r['attempts'][0]['motors_allowed'], False)
        self.assertEqual(r['evidence_status'], 'INCOMPLETE')
        f = self.fixture()
        # This deliberately fabricated declaration is only an analyzer input test.
        for _ in range(10):
            f.add(origin='hardware_reported')
        r = self.analyze(f)
        self.assertEqual(r['declared_physical_trials_status'], 'ELIGIBLE')

    def test_06_wrap_zero_and_common_anchor_contradictions(self):
        f = self.fixture()
        f.add(go=0)
        a = self.analyze(f)['attempts'][0]
        self.assertEqual((a['qualification'], a['qualified_us'], a['elapsed_us']), ('QUALIFIED', 0, 1000))
        for sequence, change in (([0, 16, 17], 'reversed'), ([0, 16, 17, 18, 19, 20], 'half')):
            f = self.fixture()
            name = f.add(sequence=sequence)
            rows = f.rows[name]
            if change == 'reversed':
                rows[4] = ((rows[3][0] - 1) & U32, *rows[4][1:])
            else:
                rows[-1] = ((rows[3][0] + (1 << 31)) & U32, *rows[-1][1:])
            f.refresh(name)
            self.invalid_attempt(self.analyze(f))

    def test_07_all_legal_nonpassing_dispositions_and_no_favorable_retry(self):
        sequences = [([], 'NOT_RECORDED'), ([0], 'INCOMPLETE'), ([0, 16], 'INCOMPLETE'),
                     ([0, 16, 17], 'INCOMPLETE'), ([0, 16, 17, 18], 'INCOMPLETE'),
                     ([0, 16, 17, 18, 19], 'INCOMPLETE'),
                     ([0, 21], 'EXCLUDED'), ([0, 22], 'EXCLUDED'), ([0, 23], 'EXCLUDED'),
                     ([0, 16, 17, 18, 22], 'EXCLUDED'),
                     ([0, 16, 17, 18, 19, 22], 'EXCLUDED'),
                     ([0, 16, 17, 18, 19, 24], 'EXCLUDED')]
        for sequence, expected in sequences:
            with self.subTest(sequence=sequence):
                f = self.fixture()
                f.add(sequence=sequence, go_present=len(sequence) > 1,
                      go_seen=int(len(sequence) > 1))
                r = self.analyze(f)
                self.assertEqual(r['attempts'][0]['trace_status'], expected)
                self.assertEqual(r['qualified_attempts'], 0)
                self.assertIsNone(r['attempts'][0]['elapsed_us'])
        f = self.fixture()
        f.add(sequence=[0, 23])
        for _ in range(9):
            f.add()
        r = self.analyze(f)
        self.assertEqual((r['qualified_attempts'], r['evidence_status']), (9, 'INCOMPLETE'))

    def test_08_missing_and_late_go_owner_and_decision_chronology(self):
        f = self.fixture()
        f.add(go_present=False, go_seen=1)
        a = self.analyze(f)['attempts'][0]
        self.assertEqual((a['trace_status'], a['qualification']), ('INCOMPLETE', 'INCOMPLETE'))
        self.assertIsNone(a['elapsed_us'])
        for change in ('late_go', 'zero_epoch', 'unseen_go', 'd_before_go'):
            f = self.fixture()
            name = f.add()
            rows = f.rows[name]
            if change == 'late_go':
                rows.append(rows.pop(2))
            elif change == 'zero_epoch':
                f.summaries[name]['epoch_token'] = 0
            elif change == 'unseen_go':
                f.summaries[name]['go_seen'] = 0
            else:
                rows[5] = (rows[2][0] - 1, *rows[5][1:])
                rows[6] = (rows[2][0] - 1, *rows[6][1:])
            f.refresh(name)
            self.invalid_attempt(self.analyze(f))

    def test_09_grammar_adjacency_header_and_terminal_replay(self):
        for change in ('ordinary_gap', 'header_gap', 'missing_header', 'p4', 'missing_interior', 'retry', 'edge_after_handover'):
            f = self.fixture()
            name = f.add()
            rows = f.rows[name]
            if change == 'ordinary_gap':
                rows.insert(4, (rows[2][0], 2, 0, 0))
            elif change == 'header_gap':
                rows.insert(1, (rows[0][0], 2, 0, 0))
            elif change == 'missing_header':
                del rows[1]
            elif change == 'p4':
                rows[1] = (*rows[1][:3], 0x0105)
            elif change == 'missing_interior':
                del rows[4]
            elif change == 'retry':
                rows.append((rows[-1][0], 10, 16, 1))
            else:
                rows[-1] = (rows[-1][0], 10, 22, 1)
            f.refresh(name)
            self.invalid_attempt(self.analyze(f))

    def test_10_phase_cue_truth_and_normal_front_priority(self):
        vectors = [(1, 1, 2, 0x52, False, 5, True),
                   (6, 4, 2, 0x0a, False, 5, True),
                   (3, 0, 2, 0x08, False, 7, True),
                   (3, 0, 1, 2, True, 5, True),
                   (1, 1, 1, 2, False, 5, False),
                   (4, 1, 1, 2, False, 5, False),
                   (3, 0, 2, 8, True, 7, False),
                   (6, 4, 2, 2, False, 5, False),
                   (1, 1, 2, 0x52, False, 7, False)]
        for mode, phase, cause, mask, snapshot, state, valid in vectors:
            with self.subTest(vector=(mode, phase, cause, mask, snapshot, state)):
                f = self.fixture(mode=mode)
                f.add(packed=cue(mode, phase, cause, mask, snapshot), state=state)
                r = self.analyze(f)
                if valid:
                    self.assertEqual(r['attempts'][0]['qualification'], 'QUALIFIED')
                else:
                    self.invalid_attempt(r)

    def test_11_centering_threshold_is_historical_not_interpreter_default(self):
        for mask in (1, 2, 3, 4, 5, 6, 7):
            f = self.fixture(values={'ATTACK_ENTER_TICKS': 1})
            state = 5 if mask in (1, 4) else 6
            f.add(packed=cue(mask=mask), state=state)
            self.assertEqual(self.analyze(f)['attempts'][0]['qualification'], 'QUALIFIED')
        for threshold, mask in ((1, 1), (3, 2)):
            f = self.fixture(values={'ATTACK_ENTER_TICKS': threshold})
            f.add(packed=cue(mask=mask), state=6)
            self.invalid_attempt(self.analyze(f))

    def test_12_source_failure_still_validates_bundles_and_empty_cohort(self):
        for populated in (False, True):
            f = self.fixture()
            if populated:
                f.add()
            data = f.cohort()
            data['source']['config_sha256'] = '0' * 64
            r = self.analyze(f, data)
            self.assertEqual((r['input_status'], r['evidence_status'], r['timing_status']),
                             ('VALID', 'INVALID', 'NOT_QUALIFIED'))
            self.assertEqual(r['source']['binding_status'], 'INVALID')
            self.assertEqual((r['qualified_attempts'], r['passing_attempts'], r['logical_failures']), (0, 0, 0))
            if populated:
                a = r['attempts'][0]
                self.assertEqual(a['validation']['format_integrity'], 'PASS')
                self.assertEqual(a['trace_status'], 'INVALID')
                self.assertIsNone(a['motors_allowed'])
            self.invalid_attempt(r)

    def test_13_restricted_literal_rejections_and_supported_lowercase(self):
        replacements = ['TICK_US = 1000 U', 'TICK_US = 01000U',
                        'TICK_US = (1000U)', 'TICK_US = 4294968296U',
                        'TICK_US = 0U', 'TICK_US = 1000ULL']
        for text in replacements:
            f = self.fixture()
            raw = f.config.read_text().replace('TICK_US = 1000U', text)
            f.config.write_text(raw, encoding='ascii', newline='\n')
            f.add()
            r = self.analyze(f)
            self.assertEqual(r['evidence_status'], 'INVALID')
            self.assertTrue(any(e['code'] == 'UNSUPPORTED_CONFIGURATION' for e in r['errors']))
        for prefix in ('#define TICK_US 1000U\n', '%:define TICK_US 1000U\n',
                       '// continuation\\\n', '#if 1\n'):
            f = self.fixture()
            raw = f.config.read_text()
            raw = prefix + raw + ('#endif\n' if prefix.startswith('#if') else '')
            f.config.write_text(raw, encoding='ascii', newline='\n')
            f.add()
            self.assertEqual(self.analyze(f)['evidence_status'], 'INVALID')
        f = self.fixture()
        f.config.write_text(f.config.read_text().replace('1000U', '1000u'), encoding='ascii', newline='\n')
        f.add()
        self.assertEqual(self.analyze(f)['attempts'][0]['qualification'], 'QUALIFIED')
        f = self.fixture(mode=6, values={'MODE_WAIT_ENABLED': 0})
        f.add(packed=cue(6, 4, 2, 8), state=7)
        r = self.analyze(f)
        self.assertEqual(r['source']['config_values']['MODE_WAIT_ENABLED'], 0)
        self.assertEqual(r['evidence_status'], 'INVALID')

    def test_14_manifest_binding_missing_mismatch_and_header_profile(self):
        for field, value, expected in (('source_sha256', None, 'INCOMPLETE'),
                                       ('source_sha256', 'c' * 64, 'INVALID'),
                                       ('firmware_revision', None, 'INCOMPLETE'),
                                       ('frame_capacity', 5000, 'INVALID')):
            f = self.fixture()
            name = f.add()
            f.manifests[name][field] = value
            f.refresh(name)
            r = self.analyze(f)
            self.assertEqual(r['attempts'][0]['qualification'], expected)
            if expected == 'INVALID':
                self.invalid_attempt(r)
        f = self.fixture()
        name = f.add()
        f.rows[name][1] = (*f.rows[name][1][:3], 0x0201)
        f.refresh(name)
        self.invalid_attempt(self.analyze(f))

    def test_15_loss_is_never_waived_and_duplicate_members_all_invalidate(self):
        for loss in ('malformed_batches', 'upstream_event_invalid', 'upstream_event_overflow',
                     'event_rejected', 'frame_overwritten', 'final_frame_missing'):
            f = self.fixture()
            name = f.add()
            f.summaries[name][loss] = 1
            f.summaries[name]['incomplete'] = 1
            f.refresh(name)
            r = self.analyze(f)
            self.assertEqual(r['attempts'][0]['qualification'], 'INCOMPLETE')
            self.assertEqual(r['attempts'][0]['timing_status'], 'PASS')
            self.assertEqual(r['qualified_attempts'], 0)
        f = self.fixture()
        f.add()
        f.attempts.append(dict(f.attempts[0], id='different_id_same_bundle'))
        r = self.analyze(f)
        self.assertEqual([a['qualification'] for a in r['attempts']], ['INVALID', 'INVALID'])
        self.invalid_attempt(r)

    def test_16_same_size_restored_mtime_reread_mutation_is_invalid(self):
        f = self.fixture()
        name = f.add()
        path = f.save()
        original = CSV.validate_bundle
        calls = []

        def mutate_after_validation(*args, **kwargs):
            accepted = original(*args, **kwargs)
            calls.append(args)
            events = f.path / (name + '.events.csv')
            old = events.stat()
            row = f.rows[name][-1]
            f.rows[name][-1] = (row[0] + 1, *row[1:])
            f.write_events(name)
            self.assertEqual(events.stat().st_size, old.st_size)
            os.utime(events, ns=(old.st_atime_ns, old.st_mtime_ns))
            return accepted

        with mock.patch.object(CSV, 'validate_bundle', side_effect=mutate_after_validation):
            r = load_subject().analyze_cohort(path)
        self.assertEqual(len(calls), 1)
        self.invalid_attempt(r)
        self.assertEqual(r['attempts'][0]['trace_status'], 'INVALID')

    def test_17_exact_schema_paths_and_cli_exit_contract(self):
        for change in ('bool_mode', 'unknown', 'network_config', 'extra_flag'):
            f = self.fixture()
            data = f.cohort()
            if change == 'bool_mode':
                data['mode'] = True
            elif change == 'unknown':
                data['modes'] = [3]
            elif change == 'network_config':
                data['source']['config'] = 'https://example.invalid/config.h'
            else:
                data['source']['flags'] += ' -DOTHER=1'
            r = self.analyze(f, data)
            self.assertEqual((r['input_status'], r['evidence_status']), ('INVALID', 'INVALID'))
            self.assertIsNone(r['mode'])
            self.assertIsNone(r['source'])
            self.assertEqual(r['attempts'], [])
        f = self.fixture()
        for _ in range(10):
            f.add()
        module = load_subject()
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            status = module.main([str(f.save())])
        self.assertEqual(status, 0)
        self.assertEqual(json.loads(output.getvalue())['timing_status'], 'PASS')
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(module.main([str(f.path / 'absent.json')]), 1)
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as caught:
            module.main([])
        self.assertEqual(caught.exception.code, 2)

    def test_18_public_decoder_is_pure_typed_and_mode_bound(self):
        decode = load_subject().decode_cue
        expected = {'mode': 6, 'phase': 4, 'cause': 2,
                    'effective_mask': 10, 'snapshot_front_present': False}
        value = cue(6, 4, 2, 10)
        self.assertEqual(decode(value, 6), expected)
        for invalid in (True, False, None, '1', 1.0, -1, 65536):
            self.assertIsNone(decode(invalid, 6))
        for mode in (True, False, None, '6', 6.0, 0, 7, 255):
            self.assertIsNone(decode(value, mode))
        self.assertIsNone(decode(value, 3))
        self.assertIsNone(decode(cue(6, 4, 2, 10, True), 6))
        self.assertIsNone(decode(cue(1, 1, 1, 2), 1))
        self.assertEqual(decode(cue(3, 0, 1, 2, True), 3),
                         dict(mode=3, phase=0, cause=1, effective_mask=2,
                              snapshot_front_present=True))

    def test_19_receipt_ordinal_gap_and_invalid_clock_diagnostics(self):
        f = self.fixture()
        name = f.add()
        f.rows[name].insert(-1, (f.rows[name][-2][0] + 1, 2, 0, 0))
        f.refresh(name)
        self.assertEqual(self.analyze(f)['attempts'][0]['qualification'], 'QUALIFIED')
        for sequence in ([0, 23], [0, 16, 17, 18, 19, 24]):
            f = self.fixture()
            name = f.add(sequence=sequence)
            row = f.rows[name][-1]
            f.rows[name][-1] = (0, *row[1:])
            f.refresh(name)
            a = self.analyze(f)['attempts'][0]
            self.assertEqual(a['trace_status'], 'EXCLUDED')
            self.assertIsNone(a['elapsed_us'])
