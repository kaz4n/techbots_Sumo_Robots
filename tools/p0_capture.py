# Captures the reviewed UNO Q timing diagnostic through bounded MEM-AP reads.
# Verifies flash identity before decoding frozen RAM; never resets or writes MCU memory.
# Pure histogram checks are host-testable; hardware execution needs a reviewed capture.
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import struct
import subprocess
import sys
import time

CORE = Path('/home/arduino/.arduino15/packages/arduino/hardware/zephyr/1.0.0')
READELF = Path('/home/arduino/.arduino15/packages/zephyr/tools/'
               'arm-zephyr-eabi/1.0.1/bin/arm-zephyr-eabi-readelf')
OPENOCD = Path('/opt/openocd/bin/openocd')
HELPER = Path('/opt/openocd/share/openocd/scripts/target/swj-dp.tcl')
LOADER = CORE / 'firmwares/zephyr-arduino_uno_q_stm32u585xx.bin'
LOADER_ELF = CORE / 'firmwares/zephyr-arduino_uno_q_stm32u585xx.elf'
CONFIG = Path(__file__).absolute().with_name('p0_mem_read.cfg')
ARTIFACT_DIR = Path('/home/arduino/sumox26-build/'
                    '3de6da69f44c2317b82b246b0fe8e324e1001a531b4741c09e511269fb24e7f4/'
                    'p0_timing/artifacts/bench-default')
CAPTURE_ROOT = Path('/home/arduino/sumox26-capture')
EXPECTED_HASHES = {
    OPENOCD: '04778a80c5c619ee4eef7505db91328f1d7e789107c496f2ddcf96d081f5b0ff',
    HELPER: 'aad132008735bbafea3d18a304632c638f0fb99bfc19530c9f577eda2b10410a',
    LOADER: '6b2ffd3a24aa77ca40bac1a8c61460c5cdd3292a2ff38cb377b938a6ac939713',
    LOADER_ELF: '39d4a4fd47241663323f6e04f94dd8f5a9f9ad6582cf1df37f9709b74026adcd',
    CONFIG: '89d16a28a1489c23ec743be55ade39824f9ca5213b02b20ef4785079122e4339',
}
ELF_HASH = 'e5131d0d465dd3bd73425d3e93570f59dd4357fcf3f08fabeb18b3bd18e4a625'
BINARY_HASH = 'c49b80f110fd34b7b5844a33f9c40da28b6b7543fe136b41621640c9b02802b8'
SYMBOL_SIZES = {'p0Samples': 4, 'p0MaxLateUs': 4,
                'p0OverPeriod': 4, 'p0Histogram': 4004}
SRAM = (0x20000000, 0x200c0000)
LIST_ADDRESS = 0x200017bc
LOADER_SIZE = 263680
UINT32_MAX = 0xffffffff


def require(condition, message):
    if not condition:
        raise ValueError(message)


def uint32(value):
    return type(value) is int and 0 <= value <= UINT32_MAX


def analyze_histogram(samples, maximum, over_period, histogram):
    require(all(uint32(x) for x in (samples, maximum, over_period)),
            'counters must be uint32 integers')
    require(isinstance(histogram, (list, tuple)) and len(histogram) == 1001,
            'histogram must contain exactly 1001 bins')
    require(all(uint32(x) for x in histogram), 'bins must be uint32 integers')
    require(samples == 60000 and sum(histogram) == samples,
            'capture must contain exactly 60000 completed samples')
    require(histogram[1000] == over_period, 'overflow and over-period counts differ')
    highest = max(i for i, count in enumerate(histogram) if count)
    require((highest == 1000 and maximum >= 1000) or
            (highest < 1000 and maximum == highest), 'maximum and histogram differ')
    rank, cumulative, p99 = (samples * 99 + 99) // 100, 0, 0
    for p99, count in enumerate(histogram):
        cumulative += count
        if cumulative >= rank:
            break
    return dict(samples=samples, max_lateness_us=maximum, over_period=over_period,
                p99_us=p99, p99_censored=p99 == 1000)


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def no_symlinks(path, must_exist=True):
    require(path.is_absolute() and '..' not in path.parts, 'path must be absolute')
    for item in (path, *path.parents):
        require(not item.is_symlink(), f'symlink rejected: {item}')
    if must_exist:
        require(path.exists() and path.resolve() == path, f'path unavailable: {path}')


def file_hash(path):
    no_symlinks(path)
    require(path.is_file(), f'not a regular file: {path}')
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(65536), b''):
            digest.update(block)
    return digest.hexdigest()


def in_range(address, size, region):
    return (uint32(address) and type(size) is int and 0 < size <= UINT32_MAX and
            region[0] <= address < region[1] and size <= region[1] - address)


def ram_range(address, size):
    require(address % 4 == 0 and in_range(address, size, SRAM),
            f'invalid SRAM range: {address:#x} + {size}')


def fresh_directory(output):
    no_symlinks(CAPTURE_ROOT, must_exist=False)
    CAPTURE_ROOT.mkdir(mode=0o700, exist_ok=True)
    name = datetime.now(timezone.utc).strftime('timing-%Y%m%dT%H%M%S-%f')
    folder = Path(output) if output else CAPTURE_ROOT / f'{name}-{os.getpid()}'
    require(folder.parent == CAPTURE_ROOT and
            re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,95}', folder.name),
            'output must be a fresh direct child of /home/arduino/sumox26-capture')
    no_symlinks(folder, must_exist=False)
    folder.mkdir(mode=0o700, exist_ok=False)
    return folder


class Capture:
    def __init__(self, folder, report):
        self.folder, self.report = folder, report
        self.deadline = None
        self.read_count = 0
        self.binary_size = 0

    def run(self, argv, attach=False):
        require(len(self.report['commands']) < 32, 'command bound exceeded')
        timeout = 30.0
        if attach:
            if self.deadline is None:
                self.deadline = time.monotonic() + 120.0
            timeout = self.deadline - time.monotonic()
            require(timeout > 0, '120-second capture deadline exceeded')
        index = len(self.report['commands'])
        out, err = self.folder / f'cmd-{index:02d}.out', self.folder / f'cmd-{index:02d}.err'
        record = dict(argv=[str(x) for x in argv], started_at_utc=utc_now(),
                      timeout_seconds=timeout, stdout_file=out.name, stderr_file=err.name)
        self.report['commands'].append(record)
        try:
            with out.open('xb') as stdout, err.open('xb') as stderr:
                result = subprocess.run(record['argv'], stdin=subprocess.DEVNULL,
                                        stdout=stdout, stderr=stderr, timeout=timeout,
                                        check=False, env={**os.environ, 'LC_ALL': 'C'})
            record['returncode'] = result.returncode
        except subprocess.TimeoutExpired:
            record['returncode'] = 124
            record['timeout'] = True
        finally:
            record['finished_at_utc'] = utc_now()
            for key, path in (('stdout', out), ('stderr', err)):
                if path.exists():
                    with path.open('rb') as stream:
                        data = stream.read(65537)
                    record[key] = data[:65536].decode('utf-8', errors='replace')
                    record[key + '_truncated'] = len(data) > 65536
        require(record.get('returncode') == 0, f'command failed: {record["argv"][0]}')
        require(out.stat().st_size <= 2_000_000, 'command output exceeds bound')
        return out.read_text(encoding='utf-8', errors='replace')

    def read(self, label, address, size, region='ram'):
        require(self.read_count < 16, 'memory-read bound exceeded')
        if region == 'ram':
            ram_range(address, size)
            require(size <= 16384, 'RAM read exceeds diagnostic bound')
        elif region == 'loader':
            require((address, size) == (0x08000000, LOADER_SIZE), 'invalid loader read')
        else:
            require(region == 'sketch' and address == 0x08100000 and
                    size == self.binary_size and 16 < size <= 0x100000,
                    'invalid sketch read')
        target = self.folder / f'{self.read_count:02d}-{label}.bin'
        require(re.fullmatch(r'[a-z0-9-]+', label) and not target.exists(),
                'invalid or reused read output')
        self.read_count += 1
        read = dict(address=address, address_hex=f'0x{address:08x}', size=size,
                    region=region, file=target.name, requested_at_utc=utc_now())
        self.report['reads'].append(read)
        command = f'dump_image {{{target}}} 0x{address:08x} {size}'
        self.run([OPENOCD, '-f', CONFIG, '-c', command, '-c', 'shutdown'], attach=True)
        no_symlinks(target)
        require(target.is_file() and target.stat().st_size == size, 'short memory read')
        data = target.read_bytes()
        read.update(sha256=hashlib.sha256(data).hexdigest(), completed_at_utc=utc_now())
        return data


def check_identities(capture, argument):
    directory = Path(argument)
    require(directory == ARTIFACT_DIR, 'only the reviewed timing/default artifact is accepted')
    no_symlinks(directory)
    files = dict(EXPECTED_HASHES)
    elf = directory / 'p0_timing.ino.elf'
    binary = directory / 'p0_timing.ino.elf-zsk.bin'
    files.update({elf: ELF_HASH, binary: BINARY_HASH})
    for path, expected in files.items():
        actual = file_hash(path)
        capture.report['file_hashes'][str(path)] = actual
        require(actual == expected, f'file identity mismatch: {path}')
    require(LOADER.stat().st_size == LOADER_SIZE, 'loader size mismatch')
    require(binary.stat().st_size == 74008, 'reviewed sketch size mismatch')
    no_symlinks(READELF)
    capture.run([OPENOCD, '--version'])
    version_result = capture.report['commands'][-1]
    capture.report['versions'] = {
        'python': sys.version, 'core': 'arduino:zephyr@1.0.0',
        'openocd': version_result['stdout'] + version_result['stderr'],
        'readelf': capture.run([READELF, '--version']),
        'audited_router_bridge': '0.4.3',
    }
    capture.binary_size = binary.stat().st_size
    return elf, binary


def read_layout(capture, elf):
    headers = capture.run([READELF, '-hSW', elf])
    require(re.search(r'Type:\s+REL\b', headers) and
            re.search(r'Class:\s+ELF32\b', headers) and
            "little endian" in headers and re.search(r'Machine:\s+ARM\b', headers),
            'unexpected final ELF format')
    rows = re.findall(r'^\s*\[\s*(\d+)\]\s+(\S+)\s+(\S+)\s+'
                      r'([0-9a-fA-F]+)\s+([0-9a-fA-F]+)\s+([0-9a-fA-F]+)',
                      headers, re.MULTILINE)
    bss = [row for row in rows if row[1] == '.bss']
    require(len(bss) == 1 and bss[0][2] == 'NOBITS', 'missing or duplicate BSS')
    section, size = int(bss[0][0]), int(bss[0][5], 16)
    require(size == 0x2d34, 'reviewed BSS layout changed')
    symbols = capture.run([READELF, '-sW', elf])
    found = {}
    for line in symbols.splitlines():
        fields = line.split()
        if len(fields) != 8 or fields[7] not in SYMBOL_SIZES:
            continue
        _, value, length, kind, binding, visibility, index, name = fields
        require(name not in found and kind == 'OBJECT' and binding == 'GLOBAL' and
                visibility == 'DEFAULT' and index == str(section), 'invalid timing symbol')
        offset, length = int(value, 16), int(length)
        require(length == SYMBOL_SIZES[name] and offset % 4 == 0 and
                0 <= offset <= size - length, 'invalid timing symbol range')
        found[name] = dict(offset=offset, size=length)
    require(set(found) == set(SYMBOL_SIZES), 'missing timing symbol')
    ranges = sorted((x['offset'], x['offset'] + x['size']) for x in found.values())
    require(all(a[1] <= b[0] for a, b in zip(ranges, ranges[1:])), 'overlapping symbols')
    capture.report['layout'] = dict(bss_section=section, bss_size=size, symbols=found)
    return size, found


def verify_flash(capture, binary):
    loader_bytes = capture.read('loader', 0x08000000, LOADER_SIZE, 'loader')
    require(loader_bytes == LOADER.read_bytes(), 'deployed loader differs from pinned file')
    sketch_bytes = capture.read('sketch', 0x08100000, capture.binary_size, 'sketch')
    require(sketch_bytes == binary.read_bytes(), 'deployed sketch differs from pinned artifact')
    capture.report['flash_identity_verified'] = True


def find_bss(capture, expected_size):
    listing = capture.read('llext-list', LIST_ADDRESS, 8)
    current, tail = struct.unpack('<II', listing)
    visited, matches = [], []
    while current:
        require(len(visited) < 4 and current not in visited, 'LLEXT traversal bound or cycle')
        ram_range(current, 196)
        visited.append(current)
        node = capture.read(f'node-{len(visited)}', current, 196)
        name = node[4:20]
        require(b'\0' in name, 'unterminated extension name')
        if name.split(b'\0', 1)[0] == b'sketch':
            base, size = struct.unpack_from('<I', node, 32)[0], struct.unpack_from('<I', node, 92)[0]
            ram_range(base, size)
            require(size == expected_size, 'runtime BSS size differs from final ELF')
            matches.append((base, current))
        current = struct.unpack_from('<I', node)[0]
    require(visited and tail == visited[-1] and len(matches) == 1,
            'LLEXT list must contain exactly one sketch and consistent tail')
    require(capture.read('llext-list-confirm', LIST_ADDRESS, 8) == listing,
            'LLEXT list changed during capture')
    base, node = matches[0]
    capture.report['extension'] = dict(node_address=node, bss_address=base,
                                      bss_size=expected_size, visited_nodes=visited)
    return base


def capture_values(capture, base, symbols):
    addresses = {name: base + item['offset'] for name, item in symbols.items()}
    for name, address in addresses.items():
        ram_range(address, SYMBOL_SIZES[name])
    sample = capture.read('samples-first', addresses['p0Samples'], 4)
    require(struct.unpack('<I', sample)[0] == 60000, 'timing run is incomplete')
    # One bounded contiguous range covers histogram, counters and samples.
    start = min(addresses.values())
    end = max(addresses[name] + SYMBOL_SIZES[name] for name in addresses)
    first = capture.read('values-first', start, end - start)
    second = capture.read('values-second', start, end - start)
    require(first == second, 'diagnostic values changed between captures')
    final = capture.read('samples-last', addresses['p0Samples'], 4)
    require(final == sample, 'sample count changed during capture')
    values = {}
    for name, address in addresses.items():
        count = SYMBOL_SIZES[name] // 4
        values[name] = struct.unpack_from('<' + 'I' * count, first, address - start)
    histogram = list(values['p0Histogram'])
    metrics = analyze_histogram(values['p0Samples'][0], values['p0MaxLateUs'][0],
                                values['p0OverPeriod'][0], histogram)
    capture.report.update(symbol_addresses=addresses, histogram=histogram, metrics=metrics)


def main(argv=None):
    report = dict(status='FAILED', started_at_utc=utc_now(), commands=[], reads=[],
                  file_hashes={}, flash_identity_verified=False,
                  limitations=['Bare scheduler only; includes installed loop-hook overhead.',
                               'No loaded control-loop or phase-gate qualification.',
                               'Debug-port activity may perturb an unfinished run.'])
    folder, started = None, time.monotonic()
    try:
        parser = argparse.ArgumentParser(description='Read the pinned P0 timing diagnostic')
        parser.add_argument('--artifact-dir', required=True)
        parser.add_argument('--output')
        args = parser.parse_args(argv)
        folder = fresh_directory(args.output)
        report['capture_directory'] = str(folder)
        capture = Capture(folder, report)
        elf, binary = check_identities(capture, args.artifact_dir)
        size, symbols = read_layout(capture, elf)
        verify_flash(capture, binary)
        base = find_bss(capture, size)
        capture_values(capture, base, symbols)
        report['status'] = 'CAPTURED'
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        report['error'] = str(error)
    report['finished_at_utc'] = utc_now()
    report['capture_duration_seconds'] = time.monotonic() - started
    output = json.dumps(report, indent=2, allow_nan=False)
    if folder is not None:
        try:
            (folder / 'capture.json').write_text(output + '\n', encoding='utf-8')
        except OSError as error:
            report.update(status='FAILED', error=f'cannot save capture record: {error}')
            output = json.dumps(report, indent=2, allow_nan=False)
    print(output)
    return 0 if report['status'] == 'CAPTURED' else 1


if __name__ == '__main__':
    raise SystemExit(main())
