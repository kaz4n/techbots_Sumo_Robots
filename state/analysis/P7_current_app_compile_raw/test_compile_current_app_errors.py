# Independent supplemental tests for inherited compile receipt-write failures.
# Preserve the first compiler/transport error when evidence storage also fails.
# Python -B controlled fixtures only; freeze before execution, no native commands.
"""Contract-derived supplement; new implementation unread at authoring time.

The original 27-test oracle is unchanged. This file reuses only its fixture setup,
then exercises the real transport/command_runner guard with endpoint substitutes.
Worker supplied public method signatures and evidence_write_errors schema only.
This is a reused-context same-model test author, not a fresh phase-gate reviewer.
"""
import base64
import errno
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest
from unittest import mock


ORACLE = Path(__file__).with_name('test_compile_current_app.py')
spec = importlib.util.spec_from_file_location('current_compile_frozen_fixture', ORACLE)
fixture_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fixture_module)


class InheritedReceiptErrors(unittest.TestCase):
    def setUp(self):
        self.fixture = fixture_module.ContractCase(methodName='runTest')
        self.addCleanup(self.fixture.doCleanups)
        self.fixture.setUp()
        self.owner = self.fixture.owner()
        self.owner.local()
        self.owner.prepare()
        self.owner.claim()
        # Isolate the receipt guard after controlled prior ownership admission.
        # These booleans are fixture state, never evidence of native ownership.
        self.owner.remote_owned = True
        self.owner.source_available = True
        self.write_failures = []

    def fail_writes(self, *names):
        original = Path.open
        owner = self.owner
        def opening(path, mode='r', *args, **kwargs):
            path = Path(path)
            is_output = path.is_relative_to(owner.output) and path.parent != owner.output
            if is_output and path.name in names and any(flag in mode for flag in 'wax+'):
                self.write_failures.append(path.name)
                raise OSError(errno.ENOSPC, 'Controlled ENOSPC for ' + path.name)
            return original(path, mode, *args, **kwargs)
        return mock.patch.object(Path, 'open', opening)

    def assert_secondary(self, error, names):
        rows = getattr(error, 'evidence_write_errors', None)
        self.assertIsInstance(rows, list)
        self.assertTrue(rows)
        for row in rows:
            self.assertEqual(set(row), {'type', 'message'})
            self.assertEqual(row['type'], 'OSError')
        text = json.dumps(rows)
        for name in names:
            self.assertIn('Controlled ENOSPC for ' + name, text)
            self.assertIn(name, self.write_failures)

    def child_reply(self, returncode):
        owner = self.owner
        def direct(program, label, timeout=90):
            self.assertEqual(label, 'checked-command')
            self.assertEqual(timeout, 810)
            self.assertTrue((owner.output / 'intent.json').is_file())
            owner.counter += 1
            folder = owner.output / ('%04d-controlled-child' % owner.counter)
            folder.mkdir()
            out, err = b'controlled compiler output', b'controlled compiler failure'
            record = dict(status='COMPLETED' if returncode == 0 else 'FAILED',
                          execution=dict(returncode=returncode, reaped=True, timed_out=False),
                          stdout_base64=base64.b64encode(out).decode('ascii'),
                          stderr_base64=base64.b64encode(err).decode('ascii'),
                          stdout_bytes=len(out), stderr_bytes=len(err))
            return subprocess.CompletedProcess([], 0, json.dumps(record).encode(), b''), folder
        return mock.patch.object(owner, 'direct', direct)

    def command(self):
        return self.owner.command_runner(
            fixture_module.BOARD,
            ['arduino-cli', 'compile', '--json', '--fqbn', 'arduino:zephyr:unoq',
             fixture_module.REMOTE_ROOT + '/' + fixture_module.SOURCE + '/app'], capture=True)

    def check_child_failure(self, name):
        with self.child_reply(43), self.fail_writes(name):
            with self.assertRaises(subprocess.CalledProcessError) as caught:
                self.command()
        error = caught.exception
        self.assertEqual(error.returncode, 43)
        self.assertEqual(error.stdout, 'controlled compiler output')
        self.assertEqual(error.stderr, 'controlled compiler failure')
        self.assertEqual(error.cmd[:4], ['/usr/bin/arduino-cli', '--config-file', '/dev/null', 'compile'])
        self.assertEqual(error.cmd[error.cmd.index('--jobs') + 1], '1')
        self.assert_secondary(error, [name])

    def test_nonzero_compiler_survives_remote_result_write_failure(self):
        self.check_child_failure('remote_result.json')

    def test_nonzero_compiler_survives_child_stdout_write_failure(self):
        self.check_child_failure('child.stdout')

    def test_nonzero_compiler_survives_child_stderr_write_failure(self):
        self.check_child_failure('child.stderr')

    def check_transport_timeout(self, name):
        primary = subprocess.TimeoutExpired(['controlled-adb'], 810,
                                            output=b'partial stdout', stderr=b'partial stderr')
        calls = []
        def timeout(argv, **kwargs):
            calls.append((argv, kwargs))
            self.assertEqual(argv[1:3], ['-s', fixture_module.BOARD])
            self.assertEqual(kwargs['timeout'], 810)
            self.assertTrue(kwargs['capture_output'])
            raise primary
        # Frozen finally writes are sequential: inject one reached failure per run.
        with mock.patch.object(subprocess, 'run', timeout), self.fail_writes(name):
            with self.assertRaises(subprocess.TimeoutExpired) as caught:
                self.owner.transport(['shell', '-T', 'controlled-no-execution'], 810, 'controlled-timeout')
        self.assertIs(caught.exception, primary)
        self.assertEqual(len(calls), 1)
        self.assertEqual(primary.stdout, b'partial stdout')
        self.assertEqual(primary.stderr, b'partial stderr')
        self.assert_secondary(primary, [name])

    def test_transport_timeout_survives_stdout_write_failure(self):
        self.check_transport_timeout('stdout')

    def test_transport_timeout_survives_stderr_write_failure(self):
        self.check_transport_timeout('stderr')

    def test_transport_timeout_survives_result_write_failure(self):
        self.check_transport_timeout('result.json')

    def test_successful_child_with_failed_receipt_is_not_reported_successful(self):
        with self.child_reply(0), self.fail_writes('remote_result.json'):
            with self.assertRaises(OSError) as caught:
                self.command()
        self.assertEqual(caught.exception.errno, errno.ENOSPC)
        self.assertIn('remote_result.json', self.write_failures)


if __name__ == '__main__':
    if not sys.dont_write_bytecode:
        raise SystemExit('Run controlled tests with Python -B')
    unittest.main(verbosity=2)
