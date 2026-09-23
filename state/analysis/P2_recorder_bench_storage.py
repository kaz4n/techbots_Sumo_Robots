"""Independently inspect retained synthetic rows in already-captured D091 RAM.

Offline only. CSV files come from MEM-AP pool snapshots, never UART/log-dump proof.
Target DWARF and readelf receipts pin the private offsets; no guessed MCU reads.
"""
import csv
import hashlib
import json
from pathlib import Path
import re
import struct
import sys
import zlib

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
import validate_csv_bundle as wire

RAW = Path(__file__).parent / 'P2_recorder_bench_raw'
POOL_BASE, POOL_SIZE = 0x20013890, 262144


def require_layout():
    layout = json.loads((RAW / 'storage_layout.json').read_text())
    assert layout['returncode'] == 0 and layout['remote_returncode'] == 0
    assert layout['sha256'] == '0bb4a53eb5ce1e497ccd8bc3a1f51f4ac067ca66f5fd0189bbc76afa74934860'
    values = [int(value, 16) for value in re.findall(r'^\$\d+ = (0x[0-9a-f]+)$',
                                                   layout['stdout'], re.MULTILINE)]
    assert values == [0x28870, 0xb50, 0, 0x1fc04, 0x27c10, 0, 0x1fbec,
                      0x1fbf0, 0, 0x8000, 26, 8, 4]
    symbols = json.loads((RAW / 'final_symbols.json').read_text())['stdout']
    line = next(line for line in symbols.splitlines() if line.endswith('_ZN15recorder_native12_GLOBAL__N_16runnerE'))
    fields = line.split()
    assert fields[1:7] == ['00000090', '0x28870', 'OBJECT', 'LOCAL', 'DEFAULT', '9']


def rows(blob, capture):
    assert len(blob) == POOL_SIZE
    base = capture['extension']['bss_address'] + 0x90 + 0xb50 - POOL_BASE
    assert 0 <= base and base + 0x27c10 <= len(blob)
    first, count = struct.unpack_from('<II', blob, base + 0x1fbec)
    event_count = struct.unpack_from('<I', blob, base + 0x1fc04 + 0x8000)[0]
    diag = capture['diagnostics']['report']
    assert 0 <= first < 5001 and count == diag['frame_count'] <= 5001
    assert event_count == diag['event_count'] <= 4096
    frames = [blob[base + ((first + i) % 5001) * 26:base + ((first + i) % 5001) * 26 + 26]
              for i in range(count)]
    events = [blob[base + 0x1fc04 + i * 8:base + 0x1fc04 + i * 8 + 8] for i in range(event_count)]
    assert all(len(row) == 26 and row[25] <= 2 for row in frames)
    assert all(len(row) == 8 for row in events)
    crc = 0
    for row in frames + events:
        crc = zlib.crc32(row, crc)
    assert crc == diag['crc32'], 'Independent retained RAM CRC differs from MCU checksum'
    return frames, events, crc


def main(folder):
    require_layout()
    capture = json.loads((folder / 'capture.json').read_text())
    assert capture['status'] == 'CAPTURED' and capture['flash_identity_verified']
    assert capture['diagnostics']['report']['phase'] == 4
    first = rows((folder / 'pool-first.bin').read_bytes(), capture)
    second = rows((folder / 'pool-second.bin').read_bytes(), capture)
    assert first == second, 'Retained rows changed across snapshots'
    frames, events, crc = first
    times = [wire.FRAME_WIRE.unpack(row[:25])[0] for row in frames]
    intervals = [(b - a) & 0xffffffff for a, b in zip(times, times[1:])]
    report = dict(origin='SYNTHETIC_INPUTS_ACTUAL_MCU_EXECUTION',
                  capture_method='MEM_AP_OFFLINE_EXTRACTION_NOT_UART_DUMP',
                  frame_count=len(frames), event_count=len(events), crc32=crc,
                  independent_crc_matches_mcu=True, retained_rows_identical=True,
                  first_frame_ms=times[0], last_frame_ms=times[-1],
                  interval_ms_counts={str(i): intervals.count(i) for i in sorted(set(intervals))},
                  pack_status_counts={str(i): sum(row[25] == i for row in frames) for i in range(3)})
    with (folder / 'memap_frames.csv').open('x', newline='', encoding='ascii') as out:
        writer = csv.writer(out); writer.writerow(wire.FRAME_FIELDS)
        for i, row in enumerate(frames):
            writer.writerow((1, i, row[25], *wire.FRAME_WIRE.unpack(row[:25]), row[:25].hex()))
    with (folder / 'memap_events.csv').open('x', newline='', encoding='ascii') as out:
        writer = csv.writer(out); writer.writerow(wire.EVENT_FIELDS)
        for i, row in enumerate(events):
            writer.writerow((1, i, *wire.EVENT_WIRE.unpack(row), row.hex()))
    with (folder / 'storage_extraction.json').open('x', encoding='utf-8') as out:
        json.dump(report, out, indent=2); out.write('\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main(Path(sys.argv[1]))
