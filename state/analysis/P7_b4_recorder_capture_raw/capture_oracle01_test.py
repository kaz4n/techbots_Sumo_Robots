# Checks D218 capture hooks and local completion against independently fixed data.
# Reuses unchanged capture dependency bodies and literal D073/D216 byte expectations.
# Root runs the sealed focused suite; no board, transport, upload or real child runs.
import ast
import builtins
from contextlib import ExitStack
import copy
import hashlib
import importlib
import io
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import types
import unittest
from unittest import mock


ROOT = Path(__file__).absolute().parents[2]
RAW = 'state/analysis/P7_b4_recorder_capture_raw'
PLAN_PATH = RAW + '/plan01.json'
PLAN_PIN = (8384, '14137f101e508e93c556eff2c0e2526cde4f63217def6e7c376d5f5078e3e5f7')
CONTRACT = 'state/analysis/P7_b4_recorder_capture_contract.md'
CONTRACT_PIN = (12517, 'c6eba89ae4a5567d220fd69ccc73190c2918e05e6fac57eba35697ca5460bc6b')
RUN = 'b4-recorder-9044ebbb-capture01'
SOURCE = '9044ebbb3cd3b2dbb7aa5984dd5ff23bfff697372f1f29d56693af9ea5eaf31a'
OUTPUT = '/home/arduino/sumox26_codex_build/' + RUN
OWNER_BASE, OWNER_BYTES, TAIL = 536954120, 159200, 159080
FIELDS = ('epoch_token', 'last_frame_token', 'phase')
FLASH_KEYS = ('before_loader', 'before_sketch', 'after_loader', 'after_sketch')
RESULT_KEYS = {'schema', 'bundle_status', 'errors', 'raw_returned', 'returned_sha256',
               'raw_layout', 'layout_sha256', 'raw_files', 'file_hashes', 'raw_owner',
               'analysis', 'decoder', 'coherence', 'body_origin', 'common_attempt_verified',
               'transport_verified', 'hardware_acceptance'}
FRAME_HEADER = (b'schema_version,ordinal,pack_status,t_ms,state,mode,line_mask,opp_mask,'
                b'heading_cdeg,gyro_z_dps10,ax_mg,ay_mg,duty_l_127,duty_r_127,'
                b'vbat_cv,flags,tick_max_us,raw_hex\n')
FRAME_LITERAL = (b'1,0,0,0,250,251,252,253,-2147483648,-32768,32767,0,'
                 b'-128,127,65535,254,4660,00000000fafbfcfd000000800080ff7f0000807ffffffe3412\n')
EVENT_HEADER = b'schema_version,ordinal,t_us,type,detail,value,raw_hex\n'
EVENT_LITERAL = b'1,0,4294967295,254,253,65535,fffffffffefdffff\n'
STUBS = {}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def checked(path, pin):
    raw = (ROOT / path).read_bytes()
    length, digest = (pin['bytes'], pin['sha256']) if type(pin) is dict else pin
    if (len(raw), sha(raw)) != (length, digest):
        raise AssertionError('Independent D218 pin changed: ' + path)
    return raw


def canonical(value):
    return (json.dumps(value, sort_keys=True, ensure_ascii=True, allow_nan=False,
                       separators=(',', ':')) + '\n').encode('ascii')


def forbidden(*args, **kwargs):
    raise AssertionError('Native action forbidden')


def setUpModule():
    if not sys.flags.isolated or not sys.dont_write_bytecode:
        raise RuntimeError('D218 oracle requires Python -I -B')
    if not sys.platform.startswith('linux'):
        for name in ('resource', 'pwd'):
            if name not in sys.modules:
                value = types.ModuleType(name)
                value.RLIMIT_FSIZE, value.setrlimit, value.getpwuid = 1, forbidden, forbidden
                STUBS[name] = value
                sys.modules[name] = value


def tearDownModule():
    for name, value in STUBS.items():
        if sys.modules.get(name) is value:
            del sys.modules[name]
    STUBS.clear()


def literal_plan():
    plan = []
    def flash(prefix, region, base, length):
        for index, offset in enumerate(range(0, length, 65536)):
            plan.append((prefix + '.' + region + '.' + str(index), base + offset,
                         min(65536, length - offset)))
    flash('before', 'loader', 0x08000000, 263680)
    flash('before', 'sketch', 0x08100000, 82912)
    plan.append(('before.lifecycle', 537113200, 120))
    for index, offset in enumerate(range(0, OWNER_BYTES, 16384)):
        plan.append(('owner.' + str(index), OWNER_BASE + offset, min(16384, OWNER_BYTES - offset)))
    plan.append(('after.lifecycle', 537113200, 120))
    flash('after', 'sketch', 0x08100000, 82912)
    flash('after', 'loader', 0x08000000, 263680)
    return tuple(plan)


PLAN = literal_plan()
LEAVES = tuple(f'{index:02d}-{name}.bin' for index, (name, _, _) in enumerate(PLAN) if 7 <= index <= 18)


def bracket(epoch=11, token=22, phase=3, fill=0):
    raw = bytearray([fill]) * 120
    raw[0:8], raw[8:16] = epoch.to_bytes(8, 'little'), token.to_bytes(8, 'little')
    raw[113] = phase
    return bytes(raw)


def observation(raw):
    return {'epoch_token': int.from_bytes(raw[:8], 'little'),
            'last_frame_token': int.from_bytes(raw[8:16], 'little'), 'phase': raw[113]}


def expected_analysis(owner=None, before=None, after=None, flash=None):
    life = {'before': None if before is None else observation(before),
            'body': None if owner is None else observation(owner[TAIL:]),
            'after': None if after is None else observation(after)}
    equal = {}
    for key, left, right in (('before_body', 'before', 'body'), ('body_after', 'body', 'after'),
                             ('before_after', 'before', 'after')):
        equal[key] = None if life[left] is None or life[right] is None else {
            field: life[left][field] == life[right][field] for field in FIELDS}
    return {'schema': 'b4-recorder-capture-analysis-v1',
            'flash': dict.fromkeys(FLASH_KEYS, True) if flash is None else dict(flash),
            'owner': None if owner is None else {'address': OWNER_BASE, 'bytes': OWNER_BYTES,
                                                'sha256': sha(owner), 'chunks': 10},
            'lifecycle': life, 'equalities': equal, 'coherence': 'UNPROVEN'}


def owner_bytes():
    raw = bytearray(OWNER_BYTES)
    raw[:25] = bytes.fromhex('00000000fafbfcfd000000800080ff7f0000807ffffffe3412')
    raw[126280:126284] = (1).to_bytes(4, 'little')
    raw[126300:126308] = bytes.fromhex('fffffffffefdffff')
    raw[159068:159072] = (1).to_bytes(4, 'little')
    raw[TAIL:] = bracket()
    return bytes(raw)


class Bundle:
    """Independent bounded evidence fixture; its synthetic flash hashes are declarations."""
    def __init__(self, owner=None, before=None, after=None):
        self.owner = owner_bytes() if owner is None else owner
        self.before = self.owner[TAIL:] if before is None else before
        self.after = self.owner[TAIL:] if after is None else after
        self.files, reads = {}, []
        for index, (name, address, size) in enumerate(PLAN):
            leaf = f'{index:02d}-{name}.bin'
            if name == 'before.lifecycle':
                raw = self.before
            elif name == 'after.lifecycle':
                raw = self.after
            elif name.startswith('owner.'):
                raw = self.owner[address - OWNER_BASE:address - OWNER_BASE + size]
            else:
                raw = None
            if raw is not None:
                self.files[leaf] = raw
            digest = sha(raw) if raw is not None else sha(name.split('.', 1)[1].encode('ascii'))
            reads.append({'name': name, 'address': address, 'bytes': size, 'sha256': digest, 'file': leaf})
        self.report = {'schema': 'b4-recorder-capture-result-v1', 'run_id': RUN,
            'source_sha256': SOURCE, 'status': 'COLLECTED',
            'counts': {'commands': 26, 'reads': 26, 'requested_bytes': 852624},
            'started_utc': '2026-09-26T00:00:00+00:00', 'finished_utc': '2026-09-26T00:00:01+00:00',
            'started_monotonic': 100.0, 'finished_monotonic': 101.0, 'wait': None,
            'reads': reads, 'first_error': None, 'postcheck_errors': [],
            'analysis': expected_analysis(self.owner, self.before, self.after)}
        self.envelope = {'schema': 'b4-recorder-action-v1', 'action': 'capture', 'run_id': RUN,
            'source_sha256': SOURCE, 'report': None, 'report_origin': 'returned',
            'remote_result_path': OUTPUT + '/capture_result.json', 'full_result_bytes': None,
            'full_result_sha256': None, 'first_error': None, 'postcheck_errors': []}

    def seal(self):
        raw = canonical(self.report)
        self.files['capture_result.json'] = raw
        self.envelope.update(report=copy.deepcopy(self.report), full_result_bytes=len(raw), full_result_sha256=sha(raw))
        return canonical(self.envelope)


class CaptureContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plan_data = json.loads(checked(PLAN_PATH, PLAN_PIN))
        checked(CONTRACT, CONTRACT_PIN)
        cls.sources = {role: checked(pin['path'], pin) for role, pin in cls.plan_data['dependency_inputs'].items()}
        cls.layout = checked(cls.plan_data['layout']['path'], cls.plan_data['layout'])
        checked(cls.plan_data['decoder']['path'], cls.plan_data['decoder'])
        sys.path.insert(0, str(ROOT))
        cls.native = importlib.import_module('tools.b4_recorder_capture')
        cls.host = importlib.import_module('tools.decode_b4_capture')

    def setUp(self):
        for owner, name in ((subprocess, 'Popen'), (subprocess, 'run'), (socket, 'socket'),
                            (socket, 'create_connection'), (os, 'system'), (os, 'killpg')):
            guard = mock.patch.object(owner, name, side_effect=forbidden, create=True)
            guard.start()
            self.addCleanup(guard.stop)

    def capture(self):
        deps = self.native.load_dependencies(dict(self.sources))
        with mock.patch.object(deps.capture, '_collect', side_effect=lambda value: value) as observed:
            capture = self.native.collect(deps, bindings=self.native.fixed_bindings(),
                                          executor=forbidden, clock=lambda: 100.0)
            observed.assert_called_once_with(capture)
        return capture, deps

    def gathered(self, *, fail=None, bad_flash=None, before=None, after=None):
        capture, deps = self.capture()
        capture.bindings = capture.profile_bindings()
        owner = owner_bytes()
        before = owner[TAIL:] if before is None else before
        after = owner[TAIL:] if after is None else after
        capture.loader, capture.sketch = bytes([17]) * 263680, bytes([34]) * 82912
        capture.prepare_plan()
        attempted = []
        def read(index, item):
            attempted.append(index)
            name, address, size = item
            capture.report['counts']['commands'] += 1
            capture.report['counts']['requested_bytes'] += size
            if index == fail:
                raise OSError('fixture read failure')
            if name == 'before.lifecycle':
                raw = before
            elif name == 'after.lifecycle':
                raw = after
            elif name.startswith('owner.'):
                raw = owner[address - OWNER_BASE:address - OWNER_BASE + size]
            else:
                region = 'loader' if '.loader.' in name else 'sketch'
                base = 0x08000000 if region == 'loader' else 0x08100000
                reference = getattr(capture, region)
                raw = reference[address - base:address - base + size]
                if name.startswith(str(bad_flash) + '.'):
                    raw = bytes([raw[0] ^ 1]) + raw[1:]
            capture.samples.append((name, address, raw))
            capture.report['reads'].append({'name': name, 'address': address, 'bytes': len(raw),
                'sha256': sha(raw), 'file': f'{index:02d}-{name}.bin'})
            capture.report['counts']['reads'] += 1
        capture.one_read = read
        return capture, deps, attempted, owner, before, after

    def decode(self, bundle, raw=None, layout=None):
        return self.host.decode_capture(bundle.seal() if raw is None else raw, files=bundle.files,
                                        layout_raw=self.layout if layout is None else layout)

    def boundary(self, report, raw, files, layout=None):
        layout = self.layout if layout is None else layout
        self.assertEqual(set(report), RESULT_KEYS)
        self.assertEqual(report['schema'], 'b4-recorder-capture-decode-v1')
        self.assertEqual(report['raw_returned'], raw)
        self.assertEqual(report['returned_sha256'], sha(raw))
        self.assertEqual(report['raw_layout'], layout)
        self.assertEqual(report['layout_sha256'], sha(layout))
        self.assertEqual(report['raw_files'], files)
        self.assertIsNot(report['raw_files'], files)
        self.assertEqual(report['file_hashes'], {name: sha(value) for name, value in files.items()})
        self.assertEqual(report['coherence'], 'UNPROVEN')
        self.assertEqual(report['body_origin'], 'UNPROVEN')
        for name in ('common_attempt_verified', 'transport_verified', 'hardware_acceptance'):
            self.assertIs(report[name], False)
        for error in report['errors']:
            self.assertEqual(set(error), {'code', 'message'})
            self.assertTrue(type(error['message']) is str and error['message'])

    def refused(self, bundle, code, raw=None, layout=None):
        raw = bundle.seal() if raw is None else raw
        report = self.decode(bundle, raw, layout)
        self.boundary(report, raw, bundle.files, layout)
        self.assertEqual(report['bundle_status'], 'REFUSED')
        self.assertIsNone(report['decoder'])
        self.assertTrue(report['errors'])
        self.assertEqual(report['errors'][0]['code'], code)
        return report

    def test_dependency_pins_precede_private_execution_and_inherited_capture_bodies_remain_exact(self):
        for role in self.sources:
            for wrong in (b'', self.sources[role] + b'\n', bytearray(self.sources[role])):
                values = dict(self.sources)
                values[role] = wrong
                with self.subTest(role=role, wrong_type=type(wrong).__name__):
                    with mock.patch.object(builtins, 'exec', side_effect=forbidden) as execute:
                        with self.assertRaises((ValueError, TypeError)):
                            self.native.load_dependencies(values)
                        execute.assert_not_called()
        capture, deps = self.capture()
        base = deps.capture.Capture
        overrides = {name for name, value in vars(base).items() if callable(value)
                     and name in vars(type(capture))}
        self.assertEqual(overrides, {'profile_bindings', 'prepare_plan', 'gather', 'complete'})
        for name, value in vars(base).items():
            if callable(value) and name not in overrides:
                self.assertIs(getattr(type(capture), name), value)
        source = ast.parse(self.sources['capture'])
        unchanged = next(node for node in source.body if isinstance(node, ast.FunctionDef) and node.name == '_collect')
        expected = ast.get_source_segment(self.sources['capture'].decode(), unchanged)
        self.assertIn('finally:', expected)
        self.assertIn('capture.close()', expected)
        reference = types.ModuleType('_independent_accepted_capture')
        exec(compile(self.sources['capture'], deps.capture._collect.__code__.co_filename, 'exec'), reference.__dict__)
        self.assertEqual(deps.capture._collect.__code__, reference._collect.__code__)
        for name, value in vars(reference.Capture).items():
            if isinstance(value, types.FunctionType):
                self.assertEqual(getattr(base, name).__code__, value.__code__, name)

    def test_exact_bindings_detach_and_reject_stale_profile_paths_pins_and_types(self):
        self.assertEqual(self.native.fixed_bindings(), self.plan_data['bindings'])
        detached = self.native.fixed_bindings()
        detached['files']['sketch']['bytes'] = 1
        self.assertEqual(self.native.fixed_bindings(), self.plan_data['bindings'])
        capture, _ = self.capture()
        self.assertEqual(capture.profile_bindings(), self.plan_data['bindings'])
        mutations = [('schema', 'fixed-ordinary-app-capture-v1'), ('run_id', 'ordinary-app-9044ebbb-run01'),
                     ('source_sha256', '0' * 64), ('boot_id', '0' * 36), ('uid', True), ('output', OUTPUT + '-other')]
        for field, value in mutations:
            with self.subTest(field=field):
                capture.input_bindings = copy.deepcopy(self.plan_data['bindings'])
                capture.input_bindings[field] = value
                with self.assertRaises(ValueError):
                    capture.profile_bindings()
        for role in ('openocd', 'config', 'swj', 'loader', 'sketch'):
            for field, value in (('path', '/tmp/stale'), ('bytes', True), ('sha256', '0' * 64)):
                capture.input_bindings = copy.deepcopy(self.plan_data['bindings'])
                capture.input_bindings['files'][role][field] = value
                with self.subTest(role=role, field=field), self.assertRaises(ValueError):
                    capture.profile_bindings()

    def test_fixed_26read_plan_and_all_three_lifecycle_observations_preserve_mismatch(self):
        self.assertEqual(self.native.read_plan(), PLAN)
        self.assertEqual(PLAN, tuple((item['name'], item['address'], item['bytes']) for item in self.plan_data['plan']))
        self.assertEqual((len(PLAN), sum(item[2] for item in PLAN)), (26, 852624))
        self.assertEqual(PLAN[17], ('owner.9', OWNER_BASE + 9 * 16384, 11744))
        before, after = bracket(9, 22, 3, 255), bracket(11, 99, 255, 17)
        capture, deps, attempted, owner, _, _ = self.gathered(before=before, after=after)
        capture.gather()
        self.assertEqual(attempted, list(range(26)))
        self.assertEqual(capture.plan, PLAN)
        self.assertEqual(capture.report['counts'], self.plan_data['counts'])
        self.assertEqual(capture.report['analysis'], expected_analysis(owner, before, after))
        self.assertIsNone(capture.report['wait'])
        self.assertTrue(capture.complete())
        self.assertEqual(capture.report['analysis']['lifecycle']['after']['phase'], 255)
        self.assertEqual(capture.started, 100.0)
        self.assertEqual(capture.budget(), 600.0)
        for _, address, length in PLAN[7:19]:
            deps.p0.ram_range(address, length)

    def test_flash_mismatch_stops_at_each_image_boundary_and_before_sram_for_stale_sketch(self):
        for region, last in (('before.loader', 4), ('before.sketch', 6), ('after.sketch', 20), ('after.loader', 25)):
            with self.subTest(region=region):
                capture, _, attempted, _, _, _ = self.gathered(bad_flash=region)
                with self.assertRaises(ValueError):
                    capture.gather()
                self.assertEqual(attempted, list(range(last + 1)))
                self.assertIs(capture.report['analysis']['flash'][region.replace('.', '_')], False)
                self.assertFalse(capture.complete())
                if region.startswith('before.'):
                    self.assertTrue(all(index < 7 for index in attempted))

    def test_partial_read_failure_preserves_available_owner_and_lifecycle_without_padding(self):
        for failed in (7, 12, 18, 24):
            with self.subTest(failed=failed):
                capture, _, attempted, owner, before, after = self.gathered(fail=failed)
                with self.assertRaisesRegex(OSError, 'fixture read failure'):
                    capture.gather()
                self.assertEqual(attempted, list(range(failed + 1)))
                self.assertEqual(len(capture.samples), failed)
                self.assertEqual(capture.report['counts']['commands'], failed + 1)
                self.assertEqual(capture.report['counts']['reads'], failed)
                self.assertFalse(capture.complete())
                flash = {'before_loader': True, 'before_sketch': True, 'after_loader': False,
                         'after_sketch': failed > 20}
                expected = expected_analysis(owner if failed > 17 else None,
                    before if failed > 7 else None, after if failed > 18 else None, flash)
                self.assertEqual(capture.report['analysis'], expected)

    def test_complete_local_bundle_reassembles_exact_owner_and_d073_csv_without_origin_claim(self):
        bundle = Bundle()
        raw = bundle.seal()
        report = self.decode(bundle, raw)
        self.boundary(report, raw, bundle.files)
        self.assertEqual(report['bundle_status'], 'PASS')
        self.assertEqual(report['errors'], [])
        self.assertEqual(report['raw_owner'], bundle.owner)
        self.assertEqual(report['analysis'], bundle.report['analysis'])
        nested = report['decoder']
        self.assertEqual(nested['raw_owner'], bundle.owner)
        self.assertEqual(nested['csv']['frames'], FRAME_HEADER + FRAME_LITERAL)
        self.assertEqual(nested['csv']['events'], EVENT_HEADER + EVENT_LITERAL)
        self.assertEqual((nested['export_status'], nested['format_integrity'], nested['consistency']), ('PASS', 'PASS', 'PASS'))
        self.assertEqual(nested['recording'], {'loss': 'NONE_REPORTED', 'lifecycle': 'SEALED', 'phase_code': 3})
        self.assertEqual(nested['coherence'], 'UNPROVEN')
        self.assertFalse(nested['common_attempt_verified'])
        self.assertEqual(len(raw), 5870)
        self.assertEqual(len(bundle.files['capture_result.json']), 5393)
        self.assertEqual(sum(map(len, bundle.files.values())), 164833)
        self.assertLess(len(raw), 65536)
        self.assertLess(len(bundle.files['capture_result.json']), 65536)
        self.assertLess(sum(map(len, bundle.files.values())), 262144)

    def test_local_lifecycle_mismatch_and_nested_decoder_refusal_remain_distinct_from_bundle_success(self):
        bundle = Bundle(before=bracket(33, 22, 255), after=bracket(11, 44, 4))
        report = self.decode(bundle)
        self.assertEqual(report['bundle_status'], 'PASS')
        self.assertEqual(report['analysis'], expected_analysis(bundle.owner, bundle.before, bundle.after))
        self.assertEqual(report['analysis']['equalities']['before_after'], dict.fromkeys(FIELDS, False))
        self.assertEqual(report['decoder']['summary']['phase'], 3)
        malformed = bytearray(owner_bytes())
        malformed[159171] = 2
        bundle = Bundle(owner=bytes(malformed))
        report = self.decode(bundle)
        self.assertEqual(report['bundle_status'], 'PASS')
        self.assertEqual(report['errors'], [])
        self.assertEqual(report['decoder']['export_status'], 'REFUSED')
        self.assertEqual(report['decoder']['native_values']['summary_.go_seen'], 2)

    def test_envelope_identity_returned_origin_and_successful_closure_are_required(self):
        changes = (('schema', 'ordinary-app-action-v1'), ('action', 'upload'), ('run_id', 'stale'),
            ('source_sha256', '0' * 64), ('report_origin', 'durable_unattributed'),
            ('remote_result_path', OUTPUT + '/elsewhere.json'), ('first_error', {'type': 'Error', 'message': 'close'}),
            ('postcheck_errors', [{'check': 'close', 'type': 'Error', 'message': 'close'}]))
        for name, value in changes:
            bundle = Bundle()
            bundle.seal()
            bundle.envelope[name] = value
            with self.subTest(field=name):
                report = self.refused(bundle, 'ENVELOPE', canonical(bundle.envelope))
                self.assertIsNone(report['raw_owner'])

    def test_exact_file_selection_and_report_hash_embedded_types_and_timestamps_are_required(self):
        for mode in ('missing', 'renamed', 'traversal'):
            bundle = Bundle()
            raw = bundle.seal()
            removed = bundle.files.pop(LEAVES[0])
            if mode != 'missing':
                bundle.files['other.bin' if mode == 'renamed' else '../other.bin'] = removed
            with self.subTest(files=mode):
                self.refused(bundle, 'FILES', raw)
        changes = (('status', 'FAILED'), ('first_error', {'type': 'Error', 'message': 'close'}),
            ('postcheck_errors', [{'check': 'final', 'type': 'Error', 'message': 'close'}]),
            ('wait', {}), ('finished_monotonic', 700.0), ('finished_monotonic', 99),
            ('started_monotonic', True), ('started_utc', 'not-a-time'),
            ('started_utc', '2026-09-26T00:00:00'), ('finished_utc', '2026-09-25T00:00:00+00:00'))
        for name, value in changes:
            bundle = Bundle()
            bundle.report[name] = value
            with self.subTest(report_field=name, value=value):
                self.refused(bundle, 'REPORT')
        for name in ('commands', 'reads', 'requested_bytes'):
            bundle = Bundle()
            bundle.report['counts'][name] = True
            with self.subTest(counter=name):
                self.refused(bundle, 'REPORT')
        bundle = Bundle()
        bundle.seal()
        bundle.envelope['report']['counts']['reads'] = 26.0
        self.refused(bundle, 'REPORT', canonical(bundle.envelope))
        bundle = Bundle()
        raw = bundle.seal()
        bundle.files['capture_result.json'] += b' '
        self.refused(bundle, 'REPORT', raw)

    def test_ordered_read_geometry_and_every_sram_leaf_hash_are_required(self):
        for index in (0, 7, 8, 17, 18, 25):
            for field, value in (('address', True), ('bytes', -1), ('file', 'wrong.bin'), ('sha256', 'Z' * 64)):
                bundle = Bundle()
                bundle.report['reads'][index][field] = value
                with self.subTest(index=index, field=field):
                    self.refused(bundle, 'READS')
        bundle = Bundle()
        bundle.report['reads'][8], bundle.report['reads'][9] = bundle.report['reads'][9], bundle.report['reads'][8]
        self.refused(bundle, 'READS')
        for leaf in LEAVES:
            bundle = Bundle()
            raw = bundle.seal()
            value = bundle.files[leaf]
            bundle.files[leaf] = bytes([value[0] ^ 1]) + value[1:]
            with self.subTest(leaf=leaf):
                report = self.refused(bundle, 'READS', raw)
                if leaf == '18-after.lifecycle.bin':
                    self.assertEqual(report['raw_owner'], bundle.owner)
        for leaf in (LEAVES[1], LEAVES[-2]):
            bundle = Bundle()
            raw = bundle.seal()
            bundle.files[leaf] = bundle.files[leaf][:-1]
            self.refused(bundle, 'READS', raw)

    def test_all_flash_flags_and_seven_chunk_hash_pairs_are_required(self):
        for field in FLASH_KEYS:
            bundle = Bundle()
            bundle.report['analysis']['flash'][field] = False
            with self.subTest(flag=field):
                self.refused(bundle, 'FLASH')
        for index in range(7):
            bundle = Bundle()
            bundle.report['reads'][index]['sha256'] = 'a' * 64
            with self.subTest(chunk=index):
                self.refused(bundle, 'FLASH')

    def test_analysis_is_recomputed_with_exact_types_and_layout_binding_precedes_nested_decode(self):
        mutations = (
            lambda a: a['owner'].update(sha256='0' * 64),
            lambda a: a['owner'].update(chunks=9),
            lambda a: a['lifecycle']['body'].update(epoch_token=12),
            lambda a: a['lifecycle']['after'].update(phase=True),
            lambda a: a['equalities']['before_after'].update(phase=1),
            lambda a: a.update(coherence='PROVEN'))
        for number, mutate in enumerate(mutations):
            bundle = Bundle()
            mutate(bundle.report['analysis'])
            with self.subTest(number=number):
                report = self.refused(bundle, 'ANALYSIS')
                self.assertEqual(report['raw_owner'], bundle.owner)
                self.assertIsNone(report['analysis'])
        bundle = Bundle()
        report = self.refused(bundle, 'LAYOUT', layout=self.layout + b' ')
        self.assertEqual(report['raw_owner'], bundle.owner)
        self.assertEqual(report['analysis'], bundle.report['analysis'])

    def test_bounded_json_utf8_duplicate_nonfinite_and_deep_failures_preserve_raw_inputs(self):
        malformed = (b'', b'\xff', b'{', b'{"schema":1,"schema":2}', b'{"x":NaN}',
                     b'[' * 2048 + b']' * 2048)
        bundle = Bundle()
        bundle.seal()
        for raw in malformed:
            with self.subTest(bytes=len(raw)):
                self.refused(bundle, 'INPUT_JSON', raw)
        bundle = Bundle()
        raw = bundle.seal()
        bundle.files['capture_result.json'] = b'[' * 2048 + b']' * 2048
        self.refused(bundle, 'INPUT_JSON', raw)

    def test_exact_input_types_and_all_resource_limits_refuse_before_hash_or_parse(self):
        class ByteSubclass(bytes):
            pass
        class DictSubclass(dict):
            pass
        class StrSubclass(str):
            pass
        bundle = Bundle()
        raw = bundle.seal()
        wrong_types = ((bytearray(raw), bundle.files, self.layout), (raw, DictSubclass(bundle.files), self.layout),
            (raw, {'x': bytearray(b'')}, self.layout), (raw, {StrSubclass('x'): b''}, self.layout),
            (raw, bundle.files, ByteSubclass(self.layout)))
        excessive = ((bytes(65537), {}, b''), (b'', {}, bytes(65537)),
            (b'', {str(i): b'' for i in range(14)}, b''), (b'', {'x' * 97: b''}, b''),
            (b'', {'x': bytes(65537)}, b''), (b'', {str(i): bytes(65536) for i in range(5)}, b''))
        with mock.patch.object(hashlib, 'sha256', side_effect=forbidden), mock.patch.object(json, 'loads', side_effect=forbidden):
            for returned, files, layout in wrong_types:
                with self.assertRaises(TypeError):
                    self.host.decode_capture(returned, files=files, layout_raw=layout)
            for returned, files, layout in excessive:
                with self.assertRaises(ValueError):
                    self.host.decode_capture(returned, files=files, layout_raw=layout)

    def test_pure_local_decode_does_not_call_native_or_io_and_retained_raw_mapping_is_detached(self):
        bundle = Bundle()
        raw = bundle.seal()
        before = copy.deepcopy(bundle.files)
        with ExitStack() as stack:
            for owner, name in ((builtins, 'open'), (io, 'open'), (os, 'open'),
                                (self.native, 'load_dependencies'), (self.native, 'collect')):
                stack.enter_context(mock.patch.object(owner, name, side_effect=forbidden))
            report = self.decode(bundle, raw)
        self.assertEqual(report['bundle_status'], 'PASS')
        self.assertEqual(bundle.files, before)
        self.boundary(report, raw, bundle.files)
        bundle.files.clear()
        self.assertEqual(report['raw_files'], before)


if __name__ == '__main__':
    unittest.main(verbosity=2)
