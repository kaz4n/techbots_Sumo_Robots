# Reads the exact reviewed startup-only GPIO diagnostic through passive MEM-AP.
# Retains raw readbacks and empirical timings without production WCET claims.
# D-064 decoder tests are independent; exact source/binary review precedes capture.
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
                    '1dfbd5711114e699fec324bcc0b97de7defd37889b5dc81c824dcde69be93dda/'
                    'p0_gpio/artifacts/bench-default')
ELF_HASH = '46c135bd8d2385e860dcc86ddf577407da9f205721a4a576e14c984836ac934f'
BINARY_HASH = 'a0a36e77e467d4a0f02bf59637f40dda3fa60334acd18e7c3c2c7efd2b093828'
ARTIFACT_SIZE = 76148
BSS_SIZE = 21980
BSS_ELF_ADDRESS = 0x5598
RECORD_OFFSET = 4
RECORD_SIZE = 14428


def require(condition, message):
    if not condition:
        raise ValueError(message)


def statistics(values):
    ordered = sorted(values)
    return dict(min_us=ordered[0], max_us=ordered[-1],
                p99_us=ordered[(len(ordered) * 99 + 99) // 100 - 1])


INTERVAL_FIELDS = ('overhead_us', 'pin_mode_us', 'write_high_us',
                   'read_low_us', 'read_high_us', 'pair_us')
SAMPLE_FIELDS = (*INTERVAL_FIELDS, 'low_level', 'high_level', 'pair_level')


def analyze_record(data):
    require(isinstance(data, (bytes, bytearray)) and len(data) == RECORD_SIZE,
            'GPIO record must contain exactly14428 bytes')
    version, ready, complete, completed, start, end, final_level = struct.unpack_from('<6Ii', data)
    require((version, ready, complete, completed, final_level) == (1, 1, 1, 400, 1),
            'GPIO record is incomplete, not ready, unsupported or not finally HIGH')
    samples = list(struct.iter_unpack('<6I3i', data[28:]))
    require(all(all(value < 0x80000000 for value in row[:6]) for row in samples),
            'ambiguous GPIO interval')
    require(all(row[6:] == (0, 1, 1) for row in samples),
            'GPIO readbacks did not match LOW/HIGH/HIGH')
    total = (end - start) & 0xffffffff
    require(total < 0x80000000 and total >= sum(sum(row[:6]) for row in samples),
            'GPIO total interval is ambiguous or cannot cover the measured calls')
    subsequent = {name: statistics([row[index] for row in samples[1:]])
                  for index, name in enumerate(INTERVAL_FIELDS)}
    return dict(version=version, samples=completed, total_elapsed_us=total,
                first_call=dict(zip(SAMPLE_FIELDS, samples[0])),
                subsequent_calls=dict(samples=399, **subsequent),
                overhead=statistics([row[0] for row in samples]),
                readbacks=dict(low_matches=400, high_matches=400,
                               pair_matches=400, final_high=True))


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
            'only the pinned GPIO/default artifact is accepted')
    helper.no_symlinks(directory)
    elf = directory / 'p0_gpio.ino.elf'
    binary = directory / 'p0_gpio.ino.elf-zsk.bin'
    files = dict(helper.EXPECTED_HASHES)
    files.update({helper_path: HELPER_HASH, elf: ELF_HASH, binary: BINARY_HASH})
    for path, expected in files.items():
        actual = helper.file_hash(path)
        capture.report['file_hashes'][str(path)] = actual
        require(actual == expected, f'file identity mismatch: {path}')
    require(helper.LOADER.stat().st_size == helper.LOADER_SIZE, 'loader size mismatch')
    require(elf.stat().st_size == ARTIFACT_SIZE and binary.stat().st_size == ARTIFACT_SIZE,
            'GPIO artifact size mismatch')
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
            re.search(r'Machine:\s+ARM\b', headers), 'unexpected GPIO ELF format')
    rows = re.findall(r'^\s*\[\s*(\d+)\]\s+(\S+)\s+(\S+)\s+'
                      r'([0-9a-fA-F]+)\s+([0-9a-fA-F]+)\s+([0-9a-fA-F]+)',
                      headers, re.MULTILINE)
    bss = [row for row in rows if row[1] == '.bss']
    require(len(bss) == 1 and bss[0][2] == 'NOBITS' and
            int(bss[0][3], 16) == BSS_ELF_ADDRESS and int(bss[0][5], 16) == BSS_SIZE, 'GPIO BSS layout changed')
    output = capture.run([helper.READELF, '-sW', elf])
    symbols = [line.split() for line in output.splitlines()
               if line.split() and line.split()[-1] == 'p0Gpio']
    require(len(symbols) == 1 and len(symbols[0]) == 8, 'GPIO symbol is not unique')
    _, value, size, kind, binding, visibility, section, _ = symbols[0]
    require(int(value, 16) == RECORD_OFFSET and int(size) == RECORD_SIZE and
            kind == 'OBJECT' and binding == 'GLOBAL' and visibility == 'DEFAULT' and
            section == bss[0][0], 'GPIO symbol layout changed')
    require(RECORD_OFFSET % 4 == 0 and RECORD_OFFSET + RECORD_SIZE <= BSS_SIZE,
            'GPIO record is outside BSS')
    capture.report['layout'] = dict(bss_size=BSS_SIZE, bss_elf_address=BSS_ELF_ADDRESS, symbol='p0Gpio',
                                   offset=RECORD_OFFSET, size=RECORD_SIZE)


def read_values(helper, capture, base):
    address = base + RECORD_OFFSET
    helper.ram_range(address, RECORD_SIZE)
    original = dict(capture.report['extension'])
    first = capture.read('gpio-first', address, RECORD_SIZE)
    second = capture.read('gpio-second', address, RECORD_SIZE)
    require(first == second, 'GPIO record changed during capture')
    # Revalidate list and sketch metadata after observation, within the read bound.
    require(helper.find_bss(capture, BSS_SIZE) == base and
            capture.report['extension'] == original, 'GPIO extension identity changed')
    capture.report['metrics'] = analyze_record(first)
    capture.report['record_address'] = address
    capture.report['extension_confirmed_after_samples'] = True


def main(argv=None):
    report = dict(status='FAILED', diagnostic='p0_gpio/default',
                  started_at_utc=datetime.now(timezone.utc).isoformat(),
                  commands=[], reads=[], file_hashes={}, flash_identity_verified=False,
                  limitations=['Setup-only empirical API timing, not a whole-robot WCET bound.',
                               'Digital readbacks do not recover discarded native errors or prove optical output.',
                               'Completion checked after attachment; debug overlap not excluded.',
                               'No external-header timing, electrical qualification or phase-gate proof.'])
    folder, started = None, time.monotonic()
    try:
        parser = argparse.ArgumentParser(description='Read the pinned P0 GPIO startup record')
        parser.add_argument('--artifact-dir', required=True)
        parser.add_argument('--output')
        args = parser.parse_args(argv)
        helper, helper_path = load_helper()
        default = helper.CAPTURE_ROOT / (
            datetime.now(timezone.utc).strftime('gpio-%Y%m%dT%H%M%S-%f') + f'-{os.getpid()}')
        folder = helper.fresh_directory(args.output or str(default))
        report['capture_directory'] = str(folder)
        capture = helper.Capture(folder, report)
        elf, binary = check_identities(helper, capture, args.artifact_dir, helper_path)
        check_layout(helper, capture, elf)
        helper.verify_flash(capture, binary)
        base = helper.find_bss(capture, BSS_SIZE)
        read_values(helper, capture, base)
        report['status'] = 'GPIO-CAPTURED'
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
    return 0 if report['status'] == 'GPIO-CAPTURED' else 1


if __name__ == '__main__':
    raise SystemExit(main())
