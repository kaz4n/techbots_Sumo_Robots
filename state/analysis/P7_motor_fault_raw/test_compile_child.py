# Tests the fixed compile caller's child-process contract using harmless Linux jobs.
# Separates stdout/stderr, process-group timeout and launch failure from board evidence.
# Runs only in /dev/shm with a cwd-only Popen shim; no compiler or board is contacted.
import base64
from contextlib import redirect_stdout
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import time
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[3]
CALLER = Path(__file__).with_name('compile_motor_fault.py')
CAPTURE = ROOT / 'state/analysis/P7_static_startup_raw/capture_remote.py'
CALLER_SHA256 = 'f804f4527d2937ff57773d7140b398ef84b6855e8574f58026a9ee570f8132f9'
CAPTURE_SHA256 = 'ab0bb32031c1986cc58db1f410a0bdca59449a9dae237672085a81e291b33458'
EXPECTED_ENV = {'HOME': '/home/arduino', 'USER': 'arduino', 'LOGNAME': 'arduino',
                'PATH': '/usr/bin:/bin', 'LANG': 'C.UTF-8'}


class CompileChildTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if sys.platform != 'linux' or not Path('/dev/shm').is_dir():
            raise unittest.SkipTest('Linux /proc and RAM scratch required')
        for path, digest in ((CALLER, CALLER_SHA256), (CAPTURE, CAPTURE_SHA256)):
            actual = hashlib.sha256(path.read_bytes()).hexdigest()
            if actual != digest:
                raise AssertionError('Frozen fixture source differs: ' + str(path))
        name = '_sumox_inert_compile_child_fixture'
        spec = importlib.util.spec_from_file_location(name, CALLER)
        cls.caller = importlib.util.module_from_spec(spec)
        sys.modules[name] = cls.caller
        cls.addClassCleanup(sys.modules.pop, name, None)
        spec.loader.exec_module(cls.caller)
        cls.wait_source = cls.caller.extracted_wait(CAPTURE.read_bytes())

    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix='sumox-compile-child-', dir='/dev/shm')
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        (self.root / 'commands').mkdir()
        self.processes = []
        self.assertEqual(EXPECTED_ENV, self.caller.ENV)

    def run_child(self, name, argv, deadline=2.0):
        real_popen = subprocess.Popen
        packet = {'name': name, 'argv': argv, 'deadline': deadline}
        namespace = {'Path': Path, 'os': os, 'json': json, 'packet': packet,
                     'REMOTE': self.root, 'ENV': dict(self.caller.ENV)}
        exec(self.wait_source, namespace)

        def host_popen(command, *args, **kwargs):
            self.assertEqual(argv, command)
            self.assertEqual((), args)
            self.assertEqual(subprocess.DEVNULL, kwargs.get('stdin'))
            self.assertIsInstance(kwargs.get('stdout'), io.IOBase)
            self.assertIsInstance(kwargs.get('stderr'), io.IOBase)
            self.assertIsNot(kwargs['stdout'], kwargs['stderr'])
            self.assertEqual(EXPECTED_ENV, kwargs.get('env'))
            self.assertEqual('/home/arduino', kwargs.get('cwd'))
            self.assertFalse(kwargs.get('shell', False))
            self.assertIs(True, kwargs.get('start_new_session'))
            kwargs['cwd'] = str(self.root)
            process = real_popen(command, **kwargs)
            self.processes.append(process)
            return process

        output = io.StringIO()
        with mock.patch.object(subprocess, 'Popen', side_effect=host_popen) as popen, redirect_stdout(output):
            exec(self.caller.REMOTE_CHILD, namespace)
        popen.assert_called_once()
        record = json.loads(output.getvalue())
        folder = self.root / 'commands' / name
        self.assertEqual(record, json.loads((folder / 'result.json').read_text()))
        self.assertIsInstance(json.loads((folder / 'intent.json').read_text()), dict)
        stdout, stderr = (folder / 'stdout').read_bytes(), (folder / 'stderr').read_bytes()
        self.assertEqual(stdout, base64.b64decode(record['stdout_base64'], validate=True))
        self.assertEqual(stderr, base64.b64decode(record['stderr_base64'], validate=True))
        self.assertEqual(len(stdout), record['stdout_bytes'])
        self.assertEqual(len(stderr), record['stderr_bytes'])
        return record, stdout, stderr

    @staticmethod
    def python(script):
        return [sys.executable, '-B', '-c', script]

    @staticmethod
    def process_state(pid):
        path = Path('/proc') / str(pid) / 'stat'
        try:
            return path.read_text().rsplit(')', 1)[1].split()[0]
        except FileNotFoundError:
            return None

    def cleanup_owned_group(self):
        for process in self.processes:
            if process.pid <= 1 or process.pid == os.getpgrp():
                continue
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            try:
                process.wait(timeout=1.0)
            except subprocess.TimeoutExpired:
                pass

    def test_zero_exit_keeps_exact_distinct_binary_stdout_and_stderr(self):
        expected_out, expected_err = b'out\x00\xff\n', b'err\xfe\x00\n'
        argv = self.python('import os; os.write(1, b"out\\x00\\xff\\n"); '
                           'os.write(2, b"err\\xfe\\x00\\n")')
        record, stdout, stderr = self.run_child('success', argv)
        self.assertEqual('COMPLETED', record['status'])
        self.assertEqual(expected_out, stdout)
        self.assertEqual(expected_err, stderr)
        self.assertEqual(0, record['execution']['returncode'])
        self.assertFalse(record['execution']['timed_out'])
        self.assertTrue(record['execution']['reaped'])

    def test_exit37_keeps_raw_streams_and_failed_reaped_execution(self):
        argv = self.python('import os; os.write(1, b"before failure\\n"); '
                           'os.write(2, b"failure detail\\x00\\n"); os._exit(37)')
        record, stdout, stderr = self.run_child('exit37', argv)
        self.assertEqual('FAILED', record['status'])
        self.assertEqual(b'before failure\n', stdout)
        self.assertEqual(b'failure detail\x00\n', stderr)
        self.assertEqual(37, record['execution']['returncode'])
        self.assertFalse(record['execution']['timed_out'])
        self.assertTrue(record['execution']['reaped'])

    def test_deadline_kills_parent_and_harmless_descendant_group_and_reaps_parent(self):
        self.addCleanup(self.cleanup_owned_group)
        pid_file = self.root / 'owned-pids.json'
        script = ('import json,os,subprocess,sys,time; '
                  'child=subprocess.Popen([sys.executable,"-B","-c","import time; time.sleep(30)"]); '
                  f'open({str(pid_file)!r},"w").write(json.dumps({{"parent":os.getpid(),'
                  '"child":child.pid,"group":os.getpgrp()})); '
                  'os.write(1,b"started\\n"); time.sleep(30)')
        record, stdout, _ = self.run_child('deadline', self.python(script), deadline=0.25)
        self.assertEqual('FAILED', record['status'])
        self.assertTrue(record['execution']['timed_out'])
        self.assertTrue(record['execution']['reaped'])
        self.assertNotEqual(0, record['execution']['returncode'])
        self.assertEqual(b'started\n', stdout)
        pids = json.loads(pid_file.read_text())
        self.assertEqual(self.processes[0].pid, pids['parent'])
        self.assertEqual(pids['parent'], pids['group'])
        self.assertNotEqual(os.getpgrp(), pids['group'])
        deadline = time.monotonic() + 1.0
        states = [self.process_state(pids[key]) for key in ('parent', 'child')]
        while any(state not in (None, 'Z', 'X') for state in states) and time.monotonic() < deadline:
            time.sleep(0.01)
            states = [self.process_state(pids[key]) for key in ('parent', 'child')]
        for key, state in zip(('parent', 'child'), states):
            with self.subTest(process=key, state=state):
                self.assertIn(state, (None, 'Z', 'X'))

    def test_missing_executable_records_launch_failure_without_execution_success(self):
        missing = str(self.root / 'executable-that-does-not-exist')
        record, stdout, stderr = self.run_child('missing', [missing])
        self.assertEqual('FAILED', record['status'])
        self.assertEqual(b'', stdout)
        self.assertEqual(b'', stderr)
        serialized = json.dumps(record)
        self.assertIn('FileNotFoundError', serialized)
        self.assertIn(missing, serialized)
        execution = record.get('execution')
        if execution is not None:
            self.assertNotEqual(0, execution.get('returncode'))
        self.assertEqual([], self.processes)


if __name__ == '__main__':
    unittest.main(verbosity=2)
