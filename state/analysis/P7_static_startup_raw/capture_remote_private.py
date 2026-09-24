# Reviews bounded D153 process admission, late timeout reduction and failure order.
# Uses the frozen public fixture with controlled host-only filesystem/process seams.
# Freeze this reviewer-authored supplemental suite before its first execution.
import contextlib
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from types import SimpleNamespace
import unittest
from unittest import mock


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location('d153_frozen_public_fixture',
                                             HERE / 'test_capture_remote.py')
PUBLIC = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PUBLIC)


@unittest.skipUnless(sys.platform.startswith('linux'), 'Linux descriptor semantics required')
class SupplementalReview(unittest.TestCase):
    def setUp(self):
        self.case = PUBLIC.CaptureRemoteContract('test_complete_exact_plan_receipts_and_diagnostics')
        self.case.setUp()
        self.addCleanup(self.case.doCleanups)

    def process_boundary(self, count):
        case = self.case
        original_scan, original_read = os.scandir, case.helper.logical_read
        observed = []

        @contextlib.contextmanager
        def scan(fd):
            if isinstance(fd, int) and os.readlink('/proc/self/fd/' + str(fd)) == str(case.logical('/proc')):
                yield (SimpleNamespace(name=str(pid)) for pid in range(1, count + 1))
            else:
                with original_scan(fd) as entries:
                    yield entries

        def read(fd, logical, limit, proc=False):
            if re.fullmatch(r'/proc/[0-9]+/comm', logical):
                self.assertEqual((limit, proc), (256, True))
                observed.append(logical)
                return b'python3\n'
            return original_read(fd, logical, limit, proc)

        with mock.patch.object(os, 'scandir', scan), \
             mock.patch.object(case.helper, 'logical_read', read):
            if count == 4096:
                case.assert_report(case.collect(), 'COLLECTED')
                self.assertEqual(len(observed), 4096)
                self.assertEqual(len(case.calls), 18)
            else:
                with self.assertRaises(Exception):
                    case.collect()
                self.assertEqual(case.calls, [])
                self.assertEqual(observed, [])
                self.assertFalse(case.output.exists())

    def test_4096_numeric_process_entries_are_admitted(self):
        self.process_boundary(4096)

    def test_4097_numeric_process_entries_refuse_before_claim(self):
        self.process_boundary(4097)

    def test_stream_setup_reduces_actual_wait_to_remaining_budget(self):
        case, waits = self.case, []
        original_open = os.open

        def opened(path, flags, *args, **kwargs):
            fd = original_open(path, flags, *args, **kwargs)
            if str(path) == '00.stderr' and flags & os.O_CREAT:
                case.clock.now = 680.0
            return fd

        class Process:
            pid = 456789

            def wait(self, timeout):
                waits.append(timeout)
                return 1

        def popen(argv, **kwargs):
            streams = [os.readlink('/proc/self/fd/' + str(kwargs[key].fileno()))
                       for key in ('stdout', 'stderr')]
            index, target = case.check_launch(argv, *streams, 20.0)
            case.write_raw(index, target)
            return Process()

        with mock.patch.object(os, 'open', opened), \
             mock.patch.object(subprocess, 'Popen', popen):
            report = case.collect(executor=None)
        case.assert_report(report, 'FAILED')
        self.assertEqual(waits, [20.0])
        self.assertEqual(len(case.calls), 1)
        receipt = json.loads((case.output / '00.result.json').read_text())
        self.assertEqual(receipt['subprocess'], {'returncode': 1, 'timed_out': False, 'reaped': True})

    def test_claim_body_failure_survives_additional_context_exit_failure(self):
        case = self.case
        original_directory, original_fsync = case.helper.directory, os.fsync
        state = {'primary': False, 'secondary': False}

        def fsync(fd):
            if not state['primary'] and os.readlink('/proc/self/fd/' + str(fd)) == str(case.output.parent):
                state['primary'] = True
                raise OSError('private primary parent fsync failure')
            return original_fsync(fd)

        @contextlib.contextmanager
        def directory(root_fd, logical):
            with original_directory(root_fd, logical) as fd:
                try:
                    yield fd
                finally:
                    if logical == '/home/arduino/sumox26_codex_build' and state['primary'] and not state['secondary']:
                        state['secondary'] = True
                        raise RuntimeError('private additional parent context failure')

        with mock.patch.object(case.helper, 'directory', directory), \
             mock.patch.object(os, 'fsync', fsync):
            report = case.collect()
        case.assert_report(report, 'FAILED')
        self.assertEqual(report['first_error'], {'type': 'OSError', 'message': 'private primary parent fsync failure'})
        self.assertTrue(any(item['type'] == 'RuntimeError' and item['message'] ==
                            'private additional parent context failure'
                            for item in report['postcheck_errors']))
        self.assertEqual(state, {'primary': True, 'secondary': True})
        self.assertEqual(case.calls, [])
        self.assertFalse((case.output / 'capture_attempt.json').exists())
        for key in case.bindings['files']:
            self.assertEqual(sum(name == key for name, _ in case.pin_checks), 2)


if __name__ == '__main__':
    unittest.main()
