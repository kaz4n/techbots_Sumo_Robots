# Tests D188 fixed compile composition from the frozen contract and declared seams.
# Keeps caller admission, exact staging and native evidence claims separate.
# Freeze before Python -B execution; command endpoints are controlled substitutes.
import ast
import base64
import copy
from contextlib import contextmanager, ExitStack, redirect_stdout
import errno
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import sys
import tempfile
import types
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[2]
RAW = 'state/analysis/P7_app_motor_fault_compile_raw'
CALLER = 'tools/compile_app_motor_fault.py'
REMOTE_HELPER = 'tools/app_motor_fault_compile_remote.py'
CONTRACT = 'state/analysis/P7_app_motor_fault_compile_contract.md'
LEGACY = 'state/analysis/P7_current_app_compile_raw/compile_current_app.py'
STATIC = 'state/analysis/P7_static_link_probe_raw/'
EXECUTOR = 'state/analysis/P7_motor_fault_raw/compile_motor_fault.py'
WAIT = 'state/analysis/P7_static_startup_raw/capture_remote.py'
BASELINES = {
    'initialization': 'state/analysis/P7_static_startup_raw/cli_initialization_inventory.json',
    'builtins': 'state/analysis/P7_static_startup_raw/cli_builtin_files_inventory.json',
}
FIXED = [CALLER, REMOTE_HELPER, CONTRACT, LEGACY, EXECUTOR, WAIT, *BASELINES.values(),
         'tools/board_tool.py', 'tools/app_build_policy.py', 'tools/app_build_commands.json',
         'tools/app_build_pins.json', 'tools/app_motor_fault_static_policy.py',
         STATIC + 'static_policy.py', STATIC + 'static_native_artifacts.py',
         STATIC + 'static_reference.json', STATIC + 'static_remote.py', STATIC + 'static_artifacts.py']
TREES = ('src', 'bench/app_motor_fault', 'bench/motor_fault/src')
HEAD = '1234567890abcdef1234567890abcdef12345678'
BOOT = '01234567-89ab-cdef-8123-456789abcdef'
OLD_BOOT = '55c386b9-fe6d-4388-a7f4-1d91e0bb49d8'
BOARD = '2629958581'
ADB = 'C:/Users/narut/AppData/Local/Arduino15/packages/arduino/tools/adb/32.0.0/adb.exe'
PROJECT = 'app_motor_fault.ino'
FQBN = 'arduino:zephyr:unoq:link_mode=static'
FLAGS = '-DMATCH=0 -DMOTORS_ALLOWED=0 -DSUMOX_MOTOR_FAULT_PROBE=1'
ATTEMPT = 'app-motor-fault-static01'
REMOTE_ROOT = '/home/arduino/sumox26_codex_build'
REMOTE = REMOTE_ROOT + '/' + ATTEMPT
BUILD, ARTIFACTS = REMOTE + '/build', REMOTE + '/artifacts'
DATA, USER = '/home/arduino/.arduino15', '/home/arduino/Arduino'
REJECTIONS = (ValueError, TypeError, RuntimeError, OSError, SystemExit)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def encode(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':')) + '\n').encode()


def load(path, name):
    module = types.ModuleType(name)
    module.__file__ = str(path)
    with mock.patch.dict(sys.modules, {name: module}):
        exec(compile(path.read_bytes(), str(path), 'exec'), module.__dict__)
    return module


def file_set(root):
    return {p.relative_to(root).as_posix(): digest(p.read_bytes())
            for p in root.rglob('*') if p.is_file()}


def expected_stage(root):
    result = {}
    for folder in TREES:
        for path in (root / folder).rglob('*'):
            if not path.is_file(): continue
            relative = path.relative_to(root).as_posix()
            target = None
            if folder == 'bench/app_motor_fault':
                tail = path.relative_to(root / folder).as_posix()
                if tail != '.gitkeep': target = tail
            elif folder == 'bench/motor_fault/src':
                if path.name in ('motor_fault.h', 'motor_fault.cpp') and path.parent == root / folder:
                    target = 'src/' + path.name
            elif relative == 'src/config.h' or relative.startswith(('src/core/', 'src/hal/')):
                target = relative
            elif relative.startswith('src/app/') and not relative.startswith('src/app/src/') \
                    and path.suffix in ('.c', '.cc', '.cpp', '.h', '.hpp'):
                target = relative
            if target is not None:
                if target in result: raise ValueError('Fixture stage collision: ' + target)
                result[target] = path.read_bytes()
    return result


def source_hash(mapping):
    value = hashlib.sha256()
    for name, raw in sorted(mapping.items()):
        value.update(name.encode()); value.update(b'\0'); value.update(raw)
    return value.hexdigest()


class CallerFixture(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not sys.dont_write_bytecode:
            raise RuntimeError('Independent D188 tests require Python -B')
        cls.subject = load(ROOT / CALLER, 'd188_caller_subject')
        cls.remote_fixture = load(ROOT / 'tests/tooling/test_app_motor_fault_compile_remote.py',
                                  'd188_artifact_fixture')
        cls.metadata_fixture = load(ROOT / 'state/analysis/P7_static_link_probe_test_draft/test_static_policy.py',
                                    'd188_metadata_fixture')

    def setUp(self):
        ram = '/dev/shm' if sys.platform == 'linux' else None
        temporary = tempfile.TemporaryDirectory(prefix='sumox-d188-caller-', dir=ram)
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()
        names = FIXED + [p.relative_to(ROOT).as_posix() for folder in TREES
                         for p in (ROOT / folder).rglob('*') if p.is_file()]
        self.files = {}
        for name in names:
            path = self.root / name; path.parent.mkdir(parents=True, exist_ok=True)
            raw = (ROOT / name).read_bytes(); path.write_bytes(raw); self.files[name] = digest(raw)
        self.expected = expected_stage(self.root)
        self.source = source_hash(self.expected)
        self.head, self.dirty, self.events = HEAD, [], []
        self.manifest()
        self.patch(self.subject.CompileDiagnostic, 'git_state', lambda owner: (self.head, self.dirty))
        self.patch(subprocess, 'run', side_effect=AssertionError('Unsubstituted process forbidden'))
        self.patch(subprocess, 'Popen', side_effect=AssertionError('Unsubstituted process forbidden'))
        self.patch(shutil, 'disk_usage', return_value=types.SimpleNamespace(free=2**31))

    def patch(self, target, name, *args, **kwargs):
        patcher = mock.patch.object(target, name, *args, **kwargs)
        value = patcher.start(); self.addCleanup(patcher.stop)
        return value

    def manifest(self, **updates):
        value = dict(schema='app-motor-fault-static-inputs-v1', source_sha256=self.source,
                     boot_id=BOOT, files=dict(self.files))
        value.update(updates)
        path = self.root / RAW / 'inputs_static.json'
        path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes(encode(value))
        return path

    def owner(self):
        owner = self.subject.CompileDiagnostic(HEAD, root=self.root)
        self.patch(owner.base, 'ADB', ADB if os.name == 'nt' else '/mnt/c/' + ADB[3:])
        self.patch(sys, 'pycache_prefix', str(self.root / RAW / 'native_static01/pycache'))
        return owner

    def reject(self, function):
        with self.assertRaises(REJECTIONS): function()

    def metadata(self):
        reference = json.loads((self.root / STATIC / 'static_reference.json').read_bytes())
        value = self.metadata_fixture.public_envelope(reference, BUILD, DATA)
        properties = self.metadata_fixture.public_properties(reference, BUILD, DATA)
        for key, template in reference.items():
            adapted = template.replace('app.ino', PROJECT).replace('-DMATCH=0 -DMOTORS_ALLOWED=0', FLAGS)
            import re
            properties[key] = re.sub(r'@(BUILD_PATH|DATA_DIR)@',
                lambda match: {'BUILD_PATH': BUILD, 'DATA_DIR': DATA}[match[1]], adapted)
        properties['build.project_name'] = PROJECT
        value['builder_result']['build_properties'] = [k + '=' + v for k, v in properties.items()]
        return json.dumps(value)

    def command(self):
        return ['arduino-cli', 'compile', '--json', '--fqbn', FQBN, '--build-path', BUILD,
                '--output-dir', ARTIFACTS, '--build-property', 'compiler.cpp.extra_flags=' + FLAGS,
                '--build-property', 'compiler.c.extra_flags=' + FLAGS,
                '--build-property', 'build.library_discovery_phase_flag=-DARDUINO_LIBRARY_DISCOVERY_PHASE=0',
                REMOTE_ROOT + '/' + self.source + '/app_motor_fault']

    @contextmanager
    def no_writes(self):
        with ExitStack() as stack:
            for name in ('mkdir', 'write_bytes', 'write_text', 'unlink', 'rename', 'replace'):
                stack.enter_context(mock.patch.object(Path, name, side_effect=AssertionError('Mutation: ' + name)))
            yield

    def folder(self, owner, label):
        self.assertTrue((owner.output / 'intent.json').is_file(), 'Intent must precede board contact')
        owner.counter += 1
        path = owner.output / ('%04d-controlled-%s' % (owner.counter, label))
        path.mkdir(); return path

    def controlled(self, owner, existing=False, partial=False):
        self.remote_files, self.packets = {}, []
        self.compile_failure, self.inventory_failure = None, None
        self.after_query, self.reply_mutation = None, None
        self.artifact_reply = self.remote_fixture.synthetic_reply()
        self.identity = dict(uid=1000, user='arduino', boot_id=BOOT, free_bytes=2**31,
            cli_sha256='b878632298958d61fd1eb19e70ac5d2e803d83db8930bc72dc6915eee6e8f433', conflicts=[])
        def direct(program, label, timeout=90):
            self.events.append(('direct', label, timeout))
            folder = self.folder(owner, label)
            if label in ('identity', 'command-owner'):
                self.assertIn(BOOT, program)
                self.assertNotIn(OLD_BOOT, program)
                result = dict(self.identity)
            elif label == 'source-admission':
                if existing:
                    self.remote_files = file_set(owner.stage_path)
                    if partial: self.remote_files.pop(next(iter(self.remote_files)))
                result = {'reused': existing}
            elif label == 'source-set': result = dict(self.remote_files)
            elif label == 'checked-command':
                assignments = {n.targets[0].id: n.value for n in ast.parse(program).body
                    if isinstance(n, ast.Assign) and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name)}
                packet = ast.literal_eval(assignments['packet']); self.packets.append(packet)
                self.assertEqual(ast.literal_eval(assignments['BOOT']), BOOT)
                is_query = '--show-properties=expanded' in packet['argv']
                if not is_query and self.compile_failure: raise self.compile_failure
                out = self.metadata().encode()
                result = dict(status='COMPLETED', execution=dict(returncode=0, timed_out=False, reaped=True),
                    stdout_base64=base64.b64encode(out).decode(), stderr_base64='', stdout_bytes=len(out), stderr_bytes=0)
                if is_query and self.after_query: self.after_query()
                if self.reply_mutation: self.reply_mutation(result)
            elif label in ('artifacts', 'artifacts-final'): result = copy.deepcopy(self.artifact_reply)
            else: raise AssertionError('Unexpected direct endpoint: ' + label)
            return subprocess.CompletedProcess([], 0, encode(result), b''), folder
        def transport(arguments, timeout, label):
            self.events.append(('transport', label, tuple(arguments), timeout))
            folder = self.folder(owner, label)
            if arguments[0] == 'push':
                local, remote = Path(arguments[1]), arguments[2]
                tail = local.relative_to(owner.stage_path).as_posix()
                self.assertEqual(remote, REMOTE_ROOT + '/' + self.source + '/app_motor_fault/' + tail)
                self.remote_files[tail] = digest(local.read_bytes()); raw = b''
            else:
                for name, relative in BASELINES.items():
                    baseline = json.loads((self.root / relative).read_bytes())
                    if arguments == ['shell', '-T', shlex.join(baseline['argv'])]:
                        if self.inventory_failure: raise self.inventory_failure
                        value = json.loads(baseline['stdout']); value['identity']['boot_id'] = BOOT
                        raw = encode(value); break
                else: raise AssertionError('Unexpected transport endpoint: ' + repr(arguments[:2]))
            return subprocess.CompletedProcess(arguments, 0, raw, b''), folder
        self.patch(owner, 'direct', direct)
        self.patch(owner, 'transport', transport)
        self.patch(owner, 'final_policy', lambda overrides=False: self.events.append(('policy', overrides)))
        # Initial installed CLI/config/pin primitives are inherited and separately
        # covered; retain the actual query capture/runner and fixed D187 validator.
        def preflight(command):
            self.events.append(('preflight', tuple(command)))
            query = command[:-1] + ['--show-properties=expanded', command[-1]]
            result = owner.capture(query, 'expanded-properties')
            return owner.static_policy().validate_preflight(result.stdout, build_path=BUILD, data_dir=DATA)
        self.patch(owner, 'preflight', preflight)
        return owner

    def local_source_fixture(self):
        owner = self.controlled(self.owner()); owner.local(); owner.prepare(); owner.claim(); owner.stage()
        source = self.root / 'synthetic-native' / self.source / 'app_motor_fault'
        for name, raw in self.expected.items():
            path = source / name; path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes(raw)
        owner.sketch = str(source)
        # Replace only target identity preamble; the actual generated source-set
        # and reuse-admission programs operate on a bounded owned local fixture.
        self.patch(owner, 'preamble', lambda: 'import os,json,stat,hashlib,re\nfrom pathlib import Path\n'
            + 'identity=' + repr(self.identity) + '\n')
        def direct(program, label, timeout=90):
            self.assertIn(label, ('source-set', 'source-admission'))
            output = io.StringIO()
            with redirect_stdout(output): exec(compile(program, '<synthetic-source-check>', 'exec'), {})
            return subprocess.CompletedProcess([], 0, output.getvalue().encode(), b''), owner.output
        self.patch(owner, 'direct', direct)
        return owner, source


class LocalAdmissionContract(CallerFixture):
    def test_import_never_dispatches_or_writes(self):
        with self.no_writes():
            fresh = load(ROOT / CALLER, 'd188_import_only')
        self.assertTrue(callable(fresh.parse_request))

    def test_exact_cli_and_invalid_forms_reject_before_io(self):
        for action in ('--check-only', '--execute'):
            self.assertEqual(self.subject.parse_request([action, '--reviewed-head', HEAD]), (action, HEAD))
        invalid = (None, True, '', [], ['--execute'], ['--check-only', '--reviewed-head', HEAD.upper()],
            ['--execute', '--reviewed-head', HEAD + '0'], ['--execute', '--reviewed-head', 7],
            ['--reviewed-head', HEAD, '--execute'], ['--execute', '--reviewed-head', HEAD, '--upload'],
            ['--execute', '--profile', 'bench', '--reviewed-head', HEAD], ('--execute', '--reviewed-head', HEAD))
        with mock.patch.object(Path, 'read_bytes', side_effect=AssertionError('Invalid argument did I/O')):
            for argv in invalid:
                with self.subTest(argv=argv): self.reject(lambda: self.subject.parse_request(argv))

    def test_invalid_constructor_head_rejects_without_io(self):
        with mock.patch.object(Path, 'read_bytes', side_effect=AssertionError('Invalid constructor did I/O')):
            for value in (None, True, '', HEAD.upper(), HEAD[:-1], 'g' * 40):
                with self.subTest(head=value):
                    self.reject(lambda: self.subject.CompileDiagnostic(value, root=self.root))

    def test_check_only_is_read_only_with_exact_current_source_and_fixed_paths(self):
        owner = self.owner(); before = file_set(self.root)
        with self.no_writes(), mock.patch.object(owner, 'direct', side_effect=AssertionError('Board call')):
            report = owner.check()
        expected = dict(schema='app-motor-fault-static-check-v1', reviewed_head=HEAD,
            source_sha256=self.source, boot_id=BOOT, project=PROJECT, fqbn=FQBN, flags=FLAGS,
            remote=REMOTE, sketch=REMOTE_ROOT + '/' + self.source + '/app_motor_fault')
        for key, value in expected.items(): self.assertEqual(report[key], value)
        self.assertEqual(Path(report['stage']), self.root / 'build/stage' / ATTEMPT / 'app_motor_fault')
        self.assertEqual(Path(report['output']), self.root / RAW / 'native_static01')
        self.assertEqual(before, file_set(self.root))
        self.assertFalse((self.root / 'build').exists())
        self.assertFalse((self.root / RAW / 'native_static01').exists())

    def test_head_clean_tree_and_bytecode_are_mandatory(self):
        for head, dirty in (('f' * 40, []), (HEAD, [(' M', 'src/config.h')]),
                            (HEAD, [('??', 'stray.txt')]),
                            (HEAD, [(' M', RAW + '/native_static01/result.json')])):
            self.head, self.dirty = head, dirty
            with self.subTest(head=head, dirty=dirty): self.reject(self.owner().check)
        self.head, self.dirty = HEAD, []
        with mock.patch.object(sys, 'dont_write_bytecode', False): self.reject(self.owner().check)

    def test_execute_prefix_and_existing_owner_requirements_precede_contact(self):
        owner = self.owner()
        for prefix in (None, 'relative', str(self.root / 'elsewhere')):
            with self.subTest(prefix=prefix), mock.patch.object(sys, 'pycache_prefix', prefix):
                self.reject(owner.run)
        self.assertFalse((self.root / RAW / 'native_static01').exists())
        for relative in (RAW + '/native_static01', 'build/stage/' + ATTEMPT):
            path = self.root / relative; path.parent.mkdir(parents=True, exist_ok=True)
            for kind in ('file', 'directory'):
                path.write_bytes(b'prior owner') if kind == 'file' else path.mkdir()
                with self.subTest(owner=relative, kind=kind): self.reject(self.owner().run)
                path.unlink() if kind == 'file' else path.rmdir()

    def test_manifest_shape_duplicate_nonfinite_bounds_boot_and_source_fail(self):
        path = self.root / RAW / 'inputs_static.json'; original = path.read_bytes()
        for update in (dict(schema='other'), dict(extra=1), dict(source_sha256='0' * 64),
                       dict(boot_id=BOOT.upper()), dict(boot_id='old'), dict(boot_id=None), dict(files=[])):
            self.manifest(**update)
            with self.subTest(update=update): self.reject(self.owner().check)
        for raw in (b'{"boot_id":"duplicate",' + original[1:], original[:-2] + b',"extra":NaN}\n',
                    original[:-2] + b',"extra":1e10000}\n', b' ' * 262145, b'[]', b'null'):
            path.write_bytes(raw); self.reject(self.owner().check)

    def test_manifest_file_set_paths_hashes_and_each_hard_pin_are_enforced(self):
        for name, value in (('src/config.h', 'A' * 64), ('src/config.h', True),
                            ('src/../outside', 'a' * 64), ('src//extra', 'a' * 64),
                            ('src/NUL.txt', 'a' * 64), ('/absolute', 'a' * 64), ('src\\bad', 'a' * 64)):
            self.manifest(files=dict(self.files, **{name: value})); self.reject(self.owner().check)
        missing = dict(self.files); missing.pop('src/config.h')
        self.manifest(files=missing); self.reject(self.owner().check)
        for name in (LEGACY, EXECUTOR, WAIT, *BASELINES.values(), 'tools/app_motor_fault_static_policy.py',
                     STATIC + 'static_remote.py', STATIC + 'static_artifacts.py', STATIC + 'static_native_artifacts.py'):
            path = self.root / name; original = path.read_bytes(); path.write_bytes(original + b'\n# drift\n')
            self.manifest(files=dict(self.files, **{name: digest(path.read_bytes())}))
            with self.subTest(pin=name): self.reject(self.owner().check)
            path.write_bytes(original)

    def test_input_symlinks_and_per_file_bound_refuse(self):
        path = self.root / 'src/config.h'; original = path.read_bytes()
        with path.open('wb') as out: out.truncate(1048577)
        self.manifest(files=dict(self.files, **{'src/config.h': digest(path.read_bytes())}))
        self.reject(self.owner().check)
        path.write_bytes(original); self.manifest(); path.unlink()
        try: path.symlink_to(self.root / 'tools/app_build_pins.json')
        except OSError as error: self.skipTest('Host cannot create symlink: ' + str(error))
        self.reject(self.owner().check)

    def test_staging_map_exact_real_bytes_and_no_old_stage_reuse(self):
        owner = self.controlled(self.owner()); owner.local(); owner.prepare(); owner.claim(); owner.stage()
        actual = {p.relative_to(owner.stage_path).as_posix(): p.read_bytes()
                  for p in owner.stage_path.rglob('*') if p.is_file()}
        self.assertEqual(actual, self.expected)
        self.assertEqual(source_hash(actual), self.source)
        self.assertEqual(owner.stage_attempt, ATTEMPT)
        self.assertEqual(owner.stage_hashes, {name: digest(raw) for name, raw in self.expected.items()})

    def test_stage_collision_cannot_be_hidden_by_manifest(self):
        path = self.root / 'bench/app_motor_fault/src/motor_fault.h'
        path.write_bytes(b'unapproved collision')
        self.manifest(files=dict(self.files, **{path.relative_to(self.root).as_posix(): digest(path.read_bytes())}))
        self.reject(self.owner().check)

    def test_manifest_and_source_are_rechecked_after_admission(self):
        owner = self.owner(); owner.local()
        for relative in ('src/config.h', 'bench/app_motor_fault/app_motor_fault.ino',
                         'bench/motor_fault/src/motor_fault.h', REMOTE_HELPER):
            path = self.root / relative; raw = path.read_bytes(); path.write_bytes(raw + b'\n')
            with self.subTest(path=relative): self.reject(owner.local)
            path.write_bytes(raw)
        extra = self.root / 'src/new_unadmitted.h'; extra.write_bytes(b'extra')
        self.reject(owner.local)

    def test_tracked_output_changes_remain_disallowed_after_claim(self):
        owner = self.owner(); owner.local(); owner.prepare(); owner.claim()
        self.dirty = [('??', RAW + '/native_static01/intent.json')]
        owner.local()
        self.dirty = [(' M', RAW + '/native_static01/intent.json')]
        self.reject(owner.local)

    def test_low_local_space_stops_before_any_owner_or_transport(self):
        owner = self.owner()
        with mock.patch.object(shutil, 'disk_usage', return_value=types.SimpleNamespace(free=128 * 1024**2 - 1)):
            self.reject(owner.run)
        self.assertFalse(owner.stage_owner.exists())

    def test_combined_source_file_count_entry_count_and_bytes_are_bounded(self):
        extra = self.root / 'src/core/d188-fixture'; extra.mkdir()
        for count, size in ((513, 1), (5, 900000)):
            created = []
            for index in range(count):
                path = extra / (str(index) + '.h'); path.write_bytes(b'x' * size); created.append(path)
            names = dict(self.files)
            names.update({p.relative_to(self.root).as_posix(): digest(p.read_bytes()) for p in created})
            self.manifest(files=names, source_sha256=source_hash(expected_stage(self.root)))
            with self.subTest(count=count, bytes_each=size): self.reject(self.owner().check)
            for path in created: path.unlink()
        for index in range(1025): (extra / str(index)).mkdir()
        self.manifest(); self.reject(self.owner().check)

    def test_reparse_metadata_is_rejected_for_ancestry_and_plain_files(self):
        class Reparse:
            def __init__(self, info):
                self.info = info; self.st_file_attributes = getattr(info, 'st_file_attributes', 0) | 0x400
            def __getattr__(self, name): return getattr(self.info, name)
        lstat, stat = Path.lstat, Path.stat
        for name in ('src', 'src/config.h', 'bench/app_motor_fault', CALLER, CONTRACT):
            target, seen = self.root / name, []
            def wrapped_lstat(path, *args, **kwargs):
                info = lstat(path, *args, **kwargs)
                if path == target: seen.append(True); return Reparse(info)
                return info
            def wrapped_stat(path, *args, **kwargs):
                info = stat(path, *args, **kwargs)
                if path == target and not kwargs.get('follow_symlinks', True):
                    seen.append(True); return Reparse(info)
                return info
            with self.subTest(path=name), mock.patch.object(Path, 'lstat', wrapped_lstat), \
                    mock.patch.object(Path, 'stat', wrapped_stat): self.reject(self.owner().check)
            self.assertTrue(seen, 'Reparse fixture must actually be observed')


class ArtifactReplyContract(CallerFixture):
    def test_exact_synthetic_response_accepted_without_external_effects(self):
        owner = self.owner(); reply = self.remote_fixture.synthetic_reply(); raw = json.dumps(reply)
        with self.no_writes(): self.assertEqual(owner.validate_artifact_reply(raw), reply)

    def test_response_schema_json_types_duplicates_nonfinite_and_errors_fail(self):
        owner = self.owner(); reply = self.remote_fixture.synthetic_reply(); raw = json.dumps(reply)
        malformed = (None, False, 7, {}, [], b'{}', '[]', 'null', '', raw + '{}',
                     '{"schema":"duplicate",' + raw[1:], '{"extra":NaN,' + raw[1:])
        for value in malformed:
            with self.subTest(value=repr(value)[:80]): self.reject(lambda: owner.validate_artifact_reply(value))
        for key, value in (('schema', 'other'), ('status', 'FAILED'), ('first_error', {'type': 'X', 'message': 'bad'}),
                           ('build_path', BUILD + '/'), ('artifacts_path', BUILD), ('extra', None)):
            bad = dict(reply, **{key: value}); self.reject(lambda: owner.validate_artifact_reply(json.dumps(bad)))
        for key in reply:
            bad = copy.deepcopy(reply); bad.pop(key)
            with self.subTest(missing=key): self.reject(lambda: owner.validate_artifact_reply(json.dumps(bad)))

    def test_each_file_record_name_hash_type_size_and_identity_is_checked(self):
        owner = self.owner(); reply = self.remote_fixture.synthetic_reply()
        for selector, limit in self.remote_fixture.LIMITS.items():
            for field, value in (('state', 'missing'), ('sha256', 'A' * 64), ('sha256', '0' * 64),
                                 ('identity', None), ('extra', 1)):
                bad = copy.deepcopy(reply); bad['files'][selector][field] = value
                with self.subTest(selector=selector, field=field):
                    self.reject(lambda: owner.validate_artifact_reply(json.dumps(bad)))
            for field in ('device', 'inode', 'bytes', 'mtime_ns', 'ctime_ns'):
                for value in (-1, True, '1'):
                    bad = copy.deepcopy(reply); bad['files'][selector]['identity'][field] = value
                    self.reject(lambda: owner.validate_artifact_reply(json.dumps(bad)))
            for size in (0, limit + 1):
                bad = copy.deepcopy(reply); bad['files'][selector]['identity']['bytes'] = size
                self.reject(lambda: owner.validate_artifact_reply(json.dumps(bad)))
        for selector in list(reply['files']):
            bad = copy.deepcopy(reply); bad['files'].pop(selector)
            self.reject(lambda: owner.validate_artifact_reply(json.dumps(bad)))

    def test_installed_hash_layout_and_every_final_check_bind_response(self):
        owner = self.owner(); original = self.remote_fixture.synthetic_reply()
        for key in ('loader', 'tls_source'):
            bad = copy.deepcopy(original); bad[key]['sha256'] = '0' * 64
            self.reject(lambda: owner.validate_artifact_reply(json.dumps(bad)))
        for key, value in (('project', 'app.ino'), ('fqbn', 'arduino:zephyr:unoq'),
                           ('flags', FLAGS.replace('MOTORS_ALLOWED=0', 'MOTORS_ALLOWED=1')),
                           ('status', 'OTHER')):
            bad = copy.deepcopy(original); bad['layout'][key] = value
            self.reject(lambda: owner.validate_artifact_reply(json.dumps(bad)))
        for name in original['layout']['artifact_sha256']:
            bad = copy.deepcopy(original); bad['layout']['artifact_sha256'][name] = '0' * 64
            self.reject(lambda: owner.validate_artifact_reply(json.dumps(bad)))
        for rows in ([], list(reversed(original['postchecks'])), original['postchecks'] * 2):
            bad = copy.deepcopy(original); bad['postchecks'] = rows
            self.reject(lambda: owner.validate_artifact_reply(json.dumps(bad)))
        for index in range(3):
            for field, value in (('status', 'FAILED'), ('error', {'type': 'X', 'message': 'bad'}), ('extra', 1)):
                bad = copy.deepcopy(original); bad['postchecks'][index][field] = value
                self.reject(lambda: owner.validate_artifact_reply(json.dumps(bad)))


class ExecutionContract(CallerFixture):
    def test_actual_canonical_source_program_accepts_exact_reuse(self):
        owner, source = self.local_source_fixture()
        before = file_set(source.parent)
        self.assertIs(owner.source_admission(), True)
        owner.sources()
        self.assertEqual(file_set(source.parent), before)

    def test_actual_canonical_source_refuses_extra_empty_directory_sibling_and_partial(self):
        owner, source = self.local_source_fixture()
        for path in (source / 'extra-empty', source.parent / 'extra-sibling'):
            path.mkdir()
            with self.subTest(extra=str(path)): self.reject(owner.source_admission)
            self.assertTrue(path.is_dir(), 'Rejected canonical source must never be repaired')
            path.rmdir()
        path = source / next(iter(self.expected)); raw = path.read_bytes(); path.unlink()
        self.reject(owner.source_admission)
        self.assertFalse(path.exists())
        path.write_bytes(raw + b'changed')
        self.reject(owner.source_admission)
        self.assertEqual(path.read_bytes(), raw + b'changed')

    def test_fixed_compile_argv_has_no_upload_reset_or_generic_profile(self):
        owner = self.owner(); owner.local()
        self.assertEqual(owner.compile_command(), self.command())
        self.assertFalse(set(owner.compile_command()) & {'--upload', '--port', '--profile', '--programmer'})

    def test_complete_pipeline_one_query_compiler_fresh_stage_and_closure(self):
        owner = self.controlled(self.owner()); result = owner.run()
        self.assertEqual(result['status'], 'COMPILE_CHECKED')
        self.assertEqual(result['schema'], 'app-motor-fault-static-compile-outcome-v1')
        for name, expected in dict(project=PROJECT, fqbn=FQBN, flags=FLAGS, reviewed_head=HEAD,
                                   boot_id=BOOT, source_sha256=self.source).items():
            self.assertEqual(result[name], expected)
        self.assertEqual((owner.query_calls, owner.compiler_calls), (1, 1))
        self.assertEqual(len(self.packets), 2)
        self.assertEqual(sum('--show-properties=expanded' in p['argv'] for p in self.packets), 1)
        for packet in self.packets:
            self.assertEqual(packet['argv'][0], '/usr/bin/arduino-cli')
            self.assertEqual(packet['argv'][packet['argv'].index('--jobs') + 1], '1')
            self.assertEqual(packet['argv'][-1], self.command()[-1])
        self.assertTrue(all(r['status'] == 'PASS' for r in result['final_checks']))
        self.assertEqual(result['first_error'], None)
        self.assertEqual(self.remote_files, {name: digest(raw) for name, raw in self.expected.items()})

    def test_exact_existing_source_reuses_without_push_partial_refuses_compile(self):
        owner = self.controlled(self.owner(), existing=True)
        result = owner.run(); self.assertEqual(result['status'], 'COMPILE_CHECKED')
        self.assertFalse(any(e[0] == 'transport' and e[2][0] == 'push' for e in self.events))

    def test_partial_existing_canonical_source_refuses_without_repair(self):
        owner = self.controlled(self.owner(), existing=True, partial=True)
        self.reject(owner.run)
        self.assertEqual(owner.compiler_calls, 0)
        self.assertFalse(any(e[0] == 'transport' and e[2][0] == 'push' for e in self.events))

    def test_failed_prerequisite_prevents_stage_and_compile_but_closes_independently(self):
        owner = self.controlled(self.owner()); primary = RuntimeError('first prerequisite failed')
        self.inventory_failure = primary
        with self.assertRaises(RuntimeError) as caught: owner.run()
        self.assertIs(caught.exception, primary)
        self.assertEqual(owner.compiler_calls, 0)
        self.assertFalse(owner.stage_path.exists())
        self.assertEqual(primary.compile_outcome['status'], 'FAILED')
        self.assertGreaterEqual(len(primary.compile_outcome['final_checks']), 4)

    def test_compiler_failure_identity_survives_final_result_write_failure(self):
        owner = self.controlled(self.owner())
        primary = subprocess.CalledProcessError(43, ['fixture-compiler'], output='partial', stderr='original')
        self.compile_failure = primary
        original = owner.save
        def save(path, value):
            if Path(path).name == 'result.json': raise OSError(errno.ENOSPC, 'secondary result write')
            return original(path, value)
        self.patch(owner, 'save', save)
        with self.assertRaises(subprocess.CalledProcessError) as caught: owner.run()
        self.assertIs(caught.exception, primary)
        self.assertEqual(primary.stderr, 'original')
        self.assertEqual(primary.compile_outcome['status'], 'FAILED')
        self.assertIn('original', json.dumps(primary.compile_outcome['first_error']))

    def test_compiler_timeout_is_not_retried_and_final_checks_still_run(self):
        owner = self.controlled(self.owner())
        primary = subprocess.TimeoutExpired(['fixture-compiler'], 810, output=b'partial')
        self.compile_failure = primary
        with self.assertRaises(subprocess.TimeoutExpired) as caught: owner.run()
        self.assertIs(caught.exception, primary)
        self.assertEqual(owner.compiler_calls, 1)
        self.assertGreaterEqual(len(primary.compile_outcome['final_checks']), 6)

    def test_manifest_byte_drift_after_query_prevents_compiler(self):
        owner = self.controlled(self.owner())
        path = self.root / RAW / 'inputs_static.json'
        self.after_query = lambda: path.write_bytes(path.read_bytes() + b' ')
        self.reject(owner.run)
        self.assertEqual(owner.compiler_calls, 0)

    def test_changed_raw_compile_metadata_is_rejected_by_actual_adapter(self):
        owner = self.controlled(self.owner())
        def mutate(result):
            raw = base64.b64decode(result['stdout_base64']).decode()
            raw = raw.replace('compiler.cpp.extra_flags=' + FLAGS,
                              'compiler.cpp.extra_flags=-DMATCH=0 -DMOTORS_ALLOWED=0')
            result['stdout_base64'] = base64.b64encode(raw.encode()).decode()
            result['stdout_bytes'] = len(raw.encode())
        self.reply_mutation = mutate
        self.reject(owner.run)
        self.assertEqual(owner.query_calls, 1)
        self.assertEqual(owner.compiler_calls, 0)

    def test_returned_nonzero_compiler_keeps_streams_and_closes(self):
        owner = self.controlled(self.owner())
        def mutate(result):
            if len(self.packets) == 2:
                result['status'] = 'FAILED'; result['execution']['returncode'] = 43
        self.reply_mutation = mutate
        with self.assertRaises(subprocess.CalledProcessError) as caught: owner.run()
        self.assertEqual(caught.exception.returncode, 43)
        self.assertIn('builder_result', caught.exception.stdout)
        self.assertEqual(caught.exception.compile_outcome['status'], 'FAILED')

    def test_successful_child_with_failed_result_receipt_is_not_success(self):
        owner = self.controlled(self.owner()); original = owner.save
        def save(path, value):
            if Path(path).name == 'result.json': raise OSError(errno.ENOSPC, 'result receipt unavailable')
            return original(path, value)
        self.patch(owner, 'save', save)
        with self.assertRaises(OSError) as caught: owner.run()
        self.assertEqual(caught.exception.compile_outcome['status'], 'FAILED')

    def test_all_closing_actions_are_attempted_after_each_prior_failure(self):
        owner = self.controlled(self.owner())
        primary = RuntimeError('original compiler failure'); self.compile_failure = primary
        original = owner.direct
        final_phase = []
        def direct(program, label, timeout=90):
            if label == 'checked-command':
                values = {n.targets[0].id: n.value for n in ast.parse(program).body
                    if isinstance(n, ast.Assign) and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name)}
                if '--show-properties=expanded' not in ast.literal_eval(values['packet'])['argv']:
                    final_phase.append(True)
            if final_phase and label in ('identity', 'source-set'):
                self.events.append(('closing-failed', label)); raise RuntimeError('closing ' + label)
            return original(program, label, timeout)
        self.patch(owner, 'direct', direct)
        original_inventory = owner.prerequisite
        def prerequisite(name):
            if final_phase:
                self.events.append(('closing-failed', name)); raise RuntimeError('closing ' + name)
            return original_inventory(name)
        self.patch(owner, 'prerequisite', prerequisite)
        def policy(overrides=False):
            self.events.append(('closing-failed', 'policy')); raise RuntimeError('closing policy')
        self.patch(owner, 'final_policy', policy)
        with self.assertRaises(RuntimeError) as caught: owner.run()
        self.assertIs(caught.exception, primary)
        failed = {e[1] for e in self.events if e[0] == 'closing-failed'}
        self.assertTrue({'identity', 'source-set', 'initialization', 'builtins', 'policy'} <= failed)
        self.assertEqual(primary.compile_outcome['first_error']['message'], str(primary))

    def test_successful_compile_cannot_survive_artifact_final_identity_drift(self):
        owner = self.controlled(self.owner()); direct = owner.direct
        def changed(program, label, timeout=90):
            if label == 'artifacts-final':
                self.artifact_reply['files']['build/' + PROJECT + '.map']['identity']['inode'] += 1
            return direct(program, label, timeout)
        self.patch(owner, 'direct', changed)
        with self.assertRaises(REJECTIONS) as caught: owner.run()
        self.assertEqual(caught.exception.compile_outcome['status'], 'FAILED')
        self.assertEqual(owner.compiler_calls, 1)

    def test_actual_artifact_program_fits_real_windows_command_and_bound_enforced(self):
        owner = self.owner(); owner.local(); owner.prepare(); owner.claim()
        program = owner.artifact_program()
        self.assertIs(type(program), str)
        captured = []
        def process(arguments, **kwargs):
            captured.append((arguments, kwargs))
            return subprocess.CompletedProcess(arguments, 0, b'{}', b'')
        self.patch(subprocess, 'run', process)
        owner.direct(program, 'artifacts')
        self.assertEqual(len(captured), 1)
        arguments = captured[0][0]
        self.assertEqual(arguments[1:3], ['-s', BOARD])
        native_argv = [ADB, *arguments[1:]]
        units = len(subprocess.list2cmdline(native_argv).encode('utf-16-le')) // 2 + 1
        self.assertLessEqual(units, 30000, 'Actual checked-source command must fit unchanged Windows bound')
        captured.clear()
        self.reject(lambda: owner.direct('x' * 40000, 'oversize'))
        self.assertFalse(captured, 'Oversize command must fail before subprocess dispatch')


if __name__ == '__main__':
    unittest.main(verbosity=2)
