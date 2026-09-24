# Tests compile completion-receipt failures at the actual local write boundary.
# Distinguishes known zero completion from transport timeout without changing validators.
# Execute only after the separate receipt freeze and coordinator host-test GO.
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import unittest
from unittest import mock

import test_static_runner as fixture


class StaticRunnerCompletionReceipts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        freeze = json.loads(Path(__file__).with_name('freeze_receipts.json').read_text())
        if freeze.get('status') != 'FROZEN_FOR_AUTHORIZED_HOST_TEST':
            raise RuntimeError('Receipt supplement is not frozen')
        for name, expected in freeze['inputs_sha256'].items():
            if hashlib.sha256((fixture.ROOT/name).read_bytes()).hexdigest() != expected:
                raise RuntimeError('Receipt supplement input changed: '+name)
        fixture.StaticRunnerContract.setUpClass.__func__(cls)

    setUp = fixture.StaticRunnerContract.setUp
    run_probe = fixture.StaticRunnerContract.run_probe
    result = fixture.StaticRunnerContract.result

    def completion_write_failure(self, dispatched, failure):
        original = io.open
        rejected = []
        def observed(file, mode='r', *args, **kwargs):
            if (dispatched and isinstance(file, (str, bytes, os.PathLike)) and
                    Path(os.fsdecode(file)) == self.receipt/'0017.json' and
                    any(flag in mode for flag in 'wax+')):
                rejected.append(True)
                raise failure
            return original(file, mode, *args, **kwargs)
        return rejected, observed

    def test_known_zero_completion_write_failure_still_performs_full_terminal_postchecks(self):
        dispatched = []
        def completed(response):
            dispatched.append(True)
            return response
        protocol = fixture.Protocol(self, self.receipt, {'compile': completed})
        original = OSError('Synthetic known-zero completion receipt failure')
        rejected, observed = self.completion_write_failure(dispatched, original)
        with mock.patch.object(io, 'open', observed):
            with self.assertRaises(OSError) as caught:
                self.run_probe(protocol)
        self.assertIs(caught.exception, original)
        self.assertTrue(rejected)
        self.assertEqual(len(protocol.calls), 20)
        self.assertEqual([name for name, _ in protocol.calls[17:]],
                         ['remote_postcheck', 'installed_pins', 'overrides'])
        result = self.result()
        self.assertEqual(result['status'], 'FAILED')
        self.assertEqual((result['query_attempts'], result['compile_attempts']), (1, 1))
        self.assertEqual(result['error'], {'class': type(original).__name__, 'message': str(original)})
        self.assertEqual(result['postcheck_errors'], [])
        self.assertFalse((self.receipt/'app.ino.elf').exists())

    def test_timeout_completion_write_failure_preserves_original_and_local_postchecks(self):
        dispatched, local_reads = [], set()
        original = subprocess.TimeoutExpired(['synthetic-compile'], 1800,
                                             output=b'partial\x00stdout', stderr=b'partial\xffstderr')
        def timed_out(response):
            dispatched.append(True)
            raise original
        protocol = fixture.Protocol(self, self.receipt, {'compile': timed_out})
        rejected, observed = self.completion_write_failure(dispatched, OSError('Synthetic timeout receipt failure'))
        read_bytes = Path.read_bytes
        def read(path):
            if dispatched:
                if path == fixture.ROOT/'tools/app_build_commands.json': local_reads.add('pins')
                if path == fixture.ROOT/'build/stage/app/app.ino': local_reads.add('stage')
            return read_bytes(path)
        with mock.patch.object(io, 'open', observed), mock.patch.object(Path, 'read_bytes', read):
            with self.assertRaises(subprocess.TimeoutExpired) as caught:
                self.run_probe(protocol)
        self.assertIs(caught.exception, original)
        self.assertEqual((caught.exception.output, caught.exception.stderr),
                         (b'partial\x00stdout', b'partial\xffstderr'))
        self.assertTrue(rejected)
        self.assertEqual(len(protocol.calls), 17)
        self.assertEqual(local_reads, {'pins', 'stage'})
        result = self.result()
        self.assertEqual(result['status'], 'COMPILE_OUTCOME_UNKNOWN')
        self.assertEqual((result['query_attempts'], result['compile_attempts']), (1, 1))
        self.assertEqual(result['error'], {'class': type(original).__name__, 'message': str(original)})
        self.assertFalse((self.receipt/'app.ino.elf').exists())


if __name__ == '__main__':
    unittest.main()
