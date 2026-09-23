# Checks the frozen D-074 bundle contract using independent D-073 wire fixtures.
# Separates local format, owner consistency and caller declarations from hardware proof.
# Runs with unittest and one temporary public-API C++ formatter integration build.
from contextlib import ExitStack, redirect_stderr, redirect_stdout
import builtins
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import shutil
import stat
import struct
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[2]
TOOL = ROOT / 'tools' / 'validate_csv_bundle.py'
U32 = (1 << 32) - 1
U64 = (1 << 64) - 1
FRAME_NAMES = ('schema_version,ordinal,pack_status,t_ms,state,mode,line_mask,opp_mask,'
               'heading_cdeg,gyro_z_dps10,ax_mg,ay_mg,duty_l_127,duty_r_127,'
               'vbat_cv,flags,tick_max_us,raw_hex').split(',')
EVENT_NAMES = 'schema_version,ordinal,t_us,type,detail,value,raw_hex'.split(',')
SUMMARY_NAMES = (
    'schema_version,epoch_token,last_frame_token,release_us,mode,phase,observed_results,'
    'missing_results,rejected_results,identity_rejected,malformed_batches,'
    'event_semantic_rejected,upstream_event_rejected,upstream_event_invalid,'
    'source_regressions,skipped_frames,ticks,overruns,tick_max_us,ticks_saturated,'
    'upstream_event_overflow,timing_incomplete,recording_incomplete,go_seen,'
    'final_frame_missing,interrupted,terminal_exhausted,frame_count,frame_overwritten,'
    'frame_rejected_status,frame_clamped,frame_invalid,event_count,event_overflow,'
    'event_rejected,incomplete').split(',')
NAMES = dict(frames=FRAME_NAMES, events=EVENT_NAMES, summary=SUMMARY_NAMES)
BOOLS = ('ticks_saturated', 'upstream_event_overflow', 'timing_incomplete',
         'recording_incomplete', 'go_seen', 'final_frame_missing', 'interrupted',
         'terminal_exhausted', 'event_overflow', 'incomplete')
LOSS_FIELDS = (
    'missing_results', 'rejected_results', 'identity_rejected', 'malformed_batches',
    'event_semantic_rejected', 'upstream_event_rejected', 'upstream_event_invalid',
    'source_regressions', 'skipped_frames', 'frame_overwritten', 'frame_rejected_status',
    'frame_clamped', 'frame_invalid', 'event_rejected', 'event_overflow',
    'ticks_saturated', 'upstream_event_overflow', 'timing_incomplete',
    'recording_incomplete', 'final_frame_missing', 'interrupted', 'terminal_exhausted')
FRAME_FORMAT = '<IBBBBihhhbbHBH'
FRAME_VALUES = [0, 250, 251, 252, 253, -(1 << 31), -32768, 32767, 0,
                -128, 127, 65535, 254, 4660]
FRAME_LITERAL = (
    b'1,18446744073709551615,0,0,250,251,252,253,-2147483648,-32768,32767,0,'
    b'-128,127,65535,254,4660,00000000fafbfcfd000000800080ff7f0000807ffffffe3412\n')
EVENT_LITERAL = b'1,7,4294967295,254,253,65535,fffffffffefdffff\n'


def header(role):
    return (','.join(NAMES[role]) + '\n').encode('ascii')


def row(values):
    return (','.join(map(str, values)) + '\n').encode('ascii')


def frame(values=None, ordinal=U64, status=0):
    values = FRAME_VALUES if values is None else values
    return row([1, ordinal, status, *values, struct.pack(FRAME_FORMAT, *values).hex()])


def event(t_us=U32, ordinal=7, kind=254, detail=253, value=65535):
    return row([1, ordinal, t_us, kind, detail, value,
                struct.pack('<IBBH', t_us, kind, detail, value).hex()])


def summary(**changes):
    values = dict.fromkeys(SUMMARY_NAMES, 0)
    values.update(schema_version=1, frame_count=1, event_count=1, phase=3)
    values.update(changes)
    return row([values[name] for name in SUMMARY_NAMES])


def replace_field(line, names, name, value):
    tokens = line.rstrip(b'\n').split(b',')
    tokens[names.index(name)] = str(value).encode('ascii')
    return b','.join(tokens) + b'\n'


def load_validator():
    # Execute the public module; do not inspect its implementation source.
    spec = importlib.util.spec_from_file_location('independent_csv_bundle', TOOL)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class CheckedReader:
    """Observe standard stream I/O without depending on validator helper names."""
    def __init__(self, stream, observations):
        self.stream = stream
        self.observations = observations

    def __getattr__(self, name):
        return getattr(self.stream, name)

    def __enter__(self):
        self.stream.__enter__()
        return self

    def __exit__(self, *args):
        return self.stream.__exit__(*args)

    def read(self, size=-1):
        self.observations.append(('read', size))
        if not 0 <= size <= 16 * 1024 * 1024 + 1:
            raise AssertionError('Input reads must have a finite contract-sized bound')
        return self.stream.read(size)

    def readline(self, size=-1):
        self.observations.append(('readline', size))
        if not 0 < size <= 1024:
            raise AssertionError('Physical-line reads require a bounded lookahead')
        return self.stream.readline(size)

    def readlines(self, hint=-1):
        raise AssertionError('Whole-file readlines is not streaming input')

    def readinto(self, buffer):
        self.observations.append(('readinto', len(buffer)))
        if len(buffer) > 16 * 1024 * 1024 + 1:
            raise AssertionError('Input buffer exceeds the finite file limit')
        return self.stream.readinto(buffer)

    def __iter__(self):
        raise AssertionError('Unbounded stream iteration can retain an oversized line')


class CsvBundleContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.module = load_validator()

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='sumo-csv-contract-')
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name)
        self.paths = {role: self.directory / (role + '.csv') for role in NAMES}
        self.manifest_path = self.directory / 'manifest.json'
        self.write_bundle()

    def write_bundle(self, frames=None, events=None, **changes):
        frames = [FRAME_LITERAL] if frames is None else frames
        events = [EVENT_LITERAL] if events is None else events
        values = dict(frame_count=len(frames), event_count=len(events))
        values.update(changes)
        content = dict(frames=header('frames') + b''.join(frames),
                       events=header('events') + b''.join(events),
                       summary=header('summary') + summary(**values))
        for role, data in content.items():
            self.paths[role].write_bytes(data)
        return content

    def validate(self, manifest=None, paths=None):
        paths = self.paths if paths is None else paths
        result = self.module.validate_bundle(
            paths['frames'], paths['events'], paths['summary'], manifest)
        self.assert_report(result)
        return result

    def assert_report(self, result):
        self.assertEqual(set(result), {'schema_version', 'format_integrity', 'consistency',
                         'errors', 'files', 'recording', 'provenance',
                         'common_attempt_verified', 'transport_verified', 'hardware_acceptance'})
        self.assertEqual(result['schema_version'], 1)
        self.assertIn(result['format_integrity'], ('PASS', 'FAIL'))
        self.assertIn(result['consistency'], ('PASS', 'FAIL', 'NOT_CHECKED'))
        self.assertEqual(set(result['files']), set(NAMES))
        self.assertEqual(set(result['recording']), {'loss', 'lifecycle', 'phase_code'})
        self.assertEqual(set(result['provenance']), {'status', 'evidence_kind', 'closure', 'declared'})
        for key in ('common_attempt_verified', 'transport_verified', 'hardware_acceptance'):
            self.assertIs(result[key], False)
        self.assertIsInstance(result['errors'], list)
        for error in result['errors']:
            self.assertEqual(set(error), {'category', 'code', 'message'})
            self.assertIn(error['category'], ('format', 'consistency', 'manifest'))
            self.assertRegex(error['code'], r'^[A-Z][A-Z0-9_]*$')
            self.assertTrue(error['message'].strip())

    def assert_pass(self, result):
        self.assertEqual(result['format_integrity'], 'PASS', result['errors'])
        self.assertEqual(result['consistency'], 'PASS', result['errors'])
        self.assertEqual(result['errors'], [])

    def assert_format_failure(self, role, result=None):
        result = self.validate() if result is None else result
        self.assertEqual(result['format_integrity'], 'FAIL', result)
        self.assertEqual(result['consistency'], 'NOT_CHECKED', result)
        self.assertIsNone(result['files'][role])
        self.assertEqual(result['recording'],
                         {'loss': 'UNKNOWN', 'lifecycle': 'UNKNOWN', 'phase_code': None})
        self.assertIn('format', [error['category'] for error in result['errors']])

    def assert_consistency_failure(self, result):
        self.assertEqual(result['format_integrity'], 'PASS', result)
        self.assertEqual(result['consistency'], 'FAIL', result)
        self.assertIn('consistency', [error['category'] for error in result['errors']])

    def manifest(self, **changes):
        value = dict(schema_version=1, session_id='independent.synthetic-1', origin='synthetic',
                     firmware_revision='a' * 40, source_sha256='b' * 64,
                     config_sha256='c' * 64, log_hz=25, frame_capacity=5001,
                     event_capacity=4096, target='HOST ONLY', closure='closed', files={})
        for role, path in self.paths.items():
            raw = path.read_bytes()
            value['files'][role] = dict(sha256=hashlib.sha256(raw).hexdigest(),
                                       rows=raw.count(b'\n') - 1)
        value.update(changes)
        return value

    def write_manifest(self, value):
        self.manifest_path.write_bytes(json.dumps(value, separators=(',', ':')).encode('utf-8'))
        return self.manifest_path

    def assert_manifest_failure(self, value=None):
        if value is not None:
            self.write_manifest(value)
        result = self.validate(self.manifest_path)
        self.assertEqual(result['consistency'], 'FAIL', result)
        self.assertEqual(result['provenance'],
                         dict(status='INVALID', evidence_kind='UNKNOWN', closure='UNKNOWN', declared=None))
        self.assertIn('manifest', [error['category'] for error in result['errors']])
        return result

    def test_literal_unknown_codes_signed_extrema_and_exact_file_hashes(self):
        self.assertEqual(frame(), FRAME_LITERAL)
        self.assertEqual(event(), EVENT_LITERAL)
        result = self.validate()
        self.assert_pass(result)
        for role, path in self.paths.items():
            raw = path.read_bytes()
            self.assertEqual(result['files'][role], dict(
                sha256=hashlib.sha256(raw).hexdigest(), bytes=len(raw), rows=1))
        self.assertEqual(result['recording'], dict(loss='NONE_REPORTED', lifecycle='SEALED', phase_code=3))
        self.assertEqual(result['provenance'],
                         dict(status='ABSENT', evidence_kind='UNKNOWN', closure='UNKNOWN', declared=None))

    def test_empty_frames_events_and_path_strings(self):
        self.write_bundle(frames=[], events=[], phase=0)
        result = self.validate(paths={key: str(value) for key, value in self.paths.items()})
        self.assert_pass(result)
        self.assertEqual(result['files']['frames']['rows'], 0)
        self.assertEqual(result['files']['events']['rows'], 0)
        self.assertEqual(result['recording']['lifecycle'], 'EMPTY')

    def test_ordinals_duplicates_disorder_timestamp_wrap_and_unknown_event_bytes(self):
        ordinals = [U64, 0, 0, 91, 2]
        times = [U32, 0, 0, 12, 3]
        frames = [frame([t, *FRAME_VALUES[1:]], ordinal=o) for o, t in zip(ordinals, times)]
        events = [event(t, o, kind=255, detail=255) for o, t in zip(ordinals, times)]
        content = self.write_bundle(frames=frames, events=events)
        self.assert_pass(self.validate())
        self.assertEqual(content, {role: path.read_bytes() for role, path in self.paths.items()})

    def test_all_known_pack_statuses_retain_arbitrary_raw_bytes(self):
        frames = [frame(status=status) for status in (0, 1, 2)]
        self.write_bundle(frames=frames, frame_clamped=1, frame_invalid=1, incomplete=1)
        result = self.validate()
        self.assert_pass(result)
        self.assertEqual(result['recording']['loss'], 'REPORTED')

    def test_each_frame_wire_field_boundary_and_raw_mismatch(self):
        widths = [(0, U32)] + [(0, 255)] * 4 + [(-(1 << 31), (1 << 31) - 1)]
        widths += [(-32768, 32767)] * 3 + [(-128, 127)] * 2 + [(0, 65535), (0, 255), (0, 65535)]
        for index, (low, high) in enumerate(widths):
            name = FRAME_NAMES[index + 3]
            for value in (low, high):
                with self.subTest(field=name, boundary=value):
                    values = list(FRAME_VALUES)
                    values[index] = value
                    self.write_bundle(frames=[frame(values)])
                    self.assert_pass(self.validate())
            for value in (low - 1, high + 1):
                with self.subTest(field=name, outside=value):
                    bad = replace_field(FRAME_LITERAL, FRAME_NAMES, name, value)
                    self.write_bundle(frames=[bad])
                    self.assert_format_failure('frames')
            with self.subTest(field=name, disagreement=True):
                bad = replace_field(FRAME_LITERAL, FRAME_NAMES, name,
                                    high if FRAME_VALUES[index] != high else low)
                self.write_bundle(frames=[bad])
                self.assert_format_failure('frames')

    def test_event_wire_ranges_and_every_raw_field_agreement(self):
        for name, low, high in [('t_us', 0, U32), ('type', 0, 255),
                                ('detail', 0, 255), ('value', 0, 65535)]:
            for value in (low, high):
                with self.subTest(field=name, value=value):
                    kwargs = {('kind' if name == 'type' else name): value}
                    self.write_bundle(events=[event(**kwargs)])
                    self.assert_pass(self.validate())
            for value in (-1, high + 1, 1):
                with self.subTest(field=name, invalid_or_mismatch=value):
                    bad = replace_field(EVENT_LITERAL, EVENT_NAMES, name, value)
                    self.write_bundle(events=[bad])
                    self.assert_format_failure('events')

    def test_schema_status_ordinal_and_hex_lexical_boundaries(self):
        cases = [('schema_version', '0'), ('schema_version', '2'), ('ordinal', '-1'),
                 ('ordinal', str(U64 + 1)), ('raw_hex', '0' * 49), ('raw_hex', '0' * 51),
                 ('raw_hex', 'G' * 50), ('raw_hex', 'A' * 50), ('pack_status', '-1'),
                 ('pack_status', '3'), ('pack_status', '255')]
        for name, value in cases:
            with self.subTest(role='frames', field=name, value=value):
                self.write_bundle(frames=[replace_field(FRAME_LITERAL, FRAME_NAMES, name, value)])
                self.assert_format_failure('frames')
        for name, value in [('schema_version', 2), ('ordinal', -1), ('ordinal', U64 + 1),
                            ('raw_hex', '0' * 15), ('raw_hex', '0' * 17), ('raw_hex', 'F' * 16)]:
            with self.subTest(role='events', field=name, value=value):
                self.write_bundle(events=[replace_field(EVENT_LITERAL, EVENT_NAMES, name, value)])
                self.assert_format_failure('events')

    def test_noncanonical_integers_rejected_in_all_three_schemas(self):
        for role, names, original, name in [('frames', FRAME_NAMES, FRAME_LITERAL, 'heading_cdeg'),
                                           ('events', EVENT_NAMES, EVENT_LITERAL, 'ordinal'),
                                           ('summary', SUMMARY_NAMES, summary(), 'ticks')]:
            for token in ('+1', '-0', '00', '01', '-01', '1e0', '1.0', '', ' 1', '1 ', '9' * 500):
                with self.subTest(role=role, token=token):
                    self.write_bundle()
                    self.paths[role].write_bytes(header(role) + replace_field(original, names, name, token))
                    self.assert_format_failure(role)

    def test_summary_wire_widths_all_numeric_and_boolean_fields(self):
        u64_fields = {'epoch_token', 'last_frame_token', 'ticks', 'overruns'}
        for name in SUMMARY_NAMES:
            maximum = 1 if name in BOOLS or name == 'schema_version' else (
                U64 if name in u64_fields else 255 if name in ('mode', 'phase') else U32)
            for value in (0, maximum):
                if name == 'schema_version' and value == 0:
                    continue
                with self.subTest(field=name, boundary=value):
                    self.write_bundle(**{name: value})
                    self.assertEqual(self.validate()['format_integrity'], 'PASS')
            for value in (-1, maximum + 1):
                with self.subTest(field=name, outside=value):
                    self.write_bundle(**{name: value})
                    self.assert_format_failure('summary')

    def test_exact_headers_field_order_and_row_counts(self):
        for role in NAMES:
            good = self.paths[role].read_bytes()
            variants = [b'', good.replace(b'schema_version', b'Schema_version', 1),
                        good.replace(b',', b';', 1), good + b'\n', header(role) + b'1\n',
                        header(role) + good.split(b'\n', 1)[1].replace(b'\n', b',0\n', 1)]
            swapped = list(NAMES[role])
            swapped[0], swapped[1] = swapped[1], swapped[0]
            variants.append((','.join(swapped) + '\n').encode() + good.split(b'\n', 1)[1])
            for bad in variants:
                with self.subTest(role=role, malformed=bad[:70]):
                    self.write_bundle()
                    self.paths[role].write_bytes(bad)
                    self.assert_format_failure(role)
        for bad in (header('summary'), header('summary') + summary() * 2):
            self.write_bundle()
            self.paths['summary'].write_bytes(bad)
            self.assert_format_failure('summary')

    def test_ascii_lf_no_bom_quotes_whitespace_or_nul(self):
        for role in NAMES:
            self.write_bundle()
            good = self.paths[role].read_bytes()
            for bad in (good[:-1], good.replace(b'\n', b'\r\n'), b'\xef\xbb\xbf' + good,
                        good + b'\0', good.replace(b'\n1,', b'\n"1",', 1),
                        good.replace(b'\n1,', b'\n 1,', 1),
                        good.replace(b'\n1,', '\n\u0661,'.encode('utf-8'), 1)):
                with self.subTest(role=role, suffix=bad[-30:]):
                    self.write_bundle()
                    self.paths[role].write_bytes(bad)
                    self.assert_format_failure(role)

    def test_owner_count_mismatch_is_consistency_not_format(self):
        for changes in ({'frame_count': 0}, {'frame_count': 2},
                        {'event_count': 0}, {'event_count': 2}):
            with self.subTest(changes=changes):
                self.write_bundle(**changes)
                self.assert_consistency_failure(self.validate())

    def test_status_lifetime_counts_and_overwritten_bounds(self):
        frames = [frame(status=1), frame(status=2)]
        cases = [(dict(frame_clamped=1, frame_invalid=1), True),
                 (dict(frame_clamped=0, frame_invalid=1), False),
                 (dict(frame_clamped=1, frame_invalid=0), False),
                 (dict(frame_clamped=2, frame_invalid=1), False),
                 (dict(frame_clamped=2, frame_invalid=1, frame_overwritten=1), True),
                 (dict(frame_clamped=2, frame_invalid=2, frame_overwritten=1), False),
                 (dict(frame_clamped=2, frame_invalid=2, frame_overwritten=2), True),
                 (dict(frame_clamped=U32, frame_invalid=U32, frame_overwritten=U32 - 1), False),
                 (dict(frame_clamped=U32, frame_invalid=U32, frame_overwritten=U32), True)]
        for changes, passes in cases:
            with self.subTest(changes=changes):
                self.write_bundle(frames=frames, incomplete=1, **changes)
                result = self.validate()
                (self.assert_pass if passes else self.assert_consistency_failure)(result)
                self.assertEqual(result['recording']['loss'], 'REPORTED')

    def test_every_detailed_loss_field_requires_aggregate_and_remains_reported(self):
        for field in LOSS_FIELDS:
            extra = {'frame_overwritten': 1} if field in ('frame_clamped', 'frame_invalid') else {}
            for aggregate in (0, 1):
                with self.subTest(field=field, aggregate=aggregate):
                    changes = dict(extra, **{field: 1, 'incomplete': aggregate})
                    self.write_bundle(**changes)
                    result = self.validate()
                    (self.assert_pass if aggregate else self.assert_consistency_failure)(result)
                    self.assertEqual(result['recording']['loss'], 'REPORTED')

    def test_aggregate_only_and_retained_bad_status_still_report_loss(self):
        self.write_bundle(incomplete=1)
        result = self.validate()
        self.assert_consistency_failure(result)
        self.assertEqual(result['recording']['loss'], 'REPORTED')
        for status in (1, 2):
            self.write_bundle(frames=[frame(status=status)])
            result = self.validate()
            self.assert_consistency_failure(result)
            self.assertEqual(result['recording']['loss'], 'REPORTED')

    def test_nonloss_counters_and_unknown_owner_codes_do_not_invent_semantics(self):
        self.write_bundle(observed_results=U32, ticks=0, overruns=U64, tick_max_us=U32,
                          go_seen=1, mode=255, phase=255, epoch_token=0, last_frame_token=U64)
        result = self.validate()
        self.assert_pass(result)
        self.assertEqual(result['recording'], dict(loss='NONE_REPORTED', lifecycle='UNKNOWN', phase_code=255))

    def test_every_lifecycle_code_preserves_unfinished_and_sealed_distinction(self):
        for phase, lifecycle in [(0, 'EMPTY'), (1, 'UNFINISHED'), (2, 'UNFINISHED'),
                                  (3, 'SEALED'), (4, 'INTERRUPTED'), (5, 'UNKNOWN'), (255, 'UNKNOWN')]:
            with self.subTest(phase=phase):
                self.write_bundle(phase=phase)
                result = self.validate()
                self.assert_pass(result)
                self.assertEqual(result['recording'], dict(loss='NONE_REPORTED', lifecycle=lifecycle, phase_code=phase))

    def test_complete_manifest_and_each_origin_closure(self):
        for origin, kind in [('synthetic', 'SYNTHETIC'), ('hardware_reported', 'HARDWARE_REPORTED')]:
            for closure, reported in [('unknown', 'UNKNOWN'), ('open', 'DECLARED_OPEN'), ('closed', 'DECLARED_CLOSED')]:
                with self.subTest(origin=origin, closure=closure):
                    value = self.manifest(origin=origin, closure=closure)
                    result = self.validate(self.write_manifest(value))
                    self.assert_pass(result)
                    self.assertEqual(result['provenance'], dict(status='DECLARED', evidence_kind=kind,
                                                              closure=reported, declared=value))

    def test_every_nullable_manifest_field_and_all_null_partial_declarations(self):
        nullable = [key for key in self.manifest() if key not in ('schema_version', 'closure', 'files')]
        cases = [{name: None} for name in nullable] + [dict.fromkeys(nullable)]
        for changes in cases:
            with self.subTest(changes=changes):
                value = self.manifest(**changes)
                result = self.validate(self.write_manifest(value))
                self.assert_pass(result)
                self.assertEqual(result['provenance']['status'], 'PARTIAL_DECLARATION')
                self.assertEqual(result['provenance']['declared'], value)
                self.assertEqual(result['provenance']['evidence_kind'],
                                 'UNKNOWN' if value['origin'] is None else 'SYNTHETIC')

    def test_manifest_types_string_boundaries_and_no_boolean_integers(self):
        cases = {'schema_version': [None, True, False, 1.0, 0, 2, '1'],
                 'session_id': ['', 'x' * 97, 'has space', 'a/b', '\u00e9', 3, True],
                 'origin': ['', 'hardware', 'SYNTHETIC', 1, True],
                 'firmware_revision': ['A' * 40, 'a' * 39, 'g' * 64, 2],
                 'source_sha256': ['B' * 64, 'b' * 63, 'g' * 64, False],
                 'config_sha256': ['C' * 64, 'c' * 65, 1],
                 'log_hz': [True, False, 1.0, 0, -1, U32 + 1, '25'],
                 'frame_capacity': [True, 1.0, 0, -1, U32 + 1],
                 'event_capacity': [False, 1.0, 0, -1, U32 + 1],
                 'target': ['', '   ', 'x' * 129, 'a\n', '\u007f', '\u00e9', 1],
                 'closure': [None, True, '', 'CLOSED', 'complete']}
        for field, values in cases.items():
            for value in values:
                with self.subTest(field=field, value=value):
                    self.assert_manifest_failure(self.manifest(**{field: value}))
        for changes in ({'session_id': 'A' * 96, 'target': 'T' * 128},
                        {'firmware_revision': 'd' * 64, 'log_hz': U32, 'frame_capacity': U32,
                         'event_capacity': U32}, {'target': ' A ', 'session_id': '_.-'}):
            self.assert_pass(self.validate(self.write_manifest(self.manifest(**changes))))

    def test_manifest_exact_keys_required_at_each_level_and_no_path_binding(self):
        for field in self.manifest():
            value = self.manifest()
            del value[field]
            with self.subTest(missing=field):
                self.assert_manifest_failure(value)
        for level in ('top', 'files', 'entry'):
            value = self.manifest()
            target = value if level == 'top' else value['files'] if level == 'files' else value['files']['frames']
            target['path'] = str(self.paths['frames'])
            self.assert_manifest_failure(value)
        for role in NAMES:
            value = self.manifest()
            del value['files'][role]
            self.assert_manifest_failure(value)
            for field in ('sha256', 'rows'):
                value = self.manifest()
                del value['files'][role][field]
                self.assert_manifest_failure(value)

    def test_manifest_duplicate_keys_at_top_files_and_entries(self):
        raw = json.dumps(self.manifest(), separators=(',', ':'))
        duplicates = [raw.replace('{', '{"schema_version":1,', 1),
                      raw.replace('"files":{', '"files":{"frames":{},', 1),
                      raw.replace('"frames":{', '"frames":{"rows":1,', 1)]
        for duplicated in duplicates:
            self.manifest_path.write_text(duplicated, encoding='utf-8')
            self.assert_manifest_failure()

    def test_manifest_files_and_entries_must_be_objects(self):
        for wrong in (None, [], 'frames', True, 1):
            self.assert_manifest_failure(self.manifest(files=wrong))
            for role in NAMES:
                value = self.manifest()
                value['files'][role] = wrong
                self.assert_manifest_failure(value)

    def test_manifest_invalid_json_nonfinite_roots_utf8_and_oversize(self):
        for bad in (b'', b'{', b'[]', b'null', b'1', b'true', b'{} {}', b'\xff',
                    b' ' * 16385, b'\xef\xbb\xbf{}'):
            self.manifest_path.write_bytes(bad)
            self.assert_manifest_failure()
        for value in (float('nan'), float('inf'), -float('inf')):
            self.assert_manifest_failure(self.manifest(log_hz=value))
        valid = json.dumps(self.manifest(), separators=(',', ':')).encode()
        self.manifest_path.write_bytes(valid + b' ' * (16384 - len(valid)))
        self.assert_pass(self.validate(self.manifest_path))

    def test_manifest_hash_rows_and_capacity_each_role(self):
        for role in NAMES:
            for field, values in [('sha256', ['0' * 64, 'A' * 64, 'a' * 63, None, 1]),
                                  ('rows', [True, 1.0, -1, U32 + 1, None, '1', 0, 2])]:
                for bad in values:
                    with self.subTest(role=role, field=field, bad=bad):
                        value = self.manifest()
                        value['files'][role][field] = bad
                        self.assert_manifest_failure(value)
        self.write_bundle(frames=[frame(), frame()], events=[event(), event()])
        for field in ('frame_capacity', 'event_capacity'):
            self.assert_manifest_failure(self.manifest(**{field: 1}))
            self.assert_pass(self.validate(self.write_manifest(self.manifest(**{field: 2}))))
            self.assert_pass(self.validate(self.write_manifest(self.manifest(**{field: None}))))

    def test_manifest_provenance_is_independent_of_owner_consistency(self):
        self.write_bundle(frame_count=6)
        value = self.manifest(closure='closed')
        result = self.validate(self.write_manifest(value))
        self.assert_consistency_failure(result)
        self.assertEqual(result['provenance']['status'], 'DECLARED')
        self.assertEqual(result['provenance']['declared'], value)
        self.paths['events'].write_bytes(b'bad\n')
        result = self.validate(self.manifest_path)
        self.assertEqual(result['format_integrity'], 'FAIL')
        self.assertEqual(result['consistency'], 'FAIL')
        self.assertEqual(result['provenance']['status'], 'INVALID')
        self.assertIsNone(result['provenance']['declared'])

    def test_invalid_paths_and_directories_report_errors_without_exceptions(self):
        for role in NAMES:
            for bad in (self.directory, self.directory / 'missing.csv', None, 3, [], 'bad\0path'):
                with self.subTest(role=role, path=repr(bad)):
                    paths = dict(self.paths, **{role: bad})
                    self.assert_format_failure(role, self.validate(paths=paths))
        for bad in (self.directory, self.directory / 'missing.json', 7, [], 'bad\0path'):
            result = self.validate(bad)
            self.assertEqual(result['provenance']['status'], 'INVALID')
            self.assertEqual(result['consistency'], 'FAIL')

    def test_symlinks_rejected_for_all_csv_roles_and_manifest(self):
        for role in (*NAMES, 'manifest'):
            destination = self.manifest_path if role == 'manifest' else self.paths[role]
            if role == 'manifest':
                self.write_manifest(self.manifest())
            link = self.directory / (role + '.link')
            try:
                link.symlink_to(destination)
            except OSError as error:
                self.fail('Symlink test requires the WSL/POSIX tooling environment: ' + str(error))
            if role == 'manifest':
                result = self.validate(link)
                self.assertEqual(result['provenance']['status'], 'INVALID')
                self.assertEqual(result['consistency'], 'FAIL')
            else:
                self.assert_format_failure(role, self.validate(paths=dict(self.paths, **{role: link})))

    def test_network_path_separator_variants_rejected_before_filesystem_access(self):
        variants = ('//server/share/frames.csv', '\\\\server\\share\\frames.csv',
                    '/\\server\\share\\frames.csv', '\\/server/share/frames.csv')
        for path in variants:
            for role in ('frames', 'manifest'):
                touched = []

                def guard(original):
                    def checked(file, *args, **kwargs):
                        if isinstance(file, (str, bytes, os.PathLike)):
                            normalized = os.fsdecode(file).replace('\\', '/')
                            if normalized.startswith('//server/'):
                                touched.append(normalized)
                                raise AssertionError('No filesystem/network lookup for remote-looking paths')
                        return original(file, *args, **kwargs)
                    return checked

                with self.subTest(path=path, role=role), ExitStack() as stack:
                    for module, name in ((os, 'lstat'), (os, 'stat'), (os, 'open'),
                                         (builtins, 'open'), (io, 'open')):
                        stack.enter_context(mock.patch.object(module, name, guard(getattr(module, name))))
                    result = self.validate(path) if role == 'manifest' else self.validate(
                        paths=dict(self.paths, frames=path))
                self.assertEqual(touched, [], 'Reject every UNC separator pair before local I/O')
                if role == 'manifest':
                    self.assertEqual(result['provenance']['status'], 'INVALID')
                    self.assertEqual(result['consistency'], 'FAIL')
                else:
                    self.assert_format_failure('frames', result)

    def test_oversized_csv_files_and_physical_lines_are_rejected(self):
        for role in NAMES:
            for bad_line in (b'9' * 1023 + b'\n', b'9' * 1024):
                self.write_bundle()
                self.paths[role].write_bytes(header(role) + bad_line)
                self.assert_format_failure(role)
            self.write_bundle()
            with self.paths[role].open('wb') as stream:
                stream.truncate(16 * 1024 * 1024 + 1)
            self.assert_format_failure(role)

    def test_size_and_mtime_changes_on_open_descriptor_fail_snapshot(self):
        original = os.fstat
        for role in (*NAMES, 'manifest'):
            for changed in ('st_size', 'st_mtime_ns'):
                self.write_bundle()
                self.write_manifest(self.manifest())
                path = self.manifest_path if role == 'manifest' else self.paths[role]
                identity = path.stat()
                calls = []

                def changed_stat(fd):
                    actual = original(fd)
                    if (actual.st_dev, actual.st_ino) != (identity.st_dev, identity.st_ino):
                        return actual
                    calls.append(fd)
                    if len(calls) < 2:
                        return actual
                    fields = {name: getattr(actual, name) for name in dir(actual) if name.startswith('st_')}
                    fields[changed] += 1
                    return SimpleNamespace(**fields)

                with self.subTest(role=role, changed=changed), mock.patch('os.fstat', changed_stat):
                    result = self.validate(self.manifest_path if role == 'manifest' else None)
                self.assertGreaterEqual(len(calls), 2, 'Read identity must be checked before and after')
                if role == 'manifest':
                    self.assertEqual(result['provenance']['status'], 'INVALID')
                    self.assertEqual(result['consistency'], 'FAIL')
                else:
                    self.assert_format_failure(role, result)

    def test_opened_descriptor_regular_type_is_checked(self):
        original = os.fstat
        identity = self.paths['frames'].stat()

        def nonregular(fd):
            actual = original(fd)
            if (actual.st_dev, actual.st_ino) != (identity.st_dev, identity.st_ino):
                return actual
            fields = {name: getattr(actual, name) for name in dir(actual) if name.startswith('st_')}
            fields['st_mode'] = stat.S_IFIFO | 0o600
            return SimpleNamespace(**fields)

        with mock.patch('os.fstat', nonregular):
            result = self.validate()
        self.assert_format_failure('frames', result)

    def test_streaming_reads_are_bounded_binary_once_per_file(self):
        self.write_manifest(self.manifest())
        observed, opened = [], []
        identities = {path.resolve() for path in (*self.paths.values(), self.manifest_path)}

        def intercept(original):
            def opening(file, *args, **kwargs):
                stream = original(file, *args, **kwargs)
                if isinstance(stream, CheckedReader):
                    return stream
                if isinstance(file, (str, bytes, os.PathLike)) and Path(file).resolve() in identities:
                    opened.append(Path(file).resolve())
                    self.assertIn('b', getattr(stream, 'mode', ''), 'CSV/manifest input must be binary')
                    return CheckedReader(stream, observed)
                if isinstance(file, int):
                    identity = os.fstat(file)
                    matches = [path for path in identities if (path.stat().st_dev, path.stat().st_ino)
                               == (identity.st_dev, identity.st_ino)]
                    if matches:
                        opened.extend(matches)
                        return CheckedReader(stream, observed)
                return stream
            return opening

        with ExitStack() as stack:
            for module, name in ((builtins, 'open'), (io, 'open'), (os, 'fdopen')):
                stack.enter_context(mock.patch.object(module, name, intercept(getattr(module, name))))
            self.assert_pass(self.validate(self.manifest_path))
        self.assertTrue(observed, 'Observe real input stream operations')
        self.assertEqual(sorted(opened), sorted(identities), 'Each input is opened/read exactly once')

    def test_import_and_validation_quiet_without_writes_network_or_processes(self):
        before = {path.name: path.read_bytes() for path in self.directory.iterdir()}
        stdout, stderr = io.StringIO(), io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            imported = load_validator()
            result = imported.validate_bundle(*self.paths.values())
        self.assert_pass(result)
        self.assertEqual(stdout.getvalue(), '')
        self.assertEqual(stderr.getvalue(), '')
        self.assertEqual(before, {path.name: path.read_bytes() for path in self.directory.iterdir()})
        guard = r'''
import importlib.util, json, pathlib, sys
sys.dont_write_bytecode = True
tool, *inputs = sys.argv[1:]
def audit(event, args):
    if event == 'open':
        name, mode, flags = args
        if (isinstance(mode, str) and any(c in mode for c in 'wax+')) or flags & 0x243:
            raise AssertionError('Validator attempted a filesystem write')
        if isinstance(name, str) and name.endswith(('config.h', 'board_tool.py')):
            raise AssertionError('Validator attempted a current config/board dependency')
    if event.startswith(('socket.', 'subprocess.')) or event in ('os.system', 'os.posix_spawn'):
        raise AssertionError('Validator attempted a transport/process action')
sys.addaudithook(audit)
spec = importlib.util.spec_from_file_location('guarded_validator', tool)
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)
assert module.validate_bundle(*inputs)['format_integrity'] == 'PASS'
'''
        run = subprocess.run([sys.executable, '-B', '-c', guard, str(TOOL),
                              *map(str, self.paths.values())], capture_output=True, text=True, timeout=20)
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        self.assertEqual(run.stdout, '')
        self.assertEqual(run.stderr, '')

    def cli(self, *extra):
        args = [sys.executable, '-B', str(TOOL)]
        for role, path in self.paths.items():
            args.extend(['--' + role, str(path)])
        return subprocess.run([*args, *extra], capture_output=True, text=True, timeout=20)

    def test_cli_json_sorted_success_loss_unfinished_and_failures(self):
        self.write_bundle(phase=1, missing_results=2, incomplete=1)
        success = self.cli()
        self.assertEqual(success.returncode, 0, success.stderr)
        result = json.loads(success.stdout)
        self.assert_pass(result)
        self.assertEqual(success.stderr, '')
        self.assertEqual(list(result), sorted(result))
        self.assertEqual(result['recording']['loss'], 'REPORTED')
        self.assertEqual(result['recording']['lifecycle'], 'UNFINISHED')
        self.write_bundle(frame_count=100)
        bad = self.cli()
        self.assertEqual(bad.returncode, 1)
        self.assert_consistency_failure(json.loads(bad.stdout))
        self.paths['frames'].write_bytes(b'broken\n')
        malformed = self.cli()
        self.assertEqual(malformed.returncode, 1)
        self.assertEqual(json.loads(malformed.stdout)['format_integrity'], 'FAIL')
        self.write_bundle()
        self.write_manifest(self.manifest(schema_version=2))
        invalid = self.cli('--manifest', str(self.manifest_path))
        self.assertEqual(invalid.returncode, 1)
        self.assertEqual(json.loads(invalid.stdout)['provenance']['status'], 'INVALID')

    def test_cli_help_usage_and_no_output_repair_modes(self):
        for args, code in [(['--help'], 0), ([], 2), (['--frames', 'missing'], 2)]:
            run = subprocess.run([sys.executable, '-B', str(TOOL), *args],
                                 capture_output=True, text=True, timeout=20)
            self.assertEqual(run.returncode, code, run.stdout + run.stderr)
        for option in ('--output', '--report', '--repair', '--overwrite'):
            run = self.cli(option, str(self.directory / 'must-not-exist'))
            self.assertEqual(run.returncode, 2)
        self.assertFalse((self.directory / 'must-not-exist').exists())

    def test_synthetic_200_seconds_25hz_5001_frames_4096_events_is_only_local_evidence(self):
        frames = [frame([index * 40, *FRAME_VALUES[1:]], ordinal=index) for index in range(5001)]
        events = [event(t_us=index * 1000, ordinal=index, kind=255) for index in range(4096)]
        self.write_bundle(frames=frames, events=events, ticks=200001, go_seen=1)
        value = self.manifest(session_id='SYNTHETIC-200s-25Hz-5001-4096')
        result = self.validate(self.write_manifest(value))
        self.assert_pass(result)
        self.assertEqual(result['files']['frames']['rows'], 5001)
        self.assertEqual(result['files']['events']['rows'], 4096)
        self.assertEqual(result['provenance']['evidence_kind'], 'SYNTHETIC')
        self.assertEqual(result['recording']['loss'], 'NONE_REPORTED')
        # Rate/capacity declarations are not cadence or duration acceptance rules.
        self.write_bundle(frames=[frame([999, *FRAME_VALUES[1:]], ordinal=300)])
        self.assert_pass(self.validate(self.write_manifest(self.manifest(log_hz=1, frame_capacity=1))))

    def test_actual_cpp_formatter_public_api_bundle_matches_independent_bytes(self):
        compiler = shutil.which('g++')
        self.assertIsNotNone(compiler, 'g++ is required for the controlled host formatter integration')
        source = self.directory / 'public_formatter.cpp'
        source.write_text(CPP_FIXTURE, encoding='ascii')
        executable = self.directory / 'public_formatter'
        command = [compiler, '-std=c++17', '-O2', '-Wall', '-Wextra', '-Wpedantic', '-Werror',
                   '-fno-exceptions', '-fno-rtti', '-ffunction-sections', '-fdata-sections',
                   '-I', str(ROOT), str(source), str(ROOT / 'src/hal/recorder_csv.cpp'),
                   '-Wl,--gc-sections', '-o', str(executable)]
        compiled = subprocess.run(command, capture_output=True, text=True, timeout=90)
        self.assertEqual(compiled.returncode, 0, compiled.stdout + compiled.stderr)
        executed = subprocess.run([str(executable), *map(str, self.paths.values())],
                                  capture_output=True, text=True, timeout=20)
        self.assertEqual(executed.returncode, 0, executed.stdout + executed.stderr)
        self.assertEqual(self.paths['frames'].read_bytes(), header('frames') + FRAME_LITERAL)
        self.assertEqual(self.paths['events'].read_bytes(), header('events') + EVENT_LITERAL)
        self.assertEqual(self.paths['summary'].read_bytes(), header('summary') + summary())
        self.assert_pass(self.validate())


CPP_FIXTURE = r'''
// Uses the frozen public formatter API to emit host-only evidence files.
// Verifies compatibility with the independent Python fixtures, not hardware.
// Compiled once by test_actual_cpp_formatter_public_api_bundle_matches_independent_bytes.
#include "src/hal/recorder_csv.h"
#include <cstdio>
#include <cstdint>
#include <limits>
using namespace recorder;
bool emit(std::FILE* file, csv::FormatResult result, const char* buffer) {
    return result.status == csv::FormatStatus::OK &&
           std::fwrite(buffer, 1, result.size, file) == result.size;
}
int main(int argc, char** argv) {
    if (argc != 4) return 2;
    char buffer[csv::MAX_LINE_BYTES];
    StoredFrame frame{};
    const std::uint8_t literal[25] = {
        0,0,0,0,250,251,252,253,0,0,0,128,0,128,255,127,0,0,128,127,255,255,254,52,18};
    for (unsigned i = 0; i < 25; ++i) frame.bytes.data[i] = literal[i];
    frame.status = logframe::PackStatus::OK;
    logframe::EventBytes event{{255,255,255,255,254,253,255,255}};
    csv::SummarySnapshot summary{};
    summary.attempt.mode = static_cast<core::Mode>(0);
    summary.phase = AttemptPhase::SEALED;
    summary.frame_count = 1;
    summary.event_count = 1;
    std::FILE* f = std::fopen(argv[1], "wb");
    if (!f) return 3;
    bool ok = emit(f, csv::frameHeader(buffer, sizeof buffer), buffer);
    ok = emit(f, csv::frameRow(frame, std::numeric_limits<std::uint64_t>::max(),
                             buffer, sizeof buffer), buffer) && ok;
    ok = std::fclose(f) == 0 && ok;
    f = std::fopen(argv[2], "wb");
    if (!f) return 4;
    ok = emit(f, csv::eventHeader(buffer, sizeof buffer), buffer) && ok;
    ok = emit(f, csv::eventRow(event, 7, buffer, sizeof buffer), buffer) && ok;
    ok = std::fclose(f) == 0 && ok;
    f = std::fopen(argv[3], "wb");
    if (!f) return 5;
    ok = emit(f, csv::summaryHeader(buffer, sizeof buffer), buffer) && ok;
    ok = emit(f, csv::summaryRow(summary, buffer, sizeof buffer), buffer) && ok;
    ok = std::fclose(f) == 0 && ok;
    return ok ? 0 : 6;
}
'''


if __name__ == '__main__':
    unittest.main()
