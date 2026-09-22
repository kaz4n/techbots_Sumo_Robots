# Reads the exact reviewed startup-only QTR-style diagnostic through passive MEM-AP.
# Separates neutral observations from diagnostic pull-up timeout stimulation.
# D-065 independent decoder tests and exact source/binary reviews precede capture.
import argparse
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import struct
import subprocess
import sys
import time

HELPER_HASH = '885c4e4206aea4ac9e03c4e92e48258db2a0ae302ff83a86430e6913afeeb57c'
# Exact default-startup image; source and binary audits must precede execution.
ARTIFACT_DIR = Path('/home/arduino/sumox26-build/'
                    '61d7a2d00ec1e7f1782d0a7439bd71cb123338dc1073e55abe43b9c6e3fe521e/'
                    'p0_qtr/artifacts/bench-default')
ELF_HASH = '080142c992024089255c0ced50904bb0ef4a6f41a7caf748ddecfcde625d1077'
BINARY_HASH = '46d305b50bd71f8f48aa8fb97a8f71d5faff1faa032dad1db123c1b62d93e632'
ARTIFACT_SIZE = 76924
BSS_SIZE = 21980
BSS_ELF_ADDRESS = 0x5778
RECORD_OFFSET = 4
RECORD_SIZE = 14424


def require(condition, message):
    if not condition:
        raise ValueError(message)


def statistics(values):
    ordered = sorted(values)
    return dict(min_us=ordered[0], max_us=ordered[-1],
                p99_us=ordered[(len(ordered) * 99 + 99) // 100 - 1])


INTERVAL_FIELDS = ('overhead_us', 'drive_us', 'charge_us', 'release_us',
                   'observe_us', 'cleanup_us', 'total_us')


def sample_dict(row):
    names = ('mode', 'outcome', *INTERVAL_FIELDS, 'charge_polls', 'polls',
             'low_mask', 'timeout_mask')
    return dict(zip(names, row[:13]), first_low_us=list(row[13:17]),
                cleanup_calls=row[17])


def validate_sample(row, mode):
    require(row[0] == mode and row[1] in (1, 2), 'QTR dataset or outcome invalid')
    require(all(value < 0x80000000 for value in row[2:9]), 'ambiguous QTR interval')
    require(row[4] >= 11 and 1 <= row[9] <= 4096 and 1 <= row[10] <= 4096,
            'QTR charge or polling guard invalid')
    require(row[11] <= 15 and row[12] == (15 ^ row[11]), 'QTR masks inconsistent')
    require(row[17] == 4, 'QTR cleanup attempts incomplete')
    require(row[8] == sum(row[3:8]), 'QTR total does not equal phase intervals')
    for pin, first in enumerate(row[13:17]):
        if row[11] & (1 << pin):
            require(first <= row[6], 'QTR first LOW exceeds observation')
        else:
            require(first == 0xffffffff, 'QTR unseen LOW timestamp is not unset')
    if row[1] == 1:
        require(row[11] == 15 and row[6] < 1500, 'QTR all-LOW outcome inconsistent')
    else:
        require(row[6] >= 1500, 'QTR deadline was not reached')


def dataset(rows):
    intervals = {name: statistics([row[i + 2] for row in rows[1:]])
                 for i, name in enumerate(INTERVAL_FIELDS)}
    masks = {}
    for row in rows:
        key = str(row[12])
        masks[key] = masks.get(key, 0) + 1
    return dict(samples=100, first_sample=sample_dict(rows[0]),
                subsequent_samples=dict(samples=99, intervals=intervals),
                overhead=statistics([row[2] for row in rows]),
                all_low_samples=sum(row[1] == 1 for row in rows),
                deadline_samples=sum(row[1] == 2 for row in rows),
                timeout_masks=masks,
                poll_range=dict(min=min(row[10] for row in rows),
                                max=max(row[10] for row in rows)))


def analyze_record(data):
    require(isinstance(data, (bytes, bytearray)) and len(data) == RECORD_SIZE,
            'QTR record must contain exactly14424 bytes')
    version, ready, complete, completed, start, end = struct.unpack_from('<6I', data)
    require((version, ready, complete, completed) == (1, 3, 1, 200),
            'QTR record is incomplete, not ready or unsupported')
    rows = list(struct.iter_unpack('<18I', data[24:]))
    for index, row in enumerate(rows):
        validate_sample(row, index // 100)
    total = (end - start) & 0xffffffff
    require(total < 0x80000000 and total >= sum(row[2] + row[8] for row in rows),
            'QTR record duration is ambiguous or cannot cover acquisitions')
    require(all(row[1] == 2 and row[11] == 0 and row[12] == 15 for row in rows[100:]),
            'QTR diagnostic pull-up stimulus failed; raw observations retained')
    return dict(version=version, samples=completed, total_elapsed_us=total,
                neutral=dataset(rows[:100]), diagnostic_pullup=dataset(rows[100:]))


def load_helper():
    path = Path(__file__).absolute().with_name('p0_capture.py')
    require(all(not item.is_symlink() for item in (path, *path.parents)),
            'capture helper path contains a symlink')
    require(path.is_file() and path.stat().st_size <= 131072, 'capture helper unavailable')
    require(hashlib.sha256(path.read_bytes()).hexdigest() == HELPER_HASH,
            'capture helper differs from reviewed version')
    spec = importlib.util.spec_from_file_location('p0_capture_reviewed', path)
    require(spec is not None and spec.loader is not None, 'cannot load capture helper')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module, path


def check_identities(helper, capture, argument, helper_path):
    directory = Path(argument)
    require(ARTIFACT_SIZE > 0 and directory == ARTIFACT_DIR,
            'only the pinned QTR/default artifact is accepted')
    helper.no_symlinks(directory)
    elf = directory / 'p0_qtr.ino.elf'
    binary = directory / 'p0_qtr.ino.elf-zsk.bin'
    files = dict(helper.EXPECTED_HASHES)
    files.update({helper_path: HELPER_HASH, elf: ELF_HASH, binary: BINARY_HASH})
    for path, expected in files.items():
        actual = helper.file_hash(path)
        capture.report['file_hashes'][str(path)] = actual
        require(actual == expected, f'file identity mismatch: {path}')
    require(helper.LOADER.stat().st_size == helper.LOADER_SIZE, 'loader size mismatch')
    require(elf.stat().st_size == ARTIFACT_SIZE and binary.stat().st_size == ARTIFACT_SIZE,
            'QTR artifact size mismatch')
    helper.no_symlinks(helper.READELF)
    capture.run([helper.OPENOCD, '--version'])
    version = capture.report['commands'][-1]
    capture.report['versions'] = dict(
        python=sys.version, core='arduino:zephyr@1.0.0',
        openocd=version['stdout'] + version['stderr'],
        readelf=capture.run([helper.READELF, '--version']))
    capture.binary_size = ARTIFACT_SIZE
    return elf, binary


def check_layout(helper, capture, elf):
    headers = capture.run([helper.READELF, '-hSW', elf])
    require(re.search(r'Type:\s+REL\b', headers) and
            re.search(r'Class:\s+ELF32\b', headers) and 'little endian' in headers and
            re.search(r'Machine:\s+ARM\b', headers), 'unexpected QTR ELF format')
    rows = re.findall(r'^\s*\[\s*(\d+)\]\s+(\S+)\s+(\S+)\s+'
                      r'([0-9a-fA-F]+)\s+([0-9a-fA-F]+)\s+([0-9a-fA-F]+)',
                      headers, re.MULTILINE)
    bss = [row for row in rows if row[1] == '.bss']
    require(len(bss) == 1 and bss[0][2] == 'NOBITS' and
            int(bss[0][3], 16) == BSS_ELF_ADDRESS and int(bss[0][5], 16) == BSS_SIZE, 'QTR BSS layout changed')
    output = capture.run([helper.READELF, '-sW', elf])
    symbols = [line.split() for line in output.splitlines()
               if line.split() and line.split()[-1] == 'p0Qtr']
    require(len(symbols) == 1 and len(symbols[0]) == 8, 'QTR symbol is not unique')
    _, value, size, kind, binding, visibility, section, _ = symbols[0]
    require(int(value, 16) == RECORD_OFFSET and int(size) == RECORD_SIZE and
            kind == 'OBJECT' and binding == 'GLOBAL' and visibility == 'DEFAULT' and
            section == bss[0][0], 'QTR symbol layout changed')
    require(RECORD_OFFSET % 4 == 0 and RECORD_OFFSET + RECORD_SIZE <= BSS_SIZE,
            'QTR record is outside BSS')
    capture.report['layout'] = dict(bss_size=BSS_SIZE, bss_elf_address=BSS_ELF_ADDRESS, symbol='p0Qtr',
                                   offset=RECORD_OFFSET, size=RECORD_SIZE)


def read_values(helper, capture, base):
    address = base + RECORD_OFFSET
    helper.ram_range(address, RECORD_SIZE)
    original = dict(capture.report['extension'])
    first = capture.read('qtr-first', address, RECORD_SIZE)
    second = capture.read('qtr-second', address, RECORD_SIZE)
    require(first == second, 'QTR record changed during capture')
    # Revalidate list and sketch metadata after observation, within the read bound.
    require(helper.find_bss(capture, BSS_SIZE) == base and
            capture.report['extension'] == original, 'QTR extension identity changed')
    capture.report['metrics'] = analyze_record(first)
    capture.report['record_address'] = address
    capture.report['extension_confirmed_after_samples'] = True


def main(argv=None):
    report = dict(status='FAILED', diagnostic='p0_qtr/default',
                  started_at_utc=datetime.now(timezone.utc).isoformat(),
                  commands=[], reads=[], file_hashes={}, flash_identity_verified=False,
                  limitations=['Setup-only empirical API timing, not a whole-robot WCET bound.',
                               'Pull-ups are diagnostic stimulation, not sensor discharge or continuous HIGH proof.',
                               'Completion checked after attachment; debug overlap not excluded.',
                               'No native-error recovery, physical cleanup, sensor freshness or pin-map qualification.'])
    folder, started = None, time.monotonic()
    try:
        parser = argparse.ArgumentParser(description='Read the pinned P0 QTR startup record')
        parser.add_argument('--artifact-dir', required=True)
        parser.add_argument('--output')
        args = parser.parse_args(argv)
        helper, helper_path = load_helper()
        default = helper.CAPTURE_ROOT / (
            datetime.now(timezone.utc).strftime('qtr-%Y%m%dT%H%M%S-%f') + f'-{os.getpid()}')
        folder = helper.fresh_directory(args.output or str(default))
        report['capture_directory'] = str(folder)
        capture = helper.Capture(folder, report)
        elf, binary = check_identities(helper, capture, args.artifact_dir, helper_path)
        check_layout(helper, capture, elf)
        helper.verify_flash(capture, binary)
        base = helper.find_bss(capture, BSS_SIZE)
        read_values(helper, capture, base)
        report['status'] = 'QTR-CAPTURED'
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        report['error'] = str(error)
    report.update(finished_at_utc=datetime.now(timezone.utc).isoformat(),
                  capture_duration_seconds=time.monotonic() - started)
    output = json.dumps(report, indent=2, allow_nan=False)
    if folder is not None:
        try:
            (folder / 'capture.json').write_text(output + '\n', encoding='utf-8')
        except OSError as error:
            report.update(status='FAILED', error=f'cannot save capture record: {error}')
            output = json.dumps(report, indent=2, allow_nan=False)
    print(output)
    return 0 if report['status'] == 'QTR-CAPTURED' else 1


if __name__ == '__main__':
    raise SystemExit(main())
