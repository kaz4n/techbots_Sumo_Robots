"""Run only D235's focused existing host cases, serially, without native I/O."""
import argparse
import contextlib
import hashlib
import io
import json
from pathlib import Path
import sys
import time
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from tests.tooling import test_dump_uart_fifo as fifo
from tests.tooling import test_dump_uart_unoq as native
from tests.tooling import test_dump_six_store as six


def archive_output(output):
    # /dev/shm may disappear between WSL invocations; seal before this process exits.
    raw = Path(__file__).resolve().parent
    archive = raw / (output.name + '.zip')
    members = []
    with zipfile.ZipFile(archive, 'x', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as saved:
        for path in sorted(output.rglob('*')):
            assert not path.is_symlink()
            if path.is_file():
                data = path.read_bytes()
                relative = path.relative_to(output).as_posix()
                members.append({'path': relative, 'bytes': len(data),
                                'sha256': hashlib.sha256(data).hexdigest()})
                saved.writestr(relative, data)
    with zipfile.ZipFile(archive) as saved:
        assert saved.namelist() == [item['path'] for item in members]
        for item in members:
            data = saved.read(item['path'])
            assert len(data) == item['bytes'] and hashlib.sha256(data).hexdigest() == item['sha256']
    record = {'source': str(output), 'archive': archive.name, 'members': members,
              'archive_bytes': archive.stat().st_size,
              'archive_sha256': hashlib.sha256(archive.read_bytes()).hexdigest(),
              'uncompressed_bytes': sum(item['bytes'] for item in members)}
    (raw / (output.name + '_archive.json')).write_text(json.dumps(record, indent=2) + '\n')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    output = ROOT / args.output
    output.mkdir(parents=True, exist_ok=False)
    loader = unittest.TestLoader()
    groups = [
        ('config', loader.loadTestsFromTestCase(six.ConfigTests)),
        ('native_current_six', loader.loadTestsFromTestCase(native.NativeDumpTests)),
        ('fifo_current_six', loader.loadTestsFromTestCase(fifo.DumpUartFifoTests)),
        ('capacity_model', loader.loadTestsFromTestCase(fifo.CapacityModelTests)),
        ('fifo_historical_eight', unittest.TestSuite(six.HistoricalEightTests(name) for name in (
            'test_real_fifo_room_and_stop_bit_completion_exact_packet_lengths',
            'test_unchanged_time_store_packet_caps_wrap_and_pending_identity',
            'test_live_loss_before_first_mid_and_after_final_store',
            'test_real_transfer_failure_then_cancel_retains_first_evidence'))),
    ]
    summary = []
    for name, suite in groups:
        destination = output / name
        destination.mkdir()
        fifo.RAW = native.RAW = six.RAW = destination
        transcript = io.StringIO()
        start = time.monotonic()
        with contextlib.redirect_stdout(transcript), contextlib.redirect_stderr(transcript):
            result = unittest.TextTestRunner(stream=transcript, verbosity=2).run(suite)
        saved = transcript.getvalue().encode()
        (destination / 'unittest.txt').write_bytes(saved)
        record = {'group': name, 'tests': result.testsRun, 'success': result.wasSuccessful(),
                  'failures': len(result.failures), 'errors': len(result.errors),
                  'skipped': len(result.skipped), 'seconds': time.monotonic() - start,
                  'transcript_sha256': hashlib.sha256(saved).hexdigest()}
        summary.append(record)
        (output / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
        print(json.dumps(record), flush=True)
        if not result.wasSuccessful():
            print(transcript.getvalue(), flush=True)
            archive_output(output)
            return 1
    archive_output(output)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
