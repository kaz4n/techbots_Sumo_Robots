# Tests D189 from its public contract without reading the new remote implementation.
# Preserves fixed artifact/profile selection and inherited one-shot lifecycle evidence.
# Freeze before Python -B execution; every device, clock and child is host-controlled.
import builtins
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import signal
import stat
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest import mock

HERE = Path(__file__).resolve().parent
ANALYSIS = HERE.parent
OLD = ANALYSIS / 'P7_static_startup_raw'
SOURCE = '21df6ae82cca4b09dc6b1e0de5bc719cf98ec6887800d5ce8297522e491a7950'
RUN = 'app-motor-fault-21df6ae8-run01'
PARENT = '/home/arduino/sumox26_codex_build'
BUILD = PARENT + '/app-motor-fault-static01/build'
SKETCH = PARENT + '/' + SOURCE + '/app_motor_fault'
UPLOAD = PARENT + '/' + RUN + '-upload'
CAPTURE = PARENT + '/' + RUN + '-capture'
ARGV = ['/usr/bin/arduino-cli', '--config-file', '/dev/null', 'upload', '--fqbn',
        'arduino:zephyr:unoq:link_mode=static', '--input-file',
        BUILD + '/app_motor_fault.ino.bin', SKETCH]
IDENTITIES = {
    'raw': (95312, '18598e13f2b5601db504f5272826b0952b95477dd2b1b8d397d20bd2ff899144'),
    'sketch': (95328, 'deb40317e5c444af26e65da4b6f1d0e577d9897d59dbddff3bce03a7bc14335c'),
    'loader': (2303728, '39d4a4fd47241663323f6e04f94dd8f5a9f9ad6582cf1df37f9709b74026adcd'),
    'loader_image': (263680, 'e9322826c422fb234ac8c2e79ea38a050d0dd8dc32b2a89f6930e0a0ff7ebab2'),
}
DEPENDENCIES = {
    'upload': (OLD / 'upload_remote.py',
               'e926b7ba5586475664b0541370e7cfb5c50e40d8dc8b47b18e35db3e0a0a25c1'),
    'capture': (OLD / 'capture_remote.py',
                '95b0344d01886b6db30d55aa18a536f9a481b82348e22643e7920d817dbfac3e'),
    'helper': (ANALYSIS / 'P7_static_link_probe_raw/static_remote.py',
               '8ba9b190c38e728013a383348c60c287b0366607f65f703161cf7f2e142d36f8'),
}
WINDOWS = (('trace', 536951180, 2128), ('report', 537119696, 1168),
           ('runtime', 537117984, 600), ('transaction', 537115448, 504),
           ('previous', 537115952, 48), ('gate', 536953520, 88))
LOADER_READS = tuple(('loader.' + str(i), 0x08000000 + i * 65536,
                      65536 if i < 4 else 1536) for i in range(5))
SKETCH_READS = (('sketch.0', 0x08100000, 65536),
               ('sketch.1', 0x08110000, 29792))
PLAN = tuple((prefix + '.' + name, address, size)
             for prefix, group in (('before', LOADER_READS + SKETCH_READS),
                                    ('first', WINDOWS), ('second', WINDOWS),
                                    ('after', SKETCH_READS + LOADER_READS))
             for name, address, size in group)
SUCCESS = {'returncode': 0, 'timed_out': False, 'reaped': True}
CAPTURE_ENV = {'HOME': '/home/arduino', 'USER': 'arduino', 'LOGNAME': 'arduino',
               'PATH': '/usr/bin:/bin', 'LANG': 'C.UTF-8'}
UPLOAD_ENV = dict(CAPTURE_ENV, LANG='C', LC_ALL='C',
                 ARDUINO_DIRECTORIES_DATA='/home/arduino/.arduino15',
                 ARDUINO_DIRECTORIES_USER='/home/arduino/Arduino',
                 ARDUINO_UPDATER_ENABLE_NOTIFICATION='false')


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def dependency_sources():
    return {key: path.read_bytes() for key, (path, _) in DEPENDENCIES.items()}


def bindings(kind):
    original = json.loads((OLD / (kind + '_bindings.json')).read_text())
    original.update(schema='fixed-app-motor-fault-' + kind + '-v1',
                    source_sha256=SOURCE, run_id=RUN,
                    output=UPLOAD if kind == 'upload' else CAPTURE)
    for role in ('raw', 'sketch', 'loader'):
        if role not in original['files']:
            continue
        pin = original['files'][role]
        pin.update(bytes=IDENTITIES[role][0], sha256=IDENTITIES[role][1])
        if role in ('raw', 'sketch'):
            suffix = '.bin' if role == 'raw' else '.bin-zsk.bin'
            pin['path'] = BUILD + '/app_motor_fault.ino' + suffix
    if kind == 'upload':
        original['absent'][-3:] = [SKETCH + '/sketch.' + extension
                                  for extension in ('yaml', 'yml', 'json')]
    else:
        size, sha = IDENTITIES['loader_image']
        original['loader_image'] = {'bytes': size, 'sha256': sha}
    return original


class Clock:
    def __init__(self):
        self.now, self.sleeps = 100.0, []

    def __call__(self):
        return self.now

    def sleep(self, seconds):
        self.sleeps.append(seconds)
        self.now += seconds


@unittest.skipUnless(sys.platform.startswith('linux'), 'Linux descriptor contract')
class Contract(unittest.TestCase):
    def setUp(self):
        for owner, name in ((subprocess, 'Popen'), (os, 'killpg'), (os, 'system')):
            guard = mock.patch.object(owner, name, side_effect=AssertionError('Native action forbidden'))
            guard.start()
            self.addCleanup(guard.stop)
        self.subject = load(HERE / 'remote.py', 'd189_contract_subject')
        self.sources = dependency_sources()
        self.deps = self.subject.load_dependencies(self.sources)

    def test_import_has_no_native_action_or_dependency_execution(self):
        spec = importlib.util.spec_from_file_location('d189_import_only', HERE / 'remote.py')
        module = importlib.util.module_from_spec(spec)
        original_exec, executions = builtins.exec, []
        def observed_exec(code, *args, **kwargs):
            executions.append(code)
            self.assertEqual(len(executions), 1, 'Import executed a dependency')
            return original_exec(code, *args, **kwargs)
        with mock.patch.object(builtins, 'exec', observed_exec), \
             mock.patch.object(Path, 'read_bytes', side_effect=AssertionError('Dependency read')), \
             mock.patch.object(subprocess, 'Popen') as process, \
             mock.patch.object(os, 'system') as system:
            spec.loader.exec_module(module)
        process.assert_not_called()
        system.assert_not_called()
        self.assertEqual(len(executions), 1)

    def test_dependencies_have_exact_bytes_fresh_private_modules_and_no_old_mutation(self):
        for key, (_, expected) in DEPENDENCIES.items():
            self.assertEqual(digest(self.sources[key]), expected, key)
        again = self.subject.load_dependencies(self.sources)
        self.assertIsInstance(again, SimpleNamespace)
        self.assertEqual(set(vars(again)), {'upload', 'capture', 'helper'})
        for key, (path, _) in DEPENDENCIES.items():
            old = load(path, 'd189_original_' + key)
            private = getattr(self.deps, key)
            self.assertIsNot(private, getattr(again, key))
            self.assertIsNot(private, old)
            for name in ('SOURCE', 'BUILD', 'SKETCH', 'FILE_PATHS', 'ABSENT', 'BINDINGS'):
                if hasattr(old, name):
                    self.assertEqual(getattr(private, name), getattr(old, name), name)
            if key == 'upload':
                self.assertIs(private.selected_profile, self.subject.selected_profile)
                with self.assertRaises(Exception):
                    old.selected_profile(self.deps.capture, RUN)

    def test_every_dependency_hash_is_checked_before_any_exec(self):
        for key in DEPENDENCIES:
            candidate = dict(self.sources)
            candidate[key] += b'\nraise AssertionError("tampered dependency executed")\n'
            with self.subTest(key=key), mock.patch.object(builtins, 'exec') as execute:
                with self.assertRaises(Exception):
                    self.subject.load_dependencies(candidate)
                execute.assert_not_called()

    def test_dependency_shape_and_byte_types_fail_before_exec(self):
        bad = [None, [], dict(self.sources, extra=b''),
               {k: v for k, v in self.sources.items() if k != 'helper'}]
        for value in ('source', bytearray(self.sources['helper']), None, 1):
            bad.append(dict(self.sources, helper=value))
        for candidate in bad:
            with self.subTest(candidate_type=type(candidate).__name__), \
                 mock.patch.object(builtins, 'exec') as execute:
                with self.assertRaises(Exception):
                    self.subject.load_dependencies(candidate)
                execute.assert_not_called()

    def test_profile_exact_native_paths_source_static_command_and_absences(self):
        profile = self.subject.selected_profile(self.deps.capture)
        expected = bindings('upload')
        self.assertEqual(set(profile), {'fixed', 'schema_prefix', 'files', 'absent', 'argv'})
        self.assertEqual(profile['fixed'], {key: expected[key] for key in
                         ('schema', 'source_sha256', 'run_id', 'output')})
        self.assertEqual(profile['schema_prefix'], 'app-motor-fault-upload-')
        self.assertEqual(profile['files'], {k: v['path'] for k, v in expected['files'].items()})
        self.assertEqual(tuple(profile['absent']), tuple(expected['absent']))
        self.assertEqual(profile['argv'], ARGV)
        self.assertNotIn('compile', profile['argv'])
        profile['argv'].append('must not contaminate next selection')
        self.assertEqual(self.subject.selected_profile(self.deps.capture)['argv'], ARGV)

    def test_profile_rejects_every_other_run_and_nonexact_string_type(self):
        class Derived(str):
            pass
        for run in (None, 1, True, b'run', [RUN], Derived(RUN), '', RUN + '/',
                    RUN.replace('run01', 'run02'), 'motor-fault-8f592937-run01',
                    'static-fcddbd8e-run01'):
            with self.subTest(run=run), self.assertRaises(Exception):
                self.subject.selected_profile(self.deps.capture, run)

    def check(self, kind, value):
        return getattr(self.subject, 'checked_' + kind + '_bindings')(self.deps, value)

    def test_both_binding_schemas_accept_only_fixed_identities_without_mutation(self):
        for kind in ('upload', 'capture'):
            expected = bindings(kind)
            original = copy.deepcopy(expected)
            self.assertEqual(self.check(kind, expected), original)
            self.assertEqual(expected, original)
            for role in ('raw', 'sketch', 'loader'):
                if role in expected['files']:
                    self.assertEqual((expected['files'][role]['bytes'],
                                      expected['files'][role]['sha256']), IDENTITIES[role])

    def test_binding_shape_identity_and_all_native_paths_rejected(self):
        for kind in ('upload', 'capture'):
            original = bindings(kind)
            bad = [None, [], dict(original, extra=1)]
            for key in original:
                bad.append({k: v for k, v in original.items() if k != key})
            for key, value in (('schema', 'fixed-static-' + kind + '-v1'),
                               ('source_sha256', '0' * 64), ('run_id', RUN + 'x'),
                               ('output', original['output'] + '/'), ('boot_id', 'bad'),
                               ('uid', True), ('uid', 0), ('files', [])):
                bad.append(dict(original, **{key: value}))
            for role in original['files']:
                candidate = copy.deepcopy(original)
                candidate['files'][role]['path'] = '/tmp/substituted-' + role
                bad.append(candidate)
            for candidate in bad:
                with self.subTest(kind=kind, candidate=repr(candidate)[:100]), \
                     self.assertRaises(Exception):
                    self.check(kind, candidate)

    def test_artifact_sizes_hashes_and_nested_shapes_cannot_be_rebound(self):
        for kind in ('upload', 'capture'):
            original = bindings(kind)
            for role in original['files']:
                mutations = [('bytes', True), ('bytes', -1), ('sha256', 'A' * 64), ('extra', 1)]
                if role in IDENTITIES:
                    mutations += [('bytes', original['files'][role]['bytes'] + 1),
                                  ('sha256', '0' * 64)]
                for key, value in mutations:
                    candidate = copy.deepcopy(original)
                    candidate['files'][role][key] = value
                    with self.subTest(kind=kind, role=role, field=key), self.assertRaises(Exception):
                        self.check(kind, candidate)
            for role in ('extra', next(iter(original['files']))):
                candidate = copy.deepcopy(original)
                if role == 'extra':
                    candidate['files'][role] = copy.deepcopy(next(iter(original['files'].values())))
                else:
                    candidate['files'].pop(role)
                with self.assertRaises(Exception):
                    self.check(kind, candidate)
        for pin in ({}, {'bytes': True, 'sha256': IDENTITIES['loader_image'][1]},
                    {'bytes': 263680, 'sha256': '0' * 64},
                    {'bytes': 263681, 'sha256': IDENTITIES['loader_image'][1]},
                    dict(bytes=263680, sha256=IDENTITIES['loader_image'][1], extra=1)):
            with self.subTest(loader_image=pin), self.assertRaises(Exception):
                self.check('capture', dict(bindings('capture'), loader_image=pin))

    def test_python_B_and_inherited_shadow_directory_constraints(self):
        flags = SimpleNamespace(dont_write_bytecode=0)
        with mock.patch.object(sys, 'flags', flags), mock.patch.object(sys, 'dont_write_bytecode', False):
            for kind in ('upload', 'capture'):
                with self.assertRaises(Exception):
                    self.check(kind, bindings(kind))
        original = bindings('upload')
        for mutation in ('absence', 'directory', 'entry'):
            candidate = copy.deepcopy(original)
            if mutation == 'absence':
                candidate['absent'][-1] = '/tmp/other.json'
            elif mutation == 'directory':
                candidate['directories']['/tmp/other'] = ['x']
            else:
                candidate['directories'][next(iter(candidate['directories']))] = ['..']
            with self.subTest(mutation=mutation), self.assertRaises(Exception):
                self.check('upload', candidate)

    def test_read_plan_exact_static_26_reads_727088_bytes(self):
        observed = self.subject.read_plan()
        self.assertEqual(tuple(observed), PLAN)
        self.assertEqual((len(observed), sum(row[2] for row in observed)), (26, 727088))
        self.assertEqual(sum(row[2] for row in WINDOWS), 4536)
        self.assertTrue(all(0 < row[2] <= 65536 for row in observed))
        with self.assertRaises(TypeError):
            self.subject.read_plan(PLAN + (('extra', 0, 1),))


@unittest.skipUnless(sys.platform.startswith('linux'), 'Linux descriptor contract')
class Lifecycle(unittest.TestCase):
    """Real historical lifecycle; fake native ownership, clock, children and blobs.

    Only the four complete, exact synthetic artifact values map to contract hashes
    in the private capture module. Every other byte string uses real SHA256. This
    is a controlled admission fixture, never target authenticity evidence.
    """
    def setUp(self):
        for owner, name in ((subprocess, 'Popen'), (os, 'killpg'), (os, 'system')):
            guard = mock.patch.object(owner, name, side_effect=AssertionError('Native action forbidden'))
            guard.start()
            self.addCleanup(guard.stop)
        self.subject = load(HERE / 'remote.py', 'd189_lifecycle_subject')
        self.deps = self.subject.load_dependencies(dependency_sources())
        self.temp = tempfile.TemporaryDirectory(prefix='sumox_d189_')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.upload_binding, self.capture_binding = bindings('upload'), bindings('capture')
        self.synthetic = {key: bytes([index + 31]) * size for index, (key, (size, _))
                          in enumerate(IDENTITIES.items())}
        self.deps.capture.digest = self.fixture_digest
        self.make_files()
        self.clock, self.calls, self.pin_reads, self.identity_calls = Clock(), [], [], []
        self.after_execute = self.raw_change = None
        self.outcome, self.execute_error = dict(SUCCESS), None
        self.stdout, self.stderr = b'', b'controlled stderr\n'
        self.identity_value = {'boot_id': self.upload_binding['boot_id'], 'uid': 1000,
                               'user': 'arduino', 'home': '/home/arduino',
                               'sysname': 'Linux', 'machine': 'aarch64'}
        self.deps.helper.identity = self.identity
        self.deps.helper.directory_info = self.directory_info
        self.real_read = self.deps.helper.logical_read
        self.deps.helper.logical_read = self.tracked_read
        self.install_null_fixture()

    def fixture_digest(self, raw):
        for key, value in self.synthetic.items():
            if raw == value:
                return IDENTITIES[key][1]
        return digest(raw)

    def logical(self, path):
        return self.root / str(path).lstrip('/')

    def local_argument(self, path):
        path = Path(path)
        return path if path.is_relative_to(self.root) else self.logical(path)

    def make_files(self):
        for binding in (self.upload_binding, self.capture_binding):
            for role, pin in binding['files'].items():
                raw = self.synthetic.get(role, ('controlled-' + role).encode())
                if role not in self.synthetic:
                    pin.update(bytes=len(raw), sha256=digest(raw))
                target = self.logical(pin['path'])
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(raw)
        for path, entries in self.upload_binding['directories'].items():
            for entry in entries:
                self.logical(path + '/' + entry).mkdir(parents=True, exist_ok=True)
        for path in (PARENT, SKETCH, '/proc', '/dev', '/tmp'):
            self.logical(path).mkdir(parents=True, exist_ok=True)
        self.logical('/dev/null').write_bytes(b'')

    def install_null_fixture(self):
        real_stat, real_lstat, real_fstat = os.stat, os.lstat, os.fstat
        info = real_stat(self.logical('/dev/null'))
        identity = (info.st_dev, info.st_ino)
        def convert(observed):
            if (observed.st_dev, observed.st_ino) != identity:
                return observed
            fields = {key: getattr(observed, key) for key in dir(observed) if key.startswith('st_')}
            fields.update(st_mode=stat.S_IFCHR | 0o600, st_rdev=os.makedev(1, 3))
            return SimpleNamespace(**fields)
        for name, original in (('stat', real_stat), ('lstat', real_lstat), ('fstat', real_fstat)):
            patcher = mock.patch.object(os, name,
                side_effect=lambda *a, _original=original, **k: convert(_original(*a, **k)))
            patcher.start()
            self.addCleanup(patcher.stop)

    def identity(self, fd):
        self.identity_calls.append(fd)
        return copy.deepcopy(self.identity_value)

    def directory_info(self, info, logical):
        if not stat.S_ISDIR(info.st_mode):
            raise ValueError('Not a directory: ' + logical)
        return self.deps.helper.directory_id(info)

    def tracked_read(self, fd, logical, limit, proc=False):
        self.pin_reads.append(logical)
        return self.real_read(fd, logical, limit, proc)

    def loader_image(self, raw):
        self.assertEqual(raw, self.synthetic['loader'])
        return self.synthetic['loader_image']

    def bytes_for(self, item):
        name, address, size = item
        for part, start in (('loader', 0x08000000), ('sketch', 0x08100000)):
            if '.' + part + '.' in name:
                key = 'loader_image' if part == 'loader' else part
                return self.synthetic[key][address - start:address - start + size]
        # Identical separated samples deliberately cannot prove coherence.
        return bytes([1 + next(i for i, row in enumerate(WINDOWS) if name.endswith('.' + row[0]))]) * size

    def check_launch(self, mode, argv, stdout, stderr, timeout):
        index = len(self.calls)
        output = UPLOAD if mode == 'upload' else CAPTURE
        if mode == 'upload':
            self.assertEqual(index, 0, 'Upload is one-shot')
            self.assertEqual(argv, ARGV)
            prefix, budget = 'upload', 280
        else:
            self.assertLess(index, len(PLAN), 'Read outside fixed plan')
            name, address, size = PLAN[index]
            files = self.capture_binding['files']
            raw_path = CAPTURE + f'/{index:02d}-{name}.bin'
            self.assertEqual(argv, [files['openocd']['path'], '-f', files['config']['path'],
                '-c', f'dump_image {{{raw_path}}} 0x{address:08x} {size}', '-c', 'shutdown'])
            prefix, budget = f'{index:02d}', 700
        self.assertEqual(timeout, min(120 if mode == 'upload' else 30, budget - self.clock.now))
        for path, extension in ((stdout, 'stdout'), (stderr, 'stderr')):
            self.assertEqual(self.local_argument(path), self.logical(output + '/' + prefix + '.' + extension))
        self.assertTrue(self.logical(output + '/' + mode + '_attempt.json').is_file())
        command = 'upload_command.json' if mode == 'upload' else prefix + '.command.json'
        self.assertTrue(self.logical(output + '/' + command).is_file())
        self.calls.append((copy.deepcopy(argv), timeout))
        return index

    def execute(self, mode, argv, stdout, stderr, timeout):
        index = self.check_launch(mode, argv, stdout, stderr, timeout)
        if self.execute_error:
            raise self.execute_error
        self.local_argument(stdout).write_bytes(self.stdout)
        self.local_argument(stderr).write_bytes(self.stderr)
        if mode == 'capture':
            name = PLAN[index][0]
            target = self.logical(CAPTURE + f'/{index:02d}-{name}.bin')
            raw = self.bytes_for(PLAN[index])
            if self.raw_change:
                raw = self.raw_change(index, raw, target)
            if raw is not None:
                with target.open('xb') as stream:
                    stream.write(raw)
        if self.after_execute:
            self.after_execute(index)
        return copy.deepcopy(self.outcome)

    def run_mode(self, mode, **kwargs):
        options = dict(fs_root=self.root, clock=self.clock,
                       executor=lambda *args: self.execute(mode, *args),
                       bindings=self.upload_binding if mode == 'upload' else self.capture_binding)
        options.update(kwargs)
        if mode == 'upload':
            return self.subject.upload(self.deps, **options)
        options.setdefault('sleeper', self.clock.sleep)
        return self.subject.collect(self.deps, self.loader_image, **options)

    def assert_report(self, report, mode, status):
        self.assertEqual(report['schema'], 'app-motor-fault-' + mode + '-result-v1')
        self.assertEqual((report['run_id'], report['source_sha256'], report['status']), (RUN, SOURCE, status))
        output = UPLOAD if mode == 'upload' else CAPTURE
        self.assertEqual(json.loads(self.logical(output + '/' + mode + '_result.json').read_text()), report)
        if status in ('UPLOADED', 'COLLECTED'):
            self.assertIsNone(report['first_error'])
            self.assertEqual(report['postcheck_errors'], [])
        else:
            self.assertIsInstance(report['first_error'], dict)
        return report

    def fresh_case(self, function):
        case = Lifecycle('test_upload_success_exact_one_shot_and_all_closing_pins')
        try:
            case.setUp()
            function(case)
        finally:
            case.doCleanups()

    def test_upload_success_exact_one_shot_and_all_closing_pins(self):
        report = self.assert_report(self.run_mode('upload'), 'upload', 'UPLOADED')
        self.assertEqual((report['attempts'], report['subprocess']), (1, SUCCESS))
        self.assertEqual(self.calls, [(ARGV, 120)])
        claim = json.loads(self.logical(UPLOAD + '/upload_attempt.json').read_text())
        self.assertEqual(claim['bindings'], self.upload_binding)
        self.assertEqual(claim['environment'], UPLOAD_ENV)
        self.assertEqual(claim['schema'], 'app-motor-fault-upload-attempt-v1')
        for pin in self.upload_binding['files'].values():
            self.assertGreaterEqual(self.pin_reads.count(pin['path']), 2)
        self.assertGreaterEqual(len(self.identity_calls), 2)

    def test_capture_all_reads_retained_flash_brackets_and_coherence_unproven(self):
        def sleep(seconds):
            self.assertEqual(len(self.calls), 13)
            self.clock.sleep(seconds)
        report = self.assert_report(self.run_mode('capture', sleeper=sleep), 'capture', 'COLLECTED')
        self.assertEqual(report['counts'], {'commands': 26, 'reads': 26, 'requested_bytes': 727088})
        self.assertEqual(self.clock.sleeps, [2])
        self.assertGreaterEqual(report['wait']['after'] - report['wait']['before'], 2)
        analysis = report['analysis']
        self.assertEqual(analysis['schema'], 'app-motor-fault-capture-analysis-v1')
        self.assertEqual(analysis['coherence'], 'UNPROVEN')
        self.assertEqual(analysis['flash'], dict.fromkeys(
            ('before_loader', 'before_sketch', 'after_loader', 'after_sketch'), True))
        self.assertTrue(all(type(value) is bool for value in analysis['flash'].values()))
        self.assertEqual(analysis['snapshots'], report['reads'][7:19])
        self.assertEqual(len(analysis['snapshots']), 12)
        for item, record in zip(PLAN, report['reads']):
            self.assertEqual((record['name'], record['address'], record['bytes']), item)
            self.assertEqual(record['sha256'], digest(self.bytes_for(item)))
            self.assertEqual(self.logical(CAPTURE + '/' + record['file']).read_bytes(), self.bytes_for(item))
        for pin in self.capture_binding['files'].values():
            self.assertGreaterEqual(self.pin_reads.count(pin['path']), 2)
        self.assertGreaterEqual(len(self.identity_calls), 2)

    def test_both_lifecycles_reject_binding_and_preexisting_owner_before_command(self):
        for mode in ('upload', 'capture'):
            def exercise(case):
                selected = copy.deepcopy(case.upload_binding if mode == 'upload' else case.capture_binding)
                selected['source_sha256'] = '0' * 64
                with case.assertRaises(Exception):
                    case.run_mode(mode, bindings=selected)
                output = case.logical(UPLOAD if mode == 'upload' else CAPTURE)
                case.assertFalse(output.exists())
                output.mkdir()
                sentinel = output / 'existing'
                sentinel.write_bytes(b'preserve')
                with case.assertRaises(Exception):
                    case.run_mode(mode)
                case.assertEqual(case.calls, [])
                case.assertEqual(list(output.iterdir()), [sentinel])
                case.assertEqual(sentinel.read_bytes(), b'preserve')
            with self.subTest(mode=mode):
                self.fresh_case(exercise)

    def test_admission_rejects_changed_artifacts_symlinks_identity_and_processes(self):
        for mode in ('upload', 'capture'):
            for failure in ('artifact', 'symlink', 'identity', 'process'):
                def exercise(case):
                    selected = case.upload_binding if mode == 'upload' else case.capture_binding
                    if failure in ('artifact', 'symlink'):
                        path = case.logical(selected['files']['sketch']['path'])
                        if failure == 'artifact':
                            path.write_bytes(b'changed')
                        else:
                            moved = path.with_suffix('.fixture')
                            path.rename(moved)
                            path.symlink_to(moved)
                    elif failure == 'identity':
                        case.identity_value['boot_id'] = '00000000-0000-0000-0000-000000000000'
                    else:
                        process = case.logical('/proc/123')
                        process.mkdir()
                        (process / 'comm').write_text('openocd\n')
                    with case.assertRaises(Exception):
                        case.run_mode(mode)
                    case.assertEqual(case.calls, [])
                    case.assertFalse(case.logical(UPLOAD if mode == 'upload' else CAPTURE).exists())
                with self.subTest(mode=mode, failure=failure):
                    self.fresh_case(exercise)

    def test_before_flash_mismatch_never_reads_sram_or_sleeps(self):
        for changed in (0, 5):
            def exercise(case):
                case.raw_change = lambda i, raw, target: b'!' + raw[1:] if i == changed else raw
                report = case.assert_report(case.run_mode('capture'), 'capture', 'FAILED')
                case.assertLessEqual(len(case.calls), 7)
                case.assertGreater(len(case.calls), changed)
                case.assertEqual(case.clock.sleeps, [])
                case.assertFalse(any(row['name'].startswith(('first.', 'second.')) for row in report['reads']))
            with self.subTest(changed=changed):
                self.fresh_case(exercise)

    def test_after_flash_mismatch_stops_at_first_complete_bad_image(self):
        for changed, maximum in ((19, 21), (21, 26)):
            def exercise(case):
                case.raw_change = lambda i, raw, target: b'!' + raw[1:] if i == changed else raw
                report = case.assert_report(case.run_mode('capture'), 'capture', 'FAILED')
                case.assertLessEqual(len(case.calls), maximum)
                case.assertGreater(len(case.calls), changed)
                case.assertEqual(len([r for r in report['reads'] if r['name'].startswith(('first.', 'second.'))]), 12)
            with self.subTest(changed=changed):
                self.fresh_case(exercise)

    def test_missing_short_extra_and_symlink_reads_stop_immediately(self):
        for selected, failure in ((0, 'missing'), (7, 'short'), (13, 'extra'), (19, 'symlink')):
            def exercise(case):
                def change(index, raw, target):
                    if index != selected:
                        return raw
                    if failure == 'missing':
                        return None
                    if failure == 'short':
                        return raw[:-1]
                    if failure == 'extra':
                        return raw + b'!'
                    real = target.with_suffix('.real')
                    real.write_bytes(raw)
                    target.symlink_to(real)
                    return None
                case.raw_change = change
                report = case.assert_report(case.run_mode('capture'), 'capture', 'FAILED')
                case.assertEqual(len(case.calls), selected + 1)
                case.assertEqual(report['counts']['reads'], selected)
                case.assertFalse(case.logical(CAPTURE + f'/{selected + 1:02d}.command.json').exists())
            with self.subTest(selected=selected, failure=failure):
                self.fresh_case(exercise)

    def test_short_sample_gap_and_expired_gap_suppress_second_sample(self):
        for elapsed in (1.999, 600):
            def exercise(case):
                def sleep(seconds):
                    case.assertEqual(len(case.calls), 13)
                    case.clock.now += elapsed
                case.assert_report(case.run_mode('capture', sleeper=sleep), 'capture', 'FAILED')
                case.assertEqual(len(case.calls), 13)
            with self.subTest(elapsed=elapsed):
                self.fresh_case(exercise)

    def test_child_failure_and_malformed_result_do_not_retry(self):
        for mode in ('upload', 'capture'):
            for outcome in (dict(SUCCESS, returncode=1), dict(SUCCESS, timed_out=True),
                            dict(SUCCESS, reaped=False), dict(SUCCESS, returncode=False),
                            dict(SUCCESS, extra=1), None):
                def exercise(case):
                    case.outcome = outcome
                    case.assert_report(case.run_mode(mode), mode, 'FAILED')
                    case.assertEqual(len(case.calls), 1)
                    with case.assertRaises(Exception):
                        case.run_mode(mode)
                    case.assertEqual(len(case.calls), 1, 'Consumed attempt cannot retry')
                with self.subTest(mode=mode, outcome=outcome):
                    self.fresh_case(exercise)

    def test_final_pins_identity_and_original_error_all_survive_failure(self):
        for mode in ('upload', 'capture'):
            def exercise(case):
                def execute(*args):
                    case.check_launch(mode, *args)
                    selected = case.upload_binding if mode == 'upload' else case.capture_binding
                    for pin in selected['files'].values():
                        case.logical(pin['path']).write_bytes(b'changed')
                    case.identity_value['boot_id'] = '00000000-0000-0000-0000-000000000000'
                    raise RuntimeError('first controlled execution failure')
                report = case.assert_report(case.run_mode(mode, executor=execute), mode, 'FAILED')
                case.assertEqual(report['first_error']['message'], 'first controlled execution failure')
                case.assertGreaterEqual(len(report['postcheck_errors']), 6)
                selected = case.upload_binding if mode == 'upload' else case.capture_binding
                for pin in selected['files'].values():
                    case.assertGreaterEqual(case.pin_reads.count(pin['path']), 2)
                case.assertGreaterEqual(len(case.identity_calls), 2)
            with self.subTest(mode=mode):
                self.fresh_case(exercise)

    def test_capture_deadline_caps_next_child_and_no_third_read(self):
        self.after_execute = lambda index: setattr(self.clock, 'now', 680 if index == 0 else 700)
        self.assert_report(self.run_mode('capture'), 'capture', 'FAILED')
        self.assertEqual([timeout for _, timeout in self.calls], [30, 20])

    def test_upload_overall_deadline_failure_is_retained(self):
        self.after_execute = lambda index: setattr(self.clock, 'now', 280)
        self.assert_report(self.run_mode('upload'), 'upload', 'FAILED')
        self.assertEqual(len(self.calls), 1)

    def test_capture_replaced_owner_stops_and_keeps_original_directory_evidence(self):
        output = self.logical(CAPTURE)
        moved = output.with_name(output.name + '-moved')
        def replace(index):
            if index == 0:
                output.rename(moved)
                output.mkdir()
                (output / 'sentinel').write_bytes(b'preserve')
        self.after_execute = replace
        report = self.run_mode('capture')
        self.assertEqual(report['status'], 'FAILED')
        self.assertEqual(len(self.calls), 1)
        self.assertEqual(json.loads((moved / 'capture_result.json').read_text()), report)
        self.assertEqual([path.name for path in output.iterdir()], ['sentinel'])

    def test_one_mib_stream_cap_is_inherited(self):
        for mode in ('upload', 'capture'):
            def exercise(case):
                case.stderr = bytes(1048576)
                case.assert_report(case.run_mode(mode), mode, 'FAILED')
                case.assertEqual(len(case.calls), 1)
            with self.subTest(mode=mode):
                self.fresh_case(exercise)

    def test_default_executors_preserve_environment_limits_timeout_and_kill_reap(self):
        import resource
        for mode in ('upload', 'capture'):
            def exercise(case):
                waits, kills, limits = [], [], []
                class Process:
                    pid = 987654
                    returncode = None
                    def wait(self, timeout):
                        waits.append(timeout)
                        if len(waits) == 1:
                            raise subprocess.TimeoutExpired('controlled-child', timeout)
                        self.returncode = -signal.SIGKILL
                        return self.returncode
                def popen(argv, **kwargs):
                    paths = [os.readlink('/proc/self/fd/' + str(kwargs[key].fileno()))
                             for key in ('stdout', 'stderr')]
                    case.check_launch(mode, argv, *paths, 120 if mode == 'upload' else 30)
                    case.assertEqual(kwargs['cwd'], '/home/arduino')
                    case.assertEqual(kwargs['env'], UPLOAD_ENV if mode == 'upload' else CAPTURE_ENV)
                    case.assertIs(kwargs['shell'], False)
                    case.assertIs(kwargs['start_new_session'], True)
                    case.assertEqual(kwargs['stdin'], subprocess.DEVNULL)
                    kwargs['preexec_fn']()
                    return Process()
                with mock.patch.object(subprocess, 'Popen', popen), \
                     mock.patch.object(os, 'getpgid', lambda pid: pid), \
                     mock.patch.object(os, 'killpg', lambda pid, sig: kills.append((pid, sig))), \
                     mock.patch.object(resource, 'setrlimit', lambda which, bounds: limits.append((which, bounds))):
                    case.assert_report(case.run_mode(mode, executor=None), mode, 'FAILED')
                case.assertEqual(waits, [120 if mode == 'upload' else 30, 5])
                case.assertEqual(kills, [(987654, signal.SIGKILL)])
                cap = 2303728 if mode == 'upload' else 1048576
                case.assertEqual(limits, [(resource.RLIMIT_FSIZE, (cap, cap))])
                case.assertEqual(len(case.calls), 1)
            with self.subTest(mode=mode):
                self.fresh_case(exercise)


if __name__ == '__main__':
    unittest.main(verbosity=2)
