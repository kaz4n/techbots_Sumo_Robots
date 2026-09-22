# Checks the pure matrix counter-delta contract with independent integer fixtures.
# Prevents invalid or ambiguous observations from being reported as forward progress.
# Unittest cases guard quiet import and never invoke hardware capture or a CLI run.
from contextlib import ExitStack, redirect_stderr, redirect_stdout
import importlib.util
import io
import os
from pathlib import Path
import socket
import subprocess
import sys
import unittest
from unittest import mock


PROJECT = Path(__file__).resolve().parents[2]
MATRIX_CAPTURE = PROJECT / 'tools/p0_matrix_capture.py'
UINT32_MAX = 0xFFFFFFFF
HALF_RANGE = 0x80000000


def import_matrix_without_actions():
    name = 'sumo_matrix_capture_contract_fixture'
    specification = importlib.util.spec_from_file_location(name, MATRIX_CAPTURE)
    module = importlib.util.module_from_spec(specification)
    stdout, stderr = io.StringIO(), io.StringIO()
    forbidden = AssertionError('Import must not perform capture or external actions')
    with ExitStack() as stack:
        for target in ('run', 'Popen', 'call', 'check_call', 'check_output'):
            stack.enter_context(mock.patch.object(subprocess, target, side_effect=forbidden))
        stack.enter_context(mock.patch.object(socket, 'socket', side_effect=forbidden))
        stack.enter_context(mock.patch.object(socket, 'create_connection', side_effect=forbidden))
        stack.enter_context(mock.patch.object(os, 'system', side_effect=forbidden))
        stack.enter_context(mock.patch('builtins.input', side_effect=forbidden))
        stack.enter_context(mock.patch.object(sys, 'argv', ['p0_matrix_capture.py', '--not-a-run']))
        stack.enter_context(mock.patch.object(sys, 'path', [str(MATRIX_CAPTURE.parent), *sys.path]))
        stack.enter_context(mock.patch.dict(sys.modules, {name: module}))
        stack.enter_context(redirect_stdout(stdout))
        stack.enter_context(redirect_stderr(stderr))
        specification.loader.exec_module(module)
    return module, stdout.getvalue(), stderr.getvalue()


class CounterSubclass(int):
    pass


class P0MatrixCounterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.module, cls.import_stdout, cls.import_stderr = import_matrix_without_actions()

    def assert_counter(self, first, second, advance):
        result = self.module.analyze_counter(first, second)
        self.assertIs(type(result), dict)
        self.assertEqual(dict(first=first, second=second, advance=advance), result)
        for field in ('first', 'second', 'advance'):
            self.assertIs(type(result[field]), int, field)

    def assert_rejected(self, first, second):
        with self.assertRaises(ValueError):
            self.module.analyze_counter(first, second)

    def test_import_is_quiet_and_does_not_execute_main_or_external_actions(self):
        self.assertEqual('', self.import_stdout)
        self.assertEqual('', self.import_stderr)
        self.assertTrue(callable(self.module.analyze_counter))

    def test_ordinary_forward_counts_preserve_observations_and_exact_difference(self):
        for first, second, advance in ((0, 1, 1), (1, 2, 1), (0, 12345, 12345),
                                       (123, 1000, 877), (UINT32_MAX - 1, UINT32_MAX, 1)):
            with self.subTest(first=first, second=second):
                self.assert_counter(first, second, advance)

    def test_forward_uint32_wrap_is_accepted_without_losing_original_values(self):
        for first, second, advance in ((UINT32_MAX, 0, 1), (UINT32_MAX - 1, 1, 3),
                                       (0xFFFFFFF0, 0x20, 48), (0xFFFF0000, 0x10000, 131072)):
            with self.subTest(first=first, second=second):
                self.assert_counter(first, second, advance)

    def test_largest_unambiguous_delta_is_accepted_with_or_without_wrap(self):
        self.assert_counter(0, HALF_RANGE - 1, HALF_RANGE - 1)
        self.assert_counter(UINT32_MAX, HALF_RANGE - 2, HALF_RANGE - 1)
        self.assert_counter(HALF_RANGE, UINT32_MAX, HALF_RANGE - 1)

    def test_equal_observations_are_not_progress_at_any_boundary(self):
        for value in (0, 1, HALF_RANGE - 1, HALF_RANGE, UINT32_MAX):
            with self.subTest(value=value):
                self.assert_rejected(value, value)

    def test_backward_and_exact_half_range_or_larger_deltas_are_rejected(self):
        cases = ((10, 9), (UINT32_MAX, UINT32_MAX - 1), (0, HALF_RANGE),
                 (HALF_RANGE, 0), (0, HALF_RANGE + 1), (UINT32_MAX, HALF_RANGE - 1),
                 (0, UINT32_MAX))
        for first, second in cases:
            with self.subTest(first=first, second=second):
                self.assert_rejected(first, second)

    def test_booleans_and_noninteger_fields_are_rejected_on_both_sides(self):
        bad = (False, True, None, '0', b'0', 0.0, 1.0, float('nan'),
               float('inf'), float('-inf'), [], {})
        for value in bad:
            with self.subTest(field='first', value=value):
                self.assert_rejected(value, 1)
            with self.subTest(field='second', value=value):
                self.assert_rejected(0, value)

    def test_exact_integer_contract_rejects_int_subclasses(self):
        self.assert_rejected(CounterSubclass(0), 1)
        self.assert_rejected(0, CounterSubclass(1))

    def test_values_outside_uint32_are_rejected_before_modular_conversion(self):
        for value in (-1, -HALF_RANGE, UINT32_MAX + 1, UINT32_MAX + 2, 1 << 128):
            with self.subTest(field='first', value=value):
                self.assert_rejected(value, 1)
            with self.subTest(field='second', value=value):
                self.assert_rejected(0, value)


if __name__ == '__main__':
    unittest.main()
