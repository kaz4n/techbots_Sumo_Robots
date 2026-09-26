# Tests D223 read-only UART holder visibility from its independent contract.
# Uses synthetic process/task/FD metadata and never opens a UART or proc file.
# Stable samples, races, permissions, limits and unknown qualification are checked.
import copy
from contextlib import ExitStack
import importlib.util
import json
from pathlib import Path
import sys
import types
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
SUBJECT = ROOT / 'tools/observe_uart_holders.py'
UART = dict(major=239, minor=1, dev=5, ino=12)
BOUNDARY = dict(boot_id='fixture-boot', kernel='fixture-kernel',
    device=dict(major=239, minor=1, character=True),
    router=dict(pid=100, start=1000, executable=dict(sha256='fixture-router-hash')))
HOLDER_IDENTITY = dict(status=dict(Name='router', Uid='0 0 0 0', Gid='0 0 0 0'),
    executable='/usr/bin/arduino-router', executable_stat=dict(dev=1, ino=2))


class Metadata:
    def __init__(self):
        self.processes = [100]
        self.tasks = {100: [100, 101]}
        self.tables = {(100, 100): {3: None}, (100, 101): {4: dict(UART)}}
        self.cap = set()
        self.failures = {}
        self.calls = []
        self.fd_calls = 0
        self.boundary_calls = 0
        self.identities = {}

    def check(self, key):
        self.calls.append(key)
        if key in self.failures:
            raise self.failures[key]

    def ids(self, pid=None, tid=None):
        self.check(('ids', pid, tid))
        if pid is None:
            values = self.processes
        elif tid is None:
            values = self.tasks.get(pid, [])
        else:
            values = list(self.tables.get((pid, tid), {}))
        return list(values), (pid, tid) in self.cap

    def start(self, pid, tid=None):
        self.check(('start', pid, tid))
        return (pid if tid is None else tid) * 10

    def fd(self, pid, tid, fd):
        self.check(('fd', pid, tid, fd))
        self.fd_calls += 1
        return copy.deepcopy(self.tables[(pid, tid)][fd])

    def holder_identity(self, pid):
        self.check(('holder_identity', pid))
        return copy.deepcopy(self.identities.get(pid, HOLDER_IDENTITY))

    def boundary(self):
        self.check(('boundary',))
        self.boundary_calls += 1
        return copy.deepcopy(BOUNDARY)


def load_subject():
    spec = importlib.util.spec_from_file_location('_d223_subject', SUBJECT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class UartObservationContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # The first production read occurs only at the separately authorized run.
        cls.subject = load_subject()

    def observe(self, ops=None, clock=None):
        ops = Metadata() if ops is None else ops
        result = self.subject.observe(ops, clock=(lambda: 0.0) if clock is None else clock)
        self.assertEqual(result['schema'], 'sumox-uart-holders-v1')
        for name in ('continuous_exclusivity', 'framing_clean', 'receiver_ready'):
            self.assertEqual(result[name], 'UNKNOWN')
        _, serialized = self.subject.bounded_report(result)
        self.assertLessEqual(len(serialized.encode('utf-8') if isinstance(serialized, str) else serialized), 1048576)
        return result

    def incomplete(self, result):
        self.assertEqual(result['visibility'], 'INCOMPLETE')
        self.assertTrue(not result.get('boundary_equal', False) or
                        not result.get('holders_equal', False) or
                        any(not sweep['complete'] for sweep in result['sweeps']))

    def test_private_thread_holder_is_observed_and_identity_is_cached_per_sweep(self):
        ops = Metadata(); result = self.observe(ops)
        self.assertEqual(result['visibility'], 'SAMPLED_COMPLETE')
        self.assertIs(result['boundary_equal'], True)
        self.assertIs(result['holders_equal'], True)
        self.assertEqual(len(result['sweeps']), 2)
        for sweep in result['sweeps']:
            self.assertIs(sweep['complete'], True)
            self.assertEqual(sweep['processes'], 1)
            self.assertEqual(sweep['tasks'], 2)
            self.assertEqual(sweep['fd_stats'], 2)
            self.assertEqual(sweep['problem_count'], 0)
            self.assertEqual(sweep['problems'], [])
            self.assertEqual(sweep['holders'], [dict(pid=100, tid=101, fd=4,
                process_start=1000, task_start=1010, device=UART)])
            self.assertEqual(sweep['holder_processes'], {'100': HOLDER_IDENTITY})
        self.assertEqual(ops.calls.count(('holder_identity', 100)), 2)

    def test_stable_absence_stays_sampled_and_never_grants_exclusivity(self):
        ops = Metadata()
        ops.tables[(100, 101)][4] = dict(major=1, minor=3, dev=5, ino=18)
        result = self.observe(ops)
        self.assertEqual(result['visibility'], 'SAMPLED_COMPLETE')
        self.assertTrue(all(sweep['holders'] == [] for sweep in result['sweeps']))
        self.assertEqual(ops.calls.count(('holder_identity', 100)), 0)

    def test_every_denied_or_vanished_table_or_stat_is_incomplete(self):
        locations = (('ids', None, None), ('ids', 100, None), ('ids', 100, 100),
                     ('start', 100, None), ('start', 100, 101),
                     ('fd', 100, 101, 4), ('holder_identity', 100))
        for location in locations:
            for error in (PermissionError('fixture denied'), FileNotFoundError('fixture vanished')):
                ops = Metadata(); ops.failures[location] = error
                with self.subTest(location=location, error=type(error).__name__):
                    result = self.observe(ops); self.incomplete(result)
                    self.assertGreater(sum(sweep['problem_count'] for sweep in result['sweeps']), 0)

    def test_process_and_task_id_reuse_cannot_be_complete(self):
        for selected in ((100, None), (100, 101)):
            ops = Metadata(); original = ops.start; counts = {}
            def changing(pid, tid=None):
                value = original(pid, tid)
                key = (pid, tid); counts[key] = counts.get(key, 0) + 1
                return value + (1 if key == selected and counts[key] > 1 else 0)
            ops.start = changing
            with self.subTest(selected=selected):
                self.incomplete(self.observe(ops))

    def test_changed_process_task_and_fd_name_sets_are_not_complete(self):
        for selected, extra in (((None, None), 200), ((100, None), 102), ((100, 101), 9)):
            ops = Metadata(); original = ops.ids; counts = {}
            def changing(pid=None, tid=None):
                values, cap = original(pid, tid)
                key = (pid, tid); counts[key] = counts.get(key, 0) + 1
                if key == selected and counts[key] > 1 and extra not in values:
                    values.append(extra)
                    if tid is not None:
                        ops.tables[(pid, tid)][extra] = None
                return values, cap
            ops.ids = changing
            with self.subTest(selected=selected):
                self.incomplete(self.observe(ops))

    def test_changed_uart_descriptor_identity_between_sweeps_is_not_complete(self):
        ops = Metadata(); original = ops.fd; count = 0
        def changing(pid, tid, fd):
            nonlocal count
            value = original(pid, tid, fd)
            if value is not None:
                count += 1
                value['ino'] += count - 1
            return value
        ops.fd = changing
        result = self.observe(ops)
        self.incomplete(result)
        self.assertIs(result['holders_equal'], False)

    def test_changed_holder_executable_identity_between_sweeps_is_not_complete(self):
        ops = Metadata(); original = ops.holder_identity; count = 0
        def changing(pid):
            nonlocal count
            value = original(pid); count += 1
            value['executable_stat']['ino'] += count - 1
            return value
        ops.holder_identity = changing
        result = self.observe(ops)
        self.incomplete(result)
        self.assertIs(result['holders_equal'], False)

    def test_boot_router_and_device_boundary_changes_remain_incomplete(self):
        variants = (dict(BOUNDARY, boot_id='new-boot'),
                    dict(BOUNDARY, kernel='new-kernel'),
                    dict(BOUNDARY, device=dict(major=239, minor=1, character=True, ino=99)),
                    dict(BOUNDARY, router=dict(pid=200, start=1, executable=dict(sha256='new'))))
        for after in variants:
            ops = Metadata()
            def changing():
                ops.boundary_calls += 1
                return copy.deepcopy(BOUNDARY if ops.boundary_calls == 1 else after)
            ops.boundary = changing
            with self.subTest(after=after):
                result = self.observe(ops); self.incomplete(result)
                self.assertIs(result['boundary_equal'], False)

    def test_boundary_failure_is_recorded_without_claiming_an_empty_device(self):
        ops = Metadata(); ops.failures[('boundary',)] = PermissionError('boundary denied')
        self.incomplete(self.observe(ops))

    def test_process_task_and_fd_enumeration_caps_are_always_incomplete(self):
        for selected in ((None, None), (100, None), (100, 101)):
            ops = Metadata(); ops.cap.add(selected)
            with self.subTest(selected=selected):
                result = self.observe(ops); self.incomplete(result)
                self.assertGreater(sum(sweep['problem_count'] for sweep in result['sweeps']), 0)

    def test_exact_global_fd_limit_with_unvisited_tasks_cannot_finish_a_sweep(self):
        ops = Metadata()
        ops.tasks = {100: list(range(100, 117))}
        ops.tables = {(100, tid): {fd: None for fd in range(4096)} for tid in ops.tasks[100]}
        result = self.observe(ops)
        self.incomplete(result)
        self.assertLessEqual(ops.fd_calls, 65536)
        self.assertLessEqual(sum(sweep['fd_stats'] for sweep in result['sweeps']), 65536)
        self.assertFalse(result['sweeps'][0]['complete'])
        self.assertGreater(sum(sweep['problem_count'] for sweep in result['sweeps']), 0)

    def test_deadline_produces_incomplete_even_without_permission_errors(self):
        ticks = 0
        def clock():
            nonlocal ticks
            value = float(ticks * 16); ticks += 1
            return value
        result = self.observe(Metadata(), clock)
        self.incomplete(result)
        self.assertGreater(sum(sweep['problem_count'] for sweep in result['sweeps']), 0)

    def test_problem_details_are_bounded_but_all_problem_counts_survive(self):
        ops = Metadata(); ops.processes = list(range(1, 1301))
        for pid in ops.processes:
            ops.failures[('ids', pid, None)] = PermissionError('denied table ' + str(pid))
        result = self.observe(ops)
        self.incomplete(result)
        for sweep in result['sweeps']:
            self.assertLessEqual(len(sweep['problems']), 1024)
            self.assertGreaterEqual(sweep['problem_count'], 1300)

    def test_holder_limit_is_not_a_complete_partial_list(self):
        ops = Metadata()
        ops.tables = {(100, tid): {fd: dict(UART) for fd in range(4096)} for tid in (100, 101)}
        result = self.observe(ops)
        self.incomplete(result)
        for sweep in result['sweeps']:
            self.assertLessEqual(len(sweep['holders']), 4096)
            self.assertGreater(sweep['problem_count'], 0)

    def test_output_limit_preserves_aggregate_scan_and_error_counts(self):
        ops = Metadata(); ops.processes.append(200)
        ops.failures[('ids', 200, None)] = PermissionError('one genuine scan failure')
        identity = copy.deepcopy(HOLDER_IDENTITY)
        identity['status']['Name'] = 'x' * 1100000
        ops.identities[100] = identity
        raw = self.subject.observe(ops, clock=lambda: 0.0)
        result, body = self.subject.bounded_report(raw)
        self.incomplete(result)
        self.assertEqual(len(result['sweeps']), 2)
        self.assertLessEqual(len(body.encode('utf-8') if isinstance(body, str) else body), 1048576)
        self.assertEqual(sum(sweep['problem_count'] for sweep in result['sweeps']),
                         sum(sweep['problem_count'] for sweep in raw['sweeps']))
        self.assertGreaterEqual(sum(sweep['problem_count'] for sweep in result['sweeps']), 2)
        self.assertGreaterEqual(sum(sweep['processes'] for sweep in result['sweeps']), 2)
        self.assertGreaterEqual(sum(sweep['tasks'] for sweep in result['sweeps']), 4)
        self.assertGreaterEqual(sum(sweep['fd_stats'] for sweep in result['sweeps']), 4)

    def test_main_refuses_nonroot_and_extra_arguments_before_metadata(self):
        for uid, arguments in ((1000, ['observe_uart_holders.py']),
                               (0, ['observe_uart_holders.py', '--arbitrary-path', '/tmp/other'])):
            with self.subTest(uid=uid, arguments=arguments), ExitStack() as stack:
                stack.enter_context(mock.patch.object(self.subject.sys, 'argv', arguments))
                stack.enter_context(mock.patch.object(self.subject.sys, 'flags', types.SimpleNamespace(isolated=1)))
                stack.enter_context(mock.patch.object(self.subject.sys, 'dont_write_bytecode', True))
                stack.enter_context(mock.patch.object(self.subject.os, 'geteuid', return_value=uid, create=True))
                stack.enter_context(mock.patch.object(self.subject, 'LinuxMetadata',
                    side_effect=AssertionError('Refused request constructed metadata provider')))
                with self.assertRaises((SystemExit, RuntimeError, ValueError)):
                    self.subject.main()


if __name__ == '__main__':
    if not sys.dont_write_bytecode:
        raise SystemExit('Run with Python -I -B')
    unittest.main(verbosity=2)
