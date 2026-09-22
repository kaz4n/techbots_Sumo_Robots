# Reads the exact reviewed startup-only ADC diagnostic through passive MEM-AP.
# Retains raw signed results and empirical timings without production WCET claims.
# D-063 decoder tests are independent; exact source/binary review precedes capture.
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
                    'f5f637b2f0799a3b08d9c4c1897c6706842e0a5ffd737e355d409ed881989c1c/'
                    'p0_adc/artifacts/bench-default')
ELF_HASH = 'a8e02489b14145f06312db3578e3349033e8b07e732beb5baeebcb8ea3a66683'
BINARY_HASH = '2cff4f0635d45c2d75c75c6b0f96444d7e28fec088973835b7b4038061d84fba'
ARTIFACT_SIZE = 74636
BSS_SIZE = 19572
RECORD_OFFSET = 4
RECORD_SIZE = 12020


def require(condition, message):
    if not condition:
        raise ValueError(message)


def statistics(values):
    ordered = sorted(values)
    return dict(min_us=ordered[0], max_us=ordered[-1],
                p99_us=ordered[(len(ordered) * 99 + 99) // 100 - 1])


def analyze_record(data):
    require(isinstance(data, (bytes, bytearray)) and len(data) == RECORD_SIZE,
            'ADC record must contain exactly12020 bytes')
    version, complete, completed, start, end = struct.unpack_from('<5I', data)
    require((version, complete, completed) == (1, 1, 1000),
            'ADC record is incomplete or has an unsupported version/count')
    samples = list(struct.iter_unpack('<IIi', data[20:]))
    require(all(overhead < 0x80000000 and elapsed < 0x80000000
                for overhead, elapsed, _ in samples), 'ambiguous ADC interval')
    require(all(0 <= value <= 1023 for _, _, value in samples),
            'ADC returned an error or a value outside its installed10-bit range')
    total = (end - start) & 0xffffffff
    require(total < 0x80000000 and
            total >= sum(overhead + elapsed for overhead, elapsed, _ in samples),
            'ADC total interval is ambiguous or cannot cover the measured calls')
    values = [sample[2] for sample in samples]
    return dict(version=version, samples=completed, total_elapsed_us=total,
                first_call=dict(overhead_us=samples[0][0], elapsed_us=samples[0][1],
                                value=samples[0][2]),
                subsequent_calls=dict(samples=999,
                                      **statistics([row[1] for row in samples[1:]])),
                overhead=statistics([row[0] for row in samples]),
                zero_results=values.count(0), nonzero_results=1000-values.count(0),
                value_min=min(values), value_max=max(values))


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
            'only the pinned ADC/default artifact is accepted')
    helper.no_symlinks(directory)
    elf = directory / 'p0_adc.ino.elf'
    binary = directory / 'p0_adc.ino.elf-zsk.bin'
    files = dict(helper.EXPECTED_HASHES)
    files.update({helper_path: HELPER_HASH, elf: ELF_HASH, binary: BINARY_HASH})
    for path, expected in files.items():
        actual = helper.file_hash(path)
        capture.report['file_hashes'][str(path)] = actual
        require(actual == expected, f'file identity mismatch: {path}')
    require(helper.LOADER.stat().st_size == helper.LOADER_SIZE, 'loader size mismatch')
    require(elf.stat().st_size == ARTIFACT_SIZE and binary.stat().st_size == ARTIFACT_SIZE,
            'ADC artifact size mismatch')
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
            re.search(r'Machine:\s+ARM\b', headers), 'unexpected ADC ELF format')
    rows = re.findall(r'^\s*\[\s*(\d+)\]\s+(\S+)\s+(\S+)\s+'
                      r'([0-9a-fA-F]+)\s+([0-9a-fA-F]+)\s+([0-9a-fA-F]+)',
                      headers, re.MULTILINE)
    bss = [row for row in rows if row[1] == '.bss']
    require(len(bss) == 1 and bss[0][2] == 'NOBITS' and
            int(bss[0][5], 16) == BSS_SIZE, 'ADC BSS layout changed')
    output = capture.run([helper.READELF, '-sW', elf])
    symbols = [line.split() for line in output.splitlines()
               if line.split() and line.split()[-1] == 'p0Adc']
    require(len(symbols) == 1 and len(symbols[0]) == 8, 'ADC symbol is not unique')
    _, value, size, kind, binding, visibility, section, _ = symbols[0]
    require(int(value, 16) == RECORD_OFFSET and int(size) == RECORD_SIZE and
            kind == 'OBJECT' and binding == 'GLOBAL' and visibility == 'DEFAULT' and
            section == bss[0][0], 'ADC symbol layout changed')
    require(RECORD_OFFSET % 4 == 0 and RECORD_OFFSET + RECORD_SIZE <= BSS_SIZE,
            'ADC record is outside BSS')
    capture.report['layout'] = dict(bss_size=BSS_SIZE, symbol='p0Adc',
                                   offset=RECORD_OFFSET, size=RECORD_SIZE)


def read_values(helper, capture, base):
    address = base + RECORD_OFFSET
    helper.ram_range(address, RECORD_SIZE)
    original = dict(capture.report['extension'])
    first = capture.read('adc-first', address, RECORD_SIZE)
    second = capture.read('adc-second', address, RECORD_SIZE)
    require(first == second, 'ADC record changed during capture')
    # Revalidate list and sketch metadata after observation, within the read bound.
    require(helper.find_bss(capture, BSS_SIZE) == base and
            capture.report['extension'] == original, 'ADC extension identity changed')
    capture.report['metrics'] = analyze_record(first)
    capture.report['record_address'] = address
    capture.report['extension_confirmed_after_samples'] = True


def main(argv=None):
    report = dict(status='FAILED', diagnostic='p0_adc/default',
                  started_at_utc=datetime.now(timezone.utc).isoformat(),
                  commands=[], reads=[], file_hashes={}, flash_identity_verified=False,
                  limitations=['Setup-only empirical API timing; ADC may wait indefinitely.',
                               'Floating input; no voltage accuracy or battery acceptance.',
                               'Completion checked after attachment; debug overlap not excluded.',
                               'No production ADC, complete-loop WCET or phase-gate proof.'])
    folder, started = None, time.monotonic()
    try:
        parser = argparse.ArgumentParser(description='Read the pinned P0 ADC startup record')
        parser.add_argument('--artifact-dir', required=True)
        parser.add_argument('--output')
        args = parser.parse_args(argv)
        helper, helper_path = load_helper()
        default = helper.CAPTURE_ROOT / (
            datetime.now(timezone.utc).strftime('adc-%Y%m%dT%H%M%S-%f') + f'-{os.getpid()}')
        folder = helper.fresh_directory(args.output or str(default))
        report['capture_directory'] = str(folder)
        capture = helper.Capture(folder, report)
        elf, binary = check_identities(helper, capture, args.artifact_dir, helper_path)
        check_layout(helper, capture, elf)
        helper.verify_flash(capture, binary)
        base = helper.find_bss(capture, BSS_SIZE)
        read_values(helper, capture, base)
        report['status'] = 'ADC-CAPTURED'
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
    return 0 if report['status'] == 'ADC-CAPTURED' else 1


if __name__ == '__main__':
    raise SystemExit(main())
