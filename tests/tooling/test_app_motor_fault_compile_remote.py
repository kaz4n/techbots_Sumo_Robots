# Tests D188 remote artifact observation against its independent public contract.
# Uses synthetic ELF packets, actual pinned source snapshots and owned RAM files.
# Freeze before Python -B execution; no compiler, transport or hardware is used.
import copy
from contextlib import contextmanager, ExitStack
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import types
import unittest
from unittest import mock
try:
    import pwd
except ImportError:
    pwd = None


ROOT = Path(__file__).resolve().parents[2]
REMOTE = '/home/arduino/sumox26_codex_build/app-motor-fault-static01'
BUILD, ARTIFACTS = REMOTE + '/build', REMOTE + '/artifacts'
CORE = '/home/arduino/.arduino15/packages/arduino/hardware/zephyr/1.0.0'
LOADER = CORE + '/firmwares/zephyr-arduino_uno_q_stm32u585xx.elf'
TLS = CORE + '/variants/arduino_uno_q_stm32u585xx/tls-syms.S'
PROJECT = 'app_motor_fault.ino'
FQBN = 'arduino:zephyr:unoq:link_mode=static'
FLAGS = '-DMATCH=0 -DMOTORS_ALLOWED=0 -DSUMOX_MOTOR_FAULT_PROBE=1'
RAW = 'state/analysis/P7_static_link_probe_raw/'
BUNDLE = {
    'helper': (RAW + 'static_remote.py', '8ba9b190c38e728013a383348c60c287b0366607f65f703161cf7f2e142d36f8'),
    'adapter': ('tools/app_motor_fault_static_policy.py', '3e5d49e4a70c0cf6197e26b1ba5ce2b7e07601bf5d9250ba430f90d1f9eab270'),
    'extension': (RAW + 'static_native_artifacts.py', 'cd52a29a32b8ae1da4bea51dd55d9011386dd4be0ca537195bb124d13031d6c0'),
    'base': (RAW + 'static_artifacts.py', 'd30372dd4b8fb8c2661d00affc4a215cc88e3f62511995ff6303827bed4b7368'),
}
LOADER_SHA = '39d4a4fd47241663323f6e04f94dd8f5a9f9ad6582cf1df37f9709b74026adcd'
TLS_SHA = '68bb147615813666d528b9bd650e02fb8e240f0db841939e8460d7a52fd2ee70'
SUFFIXES = ('.elf', '_debug.elf', '_temp.elf', '.bin', '.bin-zsk.bin', '.elf-zsk.bin', '.map')
LIMITS = {'build/' + PROJECT + s: (786416 if s == '.bin' else
          786432 if s == '.bin-zsk.bin' else 16777216) for s in SUFFIXES}
LIMITS['artifacts/' + PROJECT + '.bin-zsk.bin'] = 786432
ERROR_KEYS = {'type', 'message'}
REPLY_KEYS = {'schema', 'status', 'build_path', 'artifacts_path', 'files', 'loader',
              'tls_source', 'layout', 'postchecks', 'first_error'}
DEFAULT_BUNDLE = object()


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def load(path, name):
    module = types.ModuleType(name)
    module.__file__ = str(path)
    with mock.patch.dict(sys.modules, {name: module}):
        exec(compile(path.read_bytes(), str(path), 'exec'), module.__dict__)
    return module


def checked_bundle():
    result = {name: (ROOT / path).read_bytes() for name, (path, _) in BUNDLE.items()}
    for name, (_, expected) in BUNDLE.items():
        if digest(result[name]) != expected:
            raise AssertionError('Changed historical fixture: ' + name)
    return result


def artifact_packet():
    base = load(ROOT / 'state/analysis/P7_static_artifact_test_draft/synthetic_elf.py',
                'd188_synthetic_elf')
    with mock.patch.dict(sys.modules, {'synthetic_elf': base}):
        native = load(ROOT / 'state/analysis/P7_static_native_tls_test_draft/synthetic_native_elf.py',
                      'd188_synthetic_native_elf')
    original = native.packet()
    return {PROJECT + suffix: original['app.ino' + suffix] for suffix in SUFFIXES}


def expected_layout(packet):
    flash, ram, end = 0x08100010, 0x20013890, 0x20013c00
    fields = ('name', 'type', 'flags', 'address', 'size', 'alignment', 'load_address')
    rows = [('.text', 1, 6, flash, 8, 4, flash), ('.rodata', 1, 2, flash + 16, 8, 4, flash + 16),
            ('.data', 1, 3, ram, 8, 4, flash + 32), ('.bss', 8, 3, ram + 8, end - ram - 8, 8, None)]
    aliases = {PROJECT + s: 'app.ino' + s for s in SUFFIXES}
    tls = {'_TLS_MODULE_BASE_': 8, '_rand_next': 8, 'z_tls_current': 16,
           'errno': 20, '_strtok_last': 24, '_localtime_buf': 28}
    report = dict(status='STATIC_NATIVE_TLS_LAYOUT_PACKAGE_PASS', entry=flash | 1,
        flash=dict(start=flash, end=flash + 40, remaining=0x081c0000 - flash - 40),
        ram=dict(start=ram, end=end, remaining=0x20053890 - end),
        data_copy=dict(source=flash + 32, destination=ram, bytes=8),
        bss_zero=dict(start=ram + 8, end=ram + 24, bytes=16),
        sections=[dict(zip(fields, row)) for row in rows], weak_undefined=['optional_weak_hook'],
        artifacts={aliases[name]: dict(bytes=len(raw), sha256=digest(raw)) for name, raw in packet.items()},
        native_tls=dict(source_sha256=TLS_SHA, loader_sha256=LOADER_SHA,
            symbols=[dict(name=name, value=value, size=0, bind=1, type=6, other=0, section=0xfff1)
                     for name, value in sorted(tls.items())]))
    return dict(status='STATIC_APP_MOTOR_FAULT_LAYOUT_PACKAGE_PASS', project=PROJECT,
        fqbn=FQBN, flags=FLAGS, artifact_aliases=aliases,
        artifact_sha256={name: digest(raw) for name, raw in packet.items()}, validator_report=report)


def file_record(raw, index):
    return dict(state='regular', identity=dict(device=3, inode=index, bytes=len(raw),
                                             mtime_ns=100, ctime_ns=100), sha256=digest(raw))


def synthetic_reply(packet=None):
    packet = artifact_packet() if packet is None else packet
    records = {'build/' + name: file_record(raw, i + 1) for i, (name, raw) in enumerate(packet.items())}
    records['artifacts/' + PROJECT + '.bin-zsk.bin'] = file_record(packet[PROJECT + '.bin-zsk.bin'], 20)
    loader = file_record(b'x', 21)
    loader['sha256'], loader['identity']['bytes'] = LOADER_SHA, 2303728
    tls = file_record(b'x', 22)
    tls['sha256'], tls['identity']['bytes'] = TLS_SHA, 977
    return dict(schema='app-motor-fault-static-artifacts-v1', status='ARTIFACTS_CHECKED',
        build_path=BUILD, artifacts_path=ARTIFACTS, files=records, loader=loader,
        tls_source=tls, layout=expected_layout(packet), first_error=None,
        postchecks=[dict(name=name, status='PASS', error=None) for name in ('loader', 'tls_source', 'files')])


@unittest.skipUnless(sys.platform == 'linux', 'Real nofollow descriptor fixtures require Linux')
class RemoteArtifactContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not sys.dont_write_bytecode or os.geteuid() == 0:
            raise RuntimeError('Run Python -B using the actual nonroot WSL account')
        cls.bundle = checked_bundle()
        cls.packet = artifact_packet()
        cls.loader_raw = (ROOT / 'state/analysis/P2_ui_adc_probe_raw/root_capture_inputs/zephyr-arduino_uno_q_stm32u585xx.elf').read_bytes()
        cls.tls_raw = (ROOT / 'state/analysis/P7_static_tls_raw/observed/tls-syms.S').read_bytes()
        if digest(cls.loader_raw) != LOADER_SHA or digest(cls.tls_raw) != TLS_SHA:
            raise AssertionError('Installed-file evidence fixture changed')
        cls.subject = load(ROOT / 'tools/app_motor_fault_compile_remote.py', 'd188_remote_subject')

    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix='sumox-d188-remote-', dir='/dev/shm')
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        for name, raw in self.packet.items():
            self.write(BUILD + '/' + name, raw)
        self.write(ARTIFACTS + '/' + PROJECT + '.bin-zsk.bin', self.packet[PROJECT + '.bin-zsk.bin'])
        self.write(LOADER, self.loader_raw)
        self.write(TLS, self.tls_raw)

    def logical(self, path):
        return self.root / path.lstrip('/')

    def write(self, path, raw):
        target = self.logical(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
        return target

    @contextmanager
    def isolated(self):
        account = pwd.struct_passwd(('arduino', 'x', os.geteuid(), os.getegid(),
                                    'synthetic', '/home/arduino', '/bin/sh'))
        with ExitStack() as stack:
            stack.enter_context(mock.patch.object(pwd, 'getpwuid', return_value=account))
            for owner, names in ((subprocess, ('Popen', 'run', 'call', 'check_call', 'check_output')),
                                 (socket, ('socket', 'create_connection'))):
                for name in names:
                    stack.enter_context(mock.patch.object(owner, name,
                        side_effect=AssertionError('No external operation: ' + name)))
            yield

    def inspect(self, bundle=DEFAULT_BUNDLE, build=BUILD, artifacts=ARTIFACTS):
        with self.isolated():
            return self.subject.inspect_artifacts(build, artifacts,
                self.bundle if bundle is DEFAULT_BUNDLE else bundle, fs_root=self.root)

    def failure(self, result):
        self.assertEqual(set(result), REPLY_KEYS)
        self.assertEqual(result['status'], 'FAILED')
        self.assertEqual(set(result['first_error']), ERROR_KEYS)
        self.assertTrue(result['first_error']['message'])
        self.assertEqual([r['name'] for r in result['postchecks']], ['loader', 'tls_source', 'files'])
        for row in result['postchecks']:
            self.assertEqual(set(row), {'name', 'status', 'error'})
            self.assertIn(row['status'], ('PASS', 'FAILED'))
            self.assertIsNone(row['error']) if row['status'] == 'PASS' else self.assertEqual(set(row['error']), ERROR_KEYS)

    def test_exact_success_real_validation_and_all_eight_identities(self):
        before = {p: p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        result = self.inspect()
        self.assertEqual(set(result), REPLY_KEYS)
        self.assertEqual(result['status'], 'ARTIFACTS_CHECKED')
        self.assertEqual(result['layout'], expected_layout(self.packet))
        self.assertEqual(set(result['files']), set(LIMITS))
        self.assertEqual(result['postchecks'], synthetic_reply(self.packet)['postchecks'])
        self.assertIsNone(result['first_error'])
        for selector, record in result['files'].items():
            path = self.logical(REMOTE + '/' + selector)
            info = path.stat()
            self.assertEqual(record, dict(state='regular', sha256=digest(path.read_bytes()),
                identity=dict(device=info.st_dev, inode=info.st_ino, bytes=info.st_size,
                              mtime_ns=info.st_mtime_ns, ctime_ns=info.st_ctime_ns)))
        self.assertEqual(result['loader']['sha256'], LOADER_SHA)
        self.assertEqual(result['tls_source']['sha256'], TLS_SHA)
        self.assertEqual(before, {p: p.read_bytes() for p in self.root.rglob('*') if p.is_file()})
        json.dumps(result, allow_nan=False)

    def test_invalid_bundle_names_types_and_each_pin_fail(self):
        bad = [None, [], {}, dict(self.bundle, extra=b'x')]
        for key in self.bundle:
            missing = dict(self.bundle); missing.pop(key); bad.append(missing)
            for value in (b'', self.bundle[key] + b'\n', bytearray(self.bundle[key]), None):
                bad.append(dict(self.bundle, **{key: value}))
        for bundle in bad:
            with self.subTest(keys=list(bundle) if isinstance(bundle, dict) else repr(bundle)):
                try:
                    result = self.inspect(bundle)
                except (ValueError, TypeError):
                    continue
                self.failure(result)

    def test_only_exact_fixed_build_and_export_paths_are_allowed(self):
        for wrong in ('/tmp/arbitrary', BUILD + '/', BUILD + '/..', '', None, 7,
                      BUILD.replace('static01', 'static02')):
            for position in ('build', 'artifacts'):
                with self.subTest(position=position, path=wrong), self.assertRaises((ValueError, TypeError)):
                    self.inspect(**{position: wrong})

    def test_each_artifact_missing_empty_and_oversize_fails(self):
        for selector, limit in LIMITS.items():
            path = self.logical(REMOTE + '/' + selector)
            raw = path.read_bytes()
            for state in ('missing', 'empty', 'oversize'):
                with self.subTest(file=selector, state=state):
                    path.unlink()
                    if state != 'missing':
                        with path.open('wb') as output:
                            output.truncate(0 if state == 'empty' else limit + 1)
                    self.failure(self.inspect())
                    path.write_bytes(raw)

    def test_each_file_symlink_and_fifo_fail_without_blocking(self):
        for selector in LIMITS:
            path = self.logical(REMOTE + '/' + selector)
            raw = path.read_bytes(); path.unlink()
            for kind in ('link', 'fifo'):
                with self.subTest(file=selector, kind=kind):
                    path.symlink_to(self.logical(TLS)) if kind == 'link' else os.mkfifo(path)
                    self.failure(self.inspect())
                    path.unlink()
            path.write_bytes(raw)

    def test_export_equal_length_byte_change_fails(self):
        path = self.logical(ARTIFACTS + '/' + PROJECT + '.bin-zsk.bin')
        raw = path.read_bytes()
        path.write_bytes(raw[:-1] + bytes([raw[-1] ^ 1]))
        self.failure(self.inspect())

    def test_actual_native_validator_rejects_corrupt_elf_despite_coherent_export(self):
        path = self.logical(BUILD + '/' + PROJECT + '.elf')
        raw = path.read_bytes(); path.write_bytes(b'BAD!' + raw[4:])
        result = self.inspect()
        self.failure(result)
        self.assertNotEqual(result['layout'], expected_layout(self.packet))

    def test_loader_and_tls_missing_empty_changed_oversize_or_link_fail(self):
        for logical, limit in ((LOADER, 16777216), (TLS, 65536)):
            path = self.logical(logical); raw = path.read_bytes()
            for kind in ('missing', 'empty', 'changed', 'oversize', 'link'):
                path.unlink()
                if kind == 'link': path.symlink_to(self.logical(BUILD + '/' + PROJECT + '.elf'))
                elif kind == 'changed': path.write_bytes(raw[:-1] + bytes([raw[-1] ^ 1]))
                elif kind != 'missing':
                    with path.open('wb') as output: output.truncate(0 if kind == 'empty' else limit + 1)
                with self.subTest(path=logical, kind=kind): self.failure(self.inspect())
                if path.exists() or path.is_symlink(): path.unlink()
                path.write_bytes(raw)

    @contextmanager
    def after_validation(self, mutate):
        previous, fired = sys.getprofile(), []
        def profile(frame, event, result):
            if not fired and event == 'return' and frame.f_code.co_name == 'validate_artifacts' \
                    and type(result) is dict and result.get('status') == 'STATIC_APP_MOTOR_FAULT_LAYOUT_PACKAGE_PASS':
                fired.append(True); mutate()
        sys.setprofile(profile)
        try: yield fired
        finally: sys.setprofile(previous)

    def test_final_loader_tls_and_artifact_drift_checks_are_independent(self):
        def mutate():
            for logical in (LOADER, TLS, BUILD + '/' + PROJECT + '.map'):
                self.logical(logical).write_bytes(b'changed after valid layout')
        with self.after_validation(mutate) as fired:
            result = self.inspect()
        self.assertEqual(fired, [True], 'Actual D187 adapter validation must run')
        self.failure(result)
        self.assertEqual([r['status'] for r in result['postchecks']], ['FAILED'] * 3)
        self.assertEqual(result['first_error'], result['postchecks'][0]['error'])

    def test_final_inode_replacement_fails_even_with_unchanged_bytes(self):
        path = self.logical(BUILD + '/' + PROJECT + '.map')
        def mutate():
            raw = path.read_bytes(); path.unlink(); path.write_bytes(raw)
        with self.after_validation(mutate) as fired: result = self.inspect()
        self.assertTrue(fired)
        self.failure(result)
        self.assertEqual(result['postchecks'][2]['status'], 'FAILED')

    def test_first_initial_error_survives_independent_final_errors(self):
        self.logical(BUILD + '/' + PROJECT + '.elf').unlink()
        self.logical(LOADER).unlink()
        self.logical(TLS).unlink()
        result = self.inspect()
        self.failure(result)
        self.assertEqual([r['status'] for r in result['postchecks']], ['FAILED'] * 3)

    def test_linked_build_artifacts_and_installed_ancestors_fail(self):
        for logical in (BUILD, ARTIFACTS, CORE + '/firmwares', CORE + '/variants'):
            path = self.logical(logical); parked = path.with_name(path.name + '-parked')
            path.rename(parked); path.symlink_to(parked, target_is_directory=True)
            with self.subTest(path=logical): self.failure(self.inspect())
            path.unlink(); parked.rename(path)

    def test_unavailable_fixture_root_has_three_failed_checks_without_cwd_reads(self):
        original, attempted = os.open, []
        def opening(path, flags, *args, **kwargs):
            attempted.append((os.fspath(path), kwargs.get('dir_fd')))
            if Path(path) == self.root:
                raise PermissionError('controlled root open denied')
            raise AssertionError('Read attempted after failed root open: ' + str(path))
        with self.isolated(), mock.patch.object(os, 'open', opening):
            result = self.subject.inspect_artifacts(BUILD, ARTIFACTS, self.bundle, fs_root=self.root)
        self.failure(result)
        self.assertEqual(len(attempted), 1)
        self.assertEqual([r['status'] for r in result['postchecks']], ['FAILED'] * 3)
        self.assertEqual(result['first_error']['type'], 'PermissionError')

    def test_file_replaced_during_descriptor_read_fails_as_unstable(self):
        path = self.logical(BUILD + '/' + PROJECT + '.map')
        old = path.stat(); raw = path.read_bytes(); original = os.fstat; fired = []
        def fstat(fd):
            info = original(fd)
            if not fired and (info.st_dev, info.st_ino) == (old.st_dev, old.st_ino):
                fired.append(True); path.unlink(); path.write_bytes(raw)
            return info
        with mock.patch.object(os, 'fstat', fstat): result = self.inspect()
        self.assertTrue(fired)
        self.failure(result)
        self.assertEqual(result['files']['build/' + PROJECT + '.map']['state'], 'unstable')


if __name__ == '__main__':
    unittest.main(verbosity=2)
