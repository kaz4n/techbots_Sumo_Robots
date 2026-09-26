# Specifies D212 ordinary saved-RAM interpretation independently of its subject.
# Preserves strict receipt rejection while separating native anomalies from format.
# Root runs the frozen 46-method oracle serially with Python -I -B on both hosts.
import ast
import base64
import contextlib
import copy
import hashlib
import io
import json
import math
import os
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import time
import types
import unittest
from unittest import mock

REPO = Path(__file__).resolve().parents[2]
RAW_REL = Path('state/analysis/P7_ordinary_app_run_raw')
MAP_REL = RAW_REL / 'ordinary_scalar_map01.json'
SUBJECT_REL = RAW_REL / 'interpret_run01.py'
CONTRACT_REL = Path('state/analysis/P7_ordinary_app_run_contract.md')
DERIVATION_REL = RAW_REL / 'run_derivation01.json'
FIXTURE_REL = RAW_REL / 'decoder_fixture_derivation01.json'
FIXTURE_SHA = '97b76a3d364459bf15b58f98ffaa094e00ead8a4273bb034f72b98aca89e66b1'
MAP_SHA = 'd8f4eb7eb36430cff975e3032168fa61f2c249e55596401a67862b272bb08fb7'
CONTRACT_SHA = '828b334235877131580618908cc164381a988f297c4e22235eb72e34fe200e75'
DERIVATION_SHA = '9a8ef9caa96f0e30a8ad741319d5ea59668b8e6066d0c96fb59defd35f896d66'
SOURCE_SHA = '9044ebbb3cd3b2dbb7aa5984dd5ff23bfff697372f1f29d56693af9ea5eaf31a'
RUN = 'ordinary-app-9044ebbb-run01'
PARENT = '/home/arduino/sumox26_codex_build'
UPLOAD = PARENT + '/' + RUN + '-upload/upload_result.json'
CAPTURE_DIR = PARENT + '/' + RUN + '-capture'
CAPTURE = CAPTURE_DIR + '/capture_result.json'
IDENTITY = dict(user='arduino', uid=1000, gid=1000, home='/home/arduino',
                sysname='Linux', release='6.16.7-g0dd6551ae96b', machine='aarch64',
                boot_id='55c386b9-fe6d-4388-a7f4-1d91e0bb49d8', python=[3, 13, 5])
RESULT_KEYS = set('schema status retrieval_sha256 field_map_sha256 coherence '
                  'upload_result capture_result decode_first_error verified_files '
                  'windows application_findings repeated_fields_equal'.split())
WINDOWS = (('report', 537115800, 600, 'report'), ('transaction', 537113264, 504, 'transaction'), ('previous', 537113768, 48, 'previous'), ('gate', 536951336, 88, 'gate'), ('grants', 537115776, 21, 'grants'), ('attempted_word', 537117352, 4, 'attempted_word'), ('motor_port', 537117512, 40, 'motor_port'))
FIELDS = {'report': [('phase', 'u8', 0, 1, 'app::RuntimePhase'), ('fault', 'u8', 1, 1, 'app::RuntimeFault'), ('fresh', 'bool', 2, 1, None), ('initialization_complete', 'bool', 3, 1, None), ('raw_lines', 'bool', 4, 1, None), ('next_release_us', 'u32', 8, 4, None), ('missed_releases', 'u32', 12, 4, None), ('epochs', 'u32', 16, 4, None), ('service_passes', 'u32', 20, 4, None), ('maximum_execution_us', 'u32', 24, 4, None)], 'transaction': [('phase', 'u8', 0, 1, 'app::Phase'), ('fault', 'u8', 1, 1, 'app::Fault'), ('decision_made', 'bool', 2, 1, None), ('finished', 'bool', 3, 1, None), ('timing_valid', 'bool', 4, 1, None), ('started_us', 'u32', 8, 4, None), ('decision_us', 'u32', 12, 4, None), ('completed_us', 'u32', 16, 4, None), ('execution_us', 'u32', 20, 4, None), ('robot.token', 'u64', 24, 8, None), ('robot.fresh', 'bool', 32, 1, None), ('robot.outputs.duty_l', 'f32', 36, 4, None), ('robot.outputs.duty_r', 'f32', 40, 4, None), ('robot.outputs.motors_enabled', 'bool', 44, 1, None), ('robot.outputs.ui_state', 'u8', 45, 1, 'core::State'), ('robot.contract_faults', 'u16', 112, 2, None), ('robot.escape_fault', 'u8', 114, 1, 'edge::EscapeFault'), ('robot.match_start_eligible', 'bool', 420, 1, None), ('applied.feedback.applied_valid', 'bool', 424, 1, None), ('applied.feedback.token', 'u64', 432, 8, None), ('applied.feedback.applied_us', 'u32', 440, 4, None), ('applied.feedback.motors_enabled', 'bool', 444, 1, None), ('applied.feedback.duty_l', 'f32', 448, 4, None), ('applied.feedback.duty_r', 'f32', 452, 4, None), ('applied.feedback.duration_valid', 'bool', 456, 1, None), ('applied.feedback.completed_us', 'u32', 460, 4, None), ('applied.feedback.execution_us', 'u32', 464, 4, None), ('applied.fault', 'u8', 472, 1, 'motors::Fault'), ('applied.consumed', 'bool', 473, 1, None), ('halt.fresh', 'bool', 480, 1, None), ('halt.attempted', 'bool', 481, 1, None), ('halt.inhibition_confirmed', 'bool', 482, 1, None), ('halt.timing_valid', 'bool', 483, 1, None), ('halt.started_us', 'u32', 484, 4, None), ('halt.completed_us', 'u32', 488, 4, None), ('halt.fault', 'u8', 492, 1, 'motors::Fault')], 'previous': [('applied_valid', 'bool', 0, 1, None), ('token', 'u64', 8, 8, None), ('applied_us', 'u32', 16, 4, None), ('motors_enabled', 'bool', 20, 1, None), ('duty_l', 'f32', 24, 4, None), ('duty_r', 'f32', 28, 4, None), ('duration_valid', 'bool', 32, 1, None), ('completed_us', 'u32', 36, 4, None), ('execution_us', 'u32', 40, 4, None)], 'gate': [('fault_', 'u8', 44, 1, 'motors::Fault'), ('initialized_', 'bool', 45, 1, None), ('began_', 'bool', 46, 1, None), ('armed_', 'bool', 47, 1, None), ('hold_complete_', 'bool', 48, 1, None), ('release_us_', 'u32', 52, 4, None), ('last_token_', 'u64', 56, 8, None), ('halted_', 'bool', 64, 1, None), ('halt_result_.fresh', 'bool', 68, 1, None), ('halt_result_.attempted', 'bool', 69, 1, None), ('halt_result_.inhibition_confirmed', 'bool', 70, 1, None), ('halt_result_.timing_valid', 'bool', 71, 1, None), ('halt_result_.started_us', 'u32', 72, 4, None), ('halt_result_.completed_us', 'u32', 76, 4, None), ('halt_result_.fault', 'u8', 80, 1, 'motors::Fault')], 'grants': [('opponents', 'bool', 0, 1, None), ('adc_pair', 'bool', 1, 1, None), ('qtr_exclusive_pads', 'bool', 2, 1, None), ('imu_enabled', 'bool', 3, 1, None), ('imu_power_confirmed', 'bool', 4, 1, None), ('mounting.body_axis[0]', 'i8', 5, 1, None), ('mounting.body_axis[1]', 'i8', 6, 1, None), ('mounting.body_axis[2]', 'i8', 7, 1, None), ('mounting.confirmed', 'bool', 8, 1, None), ('default_line_thresholds_confirmed', 'bool', 9, 1, None), ('matrix_enabled', 'bool', 10, 1, None), ('matrix.normal_startup', 'bool', 11, 1, None), ('matrix.exclusive_boot_owner', 'bool', 12, 1, None), ('dump_enabled', 'bool', 13, 1, None), ('dump.setup_phase', 'bool', 14, 1, None), ('dump.exclusive_uart', 'bool', 15, 1, None), ('dump.ready_pin_owned', 'bool', 16, 1, None), ('dump.framing_clean', 'bool', 17, 1, None), ('dump_origin', 'u8', 18, 1, None), ('local_service_reset', 'bool', 19, 1, None), ('calibration_output_enabled', 'bool', 20, 1, None)], 'attempted_word': [('attempted_', 'bool', 2, 1, None)], 'motor_port': [('pwm_indices_[0]', 'u32', 0, 4, None), ('pwm_indices_[1]', 'u32', 4, 4, None), ('pwm_indices_[2]', 'u32', 8, 4, None), ('pwm_indices_[3]', 'u32', 12, 4, None), ('enable_configured_', 'bool', 16, 1, None), ('enable_low_', 'bool', 17, 1, None), ('settled_', 'bool', 18, 1, None), ('configured_mask_', 'u8', 19, 1, None), ('written_mask_', 'u8', 20, 1, None), ('initialized_timers_', 'u8', 21, 1, None), ('active_channels_', 'u8', 22, 1, None), ('pulses_[0]', 'u32', 24, 4, None), ('pulses_[1]', 'u32', 28, 4, None), ('pulses_[2]', 'u32', 32, 4, None), ('pulses_[3]', 'u32', 36, 4, None)]}
ENUMS = {'app::Fault': {'ABORTED': 6, 'CLOCK': 3, 'IDENTITY': 4, 'NONE': 0, 'ORDER': 2, 'RECEIPT': 5, 'SETUP': 1}, 'app::Phase': {'ACQUIRING': 2, 'DECIDED': 3, 'FAULT': 4, 'IDLE': 1, 'NOT_INITIALIZED': 0}, 'app::RuntimeFault': {'CLOCK': 2, 'NONE': 0, 'PORT': 1, 'PROJECTION': 5, 'SERVICE_LIMIT': 3, 'TRANSACTION': 4}, 'app::RuntimePhase': {'FAULT': 3, 'NOT_STARTED': 0, 'RUNNING': 1, 'STOPPED': 2, 'STOP_OBSERVING': 4}, 'core::State': {'ATTACK': 6, 'BOOT': 0, 'COUNTDOWN': 2, 'DEFEND_TURN': 7, 'DRIVE_TEST': 11, 'EDGE_ESCAPE': 8, 'IDLE': 1, 'OPENER': 3, 'REFLANK': 9, 'SEARCH': 4, 'STOPPED': 10, 'TRACK': 5}, 'edge::EscapeFault': {'INVALID_CONTEXT': 4, 'NONE': 0, 'PERMISSION_LOST': 3, 'REPLAN_LIMIT': 2, 'WHITE_PATTERN': 1}, 'motors::Fault': {'COMMAND': 4, 'IO': 3, 'NONE': 0, 'NOT_INITIALIZED': 1, 'PORT': 2, 'STOPPED': 6, 'TOKEN': 5}}
FORMATS = dict(u8='B', u16='H', u32='I', u64='Q', i8='b', f32='f', bool='B')
WIDTHS = dict(u8=1, u16=2, u32=4, u64=8, i8=1, f32=4, bool=1)
HISTORICAL = None


def sha(body):
    return hashlib.sha256(body).hexdigest()


def json_bytes(value):
    return json.dumps(value, ensure_ascii=False, separators=(',', ':'), allow_nan=False).encode()


def scalar_record(raw, value, enum_name=None, issues=()):
    return dict(raw_hex=raw.hex(), raw_unsigned=int.from_bytes(raw, 'little'),
                value=value, enum_name=enum_name, issues=list(issues))


def specimen(kind):
    """Independent inverse: chosen values determine both bytes and expectations."""
    size = next(size for name, _, size, _ in WINDOWS if name == kind)
    body, expected, leaves = bytearray([0xA5] * size), {}, []
    for index, (name, scalar, offset, width, enum) in enumerate(FIELDS[kind], 1):
        values = dict(u8=(index * 17) % 256, u16=0x8100 + index,
                      u32=0xA1000000 + index, u64=0xF102030405060000 + index,
                      i8=-index, f32=-index / 8, bool=index % 2)
        value, label = values[scalar], None
        if enum:
            label, value = sorted(ENUMS[enum].items(), key=lambda row: row[1])[index % len(ENUMS[enum])]
        raw = struct.pack('<' + FORMATS[scalar], value)
        body[offset:offset + width] = raw
        expected[name] = scalar_record(raw, bool(value) if scalar == 'bool' else value, label)
        leaves.append((name, offset, scalar))
    return bytes(body), dict(raw_hex=bytes(body).hex(), fields=expected), leaves


def selected_source(text, section):
    tree = ast.parse(text)
    node = next(n for n in tree.body if isinstance(n, (ast.ClassDef, ast.FunctionDef))
                and n.name == section['name'])
    lines = text.splitlines(keepends=True)
    if isinstance(node, ast.ClassDef):
        parts = [lines[node.lineno - 1]]
        for method in node.body:
            if isinstance(method, ast.FunctionDef) and method.name in section['methods']:
                start = min([method.lineno] + [d.lineno for d in method.decorator_list])
                parts.append(''.join(lines[start - 1:method.end_lineno]) + '\n')
        source = ''.join(parts)
    else:
        start = min([node.lineno] + [d.lineno for d in node.decorator_list])
        source = ''.join(lines[start - 1:node.end_lineno])
    if sha(source.encode()) != section['before_sha256']:
        raise AssertionError('Historical section changed: ' + section['name'])
    for step in section['steps']:
        if source.count(step['old']) != step['count']:
            raise AssertionError('Fixture replacement count: ' + section['name'])
        source = source.replace(step['old'], step['new'])
    if sha(source.encode()) != section['after_sha256']:
        raise AssertionError('Projected section changed: ' + section['name'])
    return source


def historical_provider():
    raw = (REPO / FIXTURE_REL).read_bytes()
    if sha(raw) != FIXTURE_SHA:
        raise AssertionError('Independent fixture drift')
    fixture_data = json.loads(raw)
    original = (REPO / fixture_data['historical']['path']).read_bytes()
    if sha(original) != fixture_data['historical']['sha256']:
        raise AssertionError('Historical oracle drift')
    text = original.decode('utf-8').replace('\r\n', '\n')
    projected = '\n\n'.join(selected_source(text, s) for s in fixture_data['sections'])
    if sha(projected.encode()) != fixture_data['projected_sha256']:
        raise AssertionError('Complete fixture projection changed')
    module = types.ModuleType('_d212_independent_retained_decoder_oracle')
    module.__dict__.update(globals())
    module.__name__ = '_d212_independent_retained_decoder_oracle'
    exec(compile(projected, '<frozen-d212-fixture-projection>', 'exec'), module.__dict__)
    module.PLAN = module.plan()
    return module


def changed_spec(kind, changes, *, failed=False, reads=28):
    spec = list(HISTORICAL.fixture(reads=reads, failed=failed))
    for sample in ('first', 'second'):
        full = sample + '.' + kind
        rows = [r for r in spec[1]['reads'] if r['name'] == full]
        if not rows:
            continue
        record = rows[0]
        body = bytearray(spec[2][record['file']])
        for offset, raw in changes:
            body[offset:offset + len(raw)] = raw
        spec[2][record['file']] = bytes(body)
        record['sha256'] = sha(body)
        for row in spec[1]['analysis']['snapshots']:
            if row['name'] == full:
                row['sha256'] = record['sha256']
    return spec


def finding(sample, field, code, record):
    return dict(sample=sample, field=field, code=code,
                raw_hex=record['raw_hex'], value=record['value'])


def expected_findings(windows):
    result = []
    for prefix in ('first', 'second'):
        for kind, _, _, _ in WINDOWS:
            sample = prefix + '.' + kind
            if sample not in windows:
                continue
            for name, _, _, _, enum in FIELDS[kind]:
                row = windows[sample]['fields'][name]
                codes = list(row['issues'])
                value = row['value']
                if not codes:
                    if (kind, name, value) in (('report', 'phase', 3), ('transaction', 'phase', 4)):
                        codes.append('SAMPLED_FAULT_PHASE')
                    if enum in ('app::RuntimeFault', 'app::Fault', 'motors::Fault', 'edge::EscapeFault') and value != 0:
                        codes.append('SAMPLED_FAULT_CODE')
                    if kind == 'transaction' and name == 'robot.contract_faults' and value != 0:
                        codes.append('SAMPLED_CONTRACT_BITS')
                        if value & ~1023:
                            codes.append('UNKNOWN_CONTRACT_BITS')
                    if kind == 'grants' and row['raw_unsigned'] != 0:
                        codes.append('UNEXPECTED_GRANT_VALUE')
                    if ((name.endswith(('duty_l', 'duty_r')) and value != 0) or
                            (name.endswith('motors_enabled') and value is True) or
                            (kind == 'motor_port' and name.startswith('pulses_[') and value != 0)):
                        codes.append('SAMPLED_NONZERO_MOTOR_COMMAND')
                    if kind == 'attempted_word' and value is False:
                        codes.append('SAMPLED_NOT_ATTEMPTED')
                result.extend(finding(sample, name, code, row) for code in codes)
    return result


class OrdinaryCases:
    def test_exact_map_provenance_all_107_fields_and_seven_enums(self):
        self.assertEqual(sha((REPO / CONTRACT_REL).read_bytes()), CONTRACT_SHA)
        self.assertEqual(sha((REPO / DERIVATION_REL).read_bytes()), DERIVATION_SHA)
        self.assertEqual((len(self.map_raw), sha(self.map_raw)), (42416, MAP_SHA))
        layout = json.loads(self.map_raw)
        abi = json.loads((REPO / layout['abi']['path']).read_bytes())
        self.assertEqual(layout['enums'], ENUMS)
        self.assertEqual(layout['objects'], abi['objects'])
        self.assertEqual(sum(len(v) for v in ENUMS.values()), 47)
        count = 0
        for window in layout['windows']:
            kind = window['name']
            self.assertIn((kind, window['address'], window['bytes'], kind), WINDOWS)
            rows = [(f['name'], f['scalar'], f['offset'], f['bytes'], f['enum']) for f in window['fields']]
            self.assertEqual(rows, FIELDS[kind])
            occupied = set()
            for field in window['fields']:
                evidence = field['evidence']
                self.assertEqual(abi['layouts'][evidence['type']].splitlines()[evidence['line'] - 1], evidence['text'])
                extent = set(range(field['offset'], field['offset'] + field['bytes']))
                self.assertFalse(occupied & extent)
                self.assertTrue(extent <= set(range(window['bytes'])))
                occupied |= extent
                count += 1
        self.assertEqual(count, 107)
        self.assertEqual(layout['source_only']['robot_fault_known_mask'], 1023)
        self.assertEqual(layout['source_only']['expected_grant_bytes'], '00' * 21)
        for name, digest in layout['ptype_sha256'].items():
            self.assertEqual(sha(abi['layouts'][name].encode()), digest)
        for key in ('abi', 'raw_abi'):
            pin = layout[key]
            body = (REPO / pin['path']).read_bytes()
            self.assertEqual((len(body), sha(body)), (pin['bytes'], pin['sha256']))

    def test_every_scalar_independent_little_endian_values_and_integer_endpoints(self):
        count = 0
        for kind, _, _, _ in WINDOWS:
            body, expected, _ = specimen(kind)
            with self.subTest(kind=kind), HISTORICAL.forbid_io():
                actual = self.decode(kind, body)
                self.assertEqual(actual, expected)
                self.assertEqual(list(actual['fields']), [row[0] for row in FIELDS[kind]])
                for field, row in actual['fields'].items():
                    self.assertIs(type(row['value']), type(expected['fields'][field]['value']))
                    self.assertIs(type(row['raw_unsigned']), int)
                    self.assertIs(type(row['raw_hex']), str)
                    self.assertIs(type(row['issues']), list)
            for name, scalar, offset, width, enum in FIELDS[kind]:
                count += 1
                if enum or scalar in ('bool', 'f32'):
                    continue
                endpoints = (-128, 127) if scalar == 'i8' else (0, (1 << (width * 8)) - 1)
                for value in endpoints:
                    raw = struct.pack('<' + FORMATS[scalar], value)
                    changed = bytearray(body); changed[offset:offset + width] = raw
                    decoded = self.decode(kind, bytes(changed))
                    self.assertEqual(decoded['fields'][name], scalar_record(raw, value))
                    self.assertEqual(decoded['raw_hex'], bytes(changed).hex())
                    self.assertIs(type(decoded['fields'][name]['raw_unsigned']), int)
                    self.assertIs(type(decoded['fields'][name]['value']), int)
        self.assertEqual(count, 107)

    def test_exact_window_sizes_public_arguments_and_map_admission_order(self):
        class B(bytes):
            pass
        class S(str):
            pass
        cases = [(None, None, None, 'window', '/kind'),
                 (S('report'), b'', self.map_raw, 'window', '/kind'),
                 ('report', B(b''), None, 'window', '/body'),
                 ('report', b'', B(self.map_raw), 'layout', '/')]
        for kind, body, raw, stage, path in cases:
            self.exception(TypeError, (stage, 'ARG_TYPE', path),
                           lambda: self.subject.decode(kind, body, field_map_raw=raw))
        for kind, _, size, _ in WINDOWS:
            for length in (0, size - 1, size + 1):
                with self.assertRaises(ValueError) as caught:
                    self.decode(kind, bytes(length))
                self.assertEqual(caught.exception.args[:2], ('window', 'BODY_SIZE'))
        for kind in ('RuntimeReport', 'app::RuntimeReport', 'runtime', 'trace', 'settle', 'u8', 'Report', ''):
            with self.assertRaises(ValueError) as caught:
                self.decode(kind, b'')
            self.assertEqual(caught.exception.args[:2], ('window', 'UNKNOWN_TYPE'))
        for raw, code in ((b'', 'MAP_SIZE'), (self.map_raw[:-1], 'MAP_SIZE'),
                          (self.map_raw + b' ', 'MAP_SIZE'), (bytes(len(self.map_raw)), 'MAP_HASH')):
            self.exception(ValueError, ('layout', code, '/'),
                           lambda: self.subject.decode('bad-kind', b'', field_map_raw=raw))
            result = self.subject.interpret(b'not-json', field_map_raw=raw)
            self.assertEqual(result['decode_first_error'], dict(stage='layout', code=code, path='/'))
            self.assertEqual(result['windows'], {})
        self.exception(TypeError, ('packet', 'ARG_TYPE', '/'),
                       lambda: self.subject.interpret(bytearray(), field_map_raw=b''))
        self.exception(TypeError, ('layout', 'ARG_TYPE', '/'),
                       lambda: self.subject.interpret(b'', field_map_raw=None))

    def test_all_boolean_fields_preserve_noncanonical_bytes_as_findings(self):
        fields = 0
        for kind, _, _, _ in WINDOWS:
            body, base, _ = specimen(kind)
            for name, scalar, offset, _, _ in FIELDS[kind]:
                if scalar != 'bool':
                    continue
                fields += 1
                for value in (0, 1, 2, 255):
                    changed = bytearray(body); changed[offset] = value
                    expected = copy.deepcopy(base); expected['raw_hex'] = bytes(changed).hex()
                    expected['fields'][name] = scalar_record(bytes([value]), bool(value) if value < 2 else None,
                                                           issues=() if value < 2 else ('INVALID_BOOL',))
                    actual = self.decode(kind, bytes(changed))
                    self.assertEqual(actual, expected)
                    self.assertIs(type(actual['fields'][name]['value']), bool if value < 2 else type(None))
        self.assertEqual(fields, 50)
        spec = changed_spec('grants', [(0, b'\x02')])
        result = self.interpret(HISTORICAL.packet_from(*spec[:3]))
        self.assertEqual(result['status'], 'DECODED')
        relevant = [r for r in result['application_findings'] if r['field'] == 'opponents']
        self.assertEqual([r['code'] for r in relevant], ['INVALID_BOOL', 'INVALID_BOOL'])

    def test_all_float_fields_preserve_nonfinite_bits_and_negative_zero(self):
        cases = [(0x80000000, -0.0, ()), (0, 0.0, ()), (0x3F800000, 1.0, ()),
                 (0xBF800000, -1.0, ()), (0x7F800000, None, ('NONFINITE_F32',)),
                 (0xFF800000, None, ('NONFINITE_F32',)), (0x7FC00001, None, ('NONFINITE_F32',)),
                 (0x7F800001, None, ('NONFINITE_F32',)), (0xFFC00001, None, ('NONFINITE_F32',))]
        count = 0
        for kind, _, _, _ in WINDOWS:
            body, base, _ = specimen(kind)
            for name, scalar, offset, _, _ in FIELDS[kind]:
                if scalar != 'f32':
                    continue
                count += 1
                for bits, value, issues in cases:
                    raw = bits.to_bytes(4, 'little'); changed = bytearray(body)
                    changed[offset:offset + 4] = raw
                    expected = copy.deepcopy(base); expected['raw_hex'] = bytes(changed).hex()
                    expected['fields'][name] = scalar_record(raw, value, issues=issues)
                    actual = self.decode(kind, bytes(changed))
                    self.assertEqual(actual, expected)
                    self.assertIs(type(actual['fields'][name]['value']), float if value is not None else type(None))
                    json.dumps(actual, allow_nan=False)
                    if bits == 0x80000000:
                        self.assertEqual(math.copysign(1, actual['fields'][name]['value']), -1)
        self.assertEqual(count, 6)
        spec = changed_spec('transaction', [(36, bytes.fromhex('0100c07f'))])
        result = self.interpret(HISTORICAL.packet_from(*spec[:3]))
        self.assertEqual(result['status'], 'DECODED')
        selected = [x for x in result['application_findings']
                    if x['sample'] == 'first.transaction' and x['field'] == 'robot.outputs.duty_l']
        self.assertEqual(selected, [dict(sample='first.transaction', field='robot.outputs.duty_l',
                                       code='NONFINITE_F32', raw_hex='0100c07f', value=None)])
        json.dumps(result, allow_nan=False)

    def test_unknown_enums_and_source_only_contract_bits_remain_numeric(self):
        observed = set()
        for kind, _, _, _ in WINDOWS:
            body, _, _ = specimen(kind)
            for name, _, offset, width, enum in FIELDS[kind]:
                if enum is None:
                    continue
                observed.add(enum)
                for label, value in list(ENUMS[enum].items()) + [(None, 255)]:
                    self.assertNotIn(255, ENUMS[enum].values())
                    raw = value.to_bytes(width, 'little'); changed = bytearray(body)
                    changed[offset:offset + width] = raw
                    row = self.decode(kind, bytes(changed))['fields'][name]
                    self.assertEqual(row, scalar_record(raw, value, label, () if label else ('UNKNOWN_ENUM',)))
                    self.assertIs(type(row['value']), int)
        self.assertEqual(observed, set(ENUMS))
        spec = changed_spec('transaction', [(472, b'\xff')])
        result = self.interpret(HISTORICAL.packet_from(*spec[:3]))
        selected = [x['code'] for x in result['application_findings']
                    if x['sample'] == 'first.transaction' and x['field'] == 'applied.fault']
        self.assertEqual(selected, ['UNKNOWN_ENUM'])
        for value in (0, 1, 1023, 1024, 65535):
            spec = changed_spec('transaction', [(112, value.to_bytes(2, 'little'))])
            result = self.interpret(HISTORICAL.packet_from(*spec[:3]))
            codes = [x['code'] for x in result['application_findings']
                     if x['sample'] == 'first.transaction' and x['field'] == 'robot.contract_faults']
            expected = [] if not value else ['SAMPLED_CONTRACT_BITS']
            if value & ~1023:
                expected.append('UNKNOWN_CONTRACT_BITS')
            self.assertEqual(codes, expected)
            self.assertIsNone(result['windows']['first.transaction']['fields']['robot.contract_faults']['enum_name'])

    def test_attempted_container_opaque_neighbors_and_unselected_bytes(self):
        for value in (0, 1, 2, 255):
            for neighbors in ((0, 0, 0), (255, 2, 17)):
                body = bytes((neighbors[0], neighbors[1], value, neighbors[2]))
                result = self.decode('attempted_word', body)
                self.assertEqual(set(result), {'raw_hex', 'fields'})
                self.assertEqual(list(result['fields']), ['attempted_'])
                self.assertEqual(result['raw_hex'], body.hex())
                self.assertEqual(result['fields']['attempted_'], scalar_record(bytes([value]),
                                 bool(value) if value < 2 else None, issues=() if value < 2 else ('INVALID_BOOL',)))
        for kind, _, size, _ in WINDOWS:
            body, _, _ = specimen(kind)
            used = {i for _, _, offset, width, _ in FIELDS[kind] for i in range(offset, offset + width)}
            changed = bytearray(body)
            for index in set(range(size)) - used:
                changed[index] ^= 255
            original, other = self.decode(kind, body), self.decode(kind, bytes(changed))
            self.assertEqual(original['fields'], other['fields'])
            if len(used) != size:
                self.assertNotEqual(original['raw_hex'], other['raw_hex'])

    def test_paired_observations_never_manufacture_coherence_or_reset_continuity(self):
        base = HISTORICAL.fixture()
        self.assertEqual(self.accepted(base)['repeated_fields_equal'], {n: True for n, *_ in WINDOWS})
        for kind, _, size, _ in WINDOWS:
            spec = list(HISTORICAL.fixture()); name = 'second.' + kind
            record = next(r for r in spec[1]['reads'] if r['name'] == name)
            body = bytearray(spec[2][record['file']]); offset = FIELDS[kind][0][2]
            body[offset] ^= 1; spec[2][record['file']] = bytes(body)
            record['sha256'] = sha(body)
            next(r for r in spec[1]['analysis']['snapshots'] if r['name'] == name)['sha256'] = sha(body)
            result = self.interpret(HISTORICAL.packet_from(*spec[:3]))
            self.assertEqual(result['status'], 'DECODED')
            self.assertFalse(result['repeated_fields_equal'][kind])
            self.assertEqual(result['coherence'], 'UNPROVEN')
        spec = list(HISTORICAL.fixture()); row = next(r for r in spec[1]['reads'] if r['name'] == 'second.attempted_word')
        body = bytearray(spec[2][row['file']]); body[0] ^= 255
        spec[2][row['file']] = bytes(body); row['sha256'] = sha(body)
        next(r for r in spec[1]['analysis']['snapshots'] if r['name'] == row['name'])['sha256'] = sha(body)
        result = self.interpret(HISTORICAL.packet_from(*spec[:3]))
        self.assertTrue(result['repeated_fields_equal']['attempted_word'])
        self.assertNotEqual(result['windows']['first.attempted_word']['raw_hex'], result['windows']['second.attempted_word']['raw_hex'])
        self.assertEqual(set(result), RESULT_KEYS)
        for epochs in (0, 0xA1000008, 0xFFFFFFFF):
            spec = list(HISTORICAL.fixture()); row = spec[1]['reads'][14]
            body = bytearray(spec[2][row['file']]); body[16:20] = struct.pack('<I', epochs)
            spec[2][row['file']] = bytes(body); row['sha256'] = sha(body)
            spec[1]['analysis']['snapshots'][7]['sha256'] = sha(body)
            result = self.interpret(HISTORICAL.packet_from(*spec[:3]))
            self.assertEqual(result['status'], 'DECODED')
            self.assertEqual(result['coherence'], 'UNPROVEN')
            self.assertEqual(set(result), RESULT_KEYS)

    def test_complete_and_partial_application_findings_do_not_change_collection_status(self):
        for reads, failed in ((28, False), (9, True), (28, True)):
            spec = changed_spec('transaction', [(0, b'\x04\x05'), (36, struct.pack('<f', 0.5)),
                                               (112, b'\x00\x04')], failed=failed, reads=reads)
            result = self.interpret(HISTORICAL.packet_from(*spec[:3]))
            self.assertEqual(result['status'], 'PARTIAL' if failed else 'DECODED')
            self.assertIsNone(result['decode_first_error'])
            self.assertEqual(result['application_findings'], expected_findings(result['windows']))
            self.assertTrue(result['application_findings'])
            self.assertEqual(result['coherence'], 'UNPROVEN')
            self.assertEqual(result['capture_result'], spec[1])
        for kind, offset, raw, code in (('report', 0, b'\x03', 'SAMPLED_FAULT_PHASE'),
                                       ('report', 1, b'\x04', 'SAMPLED_FAULT_CODE'),
                                       ('grants', 18, b'\x02', 'UNEXPECTED_GRANT_VALUE'),
                                       ('motor_port', 24, b'\x01\0\0\0', 'SAMPLED_NONZERO_MOTOR_COMMAND'),
                                       ('attempted_word', 2, b'\0', 'SAMPLED_NOT_ATTEMPTED')):
            spec = changed_spec(kind, [(offset, raw)])
            result = self.interpret(HISTORICAL.packet_from(*spec[:3]))
            self.assertIn(code, [x['code'] for x in result['application_findings'] if x['sample'] == 'first.' + kind])
            self.assertEqual(result['application_findings'], expected_findings(result['windows']))

    def test_fresh_results_and_raw_windows_do_not_alias_other_calls(self):
        for kind, _, _, _ in WINDOWS:
            body, expected, _ = specimen(kind)
            with HISTORICAL.forbid_io():
                one, two = self.decode(kind, body), self.decode(kind, body)
            first = FIELDS[kind][0][0]
            one['fields'][first]['issues'].append('MUTATION')
            one['fields'][first]['value'] = -999
            self.assertEqual(two, expected)
            self.assertEqual(self.decode(kind, body), expected)
        raw = json_bytes(HISTORICAL.packet_from(*HISTORICAL.fixture()[:3]))
        with HISTORICAL.forbid_io():
            one, two = self.interpret(raw), self.interpret(raw)
        one['capture_result']['reads'][0]['name'] = 'mutated'
        one['windows']['first.report']['fields']['phase']['issues'].append('mutated')
        one['application_findings'][0]['value'] = -999
        self.assertEqual(two, self.interpret(raw))
        self.assertEqual(two['windows']['first.report'], specimen('report')[1])

    def test_stale_diagnostic_maps_windows_owners_sources_and_images_are_refused(self):
        old = (REPO / 'state/analysis/P7_motor_const_compile_raw/abi_static01_decode_fields.json').read_bytes()
        self.assertNotEqual(sha(old), MAP_SHA)
        packet = json_bytes(HISTORICAL.packet_from(*HISTORICAL.fixture()[:3]))
        for candidate in (old, old + bytes(len(self.map_raw) - len(old))):
            result = self.subject.interpret(packet, field_map_raw=candidate)
            self.assertEqual(result['status'], 'REJECTED')
            self.assertEqual(result['decode_first_error']['stage'], 'layout')
        for stage in ('upload', 'capture'):
            for field, stale in (('run_id', 'app-motor-const-4bc3a2e6-run01'),
                                 ('source_sha256', '4bc3a2e6ebb497d43a433aa887ab8388dd3dab075a4f44918ed614db30034cd2')):
                spec = list(HISTORICAL.fixture()); target = spec[0 if stage == 'upload' else 1]
                self.assertNotEqual(target[field], stale); target[field] = stale
                self.rejected(HISTORICAL.packet_from(*spec[:3]), stage, 'IDENTITY')
        for index, field, value in ((6, 'bytes', 29832), (22, 'bytes', 29832),
                                    (7, 'name', 'first.trace'), (7, 'address', 536951180),
                                    (9, 'address', 537115952), (9, 'file', '11-first.previous.bin')):
            spec = list(HISTORICAL.fixture()); row = spec[1]['reads'][index]
            self.assertNotEqual(row[field], value); row[field] = value
            self.rejected(HISTORICAL.packet_from(*spec[:3]), 'capture', 'READ_PLAN')
        stale_path = PARENT + '/app-motor-const-4bc3a2e6-run01-upload/upload_result.json'
        packet = HISTORICAL.packet_from(*HISTORICAL.fixture()[:3])
        self.assertNotEqual(packet['files'][0]['path'], stale_path)
        packet['files'][0]['path'] = stale_path
        self.rejected(packet, 'files', 'PATH', '/files/0/path')
        packet = HISTORICAL.packet_from(*HISTORICAL.fixture()[:3])
        self.assertEqual(len(packet['files']), 16)
        packet['files'].append(copy.deepcopy(packet['files'][0]))
        packet['closing_file_checks'] = 17
        self.rejected(packet, 'packet', 'FILE_COUNT', '/files')

    def test_first_structural_error_preserves_receipts_prior_windows_and_anomaly_values(self):
        spec = changed_spec('report', [(2, b'\x02')], failed=True)
        spec[1]['postcheck_errors'] = [dict(check='closure', type='Error', message='retained secondary')]
        packet = HISTORICAL.packet_from(*spec[:3])
        packet['files'][3]['data_base64'] = '!'
        result = self.rejected(packet, 'files', 'BASE64', '/files/3/data_base64')
        self.assertEqual(list(result['windows']), ['first.report'])
        self.assertEqual(result['windows']['first.report']['fields']['fresh'], scalar_record(b'\x02', None, issues=('INVALID_BOOL',)))
        self.assertEqual(result['application_findings'], expected_findings(result['windows']))
        self.assertEqual(result['capture_result'], spec[1])
        self.assertEqual(result['upload_result'], spec[0])
        self.assertEqual(len(result['verified_files']), 3)
        self.assertTrue(all(v is None for v in result['repeated_fields_equal'].values()))
        packet['status'] = 'OTHER'
        result = self.rejected(packet, 'packet', 'STATUS', '/status')
        self.assertEqual(result['verified_files'], [])
        self.assertEqual(result['application_findings'], [])


def load_tests(loader, tests, pattern):
    global HISTORICAL
    HISTORICAL = historical_provider()
    ordinary = type('OrdinaryOracle', (OrdinaryCases, HISTORICAL.OracleBase), {'__module__': __name__})
    suite = unittest.TestSuite()
    for cls in (HISTORICAL.PacketOracle, HISTORICAL.MainOracle, ordinary):
        cls.__module__ = __name__
        suite.addTests(loader.loadTestsFromTestCase(cls))
    if suite.countTestCases() != 46:
        raise AssertionError('Expected27 packet +7 main +12 ordinary methods')
    return suite


if __name__ == '__main__':
    unittest.main()
