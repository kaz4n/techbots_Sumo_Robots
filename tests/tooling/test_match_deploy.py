# Tests D183 guarded precompiled MATCH deployment from its public contract.
# Separates synthetic qualification and permission records from real authorization.
# Freeze before Python -B execution; owned RAM fixtures and mocked remote calls only.
from contextlib import ExitStack, contextmanager
import builtins
import copy
from datetime import datetime, timedelta, timezone
import errno
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest import mock

from tests.tooling.test_match_payload import (
    ROOT, SOURCE, BUILD, RUN, BOOT, PARENT, FQBN, bindings, canonical, digest,
    load, output_path, reply)

NOW = datetime(2026, 9, 25, 10, 0, tzinfo=timezone.utc)
SOFTWARE = tuple('tools/' + name for name in (
    'board_tool.py', 'app_build_policy.py', 'app_build_pins.json', 'app_build_commands.json',
    'match_upload.py', 'match_payload.py', 'match_deploy.py'))
FROZEN_FILES = (
    'state/analysis/P7_static_link_probe_raw/static_remote.py',
    'state/analysis/P7_static_startup_raw/capture_remote.py',
    'state/analysis/P7_static_startup_raw/upload_remote.py',
    'state/analysis/P7_static_startup_raw/startup_run.py',
    'state/analysis/P7_static_startup_raw/cli_initialization_inventory.json',
    'state/analysis/P7_static_startup_raw/cli_builtin_files_inventory.json')
SCOPE = 'state/analysis/synthetic_match_scope.json'


def put(root, relative, raw):
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(raw)
    return {'path': relative, 'bytes': len(raw), 'sha256': digest(raw)}


def put_json(root, relative, value):
    return put(root, relative, canonical(value))


def args(**kwargs):
    values = dict(sketch='app', match=True, compile_only=False, startup=None,
                  run_ui_adc_probe=None, deploy_scope=SCOPE)
    values.update(kwargs)
    return SimpleNamespace(**values)


class SourceFixture(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='sumox_d183_', dir='/dev/shm')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        module_path = mock.patch.object(sys, 'path', [str(ROOT / 'tools'), *sys.path])
        module_path.start()
        self.addCleanup(module_path.stop)
        self.subject = load(ROOT / 'tools/match_deploy.py', 'd183_deploy_subject')
        self.board_tool = load(ROOT / 'tools/board_tool.py', 'd183_existing_board')
        self.source_files = {'src/app/app.ino': b'void setup() {}\nvoid loop() {}\n',
                            'src/config.h': b'#pragma once\n',
                            'src/core/core.h': b'// core\n', 'src/hal/port.h': b'// hal\n'}
        for path, raw in self.source_files.items():
            put(self.root, path, raw)
        self.mapped = {'app.ino': self.source_files['src/app/app.ino'],
                       'src/config.h': self.source_files['src/config.h'],
                       'src/core/core.h': self.source_files['src/core/core.h'],
                       'src/hal/port.h': self.source_files['src/hal/port.h']}
        guard = mock.patch.object(subprocess, 'Popen',
                                  side_effect=AssertionError('Native process forbidden'))
        guard.start()
        self.addCleanup(guard.stop)

    def expected_source_hash(self):
        expected = self.root / 'expected-staged'
        expected.mkdir()
        for path, raw in self.mapped.items():
            put(expected, path, raw)
        return self.board_tool.source_hash(expected)


class MatchRequestAndSourceTests(SourceFixture):
    def test_D183_request_selection_and_missing_flag_preserve_existing_route(self):
        self.assertIs(self.subject.validate_request(args()), True)
        self.assertIs(self.subject.validate_request(args(startup='immediate')), True)
        self.assertIs(self.subject.validate_request(args(deploy_scope=None)), False)

    def test_D183_invalid_request_combinations_refuse_before_filesystem_or_target_io(self):
        with mock.patch.object(Path, 'stat', side_effect=AssertionError('filesystem stat')), \
                mock.patch.object(Path, 'open', side_effect=AssertionError('filesystem open')):
            for update in ({'sketch': 'bench/motor_fault'}, {'match': False},
                           {'compile_only': True}, {'startup': 'default'},
                           {'run_ui_adc_probe': 'run01'}):
                with self.subTest(update=update), self.assertRaises(ValueError):
                    self.subject.validate_request(args(**update))

    def test_D183_board_route_dispatches_before_profile_staging_tools_or_target_io(self):
        selected = SimpleNamespace(validate_request=self.subject.validate_request,
                                   upload_precompiled=mock.Mock(return_value={'status': 'ACCEPTED'}))
        with mock.patch.dict(sys.modules, {'match_deploy': selected}):
            board = load(ROOT / 'tools/board_tool.py', 'd183_route_board')
            with ExitStack() as stack:
                for name in ('target', 'require_transport', 'flash_profile', 'stage',
                             'sync_sources', 'verify_core', 'compile_app'):
                    stack.enter_context(mock.patch.object(board, name,
                        side_effect=AssertionError('old route used ' + name)))
                board.flash(args())
            selected.upload_precompiled.assert_called_once_with(board, SCOPE)

    def test_D183_board_cli_invalid_deploy_combination_exits_without_io(self):
        selected = SimpleNamespace(validate_request=self.subject.validate_request,
                                   upload_precompiled=mock.Mock())
        with mock.patch.dict(sys.modules, {'match_deploy': selected}):
            board = load(ROOT / 'tools/board_tool.py', 'd183_invalid_route_board')
            with ExitStack() as stack:
                for name in ('target', 'require_transport', 'flash_profile', 'stage'):
                    stack.enter_context(mock.patch.object(board, name,
                        side_effect=AssertionError('I/O before request validation')))
                stack.enter_context(mock.patch.object(sys, 'argv', ['board_tool.py', 'flash',
                    'app', '--match', '--compile-only', '--deploy-scope', SCOPE]))
                stack.enter_context(mock.patch.object(board, 'report_app_error'))
                self.assertNotEqual(board.main(), 0)
            selected.upload_precompiled.assert_not_called()

    def test_D183_source_mapping_matches_existing_host_path_sorted_hash(self):
        additions = {'src/app/readme.txt': ('readme.txt', b'metadata'),
                     'src/app/Z.h': ('src/app/Z.h', b'uppercase'),
                     'src/app/a.h': ('src/app/a.h', b'lowercase'),
                     'src/app/deep/lib.cpp': ('src/app/deep/lib.cpp', b'support'),
                     'src/app/src/extra/local.S': ('src/extra/local.S', b'local source'),
                     'src/core/.gitkeep': ('src/core/.gitkeep', b'core marker')}
        for source, (destination, raw) in additions.items():
            put(self.root, source, raw)
            self.mapped[destination] = raw
        put(self.root, 'src/app/.gitkeep', b'ignored marker')
        put(self.root, 'src/app/deep/notes.txt', b'ignored nested non C source')
        expected = self.expected_source_hash()
        before = {path.relative_to(self.root).as_posix(): path.read_bytes()
                  for path in self.root.rglob('*') if path.is_file()}
        self.assertEqual(self.subject.app_source_hash(self.root), expected)
        after = {path.relative_to(self.root).as_posix(): path.read_bytes()
                 for path in self.root.rglob('*') if path.is_file()}
        self.assertEqual(after, before)
        self.assertFalse((self.root / 'build').exists())

    def test_D183_source_changed_bytes_change_digest(self):
        before = self.subject.app_source_hash(self.root)
        put(self.root, 'src/core/core.h', b'// changed\n')
        self.assertNotEqual(self.subject.app_source_hash(self.root), before)

    def test_D183_source_rejects_case_insensitive_destination_collision(self):
        put(self.root, 'src/app/A.h', b'upper')
        put(self.root, 'src/app/a.h', b'lower')
        with self.assertRaises(ValueError):
            self.subject.app_source_hash(self.root)

    def test_D183_source_reserved_local_roots_and_sketch_metadata_refused(self):
        for relative in ('src/app/src/config.h', 'src/app/src/core', 'src/app/src/hal',
                         'src/app/src/app', 'src/app/sketch.yaml',
                         'src/app/sketch.yml', 'src/app/sketch.json'):
            with self.subTest(relative=relative):
                path = self.root / relative
                put(self.root, relative, b'forbidden')
                with self.assertRaises(ValueError):
                    self.subject.app_source_hash(self.root)
                path.unlink()

    def test_D183_source_missing_app_symlink_and_root_link_refused(self):
        source = self.root / 'src/app/app.ino'
        source.unlink()
        with self.assertRaises((ValueError, OSError)):
            self.subject.app_source_hash(self.root)
        source.symlink_to(self.root / 'src/config.h')
        with self.assertRaises(ValueError):
            self.subject.app_source_hash(self.root)
        source.unlink()
        source.write_bytes(self.source_files['src/app/app.ino'])
        link = self.root / 'root-link'
        link.symlink_to(self.root, target_is_directory=True)
        with self.assertRaises(ValueError):
            self.subject.app_source_hash(link)

    def test_D183_source_file_count_and_byte_bounds(self):
        oversized = self.root / 'src/app/large.txt'
        oversized.write_bytes(b'x' * (1048576 + 1))
        with self.assertRaises(ValueError):
            self.subject.app_source_hash(self.root)
        oversized.unlink()
        for number in range(510):
            put(self.root, 'src/core/f' + str(number) + '.h', b'x')
        with self.assertRaises(ValueError):
            self.subject.app_source_hash(self.root)

    def test_D183_source_total_byte_limit(self):
        for number in range(4):
            put(self.root, 'src/app/large' + str(number) + '.txt', b'x' * 1048576)
        with self.assertRaises(ValueError):
            self.subject.app_source_hash(self.root)


class AdmissionFixture(SourceFixture):
    def setUp(self):
        super().setUp()
        self.source = self.expected_source_hash()
        self.bound = bindings(self.source)
        self.now = NOW
        for path in (*SOFTWARE, *FROZEN_FILES):
            put(self.root, path, (ROOT / path).read_bytes())
        self.policy = load(self.root / 'tools/app_build_policy.py', 'd183_policy_fixture')
        self.compiler = load(ROOT / 'tests/tooling/test_app_build_policy.py', 'd183_compile_fixture')
        self.request = {'run_id': RUN, 'build_id': BUILD, 'source_sha256': self.source,
                        'source_commit': 'c' * 40, 'target': 'synthetic-target', 'transport': 'adb',
                        'bindings': self.bound, 'build_receipts': {},
                        'software': {path: self.pin(path) for path in SOFTWARE},
                        'qualification': {}}
        self.make_receipts()
        self.evidence = put(self.root, 'state/analysis/synthetic_measurement.txt',
                            b'SYNTHETIC TEST ONLY - not physical evidence or permission\n')
        self.qualification = {'schema': 'match-operation-qualification-v1',
            'source_sha256': self.source, 'raw_sha256': self.bound['files']['raw']['sha256'],
            'package_sha256': self.bound['files']['sketch']['sha256'],
            'operation_image_sha256': '', 'operation': 'stand',
            'verdict': 'QUALIFIED_FOR_IDENTIFIED_OPERATION', 'reviewer': 'synthetic reviewer',
            'limitations': ['synthetic unit fixture only'], 'evidence': [self.evidence]}
        self.authorization = {'schema': 'match-human-authorization-v1', 'request_sha256': '',
            'reply': 'STAND OK', 'message_ref': 'synthetic-unittest-not-human',
            'issued_utc': (NOW - timedelta(minutes=5)).isoformat(),
            'expires_utc': (NOW + timedelta(minutes=5)).isoformat()}
        self.refresh()

    def pin(self, relative):
        raw = (self.root / relative).read_bytes()
        return {'path': relative, 'bytes': len(raw), 'sha256': digest(raw)}

    def make_receipts(self):
        runroot = PARENT + '/_app_builds/native-app-v1/' + self.source + '/match-immediate/' + BUILD
        build_path, artifacts = runroot + '/build', runroot + '/artifacts'
        doc = json.loads(json.dumps(self.compiler.sample()).replace(self.compiler.BUILD_PATH, build_path))
        flags = '-DMATCH=1 -DMOTORS_ALLOWED=1'
        for key, value in (('build.fqbn', FQBN), ('compiler.c.extra_flags', flags),
                           ('compiler.cpp.extra_flags', flags), ('build.boot_mode', 'immediate')):
            self.compiler.set_property(doc, key, value)
        self.policy.validate_result(json.dumps(doc), FQBN, flags, build_path)
        hashes = self.policy.installed_pins('/home/arduino/.arduino15')
        hashes.update({build_path + '/app.ino' + suffix: 'a' * 64
                       for suffix in ('.elf', '_debug.elf', '_temp.elf')})
        hashes[artifacts + '/app.ino.elf-zsk.bin'] = 'a' * 64
        for pin in self.bound['files'].values():
            if pin['path'] in hashes:
                pin['sha256'] = hashes[pin['path']]
        self.verified = {'policy': 'native-app-v1', 'source_sha256': self.source, 'fqbn': FQBN,
            'build_path': build_path, 'artifacts': artifacts, 'file_sha256': hashes,
            'compiler_returncode': 0, 'used_libraries': [], 'precompile_checks': True,
            'resolved_directories': {'data': '/home/arduino/.arduino15', 'user': '/home/arduino/Arduino'}}
        self.command = ['arduino-cli', 'compile', '--json', '--fqbn', FQBN,
            '--build-path', build_path, '--output-dir', artifacts,
            '--build-property', 'compiler.cpp.extra_flags=' + flags,
            '--build-property', 'compiler.c.extra_flags=' + flags,
            '--build-property', 'build.library_discovery_phase_flag=-DARDUINO_LIBRARY_DISCOVERY_PHASE=0',
            PARENT + '/' + self.source + '/app']
        self.result = doc
        self.save_receipts()

    def save_receipts(self):
        folder = 'build/app-receipts/' + BUILD + '/'
        for role, name, value in (('verified', 'verified.json', self.verified),
                                  ('command', 'command.json', self.command),
                                  ('result', 'compile.stdout.json', self.result)):
            self.request['build_receipts'][role] = put_json(self.root, folder + name, value)

    def refresh(self, *, image=True, authorization_digest=True):
        if image:
            selected = {name: self.request[name] for name in ('target', 'transport', 'source_sha256')}
            selected.update(fqbn=FQBN, operation=self.qualification['operation'])
            selected.update({name: self.bound[name] for name in ('files', 'directories', 'absent')})
            self.qualification['operation_image_sha256'] = digest(canonical(selected))
        self.request['qualification'] = put_json(self.root, 'state/analysis/synthetic_qualification.json',
                                                 self.qualification)
        if authorization_digest:
            self.authorization['request_sha256'] = digest(canonical(self.request))
        auth = put_json(self.root, 'state/analysis/synthetic_authorization.json', self.authorization)
        self.scope = {'schema': 'match-deploy-v1', 'request': self.request, 'authorization': auth}
        put_json(self.root, SCOPE, self.scope)

    def admit(self, **kwargs):
        options = dict(now=self.now)
        options.update(kwargs)
        return self.subject.load_scope(self.root, SCOPE, 'synthetic-target', 'adb', **options)

    def reject(self, **kwargs):
        with self.assertRaises((ValueError, OSError)):
            self.admit(**kwargs)


class MatchAdmissionTests(AdmissionFixture):
    def test_D183_valid_scope_is_read_only_detached_and_digest_bound(self):
        before = (self.root / SCOPE).read_bytes()
        result = self.admit()
        self.assertEqual(result['request'], self.request)
        self.assertEqual(result['scope_sha256'], digest(before))
        self.assertEqual(result['request_sha256'], digest(canonical(self.request)))
        self.assertEqual(result['profile']['fixed']['output'], output_path(self.source))
        self.assertEqual((self.root / SCOPE).read_bytes(), before)
        self.assertFalse((self.root / 'state/analysis' / ('match_deploy_' + RUN)).exists())
        result['request']['bindings']['files']['raw']['path'] = '/changed'
        self.assertEqual(self.admit()['request'], self.request)

    def test_D183_local_admission_does_not_require_windows_unavailable_resource_module(self):
        original_import = builtins.__import__
        def without_resource(name, *args, **kwargs):
            if name == 'resource':
                raise ImportError('resource unavailable on Windows')
            return original_import(name, *args, **kwargs)
        with mock.patch.object(builtins, '__import__', side_effect=without_resource), \
                mock.patch.dict(sys.modules, {'resource': None}):
            self.assertEqual(self.admit()['request'], self.request)

    def test_D183_policy_uses_checked_json_content_without_later_path_read_text(self):
        original_read = Path.read_text
        def no_policy_reopen(path, *args, **kwargs):
            if path.name in ('app_build_pins.json', 'app_build_commands.json'):
                raise AssertionError('unchecked policy JSON reopen')
            return original_read(path, *args, **kwargs)
        with mock.patch.object(Path, 'read_text', no_policy_reopen):
            self.assertEqual(self.admit()['request'], self.request)

    def test_D183_scope_and_request_missing_or_unknown_fields_rejected(self):
        original = copy.deepcopy(self.scope)
        for container in ('scope', 'request'):
            values = original if container == 'scope' else original['request']
            for key in (*values, 'unknown'):
                value = copy.deepcopy(original)
                target = value if container == 'scope' else value['request']
                if key == 'unknown':
                    target[key] = None
                else:
                    del target[key]
                put_json(self.root, SCOPE, value)
                self.reject()
        put_json(self.root, SCOPE, original)

    def test_D183_scope_duplicate_nonfinite_and_oversize_json_rejected(self):
        original = canonical(self.scope)
        for raw in (original.replace(b'"schema":', b'"schema":"x","schema":', 1),
                    original.replace(b'"uid":1000', b'"uid":NaN'), b' ' * 65537):
            put(self.root, SCOPE, raw)
            self.reject()

    def test_D183_scope_relative_path_policy_and_nonregular_objects(self):
        for path in ('/absolute.json', '../outside.json', 'a//b', 'a/./b', 'a/../b',
                     'a\\b', 'C:bad', 'a./b', 'CON.json', 'a/NUL/b'):
            with self.subTest(path=path), self.assertRaises((ValueError, OSError)):
                self.subject.load_scope(self.root, path, 'synthetic-target', 'adb', now=NOW)
        link = self.root / 'state/analysis/scope-link.json'
        link.symlink_to(self.root / SCOPE)
        with self.assertRaises(ValueError):
            self.subject.load_scope(self.root, link.relative_to(self.root).as_posix(),
                                    'synthetic-target', 'adb', now=NOW)

    def test_D183_configured_target_transport_and_aware_now_are_required(self):
        for target, transport in (('other', 'adb'), ('synthetic-target', 'ssh')):
            with self.assertRaises(ValueError):
                self.subject.load_scope(self.root, SCOPE, target, transport, now=NOW)
        self.reject(now=NOW.replace(tzinfo=None))

    def test_D183_source_and_current_software_drift_rejected(self):
        for relative in ('src/core/core.h', 'tools/board_tool.py', FROZEN_FILES[0]):
            path = self.root / relative
            original = path.read_bytes()
            path.write_bytes(original + b'\n')
            self.reject()
            path.write_bytes(original)

    def test_D183_pins_require_exact_fields_types_bytes_and_hash(self):
        for update in ({'bytes': True}, {'bytes': 0}, {'bytes': 1}, {'sha256': 'A' * 64},
                       {'sha256': 'f' * 64}, {'path': 'tools/../tools/board_tool.py'}, {'extra': 1}):
            original = copy.deepcopy(self.request['software'])
            self.request['software']['tools/board_tool.py'].update(update)
            self.refresh()
            self.reject()
            self.request['software'] = original

    def test_D183_software_roles_and_build_receipt_paths_are_closed(self):
        original = copy.deepcopy(self.request)
        del self.request['software']['tools/match_upload.py']
        self.refresh()
        self.reject()
        self.request = copy.deepcopy(original)
        self.request['software']['tools/extra.py'] = self.pin('tools/board_tool.py')
        self.refresh()
        self.reject()
        self.request = copy.deepcopy(original)
        pin = self.request['build_receipts']['command']
        self.request['build_receipts']['command'] = put(self.root, 'build/elsewhere.json',
                                                       (self.root / pin['path']).read_bytes())
        self.refresh()
        self.reject()

    def test_D183_verified_compile_flags_returncode_and_dependency_hashes_must_match(self):
        original = copy.deepcopy(self.verified)
        changes = ({'compiler_returncode': True}, {'compiler_returncode': 1},
                   {'fqbn': 'arduino:zephyr:unoq'}, {'used_libraries': ['external']},
                   {'precompile_checks': 1}, {'resolved_directories': {'data': '/wrong', 'user': '/wrong'}},
                   {'file_sha256': {}}, {'extra': None})
        for update in changes:
            with self.subTest(update=update):
                self.verified = {**copy.deepcopy(original), **update}
                self.save_receipts()
                self.refresh()
                self.reject()

    def test_D183_compiler_result_and_saved_command_must_be_valid_not_just_hashed(self):
        original = copy.deepcopy(self.result)
        self.result['success'] = False
        self.save_receipts()
        self.refresh()
        self.reject()
        self.result = original
        self.command.append('--upload')
        self.save_receipts()
        self.refresh()
        self.reject()

    def test_D183_every_runtime_dependency_overlapping_compile_hashes_must_agree(self):
        for role in ('loader', 'boards', 'platform'):
            with self.subTest(role=role):
                original = self.bound['files'][role]['sha256']
                self.bound['files'][role]['sha256'] = 'f' * 64
                self.refresh()
                self.reject()
                self.bound['files'][role]['sha256'] = original

    def test_D183_artifact_bindings_qualification_and_actual_evidence_are_required(self):
        raw = (self.root / self.evidence['path']).read_bytes()
        (self.root / self.evidence['path']).write_bytes(b'changed')
        self.reject()
        (self.root / self.evidence['path']).write_bytes(raw)
        for name, bad in (('raw_sha256', 'f' * 64), ('package_sha256', 'f' * 64),
                          ('source_sha256', 'f' * 64), ('verdict', 'COMPILED'),
                          ('reviewer', ''), ('evidence', []), ('limitations', 'none')):
            original = copy.deepcopy(self.qualification)
            self.qualification[name] = bad
            self.refresh()
            self.reject()
            self.qualification = original

    def test_D183_operation_image_binds_target_files_and_operation(self):
        self.qualification['operation_image_sha256'] = 'f' * 64
        self.refresh(image=False)
        self.reject()
        self.qualification['operation'] = 'ring'
        self.authorization['reply'] = 'RING OK'
        self.refresh()
        self.assertEqual(self.admit()['request']['qualification'], self.request['qualification'])

    def test_D183_authorization_reply_request_and_message_reference_are_exact(self):
        original = copy.deepcopy(self.authorization)
        for update in ({'reply': 'RING OK'}, {'reply': True}, {'message_ref': ''},
                       {'request_sha256': 'f' * 64}, {'unknown': True}):
            self.authorization = {**original, **update}
            self.refresh(authorization_digest=False)
            self.reject()

    def test_D183_authorization_interval_is_utc_current_positive_and_at_most_one_hour(self):
        original = copy.deepcopy(self.authorization)
        cases = ({'issued_utc': (NOW + timedelta(seconds=1)).isoformat()},
                 {'expires_utc': NOW.isoformat()}, {'expires_utc': (NOW - timedelta(seconds=1)).isoformat()},
                 {'issued_utc': (NOW - timedelta(hours=2)).isoformat()},
                 {'issued_utc': '2026-09-25T09:55:00'},
                 {'issued_utc': '2026-09-25T13:55:00+04:00'})
        for update in cases:
            self.authorization = {**original, **update}
            self.refresh()
            self.reject()


class MatchDeploymentTests(AdmissionFixture):
    def setUp(self):
        super().setUp()
        self.calls, self.remote_hook = [], None
        self.board = SimpleNamespace(ROOT=self.root, target=lambda: 'synthetic-target',
            transport=lambda: 'adb', require_transport=mock.Mock(),
            remote=self.remote, SSH_OPTIONS=['-o', 'BatchMode=yes'],
            adb_executable=lambda: 'adb', report_app_error=mock.Mock())
        self.inventories = [json.loads((self.root / path).read_text()) for path in FROZEN_FILES[-2:]]
        self.owner = self.root / 'state/analysis' / ('match_deploy_' + RUN)

    def remote(self, target, command, *, capture=False, timeout=None):
        self.assertEqual(target, 'synthetic-target')
        self.assertIs(capture, True)
        self.assertTrue((self.owner / 'attempt.json').is_file(), 'durable intent must precede remote')
        self.calls.append((list(command), timeout))
        if self.remote_hook is not None:
            injected = self.remote_hook(len(self.calls), command)
            if injected is not None:
                return injected
        for inventory in self.inventories:
            if command == inventory['argv']:
                self.assertEqual(timeout, 90)
                value = json.loads(inventory['stdout'])
                value['identity']['boot_id'] = BOOT
                return SimpleNamespace(returncode=0, stdout=canonical(value).decode(), stderr='')
        self.assertEqual(timeout, 240)
        value = reply(command[-2], self.source)
        return SimpleNamespace(returncode=0, stdout=canonical(value).decode(), stderr='')

    def deploy(self):
        return self.subject.upload_precompiled(self.board, SCOPE, now=NOW)

    def failed(self):
        with self.assertRaises(Exception) as caught:
            self.deploy()
        self.assertTrue(hasattr(caught.exception, 'deploy_outcome'))
        return caught.exception, caught.exception.deploy_outcome

    @contextmanager
    def outcome_disk_full(self):
        def selected(path):
            if not isinstance(path, (str, bytes, os.PathLike)):
                return False
            candidate = Path(os.fsdecode(path))
            return candidate == self.owner / 'outcome.json' or candidate == Path('outcome.json')
        def text_open(original):
            def guarded(path, mode='r', *args, **kwargs):
                if selected(path) and any(flag in mode for flag in 'wax+'):
                    raise OSError(errno.ENOSPC, 'synthetic receipt disk full')
                return original(path, mode, *args, **kwargs)
            return guarded
        original_os_open = os.open
        def os_open(path, flags, *args, **kwargs):
            if selected(path) and flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT):
                raise OSError(errno.ENOSPC, 'synthetic receipt disk full')
            return original_os_open(path, flags, *args, **kwargs)
        with ExitStack() as stack:
            stack.enter_context(mock.patch.object(Path, 'open', text_open(Path.open)))
            stack.enter_context(mock.patch.object(io, 'open', text_open(io.open)))
            stack.enter_context(mock.patch.object(builtins, 'open', text_open(builtins.open)))
            stack.enter_context(mock.patch.object(os, 'open', os_open))
            yield

    def test_D183_success_claims_once_dispatches_2_1_2_and_saves_exact_outcome(self):
        outcome = self.deploy()
        self.assertEqual((outcome['schema'], outcome['status'], outcome['attempts']),
                         ('match-deploy-outcome-v1', 'ACCEPTED', 1))
        expected = {'schema', 'run_id', 'source_sha256', 'scope_sha256', 'request_sha256',
            'target', 'transport', 'status', 'attempts', 'remote_result', 'commands',
            'first_error', 'postcheck_errors', 'started_utc', 'finished_utc'}
        self.assertEqual(set(outcome), expected)
        self.assertEqual(len(self.calls), 5)
        self.assertEqual([timeout for _, timeout in self.calls], [90, 90, 240, 90, 90])
        self.assertEqual(self.calls[:2], self.calls[-2:])
        self.assertEqual(json.loads((self.owner / 'outcome.json').read_text()), outcome)
        self.assertEqual(self.owner.stat().st_mode & 0o777, 0o700)
        self.board.require_transport.assert_called_once_with(sync=False)
        self.assertIsNone(outcome['first_error'])
        self.assertEqual(outcome['postcheck_errors'], [])
        for command in outcome['commands']:
            self.assertEqual(set(command), {'label', 'argv_sha256', 'returncode', 'stdout', 'stderr', 'error'})

    def test_D183_existing_or_dangling_claim_never_reused(self):
        self.owner.symlink_to(self.root / 'missing-owner')
        with self.assertRaises((ValueError, OSError)):
            self.deploy()
        self.assertTrue(self.owner.is_symlink())
        self.assertEqual(self.calls, [])
        self.owner.unlink()
        self.owner.mkdir()
        with self.assertRaises((ValueError, OSError)):
            self.deploy()
        self.assertEqual(self.calls, [])

    def test_D183_prerequisite_failure_never_dispatches_upload_and_closing_checks_run(self):
        def hook(number, command):
            if number == 1:
                return SimpleNamespace(returncode=1, stdout='missing prerequisite', stderr='unavailable')
        self.remote_hook = hook
        error, outcome = self.failed()
        self.assertEqual((outcome['status'], outcome['attempts']), ('FAILED', 0))
        self.assertGreaterEqual(len(self.calls), 3)
        self.assertFalse(any(timeout == 240 for _, timeout in self.calls))
        self.assertEqual(self.calls[-2:], [(item['argv'], 90) for item in self.inventories])
        self.assertTrue(any(row['stdout'] == 'missing prerequisite' for row in outcome['commands']))

    def test_D183_wrong_boot_and_changed_prerequisite_payload_fail_before_upload(self):
        def hook(number, command):
            if number == 1:
                value = json.loads(self.inventories[0]['stdout'])
                value['identity']['boot_id'] = 'f' * 36
                return SimpleNamespace(returncode=0, stdout=canonical(value).decode(), stderr='')
        self.remote_hook = hook
        _, outcome = self.failed()
        self.assertEqual((outcome['status'], outcome['attempts']), ('FAILED', 0))
        self.assertFalse(any(timeout == 240 for _, timeout in self.calls))

    def test_D183_prerequisite_content_drift_rejected_with_correct_current_identity(self):
        def hook(number, command):
            if number == 1:
                value = json.loads(self.inventories[0]['stdout'])
                value['identity']['boot_id'] = BOOT
                value['files'][0]['sha256'] = 'f' * 64
                return SimpleNamespace(returncode=0, stdout=canonical(value).decode(), stderr='')
        self.remote_hook = hook
        _, outcome = self.failed()
        self.assertEqual((outcome['status'], outcome['attempts']), ('FAILED', 0))
        self.assertFalse(any(timeout == 240 for _, timeout in self.calls))

    def test_D183_projection_ignores_only_timestamps_and_dictionary_list_order(self):
        def project_fixture(value):
            if type(value) is dict:
                return {key: 1 if key in ('mtime_ns', 'ctime_ns') else project_fixture(item)
                        for key, item in value.items()}
            if type(value) is list:
                items = [project_fixture(item) for item in value]
                return items[::-1] if all(type(item) is dict for item in items) else items
            return value
        def hook(number, command):
            for inventory in self.inventories:
                if command == inventory['argv']:
                    value = project_fixture(json.loads(inventory['stdout']))
                    value['identity']['boot_id'] = BOOT
                    return SimpleNamespace(returncode=0, stdout=canonical(value).decode(), stderr='')
        self.remote_hook = hook
        self.assertEqual(self.deploy()['status'], 'ACCEPTED')
        self.assertEqual(len(self.calls), 5)

    def test_D183_upload_transport_timeout_is_unknown_keeps_raw_output_and_never_retries(self):
        primary = subprocess.TimeoutExpired('synthetic remote', 240, output='partial stdout', stderr='partial stderr')
        def hook(number, command):
            if number == 3:
                raise primary
        self.remote_hook = hook
        error, outcome = self.failed()
        self.assertIs(error, primary)
        self.assertEqual((outcome['status'], outcome['attempts']), ('UNKNOWN', 1))
        self.assertEqual(len(self.calls), 5)
        self.assertTrue(any(row['stdout'] == 'partial stdout' and row['stderr'] == 'partial stderr'
                            for row in outcome['commands']))

    def test_D183_exit_zero_with_unaccepted_reply_is_unknown(self):
        self.remote_hook = lambda number, command: (
            SimpleNamespace(returncode=0, stdout='{}', stderr='') if number == 3 else None)
        _, outcome = self.failed()
        self.assertEqual((outcome['status'], outcome['attempts']), ('UNKNOWN', 1))
        self.assertEqual(len(self.calls), 5)

    def test_D183_both_closing_checks_run_independently_after_first_closing_failure(self):
        def hook(number, command):
            if number in (4, 5):
                raise OSError('closing failure ' + str(number))
        self.remote_hook = hook
        _, outcome = self.failed()
        self.assertEqual((outcome['status'], outcome['attempts']), ('UNKNOWN', 1))
        self.assertEqual(len(self.calls), 5)
        self.assertGreaterEqual(len(outcome['postcheck_errors']), 2)

    def test_D183_scope_revalidation_after_prerequisites_prevents_changed_source_upload(self):
        def hook(number, command):
            if number == 2:
                put(self.root, 'src/core/core.h', b'changed between checks')
        self.remote_hook = hook
        _, outcome = self.failed()
        self.assertEqual((outcome['status'], outcome['attempts']), ('FAILED', 0))
        self.assertFalse(any(timeout == 240 for _, timeout in self.calls))
        self.assertEqual(self.calls[-2:], [(item['argv'], 90) for item in self.inventories])

    def test_D183_local_postcheck_independent_of_remote_failures(self):
        def hook(number, command):
            if number == 3:
                put(self.root, 'src/core/core.h', b'changed during upload')
            if number == 4:
                raise OSError('closing inventory failure')
        self.remote_hook = hook
        _, outcome = self.failed()
        self.assertEqual(outcome['status'], 'UNKNOWN')
        self.assertEqual(len(self.calls), 5)
        self.assertGreaterEqual(len(outcome['postcheck_errors']), 2)

    def test_D183_outcome_write_failure_preserves_primary_and_failed_success_raises(self):
        primary = subprocess.TimeoutExpired('synthetic remote', 240)
        def hook(number, command):
            if number == 3:
                raise primary
        self.remote_hook = hook
        with self.outcome_disk_full():
            error, outcome = self.failed()
        self.assertIs(error, primary)
        self.assertEqual(outcome['status'], 'UNKNOWN')
        self.assertGreaterEqual(len(outcome['postcheck_errors']), 1)
        self.assertTrue((self.owner / 'attempt.json').exists())

    def test_D183_successful_upload_with_failed_outcome_save_never_returns_success(self):
        with self.outcome_disk_full():
            error, outcome = self.failed()
        self.assertEqual((outcome['status'], outcome['attempts']), ('UNKNOWN', 1))
        self.assertEqual(len(self.calls), 5)
        self.assertTrue((self.owner / 'attempt.json').is_file())


if __name__ == '__main__':
    unittest.main()
