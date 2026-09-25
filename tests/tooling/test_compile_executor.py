# Tests D164 per-call executor selection from the published checked-build contract.
# Keeps transport isolation independent while retaining real validators and receipts.
# All command responses are synthetic; run with Python -B under Linux RAM scratch.
from contextlib import redirect_stderr, redirect_stdout
import hashlib
import inspect
import io
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest import mock
from . import test_app_build_policy as app_fixture
from . import test_opp_view_policy as fixture

BOARD = 'fixture-board'
REMOTE_ROOT = '/fixture/checked-build'
SOURCE = REMOTE_ROOT + '/source/motor_fault'
PROJECT = 'motor_fault.ino'
DATA = fixture.DATA
USER = '/fixture/Arduino'
FLAGS = fixture.FLAGS
FQBN = fixture.FQBN
CHECKSUM = 'a' * 64


def compile_command(build=fixture.BUILD, output=fixture.ARTIFACTS):
    return ['arduino-cli', 'compile', '--fqbn', FQBN, '--json', '--build-path', build,
            '--output-dir', output, '--build-property', 'compiler.cpp.extra_flags=' + FLAGS,
            '--build-property', 'compiler.c.extra_flags=' + FLAGS,
            '--build-property', 'build.library_discovery_phase_flag=-DARDUINO_LIBRARY_DISCOVERY_PHASE=0',
            SOURCE]


class SyntheticRunner:
    """Recognizes the public fixture protocol, never dispatching a command."""
    def __init__(self, case, board=BOARD, fail=None, error=None, corrupt=None):
        self.case = case
        self.board = board
        self.fail = fail
        self.error = error
        self.corrupt = corrupt
        self.calls = []
        self.results = []
        self.before_first = None
        self.global_remote = None

    @staticmethod
    def phase(command):
        if command[:2] == ['arduino-cli', 'version']:
            return 'version'
        if command[:3] == ['arduino-cli', 'config', 'get']:
            return command[3]
        if command[:2] == ['arduino-cli', 'compile']:
            return 'preflight' if '--show-properties=expanded' in command else 'compile'
        if command[0] == 'sh':
            return 'overrides'
        if command[0] == 'sha256sum':
            return 'artifacts' if any(Path(arg).name.endswith(('.elf', '.elf-zsk.bin'))
                                      for arg in command[2:]) else 'pins'
        if command[0] == 'mkdir':
            return 'mkdir'
        raise AssertionError('Unrecognized synthetic command: ' + repr(command))

    def compile_result(self, command, phase):
        build = command[command.index('--build-path') + 1]
        document = json.loads(json.dumps(fixture.document(project=PROJECT)).replace(fixture.BUILD, build))
        if self.corrupt == phase:
            if phase == 'compile':
                document['success'] = False
            else:
                values = document['builder_result']['build_properties']
                values[:] = [value.replace('build.link_mode=dynamic', 'build.link_mode=static')
                             for value in values]
        return json.dumps(document) + '\n'

    def __call__(self, board, argv, capture=False, timeout=None):
        self.case.assertEqual(self.board, board)
        if self.global_remote is not None:
            self.case.assertIs(self.global_remote, fixture.board.remote)
        command = list(argv)
        phase = self.phase(command)
        self.calls.append((board, command, capture, timeout, phase))
        if self.before_first is not None:
            callback, self.before_first = self.before_first, None
            callback()
        if phase == self.fail:
            raise self.error
        stdout = self.response(command, phase)
        result = subprocess.CompletedProcess(command, 0, stdout=stdout, stderr='')
        self.results.append((phase, result))
        return result

    def response(self, command, phase):
        if phase == 'version':
            return app_fixture.CLI if self.corrupt != phase else 'unreviewed CLI\n'
        if phase in ('directories.data', 'directories.user'):
            return json.dumps(DATA if phase == 'directories.data' else USER) + '\n'
        if phase in ('preflight', 'compile'):
            return self.compile_result(command, phase)
        if phase in ('pins', 'artifacts'):
            self.case.assertEqual(['sha256sum', '--'], command[:2])
            pins = fixture.policy.installed_pins(DATA)
            lines = []
            for name in command[2:]:
                digest = pins.get(name, '1' * 64)
                if name not in pins:
                    self.case.assertIn(Path(name).name, [PROJECT + suffix for suffix in
                        ('.elf', '_debug.elf', '_temp.elf', '.elf-zsk.bin')])
                    if self.corrupt == 'artifacts':
                        digest = hashlib.sha256(b'').hexdigest()
                lines.append(digest + '  ' + name + '\n')
            return ''.join(lines)
        return ''


class CompileExecutorTests(unittest.TestCase):
    def setUp(self):
        if not Path('/dev/shm').is_dir():
            self.skipTest('Linux RAM scratch required')
        self.temporary = tempfile.TemporaryDirectory(prefix='sumox-executor-', dir='/dev/shm')
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        # Opaque runtime dependencies; none supplies an expected test result.
        (self.root / 'tools').mkdir()
        for name in ('app_build_policy.py', 'app_build_commands.json', 'app_build_pins.json'):
            shutil.copyfile(fixture.ROOT / 'tools' / name, self.root / 'tools' / name)
        self.receipt = self.root / 'direct-receipt'
        self.receipt.mkdir()
        self.root_patch = mock.patch.object(fixture.board, 'ROOT', self.root)
        self.root_patch.start()
        self.addCleanup(self.root_patch.stop)
        self.out = io.StringIO()
        self.err = io.StringIO()
        self.stdout_patch = redirect_stdout(self.out)
        self.stderr_patch = redirect_stderr(self.err)
        self.stdout_patch.__enter__()
        self.stderr_patch.__enter__()
        self.addCleanup(self.stdout_patch.__exit__, None, None, None)
        self.addCleanup(self.stderr_patch.__exit__, None, None, None)

    def compile(self, **kwargs):
        board = kwargs.pop('board', BOARD)
        return fixture.board.compile_app(board, CHECKSUM, SOURCE, REMOTE_ROOT,
                                          FQBN, FLAGS, 'default', project=PROJECT, **kwargs)

    def preflight(self, **kwargs):
        return fixture.board.app_preflight(fixture.policy, BOARD, compile_command(),
            self.receipt, FQBN, FLAGS, fixture.BUILD, project=PROJECT, **kwargs)

    def forbid_global_remote(self):
        patcher = mock.patch.object(fixture.board, 'remote', side_effect=AssertionError('global remote used'))
        result = patcher.start()
        self.addCleanup(patcher.stop)
        return result

    def verified_files(self):
        return sorted(self.root.glob('build/app-receipts/*/verified.json'))

    def assert_capture_receipts(self, name, command, stdout, stderr):
        self.assertEqual(command, json.loads((self.receipt / (name + '.command.json')).read_text()))
        self.assertEqual(stdout, (self.receipt / (name + '.stdout.json')).read_text())
        self.assertEqual(stderr, (self.receipt / (name + '.stderr.txt')).read_text())

    @staticmethod
    def normalized_calls(runner):
        build_commands = [call[1] for call in runner.calls if call[4] in ('preflight', 'compile')]
        build = build_commands[0][build_commands[0].index('--build-path') + 1]
        run_root = str(Path(build).parent)
        return [(board, [value.replace(run_root, '<RUN>') for value in command], capture, timeout, phase)
                for board, command, capture, timeout, phase in runner.calls]

    def test_executor_parameter_is_optional_and_keyword_only_on_all_three_boundaries(self):
        for function in (fixture.board.capture_app_command, fixture.board.app_preflight,
                         fixture.board.compile_app):
            with self.subTest(function=function.__name__):
                parameter = inspect.signature(function).parameters['command_runner']
                self.assertEqual(inspect.Parameter.KEYWORD_ONLY, parameter.kind)
                self.assertIsNone(parameter.default)

    def test_capture_uses_explicit_runner_preserves_result_identity_and_exact_raw_receipts(self):
        global_remote = self.forbid_global_remote()
        command = ['fixture-command', 'space preserved', '$literal', 'line\nbreak']
        result = subprocess.CompletedProcess(command, 0, stdout='  raw stdout\n\n', stderr='raw stderr\n')
        calls = []

        def runner(board, argv, capture=False, timeout=None):
            self.assertIs(global_remote, fixture.board.remote)
            calls.append((board, argv, capture, timeout))
            return result

        actual = fixture.board.capture_app_command(BOARD, command, self.receipt, 'success', command_runner=runner)
        self.assertIs(result, actual)
        self.assertEqual([(BOARD, command, True, None)], calls)
        self.assert_capture_receipts('success', command, result.stdout, result.stderr)
        global_remote.assert_not_called()

    def test_capture_preserves_called_process_error_identity_raw_streams_and_empty_streams(self):
        global_remote = self.forbid_global_remote()
        command = ['fixture-failure', 'argument']
        for index, (stdout, stderr) in enumerate((('inner stdout\n', 'outer stderr\n'), (None, None))):
            error = subprocess.CalledProcessError(43, command, output=stdout, stderr=stderr)
            runner = mock.Mock(side_effect=error)
            name = 'failure-' + str(index)
            with self.assertRaises(subprocess.CalledProcessError) as caught:
                fixture.board.capture_app_command(BOARD, command, self.receipt, name, command_runner=runner)
            self.assertIs(error, caught.exception)
            runner.assert_called_once_with(BOARD, command, capture=True)
            self.assert_capture_receipts(name, command, stdout or '', stderr or '')
        global_remote.assert_not_called()

    def test_falsey_callable_is_an_explicit_runner_and_never_falls_back_to_global(self):
        class FalseyRunner(SyntheticRunner):
            def __bool__(self):
                return False

        global_remote = self.forbid_global_remote()
        runner = FalseyRunner(self)
        runner.global_remote = global_remote
        self.compile(command_runner=runner)
        self.assertEqual(1, len(self.verified_files()))
        self.assertEqual(1, sum(call[4] == 'compile' for call in runner.calls))
        global_remote.assert_not_called()

    def test_noncallable_explicit_runner_refuses_before_dispatch_at_every_entrypoint(self):
        global_remote = self.forbid_global_remote()
        for runner in (False, 0, '', 'remote', [], {}, object()):
            calls = (
                lambda: fixture.board.capture_app_command(BOARD, ['fixture'], self.receipt, 'invalid', command_runner=runner),
                lambda: self.preflight(command_runner=runner),
                lambda: self.compile(command_runner=runner),
            )
            for index, call in enumerate(calls):
                with self.subTest(runner=repr(runner), boundary=index), self.assertRaises(ValueError):
                    call()
        global_remote.assert_not_called()
        self.assertEqual([], self.verified_files())

    def test_preflight_routes_directories_overrides_pins_and_properties_to_explicit_runner(self):
        global_remote = self.forbid_global_remote()
        runner = SyntheticRunner(self)
        runner.global_remote = global_remote
        self.assertEqual({'data': DATA, 'user': USER}, self.preflight(command_runner=runner))
        phases = [call[4] for call in runner.calls]
        for phase in ('directories.data', 'directories.user', 'overrides', 'pins', 'preflight'):
            self.assertIn(phase, phases)
        self.assertNotIn('compile', phases)
        self.assertNotIn('artifacts', phases)
        global_remote.assert_not_called()

    def test_whole_checked_build_routes_every_command_and_keeps_real_receipts(self):
        global_remote = self.forbid_global_remote()
        runner = SyntheticRunner(self)
        runner.global_remote = global_remote
        output = self.compile(command_runner=runner)
        self.assertIsInstance(output, str)
        self.assertTrue(output.startswith(REMOTE_ROOT + '/'))
        phases = [call[4] for call in runner.calls]
        for phase in ('version', 'directories.data', 'directories.user', 'overrides',
                      'pins', 'preflight', 'compile', 'artifacts'):
            self.assertIn(phase, phases)
        self.assertLess(phases.index('version'), phases.index('compile'))
        self.assertLess(phases.index('preflight'), phases.index('compile'))
        self.assertLess(phases.index('compile'), phases.index('artifacts'))
        self.assertEqual(1, phases.count('compile'))
        self.assertEqual(1, len(self.verified_files()))
        receipt = self.verified_files()[0].parent
        self.assertTrue((receipt / 'command.json').is_file())
        compiler = next(result for phase, result in runner.results if phase == 'compile')
        self.assertEqual(compiler.stdout, (receipt / 'compile.stdout.json').read_text())
        self.assertEqual(compiler.stderr, (receipt / 'compile.stderr.txt').read_text())
        for _, command, _, _, _ in runner.calls:
            self.assertFalse({'upload', '--upload', 'reset', 'monitor', '--jobs', '--jobs1'} & set(command))
        global_remote.assert_not_called()

    def test_omitted_none_and_explicit_runner_preserve_default_command_arguments(self):
        histories = []
        for mode in ('omitted', 'none', 'explicit'):
            runner = SyntheticRunner(self)
            with mock.patch.object(fixture.board, 'remote', side_effect=runner) as default:
                if mode == 'omitted':
                    self.compile()
                elif mode == 'none':
                    self.compile(command_runner=None)
                else:
                    self.compile(command_runner=runner)
                    default.assert_not_called()
            histories.append(self.normalized_calls(runner))
        self.assertEqual(histories[0], histories[1])
        self.assertEqual(histories[0], histories[2])

    def test_default_internal_calls_remain_compatible_with_old_public_substitution_signatures(self):
        real_capture = fixture.board.capture_app_command
        real_preflight = fixture.board.app_preflight
        seen = []

        def legacy_capture(board, command, receipt, name):
            seen.append('capture')
            return real_capture(board, command, receipt, name)

        def legacy_preflight(policy, board, command, receipt, fqbn, flags, build_path, project='app.ino'):
            seen.append('preflight')
            return real_preflight(policy, board, command, receipt, fqbn, flags, build_path, project=project)

        runner = SyntheticRunner(self)
        with mock.patch.object(fixture.board, 'remote', side_effect=runner), \
             mock.patch.object(fixture.board, 'capture_app_command', side_effect=legacy_capture), \
             mock.patch.object(fixture.board, 'app_preflight', side_effect=legacy_preflight):
            self.compile()
            self.compile(command_runner=None)
        self.assertIn('capture', seen)
        self.assertEqual(2, seen.count('preflight'))
        self.assertEqual(2, len(self.verified_files()))

    def test_sequential_explicit_and_default_builds_do_not_leak_executor_selection(self):
        first = SyntheticRunner(self, board='first-board')
        second = SyntheticRunner(self, board='second-board')
        default_runner = SyntheticRunner(self, board='default-board')
        with mock.patch.object(fixture.board, 'remote', side_effect=default_runner) as default:
            first.global_remote = second.global_remote = default
            self.compile(board='first-board', command_runner=first)
            first_count = len(first.calls)
            self.compile(board='second-board', command_runner=second)
            second_count = len(second.calls)
            self.compile(board='default-board')
            self.assertEqual(first_count, len(first.calls))
            self.assertEqual(second_count, len(second.calls))
            self.assertIs(default, fixture.board.remote)
        for runner in (first, second, default_runner):
            self.assertEqual(1, sum(call[4] == 'compile' for call in runner.calls))
        self.assertEqual(3, len(self.verified_files()))

    def test_nested_build_uses_its_executor_then_resumes_original_without_global_rebinding(self):
        global_remote = self.forbid_global_remote()
        outer = SyntheticRunner(self, board='outer-board')
        inner = SyntheticRunner(self, board='inner-board')
        outer.global_remote = inner.global_remote = global_remote
        outer.before_first = lambda: self.compile(board='inner-board', command_runner=inner)
        self.compile(board='outer-board', command_runner=outer)
        for runner in (outer, inner):
            self.assertEqual(1, sum(call[4] == 'compile' for call in runner.calls))
        self.assertEqual(2, len(self.verified_files()))
        self.assertIs(global_remote, fixture.board.remote)
        global_remote.assert_not_called()

    def test_each_phase_transport_failure_propagates_same_exception_and_stops_dispatch(self):
        global_remote = self.forbid_global_remote()
        for phase in ('version', 'directories.data', 'directories.user', 'overrides',
                      'pins', 'preflight', 'compile', 'artifacts'):
            error = subprocess.CalledProcessError(43, ['fixture-' + phase],
                                                 output='retained stdout\n', stderr='retained stderr\n')
            runner = SyntheticRunner(self, fail=phase, error=error)
            runner.global_remote = global_remote
            with self.subTest(phase=phase), self.assertRaises(subprocess.CalledProcessError) as caught:
                self.compile(command_runner=runner)
            self.assertIs(error, caught.exception)
            self.assertEqual(phase, runner.calls[-1][4])
            self.assertEqual([], self.verified_files())
        global_remote.assert_not_called()

    def test_compile_failure_keeps_real_stdout_stderr_receipts_without_success_receipt(self):
        global_remote = self.forbid_global_remote()
        error = subprocess.CalledProcessError(43, ['fixture-compile'],
            output='{"success":false,"error":"synthetic compile failure"}\n', stderr='outer stderr\n')
        runner = SyntheticRunner(self, fail='compile', error=error)
        with self.assertRaises(subprocess.CalledProcessError) as caught:
            self.compile(command_runner=runner)
        self.assertIs(error, caught.exception)
        receipts = list(self.root.glob('build/app-receipts/*/compile.stdout.json'))
        self.assertEqual(1, len(receipts))
        self.assertEqual(error.stdout, receipts[0].read_text())
        self.assertEqual(error.stderr, receipts[0].with_name('compile.stderr.txt').read_text())
        self.assertEqual([], self.verified_files())
        global_remote.assert_not_called()

    def test_invalid_version_preflight_compile_and_artifact_evidence_still_refuse(self):
        global_remote = self.forbid_global_remote()
        for phase in ('version', 'preflight', 'compile', 'artifacts'):
            runner = SyntheticRunner(self, corrupt=phase)
            with self.subTest(phase=phase), self.assertRaises(ValueError):
                self.compile(command_runner=runner)
            self.assertEqual(phase, runner.calls[-1][4])
            self.assertEqual([], self.verified_files())
        global_remote.assert_not_called()

    def test_runner_timeout_is_not_replaced_and_later_default_selection_still_works(self):
        error = subprocess.TimeoutExpired(['fixture-version'], 0.1, output='partial', stderr='deadline')
        failed = SyntheticRunner(self, fail='version', error=error)
        healthy = SyntheticRunner(self)
        with mock.patch.object(fixture.board, 'remote', side_effect=healthy) as default:
            with self.assertRaises(subprocess.TimeoutExpired) as caught:
                self.compile(command_runner=failed)
            self.assertIs(error, caught.exception)
            default.assert_not_called()
            self.compile()
            self.assertIs(default, fixture.board.remote)
        self.assertEqual(1, len(self.verified_files()))


if __name__ == '__main__':
    unittest.main(verbosity=2)
