# Exercises the D-065 passive snapshot boundary with controlled readers.
# Rejects torn/remapped/incomplete evidence without touching a board or network.
# Coordinator-authored orchestration tests use independent record fixtures.
from contextlib import ExitStack
from copy import deepcopy
import unittest
from unittest import mock

from test_p0_qtr import load_decoder, prohibit_actions, record, normal_samples

BASE = 0x20001000
SIZE = 14424
# A synthetic extension envelope, not a claim about the final target ELF.
BSS_SIZE = 20000
EXTENSION = dict(node_address=0x20000100, bss_address=BASE, bss_size=BSS_SIZE,
                 visited_nodes=[0x20000100])


class Reader:
    def __init__(self, first, second):
        self.values = [first, second]
        self.report = {'extension': deepcopy(EXTENSION)}
        self.calls = []

    def read(self, label, address, size):
        if address != BASE + 4 or size != SIZE or len(self.calls) >= 2:
            raise AssertionError('Unexpected passive read')
        self.calls.append((label, address, size))
        value = self.values[len(self.calls) - 1]
        if isinstance(value, Exception):
            raise value
        return value


class Helper:
    def __init__(self, base=BASE, extension=None, error=None):
        self.base = base
        self.extension = deepcopy(EXTENSION if extension is None else extension)
        self.error = error

    def ram_range(self, address, size):
        if address != BASE + 4 or size != SIZE:
            raise AssertionError('Wrong record range')

    def find_bss(self, capture, size):
        if size != BSS_SIZE or len(capture.calls) != 2:
            raise AssertionError('Metadata must be rechecked after both snapshots')
        if self.error:
            raise self.error
        capture.report['extension'] = deepcopy(self.extension)
        return self.base


class QtrCaptureBoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.module, _, _ = load_decoder()

    def read(self, reader, helper=None):
        with ExitStack() as stack:
            prohibit_actions(stack)
            stack.enter_context(mock.patch.object(self.module, 'BSS_SIZE', BSS_SIZE))
            self.module.read_values(helper or Helper(), reader, BASE)

    def reject(self, reader, helper=None):
        with self.assertRaises((ValueError, OSError)):
            self.read(reader, helper)
        self.assertIsNot(True, reader.report.get('extension_confirmed_after_samples'))

    def test_two_identical_complete_records_then_metadata_are_required(self):
        reader = Reader(record(), record())
        self.read(reader)
        self.assertEqual(2, len(reader.calls))
        self.assertEqual(BASE + 4, reader.report['record_address'])
        self.assertTrue(reader.report['extension_confirmed_after_samples'])
        self.assertEqual(200, reader.report['metrics']['samples'])
        self.assertEqual(100, reader.report['metrics']['diagnostic_pullup']['deadline_samples'])

    def test_byte_changes_with_unchanged_metrics_rejected(self):
        rows = normal_samples()
        rows[1][2], rows[2][2] = 1, 3
        first = record(rows)
        rows[1], rows[2] = rows[2], rows[1]
        self.reject(Reader(first, record(rows)))

    def test_incomplete_and_stimulus_failure_rejected(self):
        rows = normal_samples()
        rows[100][11:13] = [1, 14]
        rows[100][13] = 100
        for data in (record(complete=0), record(ready_mask=0), record(rows)):
            self.reject(Reader(data, data))

    def test_wrong_lengths_rejected(self):
        for data in (record()[:-1], record() + b'\0'):
            self.reject(Reader(data, data))
            self.reject(Reader(record(), data))

    def test_relocated_bss_rejected(self):
        self.reject(Reader(record(), record()), Helper(base=BASE + 4))

    def test_changed_extension_metadata_rejected(self):
        for key, value in (('node_address', 0x20000104), ('bss_address', BASE + 4),
                           ('bss_size', BSS_SIZE + 4), ('visited_nodes', [0x20000200])):
            changed = dict(EXTENSION, **{key: value})
            self.reject(Reader(record(), record()), Helper(extension=changed))

    def test_either_read_error_propagates(self):
        for index in (0, 1):
            values = [record(), record()]
            values[index] = OSError('Synthetic passive read failure')
            self.reject(Reader(*values))

    def test_metadata_error_propagates(self):
        self.reject(Reader(record(), record()), Helper(error=OSError('Synthetic metadata failure')))


if __name__ == '__main__':
    unittest.main()
