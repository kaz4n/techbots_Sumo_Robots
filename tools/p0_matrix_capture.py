# Observes progress of the reviewed default-startup UNO Q matrix diagnostic.
# Reuses pinned read-only capture mechanics without broadening the timing helper.
# Counter arithmetic is host-testable; advancement is not optical or clock qualification.
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
ARTIFACT_DIR = Path('/home/arduino/sumox26-build/'
                    '72214f8aa1b6d84e21d2dc8a568ea01adb5fe0295f3f3d0f362e8696d2543e8f/'
                    'p0_matrix/artifacts/bench-default')
ELF_HASH = '1fbb189bba0a52f2d23040522560aee66d8c1d0629e80e6476459cf05c43ec5d'
BINARY_HASH = '74dcf3e03f0122c6d0df7158c48d09aabf3a9b1ca6f9d7eebbc063f570d7fe48'
BSS_SIZE = 0x1e24
COUNTER_OFFSET = 0x78


def require(condition, message):
    if not condition:
        raise ValueError(message)


def analyze_counter(first, second):
    require(all(type(value) is int and 0 <= value <= 0xffffffff
                for value in (first, second)), 'counters must be exact uint32 integers')
    advance = (second - first) & 0xffffffff
    require(1 <= advance <= 0x7fffffff, 'counter did not advance within the modular bound')
    return dict(first=first, second=second, advance=advance)


def utc_now():
    return datetime.now(timezone.utc).isoformat()


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
    require(directory == ARTIFACT_DIR, 'only the pinned matrix/default artifact is accepted')
    helper.no_symlinks(directory)
    elf = directory / 'p0_matrix.ino.elf'
    binary = directory / 'p0_matrix.ino.elf-zsk.bin'
    files = dict(helper.EXPECTED_HASHES)
    files.update({helper_path: HELPER_HASH, elf: ELF_HASH, binary: BINARY_HASH})
    for path, expected in files.items():
        actual = helper.file_hash(path)
        capture.report['file_hashes'][str(path)] = actual
        require(actual == expected, f'file identity mismatch: {path}')
    require(helper.LOADER.stat().st_size == helper.LOADER_SIZE, 'loader size mismatch')
    require(elf.stat().st_size == 74444 and binary.stat().st_size == 74444,
            'matrix artifact size mismatch')
    helper.no_symlinks(helper.READELF)
    capture.run([helper.OPENOCD, '--version'])
    version = capture.report['commands'][-1]
    capture.report['versions'] = dict(
        python=sys.version, core='arduino:zephyr@1.0.0',
        openocd=version['stdout'] + version['stderr'],
        readelf=capture.run([helper.READELF, '--version']),
        audited_router_bridge='0.4.3', audited_matrix_library='0.1.3')
    capture.binary_size = binary.stat().st_size
    return elf, binary


def check_layout(helper, capture, elf):
    headers = capture.run([helper.READELF, '-hSW', elf])
    require(re.search(r'Type:\s+REL\b', headers) and
            re.search(r'Class:\s+ELF32\b', headers) and 'little endian' in headers and
            re.search(r'Machine:\s+ARM\b', headers), 'unexpected matrix ELF format')
    rows = re.findall(r'^\s*\[\s*(\d+)\]\s+(\S+)\s+(\S+)\s+'
                      r'([0-9a-fA-F]+)\s+([0-9a-fA-F]+)\s+([0-9a-fA-F]+)',
                      headers, re.MULTILINE)
    bss = [row for row in rows if row[1] == '.bss']
    require(len(bss) == 1 and bss[0][0] == '9' and bss[0][2] == 'NOBITS' and
            int(bss[0][5], 16) == BSS_SIZE, 'matrix BSS layout changed')
    output = capture.run([helper.READELF, '-sW', elf])
    symbols = [line.split() for line in output.splitlines()
               if line.split() and line.split()[-1] == 'p0Seconds']
    require(len(symbols) == 1 and len(symbols[0]) == 8, 'counter symbol is not unique')
    _, value, size, kind, binding, visibility, section, _ = symbols[0]
    require(int(value, 16) == COUNTER_OFFSET and int(size) == 4 and kind == 'OBJECT' and
            binding == 'GLOBAL' and visibility == 'DEFAULT' and section == '9',
            'counter symbol layout changed')
    require(COUNTER_OFFSET % 4 == 0 and COUNTER_OFFSET + 4 <= BSS_SIZE,
            'counter is outside BSS')
    capture.report['layout'] = dict(bss_section=9, bss_size=BSS_SIZE,
                                   symbol='p0Seconds', offset=COUNTER_OFFSET, size=4)


def read_counter(capture, address, label):
    started = time.monotonic()
    started_utc = utc_now()
    data = capture.read(label, address, 4)
    return dict(value=struct.unpack('<I', data)[0], address=address,
                started_at_utc=started_utc, finished_at_utc=utc_now(),
                monotonic_start=started, monotonic_end=time.monotonic())


def observe_counter(helper, capture, base):
    address = base + COUNTER_OFFSET
    helper.ram_range(address, 4)
    require(helper.in_range(address, 4, (base, base + BSS_SIZE)), 'counter outside runtime BSS')
    capture.report['counter_reads'] = []
    first = read_counter(capture, address, 'counter-first')
    capture.report['counter_reads'].append(first)
    require(capture.deadline is not None and capture.deadline - time.monotonic() > 3.0,
            'insufficient capture deadline for the observation interval')
    capture.report['requested_wait_seconds'] = 3.0
    time.sleep(3.0)
    second = read_counter(capture, address, 'counter-second')
    capture.report['counter_reads'].append(second)
    capture.report['counter'] = analyze_counter(first['value'], second['value'])
    capture.report['between_read_bounds_seconds'] = {
        'minimum': second['monotonic_start'] - first['monotonic_end'],
        'maximum': second['monotonic_end'] - first['monotonic_start']}


def initial_dump(helper, capture, address, size, filename_pattern):
    reads = capture.report['reads']
    require(len(reads) <= 16, 'initial read metadata exceeds capture bound')
    matches = [item for item in reads
               if item.get('address') == address and item.get('size') == size and
               item.get('region') == 'ram' and
               re.fullmatch(filename_pattern, item.get('file', ''))]
    require(len(matches) == 1, 'initial identity dump is missing or ambiguous')
    record = matches[0]
    path = capture.folder / record['file']
    helper.no_symlinks(path)
    require(path.is_file() and path.stat().st_size == size, 'initial dump size changed')
    data = path.read_bytes()
    require(hashlib.sha256(data).hexdigest() == record.get('sha256'),
            'initial identity dump no longer matches its read metadata')
    return data


def confirm_extension(helper, capture):
    node_address = capture.report['extension']['node_address']
    initial_list = initial_dump(helper, capture, helper.LIST_ADDRESS, 8,
                                r'\d{2}-llext-list\.bin')
    initial_node = initial_dump(helper, capture, node_address, 196,
                                r'\d{2}-node-[1-4]\.bin')
    final_list = capture.read('llext-list-after-counters', helper.LIST_ADDRESS, 8)
    require(final_list == initial_list, 'LLEXT head or tail changed during counter observation')
    final_node = capture.read('sketch-node-after-counters', node_address, 196)
    initial_fields = initial_node[:20] + initial_node[32:36] + initial_node[92:96]
    final_fields = final_node[:20] + final_node[32:36] + final_node[92:96]
    require(final_fields == initial_fields,
            'selected sketch next, name or BSS metadata changed during counter observation')
    capture.report['extension_confirmed_after_counters'] = True


def main(argv=None):
    report = dict(status='FAILED', diagnostic='p0_matrix/default', started_at_utc=utc_now(),
                  commands=[], reads=[], file_hashes={}, flash_identity_verified=False,
                  limitations=['Counter advancement only; no optical qualification.',
                               'No inference of 1 Hz accuracy or loaded control timing.',
                               'Read activity may perturb the running matrix workload.'])
    folder, started = None, time.monotonic()
    try:
        parser = argparse.ArgumentParser(description='Observe the pinned P0 matrix counter')
        parser.add_argument('--artifact-dir', required=True)
        parser.add_argument('--output')
        args = parser.parse_args(argv)
        helper, helper_path = load_helper()
        default = helper.CAPTURE_ROOT / (
            datetime.now(timezone.utc).strftime('matrix-%Y%m%dT%H%M%S-%f') + f'-{os.getpid()}')
        folder = helper.fresh_directory(args.output or str(default))
        report['capture_directory'] = str(folder)
        capture = helper.Capture(folder, report)
        elf, binary = check_identities(helper, capture, args.artifact_dir, helper_path)
        check_layout(helper, capture, elf)
        helper.verify_flash(capture, binary)
        base = helper.find_bss(capture, BSS_SIZE)
        observe_counter(helper, capture, base)
        confirm_extension(helper, capture)
        report['status'] = 'COUNTER-ADVANCED'
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        report['error'] = str(error)
    report.update(finished_at_utc=utc_now(), capture_duration_seconds=time.monotonic() - started)
    output = json.dumps(report, indent=2, allow_nan=False)
    if folder is not None:
        try:
            (folder / 'capture.json').write_text(output + '\n', encoding='utf-8')
        except OSError as error:
            report.update(status='FAILED', error=f'cannot save capture record: {error}')
            output = json.dumps(report, indent=2, allow_nan=False)
    print(output)
    return 0 if report['status'] == 'COUNTER-ADVANCED' else 1


if __name__ == '__main__':
    raise SystemExit(main())
