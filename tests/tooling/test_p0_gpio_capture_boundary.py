# Tests the D-064 passive record/extension boundary using contract-only fakes.
# Rejects torn, invalid or remapped evidence before it can be accepted as frozen.
# Python unittest runs injected readers with no board, MCU or network operations.
from contextlib import ExitStack
from copy import deepcopy
import unittest

from test_p0_gpio import (FIELD_NAMES, INTERVAL_NAMES, load_capture_without_actions,
                          prohibit_actions, record)


BASE = 0x20001000
# Exact layout supplied by the independent target-binary audit on 2026-09-23.
RECORD_OFFSET = 4
RECORD_SIZE = 14428
BSS_SIZE = 21980
EXTENSION = {
    'node_address': 0x20000100,
    'bss_address': BASE,
    'bss_size': BSS_SIZE,
    'visited_nodes': [0x20000100],
}


class FakeCapture:
    def __init__(self, records):
        self.records = list(records)
        self.reads = []
        self.report = {'extension': deepcopy(EXTENSION)}

    def read(self, label, address, size):
        if address != BASE + RECORD_OFFSET or size != RECORD_SIZE:
            raise AssertionError('Each GPIO snapshot must read the whole fixed record')
        self.reads.append((label, address, size))
        if len(self.reads) > 2:
            raise AssertionError('The contract permits exactly two GPIO snapshots')
        value = self.records[len(self.reads) - 1]
        if isinstance(value, Exception):
            raise value
        return value


class FakeHelper:
    def __init__(self, *, post_base=BASE, post_extension=None, error=None):
        self.post_base = post_base
        self.post_extension = deepcopy(EXTENSION if post_extension is None else post_extension)
        self.error = error
        self.range_checks = []
        self.revalidations = []

    def ram_range(self, address, size):
        self.range_checks.append((address, size))
        if not BASE <= address or not address + size <= BASE + BSS_SIZE:
            raise ValueError('Fixture RAM range is out of bounds')

    def find_bss(self, capture, expected_size):
        if expected_size != BSS_SIZE:
            raise AssertionError('Revalidation must require the reviewed BSS size')
        self.revalidations.append(len(capture.reads))
        if self.error is not None:
            raise self.error
        capture.report['extension'] = deepcopy(self.post_extension)
        return self.post_base


class P0GpioCaptureBoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.module, cls.import_stdout, cls.import_stderr = load_capture_without_actions()

    def read_values(self, helper, capture):
        with ExitStack() as stack:
            prohibit_actions(stack)
            return self.module.read_values(helper, capture, BASE)

    def assert_rejected(self, helper, capture):
        with self.assertRaises((ValueError, RuntimeError)):
            self.read_values(helper, capture)
        self.assertIsNot(True, capture.report.get('extension_confirmed_after_samples'))

    def test_d064_import_is_quiet_and_runs_no_transport(self):
        self.assertEqual('', self.import_stdout)
        self.assertEqual('', self.import_stderr)
        self.assertTrue(callable(self.module.read_values))

    def test_d064_unchanged_full_records_report_metrics_and_revalidate_identity(self):
        data = record()
        capture, helper = FakeCapture([data, data]), FakeHelper()
        self.read_values(helper, capture)
        self.assertEqual(2, len(capture.reads))
        self.assertIn((BASE + RECORD_OFFSET, RECORD_SIZE), helper.range_checks)
        self.assertIn(2, helper.revalidations, 'Identity must be checked after both samples')
        self.assertEqual(EXTENSION, capture.report['extension'])
        self.assertIs(True, capture.report['extension_confirmed_after_samples'])
        address = capture.report['record_address']
        self.assertEqual(BASE + RECORD_OFFSET, int(address, 0) if isinstance(address, str) else address)
        sample = (2, 3, 5, 7, 11, 13, 0, 1, 1)
        expected = {
            'version': 1, 'samples': 400, 'total_elapsed_us': 16400,
            'first_call': dict(zip(FIELD_NAMES, sample)),
            'subsequent_calls': {'samples': 399},
            'overhead': {'min_us': 2, 'max_us': 2, 'p99_us': 2},
            'readbacks': {'low_matches': 400, 'high_matches': 400,
                          'pair_matches': 400, 'final_high': True},
        }
        for field, value in zip(INTERVAL_NAMES, sample[:6]):
            expected['subsequent_calls'][field] = {'min_us': value, 'max_us': value, 'p99_us': value}
        for key, value in expected.items():
            with self.subTest(metric=key):
                self.assertEqual(value, capture.report['metrics'][key])

    def test_d064_changed_raw_records_fail_even_with_identical_aggregate_metrics(self):
        first_samples = [(2, 3, 5, 7, 11, 13, 0, 1, 1)] * 400
        first_samples[100] = (2, 3, 5, 7, 11, 12, 0, 1, 1)
        first_samples[200] = (2, 3, 5, 7, 11, 14, 0, 1, 1)
        second_samples = list(first_samples)
        second_samples[100], second_samples[200] = first_samples[200], first_samples[100]
        for first, second in ((record(first_samples), record(second_samples)),
                              (record(start=0), record(start=1))):
            with self.subTest(changed_sample_bytes=first[28:] != second[28:]):
                self.assert_rejected(FakeHelper(), FakeCapture([first, second]))

    def test_d064_identical_incomplete_bad_version_count_ready_final_records_rejected(self):
        for fields in ({'complete': 0}, {'complete': 2}, {'version': 0}, {'version': 2},
                       {'completed': 0}, {'completed': 399}, {'completed': 401},
                       {'ready': 0}, {'ready': 2}, {'final_level': 0}, {'final_level': -19}):
            with self.subTest(fields=fields):
                data = record(**fields)
                self.assert_rejected(FakeHelper(), FakeCapture([data, data]))

    def test_d064_identical_wrong_signed_readbacks_rejected_in_each_level_field(self):
        for index in (0, 399):
            for field in range(6, 9):
                for value in (-19, -1, 2, 1 if field == 6 else 0):
                    with self.subTest(index=index, field=field, value=value):
                        samples = [(2, 3, 5, 7, 11, 13, 0, 1, 1)] * 400
                        sample = list(samples[index])
                        sample[field] = value
                        samples[index] = tuple(sample)
                        data = record(samples)
                        self.assert_rejected(FakeHelper(), FakeCapture([data, data]))

    def test_d064_identical_short_or_overlong_reads_are_rejected(self):
        for data in (record()[:-1], record() + b'\0'):
            with self.subTest(length=len(data)):
                self.assert_rejected(FakeHelper(), FakeCapture([data, data]))

    def test_d064_short_second_snapshot_is_rejected(self):
        self.assert_rejected(FakeHelper(), FakeCapture([record(), record()[:-1]]))

    def test_d064_changed_bss_base_after_identical_records_is_rejected(self):
        data = record()
        self.assert_rejected(FakeHelper(post_base=BASE + 4), FakeCapture([data, data]))

    def test_d064_changed_extension_node_after_identical_records_is_rejected(self):
        extension = deepcopy(EXTENSION)
        extension['node_address'] += 4
        data = record()
        self.assert_rejected(FakeHelper(post_extension=extension), FakeCapture([data, data]))

    def test_d064_changed_extension_bss_size_after_identical_records_is_rejected(self):
        extension = deepcopy(EXTENSION)
        extension['bss_size'] += 4
        data = record()
        self.assert_rejected(FakeHelper(post_extension=extension), FakeCapture([data, data]))

    def test_d064_changed_extension_bss_address_after_identical_records_is_rejected(self):
        extension = deepcopy(EXTENSION)
        extension['bss_address'] += 4
        data = record()
        self.assert_rejected(FakeHelper(post_extension=extension), FakeCapture([data, data]))

    def test_d064_changed_visited_nodes_after_identical_records_is_rejected(self):
        extension = deepcopy(EXTENSION)
        extension['visited_nodes'] = [0x20000104, 0x20000100]
        data = record()
        self.assert_rejected(FakeHelper(post_extension=extension), FakeCapture([data, data]))

    def test_d064_transport_exception_from_either_snapshot_propagates(self):
        for index in (0, 1):
            with self.subTest(snapshot=index):
                error = OSError('Synthetic passive read failure')
                values = [record(), record()]
                values[index] = error
                capture = FakeCapture(values)
                with self.assertRaises(OSError) as caught:
                    self.read_values(FakeHelper(), capture)
                self.assertIs(error, caught.exception)
                self.assertIsNot(True, capture.report.get('extension_confirmed_after_samples'))

    def test_d064_transport_exception_during_extension_revalidation_propagates(self):
        error = OSError('Synthetic extension lookup failure')
        data = record()
        capture = FakeCapture([data, data])
        with self.assertRaises(OSError) as caught:
            self.read_values(FakeHelper(error=error), capture)
        self.assertIs(error, caught.exception)
        self.assertIsNot(True, capture.report.get('extension_confirmed_after_samples'))


if __name__ == '__main__':
    unittest.main()
