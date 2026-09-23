# Checks D107's literal motor-free bench routing through the pinned D100 policy.
# Derives expectations from the frozen contract and independent compiler fixture.
# Uses opaque public tooling APIs and synthetic transport only; no board is contacted.
from contextlib import ExitStack, contextmanager, redirect_stderr, redirect_stdout
import copy
import hashlib
import importlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
policy = importlib.import_module('app_build_policy')
board = importlib.import_module('board_tool')
FIXTURE = ROOT / 'tests/fixtures/app_build_policy/valid_result.json'
PROJECT = 'opp_view.ino'
FQBN = 'arduino:zephyr:unoq'
IMMEDIATE = FQBN + ':wait_linux_boot=no'
FLAGS = '-DMATCH=0 -DMOTORS_ALLOWED=0'
BUILD = '/fixture/native-app-v1/source/default/run-one/build'
DATA = '/home/arduino/.arduino15'
ARTIFACTS = '/fixture/output'


def document(immediate=False, project=PROJECT):
    result = json.loads(FIXTURE.read_text(encoding='utf-8').replace('app.ino', project))
    if immediate:
        entries = result['builder_result']['build_properties']
        for index, value in enumerate(entries):
            if value.startswith('build.fqbn='):
                entries[index] = 'build.fqbn=' + IMMEDIATE
            elif value == 'build.boot_mode=wait':
                entries[index] = 'build.boot_mode=immediate'
            elif value.startswith('recipe.hooks.objcopy.postobjcopy.'):
                entries[index] = value.replace('zephyr-sketch-tool"    ',
                                                'zephyr-sketch-tool"   -immediate ')
    return result


def entries(doc):
    return doc['builder_result']['build_properties']


def args(sketch='bench/opp_view', startup=None, match=False, compile_only=True):
    return SimpleNamespace(sketch=sketch, startup=startup, match=match, compile_only=compile_only)


@contextmanager
def isolated_flash(sketch='bench/opp_view'):
    with ExitStack() as stack, tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        stack.enter_context(mock.patch.object(board, 'ROOT', root))
        mocks = {}
        values = {'target': 'fixture-board', 'setting': '/fixture/root',
                  'stage': root / Path(sketch).name, 'source_hash': 'a' * 64,
                  'compile_app': '/checked/unique/artifacts'}
        for name, value in values.items():
            mocks[name] = stack.enter_context(mock.patch.object(board, name, return_value=value))
        for name in ('require_transport', 'verify_core', 'sync_sources', 'remote',
                     'verify_inert_source', 'verify_runtime_artifacts'):
            mocks[name] = stack.enter_context(mock.patch.object(board, name))
        stack.enter_context(redirect_stdout(io.StringIO()))
        stack.enter_context(redirect_stderr(io.StringIO()))
        yield mocks


class OppViewResultTests(unittest.TestCase):
    def validate(self, doc, immediate=False, project=PROJECT, flags=FLAGS):
        return policy.validate_result(json.dumps(doc), IMMEDIATE if immediate else FQBN,
                                      flags, BUILD, project=project)

    def preflight(self, doc, immediate=False, project=PROJECT):
        return policy.validate_preflight(json.dumps(doc), IMMEDIATE if immediate else FQBN,
                                         FLAGS, BUILD, DATA, project=project)

    def test_default_and_immediate_literal_project_validate_at_both_boundaries(self):
        for immediate in (False, True):
            for call in (self.validate, self.preflight):
                with self.subTest(immediate=immediate, boundary=call.__name__):
                    props = call(document(immediate), immediate)
                    self.assertEqual(PROJECT, props['build.project_name'])
                    self.assertEqual('immediate' if immediate else 'wait', props['build.boot_mode'])

    def test_each_mixed_project_reference_is_rejected_at_both_boundaries(self):
        original = document()
        changed = 0
        for index, value in enumerate(entries(original)):
            if PROJECT not in value:
                continue
            changed += 1
            for other in ('app.ino', 'runtime_inert.ino', 'opp_view.ino.other'):
                bad = copy.deepcopy(original)
                entries(bad)[index] = value.replace(PROJECT, other)
                for call in (self.validate, self.preflight):
                    with self.subTest(key=value.split('=', 1)[0], other=other,
                                      boundary=call.__name__), self.assertRaises(ValueError):
                        call(bad)
        self.assertGreaterEqual(changed, 6)

    def test_only_exact_selected_project_and_inert_flags_are_accepted(self):
        for name in ('opp_view', 'other.ino', '../opp_view.ino', 'opp_view.ino\n',
                     'opp_view.ino;true', '', None, 0, []):
            with self.subTest(project=name), self.assertRaises(ValueError):
                self.validate(document(), project=name)
        for flags in ('-DMATCH=1 -DMOTORS_ALLOWED=1', '-DMATCH=0 -DMOTORS_ALLOWED=1',
                      '-DMATCH=1 -DMOTORS_ALLOWED=0', FLAGS + ' -DUNREVIEWED=1'):
            for immediate in (False, True):
                with self.subTest(flags=flags, immediate=immediate), self.assertRaises(ValueError):
                    self.validate(document(immediate), immediate, flags=flags)

    def test_startup_metadata_and_packaging_cannot_disagree(self):
        for immediate in (False, True):
            other = dict(entry.split('=', 1) for entry in entries(document(not immediate)))
            for key in ('build.fqbn', 'build.boot_mode',
                        'recipe.hooks.objcopy.postobjcopy.1.pattern',
                        'recipe.hooks.objcopy.postobjcopy.2.pattern'):
                bad = document(immediate)
                values = entries(bad)
                index = next(i for i, value in enumerate(values) if value.startswith(key + '='))
                values[index] = key + '=' + other[key]
                for call in (self.validate, self.preflight):
                    with self.subTest(key=key, immediate=immediate), self.assertRaises(ValueError):
                        call(bad, immediate)

    def test_no_used_library_or_unsuccessful_compile_is_accepted(self):
        for value in ([{'name': 'Bridge'}], ['Unexpected'], None, {}, '', 0):
            bad = document()
            bad['builder_result']['used_libraries'] = value
            with self.subTest(libraries=value), self.assertRaises(ValueError): self.validate(bad)
        for key, value in (('success', False), ('success', 1), ('error', 'compile failed'),
                           ('upload_result', {'success': True}), ('compiler_err', [])):
            bad = document()
            bad[key] = value
            with self.subTest(key=key), self.assertRaises(ValueError): self.validate(bad)
        good = document()
        good['builder_result']['used_libraries'] = []
        self.assertEqual(PROJECT, self.validate(good)['build.project_name'])

    def test_command_or_hook_mutation_removal_and_addition_remain_rejected(self):
        original = document()
        selected = [i for i, value in enumerate(entries(original))
                    if value.startswith(('recipe.', 'compiler.'))]
        # Only effective commands are governed; include every actual nonempty recipe/hook.
        selected = [i for i in selected if entries(original)[i].split('=', 1)[1] and
                    ('.pattern=' in entries(original)[i] or '.cmd=' in entries(original)[i])]
        self.assertGreaterEqual(len(selected), 10)
        for index in selected:
            for action in ('change', 'remove'):
                bad = copy.deepcopy(original)
                if action == 'change': entries(bad)[index] += ' unreviewed'
                else: entries(bad).pop(index)
                for call in (self.validate, self.preflight):
                    with self.subTest(value=entries(original)[index].split('=', 1)[0], action=action), self.assertRaises(ValueError):
                        call(bad)
        for value in ('recipe.hooks.prebuild.99.pattern=unexpected-command',
                      'recipe.c.combine.99.pattern=unexpected-command',
                      'compiler.cpp.extra_flags.other=-DUNREVIEWED=1'):
            bad = document()
            entries(bad).append(value)
            for call in (self.validate, self.preflight):
                with self.subTest(added=value), self.assertRaises(ValueError): call(bad)

    def test_old_app_and_runtime_profiles_remain_independently_scoped(self):
        for project in ('app.ino', 'runtime_inert.ino'):
            self.assertEqual(project, self.validate(document(project=project), project=project)['build.project_name'])
        self.assertEqual('app.ino', self.validate(document(True, 'app.ino'), True, 'app.ino')['build.project_name'])
        with self.assertRaises(ValueError):
            self.validate(document(True, 'runtime_inert.ino'), True, 'runtime_inert.ino')
        for project in ('app.ino', 'runtime_inert.ino'):
            with self.subTest(project=project), self.assertRaises(ValueError):
                self.validate(document(), project=project)

    def test_hashes_bind_four_exact_selected_artifacts_and_all_installed_pins(self):
        props = self.validate(document())
        installed = policy.installed_pins(DATA)
        artifacts = [BUILD + '/' + PROJECT + suffix for suffix in ('.elf', '_debug.elf', '_temp.elf')]
        artifacts.append(ARTIFACTS + '/' + PROJECT + '.elf-zsk.bin')
        expected = {**installed, **dict.fromkeys(artifacts, '1' * 64)}
        def remote(target, command, capture):
            self.assertEqual('fixture-board', target)
            self.assertTrue(capture)
            self.assertEqual(['sha256sum', '--'], command[:2])
            self.assertEqual(set(expected), set(command[2:]))
            return SimpleNamespace(stdout=''.join(expected[path] + '  ' + path + '\n' for path in command[2:]))
        result = policy.verify_files(remote, 'fixture-board', props, BUILD, ARTIFACTS)
        self.assertEqual(expected, result)
        self.assertFalse(any('/app.ino' in path or '/runtime_inert.ino' in path for path in result))

    def test_each_installed_pin_drift_and_missing_empty_wrong_artifact_is_rejected(self):
        props = self.validate(document())
        installed = policy.installed_pins(DATA)
        artifacts = [BUILD + '/' + PROJECT + suffix for suffix in ('.elf', '_debug.elf', '_temp.elf')]
        artifacts.append(ARTIFACTS + '/' + PROJECT + '.elf-zsk.bin')
        changes = [(path, 'drift') for path in installed]
        changes += [(path, kind) for path in artifacts for kind in ('missing', 'empty', 'wrong-name')]
        for selected, kind in changes:
            def remote(target, command, capture):
                lines = []
                for path in command[2:]:
                    digest = installed.get(path, '1' * 64)
                    if path == selected:
                        if kind == 'missing': continue
                        if kind == 'empty': digest = hashlib.sha256(b'').hexdigest()
                        if kind == 'drift': digest = '0' * 64
                        if kind == 'wrong-name': path = path.replace(PROJECT, 'app.ino')
                    lines.append(digest + '  ' + path + '\n')
                return SimpleNamespace(stdout=''.join(lines))
            with self.subTest(path=selected, kind=kind), self.assertRaises(ValueError):
                policy.verify_files(remote, 'fixture-board', props, BUILD, ARTIFACTS)


class OppViewFlashTests(unittest.TestCase):
    def test_both_compile_profiles_route_only_to_checked_literal_project(self):
        for startup, fqbn, mode in ((None, FQBN, 'default'), ('default', FQBN, 'default'),
                                    ('immediate', IMMEDIATE, 'immediate')):
            with self.subTest(startup=startup), isolated_flash() as calls:
                board.flash(args(startup=startup))
                calls['compile_app'].assert_called_once_with('fixture-board', 'a' * 64,
                    '/fixture/root/' + 'a' * 64 + '/opp_view', '/fixture/root', fqbn, FLAGS,
                    mode, project=PROJECT)
                self.assertEqual([mock.call('fixture-board', ['mkdir', '-p',
                    '/fixture/root/' + 'a' * 64 + '/opp_view'])], calls['remote'].call_args_list)
                calls['verify_inert_source'].assert_not_called()
                calls['verify_runtime_artifacts'].assert_not_called()

    def test_match_and_every_upload_refuse_before_target_or_transport(self):
        for startup in (None, 'default', 'immediate'):
            for match, compile_only in ((True, True), (True, False), (False, False)):
                with self.subTest(startup=startup, match=match, compile_only=compile_only), isolated_flash() as calls:
                    with self.assertRaises(ValueError):
                        board.flash(args(startup=startup, match=match, compile_only=compile_only))
                    for name in ('target', 'require_transport', 'stage', 'remote', 'compile_app'):
                        calls[name].assert_not_called()

    def test_regular_profiles_refuse_before_target_in_each_compile_profile(self):
        for name in ('sketch.yaml', 'sketch.yml'):
            for startup in (None, 'default', 'immediate'):
                with self.subTest(name=name, startup=startup), isolated_flash() as calls:
                    folder = board.ROOT / 'bench/opp_view'
                    folder.mkdir(parents=True)
                    (folder / name).write_text('profile: unreviewed', encoding='utf-8')
                    with self.assertRaises(ValueError): board.flash(args(startup=startup))
                    calls['target'].assert_not_called()
                    calls['require_transport'].assert_not_called()

    def test_profile_symlinks_including_dangling_refuse_before_target(self):
        for name in ('sketch.yaml', 'sketch.yml'):
            for dangling in (False, True):
                with self.subTest(name=name, dangling=dangling), isolated_flash() as calls:
                    folder = board.ROOT / 'bench/opp_view'
                    folder.mkdir(parents=True)
                    destination = board.ROOT / 'outside-profile'
                    if not dangling: destination.write_text('profile: unreviewed', encoding='utf-8')
                    try: (folder / name).symlink_to(destination)
                    except OSError as error: self.skipTest('Symlink capability required; run under WSL: ' + str(error))
                    with self.assertRaises(ValueError): board.flash(args())
                    calls['target'].assert_not_called()
                    calls['require_transport'].assert_not_called()

    def test_checked_failure_preserves_exception_and_never_falls_back_or_uploads(self):
        errors = (ValueError('preflight pin refusal'), RuntimeError('effective command refusal'),
                  subprocess.CalledProcessError(43, ['fixture-compile'], output='saved stdout', stderr='saved stderr'))
        for error in errors:
            with self.subTest(error=type(error).__name__), isolated_flash() as calls:
                calls['compile_app'].side_effect = error
                with self.assertRaises(type(error)) as caught: board.flash(args())
                self.assertIs(error, caught.exception)
                calls['compile_app'].assert_called_once()
                self.assertFalse(any('compile' in call.args[1] or 'upload' in call.args[1]
                                     for call in calls['remote'].call_args_list))

    def test_generic_bench_app_and_runtime_routes_remain_distinct(self):
        for sketch in ('bench/p2_qtr_native_compile', 'bench/ui_matrix'):
            with self.subTest(sketch=sketch), isolated_flash(sketch) as calls:
                board.flash(args(sketch))
                calls['compile_app'].assert_not_called()
                commands = [call.args[1] for call in calls['remote'].call_args_list]
                self.assertEqual(1, sum(command[:2] == ['arduino-cli', 'compile'] for command in commands))
                self.assertFalse(any('upload' in command for command in commands))
        for sketch, project in (('app', 'app.ino'), ('bench/runtime_inert', 'runtime_inert.ino')):
            with self.subTest(sketch=sketch), isolated_flash(sketch) as calls:
                board.flash(args(sketch))
                calls['compile_app'].assert_called_once()
                self.assertEqual(project, calls['compile_app'].call_args.kwargs.get('project', 'app.ino'))
        with isolated_flash('bench/runtime_inert') as calls:
            with self.assertRaises(ValueError): board.flash(args('bench/runtime_inert', startup='immediate'))
            calls['target'].assert_not_called()


if __name__ == '__main__':
    unittest.main()
