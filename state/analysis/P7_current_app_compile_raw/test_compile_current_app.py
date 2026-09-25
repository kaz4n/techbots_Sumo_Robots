# Controlled contract tests for the current-app compile-only composition.
# Freeze before first execution; implementation was unread when this oracle was authored.
# Run with Python -B; all command execution is substituted and fixtures use /dev/shm.
"""Spec-derived oracle; reused-context, same-model author, not a fresh phase review.

Only the contract, existing board_tool public build/stage code and frozen original
executor were inspected. Worker supplied seam signatures and reply schemas only.
Local fixture manifests are synthetic test data, never actual invocation scopes.
Historical child lifecycle coverage is reused, not reconstructed here.
"""
import ast
import base64
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import types
import unittest
from unittest import mock


REPO = Path(__file__).resolve().parents[3]
REL = 'state/analysis/P7_current_app_compile_raw'
CALLER = REL + '/compile_current_app.py'
CONTRACT = 'state/analysis/P7_current_app_compile_contract.md'
EXECUTOR = 'state/analysis/P7_motor_fault_raw/compile_motor_fault.py'
WAIT = 'state/analysis/P7_static_startup_raw/capture_remote.py'
BASELINES = {
    'initialization': 'state/analysis/P7_static_startup_raw/cli_initialization_inventory.json',
    'builtins': 'state/analysis/P7_static_startup_raw/cli_builtin_files_inventory.json',
}
FIXED = [CALLER, CONTRACT, 'tools/board_tool.py', 'tools/app_build_policy.py',
         'tools/app_build_commands.json', 'tools/app_build_pins.json',
         'tools/match_deploy.py', EXECUTOR, WAIT, *BASELINES.values()]
SOURCE = '37a2099f6938baf6430cfed2b5a002793d9748820fe0876e9cd039fd94330c29'
BOOT = '55c386b9-fe6d-4388-a7f4-1d91e0bb49d8'
HEAD = '1234567890abcdef1234567890abcdef12345678'
BOARD = '2629958581'
REMOTE_ROOT = '/home/arduino/sumox26_codex_build'
ADB = 'C:/Users/narut/AppData/Local/Arduino15/packages/arduino/tools/adb/32.0.0/adb.exe'
POLICY = 'native-app-v1'
_MODULE = None


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def encode(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':')) + '\n').encode()


def load_sut():
    global _MODULE
    if _MODULE is None:
        spec = importlib.util.spec_from_file_location('controlled_current_app', REPO / CALLER)
        _MODULE = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(_MODULE)
    return _MODULE


def file_set(root):
    return {p.relative_to(root).as_posix(): digest(p.read_bytes())
            for p in root.rglob('*') if p.is_file()}


class ContractCase(unittest.TestCase):
    def setUp(self):
        self.sut = load_sut()
        parent = '/dev/shm' if Path('/dev/shm').is_dir() else None
        self.temp = tempfile.TemporaryDirectory(prefix='current-app-contract-', dir=parent)
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        names = FIXED + [p.relative_to(REPO).as_posix()
                         for p in (REPO / 'src').rglob('*') if p.is_file()]
        for name in names:
            dest = self.root / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes((REPO / name).read_bytes())
        self.manifest_files = {name: digest((self.root / name).read_bytes()) for name in names}
        self.head, self.dirty = HEAD, []
        self.events, self.packets = [], []
        self.transport_error = None
        self.receipt_change = None
        self.child_execution = dict(returncode=0, timed_out=False, reaped=True)
        self.after_query = None
        self.manifest('bench')
        self.manifest('match')
        self.patch(self.sut.CompileCurrent, 'git_state', lambda owner: (self.head, self.dirty))
        self.patch(subprocess, 'run', side_effect=AssertionError('Unsubstituted process forbidden'))
        self.patch(shutil, 'disk_usage', return_value=types.SimpleNamespace(free=2**30))
        adb = Path(ADB if os.name == 'nt' else '/mnt/c/' + ADB[3:])
        self.patch(self.sut, 'ADB', str(adb))

    def patch(self, obj, name, *args, **kwargs):
        patcher = mock.patch.object(obj, name, *args, **kwargs)
        value = patcher.start()
        self.addCleanup(patcher.stop)
        return value

    def manifest(self, selected, **updates):
        value = dict(schema='current-app-compile-inputs-v1', profile=selected,
                     source_sha256=SOURCE, boot_id=BOOT, files=dict(self.manifest_files))
        value.update(updates)
        path = self.root / REL / ('inputs_' + selected + '.json')
        path.write_bytes(encode(value))
        return path

    def owner(self, profile='bench'):
        owner = self.sut.CompileCurrent(profile, HEAD, root=self.root)
        self.patch(sys, 'pycache_prefix', str(self.root / REL / ('native_' + profile + '01') / 'pycache'))
        return owner

    def assert_rejected(self, operation):
        with self.assertRaises((ValueError, RuntimeError, OSError, SystemExit)):
            operation()

    def controlled(self, owner, *, existing=False, partial=False, collision=False):
        """Replace command endpoints, not admission, staging, runner or closure."""
        self.remote_files = {}
        self.compile_failure = None
        self.prerequisite_change = None
        self.identity = dict(uid=1000, user='arduino', boot_id=BOOT,
                             cli_sha256='b878632298958d61fd1eb19e70ac5d2e803d83db8930bc72dc6915eee6e8f433',
                             free_bytes=2**31, conflicts=[])
        self.patch(owner, 'transport', lambda arguments, timeout, label:
                   self.fake_transport(owner, arguments, timeout, label))

        def direct(program, label, timeout=90):
            self.events.append(('direct', label, timeout))
            folder = self.command_folder(owner, label)
            if label == 'identity':
                if collision and 'lexists' in program:
                    raise RuntimeError('Controlled remote command owner exists')
                value = self.identity
            elif label == 'command-owner':
                if collision:
                    raise RuntimeError('Controlled remote command owner exists')
                value = self.identity
            elif label == 'source-admission':
                if existing:
                    self.remote_files = file_set(owner.stage_path)
                    if partial:
                        del self.remote_files[next(iter(self.remote_files))]
                value = {'reused': existing}
            elif label == 'source-set':
                value = self.remote_files
            elif label == 'checked-command':
                assignments = {node.targets[0].id: node.value for node in ast.parse(program).body
                               if isinstance(node, ast.Assign) and len(node.targets) == 1
                               and isinstance(node.targets[0], ast.Name)}
                packet = ast.literal_eval(assignments['packet'])
                self.packets.append((packet, timeout, program))
                self.assertEqual(ast.literal_eval(assignments['BOOT']), BOOT)
                self.assertEqual(ast.literal_eval(assignments['CLI']), '/usr/bin/arduino-cli')
                if self.compile_failure and '--show-properties=expanded' not in packet['argv']:
                    raise self.compile_failure
                if self.after_query and '--show-properties=expanded' in packet['argv']:
                    self.after_query()
                out, err = b'{}', b''
                value = dict(status='COMPLETED', execution=dict(self.child_execution),
                             stdout_base64=base64.b64encode(out).decode(),
                             stderr_base64=base64.b64encode(err).decode(),
                             stdout_bytes=len(out), stderr_bytes=len(err))
            else:
                raise AssertionError('Unexpected direct endpoint: ' + label)
            return subprocess.CompletedProcess([], 0, encode(value), b''), folder

        self.patch(owner, 'direct', direct)
        original_loader = owner.load_board

        def load_board():
            board = original_loader()
            board.compile_app = lambda *args, **kwargs: self.fake_compile(owner, *args, **kwargs)
            return board

        self.patch(owner, 'load_board', load_board)
        self.patch(owner, 'final_policy', lambda overrides=False:
                   self.events.append(('policy', overrides)))
        return owner

    def command_folder(self, owner, label):
        self.assertTrue((owner.output / 'intent.json').is_file(), 'Intent before any command')
        owner.counter += 1
        folder = owner.output / ('%04d-controlled-%s' % (owner.counter, label))
        folder.mkdir()
        return folder

    def fake_transport(self, owner, arguments, timeout, label):
        self.events.append(('transport', label, arguments, timeout))
        folder = self.command_folder(owner, label)
        if self.transport_error:
            raise self.transport_error
        if arguments[0] == 'push':
            self.assertEqual(timeout, 60)
            local, remote = Path(arguments[1]), arguments[2]
            tail = local.relative_to(owner.stage_path).as_posix()
            self.assertEqual(remote, REMOTE_ROOT + '/' + SOURCE + '/app/' + tail)
            self.remote_files[tail] = digest(local.read_bytes())
            return subprocess.CompletedProcess(arguments, 0, b'', b''), folder
        import shlex
        candidates = [(name, json.loads((self.root / path).read_bytes()))
                      for name, path in BASELINES.items()]
        for name, baseline in candidates:
            if arguments == ['shell', '-T', shlex.join(baseline['argv'])]:
                self.assertEqual(timeout, 60)
                value = json.loads(baseline['stdout'])
                value['identity']['boot_id'] = BOOT
                if self.prerequisite_change:
                    self.prerequisite_change(name, value)
                return subprocess.CompletedProcess(arguments, 0, encode(value), b''), folder
        raise AssertionError('Unexpected transport endpoint: ' + repr(arguments[:2]))

    def fake_compile(self, owner, board, checksum, sketch, remote_root, fqbn, flags, startup,
                     project='app.ino', *, command_runner=None):
        profile = owner.profile
        expected = ('arduino:zephyr:unoq', '-DMATCH=0 -DMOTORS_ALLOWED=0', 'default')
        if profile == 'match':
            expected = ('arduino:zephyr:unoq:wait_linux_boot=no',
                        '-DMATCH=1 -DMOTORS_ALLOWED=1', 'immediate')
        self.assertEqual((board, checksum, sketch, remote_root, project),
                         (BOARD, SOURCE, REMOTE_ROOT + '/' + SOURCE + '/app', REMOTE_ROOT, 'app.ino'))
        self.assertEqual((fqbn, flags, startup), expected)
        self.assertTrue(callable(command_runner))
        self.events.append(('compile_app', profile))
        build_id = '0123456789abcdef0123456789abcdef' if profile == 'bench' else 'fedcba9876543210fedcba9876543210'
        run_root = '%s/_app_builds/%s/%s/%s-%s/%s' % (remote_root, POLICY, checksum, profile, startup, build_id)
        build, artifacts = run_root + '/build', run_root + '/artifacts'
        command = ['arduino-cli', 'compile', '--json', '--fqbn', fqbn,
                   '--build-path', build, '--output-dir', artifacts,
                   '--build-property', 'compiler.cpp.extra_flags=' + flags,
                   '--build-property', 'compiler.c.extra_flags=' + flags,
                   '--build-property', 'build.library_discovery_phase_flag=-DARDUINO_LIBRARY_DISCOVERY_PHASE=0', sketch]
        command_runner(board, command[:-1] + ['--show-properties=expanded', sketch], capture=True)
        command_runner(board, command, capture=True)
        receipt = self.root / 'build/app-receipts' / build_id
        receipt.mkdir(parents=True)
        report = dict(policy=POLICY, source_sha256=checksum, fqbn=fqbn, build_path=build,
                      artifacts=artifacts, file_sha256={}, compiler_returncode=0,
                      used_libraries=[], resolved_directories=dict(data='/home/arduino/.arduino15',
                      user='/home/arduino/Arduino'), precompile_checks=True)
        if self.receipt_change:
            self.receipt_change(report, command)
        (receipt / 'command.json').write_bytes(encode(command))
        (receipt / 'verified.json').write_bytes(encode(report))
        # A newer irrelevant receipt must never replace the returned build's receipt.
        decoy = self.root / 'build/app-receipts' / ('f' * 32)
        decoy.mkdir(exist_ok=True)
        (decoy / 'verified.json').write_bytes(b'{"decoy":true}')
        return artifacts

    def test_cli_exact_forms_and_no_io_for_invalid_forms(self):
        for action in ('--check-only', '--execute'):
            for profile in ('bench', 'match'):
                self.assertEqual(self.sut.parse_request(
                    [action, '--profile', profile, '--reviewed-head', HEAD]),
                    (action, profile, HEAD))
        bad = [[], None, True, '--execute', ['--execute'],
               ['--execute', '--profile', 'app', '--reviewed-head', HEAD],
               ['--execute', '--profile', 'bench', '--reviewed-head', HEAD.upper()],
               ['--execute', '--profile', 'bench', '--reviewed-head', '0' * 39],
               ['--profile', 'bench', '--execute', '--reviewed-head', HEAD],
               ['--execute', '--profile', 'bench', '--reviewed-head', HEAD, '--upload'],
               ['--execute', '--profile', False, '--reviewed-head', HEAD],
               ['--execute', '--profile', 'bench', '--reviewed-head', 7]]
        with mock.patch.object(Path, 'read_bytes', side_effect=AssertionError('Invalid CLI did I/O')):
            for argv in bad:
                with self.subTest(argv=argv):
                    self.assert_rejected(lambda: self.sut.parse_request(argv))

    def test_constructor_rejects_invalid_profile_and_head_without_io(self):
        with mock.patch.object(Path, 'read_bytes', side_effect=AssertionError('Constructor did I/O')):
            for profile, head in [('app', HEAD), (False, HEAD), ('bench', None),
                                  ('match', HEAD.upper()), ('bench', HEAD + '0')]:
                with self.subTest(profile=profile, head=head):
                    self.assert_rejected(lambda: self.sut.CompileCurrent(profile, head, root=self.root))

    def test_check_only_is_read_only_and_reports_exact_profile_paths(self):
        for profile in ('bench', 'match'):
            owner = self.owner(profile)
            before = file_set(self.root)
            result = owner.check()
            self.assertEqual(file_set(self.root), before)
            for key, value in dict(profile=profile, reviewed_head=HEAD, source_sha256=SOURCE,
                                   boot_id=BOOT, remote=REMOTE_ROOT + '/current-app-' + profile + '01',
                                   sketch=REMOTE_ROOT + '/' + SOURCE + '/app').items():
                self.assertEqual(result[key], value)
            self.assertEqual(Path(result['output']), self.root / REL / ('native_' + profile + '01'))
            self.assertEqual(Path(result['stage']), self.root / 'build/stage' / ('current-app-' + profile + '01') / 'app')
            self.assertFalse(Path(result['output']).exists())
            self.assertFalse(Path(result['stage']).parent.exists())

    def test_check_rejects_head_dirty_tracked_and_untracked_changes(self):
        for head, dirty in [('f' * 40, []), (HEAD, [(' M', 'src/config.h')]),
                            (HEAD, [('??', 'stray.txt')]),
                            (HEAD, [(' M', REL + '/native_bench01/result.json')])]:
            self.head, self.dirty = head, dirty
            with self.subTest(head=head, dirty=dirty):
                self.assert_rejected(self.owner().check)

    def test_bytecode_and_execute_prefix_admission(self):
        owner = self.owner()
        with mock.patch.object(sys, 'dont_write_bytecode', False):
            self.assert_rejected(owner.check)
        with mock.patch.object(sys, 'pycache_prefix', str(self.root / 'wrong')):
            self.assert_rejected(owner.run)
        self.assertFalse((self.root / REL / 'native_bench01').exists())

    def test_manifest_identity_types_duplicate_keys_and_nonfinite_are_rejected(self):
        path = self.root / REL / 'inputs_bench.json'
        original = path.read_bytes()
        mutations = [dict(profile='match'), dict(source_sha256='e' * 64), dict(boot_id='old-boot'),
                     dict(schema='other'), dict(extra=True), dict(files=[])]
        for change in mutations:
            self.manifest('bench', **change)
            with self.subTest(change=change):
                self.assert_rejected(self.owner().check)
        for raw in [b'{"profile":"bench",' + original[1:],
                    original[:-2] + b',"extra":NaN}\n', b' ' * 262145]:
            path.write_bytes(raw)
            self.assert_rejected(self.owner().check)

    def test_manifest_exact_set_path_digest_and_plain_file_rules(self):
        for name, value in [('src/../outside', 'a' * 64), ('src//extra', 'a' * 64),
                            ('src/NUL.txt', 'a' * 64), ('src/config.h', 'A' * 64),
                            ('src/config.h', 7)]:
            changed = dict(self.manifest_files, **{name: value})
            self.manifest('bench', files=changed)
            with self.subTest(name=name, value=value):
                self.assert_rejected(self.owner().check)
        changed = dict(self.manifest_files)
        del changed['src/config.h']
        self.manifest('bench', files=changed)
        self.assert_rejected(self.owner().check)
        self.manifest('bench')
        path = self.root / 'src/config.h'
        old = path.read_bytes()
        path.write_bytes(old + b'\n// drift\n')
        self.assert_rejected(self.owner().check)
        path.unlink()
        path.symlink_to(self.root / 'tools/app_build_commands.json')
        self.assert_rejected(self.owner().check)

    def test_manifest_cannot_repin_historical_executor(self):
        path = self.root / EXECUTOR
        path.write_bytes(path.read_bytes() + b'\n# changed pinned input\n')
        files = dict(self.manifest_files)
        files[EXECUTOR] = digest(path.read_bytes())
        self.manifest('bench', files=files)
        self.assert_rejected(self.owner().check)

    def test_existing_owner_and_stage_of_any_type_refuse_before_commands(self):
        paths = [self.root / REL / 'native_bench01',
                 self.root / 'build/stage/current-app-bench01']
        for path in paths:
            path.parent.mkdir(parents=True, exist_ok=True)
            for directory in (False, True):
                if directory:
                    path.mkdir()
                else:
                    path.write_bytes(b'occupied')
                with self.subTest(path=path, directory=directory):
                    self.assert_rejected(self.owner().run)
                path.rmdir() if directory else path.unlink()

    def test_both_profiles_fresh_stage_canonical_paths_and_bounded_single_compile(self):
        for profile in ('bench', 'match'):
            with self.subTest(profile=profile):
                owner = self.controlled(self.owner(profile))
                self.packets.clear()
                result = owner.run()
                self.assertEqual(result['schema'], 'current-app-compile-outcome-v1')
                self.assertEqual(result['status'], 'COMPILE_CHECKED')
                self.assertEqual(result['compiler_calls'], 1)
                self.assertEqual(result['query_calls'], 1)
                self.assertEqual(result['source_sha256'], SOURCE)
                self.assertEqual(result['boot_id'], BOOT)
                self.assertEqual(result['reviewed_head'], HEAD)
                self.assertIsNone(result['first_error'])
                self.assertTrue(result['final_checks'])
                self.assertTrue(all(row['status'] == 'PASS' for row in result['final_checks']))
                self.assertEqual(self.remote_files, file_set(owner.stage_path))
                self.assertEqual(len(self.packets), 2)
                for (packet, outer, program), deadline in zip(self.packets, (60, 720)):
                    argv = packet['argv']
                    self.assertEqual(argv[:3], ['/usr/bin/arduino-cli', '--config-file', '/dev/null'])
                    self.assertEqual(argv[3], 'compile')
                    self.assertEqual(argv.count('--jobs'), 1)
                    self.assertEqual(argv[argv.index('--jobs') + 1], '1')
                    self.assertEqual(packet['deadline'], deadline)
                    self.assertEqual(outer, deadline + 90)
                    self.assertEqual(argv[-1], REMOTE_ROOT + '/' + SOURCE + '/app')
                    self.assertNotIn('upload', argv)
                    self.assertNotIn('--clean', argv)
                    # The exact frozen lifecycle suffix and wait functions remain composed.
                    original = ast.parse((REPO / EXECUTOR).read_bytes())
                    child = next(ast.literal_eval(node.value) for node in original.body
                                 if isinstance(node, ast.Assign) and any(
                                     isinstance(t, ast.Name) and t.id == 'REMOTE_CHILD' for t in node.targets))
                    self.assertTrue(program.endswith(child))
                    wait_source = (REPO / WAIT).read_text(encoding='utf-8')
                    defs = {n.name: ast.get_source_segment(wait_source, n)
                            for n in ast.parse(wait_source).body if isinstance(n, ast.FunctionDef)}
                    for name in ('stop_child', 'wait_child'):
                        self.assertIn(defs[name], program)
                receipt = self.root / result['receipt']
                self.assertTrue(receipt.is_file())
                self.assertNotEqual(receipt.parent.name, 'f' * 32)
                self.assertEqual(receipt.parent.name, result['artifacts'].split('/')[-2])
                self.assertEqual(json.loads((owner.output / 'result.json').read_bytes()), result)
                count = len(self.events)
                self.assert_rejected(owner.run)
                self.assertEqual(len(self.events), count, 'Consumed profile cannot dispatch again')

    def test_existing_exact_remote_source_is_reused_without_push(self):
        owner = self.controlled(self.owner(), existing=True)
        result = owner.run()
        self.assertEqual(result['status'], 'COMPILE_CHECKED')
        self.assertFalse(any(event[0] == 'transport' and event[2][0] == 'push' for event in self.events))
        self.assertEqual(self.remote_files, file_set(owner.stage_path))

    def test_partial_remote_source_is_refused_without_overwrite_or_compile(self):
        owner = self.controlled(self.owner(), existing=True, partial=True)
        self.assert_rejected(owner.run)
        self.assertFalse(any(event[0] == 'transport' and event[2][0] == 'push' for event in self.events))
        self.assertFalse(any(event[0] == 'compile_app' for event in self.events))

    def test_remote_command_owner_collision_stops_compile(self):
        owner = self.controlled(self.owner(), collision=True)
        self.assert_rejected(owner.run)
        self.assertFalse(any(event[0] == 'compile_app' for event in self.events))

    def test_low_local_space_prevents_staging(self):
        owner = self.controlled(self.owner())
        with mock.patch.object(shutil, 'disk_usage', return_value=types.SimpleNamespace(free=128 * 2**20 - 1)):
            self.assert_rejected(owner.run)
        self.assertFalse(owner.stage_path.exists())
        self.assertFalse(any(event[0] == 'compile_app' for event in self.events))

    def test_prerequisite_old_boot_stops_before_stage_and_closes_both_inventories(self):
        owner = self.controlled(self.owner())
        self.prerequisite_change = lambda name, value: value['identity'].update(boot_id='old-boot')
        with self.assertRaises(Exception) as caught:
            owner.run()
        result = caught.exception.compile_outcome
        self.assertEqual(result['status'], 'FAILED')
        self.assertEqual(result['compiler_calls'], 0)
        self.assertFalse(owner.stage_path.exists())
        labels = [event[1] for event in self.events if event[0] == 'transport']
        self.assertGreaterEqual(len(labels), 3, 'Failed first prerequisite plus both independent closing inventories')
        self.assertGreaterEqual(sum(row['status'] == 'FAILED' for row in result['final_checks']), 2)

    def test_prerequisite_payload_change_cannot_be_hidden_by_current_boot(self):
        owner = self.controlled(self.owner())
        self.prerequisite_change = lambda name, value: value['files'][0].update(sha256='f' * 64)
        self.assert_rejected(owner.run)
        self.assertFalse(owner.stage_path.exists())
        self.assertFalse(any(event[0] == 'compile_app' for event in self.events))

    def test_prerequisite_timestamp_changes_only_are_accepted(self):
        owner = self.controlled(self.owner())
        def timestamps(name, value):
            def walk(item):
                if isinstance(item, dict):
                    for key in tuple(item):
                        if key in ('mtime_ns', 'ctime_ns'):
                            item[key] = 0
                        else:
                            walk(item[key])
                elif isinstance(item, list):
                    for child in item:
                        walk(child)
            walk(value)
        self.prerequisite_change = timestamps
        self.assertEqual(owner.run()['status'], 'COMPILE_CHECKED')

    def test_source_drift_after_query_prevents_compiler_and_fails_closure(self):
        owner = self.controlled(self.owner())
        path = self.root / 'src/config.h'
        self.after_query = lambda: path.write_bytes(path.read_bytes() + b'\n// controlled drift\n')
        self.assert_rejected(owner.run)
        self.assertEqual(len(self.packets), 1, 'Source drift must prevent compiler dispatch')
        result = json.loads((owner.output / 'result.json').read_bytes())
        self.assertEqual(result['status'], 'FAILED')
        self.assertTrue(any(row['status'] == 'FAILED' for row in result['final_checks']))

    def test_changed_manifest_bytes_after_query_prevent_compiler(self):
        owner = self.controlled(self.owner())
        path = self.root / REL / 'inputs_bench.json'
        self.after_query = lambda: path.write_bytes(path.read_bytes() + b' ')
        self.assert_rejected(owner.run)
        self.assertEqual(len(self.packets), 1)

    def test_returned_receipt_wrong_source_is_rejected(self):
        owner = self.controlled(self.owner())
        self.receipt_change = lambda report, command: report.update(source_sha256='0' * 64)
        self.assert_rejected(owner.run)
        self.assertEqual(json.loads((owner.output / 'result.json').read_bytes())['status'], 'FAILED')

    def test_receipt_compile_flags_are_checked(self):
        owner = self.controlled(self.owner())
        self.receipt_change = lambda report, command: command.__setitem__(
            command.index('compiler.cpp.extra_flags=-DMATCH=0 -DMOTORS_ALLOWED=0'),
            'compiler.cpp.extra_flags=-DMATCH=1 -DMOTORS_ALLOWED=1')
        self.assert_rejected(owner.run)

    def test_receipt_boolean_return_code_is_not_integer_zero(self):
        owner = self.controlled(self.owner())
        self.receipt_change = lambda report, command: report.update(compiler_returncode=False)
        self.assert_rejected(owner.run)

    def test_receipt_requires_precompile_checks(self):
        owner = self.controlled(self.owner())
        self.receipt_change = lambda report, command: report.update(precompile_checks=False)
        self.assert_rejected(owner.run)

    def test_timeout_is_primary_and_all_independent_closing_checks_still_run(self):
        owner = self.controlled(self.owner())
        primary = subprocess.TimeoutExpired(['controlled-compiler'], 810, output=b'partial')
        self.compile_failure = primary
        def bad_policy(overrides=False):
            self.events.append(('policy', overrides))
            raise OSError('Controlled closing ' + str(overrides))
        self.patch(owner, 'final_policy', bad_policy)
        with self.assertRaises(subprocess.TimeoutExpired) as caught:
            owner.run()
        self.assertIs(caught.exception, primary)
        result = primary.compile_outcome
        self.assertEqual(result['status'], 'FAILED')
        self.assertEqual(result['first_error']['type'], 'TimeoutExpired')
        self.assertIn(('policy', False), self.events)
        self.assertIn(('policy', True), self.events)
        self.assertGreaterEqual(sum(row['status'] == 'FAILED' for row in result['final_checks']), 2)
        self.assertGreaterEqual(sum(event[:2] == ('direct', 'identity') for event in self.events), 2)

    def test_child_not_reaped_or_timed_out_cannot_be_compile_checked(self):
        owner = self.controlled(self.owner())
        self.child_execution = dict(returncode=0, timed_out=True, reaped=False)
        self.assert_rejected(owner.run)
        self.assertEqual(len(self.packets), 1, 'Rejected query child must prevent compiler')

    def test_result_save_error_preserves_primary_exception(self):
        owner = self.controlled(self.owner())
        primary = subprocess.CalledProcessError(7, ['controlled-compiler'], 'stdout', 'stderr')
        self.compile_failure = primary
        original = owner.save
        def save(name, value):
            if name in ('result', 'result.json'):
                raise OSError('Controlled result save failure')
            return original(name, value)
        self.patch(owner, 'save', save)
        with self.assertRaises(subprocess.CalledProcessError) as caught:
            owner.run()
        self.assertIs(caught.exception, primary)
        self.assertEqual(primary.compile_outcome['status'], 'FAILED')
        self.assertEqual(primary.compile_outcome['first_error']['type'], 'CalledProcessError')
        self.assertIn('Controlled result save failure', json.dumps(primary.compile_outcome))

    def test_result_save_error_turns_success_into_failure(self):
        owner = self.controlled(self.owner())
        original = owner.save
        def save(name, value):
            if name in ('result', 'result.json'):
                raise OSError('Controlled result save failure')
            return original(name, value)
        self.patch(owner, 'save', save)
        with self.assertRaises(OSError) as caught:
            owner.run()
        self.assertEqual(caught.exception.compile_outcome['status'], 'FAILED')


if __name__ == '__main__':
    if not sys.dont_write_bytecode:
        raise SystemExit('Run controlled tests with Python -B')
    unittest.main(verbosity=2)
