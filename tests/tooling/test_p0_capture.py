# Checks the diagnostic histogram contract independently of the capture implementation.
# Prevents incomplete, inconsistent or censored timing evidence from becoming exact claims.
# Pure unittest cases use synthetic RAM values and forbid board commands during import.
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
CAPTURE_TOOL = PROJECT / 'tools/p0_capture.py'
SAMPLES = 60000
BINS = 1001
UINT32_MAX = 4294967295


def load_capture_without_actions():
    name = 'sumo_capture_contract_fixture'
    specification = importlib.util.spec_from_file_location(name, CAPTURE_TOOL)
    module = importlib.util.module_from_spec(specification)
    stdout, stderr = io.StringIO(), io.StringIO()
    forbidden = AssertionError('Import must not start capture, commands or networking')
    with ExitStack() as stack:
        for target in ('run', 'Popen', 'call', 'check_call', 'check_output'):
            stack.enter_context(mock.patch.object(subprocess, target, side_effect=forbidden))
        stack.enter_context(mock.patch.object(socket, 'socket', side_effect=forbidden))
        stack.enter_context(mock.patch.object(socket, 'create_connection', side_effect=forbidden))
        stack.enter_context(mock.patch.object(os, 'system', side_effect=forbidden))
        stack.enter_context(mock.patch('builtins.input', side_effect=forbidden))
        stack.enter_context(mock.patch.object(sys, 'argv', ['p0_capture.py', '--not-a-real-run']))
        stack.enter_context(mock.patch.dict(sys.modules, {name: module}))
        stack.enter_context(redirect_stdout(stdout))
        stack.enter_context(redirect_stderr(stderr))
        specification.loader.exec_module(module)
    return module, stdout.getvalue(), stderr.getvalue()


def histogram():
    # Every expected shape is literal and independent of production configuration.
    return [0] * BINS


class P0HistogramAnalysisTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.module, cls.import_stdout, cls.import_stderr = load_capture_without_actions()

    def analyze(self, values, maximum=0, over_period=0, samples=SAMPLES):
        return self.module.analyze_histogram(samples, maximum, over_period, values)

    def assert_summary(self, result, p99, maximum, over_period, censored=False):
        self.assertIsInstance(result, dict)
        expected = dict(p99_us=p99, p99_censored=censored, samples=SAMPLES,
                        max_lateness_us=maximum, over_period=over_period)
        for key, value in expected.items():
            self.assertIn(key, result)
            self.assertEqual(value, result[key], key)
            self.assertIs(type(result[key]), type(value), key)

    def assert_rejected(self, values, maximum=0, over_period=0, samples=SAMPLES):
        # The public contract requires rejection, not one particular validation class.
        with self.assertRaises((TypeError, ValueError)):
            self.analyze(values, maximum, over_period, samples)

    def test_import_is_quiet_and_does_not_execute_main_or_board_commands(self):
        self.assertEqual('', self.import_stdout)
        self.assertEqual('', self.import_stderr)
        self.assertTrue(callable(self.module.analyze_histogram))

    def test_zero_lateness_has_exact_zero_p99_and_preserves_complete_count(self):
        values = histogram()
        values[0] = SAMPLES
        self.assert_summary(self.analyze(values), 0, 0, 0)

    def test_nearest_rank_59400_uses_first_inclusive_cumulative_bin(self):
        for below, expected in ((59399, 27), (59400, 4), (59401, 4)):
            with self.subTest(below=below):
                values = histogram()
                values[4], values[27], values[900] = below, 1, SAMPLES - below - 1
                self.assert_summary(self.analyze(values, 900), expected, 900, 0)

    def test_spread_distribution_uses_counts_not_bin_count_or_interpolation(self):
        values = histogram()
        values[0], values[100], values[900] = 30000, 29400, 600
        self.assert_summary(self.analyze(values, 900), 100, 900, 0)
        values[100], values[900] = 29399, 601
        self.assert_summary(self.analyze(values, 900), 900, 900, 0)

    def test_600_overflow_samples_leave_p99_exact_but_601_make_it_censored(self):
        for overflow, p99, censored in ((600, 7, False), (601, 1000, True)):
            with self.subTest(overflow=overflow):
                values = histogram()
                values[7], values[1000] = SAMPLES - overflow, overflow
                self.assert_summary(self.analyze(values, 12345, overflow),
                                    p99, 12345, overflow, censored)

    def test_last_bin_stays_censored_even_when_observed_maximum_is_exactly_1000(self):
        values = histogram()
        values[1000] = SAMPLES
        self.assert_summary(self.analyze(values, 1000, SAMPLES), 1000, 1000, SAMPLES, True)

    def test_single_uint32_max_outlier_does_not_hide_the_max_or_inflate_p99(self):
        values = histogram()
        values[0], values[1000] = 59999, 1
        self.assert_summary(self.analyze(values, UINT32_MAX, 1), 0, UINT32_MAX, 1)
        values[0], values[1000] = 0, SAMPLES
        self.assert_summary(self.analyze(values, UINT32_MAX, SAMPLES),
                            1000, UINT32_MAX, SAMPLES, True)

    def test_highest_exact_bin_999_is_not_censored(self):
        values = histogram()
        values[999] = SAMPLES
        self.assert_summary(self.analyze(values, 999), 999, 999, 0)

    def test_sample_count_must_be_exactly_60000(self):
        values = histogram()
        values[0] = SAMPLES
        for count in (0, 1, 59999, 60001, UINT32_MAX):
            with self.subTest(samples=count):
                self.assert_rejected(values, samples=count)

    def test_boolean_and_noninteger_scalar_fields_are_rejected(self):
        values = histogram()
        values[0] = SAMPLES
        bad_values = (False, True, None, '0', 0.0, 60000.0, float('nan'), float('inf'), [])
        for field in ('samples', 'maximum', 'over_period'):
            for value in bad_values:
                with self.subTest(field=field, value=value):
                    arguments = dict(samples=SAMPLES, maximum=0, over_period=0)
                    arguments[field] = value
                    self.assert_rejected(values, **arguments)

    def test_negative_and_above_uint32_scalar_fields_are_rejected(self):
        values = histogram()
        values[0] = SAMPLES
        for field in ('samples', 'maximum', 'over_period'):
            for value in (-1, UINT32_MAX + 1):
                with self.subTest(field=field, value=value):
                    arguments = dict(samples=SAMPLES, maximum=0, over_period=0)
                    arguments[field] = value
                    self.assert_rejected(values, **arguments)

    def test_wrong_histogram_shape_or_noncollection_is_rejected(self):
        for values in (None, False, 1001, [], [0] * 1000, [0] * 1002,
                       '0' * 1001, [[0]] * 1001):
            with self.subTest(shape=type(values).__name__, length=len(values)
                              if hasattr(values, '__len__') else None):
                self.assert_rejected(values)

    def test_bins_reject_booleans_nonintegers_negative_and_oversized_values(self):
        for value in (False, True, 0.0, 1.0, None, '1', [], float('nan'),
                      float('inf'), -1, UINT32_MAX + 1):
            with self.subTest(value=value):
                values = histogram()
                one = value is True or type(value) is float and value == 1.0
                values[0] = SAMPLES - 1 if one else SAMPLES
                values[1] = value
                maximum = 1 if values[0] == SAMPLES - 1 else 0
                self.assert_rejected(values, maximum)

    def test_histogram_sum_must_equal_complete_sample_count(self):
        for total in (0, 59999, 60001):
            with self.subTest(total=total):
                values = histogram()
                values[0] = total
                self.assert_rejected(values)

    def test_over_period_count_must_equal_the_overflow_bin(self):
        values = histogram()
        values[0], values[1000] = 59990, 10
        for count in (0, 9, 11, SAMPLES):
            with self.subTest(over_period=count):
                self.assert_rejected(values, 1000, count)
        self.assert_summary(self.analyze(values, 1000, 10), 0, 1000, 10)

    def test_maximum_must_match_exact_bins_or_bound_the_overflow_bin(self):
        values = histogram()
        values[0], values[14] = 59999, 1
        for maximum in (0, 13, 15, 999, 1000, UINT32_MAX):
            with self.subTest(maximum=maximum, overflow=False):
                self.assert_rejected(values, maximum)
        self.assert_summary(self.analyze(values, 14), 0, 14, 0)
        values[14], values[1000] = 0, 1
        for maximum in (0, 14, 999):
            with self.subTest(maximum=maximum, overflow=True):
                self.assert_rejected(values, maximum, 1)

    def test_pure_analysis_does_not_change_histogram_on_success_or_rejection(self):
        values = histogram()
        values[0], values[27] = 59000, 1000
        original = list(values)
        first = self.analyze(values, 27)
        self.assertEqual(original, values)
        self.assertEqual(first, self.analyze(values, 27))
        self.assert_rejected(values, 26)
        self.assertEqual(original, values)


if __name__ == '__main__':
    unittest.main()
