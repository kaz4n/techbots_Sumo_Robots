# Checks D181 compiler error retention against the independently frozen contract.
# Exercises opaque public APIs with synthetic runners and memory-only output sinks.
# Run with Python -B unittest; no subprocess, board, compiler, or scratch file runs.
from contextlib import redirect_stderr, redirect_stdout
import errno
import importlib
import inspect
import io
import json
from pathlib import Path
import subprocess
import sys
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[2]
RECEIPT = Path('/fixture-retention/receipts')
COMMAND = ['fixture-compiler', 'space preserved', '$literal', 'line\nbreak']
BOARD = 'fixture-board'
NAME = 'compile'
COMMAND_PATH = RECEIPT / (NAME + '.command.json')
STDOUT_PATH = RECEIPT / (NAME + '.stdout.json')
STDERR_PATH = RECEIPT / (NAME + '.stderr.txt')
RAW_STDOUT = '  raw stdout \u03bc\n\n'
RAW_STDERR = 'raw stderr \u03bb\n'


class MemoryWrites:
    """One write attempt may leave partial bytes before its configured failure."""

    def __init__(self, events):
        self.events = events
        self.failures = {}
        self.partial = {}
        self.contents = {}
        self.attempts = []

    def write_text(self, path, text, encoding=None, errors=None, newline=None):
        path = Path(path)
        self.events.append(('write', path))
        self.attempts.append((path, text, encoding))
        if not isinstance(text, str):
            raise TypeError('data must be str, not ' + type(text).__name__)
        if path in self.failures:
            if path in self.partial:
                self.contents[path] = self.partial[path]
            raise self.failures[path]
        self.contents[path] = text.encode(encoding or 'utf-8')
        return len(text)


class BrokenStderr:
    def __init__(self, error):
        self.error = error
        self.attempts = []

    def write(self, text):
        self.attempts.append(text)
        raise self.error

    def flush(self):
        pass


class CompileErrorRetentionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Runtime import is opaque: all expectations above come from D181/public tests.
        with mock.patch.object(sys, 'path', [str(ROOT / 'tools')] + sys.path):
            cls.board = importlib.import_module('board_tool')

    def setUp(self):
        self.events = []
        self.files = MemoryWrites(self.events)
        self.stdout = io.StringIO()
        self.stderr = io.StringIO()
        self.enterContext(redirect_stdout(self.stdout))
        self.enterContext(redirect_stderr(self.stderr))
        self.enterContext(mock.patch.object(Path, 'write_text', autospec=True,
                                           side_effect=self.files.write_text))
        for operation in ('open', 'write_bytes', 'unlink', 'rename', 'replace', 'mkdir'):
            self.enterContext(mock.patch.object(Path, operation,
                side_effect=AssertionError('unexpected filesystem operation: ' + operation)))
        for operation in ('run', 'Popen'):
            self.enterContext(mock.patch.object(subprocess, operation,
                side_effect=AssertionError('real process execution forbidden')))
        self.remote = self.enterContext(mock.patch.object(self.board, 'remote',
            side_effect=AssertionError('unexpected global transport')))
        self.runner = mock.Mock(side_effect=self.run_command)
        self.outcome = subprocess.CompletedProcess(COMMAND, 0, RAW_STDOUT, RAW_STDERR)

    def run_command(self, board, command, capture=False):
        self.events.append(('runner', list(command)))
        self.assertEqual(BOARD, board)
        self.assertEqual(COMMAND, command)
        self.assertIs(True, capture)
        if isinstance(self.outcome, BaseException):
            raise self.outcome
        return self.outcome

    def capture(self):
        return self.board.capture_app_command(BOARD, COMMAND, RECEIPT, NAME,
                                              command_runner=self.runner)

    def compiler_error(self, stdout=RAW_STDOUT, stderr=RAW_STDERR):
        error = subprocess.CalledProcessError(43, COMMAND, output=stdout, stderr=stderr)
        self.outcome = error
        return error

    def fail_write(self, path, error=None, partial=None):
        error = error if error is not None else OSError(errno.ENOSPC, 'fixture disk full')
        self.files.failures[path] = error
        if partial is not None:
            self.files.partial[path] = partial
        return error

    def assert_attempts(self, streams=(STDOUT_PATH, STDERR_PATH)):
        self.assertEqual([COMMAND_PATH] + list(streams),
                         [item[0] for item in self.files.attempts])
        self.assertEqual(('write', COMMAND_PATH), self.events[0])
        self.assertEqual(('runner', COMMAND), self.events[1])
        self.runner.assert_called_once_with(BOARD, COMMAND, capture=True)
        self.remote.assert_not_called()
        for path, _, encoding in self.files.attempts:
            if path == COMMAND_PATH:
                self.assertIsNone(encoding)
            else:
                self.assertEqual('utf8', encoding.lower().replace('-', ''))

    def assert_primary_fields(self, error, stdout=RAW_STDOUT, stderr=RAW_STDERR):
        self.assertEqual(43, error.returncode)
        self.assertEqual(COMMAND, error.cmd)
        self.assertEqual(stdout, error.stdout)
        self.assertEqual(stderr, error.stderr)

    def assert_write_errors(self, error, paths):
        expected = [{'path': str(path), 'type': type(self.files.failures[path]).__name__,
                     'message': str(self.files.failures[path])} for path in paths]
        self.assertEqual(expected, error.evidence_write_errors)

    def assert_failure_diagnostic(self, paths):
        text = self.stderr.getvalue()
        self.assertIn(str(RECEIPT), text)
        self.assertIn('could not save', text.lower())
        for path in paths:
            self.assertIn(str(path), text)
            self.assertIn(type(self.files.failures[path]).__name__, text)
            self.assertIn(str(self.files.failures[path]), text)

    def main(self, action):
        argv = ['board_tool.py', 'flash', 'app', '--compile-only']
        with mock.patch.object(sys, 'argv', argv), \
             mock.patch.object(self.board, 'flash', side_effect=lambda args: action()) as flash:
            result = self.board.main()
        flash.assert_called_once()
        return result

    def test_capture_signature_retains_optional_keyword_only_runner(self):
        parameter = inspect.signature(self.board.capture_app_command).parameters['command_runner']
        self.assertEqual(inspect.Parameter.KEYWORD_ONLY, parameter.kind)
        self.assertIsNone(parameter.default)

    def test_success_keeps_result_identity_raw_utf8_and_command_before_dispatch(self):
        result = self.outcome
        self.assertIs(result, self.capture())
        self.assert_attempts()
        self.assertEqual(COMMAND, json.loads(self.files.contents[COMMAND_PATH]))
        self.assertEqual(RAW_STDOUT.encode('utf-8'), self.files.contents[STDOUT_PATH])
        self.assertEqual(RAW_STDERR.encode('utf-8'), self.files.contents[STDERR_PATH])

    def test_success_none_streams_refuse_nontext_without_stderr_receipt(self):
        self.outcome = subprocess.CompletedProcess(COMMAND, 0, None, None)
        with self.assertRaises(TypeError):
            self.capture()
        self.assert_attempts((STDOUT_PATH,))
        self.assertNotIn(STDOUT_PATH, self.files.contents)
        self.assertNotIn(STDERR_PATH, self.files.contents)

    def test_falsey_explicit_callable_never_selects_global_transport(self):
        class FalseyRunner:
            def __bool__(self):
                return False

            def __call__(inner, *args, **kwargs):
                return self.runner(*args, **kwargs)

        result = self.board.capture_app_command(BOARD, COMMAND, RECEIPT, NAME,
                                               command_runner=FalseyRunner())
        self.assertIs(self.outcome, result)
        self.assert_attempts()

    def test_raised_failure_keeps_identity_raw_bytes_and_empty_error_list(self):
        primary = self.compiler_error()
        with self.assertRaises(subprocess.CalledProcessError) as caught:
            self.capture()
        self.assertIs(primary, caught.exception)
        self.assert_primary_fields(primary)
        self.assert_write_errors(primary, [])
        self.assert_attempts()
        self.assertEqual(RAW_STDOUT.encode('utf-8'), self.files.contents[STDOUT_PATH])
        self.assertEqual(RAW_STDERR.encode('utf-8'), self.files.contents[STDERR_PATH])

    def test_returned_nonzero_result_becomes_primary_with_raw_streams(self):
        self.outcome = subprocess.CompletedProcess(COMMAND, 43, RAW_STDOUT, RAW_STDERR)
        with self.assertRaises(subprocess.CalledProcessError) as caught:
            self.capture()
        self.assert_primary_fields(caught.exception)
        self.assert_write_errors(caught.exception, [])
        self.assert_attempts()
        self.assertEqual(RAW_STDOUT.encode('utf-8'), self.files.contents[STDOUT_PATH])
        self.assertEqual(RAW_STDERR.encode('utf-8'), self.files.contents[STDERR_PATH])

    def test_none_failure_streams_write_empty_bytes_without_mutating_primary(self):
        primary = self.compiler_error(None, None)
        with self.assertRaises(subprocess.CalledProcessError) as caught:
            self.capture()
        self.assertIs(primary, caught.exception)
        self.assert_primary_fields(primary, None, None)
        self.assert_write_errors(primary, [])
        self.assert_attempts()
        self.assertEqual(b'', self.files.contents[STDOUT_PATH])
        self.assertEqual(b'', self.files.contents[STDERR_PATH])

    def test_stdout_receipt_failure_preserves_primary_and_still_saves_stderr(self):
        primary = self.compiler_error()
        self.fail_write(STDOUT_PATH)
        with self.assertRaises(subprocess.CalledProcessError) as caught:
            self.capture()
        self.assertIs(primary, caught.exception)
        self.assert_primary_fields(primary)
        self.assert_write_errors(primary, [STDOUT_PATH])
        self.assert_attempts()
        self.assertEqual(RAW_STDERR.encode('utf-8'), self.files.contents[STDERR_PATH])
        self.assert_failure_diagnostic([STDOUT_PATH])

    def test_stderr_receipt_failure_preserves_primary_and_saved_stdout(self):
        primary = self.compiler_error()
        self.fail_write(STDERR_PATH, PermissionError(errno.EACCES, 'fixture denied'))
        with self.assertRaises(subprocess.CalledProcessError) as caught:
            self.capture()
        self.assertIs(primary, caught.exception)
        self.assert_primary_fields(primary)
        self.assert_write_errors(primary, [STDERR_PATH])
        self.assert_attempts()
        self.assertEqual(RAW_STDOUT.encode('utf-8'), self.files.contents[STDOUT_PATH])
        self.assert_failure_diagnostic([STDERR_PATH])

    def test_both_receipt_exceptions_are_ordered_and_primary_cause_context_survive(self):
        primary = self.compiler_error()
        cause = ValueError('original cause')
        context = RuntimeError('original context')
        primary.__cause__, primary.__context__ = cause, context
        self.fail_write(STDOUT_PATH, ValueError('stdout encoding fixture'))
        self.fail_write(STDERR_PATH, RuntimeError('stderr writer fixture'))
        with self.assertRaises(subprocess.CalledProcessError) as caught:
            self.capture()
        self.assertIs(primary, caught.exception)
        self.assertIs(cause, primary.__cause__)
        self.assertIs(context, primary.__context__)
        self.assert_primary_fields(primary)
        self.assert_write_errors(primary, [STDOUT_PATH, STDERR_PATH])
        self.assert_attempts()
        self.assert_failure_diagnostic([STDOUT_PATH, STDERR_PATH])

    def test_returned_failure_keeps_primary_fields_when_both_receipts_fail(self):
        self.outcome = subprocess.CompletedProcess(COMMAND, 43, None, RAW_STDERR)
        self.fail_write(STDOUT_PATH)
        self.fail_write(STDERR_PATH)
        with self.assertRaises(subprocess.CalledProcessError) as caught:
            self.capture()
        self.assert_primary_fields(caught.exception, None, RAW_STDERR)
        self.assert_write_errors(caught.exception, [STDOUT_PATH, STDERR_PATH])
        self.assert_attempts()
        self.assertEqual('', self.files.attempts[1][1])

    def test_partial_receipt_bytes_remain_without_reopen_retry_or_delete(self):
        primary = self.compiler_error()
        self.fail_write(STDOUT_PATH, partial=b'  raw')
        self.fail_write(STDERR_PATH, partial=b'raw st')
        with self.assertRaises(subprocess.CalledProcessError) as caught:
            self.capture()
        self.assertIs(primary, caught.exception)
        self.assertEqual(b'  raw', self.files.contents[STDOUT_PATH])
        self.assertEqual(b'raw st', self.files.contents[STDERR_PATH])
        self.assert_attempts()
        self.assert_write_errors(primary, [STDOUT_PATH, STDERR_PATH])

    def test_command_receipt_failure_prevents_runner_dispatch(self):
        secondary = self.fail_write(COMMAND_PATH)
        with self.assertRaises(OSError) as caught:
            self.capture()
        self.assertIs(secondary, caught.exception)
        self.runner.assert_not_called()
        self.remote.assert_not_called()
        self.assertEqual([('write', COMMAND_PATH)], self.events)

    def test_success_stdout_receipt_failure_still_refuses_success(self):
        secondary = self.fail_write(STDOUT_PATH)
        with self.assertRaises(OSError) as caught:
            self.capture()
        self.assertIs(secondary, caught.exception)
        self.assert_attempts((STDOUT_PATH,))
        self.assertNotIn(STDERR_PATH, self.files.contents)

    def test_success_stderr_receipt_failure_still_refuses_success(self):
        secondary = self.fail_write(STDERR_PATH)
        with self.assertRaises(OSError) as caught:
            self.capture()
        self.assertIs(secondary, caught.exception)
        self.assert_attempts()
        self.assertEqual(RAW_STDOUT.encode('utf-8'), self.files.contents[STDOUT_PATH])

    def test_receipt_baseexception_is_not_swallowed(self):
        self.compiler_error()
        interruption = KeyboardInterrupt('receipt interrupted')
        self.fail_write(STDOUT_PATH, interruption)
        with self.assertRaises(KeyboardInterrupt) as caught:
            self.capture()
        self.assertIs(interruption, caught.exception)
        self.assert_attempts((STDOUT_PATH,))

    def test_runner_baseexception_is_not_swallowed_or_treated_as_compiler_failure(self):
        interruption = SystemExit(17)
        self.outcome = interruption
        with self.assertRaises(SystemExit) as caught:
            self.capture()
        self.assertIs(interruption, caught.exception)
        self.assert_attempts(())

    def test_runner_timeout_keeps_identity_without_compiler_receipt_handling(self):
        timeout = subprocess.TimeoutExpired(COMMAND, 0.1, output='partial', stderr='deadline')
        self.outcome = timeout
        with self.assertRaises(subprocess.TimeoutExpired) as caught:
            self.capture()
        self.assertIs(timeout, caught.exception)
        self.assert_attempts(())

    def test_saved_failure_receipts_survive_unavailable_diagnostic_console(self):
        primary = self.compiler_error()
        console_error = OSError(errno.EPIPE, 'fixture console closed')
        console = BrokenStderr(console_error)
        with redirect_stderr(console), self.assertRaises(subprocess.CalledProcessError) as caught:
            self.capture()
        self.assertIs(primary, caught.exception)
        self.assert_attempts()
        self.assert_write_errors(primary, [])
        self.assertEqual(RAW_STDOUT.encode('utf-8'), self.files.contents[STDOUT_PATH])
        self.assertEqual(RAW_STDERR.encode('utf-8'), self.files.contents[STDERR_PATH])
        self.assertGreater(len(console.attempts), 0)
        self.assertEqual([{'type': type(console_error).__name__, 'message': str(console_error)}]
                         * len(console.attempts), primary.diagnostic_write_errors)

    def test_failing_capture_diagnostic_preserves_primary_and_records_console_error(self):
        primary = self.compiler_error()
        self.fail_write(STDOUT_PATH)
        console_error = OSError(errno.EPIPE, 'fixture console closed')
        console = BrokenStderr(console_error)
        with redirect_stderr(console), self.assertRaises(subprocess.CalledProcessError) as caught:
            self.capture()
        self.assertIs(primary, caught.exception)
        self.assert_primary_fields(primary)
        self.assert_attempts()
        self.assert_write_errors(primary, [STDOUT_PATH])
        self.assertGreater(len(console.attempts), 0)
        self.assertEqual([{'type': type(console_error).__name__, 'message': str(console_error)}]
                         * len(console.attempts), primary.diagnostic_write_errors)

    def test_capture_diagnostic_baseexception_propagates(self):
        self.compiler_error()
        self.fail_write(STDOUT_PATH)
        interruption = KeyboardInterrupt('console interrupted')
        with redirect_stderr(BrokenStderr(interruption)), self.assertRaises(KeyboardInterrupt) as caught:
            self.capture()
        self.assertIs(interruption, caught.exception)

    def test_main_returns_compiler_exit_and_final_diagnostic_names_primary(self):
        primary = self.compiler_error()
        self.fail_write(STDOUT_PATH)
        self.assertEqual(43, self.main(self.capture))
        self.assert_attempts()
        self.assert_write_errors(primary, [STDOUT_PATH])
        self.assert_failure_diagnostic([STDOUT_PATH])
        self.assertIn('ERROR:', self.stderr.getvalue())
        self.assertIn(str(primary), self.stderr.getvalue())

    def test_main_returned_command_failure_keeps_exit_despite_receipt_failure(self):
        self.outcome = subprocess.CompletedProcess(COMMAND, 43, RAW_STDOUT, RAW_STDERR)
        self.fail_write(STDERR_PATH)
        self.assertEqual(43, self.main(self.capture))
        self.assert_attempts()
        self.assertIn('ERROR:', self.stderr.getvalue())
        self.assertIn('43', self.stderr.getvalue())

    def test_main_compiler_exit_survives_failing_capture_and_final_diagnostics(self):
        primary = self.compiler_error()
        self.fail_write(STDOUT_PATH)
        console_error = RuntimeError('fixture stderr failure')
        console = BrokenStderr(console_error)
        with redirect_stderr(console):
            self.assertEqual(43, self.main(self.capture))
        self.assert_attempts()
        self.assert_write_errors(primary, [STDOUT_PATH])
        self.assertGreaterEqual(len(console.attempts), 2)
        self.assertEqual([{'type': 'RuntimeError', 'message': str(console_error)}]
                         * len(console.attempts), primary.diagnostic_write_errors)

    def test_main_other_caught_errors_keep_exit_two_with_unavailable_stderr(self):
        selected = ValueError('fixture validation failure')
        console_error = OSError(errno.EPIPE, 'fixture console closed')
        console = BrokenStderr(console_error)
        with redirect_stderr(console):
            self.assertEqual(2, self.main(mock.Mock(side_effect=selected)))
        self.assertGreater(len(console.attempts), 0)
        self.assertEqual([{'type': type(console_error).__name__, 'message': str(console_error)}]
                         * len(console.attempts), selected.diagnostic_write_errors)
        self.runner.assert_not_called()
        self.assertEqual([], self.files.attempts)

    def test_main_success_receipt_error_remains_explicit_exit_two(self):
        secondary = self.fail_write(STDOUT_PATH)
        self.assertEqual(2, self.main(self.capture))
        self.assertIn(str(secondary), self.stderr.getvalue())
        self.assert_attempts((STDOUT_PATH,))

    def test_main_diagnostic_baseexception_is_not_swallowed(self):
        primary = subprocess.CalledProcessError(43, COMMAND)
        interruption = SystemExit(19)
        with redirect_stderr(BrokenStderr(interruption)), self.assertRaises(SystemExit) as caught:
            self.main(mock.Mock(side_effect=primary))
        self.assertIs(interruption, caught.exception)


if __name__ == '__main__':
    unittest.main(verbosity=2)
