# Captures the reviewed bare-board Runtime diagnostic and pinned LLEXT heap read-only.
# Verifies deployed identities before private RAM and independently bounds every read.
# Independent D104 tests exercise literal layouts, guard failures and complete receipts.
"""CAPTURED means inspected evidence, never a physical bench or phase-gate pass."""
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

import p0_capture as p0
import recorder_heap

OPENOCD, READELF, CONFIG = p0.OPENOCD, p0.READELF, p0.CONFIG
LOADER, LOADER_ELF, LOADER_SIZE = p0.LOADER, p0.LOADER_ELF, p0.LOADER_SIZE
CAPTURE_ROOT, SRAM, LIST_ADDRESS = p0.CAPTURE_ROOT, p0.SRAM, p0.LIST_ADDRESS
# The coordinator pins one independently reviewed build before any execution.
ARTIFACT_DIR = Path('/home/arduino/sumox26_codex_build/_app_builds/native-app-v1/2bd817c4e535324964a031cdd44720f26fd145a3cd317ab7b3ced089f35db7e5/bench-default/360b0e9f766643f98b29c6f6d68b9656/artifacts')
ELF_PATH = ARTIFACT_DIR / 'runtime_inert.ino.elf'
ELF_HASH = '8be8768aca2990eafa1edabcff37b645c9beec51df7617db7324f228f672daf8'
BINARY_HASH = 'eb1d2b5b7ddeb432ec453da12cf69b4e86f2bb61b2ca63b3e58df4819de5f852'
READELF_HASH = 'c37462dcd380ae1039eb8a0aab379a619415e1100472291ffea2eae34161092e'
EXPECTED_HASHES = {**p0.EXPECTED_HASHES, READELF: READELF_HASH,
    Path(__file__).absolute().with_name('p0_capture.py'): '885c4e4206aea4ac9e03c4e92e48258db2a0ae302ff83a86430e6913afeeb57c',
    Path(__file__).absolute().with_name('recorder_heap.py'): 'd661024975925a7d8a83f4b772199bbf59911adb5adb8ea69a2082b69eed4b92',
}
MAX_READS, MAX_BYTES, MAX_RAM_READ = 48, 2097152, 16384
MAX_COMMANDS, SEQUENCE_SECONDS, COMMAND_SECONDS = 64, 600.0, 30.0
DIAGNOSTIC_BYTES, HEAP_DESCRIPTOR, HEAP_BASE = 232, 0x2000112c, 0x20013890
POOL_BYTES, BLOCK_BYTES = 262144, 16384
FLASH_BLOCK_BYTES = 65536
MAX_EXTENSION_NODES = 3
REPORT_FIELDS = (
    'schema_version', 'byte_size', 'phase', 'failure', 'boot_us',
    'first_s_us', 'first_d_us', 'first_c_us', 'last_s_us', 'last_d_us',
    'last_a_us', 'last_c_us', 'elapsed_us', 'epochs', 'missed_releases',
    'maximum_execution_us', 'maximum_runner_us', 'token_lo', 'token_hi',
    'runtime_phase', 'runtime_fault', 'transaction_phase', 'transaction_fault',
    'robot_state', 'contract_faults', 'escape_fault', 'gate_fault', 'receipt_flags',
    'input_absent_mask', 'initialization_complete', 'recorder_phase', 'frame_count',
    'event_count', 'setup_enable_calls', 'setup_pwm_calls', 'enable_low_calls',
    'pwm_zero_calls', 'settle_calls', 'clock_calls', 'enabled_requests',
    'nonzero_requests', 'invalid_requests',
)
STACK_FIELDS = ('valid', 'region_start', 'region_size', 'region_delta',
                'minimum_sp', 'samples', 'sampled_headroom_bytes', 'fault')
UINT32_MAX, HALF_RANGE = 0xffffffff, 0x80000000


def require(condition, message):
    if not condition:
        raise ValueError(message)


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def valid_stack(stack):
    start, size, delta = (stack[key] for key in ('region_start', 'region_size', 'region_delta'))
    minimum = stack['minimum_sp']
    return (stack['valid'] == 1 and stack['fault'] == 0 and
            0 < stack['samples'] < UINT32_MAX and start % 4 == minimum % 4 == 0 and
            SRAM[0] <= start < SRAM[1] and size > 0 and start + size <= SRAM[1] and
            delta <= size and start <= minimum <= start + size - delta and
            stack['sampled_headroom_bytes'] == minimum - start)


def valid_timing(report):
    delta = lambda name: (report[name] - report['boot_us']) & UINT32_MAX
    first = [delta(name) for name in ('first_s_us', 'first_d_us', 'first_c_us')]
    last = [delta(name) for name in ('last_s_us', 'last_d_us', 'last_a_us', 'last_c_us')]
    execution, runner = report['maximum_execution_us'], report['maximum_runner_us']
    return (all(value < HALF_RANGE for value in first + last) and
            first == sorted(first) and last == sorted(last) and first[2] <= last[0] and
            200000000 <= report['elapsed_us'] < 201000000 and
            200000000 <= last[3] < 201000000 and first[2] < 1000000 and
            report['elapsed_us'] >= last[3] and
            0 < execution < HALF_RANGE and 0 < runner < HALF_RANGE and
            execution >= max(first[2] - first[0], last[3] - last[0]) and runner >= execution)


def acceptance(report, stack):
    epochs = report['epochs']
    checks = (
        ('probe_failed', report['phase'] == 2),
        ('runtime_state', report['runtime_phase'] == 1 and report['transaction_phase'] == 1 and
         report['robot_state'] == 0),
        ('owner_fault', all(report[key] == 0 for key in
         ('runtime_fault', 'transaction_fault', 'contract_faults', 'escape_fault', 'gate_fault')) and
         report['receipt_flags'] == 15),
        ('source_state', report['input_absent_mask'] == 31 and report['initialization_complete'] == 0),
        ('recorder_state', report['recorder_phase'] == report['frame_count'] == report['event_count'] == 0),
        ('nonzero_activity', report['enabled_requests'] == report['nonzero_requests'] == report['invalid_requests'] == 0),
        ('counts', 200000 <= epochs < UINT32_MAX and report['missed_releases'] == 0 and
         report['token_lo'] + (report['token_hi'] << 32) == epochs and
         report['setup_enable_calls'] == 1 and report['setup_pwm_calls'] == 4 and
         report['enable_low_calls'] == report['settle_calls'] == epochs + 1 and
         report['pwm_zero_calls'] == 4 * (epochs + 1) and 0 < report['clock_calls'] < UINT32_MAX),
        ('timing', valid_timing(report)),
        ('stack_invalid', valid_stack(stack)),
    )
    failures = [name for name, passed in checks if not passed]
    return {'passed': not failures, 'failures': failures}


def decode_diagnostics(blob):
    require(type(blob) is bytes and len(blob) == DIAGNOSTIC_BYTES,
            'diagnostics must be exactly232 immutable bytes')
    words = struct.unpack('<58I', blob)
    require(words[0] != 0 and words[0] % 2 == 0 and words[0] == words[57],
            'diagnostic sequence is unfinished or incoherent')
    report, stack = dict(zip(REPORT_FIELDS, words[1:43])), dict(zip(STACK_FIELDS, words[49:57]))
    require(report['schema_version'] == 1 and report['byte_size'] == 192,
            'unsupported diagnostic report schema/size')
    require(not any(words[43:49]), 'nonzero reserved diagnostic words')
    require((report['phase'] == 2 and report['failure'] == 0) or
            (report['phase'] == 3 and 1 <= report['failure'] <= 12), 'phase/failure mismatch')
    domains = {'runtime_phase': 4, 'runtime_fault': 5, 'transaction_phase': 4,
               'transaction_fault': 6, 'robot_state': 11, 'contract_faults': 1023,
               'escape_fault': 4, 'gate_fault': 6, 'receipt_flags': 15,
               'input_absent_mask': 31, 'initialization_complete': 1, 'recorder_phase': 4}
    require(all(report[key] <= maximum for key, maximum in domains.items()), 'unknown report enum or bits')
    require(stack['valid'] <= 1 and stack['fault'] <= 5, 'unknown stack enum')
    return {'sequence': words[0], 'report': report, 'stack': stack,
            'acceptance': acceptance(report, stack)}


def fresh_directory(output):
    p0.no_symlinks(CAPTURE_ROOT, must_exist=False)
    CAPTURE_ROOT.mkdir(mode=0o700, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime('runtime-%Y%m%dT%H%M%S-%f')
    folder = Path(output) if output else CAPTURE_ROOT / f'{stamp}-{os.getpid()}'
    require(folder.parent == CAPTURE_ROOT and
            re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,95}', folder.name),
            'output must be a fresh direct child of the fixed capture root')
    p0.no_symlinks(folder, must_exist=False)
    folder.mkdir(mode=0o700, exist_ok=False)
    return folder


class Capture:
    def __init__(self, folder, report):
        self.folder, self.report = Path(folder), report
        self.read_count = self.read_bytes = self.binary_size = 0
        self.identities_verified = False
        self.deadline = time.monotonic() + SEQUENCE_SECONDS
        self._read_command = None
        self._read_purposes = set()
        self.report.setdefault('commands', [])
        self.report.setdefault('reads', [])

    def _command_allowed(self, argv, attach):
        require(self.identities_verified, 'reviewed local identities have not been verified')
        if attach:
            require(tuple(argv) == self._read_command, 'only the current bounded MEM-AP read is permitted')
            return
        allowed = [(str(OPENOCD), '--version'), (str(READELF), '--version')]
        if ARTIFACT_DIR is not None:
            elf = str(ELF_PATH)
            allowed += [(str(READELF), '-hSW', elf), (str(READELF), '-sW', elf)]
        require(tuple(argv) in allowed, 'command is outside the fixed identity/layout purposes')

    def _finish_command(self, record, out, err):
        record.update(finished_at_utc=utc_now(), finished_monotonic=time.monotonic())
        for key, path in (('stdout', out), ('stderr', err)):
            if path.exists():
                with path.open('rb') as stream:
                    data = stream.read(65537)
                record[key] = data[:65536].decode('utf-8', errors='replace')
                record[key + '_truncated'] = len(data) > 65536

    def run(self, argv, attach=False):
        # Legacy helper naming: attach selects only the pinned MEM-AP command.
        argv = [str(item) for item in argv]
        self._command_allowed(argv, attach)
        require(len(self.report['commands']) < MAX_COMMANDS, '64-command bound exceeded')
        started = time.monotonic()
        timeout = min(COMMAND_SECONDS, self.deadline - started)
        require(timeout > 0, '600-second command-sequence deadline exceeded')
        index = len(self.report['commands'])
        out, err = self.folder / f'cmd-{index:02d}.out', self.folder / f'cmd-{index:02d}.err'
        record = dict(argv=argv, started_at_utc=utc_now(), started_monotonic=started,
                      timeout_seconds=timeout, stdout_file=out.name, stderr_file=err.name)
        self.report['commands'].append(record)
        try:
            with out.open('xb') as stdout, err.open('xb') as stderr:
                result = subprocess.run(argv, stdin=subprocess.DEVNULL, stdout=stdout, stderr=stderr,
                                        timeout=timeout, check=False, env={**os.environ, 'LC_ALL': 'C'})
            record['returncode'] = result.returncode
        except subprocess.TimeoutExpired as error:
            record.update(returncode=None, timeout=True, error=str(error))
        except OSError as error:
            record.update(returncode=None, error=str(error))
        except subprocess.SubprocessError as error:
            record.update(returncode=getattr(error, 'returncode', None), error=str(error))
        finally:
            self._finish_command(record, out, err)
        require(record.get('returncode') == 0, 'capture command failed')
        require(record['finished_monotonic'] < self.deadline, '600-second capture deadline exceeded')
        require(out.stat().st_size <= 2_000_000, 'command text output exceeds bound')
        return out.read_text(encoding='utf-8', errors='replace')

    def _diagnostic_range(self):
        layout = self.report.get('layout', {})
        entry = layout.get('symbols', {}).get('runtimeDiagnostics', {})
        base = self.report.get('extension', {}).get('bss_address')
        require(p0.uint32(base) and entry.get('size') == DIAGNOSTIC_BYTES,
                'verified relocated diagnostic layout is unavailable')
        offset, bss_size = entry.get('offset'), layout.get('bss_size')
        require(p0.uint32(offset) and p0.uint32(bss_size) and offset <= bss_size - DIAGNOSTIC_BYTES,
                'diagnostic symbol escapes verified BSS')
        p0.ram_range(base, bss_size)
        return base + offset

    def _ram_purpose(self, label, address, size):
        require(self.report.get('flash_identity_verified') is True, 'deployed identity required before private RAM')
        p0.ram_range(address, size)
        require(size <= MAX_RAM_READ, 'RAM read exceeds16KiB')
        if label in ('llext-list', 'llext-list-confirm'):
            require((address, size) == (LIST_ADDRESS, 8), 'invalid LLEXT list range')
        elif re.fullmatch(r'node-[1-3]', label):
            require(size == 196, 'invalid LLEXT node extent')
        elif label in ('diagnostics-first', 'diagnostics-last'):
            require((address, size) == (self._diagnostic_range(), DIAGNOSTIC_BYTES), 'invalid diagnostic range')
        elif label in ('heap-descriptor-first', 'heap-descriptor-last'):
            require((address, size) == (HEAP_DESCRIPTOR, 24), 'invalid fixed heap descriptor')
        else:
            match = re.fullmatch(r'pool-[12]-(0[0-9]|1[0-5])', label)
            require(match is not None, 'unknown private RAM read purpose')
            index = int(match.group(1))
            require((address, size) == (HEAP_BASE + index * BLOCK_BYTES, BLOCK_BYTES),
                    'pool read must be one indexed16KiB block of the pinned allocation')

    def _read_purpose(self, label, address, size, region):
        require(self.identities_verified, 'local reviewed identities required before memory reads')
        require(type(label) is str and re.fullmatch(r'[a-z0-9-]+', label), 'invalid memory read label')
        require(p0.uint32(address) and type(size) is int and size > 0, 'invalid memory extent')
        if region == 'ram':
            self._ram_purpose(label, address, size)
        elif region == 'loader':
            self._flash_purpose(label, address, size, region, 0x08000000, LOADER_SIZE)
        elif region == 'sketch':
            require(16 < self.binary_size <= 0x100000, 'invalid sketch identity extent')
            self._flash_purpose(label, address, size, region, 0x08100000, self.binary_size)
        else:
            raise ValueError('unknown memory region')

    def _flash_purpose(self, label, address, size, region, base, total):
        match = re.fullmatch(re.escape(region) + r'-(\d{2})', label)
        require(match is not None, 'invalid indexed flash identity purpose')
        offset = int(match.group(1)) * FLASH_BLOCK_BYTES
        require(offset < total and address == base + offset and
                size == min(FLASH_BLOCK_BYTES, total - offset),
                'flash identity chunk differs from its fixed indexed range')

    def read(self, label, address, size, region='ram'):
        self._read_purpose(label, address, size, region)
        require(self.read_count < MAX_READS, '48-read bound exceeded')
        require(size <= MAX_BYTES - self.read_bytes, '2MiB cumulative read bound exceeded')
        require(label not in self._read_purposes, 'one read attempt per fixed capture purpose')
        target = self.folder / f'{self.read_count:02d}-{label}.bin'
        require(not target.exists() and not target.is_symlink(), 'memory output already exists')
        self.read_count += 1
        self.read_bytes += size
        self._read_purposes.add(label)
        record = dict(address=address, address_hex=f'0x{address:08x}', size=size, region=region,
                      purpose=label, file=target.name, requested_at_utc=utc_now(),
                      requested_monotonic=time.monotonic())
        self.report['reads'].append(record)
        command = f'dump_image {{{target}}} 0x{address:08x} {size}'
        argv = [str(OPENOCD), '-f', str(CONFIG), '-c', command, '-c', 'shutdown']
        self._read_command = tuple(argv)
        try:
            self.run(argv, attach=True)
            p0.no_symlinks(target)
            require(target.is_file() and target.stat().st_size == size, 'short or oversized memory read')
            data = target.read_bytes()
            record['sha256'] = hashlib.sha256(data).hexdigest()
            return data
        except (OSError, ValueError, subprocess.SubprocessError) as error:
            record['error'] = str(error)
            raise
        finally:
            self._read_command = None
            record.update(completed_at_utc=utc_now(), completed_monotonic=time.monotonic())
            self.report.update(memory_read_attempts=self.read_count, memory_bytes_requested=self.read_bytes)


def check_identities(capture, argument):
    require(ARTIFACT_DIR is not None and type(ELF_HASH) is str and type(BINARY_HASH) is str and
            re.fullmatch(r'[0-9a-f]{64}', ELF_HASH) and re.fullmatch(r'[0-9a-f]{64}', BINARY_HASH),
            'reviewed artifact/ELF/ZSK pins are unset')
    directory = Path(argument)
    require(directory == ARTIFACT_DIR, 'only the pinned runtime_inert artifact is accepted')
    p0.no_symlinks(directory)
    elf, binary = ELF_PATH, directory / 'runtime_inert.ino.elf-zsk.bin'
    files = {**EXPECTED_HASHES, elf: ELF_HASH, binary: BINARY_HASH}
    capture.report.setdefault('file_hashes', {})
    for path, expected in files.items():
        actual = p0.file_hash(path)
        capture.report['file_hashes'][str(path)] = actual
        require(actual == expected, f'file identity mismatch: {path}')
    require(LOADER.stat().st_size == LOADER_SIZE, 'loader size mismatch')
    require(16 < binary.stat().st_size <= 0x100000, 'sketch image outside fixed flash bounds')
    capture.binary_size = binary.stat().st_size
    flash_reads = ((LOADER_SIZE + FLASH_BLOCK_BYTES - 1) // FLASH_BLOCK_BYTES +
                   (capture.binary_size + FLASH_BLOCK_BYTES - 1) // FLASH_BLOCK_BYTES)
    # Two list/diagnostic/descriptor reads, two sixteen-block pools and bounded nodes.
    maximum_reads = flash_reads + 38 + MAX_EXTENSION_NODES
    maximum_bytes = LOADER_SIZE + capture.binary_size + 16 + 2 * DIAGNOSTIC_BYTES + 48 + 2 * POOL_BYTES + 196 * MAX_EXTENSION_NODES
    require(maximum_reads <= MAX_READS and maximum_bytes <= MAX_BYTES,
            'complete capture exceeds fixed read budget')
    capture.report['maximum_read_budget'] = {'reads': maximum_reads, 'bytes': maximum_bytes,
                                             'extension_nodes': MAX_EXTENSION_NODES}
    capture.identities_verified = True
    capture.report['local_identities_verified'] = True
    capture.run([OPENOCD, '--version'])
    openocd = capture.report['commands'][-1]
    capture.report['versions'] = {'python': sys.version, 'core': 'arduino:zephyr@1.0.0',
        'openocd': openocd.get('stdout', '') + openocd.get('stderr', ''),
        'readelf': capture.run([READELF, '--version'])}
    return elf, binary


def read_layout(capture, elf):
    headers = capture.run([READELF, '-hSW', elf])
    require(re.search(r'Type:\s+REL\b', headers) and re.search(r'Class:\s+ELF32\b', headers) and
            'little endian' in headers and re.search(r'Machine:\s+ARM\b', headers), 'unexpected final ELF format')
    rows = re.findall(r'^\s*\[\s*(\d+)\]\s+(\S+)\s+(\S+)\s+'
                      r'([0-9a-fA-F]+)\s+([0-9a-fA-F]+)\s+([0-9a-fA-F]+)', headers, re.MULTILINE)
    bss = [row for row in rows if row[1] == '.bss']
    require(len(bss) == 1 and bss[0][2] == 'NOBITS', 'missing or duplicate BSS')
    section, size = int(bss[0][0]), int(bss[0][5], 16)
    require(DIAGNOSTIC_BYTES <= size <= SRAM[1] - SRAM[0] and size % 4 == 0,
            'BSS outside bounded SRAM extent')
    found = {}
    for line in capture.run([READELF, '-sW', elf]).splitlines():
        fields = line.split()
        if len(fields) != 8 or fields[7] != 'runtimeDiagnostics':
            continue
        _, value, length, kind, binding, visibility, index, name = fields
        require(not found and kind == 'OBJECT' and binding == 'GLOBAL' and visibility == 'DEFAULT' and
                index == str(section), 'invalid or duplicate recorder diagnostic symbol')
        offset, length = int(value, 16), int(length)
        require(length == DIAGNOSTIC_BYTES and offset % 4 == 0 and 0 <= offset <= size - length,
                'diagnostic symbol range outside BSS')
        found[name] = {'offset': offset, 'size': length}
    require(set(found) == {'runtimeDiagnostics'}, 'missing recorder diagnostic symbol')
    capture.report['layout'] = {'bss_section': section, 'bss_size': size, 'symbols': found}
    return size, found


def verify_flash(capture, binary):
    capture.report['flash_identity_verified'] = False
    require(capture.identities_verified, 'reviewed local identities required before flash comparison')
    expected, packaged = p0.loader_image(LOADER_ELF.read_bytes()), LOADER.read_bytes()
    sketch = binary.read_bytes()
    require(len(expected) == LOADER_SIZE and len(sketch) == capture.binary_size,
            'verified flash reference size changed')
    differences = [i for i, pair in enumerate(zip(expected, packaged)) if pair[0] != pair[1]]
    capture.report['loader_identity'] = dict(
        reference='pinned ELF nonempty PT_LOAD physical bytes', size=len(expected),
        expected_sha256=hashlib.sha256(expected).hexdigest(),
        package_binary_sha256=hashlib.sha256(packaged).hexdigest(),
        package_binary_matches=packaged == expected, package_binary_different_bytes=len(differences),
        package_binary_first_differences=[dict(offset=i, elf=expected[i], binary=packaged[i])
                                          for i in differences[:16]])
    loader = read_flash_chunks(capture, 'loader', 0x08000000, LOADER_SIZE)
    require(loader == expected, 'deployed loader differs from pinned ELF load image')
    loaded_sketch = read_flash_chunks(capture, 'sketch', 0x08100000, capture.binary_size)
    require(loaded_sketch == sketch, 'deployed sketch differs from pinned artifact')
    capture.report['flash_identity_verified'] = True


def read_flash_chunks(capture, region, base, size):
    # Exact indexed chunks all count against the unchanged48-read limit.
    blocks = []
    for index, offset in enumerate(range(0, size, FLASH_BLOCK_BYTES)):
        count = min(FLASH_BLOCK_BYTES, size - offset)
        block = capture.read(f'{region}-{index:02d}', base + offset, count, region)
        require(type(block) is bytes and len(block) == count, 'incomplete flash identity chunk')
        blocks.append(block)
    return b''.join(blocks)


def find_bss(capture, expected_size):
    require(capture.report.get('flash_identity_verified') is True, 'deployed identities required before LLEXT traversal')
    listing = capture.read('llext-list', LIST_ADDRESS, 8)
    current, tail = struct.unpack('<II', listing)
    visited, matches = [], []
    while current:
        require(len(visited) < MAX_EXTENSION_NODES and current not in visited, 'LLEXT traversal bound or cycle')
        p0.ram_range(current, 196)
        visited.append(current)
        node = capture.read(f'node-{len(visited)}', current, 196)
        name = node[4:20]
        require(b'\0' in name, 'unterminated extension name')
        if name.split(b'\0', 1)[0] == b'sketch':
            base, size = struct.unpack_from('<I', node, 32)[0], struct.unpack_from('<I', node, 92)[0]
            p0.ram_range(base, size)
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



def read_pool(capture, number):
    blocks = [capture.read(f'pool-{number}-{index:02d}', HEAP_BASE + index * BLOCK_BYTES, BLOCK_BYTES)
              for index in range(16)]
    require(all(type(block) is bytes and len(block) == BLOCK_BYTES for block in blocks), 'incomplete pool block')
    blob = b''.join(blocks)
    filename = 'pool-first.bin' if number == 1 else 'pool-second.bin'
    with (capture.folder / filename).open('xb') as stream:
        stream.write(blob)
    return blob


def capture_values(capture, base, symbols):
    require(set(symbols) == {'runtimeDiagnostics'}, 'unexpected diagnostic symbols')
    symbol = symbols['runtimeDiagnostics']
    require(type(symbol) is dict and set(symbol) == {'offset', 'size'} and
            p0.uint32(symbol['offset']) and symbol['size'] == DIAGNOSTIC_BYTES,
            'invalid diagnostic symbol metadata')
    require(p0.uint32(base), 'invalid relocated BSS base')
    address = base + symbol['offset']
    p0.ram_range(address, DIAGNOSTIC_BYTES)
    first = capture.read('diagnostics-first', address, DIAGNOSTIC_BYTES)
    capture.report['diagnostics'] = decode_diagnostics(first)
    capture.report['symbol_addresses'] = {'runtimeDiagnostics': address}
    descriptor = capture.read('heap-descriptor-first', HEAP_DESCRIPTOR, 24)
    require(type(descriptor) is bytes and len(descriptor) == 24, 'invalid heap descriptor size')
    words = struct.unpack('<6I', descriptor)
    require(words[:3] == (HEAP_BASE, HEAP_BASE, POOL_BYTES), 'pinned LLEXT allocator descriptor differs')
    capture.report['heap_descriptor'] = {'address': HEAP_DESCRIPTOR, 'words': list(words)}
    first_pool, second_pool = read_pool(capture, 1), read_pool(capture, 2)
    capture.report['heap'] = recorder_heap.compare_pools(first_pool, second_pool, base_address=HEAP_BASE)
    require(capture.read('heap-descriptor-last', HEAP_DESCRIPTOR, 24) == descriptor,
            'heap descriptor changed across pool snapshots')
    require(capture.read('diagnostics-last', address, DIAGNOSTIC_BYTES) == first,
            'terminal diagnostic changed across pool snapshots')
    capture.report['diagnostic_sha256'] = hashlib.sha256(first).hexdigest()


def initial_report():
    return {'status': 'FAILED', 'started_at_utc': utc_now(), 'commands': [], 'reads': [],
            'file_hashes': {}, 'local_identities_verified': False, 'flash_identity_verified': False,
            'limitations': ['Bare-board absent-source Runtime evidence only; no sensor or motor qualification.',
                'Two matching metadata snapshots are sampled consistency, not atomic or historical minimum.',
                'Sampled stack headroom is not a historical watermark; MCU clock/WCET remain separate.',
                'CAPTURED is collection; diagnostics.acceptance is separate and no human gate is implied.']}


def main(argv=None):
    parser = argparse.ArgumentParser(description='Read the pinned bare Runtime and LLEXT heap evidence')
    parser.add_argument('--artifact-dir', required=True)
    parser.add_argument('--output')
    args = parser.parse_args(argv)
    report, folder, started = initial_report(), None, time.monotonic()
    try:
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
    report.update(finished_at_utc=utc_now(), capture_duration_seconds=time.monotonic() - started)
    output = json.dumps(report, indent=2, allow_nan=False)
    if folder is not None:
        try:
            with (folder / 'capture.json').open('x', encoding='utf-8') as stream:
                stream.write(output + '\n')
        except OSError as error:
            report.update(status='FAILED', error=f'cannot save capture report: {error}')
            output = json.dumps(report, indent=2, allow_nan=False)
    print(output)
    return 0 if report['status'] == 'CAPTURED' else 1


if __name__ == '__main__':
    raise SystemExit(main())
