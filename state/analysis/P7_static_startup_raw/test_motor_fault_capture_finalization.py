# Tests D176 final deadline and child-result preservation from the public contract.
# Separates primary process failures from later stream cleanup and final-check errors.
# Uses the frozen independent fixture; only mocked children and temporary host files.
import importlib.util
import json
import os
from pathlib import Path
import signal
import subprocess
import unittest
from unittest import mock


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location('d176_frozen_capture_tests',
                                             HERE / 'test_motor_fault_capture.py')
fixture = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(fixture)


class StreamProxy:
    def __init__(self, stream, path, inject):
        self.stream, self.path, self.inject = stream, path, inject

    def __getattr__(self, name):
        return getattr(self.stream, name)

    def __enter__(self):
        return self

    def __exit__(self, kind, value, trace):
        self.close()
        return False

    def flush(self):
        self.stream.flush()
        self.inject(self.path, 'flush')

    def close(self):
        # Close the real temporary file even when simulating a reported close
        # failure, so no test descriptor outlives its private fixture.
        self.stream.close()
        self.inject(self.path, 'close')


class MotorFaultFinalization(fixture.MotorFaultCaptureContract):
    def assert_final_checks(self):
        self.assertGreaterEqual(len(self.identity_calls), 2)
        for role in fixture.PATHS:
            self.assertEqual(sum(name == role for name, limit in self.pin_checks), 2)

    def expire_during_postchecks(self, elapsed):
        original = self.helper.logical_read
        observed = []
        def read(fd, logical, limit, proc=False):
            raw = original(fd, logical, limit, proc)
            if self.calls and logical in fixture.PATHS.values():
                # There are no pin rereads during gathering. The independently
                # required final checks begin after the last child attempt.
                observed.append(logical)
                self.clock.now = 100.0 + elapsed
            return raw
        self.helper.logical_read = read
        return observed

    def test_final_check_deadline_boundaries_599_999_600_and_601_seconds(self):
        for elapsed in (599.999, 600.0, 601.0):
            with self.subTest(elapsed=elapsed), self.fresh() as case:
                final_reads = case.expire_during_postchecks(elapsed)
                report = case.assert_report(case.collect(),
                    'COLLECTED' if elapsed < 600 else 'FAILED')
                self.assertEqual(len(case.calls), 20)
                self.assertEqual(report['counts']['reads'], 20)
                self.assertEqual(set(final_reads), set(fixture.PATHS.values()))
                case.assert_final_checks()
                self.assertEqual(report['finished_monotonic'], 100.0 + elapsed)
                self.assertEqual(len(report['analysis']['snapshots']), 2)
                if elapsed >= 600:
                    self.assertRegex(json.dumps(report).lower(), r'deadline|budget|expir')

    def test_primary_error_and_all_independent_final_errors_survive_expiry(self):
        original_output = self.output
        moved_output = original_output.with_name(original_output.name + '-owned')
        final_reads = self.expire_during_postchecks(601.0)
        def execute(*args):
            self.check_launch(*args)
            for path in fixture.PATHS.values():
                self.logical(path).write_bytes(b'changed after admission')
            self.identity_value['boot_id'] = '00000000-0000-0000-0000-000000000000'
            original_output.rename(moved_output)
            original_output.mkdir()
            (original_output / 'sentinel').write_bytes(b'preserve replacement')
            self.output = moved_output
            raise RuntimeError('first controlled child failure')
        report = self.assert_report(self.collect(executor=execute), 'FAILED')
        self.assertEqual(report['first_error'],
                         {'type': 'RuntimeError', 'message': 'first controlled child failure'})
        self.assertEqual(len(self.calls), 1)
        self.assertEqual(set(final_reads), set(fixture.PATHS.values()))
        self.assert_final_checks()
        self.assertGreaterEqual(len(report['postcheck_errors']), 7)
        self.assertRegex(json.dumps(report['postcheck_errors']).lower(), r'deadline|budget|expir')
        self.assertEqual([p.name for p in original_output.iterdir()], ['sentinel'])
        self.assertEqual((original_output / 'sentinel').read_bytes(), b'preserve replacement')
        self.assertTrue((moved_output / '00.result.json').is_file())

    def test_clean_gathering_preserves_all_final_pin_failures_and_expiry(self):
        final_reads = self.expire_during_postchecks(600.0)
        def alter(index):
            if index == 19:
                for path in fixture.PATHS.values():
                    self.logical(path).write_bytes(b'changed after final raw read')
                self.identity_value['boot_id'] = '00000000-0000-0000-0000-000000000000'
        self.after_execute = alter
        report = self.assert_report(self.collect(), 'FAILED')
        self.assertEqual(len(self.calls), 20)
        self.assertEqual(report['counts']['reads'], 20)
        self.assertEqual(set(final_reads), set(fixture.PATHS.values()))
        self.assert_final_checks()
        self.assertGreaterEqual(len(report['postcheck_errors']), 7)
        self.assertEqual(len(report['analysis']['snapshots']), 2)
        self.assertRegex(json.dumps(report['postcheck_errors']).lower(), r'deadline|budget|expir')

    def controlled_cleanup(self, outcome, stream_name, operation):
        import resource
        waits, kills, injected, cleanup_actions = [], [], [], []
        child_completed = []
        marker = f'late controlled {stream_name} {operation} failure'
        target_path = str(self.output / ('00.' + stream_name))
        real_fdopen, real_fsync = os.fdopen, os.fsync
        def inject(path, action):
            if child_completed:
                cleanup_actions.append((path, action))
            if child_completed and not injected and path == target_path and action == operation:
                injected.append((path, action))
                raise OSError(marker)
        def fdopen(fd, *args, **kwargs):
            path = os.readlink('/proc/self/fd/' + str(fd))
            stream = real_fdopen(fd, *args, **kwargs)
            if path in (str(self.output / '00.stdout'), str(self.output / '00.stderr')):
                return StreamProxy(stream, path, inject)
            return stream
        def fsync(fd):
            path = os.readlink('/proc/self/fd/' + str(fd))
            real_fsync(fd)
            inject(path, 'fsync')
        case = self
        class Process:
            pid = 345678
            returncode = None
            def wait(self, timeout):
                waits.append(timeout)
                child_completed.append(True)
                if outcome == 'wait-error' and len(waits) == 1:
                    raise RuntimeError('first controlled wait exception')
                if outcome == 'unreaped' or (outcome == 'timeout' and len(waits) == 1):
                    raise subprocess.TimeoutExpired('controlled child', timeout)
                self.returncode = {'success': 0, 'nonzero': 7, 'timeout': -signal.SIGKILL,
                                   'wait-error': 0}[outcome]
                return self.returncode
        def popen(argv, **kwargs):
            paths = []
            for name in ('stdout', 'stderr'):
                stream = kwargs[name]
                fd = stream if isinstance(stream, int) else stream.fileno()
                paths.append(os.readlink('/proc/self/fd/' + str(fd)))
                os.write(fd, ('preserved ' + name + '\n').encode())
            index, target = case.check_launch(argv, *paths, 30.0)
            target.write_bytes(case.bytes_for(case.plan[index]))
            kwargs['preexec_fn']()
            return Process()
        with mock.patch.object(os, 'fdopen', fdopen), \
             mock.patch.object(os, 'fsync', fsync), \
             mock.patch.object(subprocess, 'Popen', popen), \
             mock.patch.object(os, 'killpg', lambda pid, sig: kills.append((pid, sig))), \
             mock.patch.object(os, 'getpgid', lambda pid: pid), \
             mock.patch.object(resource, 'setrlimit', lambda *args: None):
            report = self.collect(executor=None)
        self.assertEqual(injected, [(target_path, operation)], 'Cleanup fault must actually fire')
        for name in ('stdout', 'stderr'):
            self.assertIn((str(self.output / ('00.' + name)), 'close'), cleanup_actions)
        return report, marker, waits, kills

    def assert_cleanup_evidence(self, report, marker, outcome, waits, kills):
        self.assert_report(report, 'FAILED')
        self.assertEqual(len(self.calls), 1)
        self.assertEqual(report['counts']['requested_bytes'], 65536)
        self.assert_final_checks()
        receipt = json.loads((self.output / '00.result.json').read_text())
        expected = {'success': (0, False, True), 'nonzero': (7, False, True),
                    'timeout': (-signal.SIGKILL, True, True), 'unreaped': (None, True, False)}
        if outcome in expected:
            code, timed_out, reaped = expected[outcome]
            self.assertEqual(receipt['subprocess'],
                             {'returncode': code, 'timed_out': timed_out, 'reaped': reaped})
        errors = receipt.get('output_errors', []) + report['postcheck_errors']
        if outcome == 'success':
            # With no prior child failure, cleanup may itself be the first error.
            errors.append(report['first_error'])
        cleanup = [entry for entry in errors if marker in entry.get('message', '')]
        self.assertTrue(cleanup, 'Keep later cleanup error separately from the primary outcome')
        for entry in cleanup:
            permitted = ({'file', 'type', 'message'}, {'check', 'type', 'message'})
            self.assertTrue(set(entry) in permitted or
                            (outcome == 'success' and set(entry) == {'type', 'message'}))
        self.assertEqual((self.output / '00.stdout').read_bytes(), b'preserved stdout\n')
        self.assertEqual((self.output / '00.stderr').read_bytes(), b'preserved stderr\n')
        self.assertEqual((self.output / '00-before.loader.0.bin').read_bytes(), fixture.LOADER[:65536])
        self.assertTrue((self.output / '00.command.json').is_file())
        self.assertFalse((self.output / '01.command.json').exists())
        if outcome in ('nonzero', 'timeout', 'unreaped'):
            self.assertNotIn(marker, report['first_error']['message'])
        if outcome in ('timeout', 'unreaped'):
            self.assertEqual(waits, [30.0, 5.0])
            self.assertEqual(kills, [(345678, signal.SIGKILL)])
        elif outcome != 'wait-error':
            self.assertEqual(waits, [30.0])
            self.assertEqual(kills, [])
        if outcome == 'wait-error':
            self.assertEqual(report['first_error'],
                             {'type': 'RuntimeError', 'message': 'first controlled wait exception'})

    def cleanup_matrix(self, outcome):
        for stream in ('stdout', 'stderr'):
            for operation in ('flush', 'fsync', 'close'):
                with self.subTest(outcome=outcome, stream=stream, operation=operation), self.fresh() as case:
                    report, marker, waits, kills = case.controlled_cleanup(outcome, stream, operation)
                    case.assert_cleanup_evidence(report, marker, outcome, waits, kills)

    def test_successful_child_result_survives_each_later_stream_failure(self):
        self.cleanup_matrix('success')

    def test_nonzero_child_remains_primary_before_each_later_stream_failure(self):
        self.cleanup_matrix('nonzero')

    def test_timed_out_child_result_survives_each_later_stream_failure(self):
        self.cleanup_matrix('timeout')

    def test_unreaped_child_result_survives_each_later_stream_failure(self):
        self.cleanup_matrix('unreaped')

    def test_wait_exception_remains_primary_before_later_stream_failure(self):
        self.cleanup_matrix('wait-error')


def load_tests(loader, suite, pattern):
    # The original38 methods remain immutable and run in their own suite.
    return unittest.TestSuite(MotorFaultFinalization(name)
        for name in sorted(MotorFaultFinalization.__dict__) if name.startswith('test_'))


if __name__ == '__main__':
    unittest.main(verbosity=2)
