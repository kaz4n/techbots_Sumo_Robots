# Specifies the D201 offline decoder from the adopted contract and pinned ABI.
# Independent inverse fixtures retain raw numbers, failed prefixes and boundaries.
# Root runs this frozen unittest oracle serially with Python -B on Linux/Windows.
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
RAW_REL = Path('state/analysis/P7_motor_const_run_raw')
MAP_REL = Path('state/analysis/P7_motor_const_compile_raw/abi_static01_decode_fields.json')
SUBJECT_REL = RAW_REL / 'interpret_run01.py'
CONTRACT_REL = Path('state/analysis/P7_motor_const_run_contract.md')
MAP_SHA = 'ecceef9168975b206cf3b3c7d11f24dc9feb16083dbf0f68e11c7b7b94433709'
CONTRACT_SHA = '1949c7db32bfda4c3318095597b740ea17644ec5b0109cc2e589387842dbbf85'
SOURCE_SHA = '4bc3a2e6ebb497d43a433aa887ab8388dd3dab075a4f44918ed614db30034cd2'
RUN = 'app-motor-const-4bc3a2e6-run01'
PARENT = '/home/arduino/sumox26_codex_build'
UPLOAD = PARENT + '/' + RUN + '-upload/upload_result.json'
CAPTURE_DIR = PARENT + '/' + RUN + '-capture'
CAPTURE = CAPTURE_DIR + '/capture_result.json'
IDENTITY = dict(user='arduino', uid=1000, gid=1000, home='/home/arduino',
                sysname='Linux', release='6.16.7-g0dd6551ae96b', machine='aarch64',
                boot_id='55c386b9-fe6d-4388-a7f4-1d91e0bb49d8', python=[3, 13, 5])
RESULT_KEYS = set('schema status retrieval_sha256 field_map_sha256 coherence '
                  'upload_result capture_result decode_first_error verified_files '
                  'windows settle_annotations repeated_fields_equal'.split())
WINDOWS = (
    ('trace', 536951180, 2128, 'motor_fault::TraceReport'),
    ('report', 537119696, 1168, 'app_motor_observe::Report'),
    ('runtime', 537117984, 600, 'app::RuntimeReport'),
    ('transaction', 537115448, 504, 'app::TransactionReport'),
    ('settle', 537121768, 28, 'motors::SettleProbeReport'),
    ('gate', 536953520, 88, 'motors::MotorGate'),
)

# These 115 declarations are transcribed from the pinned observed map, never
# harvested from the implementation. The fixture writer is the inverse of decode.
DECLARATIONS = {
    'app::RuntimeReport': (600, 'phase:u8:0 fault:u8:1 fresh:bool:2 initialization_complete:bool:3 next_release_us:u32:8 missed_releases:u32:12 epochs:u32:16 service_passes:u32:20 maximum_execution_us:u32:24'),
    'app::TransactionReport': (504, 'phase:u8:0 fault:u8:1 decision_made:bool:2 finished:bool:3 timing_valid:bool:4 started_us:u32:8 decision_us:u32:12 completed_us:u32:16 execution_us:u32:20 robot:RobotResult:24 applied:Result:424 halt:HaltResult:480 recorded:u8:496'),
    'app_motor_observe::Report': (1168, 'phase:u8:0 reason:u8:1 begin_called:bool:2 begin_finished:bool:3 begin_ok:bool:4 before_abort_valid:bool:5 abort_called:bool:6 abort_returned:bool:7 last_step_returned:bool:8 polls:u32:12 before_abort:Snapshot:16'),
    'app_motor_observe::Snapshot': (1152, 'runtime:RuntimeReport:0 transaction:TransactionReport:600 previous:PreviousTick:1104'),
    'core::Outputs': (12, 'duty_l:f32:0 duty_r:f32:4 motors_enabled:bool:8 ui_state:u8:9'),
    'countdown::LifecycleResult': (28, 'gate:CountdownResult:0'),
    'countdown::Result': (8, 'phase:u8:0 motion_permitted:bool:1 start_release:bool:2 go:bool:3 release_us:u32:4'),
    'fsm::PreviousTick': (48, 'applied_valid:bool:0 token:u64:8 applied_us:u32:16 motors_enabled:bool:20 duty_l:f32:24 duty_r:f32:28 duration_valid:bool:32 completed_us:u32:36 execution_us:u32:40'),
    'fsm::RobotResult': (400, 'token:u64:0 fresh:bool:8 outputs:Outputs:12 running_mode:u8:24 lifecycle:LifecycleResult:32 contract_faults:u16:88 escape_fault:u8:90'),
    'motor_fault::Call': (32, 'stage:u8:0 operation:u8:1 channel:u8:2 application:u32:4 requested_high:bool:8 period_cycles:u32:12 pulse_cycles:u32:16 invoked:bool:20 completed:bool:21 returned:bool:22 timing_valid:bool:23 started_us:u32:24 completed_us:u32:28'),
    'motor_fault::TraceReport': (2128, 'calls:Call[64]:0 count:u32:2048 rejected:u32:2052 clock_reads:u32:2056 overflow:bool:2060 timing_fault:bool:2061 has_failure:bool:2062 has_current:bool:2063 current:Call:2064 first_failure:Call:2096'),
    'motors::HaltResult': (16, 'fresh:bool:0 attempted:bool:1 inhibition_confirmed:bool:2 timing_valid:bool:3 started_us:u32:4 completed_us:u32:8 fault:u8:12'),
    'motors::MotorGate': (88, 'fault_:u8:44 initialized_:bool:45 began_:bool:46 armed_:bool:47 hold_complete_:bool:48 release_us_:u32:52 last_token_:u64:56 halted_:bool:64 halt_result_:HaltResult:68'),
    'motors::Result': (56, 'feedback:PreviousTick:0 fault:u8:48 consumed:bool:49'),
    'motors::SettleProbeReport': (28, 'current:SettleProbeSample:0 first_failure:SettleProbeSample:12 has_current:u8:24 has_failure:u8:25 reserved:u8[2]:26'),
    'motors::SettleProbeSample': (12, 'elapsed_us:u32:0 poll_index:u32:4 reason:u8:8 fresh_mask:u8:9 valid:u8:10 reserved:u8:11'),
}
ALIASES = dict(Call='motor_fault::Call', CountdownResult='countdown::Result',
               HaltResult='motors::HaltResult', LifecycleResult='countdown::LifecycleResult',
               Outputs='core::Outputs', PreviousTick='fsm::PreviousTick',
               Result='motors::Result', RobotResult='fsm::RobotResult',
               RuntimeReport='app::RuntimeReport', SettleProbeSample='motors::SettleProbeSample',
               Snapshot='app_motor_observe::Snapshot', TransactionReport='app::TransactionReport')
FORMATS = dict(u8='B', u16='H', u32='I', u64='Q', f32='f', bool='B')
REASONS = ('NONE', 'SUCCESS', 'NULL_CONTEXT', 'PRECONDITION', 'INITIAL_BANK',
           'POLL_DEADLINE', 'POLL_BANK', 'FINAL_DEADLINE', 'POLL_LIMIT')


def sha(body):
    return hashlib.sha256(body).hexdigest()


def json_bytes(value):
    return json.dumps(value, ensure_ascii=False, separators=(',', ':'), allow_nan=False).encode()


def field_specs(kind):
    return [(name, child, int(offset)) for name, child, offset in
            (token.split(':') for token in DECLARATIONS[kind][1].split())]


def specimen(kind):
    """Write independent, distinguishable little-endian leaves and expected tree."""
    body = bytearray([0xA5] * DECLARATIONS[kind][0])
    leaves = []
    counter = [0]

    def write(selected, offset, path):
        if selected in FORMATS:
            counter[0] += 1
            n = counter[0]
            values = dict(u8=(n * 29) % 256, u16=0x8100 + n,
                          u32=0xA1000000 + n, u64=0xF102030405060000 + n,
                          f32=-n / 8, bool=n % 2)
            value = values[selected]
            struct.pack_into('<' + FORMATS[selected], body, offset, value)
            leaves.append((path, offset, selected))
            return bool(value) if selected == 'bool' else value
        if selected == 'Call[64]':
            return [write('motor_fault::Call', offset + 32 * i, path + '/' + str(i))
                    for i in range(64)]
        if selected == 'u8[2]':
            return [write('u8', offset + i, path + '/' + str(i)) for i in range(2)]
        full = ALIASES.get(selected, selected)
        return {name: write(child, offset + delta, path + '/' + name)
                for name, child, delta in field_specs(full)}

    expected = write(kind, 0, '')
    return bytes(body), expected, leaves


def sample(reason=0, elapsed=0, poll=0, fresh=0, valid=0, reserved=0):
    return dict(elapsed_us=elapsed, poll_index=poll, reason=reason,
                fresh_mask=fresh, valid=valid, reserved=reserved)


def report(current=None, first_failure=None, has_current=0, has_failure=0, reserved=None):
    return dict(current=sample() if current is None else current,
                first_failure=sample() if first_failure is None else first_failure,
                has_current=has_current, has_failure=has_failure,
                reserved=[0, 0] if reserved is None else reserved)


def settle_bytes(value):
    out = bytearray()
    for key in ('current', 'first_failure'):
        item = value[key]
        out.extend(struct.pack('<IIBBBB', item['elapsed_us'], item['poll_index'],
                               item['reason'], item['fresh_mask'], item['valid'], item['reserved']))
    return bytes(out) + bytes([value['has_current'], value['has_failure'], *value['reserved']])


def source_consistent(reason):
    return {
        1: sample(1, 149, 4095, 7, 7), 2: sample(2), 3: sample(3), 4: sample(4),
        5: sample(5, 150, 4095, 6, 7), 6: sample(6, 149, 0, 7, 7),
        7: sample(7, 151, 4095, 7, 7), 8: sample(8, 149, 4095, 6, 7),
    }[reason]


def plan():
    rows = []
    for phase, kind, base, widths in (
            ('before', 'loader', 0x08000000, [65536] * 4 + [1536]),
            ('before', 'sketch', 0x08100000, [65536, 29832])):
        rows.extend((phase + '.' + kind + '.' + str(i), base + i * 65536, size)
                    for i, size in enumerate(widths))
    for phase in ('first', 'second'):
        rows.extend((phase + '.' + name, address, size) for name, address, size, _ in WINDOWS)
    for kind, base, widths in (('sketch', 0x08100000, [65536, 29832]),
                               ('loader', 0x08000000, [65536] * 4 + [1536])):
        rows.extend(('after.' + kind + '.' + str(i), base + i * 65536, size)
                    for i, size in enumerate(widths))
    return rows


PLAN = plan()


def file_row(path, body):
    return dict(path=path, bytes=len(body), sha256=sha(body),
                data_base64=base64.b64encode(body).decode('ascii'))


def fixture(reads=26, commands=None, failed=False):
    """Independent synthetic receipts; flash hashes declare equality, not bytes."""
    commands = reads if commands is None else commands
    upload = dict(attempts=1, finished_monotonic=2.0, finished_utc='saved-upload-end',
                  first_error=None, postcheck_errors=[], run_id=RUN,
                  schema='app-motor-const-upload-result-v1', source_sha256=SOURCE_SHA,
                  started_monotonic=1, started_utc='saved-upload-start', status='UPLOADED',
                  stderr='diagnostic text retained', stdout='arbitrary stdout retained',
                  subprocess=dict(reaped=True, returncode=0, timed_out=False))
    bodies = {}
    expected = {}
    records = []
    for index, (name, address, size) in enumerate(PLAN[:reads]):
        filename = f'{index:02d}-{name}.bin'
        digest = sha(name.split('.', 1)[1].encode())
        if 7 <= index <= 18:
            kind = WINDOWS[(index - 7) % 6][3]
            body, fields, _ = specimen(kind)
            if name.endswith('.settle'):
                fields = report(source_consistent(1), source_consistent(5), 1, 1)
                body = settle_bytes(fields)
            bodies[filename] = body
            expected[name] = fields
            digest = sha(body)
        records.append(dict(name=name, address=address, bytes=size, sha256=digest, file=filename))
    capture = dict(
        analysis=dict(coherence='UNPROVEN', schema='app-motor-const-capture-analysis-v1',
                      flash={name: reads > boundary for name, boundary in
                             [('before_loader', 4), ('before_sketch', 6),
                              ('after_sketch', 20), ('after_loader', 25)]},
                      pre_sample_wait=None if reads < 7 else
                      dict(requested_seconds=30, before=20, after=50),
                      snapshots=copy.deepcopy(records[7:min(reads, 19)])),
        counts=dict(commands=commands, reads=reads,
                    requested_bytes=sum(item[2] for item in PLAN[:commands])),
        finished_monotonic=100, finished_utc='saved-capture-end',
        first_error=dict(type='SyntheticFailure', message='original failure') if failed else None,
        postcheck_errors=[], reads=records, run_id=RUN,
        schema='app-motor-const-capture-result-v1', source_sha256=SOURCE_SHA,
        started_monotonic=10, started_utc='saved-capture-start',
        status='FAILED' if failed else 'COLLECTED',
        wait=None if reads < 13 else dict(requested_seconds=2, before=60, after=62))
    return upload, capture, bodies, expected


def packet_from(upload, capture, bodies):
    rows = [file_row(UPLOAD, json_bytes(upload)), file_row(CAPTURE, json_bytes(capture))]
    rows.extend(file_row(CAPTURE_DIR + '/' + filename, body) for filename, body in bodies.items())
    return dict(status='FILE_ONLY_RESULTS_VERIFIED', identity_before=copy.deepcopy(IDENTITY),
                identity_after=copy.deepcopy(IDENTITY), files=rows, closing_file_checks=len(rows))


@contextlib.contextmanager
def forbid_io():
    with contextlib.ExitStack() as stack:
        for owner, name in [(Path, 'open'), (Path, 'read_bytes'), (Path, 'write_bytes'),
                            (os, 'open'), (subprocess, 'run'), (subprocess, 'Popen'),
                            (time, 'sleep')]:
            stack.enter_context(mock.patch.object(owner, name, side_effect=AssertionError('pure seam I/O')))
        stack.enter_context(mock.patch('builtins.open', side_effect=AssertionError('pure seam open')))
        yield


class OracleBase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # The author never executes this loader until the root records freeze01.
        cls.map_raw = (REPO / MAP_REL).read_bytes()
        cls.subject_source = (REPO / SUBJECT_REL).read_bytes()
        cls.subject_code = compile(cls.subject_source, str(SUBJECT_REL), 'exec')
        cls.subject = cls.load_subject(REPO)

    @classmethod
    def load_subject(cls, root):
        module = types.ModuleType('independent_settle_decoder')
        module.__file__ = str(root / SUBJECT_REL)
        with forbid_io():
            exec(cls.subject_code, module.__dict__)
        return module

    def decode(self, kind, body):
        return self.subject.decode(kind, body, field_map_raw=self.map_raw)

    def interpret(self, packet):
        raw = packet if type(packet) is bytes else json_bytes(packet)
        return self.subject.interpret(raw, field_map_raw=self.map_raw)

    def accepted(self, spec=None, status='DECODED'):
        upload, capture, bodies, expected = fixture() if spec is None else spec
        packet = packet_from(upload, capture, bodies)
        result = self.interpret(packet)
        self.assertEqual(result['status'], status)
        self.assertIsNone(result['decode_first_error'])
        self.assertEqual(set(result), RESULT_KEYS)
        self.assertEqual(result['schema'], 'motor-const-observed-fields-v1')
        self.assertEqual(result['coherence'], 'UNPROVEN')
        self.assertEqual(result['retrieval_sha256'], sha(json_bytes(packet)))
        self.assertEqual(result['field_map_sha256'], MAP_SHA)
        self.assertEqual(result['upload_result'], upload)
        self.assertEqual(result['capture_result'], capture)
        self.assertEqual(result['windows'], expected)
        self.assertEqual(set(result['repeated_fields_equal']), {w[0] for w in WINDOWS})
        return result

    def rejected(self, packet, stage, code, path=None):
        result = self.interpret(packet)
        self.assertEqual(result['status'], 'REJECTED')
        self.assertEqual(set(result), RESULT_KEYS)
        error = result['decode_first_error']
        self.assertEqual(set(error), {'stage', 'code', 'path'})
        self.assertEqual((error['stage'], error['code']), (stage, code))
        self.assertIs(type(error['path']), str)
        self.assertTrue(error['path'].startswith('/'))
        if path is not None:
            self.assertEqual(error['path'], path)
        self.assertEqual(result['coherence'], 'UNPROVEN')
        return result

    def exception(self, error_class, arguments, call):
        with self.assertRaises(error_class) as caught:
            call()
        self.assertEqual(caught.exception.args, arguments)

    def issues(self, raw, expected, status='INCONCLUSIVE'):
        actual = self.subject.annotate_settle(raw)
        self.assertEqual(actual['raw'], raw)
        self.assertEqual(actual['issues'], [dict(code=code, path=path) for code, path in expected])
        self.assertEqual(actual['status'], status)
        return actual


class ProvenanceAndDecode(OracleBase):
    def test_contract_and_observed_map_pins(self):
        self.assertEqual(sha((REPO / CONTRACT_REL).read_bytes()), CONTRACT_SHA)
        self.assertEqual(len(self.map_raw), 16755)
        self.assertEqual(sha(self.map_raw), MAP_SHA)
        layout = json.loads(self.map_raw)
        self.assertEqual((layout['selected_types'], layout['selected_fields']), (16, 115))
        self.assertEqual(sum(len(field_specs(kind)) for kind in DECLARATIONS), 115)
        for kind, (width, _) in DECLARATIONS.items():
            self.assertEqual(layout['types'][kind], dict(bytes=width, fields={
                name: dict(kind=child, offset=offset) for name, child, offset in field_specs(kind)}))

    def test_enum_layout_and_validity_provenance_are_separate(self):
        layout = json.loads(self.map_raw)
        abi = json.loads((REPO / 'state/analysis/P7_motor_const_compile_raw/native_abi_static01/abi.json').read_bytes())
        values = dict(zip(REASONS, range(9)))
        self.assertEqual(layout['enums']['motors::SettleProbeReason']['values'], values)
        self.assertEqual(abi['settle_probe']['reasons'], values)
        self.assertEqual(abi['settle_probe']['address'], 537121768)
        validity = layout['source_semantics']['validity']
        self.assertIn('Pinned source only', validity['provenance'])
        self.assertIn('not queried', validity['provenance'])
        self.assertEqual([validity[x] for x in ('elapsed_bit', 'poll_bit', 'fresh_bit', 'allowed_mask')], [1, 2, 4, 7])
        source = (REPO / validity['source']).read_bytes()
        self.assertEqual(sha(source), validity['source_sha256'])
        for kind in ('motors::SettleProbeSample', 'motors::SettleProbeReport'):
            for name, _, offset in field_specs(kind):
                self.assertEqual(abi['settle_probe']['fields'][kind + '.' + name]['offset'], offset)

    def test_all_sixteen_structs_all_selected_fields_and_aliases(self):
        for kind in DECLARATIONS:
            with self.subTest(kind=kind):
                body, expected, _ = specimen(kind)
                with forbid_io():
                    actual = self.decode(kind, body)
                self.assertEqual(actual, expected)

    def test_trace_retains_64_slots_and_loss_fields_without_completion_claim(self):
        body, expected, _ = specimen('motor_fault::TraceReport')
        amended = bytearray(body)
        struct.pack_into('<III', amended, 2048, 2, 0xFFFFFFFF, 0xFEDCBA98)
        actual = self.decode('motor_fault::TraceReport', bytes(amended))
        self.assertEqual(len(actual['calls']), 64)
        self.assertEqual(actual['calls'][63], expected['calls'][63])
        self.assertEqual((actual['count'], actual['rejected'], actual['clock_reads']), (2, 0xFFFFFFFF, 0xFEDCBA98))
        self.assertEqual(set(actual), set(expected))

    def test_preabort_previous_is_nested_at_1120_not_old_live_address(self):
        body = bytearray(1168)
        struct.pack_into('<Q', body, 1128, 0xFFFFFFFFFFFFFFFF)
        struct.pack_into('<I', body, 1136, 0xF1E2D3C4)
        actual = self.decode('app_motor_observe::Report', bytes(body))
        self.assertEqual(actual['before_abort']['previous']['token'], 0xFFFFFFFFFFFFFFFF)
        self.assertEqual(actual['before_abort']['previous']['applied_us'], 0xF1E2D3C4)
        self.assertNotIn('previous', actual)

    def test_unsigned_little_endian_and_finite_negative_zero(self):
        body = struct.pack('<IIBBBB', 0xFFFFFFFF, 0xF1E2D3C4, 255, 254, 253, 252)
        self.assertEqual(self.decode('motors::SettleProbeSample', body), sample(255, 0xFFFFFFFF, 0xF1E2D3C4, 254, 253, 252))
        out = self.decode('core::Outputs', struct.pack('<ffBBxx', -0.0, 3.4028234663852886e38, 1, 255))
        self.assertEqual(math.copysign(1, out['duty_l']), -1)
        self.assertEqual(out['duty_r'], 3.4028234663852886e38)
        self.assertIs(out['motors_enabled'], True)
        robot = bytearray(400)
        struct.pack_into('<Q', robot, 0, 0xFFFFFFFFFFFFFFFF)
        struct.pack_into('<H', robot, 88, 65535)
        value = self.decode('fsm::RobotResult', bytes(robot))
        self.assertEqual((value['token'], value['contract_faults']), (0xFFFFFFFFFFFFFFFF, 65535))

    def test_public_short_aliases_scalars_and_unknown_types_are_rejected(self):
        for kind in list(ALIASES) + ['u8', 'Call[64]', '', 'motors::NoSuchType']:
            with self.subTest(kind=kind):
                self.exception(ValueError, ('window', 'UNKNOWN_TYPE', '/kind'), lambda: self.decode(kind, b''))

    def test_exact_body_width_for_every_struct(self):
        for kind, (width, _) in DECLARATIONS.items():
            for length in (0, width - 1, width + 1):
                with self.subTest(kind=kind, length=length):
                    self.exception(ValueError, ('window', 'BODY_SIZE', '/'), lambda: self.decode(kind, bytes(length)))

    def test_exact_python_types_and_argument_check_order(self):
        class BytesSubclass(bytes):
            pass
        class StrSubclass(str):
            pass
        for kind in (None, True, 3, StrSubclass('core::Outputs')):
            self.exception(TypeError, ('window', 'ARG_TYPE', '/kind'), lambda: self.subject.decode(kind, None, field_map_raw=None))
        for body in (None, bytearray(12), memoryview(bytes(12)), BytesSubclass(bytes(12))):
            self.exception(TypeError, ('window', 'ARG_TYPE', '/body'), lambda: self.subject.decode('core::Outputs', body, field_map_raw=None))
        self.exception(TypeError, ('layout', 'ARG_TYPE', '/'), lambda: self.subject.decode('core::Outputs', bytes(12), field_map_raw=bytearray(self.map_raw)))
        self.exception(TypeError, ('packet', 'ARG_TYPE', '/'), lambda: self.subject.interpret(bytearray(), field_map_raw=None))
        self.exception(TypeError, ('layout', 'ARG_TYPE', '/'), lambda: self.subject.interpret(b'{}', field_map_raw=None))

    def test_map_bound_exact_length_pin_before_packet_or_window(self):
        for raw, code in [(b'', 'MAP_SIZE'), (self.map_raw + b' ', 'MAP_SIZE'), (bytes(65537), 'MAP_SIZE'),
                          (bytes(len(self.map_raw)), 'MAP_HASH')]:
            with self.subTest(code=code, size=len(raw)):
                self.exception(ValueError, ('layout', code, '/'), lambda: self.subject.decode('missing', b'', field_map_raw=raw))
                result = self.subject.interpret(b'invalid JSON', field_map_raw=raw)
                self.assertEqual(result['decode_first_error'], dict(stage='layout', code=code, path='/'))
                self.assertEqual(result['status'], 'REJECTED')

    def test_every_bool_leaf_refuses_nonbinary_bytes_and_preserves_field_path(self):
        for kind in DECLARATIONS:
            body, _, leaves = specimen(kind)
            for path, offset, scalar in leaves:
                if scalar != 'bool':
                    continue
                with self.subTest(kind=kind, path=path):
                    changed = bytearray(body)
                    changed[offset] = 2
                    self.exception(ValueError, ('window', 'INVALID_BOOL', path), lambda: self.decode(kind, bytes(changed)))

    def test_nonfinite_f32_all_encodings_and_first_offset_order(self):
        for bits in (0x7F800000, 0xFF800000, 0x7FC00000, 0x7FA00001):
            body = bytearray(12)
            struct.pack_into('<I', body, 0, bits)
            body[8] = 2
            self.exception(ValueError, ('window', 'NONFINITE_F32', '/duty_l'), lambda: self.decode('core::Outputs', bytes(body)))
        body = bytearray(48)
        body[0] = 2
        struct.pack_into('<I', body, 24, 0x7F800000)
        self.exception(ValueError, ('window', 'INVALID_BOOL', '/applied_valid'), lambda: self.decode('fsm::PreviousTick', bytes(body)))

    def test_decode_returns_fresh_nested_containers(self):
        body, expected, _ = specimen('motor_fault::TraceReport')
        first = self.decode('motor_fault::TraceReport', body)
        second = self.decode('motor_fault::TraceReport', body)
        first['calls'][0]['stage'] = -1
        first['current']['stage'] = -2
        self.assertEqual(second, expected)
        self.assertEqual(self.decode('motor_fault::TraceReport', body), expected)


class AnnotationOracle(OracleBase):
    def test_all_eight_completed_reasons_have_explicit_numeric_labels(self):
        for reason in range(1, 9):
            with self.subTest(reason=reason):
                current = source_consistent(reason)
                raw = report(current, current if reason > 1 else None, 1, int(reason > 1))
                result = self.issues(raw, [], 'CONSISTENT')
                self.assertEqual(set(result), {'raw', 'current', 'first_failure', 'issues', 'status'})
                ann = result['current']
                self.assertEqual(set(ann), {'presence', 'reason_label', 'available', 'status'})
                self.assertEqual(ann['presence'], 'PRESENT')
                self.assertEqual(ann['reason_label'], REASONS[reason])
                self.assertEqual(ann['status'], 'CONSISTENT')
                expected = reason not in (2, 3, 4)
                self.assertEqual(ann['available'], dict(elapsed_us=expected, poll_index=expected, fresh_mask=expected))

    def test_none_before_publication_is_unavailable(self):
        result = self.issues(report(), [], 'UNAVAILABLE')
        for key in ('current', 'first_failure'):
            self.assertEqual(result[key], dict(presence='ABSENT', reason_label='NONE',
                                              available=dict(elapsed_us=False, poll_index=False, fresh_mask=False),
                                              status='UNAVAILABLE'))

    def test_absent_nonzero_payload_is_not_a_completed_branch(self):
        arbitrary = sample(255, 0xFFFFFFFF, 0xFFFFFFFF, 255, 255, 255)
        result = self.issues(report(arbitrary, copy.deepcopy(arbitrary)), [], 'UNAVAILABLE')
        self.assertIsNone(result['current']['reason_label'])
        self.assertEqual(result['current']['status'], 'UNAVAILABLE')
        self.assertEqual(result['current']['available'], dict(elapsed_us=False, poll_index=False, fresh_mask=False))

    def test_invalid_presence_cannot_gain_availability_from_valid_bits(self):
        raw = report(sample(1, 0, 0, 7, 7, 255), sample(5, 150, 0, 0, 7, 255), 2, 255)
        result = self.issues(raw, [('NON_BINARY_PRESENCE', '/has_current'), ('NON_BINARY_PRESENCE', '/has_failure')])
        for key in ('current', 'first_failure'):
            self.assertEqual(result[key]['presence'], 'UNKNOWN')
            self.assertEqual(result[key]['available'], dict(elapsed_us=None, poll_index=None, fresh_mask=None))
            self.assertEqual(result[key]['status'], 'INCONCLUSIVE')

    def test_elapsed_149_150_151_thresholds_and_wrapped_uint32(self):
        for reason, base in [(1, sample(1, 0, 1, 7, 7)), (5, sample(5, 0, 1, 6, 7)),
                             (6, sample(6, 0, 1, 7, 7)), (7, sample(7, 0, 1, 7, 7)),
                             (8, sample(8, 0, 4095, 6, 7))]:
            for elapsed in (149, 150, 151, 0xFFFFFFFF):
                with self.subTest(reason=reason, elapsed=elapsed):
                    current = dict(base, elapsed_us=elapsed)
                    valid = elapsed >= 150 if reason in (5, 7) else elapsed < 150
                    raw = report(current, source_consistent(2), 1, 1)
                    errors = [] if valid else [('ELAPSED_CONDITION', '/current/elapsed_us')]
                    self.issues(raw, errors, 'CONSISTENT' if valid else 'INCONCLUSIVE')

    def test_poll_4095_4096_and_poll_limit_exactness(self):
        for reason in (1, 5, 6, 7, 8):
            for poll in (0, 4094, 4095, 4096, 0xFFFFFFFF):
                with self.subTest(reason=reason, poll=poll):
                    current = dict(source_consistent(reason), poll_index=poll)
                    if reason == 5 and poll == 0:
                        current['fresh_mask'] = 0
                    valid = poll == 4095 if reason == 8 else poll <= 4095
                    errors = [] if valid else [('POLL_CONDITION', '/current/poll_index')]
                    self.issues(report(current, source_consistent(2), 1, 1), errors,
                                'CONSISTENT' if valid else 'INCONCLUSIVE')

    def test_fresh_branch_conditions_and_first_poll_deadline(self):
        cases = [(1, 6, 'FRESH_CONDITION'), (1, 7, None), (5, 7, 'FRESH_CONDITION'),
                 (5, 6, None), (6, 7, None), (7, 6, 'FRESH_CONDITION'),
                 (8, 7, 'FRESH_CONDITION'), (8, 6, None)]
        for reason, fresh, issue in cases:
            current = dict(source_consistent(reason), fresh_mask=fresh)
            errors = [] if issue is None else [(issue, '/current/fresh_mask')]
            self.issues(report(current, source_consistent(2), 1, 1), errors,
                        'CONSISTENT' if issue is None else 'INCONCLUSIVE')
        for fresh in (0, 1, 6):
            errors = [] if fresh == 0 else [('FRESH_CONDITION', '/current/fresh_mask')]
            self.issues(report(sample(5, 150, 0, fresh, 7), source_consistent(2), 1, 1), errors,
                        'CONSISTENT' if fresh == 0 else 'INCONCLUSIVE')

    def test_valid_bits_control_checks_and_zero_is_not_availability(self):
        # Out-of-branch numeric values with bits clear remain raw, not measurements.
        current = sample(1, 0xFFFFFFFF, 0xFFFFFFFF, 6, 0)
        result = self.issues(report(current, None, 1, 0), [('VALID_MASK_MISMATCH', '/current/valid')])
        self.assertEqual(result['current']['available'], dict(elapsed_us=False, poll_index=False, fresh_mask=False))
        result = self.issues(report(sample(1, 0, 0, 7, 7), None, 1, 0), [], 'CONSISTENT')
        self.assertEqual(result['current']['available'], dict(elapsed_us=True, poll_index=True, fresh_mask=True))
        for mask, availability in [(1, (True, False, False)), (2, (False, True, False)), (4, (False, False, True))]:
            result = self.issues(report(sample(1, 0, 0, 7, mask), None, 1, 0), [('VALID_MASK_MISMATCH', '/current/valid')])
            self.assertEqual(result['current']['available'], dict(zip(('elapsed_us', 'poll_index', 'fresh_mask'), availability)))

    def test_early_literals_and_measured_validity_are_separate(self):
        for reason in (2, 3, 4):
            raw = report(sample(reason, 1, 2, 3, 7), source_consistent(2), 1, 1)
            self.issues(raw, [('VALID_MASK_MISMATCH', '/current/valid'),
                              ('EARLY_NONZERO', '/current/elapsed_us'),
                              ('EARLY_NONZERO', '/current/poll_index'),
                              ('EARLY_NONZERO', '/current/fresh_mask')])

    def test_first_poll_fresh_constraint_requires_both_relevant_valid_bits(self):
        for mask in (1, 2, 4, 5, 6, 7):
            expected = [] if mask == 7 else [('VALID_MASK_MISMATCH', '/current/valid')]
            if mask in (6, 7):
                expected.append(('FRESH_CONDITION', '/current/fresh_mask'))
            self.issues(report(sample(5, 150, 0, 6, mask), source_consistent(2), 1, 1), expected)

    def test_unknown_bytes_and_present_none_preserve_numeric_values(self):
        raw = report(sample(255, 0xFFFFFFFF, 0xFFFFFFFF, 0xF7, 0x87, 9), None, 1, 0)
        result = self.issues(raw, [('NONZERO_RESERVED', '/current/reserved'),
                                  ('UNKNOWN_VALID_BITS', '/current/valid'),
                                  ('UNKNOWN_FRESH_BITS', '/current/fresh_mask'),
                                  ('UNKNOWN_REASON', '/current/reason')])
        self.assertIsNone(result['current']['reason_label'])
        self.assertEqual(result['raw']['current']['valid'], 0x87)
        self.issues(report(sample(0, 400, 9000, 7, 7), None, 1, 0), [('PRESENT_NONE', '/current/reason')])

    def test_global_and_sample_issue_order_is_fixed(self):
        raw = report(sample(1, 150, 4096, 255, 255, 1),
                     sample(0, 999, 999, 255, 255, 2), 1, 1, [3, 4])
        self.issues(raw, [('NONZERO_RESERVED', '/reserved/0'), ('NONZERO_RESERVED', '/reserved/1'),
                          ('NONZERO_RESERVED', '/current/reserved'), ('UNKNOWN_VALID_BITS', '/current/valid'),
                          ('UNKNOWN_FRESH_BITS', '/current/fresh_mask'), ('VALID_MASK_MISMATCH', '/current/valid'),
                          ('ELAPSED_CONDITION', '/current/elapsed_us'), ('POLL_CONDITION', '/current/poll_index'),
                          ('FRESH_CONDITION', '/current/fresh_mask'), ('NONZERO_RESERVED', '/first_failure/reserved'),
                          ('UNKNOWN_VALID_BITS', '/first_failure/valid'), ('UNKNOWN_FRESH_BITS', '/first_failure/fresh_mask'),
                          ('PRESENT_NONE', '/first_failure/reason'), ('FIRST_FAILURE_NOT_FAILURE', '/first_failure/reason')])

    def test_first_failure_lifetime_is_independent_of_later_current_success(self):
        raw = report(source_consistent(1), source_consistent(5), 1, 1)
        result = self.issues(raw, [], 'CONSISTENT')
        self.assertEqual(result['first_failure']['reason_label'], 'POLL_DEADLINE')
        self.assertEqual(result['current']['reason_label'], 'SUCCESS')
        for reason in (0, 1):
            failure = sample() if reason == 0 else source_consistent(1)
            expected = [('PRESENT_NONE', '/first_failure/reason')] if reason == 0 else []
            expected.append(('FIRST_FAILURE_NOT_FAILURE', '/first_failure/reason'))
            self.issues(report(source_consistent(1), failure, 1, 1), expected)

    def test_flag_relationship_issues_never_reclassify_absent_sample(self):
        result = self.issues(report(None, source_consistent(2), 0, 1), [('FLAG_RELATION', '/has_current')])
        self.assertEqual(result['current']['status'], 'UNAVAILABLE')
        self.assertEqual(result['first_failure']['status'], 'CONSISTENT')
        result = self.issues(report(source_consistent(2), None, 1, 0), [('FLAG_RELATION', '/has_failure')])
        self.assertEqual(result['current']['status'], 'CONSISTENT')
        self.assertEqual(result['first_failure']['status'], 'UNAVAILABLE')

    def test_report_reserved_issues_preserve_unavailable_samples(self):
        result = self.issues(report(reserved=[1, 2]), [('NONZERO_RESERVED', '/reserved/0'), ('NONZERO_RESERVED', '/reserved/1')])
        self.assertEqual(result['current']['status'], 'UNAVAILABLE')
        self.assertEqual(result['first_failure']['status'], 'UNAVAILABLE')

    def test_annotation_input_shapes_ranges_and_no_mutation(self):
        values = [(None, TypeError, 'ARG_TYPE'), ([], TypeError, 'ARG_TYPE'),
                  (dict(report(), extra=0), ValueError, 'SHAPE'),
                  (dict(report(), reserved=[0]), ValueError, 'SHAPE'),
                  (dict(report(), has_current=256), ValueError, 'SHAPE'),
                  (dict(report(), has_current=True), TypeError, 'ARG_TYPE'),
                  (dict(report(), current=dict(sample(), elapsed_us=-1)), ValueError, 'SHAPE'),
                  (dict(report(), current=dict(sample(), elapsed_us=1.0)), TypeError, 'ARG_TYPE')]
        for value, error, code in values:
            with self.subTest(value=value):
                with self.assertRaises(error) as caught:
                    self.subject.annotate_settle(value)
                self.assertEqual(caught.exception.args[:2], ('annotation', code))
                self.assertEqual(len(caught.exception.args), 3)
        original = report(source_consistent(1), source_consistent(2), 1, 1)
        frozen = copy.deepcopy(original)
        with forbid_io():
            first = self.subject.annotate_settle(original)
            second = self.subject.annotate_settle(original)
        first['raw']['current']['reason'] = 255
        first['current']['available']['elapsed_us'] = False
        self.assertEqual(original, frozen)
        self.assertEqual(second['raw'], frozen)
        self.assertIs(second['current']['available']['elapsed_us'], True)


class PacketOracle(OracleBase):
    def test_complete_packet_preserves_fields_receipts_and_unproven_coherence(self):
        result = self.accepted()
        self.assertEqual(len(result['verified_files']), 14)
        self.assertEqual(result['repeated_fields_equal'], {name: True for name, *_ in WINDOWS})
        self.assertEqual(set(result['settle_annotations']), {'first.settle', 'second.settle'})
        self.assertTrue(all(item['status'] == 'CONSISTENT' for item in result['settle_annotations'].values()))

    def test_all_53_allowed_prefix_count_pairs_are_partial_not_complete(self):
        count = 0
        for reads in range(27):
            for commands in (reads, reads + 1):
                if commands > 26:
                    continue
                with self.subTest(reads=reads, commands=commands):
                    spec = fixture(reads, commands, failed=True)
                    result = self.accepted(spec, 'PARTIAL')
                    expected_snapshots = max(0, min(reads, 19) - 7)
                    self.assertEqual(len(result['windows']), expected_snapshots)
                    self.assertEqual(len(result['verified_files']), 2 + expected_snapshots)
                    for index, (name, *_) in enumerate(WINDOWS):
                        self.assertEqual(result['repeated_fields_equal'][name], True if reads > 13 + index else None)
                    count += 1
        self.assertEqual(count, 53)

    def test_packet_json_is_strict_utf8_duplicate_finite_and_bounded(self):
        bodies = [b'\xff', b'{', b'{} trailing', b'{"status":0,"status":1}',
                  b'{"x":NaN}', b'{"x":Infinity}', b'{"x":-Infinity}', b'{"x":1e999}']
        for raw in bodies:
            with self.subTest(raw=raw[:30]):
                self.rejected(raw, 'packet', 'JSON', '/')
        deep_raw = b'[' * 2000 + b'0' + b']' * 2000
        try:
            json.loads(deep_raw)
        except RecursionError:
            expected_code = 'JSON'
        else:
            expected_code = 'KEYS'
        self.rejected(deep_raw, 'packet', expected_code, '/')
        self.rejected(bytes(1048577), 'packet', 'PACKET_SIZE', '/')
        for raw in (b'null', b'[]', b'3', b'"x"'):
            self.rejected(raw, 'packet', 'KEYS', '/')

    def test_packet_parser_recursion_error_is_a_stable_json_rejection(self):
        packet_text = '{"oracle_recursion_probe":0}'
        packet_raw = packet_text.encode('ascii')
        original_loads = json.loads
        injections = []

        def controlled_loads(value, *args, **kwargs):
            if value == packet_text or value == packet_raw:
                injections.append('packet')
                raise RecursionError('controlled oracle packet parse failure')
            return original_loads(value, *args, **kwargs)

        with mock.patch.object(json, 'loads', side_effect=controlled_loads):
            self.rejected(packet_raw, 'packet', 'JSON', '/')
        self.assertEqual(injections, ['packet'])

    def test_whitespace_key_order_and_string_contents_are_preserved(self):
        upload, capture, bodies, _ = fixture()
        upload['stdout'] = '  untouched\n\t\u2603 "quoted"  '
        packet = packet_from(upload, capture, bodies)
        raw = json.dumps(dict(reversed(list(packet.items()))), ensure_ascii=False, indent=3).encode()
        result = self.interpret(raw)
        self.assertEqual(result['status'], 'DECODED')
        self.assertEqual(result['retrieval_sha256'], sha(raw))
        self.assertEqual(result['upload_result']['stdout'], upload['stdout'])

    def test_packet_keys_status_identity_file_and_closure_counts(self):
        base = packet_from(*fixture()[:3])
        cases = [(dict(base, extra=1), 'KEYS'), (dict(base, status='OTHER'), 'STATUS'),
                 (dict(base, identity_before=dict(IDENTITY, uid=True)), 'IDENTITY'),
                 (dict(base, identity_before=dict(IDENTITY, uid=1000.0)), 'IDENTITY'),
                 (dict(base, identity_after=dict(IDENTITY, python=[3.0, 13, 5])), 'IDENTITY'),
                 (dict(base, identity_after=dict(IDENTITY, python=[3, 13, True])), 'IDENTITY'),
                 (dict(base, identity_after=dict(IDENTITY, boot_id='other')), 'IDENTITY'),
                 (dict(base, files=base['files'][:1]), 'FILE_COUNT'),
                 (dict(base, closing_file_checks=True), 'CLOSURE_COUNT'),
                 (dict(base, closing_file_checks=13), 'CLOSURE_COUNT')]
        for packet, code in cases:
            with self.subTest(code=code):
                self.rejected(packet, 'packet', code)

    def test_exact_full_paths_same_basename_traversal_and_old_previous_rejected(self):
        bad_paths = [UPLOAD.replace('-upload/', '-capture/'), '/tmp/upload_result.json',
                     CAPTURE_DIR + '/../' + RUN + '-upload/upload_result.json',
                     CAPTURE_DIR + '/11-first.previous.bin', CAPTURE_DIR + '/00-before.loader.0.bin']
        for path in bad_paths:
            packet = packet_from(*fixture()[:3])
            packet['files'][0]['path'] = path
            self.rejected(packet, 'files', 'PATH', '/files/0/path')

    def test_duplicate_paths_identical_or_different_payload_never_overwrite(self):
        for alter in (False, True):
            packet = packet_from(*fixture(8, failed=True)[:3])
            duplicate = copy.deepcopy(packet['files'][0])
            if alter:
                duplicate['data_base64'] = 'AA=='
            packet['files'].append(duplicate)
            packet['closing_file_checks'] += 1
            result = self.rejected(packet, 'files', 'DUPLICATE_FILE', '/files/3/path')
            self.assertEqual(result['verified_files'], [])
            self.assertIsNone(result['upload_result'])

    def test_file_metadata_exact_keys_types_bounds_hash_syntax(self):
        cases = [('bytes', True), ('bytes', 0), ('bytes', -1), ('bytes', 1048577),
                 ('sha256', 'A' * 64), ('sha256', '0' * 63), ('path', 7), ('data_base64', [])]
        for field, value in cases:
            packet = packet_from(*fixture()[:3])
            packet['files'][0][field] = value
            self.rejected(packet, 'files', 'ROW_TYPE', '/files/0/' + field)
        packet = packet_from(*fixture()[:3])
        packet['files'][0]['extra'] = None
        self.rejected(packet, 'files', 'ROW_KEYS')

    def test_required_receipt_missing_is_identified_before_body_verification(self):
        for index, path in ((0, UPLOAD), (1, CAPTURE)):
            packet = packet_from(*fixture()[:3])
            del packet['files'][index]
            packet['closing_file_checks'] -= 1
            packet['files'][0]['data_base64'] = 'invalid'
            result = self.rejected(packet, 'files', 'MISSING_FILE', path)
            self.assertEqual(result['verified_files'], [])

    def test_base64_is_strict_canonical_and_length_hash_checks_follow(self):
        for encoded in ('!', 'AA', 'AB==', 'AA==\n', 'AAAA=', 'AA===='):
            packet = packet_from(*fixture()[:3])
            packet['files'][0]['data_base64'] = encoded
            self.rejected(packet, 'files', 'BASE64')
        for field, value, code in [('bytes', 1, 'FILE_SIZE'), ('sha256', '0' * 64, 'FILE_HASH')]:
            packet = packet_from(*fixture()[:3])
            packet['files'][0][field] = value
            self.rejected(packet, 'files', code, '/files/0/' + field)

    def test_receipt_json_strict_parsing_retains_prior_verified_reference(self):
        malformed = [b'{"status":0,"status":1}', b'{"x":NaN}', b'{"x":1e999}', b'\xff']
        for index, stage, path in ((0, 'upload', UPLOAD), (1, 'capture', CAPTURE)):
            for body in malformed:
                packet = packet_from(*fixture()[:3])
                packet['files'][index] = file_row(path, body)
                result = self.rejected(packet, stage, 'JSON')
                self.assertEqual(len(result['verified_files']), index + 1)
                self.assertEqual(result['windows'], {})
                if index == 1:
                    self.assertEqual(result['upload_result'], fixture()[0])

    def test_parsed_bad_receipt_is_retained_even_when_schema_rejects(self):
        for index, stage, path in ((0, 'upload', UPLOAD), (1, 'capture', CAPTURE)):
            packet = packet_from(*fixture()[:3])
            value = {'wrong': ['retained', 3]}
            packet['files'][index] = file_row(path, json_bytes(value))
            result = self.rejected(packet, stage, 'KEYS')
            self.assertEqual(result[stage + '_result'], value)
            self.assertEqual(len(result['verified_files']), 2)

    def test_receipt_top_and_nested_container_key_type_classification(self):
        for stage, field in [('upload', 'subprocess'), ('capture', 'analysis'), ('capture', 'counts')]:
            for value, code in [([], 'TYPE'), ({}, 'KEYS')]:
                upload, capture, bodies, _ = fixture()
                target = upload if stage == 'upload' else capture
                target[field] = value
                self.rejected(packet_from(upload, capture, bodies), stage, code, '/' + stage + '_result/' + field)
        for value, code in [([], 'TYPE'), ({}, 'KEYS')]:
            upload, capture, bodies, _ = fixture()
            capture['analysis']['flash'] = value
            self.rejected(packet_from(upload, capture, bodies), 'capture', code)

    def test_receipt_schema_run_source_and_upload_success_are_fixed(self):
        for stage in ('upload', 'capture'):
            for field in ('schema', 'run_id', 'source_sha256'):
                upload, capture, bodies, _ = fixture()
                (upload if stage == 'upload' else capture)[field] = 'stale'
                self.rejected(packet_from(upload, capture, bodies), stage, 'IDENTITY', '/' + stage + '_result/' + field)
        for field, value in [('attempts', 2), ('status', 'FAILED'), ('first_error', dict(type='Error', message='original')),
                             ('postcheck_errors', [dict(check='x', type='Error', message='original')])]:
            upload, capture, bodies, _ = fixture()
            upload[field] = value
            self.rejected(packet_from(upload, capture, bodies), 'upload', 'STATUS', '/upload_result/' + field)
        for field, value in [('reaped', False), ('returncode', 1), ('timed_out', True)]:
            upload, capture, bodies, _ = fixture()
            upload['subprocess'][field] = value
            self.rejected(packet_from(upload, capture, bodies), 'upload', 'STATUS', '/upload_result/subprocess/' + field)

    def test_receipt_exact_types_exclude_bool_as_integer(self):
        for field, value in [('attempts', True), ('stdout', []), ('stderr', None)]:
            upload, capture, bodies, _ = fixture()
            upload[field] = value
            self.rejected(packet_from(upload, capture, bodies), 'upload', 'TYPE', '/upload_result/' + field)
        for field, value in [('returncode', False), ('reaped', 1), ('timed_out', 0)]:
            upload, capture, bodies, _ = fixture()
            upload['subprocess'][field] = value
            self.rejected(packet_from(upload, capture, bodies), 'upload', 'TYPE', '/upload_result/subprocess/' + field)
        for field, value in [('address', True), ('bytes', True), ('name', 3), ('sha256', 0)]:
            upload, capture, bodies, _ = fixture()
            capture['reads'][0][field] = value
            self.rejected(packet_from(upload, capture, bodies), 'capture', 'TYPE')
        upload, capture, bodies, _ = fixture()
        capture['analysis']['flash']['before_loader'] = 1
        self.rejected(packet_from(upload, capture, bodies), 'capture', 'TYPE')

    def test_receipt_clocks_and_error_shapes_are_not_repaired(self):
        for stage in ('upload', 'capture'):
            for field, value, code in [('finished_monotonic', None, 'CLOCK'), ('started_monotonic', True, 'CLOCK'),
                                       ('finished_monotonic', -1, 'CLOCK'), ('finished_utc', '', 'CLOCK'),
                                       ('started_utc', None, 'CLOCK'), ('first_error', [], 'TYPE'),
                                       ('first_error', dict(type='', message='x'), 'ERROR_SHAPE'),
                                       ('postcheck_errors', {}, 'TYPE'), ('postcheck_errors', [None], 'ERROR_SHAPE')]:
                upload, capture, bodies, _ = fixture()
                (upload if stage == 'upload' else capture)[field] = value
                result = self.rejected(packet_from(upload, capture, bodies), stage, code)
                self.assertEqual(result[stage + '_result'][field], value)

    def test_counts_must_match_fixed_attempted_and_successful_prefixes(self):
        for field, value in [('commands', 27), ('commands', 24), ('reads', 27), ('reads', -1),
                             ('requested_bytes', 727431), ('reads', True), ('commands', False)]:
            upload, capture, bodies, _ = fixture()
            capture['counts'][field] = value
            self.rejected(packet_from(upload, capture, bodies), 'capture', 'COUNTS')
        upload, capture, bodies, _ = fixture(7, 9, True)
        self.rejected(packet_from(upload, capture, bodies), 'capture', 'COUNTS')

    def test_read_rows_fixed_order_addresses_extent_names_and_basenames(self):
        for field, value in [('address', 537115952), ('bytes', 48), ('name', 'first.previous'),
                             ('file', '11-first.previous.bin')]:
            upload, capture, bodies, _ = fixture()
            capture['reads'][11][field] = value
            capture['analysis']['snapshots'][4][field] = value
            self.rejected(packet_from(upload, capture, bodies), 'capture', 'READ_PLAN')
        for mode in ('reverse', 'duplicate', 'missing'):
            upload, capture, bodies, _ = fixture()
            if mode == 'reverse':
                capture['reads'][7:9] = reversed(capture['reads'][7:9])
            elif mode == 'duplicate':
                capture['reads'][8] = copy.deepcopy(capture['reads'][7])
            else:
                capture['reads'].pop()
            self.rejected(packet_from(upload, capture, bodies), 'capture', 'READ_PLAN')

    def test_snapshot_rows_are_exact_ordered_copies_not_digest_only(self):
        for mode in ('duplicate', 'reverse', 'address', 'hash'):
            upload, capture, bodies, _ = fixture()
            snapshots = capture['analysis']['snapshots']
            if mode == 'duplicate':
                snapshots[1] = copy.deepcopy(snapshots[0])
            elif mode == 'reverse':
                snapshots.reverse()
            elif mode == 'address':
                snapshots[0]['address'] += 1
            else:
                snapshots[0]['sha256'] = '0' * 64
            self.rejected(packet_from(upload, capture, bodies), 'capture', 'SNAPSHOTS')

    def test_declared_missing_body_differs_from_unread_tail(self):
        upload, capture, bodies, _ = fixture()
        del bodies['11-first.settle.bin']
        self.rejected(packet_from(upload, capture, bodies), 'files', 'MISSING_FILE', CAPTURE_DIR + '/11-first.settle.bin')
        self.accepted(fixture(11, failed=True), 'PARTIAL')
        upload, capture, bodies, _ = fixture(8, failed=True)
        bodies['11-first.settle.bin'] = bytes(28)
        self.rejected(packet_from(upload, capture, bodies), 'files', 'FILE_SET', CAPTURE_DIR + '/11-first.settle.bin')

    def test_wait_boundaries_accept_null_incomplete_and_failed_short_waits(self):
        for reads, key in [(7, 'pre_sample_wait'), (13, 'wait')]:
            for after in (None, 21, 50):
                spec = list(fixture(reads, failed=True))
                capture = spec[1]
                holder = capture['analysis'] if key == 'pre_sample_wait' else capture
                holder[key] = dict(requested_seconds=30 if reads == 7 else 2,
                                   before=20 if reads == 7 else 60,
                                   after=after if reads == 7 else (None if after is None else 60 + (after - 20)))
                self.accepted(tuple(spec), 'PARTIAL')
            spec = list(fixture(reads, failed=True))
            holder = spec[1]['analysis'] if key == 'pre_sample_wait' else spec[1]
            holder[key] = None
            self.accepted(tuple(spec), 'PARTIAL')

    def test_wait_shape_type_range_duration_and_chronology_errors(self):
        values = [[], {}, dict(requested_seconds=True, before=20, after=50),
                  dict(requested_seconds=30, before=True, after=50),
                  dict(requested_seconds=30, before=20, after=None),
                  dict(requested_seconds=30, before=20, after=49.999),
                  dict(requested_seconds=30, before=0, after=50),
                  dict(requested_seconds=30, before=80, after=110)]
        for value in values:
            upload, capture, bodies, _ = fixture()
            capture['analysis']['pre_sample_wait'] = value
            self.rejected(packet_from(upload, capture, bodies), 'capture', 'WAIT')
        upload, capture, bodies, _ = fixture()
        capture['wait']['before'], capture['wait']['after'] = 49, 51
        self.rejected(packet_from(upload, capture, bodies), 'capture', 'WAIT')
        upload, capture, bodies, _ = fixture(6, failed=True)
        capture['analysis']['pre_sample_wait'] = dict(requested_seconds=30, before=20, after=50)
        self.rejected(packet_from(upload, capture, bodies), 'capture', 'WAIT')

    def test_flash_comparison_boundaries_are_retained_and_enforced(self):
        for boundary, flag in [(4, 'before_loader'), (6, 'before_sketch'), (20, 'after_sketch'), (25, 'after_loader')]:
            spec = list(fixture(boundary + 1, failed=True))
            spec[1]['analysis']['flash'][flag] = False
            self.accepted(tuple(spec), 'PARTIAL')
            upload, capture, bodies, _ = fixture(boundary, failed=True)
            capture['analysis']['flash'][flag] = True
            self.rejected(packet_from(upload, capture, bodies), 'capture', 'FLASH')
            if boundary < 25:
                upload, capture, bodies, _ = fixture(boundary + 1, boundary + 2, True)
                capture['analysis']['flash'][flag] = False
                self.rejected(packet_from(upload, capture, bodies), 'capture', 'FLASH')

    def test_complete_status_never_upgrades_incomplete_or_failed_evidence(self):
        for reads in (0, 7, 19, 25):
            upload, capture, bodies, _ = fixture(reads)
            self.rejected(packet_from(upload, capture, bodies), 'capture', 'STATUS')
        for field, value in [('status', 'OTHER'), ('first_error', dict(type='Error', message='original')),
                             ('postcheck_errors', [dict(check='close', type='Error', message='original')]),
                             ('finished_monotonic', 610)]:
            upload, capture, bodies, _ = fixture()
            capture[field] = value
            self.rejected(packet_from(upload, capture, bodies), 'capture', 'STATUS')
        upload, capture, bodies, _ = fixture(26, failed=True)
        capture['first_error'] = None
        self.rejected(packet_from(upload, capture, bodies), 'capture', 'STATUS')

    def test_flash_hash_mismatch_complete_rejects_failed_preserves(self):
        for failed in (False, True):
            spec = list(fixture(26, failed=failed))
            spec[1]['reads'][19]['sha256'] = '0' * 64
            if failed:
                spec[1]['analysis']['flash']['after_loader'] = False
                spec[1]['finished_monotonic'] = 1000
                spec[1]['postcheck_errors'] = [dict(check='close', type='Error', message='second failure')]
                result = self.accepted(tuple(spec), 'PARTIAL')
                self.assertEqual(result['capture_result']['reads'][19]['sha256'], '0' * 64)
            else:
                self.rejected(packet_from(*spec[:3]), 'capture', 'STATUS', '/capture_result')

    def test_snapshot_body_linkage_and_short_trailing_bodies_reject(self):
        for body in (bytes(27), bytes(29), bytes(28)):
            upload, capture, bodies, _ = fixture()
            bodies['11-first.settle.bin'] = body
            field, code = ('sha256', 'FILE_HASH') if len(body) == 28 else ('bytes', 'FILE_SIZE')
            result = self.rejected(packet_from(upload, capture, bodies), 'files', code, '/files/6/' + field)
            self.assertEqual(result['windows'].keys(), {'first.trace', 'first.report', 'first.runtime', 'first.transaction'})

    def test_window_failure_retains_receipts_prior_windows_and_reference(self):
        upload, capture, bodies, _ = fixture()
        damaged = bytearray(bodies['09-first.runtime.bin'])
        damaged[2] = 2
        bodies['09-first.runtime.bin'] = bytes(damaged)
        capture['reads'][9]['sha256'] = sha(bytes(damaged))
        capture['analysis']['snapshots'][2]['sha256'] = sha(bytes(damaged))
        result = self.rejected(packet_from(upload, capture, bodies), 'window', 'INVALID_BOOL', '/windows/first.runtime/fresh')
        self.assertEqual(list(result['windows']), ['first.trace', 'first.report'])
        self.assertEqual(len(result['verified_files']), 5)
        self.assertEqual(result['capture_result'], capture)
        self.assertEqual(result['upload_result'], upload)
        self.assertTrue(all(value is None for value in result['repeated_fields_equal'].values()))

    def test_file_input_order_does_not_change_decode_order_or_early_error(self):
        packet = packet_from(*fixture()[:3])
        packet['files'].reverse()
        result = self.interpret(packet)
        self.assertEqual(result['status'], 'DECODED')
        self.assertEqual([row['path'] for row in result['verified_files']][:2], [UPLOAD, CAPTURE])
        self.assertEqual(list(result['windows']), [item[0] for item in PLAN[7:19]])
        packet['status'] = 'OTHER'
        packet['files'][0]['data_base64'] = 'not base64'
        self.rejected(packet, 'packet', 'STATUS')

    def test_semantically_inconclusive_window_still_has_decoded_format_status(self):
        spec = list(fixture())
        raw = report(sample(255, 0xFFFFFFFF, 4096, 255, 255, 4), None, 255, 0, [1, 2])
        name = 'first.settle'
        body = settle_bytes(raw)
        spec[2]['11-first.settle.bin'] = body
        spec[3][name] = raw
        spec[1]['reads'][11]['sha256'] = sha(body)
        spec[1]['analysis']['snapshots'][4]['sha256'] = sha(body)
        result = self.accepted(tuple(spec))
        self.assertEqual(result['settle_annotations'][name]['status'], 'INCONCLUSIVE')
        self.assertFalse(result['repeated_fields_equal']['settle'])
        self.assertEqual(result['coherence'], 'UNPROVEN')

    def test_results_and_receipts_do_not_alias_inputs_other_calls_or_annotations(self):
        packet = packet_from(*fixture()[:3])
        raw = json_bytes(packet)
        frozen = bytes(raw)
        with forbid_io():
            one = self.interpret(raw)
            two = self.interpret(raw)
        one['capture_result']['reads'][0]['name'] = 'altered'
        one['settle_annotations']['first.settle']['raw']['current']['reason'] = 255
        one['windows']['first.trace']['calls'][0]['stage'] = -1
        self.assertEqual(raw, frozen)
        self.assertEqual(two, self.interpret(raw))
        self.assertEqual(one['windows']['first.settle']['current']['reason'], 1)


class MainOracle(OracleBase):
    @contextlib.contextmanager
    def local_main(self, raw=None, field_map=None):
        with tempfile.TemporaryDirectory(prefix='d201-oracle-') as name:
            root = Path(name)
            packet = root / RAW_REL / 'retrieved_inert_run01/0001-read-saved-results/stdout'
            packet.parent.mkdir(parents=True)
            map_path = root / MAP_REL
            map_path.parent.mkdir(parents=True)
            raw = json_bytes(packet_from(*fixture()[:3])) if raw is None else raw
            packet.write_bytes(raw)
            map_path.write_bytes(self.map_raw if field_map is None else field_map)
            module = self.load_subject(root)
            output = root / RAW_REL / 'retrieved_inert_run01/decoded.json'
            yield module, packet, map_path, output, raw

    def call_main(self, module, raw):
        with contextlib.redirect_stdout(io.StringIO()):
            return module.main(['--packet-sha256', sha(raw)])

    def test_main_invalid_cli_shapes_and_hashes_do_no_input_output(self):
        class StrSubclass(str):
            pass
        cases = [None, [], ['--packet-sha256'], ['--other', '0' * 64],
                 ['--packet-sha256', 'A' * 64], ['--packet-sha256', '0' * 63],
                 ['--packet-sha256', 'g' * 64], ['--packet-sha256', b'0' * 64],
                 ['--packet-sha256', StrSubclass('0' * 64)],
                 ['--packet-sha256', '0' * 64, '--output', '/tmp/wrong']]
        with self.local_main() as (module, _, _, output, _):
            for argv in cases:
                with self.subTest(argv=argv), forbid_io():
                    self.exception(ValueError, ('main', 'CLI', '/'), lambda: module.main(argv))
            self.assertFalse(output.exists())

    def test_main_missing_bytecode_disable_is_rejected_before_io(self):
        original_flags = sys.flags
        class FlagsWithoutB:
            dont_write_bytecode = 0
            def __getattr__(self, key):
                return getattr(original_flags, key)
        with self.local_main() as (module, _, _, output, raw):
            with mock.patch.object(sys, 'dont_write_bytecode', False), \
                    mock.patch.object(sys, 'flags', FlagsWithoutB()), forbid_io():
                self.exception(ValueError, ('main', 'BYTECODE', '/'),
                               lambda: module.main(['--packet-sha256', sha(raw)]))
            self.assertFalse(output.exists())

    def test_main_reads_each_input_once_with_limit_plus_one_bounds(self):
        with self.local_main() as (module, packet, map_path, output, raw):
            originals = {'builtins': open, 'io': io.open}
            observed = {str(packet): [], str(map_path): []}
            openings = {str(packet): 0, str(map_path): 0}
            limits = {str(packet): 1048577, str(map_path): 65537}

            class TrackedReader:
                def __init__(self, stream, path):
                    self.stream, self.path = stream, path
                def __enter__(self):
                    self.stream.__enter__()
                    return self
                def __exit__(self, *args):
                    return self.stream.__exit__(*args)
                def __getattr__(self, key):
                    return getattr(self.stream, key)
                def read(self, size=-1):
                    if type(size) is not int or size < 0 or size > limits[self.path]:
                        raise AssertionError('input read must be explicitly bounded')
                    observed[self.path].append(size)
                    return self.stream.read(size)

            def tracked_open(which, file, mode='r', *args, **kwargs):
                stream = originals[which](file, mode, *args, **kwargs)
                path = str(file)
                if path in observed and 'r' in mode:
                    openings[path] += 1
                    return TrackedReader(stream, path)
                return stream

            with mock.patch('builtins.open', side_effect=lambda *a, **kw: tracked_open('builtins', *a, **kw)), \
                    mock.patch.object(io, 'open', side_effect=lambda *a, **kw: tracked_open('io', *a, **kw)):
                self.assertEqual(self.call_main(module, raw), 0)
            self.assertEqual(openings, {str(packet): 1, str(map_path): 1})
            self.assertEqual(observed, {str(packet): [1048577], str(map_path): [65537]})
            self.assertTrue(output.is_file())

    def test_main_packet_hash_mismatch_never_invokes_interpret_or_creates_output(self):
        with self.local_main() as (module, packet, _, output, raw):
            with mock.patch.object(module, 'interpret', side_effect=AssertionError('must hash before interpret')):
                self.exception(ValueError, ('packet', 'PACKET_HASH', '/'),
                               lambda: module.main(['--packet-sha256', '0' * 64]))
            self.assertFalse(output.exists())
            self.assertEqual(packet.read_bytes(), raw)

    def test_main_canonical_exclusive_output_all_three_exit_statuses(self):
        cases = [(json_bytes(packet_from(*fixture()[:3])), 0, 'DECODED'),
                 (json_bytes(packet_from(*fixture(0, failed=True)[:3])), 1, 'PARTIAL'),
                 (b'{}', 2, 'REJECTED')]
        for raw, code, status in cases:
            with self.subTest(status=status), self.local_main(raw) as (module, packet, _, output, received):
                self.assertEqual(self.call_main(module, received), code)
                output_raw = output.read_bytes()
                value = json.loads(output_raw)
                self.assertEqual(value['status'], status)
                self.assertEqual(output_raw, (json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + '\n').encode())
                self.assertEqual(packet.read_bytes(), received)
                self.assertEqual(sorted(path.name for path in output.parent.iterdir()), ['0001-read-saved-results', 'decoded.json'])

    def test_main_existing_output_and_filesystem_errors_propagate_without_cleanup(self):
        with self.local_main() as (module, packet, _, output, raw):
            original = b'uniquely retained prior output\n'
            output.write_bytes(original)
            with self.assertRaises(FileExistsError):
                self.call_main(module, raw)
            self.assertEqual(output.read_bytes(), original)
            self.assertEqual(packet.read_bytes(), raw)
        with self.local_main() as (module, _, map_path, output, raw):
            map_path.unlink()
            with self.assertRaises(FileNotFoundError):
                self.call_main(module, raw)
            self.assertFalse(output.exists())

    def test_main_oversize_inputs_refuse_before_json_parse(self):
        with self.local_main(bytes(1048577)) as (module, _, _, output, raw):
            with mock.patch.object(module, 'interpret', side_effect=AssertionError('oversize packet reached interpret')):
                with self.assertRaises(ValueError) as caught:
                    self.call_main(module, raw)
            self.assertEqual(caught.exception.args, ('packet', 'PACKET_SIZE', '/'))
            self.assertFalse(output.exists())
        with self.local_main(field_map=bytes(65537)) as (module, _, _, output, raw):
            # The map is a bounded admitted buffer and its pure format result is
            # REJECTED; either bounded-reader refusal or that result is allowed
            # by main's explicit bound-before-parse requirement.
            try:
                status = self.call_main(module, raw)
            except ValueError as error:
                self.assertEqual(error.args, ('layout', 'MAP_SIZE', '/'))
                self.assertFalse(output.exists())
            else:
                self.assertEqual(status, 2)
                self.assertEqual(json.loads(output.read_bytes())['decode_first_error'],
                                 dict(stage='layout', code='MAP_SIZE', path='/'))


class CurrentConstProvenance(OracleBase):
    def test_exact_seven_decoder_and_map_metadata_steps_preserve_payload_semantics(self):
        contract_raw = (REPO / 'state/analysis/P7_motor_const_run_raw/run_derivation01.json').read_bytes()
        self.assertEqual(sha(contract_raw), 'c90961438062c153f9c99621eba0617b3fc26b0f3dbdd2c35859ec2e744b5bfb')
        derivation = json.loads(contract_raw)
        spec = derivation['metadata_derivatives']['interpreter']
        self.assertEqual(len(spec['steps']), 7)
        source = (REPO / spec['input']['path']).read_bytes()
        self.assertEqual((len(source), sha(source)), (spec['input']['bytes'], spec['input']['sha256']))
        for row in spec['steps']:
            self.assertEqual(source.count(row['old'].encode()), row['count'])
            source = source.replace(row['old'].encode(), row['new'].encode())
        self.assertEqual(self.subject_source, source)
        self.assertEqual((len(source), sha(source)),
            (31259, 'd96c0bec92a5e49571ccfa2fd669afa7bcb27e1fa4243cd20d819ad592b003ab'))
        layout = derivation['field_map']
        prior = (REPO / layout['input']['path']).read_bytes()
        self.assertEqual((len(prior), sha(prior)), (layout['input']['bytes'], layout['input']['sha256']))
        projected = json.loads(prior)
        original = copy.deepcopy(projected)
        self.assertEqual(len(layout['steps']), 7)
        for row in layout['steps']:
            self.assertEqual(projected[row['key']], row['old'])
            projected[row['key']] = row['new']
        self.assertEqual(self.map_raw, (json.dumps(projected, indent=2, sort_keys=True) + '\n').encode())
        self.assertEqual(projected['types'], original['types'])
        self.assertEqual((projected['selected_types'], projected['selected_fields']), (16, 115))
        self.assertEqual(len(PLAN), 26)
        self.assertEqual(sum(row[2] for row in PLAN), 727128)
        self.assertEqual(PLAN[6], ('before.sketch.1', 0x08110000, 29832))
        self.assertEqual(PLAN[20], ('after.sketch.1', 0x08110000, 29832))

    def test_D201_run_and_source_receipts_are_rejected_in_both_roles(self):
        for stage in ('upload', 'capture'):
            for field, stale in (('run_id', 'app-motor-settle-117cc0e7-run01'),
                                 ('source_sha256', '117cc0e777341c893f4e618a97e3f196fd0bbf2427cb2a4b02543eb37d6522da')):
                upload, capture, bodies, _ = fixture()
                (upload if stage == 'upload' else capture)[field] = stale
                self.rejected(packet_from(upload, capture, bodies), stage, 'IDENTITY',
                              '/' + stage + '_result/' + field)

    def test_D201_map_and_95520_package_extent_cannot_be_promoted(self):
        old = (REPO / 'state/analysis/P7_motor_settle_compile_raw/abi_static01_decode_fields.json').read_bytes()
        self.assertEqual(sha(old), '0faba2433fd812508a6b9ac974d75a18e65cf360a123eb009306e3b75ae49bbd')
        packet = json_bytes(packet_from(*fixture()[:3]))
        for candidate, code in ((old, 'MAP_SIZE'), (old + bytes(16755 - len(old)), 'MAP_HASH')):
            result = self.subject.interpret(packet, field_map_raw=candidate)
            self.assertEqual(result['status'], 'REJECTED')
            self.assertEqual(result['decode_first_error'], dict(stage='layout', code=code, path='/'))
        for index in (6, 20):
            upload, capture, bodies, _ = fixture()
            capture['reads'][index]['bytes'] = 29984
            self.rejected(packet_from(upload, capture, bodies), 'capture', 'READ_PLAN')


if __name__ == '__main__':
    unittest.main()
