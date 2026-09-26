# Tests D222 caller admission against its independent public contract.
# Keeps old fixed launchers and inert bench wrappers outside this implementation.
# Host-only fixtures exercise profile identity and compilation without uploading.
import ast
import builtins
from contextlib import ExitStack
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import types
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
SUBJECT = ROOT / 'tools/compile_commissioning_app.py'
HEAD = '0123456789abcdef0123456789abcdef01234567'
SOURCE = 'abcdef0123456789abcdef0123456789abcdef0123456789abcdef0123456789'
PROFILES = ('b4_stand', 'p3_drive', 'p3_turn', 'p3_stop', 'p4_reactive',
            'p4_timing', 'p5_abort_timing')


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def argv(profile='p3_drive', motors=0, attempt='trial01', action='--check-only', head=HEAD):
    return [action, '--profile', profile, '--motors-allowed', str(motors),
            '--attempt', attempt, '--reviewed-head', head]


def request(profile='p3_drive', motors=0, attempt='trial01', action='--check-only', head=HEAD):
    return dict(action=action, profile=profile, motors_allowed=motors,
                attempt=attempt, reviewed_head=head)


def expected_paths(profile, motors, attempt, source=SOURCE):
    digest = hashlib.sha256((source + '\0' + attempt).encode('utf-8')).hexdigest()
    owner = 'commission-' + profile + '-m' + str(motors) + '-' + digest[:12]
    remote = '/home/arduino/sumox26_codex_build/' + owner
    stage_owner = 'build/stage/' + owner
    return dict(owner=owner, output='state/analysis/P7_commissioning_build_raw/' + owner,
                stage_owner=stage_owner, stage=stage_owner + '/app', remote=remote,
                build=remote + '/build', artifacts=remote + '/artifacts',
                sketch='/home/arduino/sumox26_codex_build/' + source + '/app')


class StrSubclass(str):
    pass


class IntSubclass(int):
    pass


class ListSubclass(list):
    pass


class DictSubclass(dict):
    pass


class PublicCallerContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.subject = load(SUBJECT, '_d222_caller_subject')

    def test_all_cli_profiles_modes_actions_and_boundary_tokens(self):
        for profile in PROFILES:
            for motors in (0, 1):
                for action in ('--check-only', '--execute'):
                    for attempt in ('a', 'trial_1', 'a' + '0' * 23):
                        with self.subTest(profile=profile, motors=motors, action=action, attempt=attempt):
                            result = self.subject.parse_request(argv(profile, motors, attempt, action))
                            self.assertEqual(result, request(profile, motors, attempt, action))
                            self.assertIs(type(result['motors_allowed']), int)

    def test_cli_rejects_type_alias_order_repeat_extra_and_shell_text_before_io(self):
        good = argv()
        invalid = [None, {}, (), tuple(good), ListSubclass(good), [], good[:-1],
                   good + ['--upload'], good + ['--execute'], good + ['--profile', 'p3_turn'],
                   ['--profile', good[2], good[0], *good[3:]]]
        for index in range(len(good)):
            changed = list(good); changed[index] = StrSubclass(changed[index]); invalid.append(changed)
            changed = list(good); changed[index] = None; invalid.append(changed)
        for index, values in ((0, ('--upload', '--reset', '--compile-only')),
                              (2, ('P3_DRIVE', 'p3-drive', 'app', 'p3_drive;whoami', '')),
                              (4, ('true', '01', '-1', '2', '0.0', '')),
                              (6, ('../x', '/tmp/x', 'A', '1a', 'a-b', 'a' * 25, 'a b', 'a;id')),
                              (8, (HEAD.upper(), HEAD[:-1], HEAD + '0', 'g' * 40))):
            for value in values:
                changed = list(good); changed[index] = value; invalid.append(changed)
        with mock.patch.object(Path, 'read_bytes', side_effect=AssertionError('CLI validation read source')):
            for value in invalid:
                with self.subTest(argv=value), self.assertRaises((TypeError, ValueError)):
                    self.subject.parse_request(value)

    def test_paths_bind_all_four_inputs_and_keep_full_source_in_sketch(self):
        for profile in PROFILES:
            for motors in (0, 1):
                for attempt in ('a', 'trial_1', 'a' + '0' * 23):
                    with self.subTest(profile=profile, motors=motors, attempt=attempt):
                        result = self.subject.build_paths(profile, motors, attempt, SOURCE)
                        self.assertEqual(result, expected_paths(profile, motors, attempt))
                        self.assertTrue(all(type(value) is str for value in result.values()))
                        self.assertLessEqual(len(result['owner']), 48)
        changed = SOURCE[:12] + ('0' if SOURCE[12] != '0' else '1') + SOURCE[13:]
        first = self.subject.build_paths('p3_drive', 0, 'trial01', SOURCE)
        second = self.subject.build_paths('p3_drive', 0, 'trial01', changed)
        self.assertNotEqual(first['owner'], second['owner'])
        self.assertNotEqual(first['sketch'], second['sketch'])

    def test_paths_reject_nonexact_types_and_confinement_violations(self):
        values = ['p3_drive', 0, 'trial01', SOURCE]
        replacements = ((None, True, StrSubclass('p3_drive'), 'p3_drive/../../x', 'p3-drive'),
                        (None, True, False, IntSubclass(0), 0.0, '0', -1, 2),
                        (None, StrSubclass('trial01'), '../escape', '/absolute', 'a/b', 'a\\b',
                         'A', '1a', 'x' * 25, 'x;id'),
                        (None, StrSubclass(SOURCE), SOURCE.upper(), SOURCE[:-1], 'g' * 64))
        with mock.patch.object(Path, 'read_bytes', side_effect=AssertionError('Invalid path read source')):
            for index, alternatives in enumerate(replacements):
                for value in alternatives:
                    changed = list(values); changed[index] = value
                    with self.subTest(index=index, value=repr(value)), self.assertRaises((TypeError, ValueError)):
                        self.subject.build_paths(*changed)

    def test_request_shape_is_closed_before_primitive_loading(self):
        valid = request()
        invalid = [None, [], DictSubclass(valid), dict(valid, extra=True)]
        for key in valid:
            missing = dict(valid); del missing[key]; invalid.append(missing)
        for key, value in (('profile', StrSubclass('p3_drive')), ('motors_allowed', True),
                           ('attempt', '../old'), ('reviewed_head', HEAD.upper()),
                           ('action', '--upload')):
            invalid.append(dict(valid, **{key: value}))
        for value in invalid:
            for name in ('load_caller', 'make_owner'):
                with self.subTest(method=name, request=value), mock.patch.object(
                        Path, 'read_bytes', side_effect=AssertionError('Invalid request loaded primitive')):
                    with self.assertRaises((TypeError, ValueError)):
                        getattr(self.subject, name)(value, root=ROOT)

    def test_private_modules_and_constructor_head_are_request_bound(self):
        first = self.subject.load_caller(request('p3_drive', 0), root=ROOT)
        second = self.subject.load_caller(request('p4_timing', 1), root=ROOT)
        self.assertIsNot(first, second)
        for module in (first, second):
            with self.assertRaises((TypeError, ValueError)):
                module.CompileDiagnostic('f' * 40, root=ROOT)
        a = first.CompileDiagnostic(HEAD, root=ROOT)
        b = second.CompileDiagnostic(HEAD, root=ROOT)
        self.assertNotEqual(a.flags, b.flags)
        self.assertIn('-DSUMOX_P3_DRIVE_TEST=1', a.flags)
        self.assertIn('-DMOTORS_ALLOWED=0', a.flags)
        self.assertIn('-DSUMOX_P4_REACTIVE=1', b.flags)
        self.assertIn('-DSUMOX_TIMING_EVIDENCE=1', b.flags)
        self.assertIn('-DMOTORS_ALLOWED=1', b.flags)
        self.assertEqual(a.fqbn, 'arduino:zephyr:unoq:link_mode=static')
        self.assertEqual(b.fqbn, a.fqbn)
        for method in ('git_state', 'local', 'transport', 'direct', 'inventory',
                       'prerequisite', 'stage', 'command_runner', 'build', 'closing', 'finish'):
            self.assertTrue(callable(getattr(a, method)), method)


class RemoteSelectionContract(unittest.TestCase):
    def setUp(self):
        if sys.platform == 'win32' and 'pwd' not in sys.modules:
            sentinel = types.ModuleType('pwd')
            sentinel.getpwuid = lambda *args: (_ for _ in ()).throw(AssertionError('Account call on Windows'))
            self.addCleanup(lambda: sys.modules.pop('pwd', None))
            sys.modules['pwd'] = sentinel
        self.subject = load(ROOT / 'tools/commissioning_app_compile_remote.py', '_d222_remote_subject')
        raw = 'state/analysis/P7_static_link_probe_raw/'
        paths = dict(helper=raw + 'static_remote.py', policy='tools/commissioning_app_static_policy.py',
            adapter='tools/app_motor_fault_static_policy.py', common='tools/app_build_policy.py',
            static_policy=raw + 'static_policy.py', reference=raw + 'static_reference.json',
            extension=raw + 'static_native_artifacts.py', base=raw + 'static_artifacts.py',
            primitive='tools/b4_app_compile_remote.py')
        self.bundle = {name: (ROOT / path).read_bytes() for name, path in paths.items()}
        self.selection = dict(profile='p3_drive', motors_allowed=0, attempt='remote01', source_digest=SOURCE)

    def test_every_bundle_member_is_validated_before_any_python_execution(self):
        invalid = [None, {}, DictSubclass(self.bundle), dict(self.bundle, extra=b'x')]
        for key, raw in self.bundle.items():
            missing = dict(self.bundle); del missing[key]; invalid.append(missing)
            subclass_key = dict(missing); subclass_key[StrSubclass(key)] = raw; invalid.append(subclass_key)
            for value in (raw + b'\n', raw[:-1], b'', None, bytearray(raw)):
                invalid.append(dict(self.bundle, **{key: value}))
        paths = expected_paths('p3_drive', 0, 'remote01')
        for index, value in enumerate(invalid):
            with self.subTest(index=index), mock.patch.object(
                    builtins, 'exec', side_effect=AssertionError('Unverified bundle executed')):
                with self.assertRaises((TypeError, ValueError)):
                    self.subject.inspect_artifacts(paths['build'], paths['artifacts'], value, **self.selection)

    def test_remote_profile_and_owner_path_cannot_be_substituted(self):
        paths = expected_paths('p3_drive', 0, 'remote01')
        for name in ('build', 'artifacts'):
            for value in ('/tmp/arbitrary', paths[name] + '/..', paths[name] + '/',
                          expected_paths('p3_turn', 0, 'remote01')[name],
                          expected_paths('p3_drive', 1, 'remote01')[name],
                          expected_paths('p3_drive', 0, 'remote02')[name]):
                changed = dict(paths); changed[name] = value
                with self.subTest(name=name, value=value), mock.patch.object(
                        os, 'open', side_effect=AssertionError('Wrong path opened')):
                    with self.assertRaises((TypeError, ValueError)):
                        self.subject.inspect_artifacts(changed['build'], changed['artifacts'],
                                                       self.bundle, **self.selection)

    @unittest.skipUnless(sys.platform == 'linux', 'Descriptor-backed artifact fixture requires Linux')
    def test_real_descriptor_artifact_observation_and_failed_export_close(self):
        import pwd
        historical = load(ROOT / 'tests/tooling/test_b4_app_compile.py', '_d222_remote_fixtures')
        fixture = historical.remote_fixture()
        packet = fixture.artifact_packet()
        loader = (ROOT / 'state/analysis/P2_ui_adc_probe_raw/root_capture_inputs/zephyr-arduino_uno_q_stm32u585xx.elf').read_bytes()
        tls = (ROOT / 'state/analysis/P7_static_tls_raw/observed/tls-syms.S').read_bytes()
        paths = expected_paths('p3_drive', 0, 'remote01')
        with tempfile.TemporaryDirectory(prefix='sumox-d222-remote-', dir='/dev/shm') as temporary:
            root = Path(temporary)
            contents = {paths['build'] + '/' + name: raw for name, raw in packet.items()}
            export_name = paths['artifacts'] + '/app.ino.bin-zsk.bin'
            contents.update({export_name: packet['app.ino.bin-zsk.bin'], fixture.LOADER: loader, fixture.TLS: tls})
            for name, raw in contents.items():
                path = root / name.lstrip('/'); path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes(raw)
            account = pwd.struct_passwd(('arduino', 'x', os.geteuid(), os.getegid(),
                                        'fixture', '/home/arduino', '/bin/sh'))
            with mock.patch.object(pwd, 'getpwuid', return_value=account), \
                    mock.patch.object(subprocess, 'run', side_effect=AssertionError('No process')):
                result = self.subject.inspect_artifacts(paths['build'], paths['artifacts'], self.bundle,
                                                       fs_root=root, **self.selection)
                self.assertEqual(result['status'], 'ARTIFACTS_CHECKED')
                self.assertEqual(result['profile'], 'p3_drive')
                self.assertEqual(result['motors_allowed'], 0)
                self.assertEqual(result['layout']['status'], 'STATIC_COMMISSIONING_APP_LAYOUT_PACKAGE_PASS')
                self.assertEqual([row['name'] for row in result['postchecks']], ['loader', 'tls_source', 'files'])
                self.assertTrue(all(row['status'] == 'PASS' for row in result['postchecks']))
                (root / export_name.lstrip('/')).write_bytes(b'bad export')
                failed = self.subject.inspect_artifacts(paths['build'], paths['artifacts'], self.bundle,
                                                       fs_root=root, **self.selection)
                self.assertEqual(failed['status'], 'FAILED')
                self.assertIsNotNone(failed['first_error'])
                self.assertEqual([row['name'] for row in failed['postchecks']], ['loader', 'tls_source', 'files'])


def pipeline_cases():
    """Adapt accepted fixture endpoints, preserving real local/policy execution."""
    historical = load(ROOT / 'tests/tooling/test_b4_app_compile.py', '_d222_d214_fixtures')
    base = historical.caller_fixture()
    base.FIXED = sorted(set(base.FIXED) | {
        'tools/compile_commissioning_app.py', 'tools/commissioning_app_static_policy.py',
        'tools/commissioning_app_compile_remote.py',
        'state/analysis/P7_commissioning_build_contract.md'})
    base.BOOT = '55c386b9-fe6d-4388-a7f4-1d91e0bb49d8'
    base.OLD_BOOT = '01234567-89ab-cdef-8123-456789abcdef'

    class CommissioningPipeline(base.CallerFixture):
        @classmethod
        def setUpClass(cls):
            super().setUpClass()
            cls.launcher = load(SUBJECT, '_d222_pipeline_subject')

        def setUp(self):
            super().setUp()
            self.head_bodies = {path.relative_to(self.root).as_posix(): path.read_bytes()
                                for path in self.root.rglob('*') if path.is_file()}
            self.patch(self.launcher, '_head_bytes', self.checked_head)
            (self.root / 'state/analysis/P7_commissioning_build_raw').mkdir(exist_ok=True)

        def checked_head(self, root, head, names):
            self.assertEqual(root, self.root)
            self.assertEqual(head, self.head)
            return {name: self.head_bodies[name] for name in names}

        def owner(self, profile='p4_timing', motors=0, attempt='controlled01'):
            selected = request(profile, motors, attempt, '--execute', self.head)
            owner = self.launcher.make_owner(selected, root=self.root)
            self.patch(owner, 'git_state', lambda: (self.head, self.dirty))
            self.patch(owner.base, 'ADB', base.ADB if os.name == 'nt' else '/mnt/c/' + base.ADB[3:])
            # The accepted endpoints contain only identity metadata in globals.
            for target in (base, self.remote_fixture):
                target.FLAGS, target.BUILD, target.ARTIFACTS = owner.flags, owner.build_path, owner.artifacts
                target.REMOTE, target.ATTEMPT = owner.remote, owner.stage_attempt
            return owner

        def controlled(self, owner, **kwargs):
            super().controlled(owner, **kwargs)
            selected = dict(profile=owner.profile, motors_allowed=owner.motors_allowed,
                            attempt=owner.attempt, source_sha256=owner.source_sha256)
            self.artifact_reply.update(schema='commissioning-app-static-artifacts-v1', **selected)
            self.artifact_reply['layout'].update(
                status='STATIC_COMMISSIONING_APP_LAYOUT_PACKAGE_PASS',
                profile=owner.profile, motors_allowed=owner.motors_allowed)
            return owner

        def test_check_is_read_only_and_manifest_has_full_request_and_head_bytes(self):
            owner = self.owner(); before = base.file_set(self.root)
            with self.no_writes(), mock.patch.object(owner, 'direct', side_effect=AssertionError('Board call')):
                result = owner.check()
            self.assertEqual(base.file_set(self.root), before)
            self.assertFalse(owner.output.exists())
            self.assertFalse(owner.stage_owner.exists())
            self.assertIs(result['board_observed'], False)
            self.assertEqual(result['profile'], 'p4_timing')
            self.assertEqual(result['motors_allowed'], 0)
            self.assertEqual(result['source_sha256'], self.source)
            self.assertEqual(set(owner.inputs), {'schema', 'profile', 'motors_allowed', 'attempt',
                'reviewed_head', 'source_sha256', 'boot_id', 'files'})
            self.assertEqual(owner.inputs['reviewed_head'], self.head)
            self.assertEqual(owner.inputs['attempt'], 'controlled01')
            self.assertEqual(owner.inputs['source_sha256'], self.source)
            for name, digest in owner.inputs['files'].items():
                self.assertEqual(digest, hashlib.sha256(self.head_bodies[name]).hexdigest())

        def test_changed_head_dirty_tree_reviewed_blob_or_source_refuses_before_contact(self):
            for head, changes in (('f' * 40, []), (self.head, [(' M', 'src/config.h')]),
                                  (self.head, [('??', 'unrelated.txt')])):
                owner = self.owner()
                with mock.patch.object(owner, 'git_state', return_value=(head, changes)), \
                        mock.patch.object(owner, 'direct', side_effect=AssertionError('Board call')):
                    self.reject(owner.check)
            name = 'src/config.h'; original = self.head_bodies[name]
            self.head_bodies[name] = original + b'\n'
            self.reject(self.owner().check)
            self.head_bodies[name] = original
            owner = self.owner(); owner.check()
            path = self.root / name; original_file = path.read_bytes()
            path.write_bytes(original_file + b'\n')
            with mock.patch.object(owner, 'direct', side_effect=AssertionError('Board call')):
                self.reject(owner.local)

        def test_existing_output_or_stage_consumes_owner_without_contact(self):
            owner = self.owner()
            for path in (owner.output, owner.stage_owner):
                path.parent.mkdir(parents=True, exist_ok=True)
                path.mkdir()
                with mock.patch.object(owner, 'direct', side_effect=AssertionError('Board call')):
                    self.reject(owner.check)
                path.rmdir()

        def test_real_query_compile_pipeline_and_saved_profile_receipts(self):
            owner = self.controlled(self.owner(motors=1))
            result = owner.run()
            self.assertEqual(result['status'], 'COMPILE_CHECKED')
            self.assertEqual((owner.query_calls, owner.compiler_calls), (1, 1))
            self.assertEqual(result['profile'], 'p4_timing')
            self.assertEqual(result['motors_allowed'], 1)
            self.assertEqual(json.loads((owner.output / 'inputs.json').read_bytes()), owner.inputs)
            self.assertEqual(len(self.packets), 2)
            for index, packet in enumerate(self.packets):
                command = packet['argv']
                self.assertIn('compile', command)
                self.assertEqual('--show-properties=expanded' in command, index == 0)
                self.assertIn('compiler.cpp.extra_flags=' + owner.flags, command)
                self.assertIn('compiler.c.extra_flags=' + owner.flags, command)
                self.assertTrue(('--jobs' in command and command[command.index('--jobs') + 1] == '1')
                                or '--jobs=1' in command)
                self.assertFalse(any(value in ('upload', '--upload', 'reset', 'monitor') for value in command))
            checks = {row['name']: row['status'] for row in result['final_checks']}
            for name in ('local', 'identity', 'initialization', 'builtins', 'remote_sources',
                         'installed_pins', 'overrides', 'artifacts', 'artifact_sources'):
                self.assertEqual(checks[name], 'PASS')
            labels = [row[0] for row in owner.fixture_source_endpoint.calls]
            self.assertEqual(labels, ['artifact-source-first', 'artifact-source-second', 'artifact-sources-final'])
            self.reject(owner.run)

        def test_every_profile_real_metadata_and_generated_compile_command_match_request(self):
            for profile in PROFILES:
                for motors in (0, 1):
                    owner = self.owner(profile, motors); owner.local(); owner.prepare()
                    with self.subTest(profile=profile, motors=motors):
                        policy = owner.static_policy()
                        text = self.metadata()
                        for method in ('validate_preflight', 'validate_compile_result'):
                            result = getattr(policy, method)(text, build_path=owner.build_path, data_dir=base.DATA)
                            self.assertEqual(result['compiler.cpp.extra_flags'], owner.flags)
                        command = owner.compile_command()
                        self.assertIn('compiler.c.extra_flags=' + owner.flags, command)
                        self.assertEqual(command[-1], owner.sketch)

        def test_early_failure_preserves_first_error_and_runs_every_available_closing(self):
            owner = self.controlled(self.owner())
            primary = ValueError('primary prerequisite failure')
            self.patch(owner, 'prerequisites', side_effect=primary)
            self.patch(owner, 'prerequisite', side_effect=ValueError('closing prerequisite failure'))
            with self.assertRaises(ValueError) as caught:
                owner.run()
            self.assertIs(caught.exception, primary)
            result = primary.compile_outcome
            self.assertEqual((owner.query_calls, owner.compiler_calls), (0, 0))
            self.assertEqual([row['name'] for row in result['final_checks']],
                             ['local', 'identity', 'initialization', 'builtins'])
            self.assertEqual(result['first_error']['message'], str(primary))
            self.assertEqual(result['status'], 'FAILED')

        def test_compiler_error_does_not_retry_and_retains_raw_query_and_failure(self):
            owner = self.controlled(self.owner())
            primary = subprocess.TimeoutExpired(['controlled-compiler'], 120, output=b'partial compiler')
            self.compile_failure = primary
            with self.assertRaises(subprocess.TimeoutExpired) as caught:
                owner.run()
            self.assertIs(caught.exception, primary)
            self.assertEqual(len(self.packets), 2)
            self.assertEqual(primary.compile_outcome['first_error']['message'], str(primary))
            self.assertTrue((owner.output / 'result.json').is_file())
            self.assertTrue(any(path.name.endswith('.json') for path in (owner.output / 'compile').iterdir()))
            names = [row['name'] for row in primary.compile_outcome['final_checks']]
            self.assertTrue({'local', 'identity', 'initialization', 'builtins', 'remote_sources',
                             'installed_pins', 'overrides'} <= set(names))

        def test_lost_second_transfer_preserves_partial_and_all_closing(self):
            owner = self.controlled(self.owner())
            endpoint = owner.fixture_source_endpoint
            primary = subprocess.TimeoutExpired(['controlled-transfer'], 90, output=b'lost reply')
            endpoint.failures['artifact-source-second'] = primary
            endpoint.lost_replies.add('artifact-source-second')
            with self.assertRaises(subprocess.TimeoutExpired) as caught:
                owner.run()
            self.assertIs(caught.exception, primary)
            labels = [row[0] for row in endpoint.calls]
            self.assertEqual(labels.count('artifact-source-first'), 1)
            self.assertEqual(labels.count('artifact-source-second'), 1)
            self.assertEqual(labels.count('artifact-sources-final'), 1)
            self.assertIsNone(owner.artifact_sources_identity)
            self.assertEqual(primary.compile_outcome['status'], 'FAILED')
            self.assertEqual(primary.compile_outcome['first_error']['message'], str(primary))

        def test_wrong_artifact_profile_cannot_pass_after_successful_compilation(self):
            owner = self.controlled(self.owner())
            self.artifact_reply['profile'] = 'p3_drive'
            with self.assertRaises(ValueError) as caught:
                owner.run()
            self.assertEqual((owner.query_calls, owner.compiler_calls), (1, 1))
            self.assertEqual(caught.exception.compile_outcome['status'], 'FAILED')
            self.assertIsNone(owner.artifact_receipt)
            self.assertTrue(any(row['name'] == 'artifact_sources'
                                for row in caught.exception.compile_outcome['final_checks']))

        def test_full_commands_stay_bounded_and_artifact_call_carries_complete_selection(self):
            owner = self.controlled(self.owner('p5_abort_timing', 1, 'a' + '0' * 23))
            owner.local(); owner.prepare(); owner.claim()
            owner.prepare_artifact_sources()
            program = owner.artifact_program()
            tree = ast.parse(program)
            calls = [node for node in ast.walk(tree) if isinstance(node, ast.Call)
                     and isinstance(node.func, ast.Attribute) and node.func.attr == 'inspect_artifacts']
            self.assertEqual(len(calls), 1)
            kwargs = next(keyword.value for keyword in calls[0].keywords if keyword.arg is None)
            self.assertEqual(ast.literal_eval(kwargs), dict(profile=owner.profile,
                motors_allowed=1, attempt=owner.attempt, source_digest=owner.source_sha256))
            programs = [value for _, value in owner.fixture_source_endpoint.calls] + [program]
            for command in programs:
                argv_value = [owner.base.ADB, '-s', owner.base.BOARD, 'shell', '-T',
                              base.shlex.join(['python3', '-I', '-B', '-c', command])]
                units = len(subprocess.list2cmdline(argv_value).encode('utf-16-le')) // 2 + 1
                self.assertLessEqual(units, 30000)

    return CommissioningPipeline


def load_tests(loader, standard, pattern):
    return unittest.TestSuite((standard, loader.loadTestsFromTestCase(pipeline_cases())))


if __name__ == '__main__':
    if not sys.dont_write_bytecode:
        raise SystemExit('Run with Python -I -B')
    unittest.main(verbosity=2)
