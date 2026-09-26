# Tests caller-bound B15 identities against independently constructed v1 wire bytes.
# A fresh connection receipt cannot authenticate stale UART data or repair framing.
# Offline unittest cases preserve raw evidence and never open a board connection.
import contextlib
import importlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'tools'))
from tests.tooling.test_dump_match import wire, chunks, rechecksum

MAXIMUM = (1 << 64) - 1
FRESH = 0xF123456789ABCDEF
STALE = 202472


class IntSubclass(int):
    pass


class RecorderSessionReceiverTests(unittest.TestCase):
    def setUp(self):
        self.module = importlib.import_module('dump_match')
        self.temporary = tempfile.TemporaryDirectory(prefix='sumox-session-parser-')
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)

    def parse(self, data, expected=FRESH, sizes=(1, 3, 17, 64, 7)):
        parser = self.module.Parser(expected_session=expected)
        for part in chunks(data, sizes):
            parser.feed(part)
        return parser, parser.finish()

    def retained_failure(self, data, expected=FRESH, source=None):
        with self.assertRaises(self.module.CaptureError) as caught:
            self.module.save_capture([data] if source is None else source,
                                     self.root, expected_session=expected)
        partial = Path(caught.exception.partial_path)
        self.assertTrue(partial.name.endswith('.partial'))
        self.assertEqual((partial / 'wire.txt').read_bytes(), data)
        self.assertFalse((partial / 'capture.json').exists())
        return caught.exception, json.loads((partial / 'error.json').read_text())

    def test_exact_integer_domain_before_input_consumption_or_output_creation(self):
        invalid = (True, False, 0, -1, MAXIMUM + 1, 1.0, '1', b'1', IntSubclass(1), [], {})
        for value in invalid:
            with self.subTest(value=repr(value)):
                with self.assertRaises((ValueError, TypeError)):
                    self.module.Parser(expected_session=value)
                output = self.root / 'never-created'
                with self.assertRaises((ValueError, TypeError)):
                    self.module.save_capture(iter(()), output, expected_session=value)
                self.assertFalse(output.exists())
        for value in (1, FRESH, MAXIMUM):
            parser, capture = self.parse(wire(session=value), value)
            self.assertEqual((capture.session, parser.expected_session,
                              parser.observed_session, parser.rejected_session),
                             (value, value, value, None))

    def test_zero_argument_legacy_keeps_v1_bytes_and_no_expected_identity(self):
        data = wire()
        parser = self.module.Parser()
        parser.feed(data)
        self.assertEqual(parser.finish().session, 10)
        self.assertIsNone(parser.expected_session)
        destination = self.module.save_capture([data], self.root)
        self.assertEqual((destination / 'wire.txt').read_bytes(), data)
        evidence = json.loads((destination / 'capture.json').read_text())
        self.assertIsNone(evidence['expected_session'])
        self.assertEqual(evidence['observed_session'], 10)

    def test_all_single_splits_and_irregular_chunks_preserve_exact_identity(self):
        data = wire(session=FRESH)
        for split in range(len(data) + 1):
            parser = self.module.Parser(expected_session=FRESH)
            parser.feed(data[:split])
            parser.feed(data[split:])
            self.assertEqual(parser.finish().session, FRESH)
        for sizes in ((1,), (4096,), (1, 2, 17, 64, 257), (37, 1, 1024, 3)):
            parser, capture = self.parse(data, sizes=sizes)
            self.assertEqual(capture.frame_count, 2)
            self.assertEqual(parser.observed_session, FRESH)

    def test_wrong_begin_is_retained_and_never_published_even_with_valid_crc(self):
        error, evidence = self.retained_failure(wire(session=STALE))
        self.assertEqual(error.code, 'SESSION_MISMATCH')
        self.assertEqual((evidence['expected_session'], evidence['observed_session'],
                          evidence['rejected_session']), (FRESH, STALE, STALE))

    def test_each_payload_tag_and_end_rejects_another_identity_despite_correct_crc(self):
        original = wire(session=FRESH).splitlines(keepends=True)
        for tag in (b'SH', b'SR', b'FH', b'FR', b'EH', b'ER', b'END'):
            with self.subTest(tag=tag):
                lines = list(original)
                index = next(i for i, line in enumerate(lines) if line.startswith(tag + b','))
                fields = lines[index].rstrip(b'\n').split(b',')
                fields[1] = str(STALE).encode()
                lines[index] = b','.join(fields) + b'\n'
                data = rechecksum(b''.join(lines))
                error, evidence = self.retained_failure(data)
                self.assertEqual(error.code, 'SESSION_MISMATCH')
                self.assertEqual((evidence['expected_session'], evidence['observed_session'],
                                  evidence['rejected_session']), (FRESH, FRESH, STALE))

    def test_stale_complete_stream_cannot_borrow_fresh_connection_ticket(self):
        class ConnectedBytes:
            outcome = {'returncode': 0}
            connection_evidence = {'state': 'TERMINAL', 'ticket': 'a' * 32,
                'router_registration': 'UNKNOWN', 'terminal': {'reason': 'END_OBSERVED'}}
            def __iter__(self):
                yield wire(session=STALE)
        error, evidence = self.retained_failure(wire(session=STALE), source=ConnectedBytes())
        self.assertEqual(error.code, 'SESSION_MISMATCH')
        self.assertEqual(evidence['connection_evidence'], ConnectedBytes.connection_evidence)
        self.assertEqual(evidence['transport_outcome'], {'returncode': 0})

    def test_stale_prefix_fresh_suffix_concatenation_and_garbage_never_resynchronize(self):
        stale = wire(session=STALE)
        fresh = wire(session=FRESH)
        cases = (stale + fresh, stale[:11] + fresh, stale[:stale.index(b'FH,')] + fresh,
                 b'garbage\n' + fresh, fresh + stale, fresh + fresh)
        for data in cases:
            with self.subTest(prefix=data[:40]):
                self.retained_failure(data)

    def test_truncation_retains_expected_and_observed_identity_without_success(self):
        fresh = wire(session=FRESH)
        for data, observed in ((fresh[:12], None), (fresh[:fresh.index(b'FR,')], FRESH),
                               (fresh[:-1], FRESH), (fresh[:fresh.index(b'END,')], FRESH)):
            with self.subTest(length=len(data)):
                _, evidence = self.retained_failure(data)
                self.assertEqual(evidence['expected_session'], FRESH)
                self.assertEqual(evidence['observed_session'], observed)
                self.assertIsNone(evidence['rejected_session'])

    def test_valid_publication_retains_raw_and_bound_identity_without_hardware_claim(self):
        data = wire(session=MAXIMUM)
        destination = self.module.save_capture(chunks(data), self.root, expected_session=MAXIMUM)
        evidence = json.loads((destination / 'capture.json').read_text())
        self.assertEqual((destination / 'wire.txt').read_bytes(), data)
        self.assertEqual((evidence['expected_session'], evidence['observed_session'],
                          evidence['session']), (MAXIMUM, MAXIMUM, MAXIMUM))
        self.assertIsNone(evidence['rejected_session'])
        self.assertFalse(evidence['hardware_acceptance'])
        self.assertEqual(evidence['transport_integrity'], 'PASS')

    def test_cli_canonical_decimal_rejects_coercion_before_any_io(self):
        invalid = ('0', '-1', '+1', '01', ' 1', '1 ', '1.0', '1e3', '0x10',
                   '18446744073709551616', '１２', '')
        for value in invalid:
            with self.subTest(value=value), mock.patch.object(self.module.board, 'remote',
                    side_effect=AssertionError('unexpected remote')):
                with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as caught:
                    self.module.main(['--expected-session', value, '--output-dir', str(self.root / 'no')])
                self.assertEqual(caught.exception.code, 2)
                self.assertFalse((self.root / 'no').exists())

    def test_cli_offline_bound_identity_and_observer_exclusion(self):
        source = self.root / 'input.wire'
        source.write_bytes(wire(session=MAXIMUM))
        output = self.root / 'capture'
        with mock.patch('subprocess.Popen', side_effect=AssertionError('offline process')), \
             mock.patch('socket.create_connection', side_effect=AssertionError('offline network')), \
             contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            result = self.module.main(['--input', str(source), '--output-dir', str(output),
                                       '--expected-session', str(MAXIMUM)])
            self.assertEqual(result, 0)
            with self.assertRaises(SystemExit) as caught:
                self.module.main(['--observe-connection', 'a' * 32, '--expected-session', '1'])
            self.assertEqual(caught.exception.code, 2)
        destination = next(output.iterdir())
        self.assertEqual(json.loads((destination / 'capture.json').read_text())['expected_session'], MAXIMUM)


if __name__ == '__main__':
    unittest.main()
