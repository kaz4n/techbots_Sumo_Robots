# Tests D176 from its public contract and the existing find_bss traversal interface.
# Keeps synthetic raw observations separate from hardware origin and lifecycle claims.
# Freeze before execution; Linux temporary files only, with every native child mocked.
import copy
from contextlib import contextmanager
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import signal
import stat
import struct
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest import mock


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SOURCE = '8f592937961a0c95b7cc4db88617169fcc9504644aa8b8b7dcf62f83c4c33f36'
RUN = 'motor-fault-8f592937-run01'
OUTPUT = '/home/arduino/sumox26_codex_build/' + RUN + '-capture'
PATHS = {
    'openocd': '/opt/openocd/bin/openocd',
    'config': '/home/arduino/sumox26-capture-tools/app-default-beeffff315b2e28a95a20dc1e26477fc924b2da26d1fdd8a8b36fb013ca110e1/p0_mem_read.cfg',
    'swj': '/opt/openocd/share/openocd/scripts/target/swj-dp.tcl',
    'loader': '/home/arduino/.arduino15/packages/arduino/hardware/zephyr/1.0.0/firmwares/zephyr-arduino_uno_q_stm32u585xx.elf',
    'sketch': '/home/arduino/sumox26_codex_build/motor-fault-active01/_app_builds/native-app-v1/' + SOURCE + '/bench-default/3aafdd0129f64799b4db51efe78e5c44/build/motor_fault.ino.elf-zsk.bin',
}
PLAN_SUMMARY = {'profile': 'motor-fault-v1', 'max_reads': 24,
    'max_requested_bytes': 593424, 'loader_bytes': 263680,
    'sketch_bytes': 29836, 'bss_bytes': 2632, 'snapshot_bytes': 2592,
    'extension_nodes': 3, 'sample_gap_seconds': 2}
REPORT_KEYS = {'schema', 'run_id', 'source_sha256', 'status', 'counts',
    'started_utc', 'finished_utc', 'started_monotonic', 'finished_monotonic',
    'wait', 'reads', 'first_error', 'postcheck_errors', 'analysis'}
SUCCESS = {'returncode': 0, 'timed_out': False, 'reaped': True}
LOADER = bytes(range(256)) * 1030
SKETCH = (bytes(reversed(range(256))) * 117)[:29836]
LIST = 0x200017bc
BSS = 0x20040000
NODES = (0x20002000, 0x20002200, 0x20002400)
ENV = {'HOME': '/home/arduino', 'USER': 'arduino', 'LOGNAME': 'arduino',
       'PATH': '/usr/bin:/bin', 'LANG': 'C.UTF-8'}


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def patch_word(raw, offset, value):
    result = bytearray(raw)
    struct.pack_into('<I', result, offset, value)
    return bytes(result)


def snapshot(phase=0, counter=0):
    # D173 public ARM ABI: Report at2312, last_us_ at2580; zero is valid
    # for every enum, bool and float, including unused array entries.
    raw = bytearray(2592)
    raw[2312] = phase
    struct.pack_into('<I', raw, 2580, counter)
    return bytes(raw)


class Clock:
    def __init__(self):
        self.now = 100.0
        self.sleeps = []

    def __call__(self):
        return self.now

    def sleep(self, seconds):
        self.sleeps.append(seconds)
        self.now += seconds


@unittest.skipUnless(sys.platform.startswith('linux'), 'Linux descriptor semantics required')
class MotorFaultCaptureContract(unittest.TestCase):
    def setUp(self):
        for owner, name in ((subprocess, 'Popen'), (os, 'killpg')):
            guard = mock.patch.object(owner, name,
                side_effect=AssertionError('Native process action forbidden in this fixture'))
            guard.start()
            self.addCleanup(guard.stop)
        self.temp = tempfile.TemporaryDirectory(prefix='sumox_motor_fault_capture_')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.subject = load(HERE / 'capture_remote.py', 'd176_capture_subject')
        self.globals_before = copy.deepcopy((self.subject.BINDINGS,
                                           getattr(self.subject, 'OUTPUT_NAME', None)))
        self.helper = load(ROOT / 'state/analysis/P7_static_link_probe_raw/static_remote.py',
                           'd176_descriptor_helper')
        with mock.patch.object(sys, 'path', [str(ROOT / 'tools'), *sys.path]):
            self.relocation = load(ROOT / 'tools/runtime_capture.py', 'd176_real_relocation')
        self.make_files()
        self.calls, self.identity_calls, self.pin_checks = [], [], []
        self.after_execute = None
        self.raw_change = None
        self.process_result = dict(SUCCESS)
        self.execute_error = None
        self.stdout, self.stderr = b'', b'controlled diagnostic stderr\n'
        self.clock = Clock()
        self.identity_value = {'user': 'arduino', 'uid': 1000, 'gid': 1000,
            'home': '/home/arduino', 'sysname': 'Linux', 'release': 'fixture',
            'machine': 'aarch64', 'boot_id': self.bindings['boot_id'],
            'python': list(sys.version_info[:3])}
        self.helper.identity = self.identity
        self.helper.directory_info = self.directory_info
        self.original_read = self.helper.logical_read
        self.helper.logical_read = self.logical_read
        self.set_nodes(1)

    def make_files(self):
        self.contents = {key: ('synthetic-' + key).encode() for key in PATHS}
        self.contents['sketch'] = SKETCH
        self.bindings = {'schema': 'fixed-motor-fault-capture-v1', 'run_id': RUN,
            'source_sha256': SOURCE, 'boot_id': '01234567-89ab-4cde-8fab-0123456789ab',
            'uid': 1000, 'output': OUTPUT, 'files': {},
            'loader_image': {'bytes': len(LOADER), 'sha256': digest(LOADER)}}
        for key, logical in PATHS.items():
            raw = self.contents[key]
            self.bindings['files'][key] = {'path': logical, 'bytes': len(raw),
                                          'sha256': digest(raw)}
            path = self.logical(logical)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(raw)
        self.output = self.logical(OUTPUT)
        self.output.parent.mkdir(parents=True, exist_ok=True)
        self.logical('/proc').mkdir()

    def logical(self, path):
        return self.root / str(path).lstrip('/')

    def local_argument(self, path):
        value = Path(path)
        return value if value.is_relative_to(self.root) else self.logical(value)

    def identity(self, fd):
        self.identity_calls.append(fd)
        return copy.deepcopy(self.identity_value)

    def directory_info(self, info, logical):
        if not stat.S_ISDIR(info.st_mode):
            raise ValueError('Not a directory: ' + logical)
        return self.helper.directory_id(info)

    def logical_read(self, fd, logical, limit, proc=False):
        for key, path in PATHS.items():
            if logical == path:
                self.pin_checks.append((key, limit))
        return self.original_read(fd, logical, limit, proc)

    def loader_image(self, raw):
        self.assertEqual(raw, self.contents['loader'])
        return LOADER

    def set_nodes(self, count, selected=None):
        self.node_count = count
        selected = count - 1 if selected is None else selected
        self.extension = {'node_address': NODES[selected], 'bss_address': BSS,
                          'bss_size': 2632, 'visited_nodes': list(NODES[:count])}
        self.node_raw = []
        for i in range(count):
            node = bytearray(196)
            struct.pack_into('<I', node, 0, NODES[i + 1] if i + 1 < count else 0)
            name = b'sketch' if i == selected else ('helper' + str(i)).encode()
            node[4:4 + len(name)] = name
            struct.pack_into('<I', node, 32, BSS)
            struct.pack_into('<I', node, 92, 2632)
            node[195] = 10 + i  # Full raw equality must include unused tail bytes.
            self.node_raw.append(bytes(node))
        self.list_raw = struct.pack('<II', NODES[0], NODES[count - 1])
        loader = [(f'loader.{i}', 0x08000000 + i * 65536,
                   65536 if i < 4 else 1536) for i in range(5)]
        flash = lambda prefix, items: [(prefix + '.' + n, a, s) for n, a, s in items]
        walk = [('llext-list', LIST, 8)]
        walk += [(f'node-{i + 1}', NODES[i], 196) for i in range(count)]
        walk += [('llext-list-confirm', LIST, 8)]
        sketch = [('sketch.0', 0x08100000, 29836)]
        self.plan = flash('before', loader + sketch + walk)
        self.plan += [('first.diagnostic', BSS, 2592), ('second.diagnostic', BSS, 2592)]
        self.plan += flash('after', walk + sketch + loader)
        self.samples = {'first.diagnostic': snapshot(), 'second.diagnostic': snapshot(2, 17)}

    def bytes_for(self, item):
        name, address, size = item
        if '.loader.' in name:
            return LOADER[address - 0x08000000:address - 0x08000000 + size]
        if '.sketch.' in name:
            return SKETCH
        if '.llext-list' in name:
            return self.list_raw
        if '.node-' in name:
            return self.node_raw[int(name.rsplit('-', 1)[1]) - 1]
        return self.samples[name]

    def check_launch(self, argv, stdout, stderr, timeout):
        index = len(self.calls)
        self.assertLess(index, len(self.plan), 'No command outside the finite public plan')
        name, address, size = self.plan[index]
        raw_path = OUTPUT + f'/{index:02d}-{name}.bin'
        self.assertEqual(argv, [PATHS['openocd'], '-f', PATHS['config'], '-c',
            f'dump_image {{{raw_path}}} 0x{address:08x} {size}', '-c', 'shutdown'])
        self.assertEqual(self.local_argument(stdout), self.output / f'{index:02d}.stdout')
        self.assertEqual(self.local_argument(stderr), self.output / f'{index:02d}.stderr')
        self.assertEqual(timeout, min(30.0, 700.0 - self.clock.now))
        self.assertTrue((self.output / 'capture_attempt.json').is_file())
        self.assertTrue((self.output / f'{index:02d}.command.json').is_file())
        self.calls.append((copy.deepcopy(argv), timeout))
        return index, self.logical(raw_path)

    def execute(self, argv, stdout, stderr, timeout):
        index, target = self.check_launch(argv, stdout, stderr, timeout)
        if self.execute_error:
            raise self.execute_error
        self.local_argument(stdout).write_bytes(self.stdout)
        self.local_argument(stderr).write_bytes(self.stderr)
        raw = self.bytes_for(self.plan[index])
        if self.raw_change:
            raw = self.raw_change(index, raw, target)
        if raw is not None:
            with target.open('xb') as stream:
                stream.write(raw)
        if self.after_execute:
            self.after_execute(index)
        return copy.deepcopy(self.process_result)

    def collect(self, **kwargs):
        options = dict(fs_root=self.root, executor=self.execute, clock=self.clock,
                       sleeper=self.clock.sleep, bindings=self.bindings)
        options.update(kwargs)
        return self.subject.collect_motor_fault(self.helper, self.relocation,
                                                self.loader_image, **options)

    def assert_report(self, report, status):
        self.assertEqual(set(report), REPORT_KEYS)
        self.assertEqual(report['schema'], 'motor-fault-capture-result-v1')
        self.assertEqual((report['run_id'], report['source_sha256']), (RUN, SOURCE))
        self.assertEqual(report['status'], status)
        self.assertEqual(report['counts'], {'commands': len(self.calls),
            'reads': len(report['reads']),
            'requested_bytes': sum(item[2] for item in self.plan[:len(self.calls)])})
        self.assertLessEqual(report['counts']['commands'], 24)
        self.assertLessEqual(report['counts']['requested_bytes'], 593424)
        for index, (read, item) in enumerate(zip(report['reads'], self.plan)):
            self.assertEqual(set(read), {'name', 'address', 'bytes', 'sha256', 'file'})
            self.assertEqual((read['name'], read['address'], read['bytes']), item)
            self.assertEqual(read['file'], f'{index:02d}-{item[0]}.bin')
            raw = (self.output / read['file']).read_bytes()
            self.assertEqual((len(raw), digest(raw)), (read['bytes'], read['sha256']))
        analysis = report['analysis']
        self.assertEqual(set(analysis), {'schema', 'flash', 'relocation', 'snapshots', 'coherence'})
        self.assertEqual(analysis['schema'], 'motor-fault-capture-analysis-v1')
        self.assertEqual(analysis['coherence'], 'UNPROVEN')
        self.assertEqual(set(analysis['flash']), {'before_loader', 'before_sketch',
                                               'after_loader', 'after_sketch'})
        self.assertTrue(all(type(value) is bool for value in analysis['flash'].values()))
        self.assertEqual(set(analysis['relocation']), {'before', 'after'})
        self.assertEqual(analysis['snapshots'], [r for r in report['reads']
                         if r['name'] in ('first.diagnostic', 'second.diagnostic')])
        if status == 'COLLECTED':
            self.assertIsNone(report['first_error'])
            self.assertEqual(report['postcheck_errors'], [])
        else:
            self.assertIsNotNone(report['first_error'])
        for error in report['postcheck_errors']:
            self.assertEqual(set(error), {'check', 'type', 'message'})
        self.assertEqual(json.loads((self.output / 'capture_result.json').read_text()), report)
        self.assertEqual((self.subject.BINDINGS, getattr(self.subject, 'OUTPUT_NAME', None)),
                         self.globals_before)
        return report

    def refused(self, **kwargs):
        with self.assertRaises(Exception):
            self.collect(**kwargs)
        self.assertEqual(self.calls, [])
        self.assertFalse(self.output.exists())

    @contextmanager
    def fresh(self):
        case = type(self)()
        case.setUp()
        try:
            yield case
        finally:
            case.doCleanups()

    def change_named(self, name, transform):
        self.raw_change = lambda i, raw, path: transform(raw) if self.plan[i][0] == name else raw

    def assert_no_snapshots(self, report):
        self.assertEqual(report['analysis']['snapshots'], [])
        self.assertFalse(any('diagnostic' in r['name'] for r in report['reads']))
        self.assertEqual(self.clock.sleeps, [])

    def test_real_traversal_one_two_three_nodes_exact_plan_and_counts(self):
        for count in (1, 2, 3):
            with self.subTest(nodes=count), self.fresh() as case:
                case.set_nodes(count)
                report = case.assert_report(case.collect(), 'COLLECTED')
                self.assertEqual(report['counts'], {'commands': 18 + 2 * count,
                    'reads': 18 + 2 * count, 'requested_bytes': 592248 + 392 * count})
                self.assertEqual(report['analysis']['relocation'],
                                 {'before': case.extension, 'after': case.extension})
                self.assertTrue(all(report['analysis']['flash'].values()))
                self.assertEqual(case.clock.sleeps, [2])
                self.assertEqual(report['wait'], {'requested_seconds': 2, 'before': 100.0, 'after': 102.0})
                self.assertEqual(stat.S_IMODE(case.output.stat().st_mode), 0o700)
                attempt = json.loads((case.output / 'capture_attempt.json').read_text())
                self.assertEqual(attempt['schema'], 'motor-fault-capture-attempt-v1')
                self.assertEqual(attempt['plan'], PLAN_SUMMARY)
                self.assertEqual((attempt['run_id'], attempt['source_sha256']), (RUN, SOURCE))
                self.assertEqual(len(list(case.output.glob('*.command.json'))), len(case.plan))
                self.assertEqual(len(list(case.output.glob('*.result.json'))), len(case.plan))

    def test_selected_sketch_can_be_first_middle_or_last(self):
        for selected in range(3):
            with self.subTest(selected=selected), self.fresh() as case:
                case.set_nodes(3, selected)
                report = case.assert_report(case.collect(), 'COLLECTED')
                self.assertEqual(report['analysis']['relocation']['before'], case.extension)

    def test_identity_run_and_schema_are_closed_before_ownership(self):
        class StringSubclass(str):
            pass
        for run in ('static-fcddbd8e-run01', 'motor-fault-8f592937-run02', '',
                    None, True, 1, StringSubclass(RUN)):
            with self.subTest(run=run):
                self.refused(run_id=run)
        for field, value in (('schema', 'fixed-static-capture-v1'), ('run_id', 'wrong'),
                ('source_sha256', 'a' * 64), ('uid', True), ('uid', 0),
                ('output', OUTPUT + '/child'), ('boot_id', self.bindings['boot_id'].upper())):
            changed = copy.deepcopy(self.bindings)
            changed[field] = value
            with self.subTest(field=field):
                self.refused(bindings=changed)

    def test_exact_binding_keys_roles_types_and_paths(self):
        candidates = []
        for key in self.bindings:
            bad = copy.deepcopy(self.bindings)
            del bad[key]
            candidates.append(bad)
        candidates.append(dict(self.bindings, extra=True))
        for role in PATHS:
            bad = copy.deepcopy(self.bindings)
            bad['files'][role]['path'] += '-substitute'
            candidates.append(bad)
        for key, value in (('bytes', True), ('bytes', 0), ('sha256', 'A' * 64),
                           ('sha256', 'a' * 63), ('extra', 1)):
            bad = copy.deepcopy(self.bindings)
            bad['files']['openocd'][key] = value
            candidates.append(bad)
        for role in ('missing', 'extra'):
            bad = copy.deepcopy(self.bindings)
            if role == 'missing':
                del bad['files']['swj']
            else:
                bad['files']['another'] = dict(bad['files']['swj'])
            candidates.append(bad)
        for bad in candidates:
            with self.subTest(bindings=bad):
                self.refused(bindings=bad)

    def test_all_five_pin_mismatches_and_wrong_sketch_extent_rejected(self):
        for role, path in PATHS.items():
            self.logical(path).write_bytes(b'!' + self.contents[role][1:])
            with self.subTest(role=role):
                self.refused()
            self.logical(path).write_bytes(self.contents[role])
        raw = SKETCH[:-1]
        self.logical(PATHS['sketch']).write_bytes(raw)
        self.bindings['files']['sketch'].update(bytes=len(raw), sha256=digest(raw))
        self.refused()

    def test_loader_reference_type_extent_hash_and_pin_shape(self):
        for raw in (bytearray(LOADER), memoryview(LOADER), LOADER[:-1], LOADER + b'!', b'!' + LOADER[1:]):
            with self.subTest(kind=type(raw), size=len(raw)):
                self.loader_image = lambda data: raw
                self.refused()
        self.loader_image = lambda data: LOADER
        for pin in ({'bytes': 263679, 'sha256': digest(LOADER)},
                    {'bytes': True, 'sha256': digest(LOADER)},
                    {'bytes': 263680}, dict(self.bindings['loader_image'], extra=1)):
            with self.subTest(pin=pin):
                self.refused(bindings=dict(self.bindings, loader_image=pin))

    def test_identity_and_process_conflicts_precede_directory_claim(self):
        original = copy.deepcopy(self.identity_value)
        for field, value in (('uid', 0), ('user', 'root'), ('machine', 'x86_64'),
                ('sysname', 'Darwin'), ('home', '/tmp'), ('boot_id', '0' * 36)):
            self.identity_value = dict(original, **{field: value})
            with self.subTest(field=field):
                self.refused()
        self.identity_value = original
        folder = self.logical('/proc/123')
        folder.mkdir()
        for name in ('openocd', 'remoteocd', 'arduino-cli'):
            (folder / 'comm').write_text(name + '\n')
            with self.subTest(name=name):
                self.refused()

    def test_symlink_input_and_output_parent_never_followed(self):
        target = self.logical(PATHS['config'])
        real = target.with_suffix('.real')
        target.rename(real)
        target.symlink_to(real)
        self.refused()
        target.unlink()
        real.rename(target)
        parent = self.output.parent
        moved = parent.with_name(parent.name + '-moved')
        parent.rename(moved)
        parent.symlink_to(moved, target_is_directory=True)
        self.refused()

    def test_existing_output_and_consumed_success_cannot_be_reused(self):
        self.assert_report(self.collect(), 'COLLECTED')
        saved = {p.name: p.read_bytes() for p in self.output.iterdir()}
        with self.assertRaises(Exception):
            self.collect()
        self.assertEqual(len(self.calls), 20)
        self.assertEqual({p.name: p.read_bytes() for p in self.output.iterdir()}, saved)
        with self.fresh() as case:
            case.output.mkdir()
            sentinel = case.output / 'user-owned'
            sentinel.write_bytes(b'preserve')
            with self.assertRaises(Exception):
                case.collect()
            self.assertEqual(case.calls, [])
            self.assertEqual(list(case.output.iterdir()), [sentinel])
            self.assertEqual(sentinel.read_bytes(), b'preserve')

    def test_detached_bindings_survive_caller_mutation(self):
        def mutate(index):
            if index == 0:
                self.bindings['files']['config']['sha256'] = '0' * 64
                self.bindings['output'] = '/tmp/redirect'
                self.bindings['run_id'] = 'another-run'
        self.after_execute = mutate
        self.assert_report(self.collect(), 'COLLECTED')
        self.assertFalse(self.logical('/tmp/redirect').exists())

    def test_legacy_collect_rejects_diagnostic_binding_and_identifier(self):
        decoder = SimpleNamespace(read_plan=mock.Mock(side_effect=AssertionError('legacy decoder touched')))
        for run in ('static-fcddbd8e-run01', RUN):
            with self.subTest(run=run), self.assertRaises(Exception):
                self.subject.collect(self.helper, decoder, self.loader_image,
                    fs_root=self.root, executor=self.execute, clock=self.clock,
                    sleeper=self.clock.sleep, bindings=self.bindings, run_id=run)
        self.assertEqual(self.calls, [])
        self.assertFalse(self.output.exists())
        self.assertEqual((self.subject.BINDINGS, getattr(self.subject, 'OUTPUT_NAME', None)), self.globals_before)

    def test_nested_diagnostic_instances_keep_separate_ownership(self):
        inner_reports = []
        with self.fresh() as inner:
            def nested(index):
                if index == 0:
                    inner_reports.append(inner.assert_report(inner.collect(), 'COLLECTED'))
            self.after_execute = nested
            self.assert_report(self.collect(), 'COLLECTED')
            self.assertEqual(len(inner.calls), 20)
            self.assertEqual(inner_reports[0]['run_id'], RUN)

    def test_all_before_flash_mismatches_prevent_sram_and_traversal(self):
        for name in ('before.loader.0', 'before.loader.4', 'before.sketch.0'):
            with self.subTest(name=name), self.fresh() as case:
                case.change_named(name, lambda raw: bytes([raw[0] ^ 1]) + raw[1:])
                with mock.patch.object(case.relocation, 'find_bss', wraps=case.relocation.find_bss) as walk:
                    report = case.assert_report(case.collect(), 'FAILED')
                walk.assert_not_called()
                case.assert_no_snapshots(report)
                self.assertLessEqual(len(case.calls), 6)
                self.assertTrue(all(r['address'] < 0x20000000 for r in report['reads']))
                self.assertFalse(report['analysis']['flash']['before_sketch' if 'sketch' in name else 'before_loader'])

    def test_traversal_admitted_only_after_full_flash_comparison(self):
        real = self.relocation.find_bss
        observed = []
        def checked(adapter, expected_size):
            self.assertIs(adapter.report.get('flash_identity_verified'), True)
            self.assertEqual(expected_size, 2632)
            self.assertGreaterEqual(len(self.calls), 6)
            observed.append(adapter)
            return real(adapter, expected_size)
        with mock.patch.object(self.relocation, 'find_bss', checked):
            self.assert_report(self.collect(), 'COLLECTED')
        self.assertEqual(len(observed), 2)

    def test_real_traversal_empty_tail_cycle_name_and_match_faults(self):
        cases = ('empty', 'tail', 'cycle', 'unterminated', 'missing-sketch', 'duplicate-sketch',
                 'wrong-bss-size', 'bss-outside', 'bss-crosses-end', 'bss-four-byte-only')
        for fault in cases:
            with self.subTest(fault=fault), self.fresh() as case:
                case.set_nodes(2)
                if fault == 'empty':
                    case.list_raw = bytes(8)
                elif fault == 'tail':
                    case.list_raw = struct.pack('<II', NODES[0], NODES[0])
                elif fault == 'cycle':
                    case.node_raw[1] = patch_word(case.node_raw[1], 0, NODES[0])
                elif fault == 'unterminated':
                    case.node_raw[0] = case.node_raw[0][:4] + b'x' * 16 + case.node_raw[0][20:]
                elif fault == 'missing-sketch':
                    case.node_raw[1] = case.node_raw[1][:4] + b'helper\0' + case.node_raw[1][11:]
                elif fault == 'duplicate-sketch':
                    case.node_raw[0] = case.node_raw[0][:4] + b'sketch\0' + case.node_raw[0][11:]
                else:
                    offset, value = {'wrong-bss-size': (92, 2631), 'bss-outside': (32, 0x10000000),
                        'bss-crosses-end': (32, 0x200bfff8), 'bss-four-byte-only': (32, BSS + 4)}[fault]
                    case.node_raw[1] = patch_word(case.node_raw[1], offset, value)
                report = case.assert_report(case.collect(), 'FAILED')
                case.assert_no_snapshots(report)
                self.assertIsNone(report['analysis']['relocation']['before'])

    def test_bad_node_address_is_rejected_without_launch(self):
        for address in (NODES[0] + 1, 0x10000000, 0x200bfffc, 0xffffffff):
            with self.subTest(address=address), self.fresh() as case:
                case.list_raw = struct.pack('<II', address, address)
                report = case.assert_report(case.collect(), 'FAILED')
                self.assertEqual(len(case.calls), 7)
                case.assert_no_snapshots(report)

    def test_real_fourth_node_never_requested(self):
        self.set_nodes(3)
        self.node_raw[2] = patch_word(self.node_raw[2], 0, 0x20002600)
        report = self.assert_report(self.collect(), 'FAILED')
        self.assertEqual(len(self.calls), 10)
        self.assert_no_snapshots(report)

    def test_list_confirmation_change_fails_before_snapshot(self):
        self.change_named('before.llext-list-confirm', lambda raw: patch_word(raw, 4, 0))
        report = self.assert_report(self.collect(), 'FAILED')
        self.assertEqual(len(self.calls), 9)
        self.assert_no_snapshots(report)

    def test_full_after_node_bytes_detect_change_outside_selected_metadata(self):
        for index, byte in ((0, 195), (1, 120), (2, 194)):
            with self.subTest(node=index, byte=byte), self.fresh() as case:
                case.set_nodes(3)
                def change(raw):
                    return raw[:byte] + bytes([raw[byte] ^ 1]) + raw[byte + 1:]
                case.change_named(f'after.node-{index + 1}', change)
                report = case.assert_report(case.collect(), 'FAILED')
                self.assertEqual(len(report['analysis']['snapshots']), 2)
                self.assertFalse(any(r['name'].startswith(('after.loader.', 'after.sketch.'))
                                     for r in report['reads']))

    def test_after_relocation_base_and_list_changes_retain_both_raw_snapshots(self):
        for name, offset, value in (('after.node-1', 32, BSS + 8),
                                   ('after.llext-list', 4, 0),
                                   ('after.llext-list-confirm', 4, 0)):
            with self.subTest(name=name), self.fresh() as case:
                case.change_named(name, lambda raw: patch_word(raw, offset, value))
                report = case.assert_report(case.collect(), 'FAILED')
                self.assertEqual(len(report['analysis']['snapshots']), 2)
                self.assertFalse(report['analysis']['flash']['after_loader'])
                self.assertFalse(report['analysis']['flash']['after_sketch'])

    def test_after_flash_mismatches_fail_and_keep_both_snapshots(self):
        for name in ('after.sketch.0', 'after.loader.0', 'after.loader.4'):
            with self.subTest(name=name), self.fresh() as case:
                case.change_named(name, lambda raw: bytes([raw[0] ^ 1]) + raw[1:])
                report = case.assert_report(case.collect(), 'FAILED')
                self.assertEqual(len(report['analysis']['snapshots']), 2)
                flag = 'after_sketch' if 'sketch' in name else 'after_loader'
                self.assertFalse(report['analysis']['flash'][flag])
                self.assertEqual(report['analysis']['relocation'],
                                 {'before': case.extension, 'after': case.extension})

    def test_adapter_rejects_arbitrary_names_types_regions_sizes_and_order(self):
        class StringSubclass(str):
            pass
        class IntSubclass(int):
            pass
        attempts = [('arbitrary', LIST, 8), ('llext-list', True, 8),
            ('llext-list', LIST, True), ('llext-list', LIST, 9),
            ('llext-list', LIST + 4, 8), ('llext-list', 0x40000000, 8),
            ('node-1', NODES[0], 196), ('node-4', NODES[0], 196),
            ('first.diagnostic', BSS, 2592), ('llext-list', LIST, 65536),
            ('llext-list', LIST, 593425), (b'llext-list', LIST, 8),
            (StringSubclass('llext-list'), LIST, 8),
            ('llext-list', IntSubclass(LIST), 8), ('llext-list', LIST, IntSubclass(8))]
        for request in attempts:
            with self.subTest(request=request), self.fresh() as case:
                def malicious(adapter, expected_size):
                    return adapter.read(*request)
                with mock.patch.object(case.relocation, 'find_bss', malicious):
                    report = case.assert_report(case.collect(), 'FAILED')
                self.assertEqual(len(case.calls), 6)
                case.assert_no_snapshots(report)

    def test_adapter_repeated_list_and_unbounded_failed_requests_cannot_launch(self):
        def malicious(adapter, expected_size):
            adapter.read('llext-list', LIST, 8)
            for index in range(100):
                try:
                    adapter.read('llext-list', LIST, 8 if index % 2 else 593425)
                except Exception:
                    pass
            raise ValueError('malicious traversal exhausted')
        with mock.patch.object(self.relocation, 'find_bss', malicious):
            report = self.assert_report(self.collect(), 'FAILED')
        self.assertEqual(len(self.calls), 7)
        self.assertEqual(report['counts']['requested_bytes'], 293524)

    def test_failed_launch_is_counted_at_final_read_ceiling(self):
        self.set_nodes(3)
        def fail_last(index):
            if index == 23:
                self.process_result = dict(SUCCESS, returncode=1)
        self.after_execute = fail_last
        report = self.assert_report(self.collect(), 'FAILED')
        self.assertEqual(report['counts']['commands'], 24)
        self.assertEqual(report['counts']['requested_bytes'], 593424)
        self.assertEqual(len(report['analysis']['snapshots']), 2)
        self.assertFalse(report['analysis']['flash']['after_loader'])

    def test_pause_happens_after_first_snapshot_and_before_second(self):
        def sleep(seconds):
            self.assertEqual(self.plan[len(self.calls) - 1][0], 'first.diagnostic')
            self.assertEqual(self.plan[len(self.calls)][0], 'second.diagnostic')
            self.clock.sleep(seconds)
        self.assert_report(self.collect(sleeper=sleep), 'COLLECTED')

    def test_short_throwing_or_deadline_pause_preserves_one_snapshot(self):
        for mode in ('short', 'throw', 'deadline'):
            with self.subTest(mode=mode), self.fresh() as case:
                def sleep(seconds):
                    if mode == 'throw':
                        raise RuntimeError('controlled pause failure')
                    case.clock.now += 1.999 if mode == 'short' else 600.0
                report = case.assert_report(case.collect(sleeper=sleep), 'FAILED')
                self.assertEqual(len(case.calls), 10)
                self.assertEqual(len(report['analysis']['snapshots']), 1)
                self.assertIsNone(report['analysis']['relocation']['after'])

    def test_deadline_shortens_timeout_and_blocks_next_launch(self):
        self.after_execute = lambda index: setattr(self.clock, 'now', 680.0 if index == 0 else 700.0)
        report = self.assert_report(self.collect(), 'FAILED')
        self.assertEqual([timeout for argv, timeout in self.calls], [30.0, 20.0])
        self.assert_no_snapshots(report)

    def test_bad_process_results_and_exceptions_abort_without_retry(self):
        results = [dict(SUCCESS, returncode=1), dict(SUCCESS, timed_out=True),
            dict(SUCCESS, reaped=False), dict(SUCCESS, returncode=False),
            dict(SUCCESS, returncode=None), dict(SUCCESS, timed_out=0),
            dict(SUCCESS, reaped=1), dict(SUCCESS, extra=1), {}, None]
        for result in results:
            with self.subTest(result=result), self.fresh() as case:
                case.process_result = result
                report = case.assert_report(case.collect(), 'FAILED')
                self.assertEqual(len(case.calls), 1)
                self.assertEqual(report['counts']['reads'], 0)
        self.execute_error = RuntimeError('controlled launch failure')
        report = self.assert_report(self.collect(), 'FAILED')
        self.assertEqual(report['first_error']['message'], 'controlled launch failure')
        self.assertEqual(len(self.calls), 1)
        self.assertTrue((self.output / '00.result.json').is_file())

    def test_missing_short_oversize_symlink_raw_retains_failure_evidence(self):
        for mode in ('missing', 'short', 'oversize', 'symlink'):
            with self.subTest(mode=mode), self.fresh() as case:
                def change(index, raw, target):
                    if mode == 'missing':
                        return None
                    if mode == 'short':
                        return raw[:-1]
                    if mode == 'oversize':
                        return raw + b'!'
                    real = target.with_suffix('.real')
                    real.write_bytes(raw)
                    target.symlink_to(real)
                    return None
                case.raw_change = change
                report = case.assert_report(case.collect(), 'FAILED')
                self.assertEqual((len(case.calls), report['counts']['reads']), (1, 0))
                self.assertEqual((case.output / '00.stderr').read_bytes(), case.stderr)
                if mode != 'missing':
                    self.assertTrue((case.output / '00-before.loader.0.bin').exists())

    def test_stream_ceiling_stops_at_first_command_and_keeps_raw(self):
        for which in ('stdout', 'stderr'):
            with self.subTest(which=which), self.fresh() as case:
                setattr(case, which, bytes(1048576))
                report = case.assert_report(case.collect(), 'FAILED')
                self.assertEqual(len(case.calls), 1)
                self.assertEqual((case.output / ('00.' + which)).stat().st_size, 1048576)
                self.assertTrue((case.output / '00-before.loader.0.bin').exists())

    def test_independent_final_identity_and_all_pins_after_primary_error(self):
        def execute(*args):
            self.check_launch(*args)
            for path in PATHS.values():
                self.logical(path).write_bytes(b'changed')
            self.identity_value['boot_id'] = '00000000-0000-0000-0000-000000000000'
            raise RuntimeError('primary failure survives')
        report = self.assert_report(self.collect(executor=execute), 'FAILED')
        self.assertEqual(report['first_error']['message'], 'primary failure survives')
        self.assertGreaterEqual(len(report['postcheck_errors']), 6)
        self.assertGreaterEqual(len(self.identity_calls), 2)
        for role in PATHS:
            self.assertEqual(sum(key == role for key, limit in self.pin_checks), 2)

    def test_complete_capture_with_final_pin_drift_is_failed(self):
        def drift(index):
            if index == len(self.plan) - 1:
                self.logical(PATHS['config']).write_bytes(b'changed')
        self.after_execute = drift
        report = self.assert_report(self.collect(), 'FAILED')
        self.assertEqual(len(report['reads']), 20)
        self.assertEqual(len(report['analysis']['snapshots']), 2)
        self.assertTrue(report['postcheck_errors'])

    def test_output_replacement_preserves_original_owned_receipts(self):
        original = self.output
        moved = original.with_name(original.name + '-moved')
        def replace(index):
            if index == 0:
                original.rename(moved)
                original.mkdir()
                (original / 'sentinel').write_bytes(b'preserve replacement')
                self.output = moved
        self.after_execute = replace
        report = self.collect()
        self.assertEqual(report['status'], 'FAILED')
        self.assertEqual(len(self.calls), 1)
        self.assertTrue(report['postcheck_errors'])
        self.assertEqual(json.loads((moved / 'capture_result.json').read_text()), report)
        self.assertEqual([p.name for p in original.iterdir()], ['sentinel'])
        self.assertEqual((original / 'sentinel').read_bytes(), b'preserve replacement')

    def test_receipts_synced_before_launch_and_claim_failure_consumes_owner(self):
        synced = []
        original = os.fsync
        def fsync(fd):
            synced.append(os.readlink('/proc/self/fd/' + str(fd)))
            return original(fd)
        def execute(*args):
            self.assertIn(str(self.output / 'capture_attempt.json'), synced)
            self.assertIn(str(self.output / f'{len(self.calls):02d}.command.json'), synced)
            return self.execute(*args)
        with mock.patch.object(os, 'fsync', fsync):
            self.assert_report(self.collect(executor=execute), 'COLLECTED')
        with self.fresh() as case:
            failed = []
            def broken(fd):
                if not failed and os.readlink('/proc/self/fd/' + str(fd)).endswith('/capture_attempt.json'):
                    failed.append(True)
                    raise OSError('claim fsync failed')
                return original(fd)
            with mock.patch.object(os, 'fsync', broken):
                report = case.assert_report(case.collect(), 'FAILED')
            self.assertEqual(case.calls, [])
            self.assertEqual(report['first_error']['message'], 'claim fsync failed')
            with self.assertRaises(Exception):
                case.collect()

    def test_clock_error_cannot_replace_primary_failure(self):
        broken = []
        def clock():
            if broken:
                raise RuntimeError('later clock failure')
            return self.clock.now
        def execute(*args):
            self.check_launch(*args)
            broken.append(True)
            raise OSError('primary execution failure')
        report = self.assert_report(self.collect(executor=execute, clock=clock), 'FAILED')
        self.assertEqual(report['first_error']['message'], 'primary execution failure')
        self.assertEqual(report['finished_monotonic'], 100.0)
        self.assertIn('later clock failure', json.dumps(report) + (self.output / '00.result.json').read_text())

    def test_default_wrapper_uses_passive_environment_group_limits_and_reap(self):
        import resource
        for mode in ('success', 'timeout', 'spawn-error'):
            with self.subTest(mode=mode), self.fresh() as case:
                waits, kills, limits = [], [], []
                class Process:
                    pid = 654321
                    returncode = None
                    def wait(self, timeout):
                        waits.append(timeout)
                        if mode == 'timeout' and len(waits) == 1:
                            raise subprocess.TimeoutExpired('controlled-openocd', timeout)
                        self.returncode = -signal.SIGKILL if mode == 'timeout' else 0
                        return self.returncode
                def popen(argv, **kwargs):
                    self.assertEqual(kwargs.get('cwd'), '/home/arduino')
                    self.assertEqual(kwargs.get('env'), ENV)
                    self.assertIs(kwargs.get('start_new_session'), True)
                    self.assertEqual(kwargs.get('stdin'), subprocess.DEVNULL)
                    self.assertFalse(kwargs.get('shell', False))
                    kwargs['preexec_fn']()
                    paths = []
                    for field in ('stdout', 'stderr'):
                        stream = kwargs[field]
                        fd = stream if isinstance(stream, int) else stream.fileno()
                        paths.append(os.readlink('/proc/self/fd/' + str(fd)))
                    index, target = case.check_launch(argv, *paths, 30.0)
                    if mode == 'spawn-error':
                        raise OSError('controlled spawn error')
                    target.write_bytes(case.bytes_for(case.plan[index]))
                    return Process()
                with mock.patch.object(subprocess, 'Popen', popen), \
                     mock.patch.object(os, 'killpg', lambda pid, sig: kills.append((pid, sig))), \
                     mock.patch.object(os, 'getpgid', lambda pid: pid), \
                     mock.patch.object(resource, 'setrlimit', lambda kind, value: limits.append((kind, value))):
                    report = case.assert_report(case.collect(executor=None),
                                                'COLLECTED' if mode == 'success' else 'FAILED')
                self.assertEqual(limits, [(resource.RLIMIT_FSIZE, (1048576, 1048576))] * len(case.calls))
                if mode == 'success':
                    self.assertEqual(waits, [30.0] * 20)
                    self.assertEqual(kills, [])
                elif mode == 'timeout':
                    self.assertIn((654321, signal.SIGKILL), kills)
                    self.assertGreaterEqual(len(waits), 2)
                    self.assertEqual(len(case.calls), 1)
                else:
                    self.assertEqual(len(case.calls), 1)

    def test_matching_and_different_snapshots_never_claim_coherence(self):
        for same in (False, True):
            with self.subTest(same=same), self.fresh() as case:
                if same:
                    case.samples['second.diagnostic'] = case.samples['first.diagnostic']
                report = case.assert_report(case.collect(), 'COLLECTED')
                self.assertEqual(report['analysis']['coherence'], 'UNPROVEN')
                self.assertEqual(set(report['analysis']), {'schema', 'flash', 'relocation', 'snapshots', 'coherence'})

    def test_offline_decoder_valid_fault_and_malformed_raw_keep_capture_unchanged(self):
        # Import only at test execution; the author used D174 contract and D173 ABI.
        with mock.patch.object(sys, 'path', [str(ROOT / 'tools'), *sys.path]):
            decoder = load(ROOT / 'tools/motor_fault_decode.py', 'd176_offline_decoder')
        for phase, malformed in ((0, False), (4, False), (255, True)):
            with self.subTest(phase=phase), self.fresh() as case:
                case.samples['first.diagnostic'] = snapshot(phase)
                case.samples['second.diagnostic'] = snapshot(phase)
                with mock.patch.object(decoder, 'decode_snapshot', wraps=decoder.decode_snapshot) as decode:
                    report = case.assert_report(case.collect(), 'COLLECTED')
                    decode.assert_not_called()
                    saved = {p.name: p.read_bytes() for p in case.output.iterdir()}
                    for item in report['analysis']['snapshots']:
                        raw = (case.output / item['file']).read_bytes()
                        if malformed:
                            with self.assertRaises(ValueError):
                                decode(raw)
                        else:
                            parsed = decode(raw)
                            self.assertEqual(parsed['status'], 'DECODED')
                            self.assertEqual(parsed['coherence'], 'UNPROVEN')
                            self.assertEqual(parsed['reported_phase'], 'FAULT' if phase == 4 else 'NOT_STARTED')
                self.assertEqual({p.name: p.read_bytes() for p in case.output.iterdir()}, saved)
                self.assertEqual(report['status'], 'COLLECTED')


if __name__ == '__main__':
    unittest.main(verbosity=2)
