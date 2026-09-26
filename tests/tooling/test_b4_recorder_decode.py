# Checks the D216 retained-recorder decoder through its fixed public byte API.
# Uses observed D215 layout data and independent D073 wire/CSV expectations.
# Root runs this focused oracle after separate implementation and oracle seals.
import builtins
from contextlib import ExitStack
import hashlib
import importlib
import io
import json
import os
from pathlib import Path
import socket
import struct
import subprocess
import sys
import unittest
from unittest import mock


ROOT = Path(__file__).absolute().parents[2]
MAP_PATH = ROOT / 'state/analysis/P7_b4_recorder_decode_raw/layout01.json'
MAP_BYTES = 4443
MAP_SHA = 'f9b4b1531b9f714fb2b424d9613787449b2172fcc7a0e96292dd51d37d8c0b2d'
OWNER_BYTES = 159200
U32 = (1 << 32) - 1
U64 = (1 << 64) - 1
ROLES = ('frames', 'events', 'summary')
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
LOSS_FIELDS = (
    'missing_results', 'rejected_results', 'identity_rejected', 'malformed_batches',
    'event_semantic_rejected', 'upstream_event_rejected', 'upstream_event_invalid',
    'source_regressions', 'skipped_frames', 'frame_overwritten', 'frame_rejected_status',
    'frame_clamped', 'frame_invalid', 'event_rejected', 'event_overflow',
    'ticks_saturated', 'upstream_event_overflow', 'timing_incomplete',
    'recording_incomplete', 'final_frame_missing', 'interrupted', 'terminal_exhausted')
BOOL_NAMES = ('ticks_saturated', 'upstream_event_overflow', 'timing_incomplete',
              'recording_incomplete', 'go_seen', 'final_frame_missing', 'interrupted',
              'terminal_exhausted', 'event_overflow')
CSV_TO_NATIVE = {
    'epoch_token': 'summary_.epoch_token',
    'last_frame_token': 'summary_.last_frame_token',
    'release_us': 'summary_.release_us', 'mode': 'summary_.mode', 'phase': 'phase_',
    'observed_results': 'summary_.observed_results',
    'missing_results': 'summary_.missing_results',
    'rejected_results': 'summary_.rejected_results',
    'identity_rejected': 'summary_.identity_rejected',
    'malformed_batches': 'summary_.malformed_batches',
    'event_semantic_rejected': 'summary_.event_semantic_rejected',
    'upstream_event_rejected': 'summary_.upstream_event_rejected',
    'upstream_event_invalid': 'summary_.upstream_event_invalid',
    'source_regressions': 'summary_.source_regressions',
    'skipped_frames': 'summary_.skipped_frames',
    'ticks': 'summary_.ticks.ticks', 'overruns': 'summary_.ticks.overruns',
    'tick_max_us': 'summary_.ticks.max_us',
    'ticks_saturated': 'summary_.ticks.saturated',
    'upstream_event_overflow': 'summary_.upstream_event_overflow',
    'timing_incomplete': 'summary_.timing_incomplete',
    'recording_incomplete': 'summary_.recording_incomplete',
    'go_seen': 'summary_.go_seen', 'final_frame_missing': 'summary_.final_frame_missing',
    'interrupted': 'summary_.interrupted', 'terminal_exhausted': 'summary_.terminal_exhausted',
    'frame_count': 'frames_.size_', 'frame_overwritten': 'frames_.overwritten_',
    'frame_rejected_status': 'frames_.rejected_status_',
    'frame_clamped': 'frames_.clamped_', 'frame_invalid': 'frames_.invalid_',
    'event_count': 'events_.size_', 'event_overflow': 'events_.overflowed_',
    'event_rejected': 'events_.rejected_',
}
FRAME_FORMAT = '<IBBBBihhhbbHBH'
FRAME_VALUES = [0, 250, 251, 252, 253, -(1 << 31), -32768, 32767, 0,
                -128, 127, 65535, 254, 4660]
# Accepted D073 literal payload; only exported ordinal changes to the API's zero.
FRAME_LITERAL = (
    b'1,0,0,0,250,251,252,253,-2147483648,-32768,32767,0,'
    b'-128,127,65535,254,4660,00000000fafbfcfd000000800080ff7f0000807ffffffe3412\n')
EVENT_LITERAL = b'1,0,4294967295,254,253,65535,fffffffffefdffff\n'
TOP_KEYS = set(('schema_version', 'schema', 'raw_owner', 'raw_sha256', 'layout_sha256', 'layout_binding',
                'export_status', 'native_values', 'summary', 'csv', 'format_integrity',
                'consistency', 'errors', 'files', 'recording', 'provenance', 'body_origin',
                'coherence', 'common_attempt_verified', 'transport_verified',
                'hardware_acceptance'))


def header(role):
    return (','.join(NAMES[role]) + '\n').encode('ascii')


def row(values):
    return (','.join(map(str, values)) + '\n').encode('ascii')


def frame_row(values, ordinal, status):
    wire = struct.pack(FRAME_FORMAT, *values)
    return row([1, ordinal, status, *values, wire.hex()])


def event_row(values, ordinal):
    wire = struct.pack('<IBBH', *values)
    return row([1, ordinal, *values, wire.hex()])


class OwnerFixture:
    """Write only immutable observed map locations, never guess native padding."""
    def __init__(self, layout, fill=0):
        self.layout = layout
        self.data = bytearray([fill]) * layout['owner']['bytes']
        self.values = {}
        for name in layout['fields']:
            self.set_native(name, 0)
        self.set_summary(phase=3)

    def set_native(self, name, value):
        field = self.layout['fields'][name]
        start, width = field['offset'], field['bytes']
        self.data[start:start + width] = value.to_bytes(width, 'little')
        self.values[name] = value
        return self

    def set_summary(self, **changes):
        for name, value in changes.items():
            self.set_native(CSV_TO_NATIVE[name], value)
        return self

    def set_status(self, physical_slot, status):
        base = self.layout['arrays']['frames_.statuses_']['offset']
        index, shift = base + physical_slot // 4, 2 * (physical_slot % 4)
        self.data[index] = (self.data[index] & ~(3 << shift)) | (status << shift)
        return self

    def frame(self, physical_slot, values=None, status=0):
        values = FRAME_VALUES if values is None else values
        array = self.layout['arrays']['frames_.payloads_']
        start = array['offset'] + physical_slot * array['stride']
        self.data[start:start + array['stride']] = struct.pack(FRAME_FORMAT, *values)
        return self.set_status(physical_slot, status)

    def event(self, index, values=(U32, 254, 253, 65535)):
        array = self.layout['arrays']['events_.events_']
        start = array['offset'] + index * array['stride']
        self.data[start:start + array['stride']] = struct.pack('<IBBH', *values)
        return self

    def summary(self):
        values = {name: self.values[field] for name, field in CSV_TO_NATIVE.items()}
        values['schema_version'] = 1
        values['incomplete'] = int(any(values[name] != 0 for name in LOSS_FIELDS))
        return values

    def body(self):
        return bytes(self.data)


class B4RecorderDecodeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.layout_raw = MAP_PATH.read_bytes()
        if len(cls.layout_raw) != MAP_BYTES or hashlib.sha256(cls.layout_raw).hexdigest() != MAP_SHA:
            raise AssertionError('Independent fixture requires the exact observed D215 map.')
        cls.layout = json.loads(cls.layout_raw)
        sys.path.insert(0, str(ROOT))
        cls.subject = importlib.import_module('tools.decode_b4_recorder')

    def fixture(self, fill=0):
        return OwnerFixture(self.layout, fill)

    def decode(self, body, layout=None):
        return self.subject.decode_recorder(
            body, layout_raw=self.layout_raw if layout is None else layout)

    def assert_boundary(self, report, body, layout=None):
        layout = self.layout_raw if layout is None else layout
        self.assertEqual(set(report), TOP_KEYS)
        self.assertIs(type(report['schema_version']), int)
        self.assertEqual(report['schema_version'], 1)
        self.assertEqual(report['schema'], 'b4-recorder-decode-v1')
        self.assertEqual(report['raw_owner'], body)
        self.assertIs(type(report['raw_owner']), bytes)
        self.assertEqual(report['raw_sha256'], hashlib.sha256(body).hexdigest())
        self.assertEqual(report['layout_sha256'], hashlib.sha256(layout).hexdigest())
        self.assertEqual(report['provenance'], {'status': 'ABSENT', 'evidence_kind': 'UNKNOWN',
                                              'closure': 'UNKNOWN', 'declared': None})
        self.assertEqual(report['body_origin'], 'UNPROVEN')
        self.assertEqual(report['coherence'], 'UNPROVEN')
        for name in ('common_attempt_verified', 'transport_verified', 'hardware_acceptance'):
            self.assertIs(report[name], False)
        self.assertEqual(set(report['csv']), set(ROLES))
        self.assertEqual(set(report['files']), set(ROLES))
        for error in report['errors']:
            self.assertEqual(set(error), {'category', 'code', 'message'})
            self.assertTrue(all(type(error[key]) is str for key in error))
            self.assertTrue(error['message'])

    def assert_export(self, report, fixture, consistency='PASS'):
        self.assert_boundary(report, fixture.body())
        self.assertEqual(report['layout_binding'], 'PASS')
        self.assertEqual(report['export_status'], 'PASS')
        self.assertEqual(report['format_integrity'], 'PASS')
        self.assertEqual(report['consistency'], consistency)
        self.assertEqual(report['native_values'], fixture.values)
        self.assertEqual(report['summary'], fixture.summary())
        for role in ROLES:
            csv = report['csv'][role]
            self.assertIs(type(csv), bytes)
            self.assertTrue(csv.startswith(header(role)))
            self.assertTrue(csv.endswith(b'\n'))
            self.assertNotIn(b'\r', csv)
            self.assertNotIn(b'\0', csv)
            self.assertEqual(report['files'][role], {
                'sha256': hashlib.sha256(csv).hexdigest(), 'bytes': len(csv),
                'rows': len(csv.splitlines()) - 1})
        expected = header('summary') + row([fixture.summary()[name] for name in SUMMARY_NAMES])
        self.assertEqual(report['csv']['summary'], expected)
        self.assertEqual(report['files']['summary']['rows'], 1)

    def assert_refused(self, report, body, code, category, layout=None):
        self.assert_boundary(report, body, layout)
        self.assertEqual(report['export_status'], 'REFUSED')
        self.assertEqual(report['csv'], dict.fromkeys(ROLES))
        self.assertEqual(report['files'], dict.fromkeys(ROLES))
        self.assertNotEqual(report['format_integrity'], 'PASS')
        self.assertEqual(report['consistency'], 'NOT_CHECKED')
        self.assertTrue(report['errors'])
        self.assertEqual(report['errors'][0]['code'], code)
        self.assertEqual(report['errors'][0]['category'], category)

    def test_exact_observed_map_has_35_essential_fields_and_fixed_artifact_binding(self):
        self.assertEqual(self.layout['schema'], 'b4-recorder-layout-v1')
        self.assertEqual(self.layout['byte_order'], 'little')
        self.assertEqual(self.layout['owner'], {'type': 'recorder::AttemptRecorder',
                                              'address': 536954120, 'bytes': 159200,
                                              'alignment': 8})
        self.assertEqual(self.layout['binding'], {
            'source_sha256': '9044ebbb3cd3b2dbb7aa5984dd5ff23bfff697372f1f29d56693af9ea5eaf31a',
            'artifacts_sha256': '0acaa30a4ba01ac5c9ff8c8fddc66c4bec94e033b1194ec63271f12affb6c085',
            'abi_sha256': '25bf57646977fec8b4614b06cfe2b3df2e3bb94172122b2ee8f5ceaaec6677bc',
            'profile': 'b4-app-m0-static'})
        self.assertEqual(set(self.layout['fields']), set(CSV_TO_NATIVE.values()) | {'frames_.first_'})
        self.assertEqual(len(self.layout['fields']), 35)
        bools = {key for key, field in self.layout['fields'].items() if field['kind'] == 'bool'}
        self.assertEqual(bools, {CSV_TO_NATIVE[name] for name in BOOL_NAMES})
        self.assertEqual(self.layout['arrays'], {
            'frames_.payloads_': {'offset': 0, 'bytes': 125025, 'stride': 25, 'count': 5001},
            'frames_.statuses_': {'offset': 125025, 'bytes': 1251, 'stride': 1, 'count': 1251},
            'events_.events_': {'offset': 126300, 'bytes': 32768, 'stride': 8, 'count': 4096}})

    def test_empty_owner_exports_exact_headers_and_complete_summary_without_origin_claim(self):
        fixture = self.fixture()
        report = self.decode(fixture.body())
        self.assert_export(report, fixture)
        self.assertEqual(report['csv']['frames'], header('frames'))
        self.assertEqual(report['csv']['events'], header('events'))
        self.assertEqual(report['recording'], {'loss': 'NONE_REPORTED', 'lifecycle': 'SEALED',
                                             'phase_code': 3})
        self.assertEqual(report['errors'], [])

    def test_d073_literal_csv_preserves_signed_extrema_raw_minus128_and_unknown_payloads(self):
        fixture = self.fixture().set_summary(frame_count=1, event_count=1)
        fixture.frame(0).event(0)
        report = self.decode(fixture.body())
        self.assert_export(report, fixture)
        self.assertEqual(report['csv']['frames'], header('frames') + FRAME_LITERAL)
        self.assertEqual(report['csv']['events'], header('events') + EVENT_LITERAL)

    def test_wrapped_frames_and_event_prefix_preserve_timestamp_insertion_order(self):
        fixture = self.fixture().set_native('frames_.first_', 5000)
        fixture.set_summary(frame_count=3, event_count=4, frame_clamped=1, frame_invalid=1)
        frames = []
        for index, stamp in enumerate((U32, 0, U32)):
            values = list(FRAME_VALUES)
            values[0] = stamp
            fixture.frame((5000 + index) % 5001, values, index)
            frames.append(frame_row(values, index, index))
        events = []
        for index, stamp in enumerate((U32, 0, 0, U32 - 1)):
            values = (stamp, 200 + index, 255 - index, 65535 - index)
            fixture.event(index, values)
            events.append(event_row(values, index))
        report = self.decode(fixture.body())
        self.assert_export(report, fixture)
        self.assertEqual(report['csv']['frames'], header('frames') + b''.join(frames))
        self.assertEqual(report['csv']['events'], header('events') + b''.join(events))

    def test_four_status_lanes_and_unused_status3_are_distinguished(self):
        fixture = self.fixture().set_summary(frame_count=4, frame_clamped=2, frame_invalid=1)
        fixture.set_native('frames_.first_', 4)
        statuses = (2, 1, 0, 1)
        for index, status in enumerate(statuses):
            fixture.frame(4 + index, status=status)
        fixture.set_status(3, 3).set_status(8, 3).set_status(5000, 3)
        report = self.decode(fixture.body())
        self.assert_export(report, fixture)
        expected = b''.join(frame_row(FRAME_VALUES, n, status) for n, status in enumerate(statuses))
        self.assertEqual(report['csv']['frames'], header('frames') + expected)

    def test_exact_full_capacities_and_last_first_index_are_accepted(self):
        fixture = self.fixture().set_native('frames_.first_', 5000)
        fixture.set_summary(frame_count=5001, event_count=4096)
        zero_frame = [0] * 14
        zero_event = (0, 0, 0, 0)
        report = self.decode(fixture.body())
        self.assert_export(report, fixture)
        self.assertEqual(report['files']['frames']['rows'], 5001)
        self.assertEqual(report['files']['events']['rows'], 4096)
        self.assertEqual(report['csv']['frames'].splitlines()[1], frame_row(zero_frame, 0, 0).rstrip(b'\n'))
        self.assertEqual(report['csv']['frames'].splitlines()[-1], frame_row(zero_frame, 5000, 0).rstrip(b'\n'))
        self.assertEqual(report['csv']['events'].splitlines()[-1], event_row(zero_event, 4095).rstrip(b'\n'))

    def test_all_summary_columns_and_native_unsigned_widths_preserve_maxima(self):
        fixture = self.fixture()
        for name, field in self.layout['fields'].items():
            maximum = 1 if field['kind'] == 'bool' else (1 << (8 * field['bytes'])) - 1
            fixture.set_native(name, maximum)
        fixture.set_native('frames_.first_', 0).set_summary(frame_count=0, event_count=0)
        report = self.decode(fixture.body())
        self.assert_export(report, fixture)
        self.assertEqual(len(report['summary']), 36)
        self.assertEqual(report['summary']['epoch_token'], U64)
        self.assertEqual(report['summary']['last_frame_token'], U64)
        self.assertEqual(report['summary']['ticks'], U64)
        self.assertEqual(report['summary']['overruns'], U64)
        self.assertEqual(report['summary']['frame_overwritten'], U32)
        self.assertEqual(report['summary']['incomplete'], 1)
        self.assertEqual(report['recording']['lifecycle'], 'UNKNOWN')

    def test_distinct_scalar_values_detect_swapped_fields_and_endian_errors(self):
        fixture = self.fixture()
        for index, (name, field) in enumerate(self.layout['fields'].items()):
            values = {'bool': index % 2, 'u8': 200 + index,
                      'u32': 0x12340000 + index, 'u64': 0x0102030405060708 + index}
            fixture.set_native(name, values[field['kind']])
        fixture.set_native('frames_.first_', 4999)
        fixture.set_summary(frame_count=2, event_count=2, frame_overwritten=U32)
        fixture.frame(4999).frame(5000).event(0).event(1, (1234, 9, 8, 7))
        report = self.decode(fixture.body())
        self.assert_export(report, fixture)
        self.assertEqual(report['summary']['epoch_token'], 0x0102030405060711)
        self.assertEqual(report['summary']['last_frame_token'], 0x0102030405060712)
        self.assertNotEqual(report['summary']['ticks'], report['summary']['overruns'])

    def test_each_of_22_loss_fields_independently_sets_incomplete_without_hiding_data(self):
        for name in LOSS_FIELDS:
            with self.subTest(field=name):
                fixture = self.fixture().set_summary(**{name: 1})
                report = self.decode(fixture.body())
                consistency = 'FAIL' if name in ('frame_clamped', 'frame_invalid') else 'PASS'
                self.assert_export(report, fixture, consistency)
                self.assertEqual(report['summary']['incomplete'], 1)
                self.assertEqual(report['recording']['loss'], 'REPORTED')

    def test_nonloss_fields_and_lifecycle_do_not_invent_incomplete(self):
        fixture = self.fixture().set_summary(epoch_token=U64, last_frame_token=U64,
            release_us=U32, mode=255, phase=4, observed_results=U32, ticks=U64,
            overruns=U64, tick_max_us=U32, go_seen=1)
        report = self.decode(fixture.body())
        self.assert_export(report, fixture)
        self.assertEqual(report['summary']['incomplete'], 0)
        self.assertEqual(report['recording']['loss'], 'NONE_REPORTED')
        self.assertEqual(report['recording']['lifecycle'], 'INTERRUPTED')

    def test_lifetime_status_consistency_is_separate_from_format_and_export(self):
        cases = (
            (1, 0, 0, 0, 'FAIL', 'STATUS_LIFETIME'),
            (0, 1, 0, 0, 'FAIL', 'STATUS_WITHOUT_OVERWRITE'),
            (0, 2, 1, 1, 'FAIL', 'STATUS_OVERWRITE_BOUND'),
            (0, 2, 1, 3, 'PASS', None),
            (2, 0, 1, 0, 'PASS', None),
            (1, U32, U32, U32, 'PASS', None),
        )
        for status, clamped, invalid, overwritten, expected, code in cases:
            with self.subTest(status=status, clamped=clamped, invalid=invalid, overwritten=overwritten):
                fixture = self.fixture().set_summary(frame_count=1, frame_clamped=clamped,
                    frame_invalid=invalid, frame_overwritten=overwritten)
                fixture.frame(0, status=status)
                report = self.decode(fixture.body())
                self.assert_export(report, fixture, expected)
                if code:
                    self.assertIn(code, [error['code'] for error in report['errors']])
                else:
                    self.assertEqual(report['errors'], [])
                if status:
                    self.assertEqual(report['recording']['loss'], 'REPORTED')

    def test_each_known_and_unknown_phase_preserves_numeric_code_and_lifecycle(self):
        for phase, lifecycle in ((0, 'EMPTY'), (1, 'UNFINISHED'), (2, 'UNFINISHED'),
                                 (3, 'SEALED'), (4, 'INTERRUPTED'), (5, 'UNKNOWN'), (255, 'UNKNOWN')):
            with self.subTest(phase=phase):
                fixture = self.fixture().set_summary(phase=phase, mode=254)
                report = self.decode(fixture.body())
                self.assert_export(report, fixture)
                self.assertEqual(report['recording'], {'loss': 'NONE_REPORTED',
                                                      'lifecycle': lifecycle, 'phase_code': phase})
                self.assertEqual(report['summary']['mode'], 254)

    def test_any_changed_map_bytes_refuse_with_raw_body_and_no_origin_claim(self):
        body = self.fixture().body()
        variants = (b'', b'{}', b'not json', self.layout_raw + b' ',
                    self.layout_raw.replace(b'b4-app-m0-static', b'b4-app-m1-static'),
                    self.layout_raw.replace(b'159200', b'159201', 1),
                    bytes([255]) * 65536)
        for layout in variants:
            with self.subTest(bytes=len(layout)):
                report = self.decode(body, layout)
                self.assert_refused(report, body, 'LAYOUT_IDENTITY', 'admission', layout)
                self.assertEqual(report['layout_binding'], 'FAIL')
                self.assertEqual(report['native_values'], {})
                self.assertIsNone(report['summary'])

    def test_owner_length_must_equal_exact_observed_extent(self):
        for size in (0, OWNER_BYTES - 1, OWNER_BYTES + 1, 1048576):
            with self.subTest(bytes=size):
                body = bytes(size)
                report = self.decode(body)
                self.assert_refused(report, body, 'OWNER_SIZE', 'admission')
                self.assertEqual(report['layout_binding'], 'PASS')
                self.assertEqual(report['native_values'], {})
                self.assertIsNone(report['summary'])

    def test_exact_byte_types_and_limits_refuse_before_hash_or_parse(self):
        class ByteSubclass(bytes):
            pass
        body = self.fixture().body()
        with mock.patch.object(hashlib, 'sha256', side_effect=AssertionError('early hash')):
            with mock.patch.object(json, 'loads', side_effect=AssertionError('early parse')):
                for invalid in (None, '', bytearray(body), memoryview(body), ByteSubclass(body)):
                    with self.subTest(body_type=type(invalid).__name__):
                        with self.assertRaises(TypeError):
                            self.subject.decode_recorder(invalid, layout_raw=self.layout_raw)
                for invalid in (None, '', bytearray(self.layout_raw), ByteSubclass(self.layout_raw)):
                    with self.subTest(layout_type=type(invalid).__name__):
                        with self.assertRaises(TypeError):
                            self.subject.decode_recorder(body, layout_raw=invalid)
                with self.assertRaises(TypeError):
                    self.subject.decode_recorder(bytes(1048577), layout_raw=None)
                for owner, layout in ((bytes(1048577), b''), (body, bytes(65537)),
                                      (bytes(1048577), bytes(65537))):
                    with self.assertRaises(ValueError):
                        self.subject.decode_recorder(owner, layout_raw=layout)

    def test_every_interpreted_boolean_rejects2_and_preserves_all_raw_scalars(self):
        for name in BOOL_NAMES:
            with self.subTest(boolean=name):
                fixture = self.fixture().set_summary(**{name: 2})
                report = self.decode(fixture.body())
                self.assert_refused(report, fixture.body(), 'NATIVE_BOOL', 'native')
                self.assertEqual(report['native_values'], fixture.values)
                self.assertEqual(report['native_values'][CSV_TO_NATIVE[name]], 2)
                self.assertIsNone(report['summary'])
                self.assertEqual(report['recording'], {'loss': 'UNKNOWN', 'lifecycle': 'SEALED',
                                                      'phase_code': 3})

    def test_indices_refuse_outside_capacity_and_first_is_checked_even_when_empty(self):
        cases = (('frames_.first_', 5001, 'FRAME_FIRST_RANGE'),
                 ('frames_.first_', U32, 'FRAME_FIRST_RANGE'),
                 ('frames_.size_', 5002, 'FRAME_SIZE_RANGE'),
                 ('frames_.size_', U32, 'FRAME_SIZE_RANGE'),
                 ('events_.size_', 4097, 'EVENT_SIZE_RANGE'),
                 ('events_.size_', U32, 'EVENT_SIZE_RANGE'))
        for name, value, code in cases:
            with self.subTest(field=name, value=value):
                fixture = self.fixture().set_native(name, value)
                report = self.decode(fixture.body())
                self.assert_refused(report, fixture.body(), code, 'native')
                self.assertEqual(report['native_values'], fixture.values)
                self.assertIsNone(report['summary'])
        fixture = self.fixture().set_native('frames_.first_', 5000)
        self.assert_export(self.decode(fixture.body()), fixture)

    def test_retained_status3_refuses_all_csv_but_keeps_decoded_summary(self):
        for first, slot in ((0, 0), (2, 3), (5000, 0)):
            with self.subTest(first=first, corrupt_slot=slot):
                fixture = self.fixture().set_native('frames_.first_', first)
                fixture.set_summary(frame_count=2, event_count=1, missing_results=1)
                fixture.frame(first).frame((first + 1) % 5001).event(0)
                fixture.set_status(slot, 3)
                report = self.decode(fixture.body())
                self.assert_refused(report, fixture.body(), 'PACK_STATUS', 'native')
                self.assertEqual(report['native_values'], fixture.values)
                self.assertEqual(report['summary'], fixture.summary())
                self.assertEqual(report['recording']['loss'], 'REPORTED')

    def test_unused_bytes_lanes_and_uninterpreted_terminal_bool_do_not_refuse(self):
        fixture = self.fixture(fill=255).set_summary(frame_count=1, event_count=1)
        fixture.frame(0).event(0)
        # D215 observes phase_ at159193 and terminal_seen_ at159194, outside the
        # essential map. Preserve that raw value without interpreting it as a bool.
        fixture.data[159194] = 2
        body = fixture.body()
        report = self.decode(body)
        self.assert_export(report, fixture)
        self.assertEqual(report['raw_owner'][159194], 2)
        self.assertEqual(report['csv']['frames'], header('frames') + FRAME_LITERAL)
        self.assertEqual(report['csv']['events'], header('events') + EVENT_LITERAL)

    def test_public_decode_is_pure_and_repeated_outputs_do_not_alias_mutable_state(self):
        fixture = self.fixture().set_summary(frame_count=1, event_count=1)
        fixture.frame(0).event(0)
        body, layout = fixture.body(), self.layout_raw
        blocked = AssertionError('Pure decoder attempted external I/O')
        with ExitStack() as stack:
            for owner, name in ((builtins, 'open'), (io, 'open'), (os, 'open'),
                                (os, 'system'), (subprocess, 'Popen'), (socket, 'socket')):
                stack.enter_context(mock.patch.object(owner, name, side_effect=blocked))
            first = self.decode(body)
            first['native_values']['phase_'] = 255
            first['summary']['phase'] = 255
            first['csv']['frames'] = b'changed'
            first['files']['frames']['rows'] = U32
            second = self.decode(body)
            refused = self.decode(body[:-1])
        self.assert_export(second, fixture)
        self.assert_refused(refused, body[:-1], 'OWNER_SIZE', 'admission')
        self.assertEqual(body, fixture.body())
        self.assertEqual(layout, self.layout_raw)


if __name__ == '__main__':
    unittest.main(verbosity=2)
