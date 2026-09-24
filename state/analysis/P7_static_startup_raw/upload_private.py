# Reviews D154 failure preservation after inspecting its implementation.
# Supplements the unchanged public fixture with nested stream-close failures.
# Freeze this code before controlled Linux execution; no native child is run.
import os
import signal
import subprocess
import unittest
from unittest import mock

from test_upload_remote import ARGV, SUCCESS, UploadContract


class CloseFailure:
    def __init__(self, stream, observed):
        self.stream, self.observed = stream, observed

    def __enter__(self):
        return self.stream.__enter__()

    def __exit__(self, *exc_info):
        self.stream.__exit__(*exc_info)
        self.observed.append(self.stream.closed)
        raise OSError('later stderr close failure')


class UploadPrivate(UploadContract):
    def close_failure_run(self, wait_values, kill_error=None):
        real_fdopen, observed = os.fdopen, []

        def substituted(fd, *args, **kwargs):
            name = self.actual_path(fd).name
            stream = real_fdopen(fd, *args, **kwargs)
            return CloseFailure(stream, observed) if name == 'upload.stderr' else stream

        with mock.patch.object(os, 'fdopen', side_effect=substituted):
            report, kill = self.default_run(wait_values, kill_error)
        self.assertEqual(observed, [True])
        self.assert_report(report, 'FAILED')
        self.assertEqual(report['attempts'], 1)
        self.assertEqual(report['stdout'], self.stdout.decode())
        self.assertEqual(report['stderr'], self.stderr.decode())
        return report, kill

    def assert_later_close_recorded(self, report):
        errors = [item for item in report['postcheck_errors']
                  if item['message'] == 'later stderr close failure']
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0]['type'], 'OSError')

    def test_kill_error_and_reaped_flags_survive_later_close_error(self):
        report, kill = self.close_failure_run(
            [subprocess.TimeoutExpired(ARGV, 120), -9], OSError('primary kill failure'))
        self.assertEqual(report['first_error'],
                         {'type': 'OSError', 'message': 'primary kill failure'})
        self.assertEqual(report['subprocess'],
                         {'returncode': -9, 'timed_out': True, 'reaped': True})
        self.assert_later_close_recorded(report)
        kill.assert_called_once_with(45671, signal.SIGKILL)
        self.assertEqual(self.child.wait.call_args_list,
                         [mock.call(timeout=120), mock.call(timeout=5)])

    def test_wait_error_and_unknown_flags_survive_later_close_error(self):
        report, kill = self.close_failure_run(
            [RuntimeError('primary wait failure'), subprocess.TimeoutExpired(ARGV, 5)])
        self.assertEqual(report['first_error'],
                         {'type': 'RuntimeError', 'message': 'primary wait failure'})
        self.assertEqual(report['subprocess'],
                         {'returncode': None, 'timed_out': False, 'reaped': False})
        self.assert_later_close_recorded(report)
        kill.assert_called_once_with(45671, signal.SIGKILL)
        self.assertEqual(self.child.wait.call_args_list,
                         [mock.call(timeout=120), mock.call(timeout=5)])

    def test_success_flags_remain_failed_when_stream_close_fails(self):
        report, kill = self.close_failure_run([0])
        self.assertEqual(report['first_error'],
                         {'type': 'OSError', 'message': 'later stderr close failure'})
        self.assertEqual(report['subprocess'], SUCCESS)
        kill.assert_not_called()
        self.child.wait.assert_called_once_with(timeout=120)


def load_tests(loader, tests, pattern):
    # Only these three reviewer cases run; inherited public tests stay separate.
    return unittest.TestSuite(UploadPrivate(name) for name in sorted(
        name for name in UploadPrivate.__dict__ if name.startswith('test_')))


if __name__ == '__main__':
    unittest.main(verbosity=2)
