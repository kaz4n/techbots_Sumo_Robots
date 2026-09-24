# Collect the exact default app through finite, read-only MEM-AP observations.
# Preserve live samples and allocation evidence without claiming terminal or physical success.
# Tested by independent literal ABI, heap, command-order and failure fixtures.
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

SOURCE_HASH = 'e820c0e16c29cfd289889273f02721a995e5336b14397f64d6093cffd42b8b69'
ELF_HASH = '8379f152554649fd1b96165f29fda1f165c2b5cfc51d8dca430a37e19f693257'
BINARY_HASH = 'c60443cd8d90c26a85591153dfa38d5f9233bd686b413b2ab7daa3e1457f6df5'
DEBUG_ELF_HASH = 'd9746e05b7081e95d07d1244015aa5bcd587741d6ab23c2449e17ff14dc70449'
ARTIFACT_DIR = Path('/home/arduino/sumox26-capture-input/app_default_' + SOURCE_HASH)
ELF_PATH, BINARY_PATH = (ARTIFACT_DIR / name for name in ('app.ino.elf', 'app.ino.elf-zsk.bin'))
OPENOCD, READELF, CONFIG = p0.OPENOCD, p0.READELF, p0.CONFIG
LOADER, LOADER_ELF, CAPTURE_ROOT = p0.LOADER, p0.LOADER_ELF, p0.CAPTURE_ROOT
EXPECTED_HASHES = {
    **p0.EXPECTED_HASHES,
    READELF: 'c37462dcd380ae1039eb8a0aab379a619415e1100472291ffea2eae34161092e',
    Path(p0.__file__): '885c4e4206aea4ac9e03c4e92e48258db2a0ae302ff83a86430e6913afeeb57c',
    Path(recorder_heap.__file__): 'd661024975925a7d8a83f4b772199bbf59911adb5adb8ea69a2082b69eed4b92',
}
LOADER_BYTES, BINARY_BYTES = 263680, 176048
HEAP_BASE, HEAP_BYTES, DESCRIPTOR_ADDRESS = 0x20013890, 262144, 0x2000112c
LIST_ADDRESS, NODE_BYTES, MAX_NODES = 0x200017bc, 196, 3
FLASH_BLOCK_BYTES, RAM_BLOCK_BYTES = 65536, 16384
MAX_READS, MAX_COMMANDS, MAX_BYTES = 64, 80, 2097152
TOTAL_SECONDS, COMMAND_SECONDS = 600, 30
MAXIMUM_READ_PLAN = dict(reads=62, commands=66, requested_bytes=1405088)
PINNED_LAYOUT = dict(bss_section=8, bss_size=167272, bss_alignment=8,
                     runtime_offset=0, runtime_size=166376,
                     runtime_report_offset=164664, runtime_prefix_size=28,
                     transaction_report_offset=162128, transaction_prefix_size=24)
RUNTIME_PHASES = ('NOT_STARTED', 'RUNNING', 'STOPPED', 'FAULT', 'STOP_OBSERVING')
RUNTIME_FAULTS = ('NONE', 'PORT', 'CLOCK', 'SERVICE_LIMIT', 'TRANSACTION', 'PROJECTION')
TRANSACTION_PHASES = ('NOT_INITIALIZED', 'IDLE', 'ACQUIRING', 'DECIDED', 'FAULT')
TRANSACTION_FAULTS = ('NONE', 'SETUP', 'ORDER', 'CLOCK', 'IDENTITY', 'RECEIPT', 'ABORTED')
RUNTIME_FLAGS = ('fresh', 'initialization_complete', 'raw_lines', 'imu_expired',
                 'calibration_interrupted')
TRANSACTION_FLAGS = ('decision_made', 'finished', 'timing_valid')
RUNTIME_WORDS = ('next_release_us', 'missed_releases', 'epochs', 'service_passes',
                 'maximum_execution_us')
TRANSACTION_WORDS = ('started_us', 'decision_us', 'completed_us', 'execution_us')
require = p0.require


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def _sample(blob, path, runtime, errors):
    size, phases, faults, flags, words = ((28, RUNTIME_PHASES, RUNTIME_FAULTS,
        RUNTIME_FLAGS, RUNTIME_WORDS) if runtime else (24, TRANSACTION_PHASES,
        TRANSACTION_FAULTS, TRANSACTION_FLAGS, TRANSACTION_WORDS))
    if type(blob) is not bytes or len(blob) != size:
        errors.append(dict(code='EXTENT', path=path))
        return None
    sample = dict(phase=blob[0], fault=blob[1])
    for name, names in (('phase', phases), ('fault', faults)):
        value = sample[name]
        sample[name + '_name'] = names[value] if value < len(names) else 'UNKNOWN'
        if value >= len(names):
            errors.append(dict(code='ENUM', path=path + '.' + name))
    for offset, name in enumerate(flags, 2):
        sample[name] = blob[offset]
        if blob[offset] not in (0, 1):
            errors.append(dict(code='BOOLEAN', path=path + '.' + name))
    sample.update(zip(words, struct.unpack_from('<' + 'I' * len(words), blob, 8)))
    return sample


def decode_app_samples(runtime_first: bytes, transaction_first: bytes,
                       runtime_second: bytes, transaction_second: bytes) -> dict:
    errors, runtime, transaction = [], [], []
    for index, (rb, tb) in enumerate(((runtime_first, transaction_first),
                                     (runtime_second, transaction_second))):
        runtime.append(_sample(rb, f'runtime[{index}]', True, errors))
        transaction.append(_sample(tb, f'transaction[{index}]', False, errors))
    if errors:
        observation = 'MALFORMED_SAMPLE'
    elif any(s['phase'] == 3 or s['fault'] != 0 for s in runtime):
        observation = 'FAULT_SAMPLED'
    elif all(s['phase'] == 1 for s in runtime) and runtime[1]['epochs'] > runtime[0]['epochs']:
        observation = 'RUNNING_COUNTER_ADVANCED'
    else:
        observation = 'INCONCLUSIVE_SAMPLED'
    if any(s is not None and (s['phase'] == 4 or 1 <= s['fault'] <= 6) for s in transaction):
        fault = True
    elif any(e['path'].startswith('transaction[') for e in errors):
        fault = None
    else:
        fault = False
    return dict(runtime=runtime, transaction=transaction, errors=errors,
                runtime_observation=observation, transaction_fault_sampled=fault)


def _initial_report(folder):
    return dict(schema_version=1, collection_status='FAILED', output_directory=str(folder),
        source_sha256=SOURCE_HASH, elf_sha256=ELF_HASH, zsk_sha256=BINARY_HASH,
        offline_debug_elf_sha256=DEBUG_ELF_HASH, pinned_files={str(p): h for p, h in EXPECTED_HASHES.items()},
        maximum_read_plan=dict(MAXIMUM_READ_PLAN), counts=dict(reads=0, commands=0, requested_bytes=0),
        layout=None, extension=dict(status='UNKNOWN', nodes=[], sketch=None),
        heap=dict(before=None, after=None, comparison=None), app_samples=None,
        errors=[], commands=[], reads=[], file_hashes={}, limitations=[
            'Live multi-byte samples and matching references are not atomic observations.',
            'The app remains loaded and may continue inhibited native ticks after observation.',
            'All optional SetupGrants remain false; existing inhibited native motor setup is real I/O.',
            'Stored execution counters do not establish WCET, calibrated timing or a five-minute run.',
            'Allocator payload is not loading peak, stack headroom or total free system RAM.',
            'No pin, electrical inhibition, motor, physical, STAND/RING or human gate acceptance.',
            'Absence does not diagnose OOM; observed progress is not a terminal result.'])


def _read_plan():
    flash_reads = sum((n + FLASH_BLOCK_BYTES - 1) // FLASH_BLOCK_BYTES
                      for n in (LOADER_BYTES, BINARY_BYTES))
    reads = 2 * flash_reads + 32 + 2 + 2 + 2 * MAX_NODES + 4
    size = 2 * (LOADER_BYTES + BINARY_BYTES + HEAP_BYTES) + 48 + 16 + 6 * NODE_BYTES + 104
    plan = dict(reads=reads, commands=reads + 4, requested_bytes=size)
    require(plan == MAXIMUM_READ_PLAN, 'complete pinned read plan changed')
    require(reads <= MAX_READS and reads + 4 <= MAX_COMMANDS and size <= MAX_BYTES,
            'complete plan exceeds its finite ceiling')
    return plan


def _metadata_commands():
    return ([str(OPENOCD), '--version'], [str(READELF), '--version'],
            [str(READELF), '-h', '-S', '-W', str(ELF_PATH)],
            [str(READELF), '-s', '-W', str(ELF_PATH)])


class Capture:
    def __init__(self, folder: Path, report: dict):
        self.folder, self.report = folder, report
        self._used = self._active = self._failed = False
        self._identities = self._layout = False
        self._metadata_index = self._block = self._confirm_index = 0
        self._phase, self._read_command = 'unstarted', None
        self._nodes, self._samples, self._pools = [], {}, {}
        self._pieces, self._purposes, self._references = [], set(), {}
        self._sketch = None
        self._output_created = False

    def _remaining(self):
        require(self._active and not self._failed, 'no healthy active collection')
        remaining = TOTAL_SECONDS - (time.monotonic() - self._started)
        if remaining <= 0:
            raise TimeoutError('600-second collection deadline reached')
        return remaining

    def _command_allowed(self, argv, attach):
        self._remaining()
        require(type(attach) is bool and self._identities, 'verified identities required')
        if attach:
            require(self._read_command is not None and tuple(argv) == self._read_command,
                    'command differs from the admitted MEM-AP read')
            self._read_command = None
        else:
            require(self._metadata_index < 4 and argv == _metadata_commands()[self._metadata_index],
                    'command is not the next exact metadata purpose')
            self._metadata_index += 1

    def _finish_command(self, record, out, err):
        record.update(finished_at_utc=utc_now(), finished_monotonic=time.monotonic())
        for name, path in (('stdout', out), ('stderr', err)):
            if path.exists():
                p0.no_symlinks(path)
                require(path.is_file(), 'command output is not a regular file')
                with path.open('rb') as stream:
                    raw = stream.read(65537)
                record[name] = raw[:65536].decode('utf-8', errors='replace')
                record[name + '_truncated'] = len(raw) > 65536
                record[name + '_bytes'] = path.stat().st_size
                record[name + '_sha256'] = p0.file_hash(path)

    def run(self, argv, attach=False) -> str:
        try:
            argv = [str(item) for item in argv]
            self._command_allowed(argv, attach)
            counts = self.report['counts']
            require(counts['commands'] < MAX_COMMANDS, 'command ceiling exceeded')
            started = time.monotonic()
            timeout = min(COMMAND_SECONDS, self._remaining())
            p0.no_symlinks(self.folder)
            index = counts['commands']
            out, err = self.folder / f'cmd-{index:02d}.out', self.folder / f'cmd-{index:02d}.err'
            record = dict(argv=argv, attach=attach, started_at_utc=utc_now(),
                started_monotonic=started, timeout_seconds=timeout,
                stdout_file=out.name, stderr_file=err.name)
            counts['commands'] += 1
            self.report['commands'].append(record)
            try:
                with out.open('xb') as stdout, err.open('xb') as stderr:
                    timeout = min(timeout, self._remaining())
                    record['timeout_seconds'] = timeout
                    result = subprocess.run(argv, stdin=subprocess.DEVNULL, stdout=stdout,
                        stderr=stderr, timeout=timeout, check=False, env={**os.environ, 'LC_ALL': 'C'})
                record['returncode'] = result.returncode
            except Exception as error:
                record.update(error_type=type(error).__name__, error=str(error),
                              returncode=getattr(error, 'returncode', None))
                if isinstance(error, subprocess.TimeoutExpired):
                    record['timeout'] = True
                raise
            finally:
                self._finish_command(record, out, err)
            self._remaining()
            if result.returncode != 0:
                raise subprocess.CalledProcessError(result.returncode, argv)
            require(out.stat().st_size <= 2000000 and err.stat().st_size <= 2000000,
                    'command text exceeds the retained decode bound')
            text = out.read_text(encoding='utf-8', errors='replace')
            self._remaining()
            return text
        except Exception:
            self._failed = True
            raise

    def _contained(self, address, size, heap, alignment=4):
        p0.ram_range(address, size)
        require(address % alignment == 0, 'allocation reference alignment differs')
        matches = [c for c in heap['chunks'] if c['used'] and
            p0.in_range(address, size, (HEAP_BASE + c['index'] * 8 + 4,
                                       HEAP_BASE + (c['index'] + c['size_units']) * 8))]
        require(len(matches) == 1, 'reference does not fit one used allocation')
        return matches[0]

    def _check_sketch_extent(self, sketch, heap):
        base, runtime = sketch['bss_address'], sketch['runtime_address']
        self._contained(base, PINNED_LAYOUT['bss_size'], heap, 8)
        for address, size in ((runtime, PINNED_LAYOUT['runtime_size']),
            (runtime + PINNED_LAYOUT['runtime_report_offset'], 28),
            (runtime + PINNED_LAYOUT['transaction_report_offset'], 24)):
            require(p0.in_range(address, size, (base, base + PINNED_LAYOUT['bss_size'])),
                    'runtime or report exceeds BSS')
            self._contained(address, size, heap)

    def _expected_read(self):
        self._remaining()
        require(self._layout and self._metadata_index == 4, 'validated final layout required')
        phase = self._phase
        if phase.startswith(('loader-', 'sketch-')):
            region = phase.split('-')[0]
            base, total = (0x08000000, LOADER_BYTES) if region == 'loader' else (0x08100000, BINARY_BYTES)
            offset = self._block * FLASH_BLOCK_BYTES
            return f'{phase}-{self._block:02d}', base + offset, min(FLASH_BLOCK_BYTES, total - offset), region
        if phase.startswith('heap-descriptor-'):
            return phase, DESCRIPTOR_ADDRESS, 24, 'ram'
        if phase.startswith('pool-'):
            return f'{phase}-{self._block:02d}', HEAP_BASE + self._block * RAM_BLOCK_BYTES, RAM_BLOCK_BYTES, 'ram'
        if phase.startswith('llext-list-'):
            return phase, LIST_ADDRESS, 8, 'ram'
        if phase == 'nodes-before':
            require(len(self._nodes) < MAX_NODES and self._next not in [n['address'] for n in self._nodes],
                    'excess nodes or cyclic list')
            self._contained(self._next, NODE_BYTES, self.report['heap']['before'])
            return f'node-before-{len(self._nodes) + 1}', self._next, NODE_BYTES, 'ram'
        if phase == 'nodes-after':
            return f'node-after-{self._confirm_index + 1}', self._nodes[self._confirm_index]['address'], NODE_BYTES, 'ram'
        if phase in ('runtime-first', 'runtime-second', 'transaction-first', 'transaction-second'):
            kind = phase.split('-')[0]
            address = self._sketch['runtime_address'] + PINNED_LAYOUT[kind + '_report_offset']
            return phase, address, PINNED_LAYOUT[kind + '_prefix_size'], 'ram'
        raise ValueError('no further memory purpose exists')

    def _accept_flash(self, data):
        region, when = self._phase.split('-')
        offset = self._block * FLASH_BLOCK_BYTES
        reference = self._references[region]
        require(data == reference[offset:offset + len(data)], 'full flash identity mismatch')
        self._block += 1
        if self._block * FLASH_BLOCK_BYTES < len(reference):
            return
        self._block = 0
        if region == 'loader':
            self._phase = 'sketch-' + when
        elif when == 'before':
            self.report['flash_identity_verified'] = True
            self._phase = 'heap-descriptor-before'
        else:
            self.report['final_flash_identity_verified'] = True
            self._phase = 'finished'

    def _accept_pool(self, data):
        self._pieces.append(data)
        self._block += 1
        if self._block != 16:
            return
        blob = b''.join(self._pieces)
        self._pieces, self._block = [], 0
        key = 'before' if self._phase == 'pool-1' else 'after'
        self._pools[key] = blob
        self.report['heap'][key] = recorder_heap.decode_pool(blob)
        if key == 'before':
            self._phase = 'llext-list-before'
            return
        self.report['heap']['comparison'] = recorder_heap.compare_pools(self._pools['before'], blob)
        for node in self._nodes:
            self._contained(node['address'], NODE_BYTES, self.report['heap']['after'])
        if self._sketch is not None:
            self._check_sketch_extent(self._sketch, self.report['heap']['after'])
        self._phase = 'heap-descriptor-after'

    def _accept_descriptor(self, data):
        require(struct.unpack_from('<III', data) == (HEAP_BASE, HEAP_BASE, HEAP_BYTES),
                'heap descriptor differs from pinned allocator')
        if self._phase == 'heap-descriptor-before':
            self._descriptor = data
            self._phase = 'pool-1'
        else:
            require(data == self._descriptor, 'heap descriptor changed')
            self._phase = 'runtime-second' if self._sketch else self._confirmation_phase()

    def _confirmation_phase(self):
        return 'nodes-after' if self._nodes else 'llext-list-after'

    def _accept_list(self, data):
        if self._phase == 'llext-list-after':
            require(data == self._listing, 'LLEXT list changed')
            self._phase = 'loader-after'
            return
        self._listing = data
        self._next, self._tail = struct.unpack('<II', data)
        require(bool(self._next) == bool(self._tail), 'inconsistent empty-list descriptor')
        if self._next:
            self._contained(self._next, NODE_BYTES, self.report['heap']['before'])
            self._contained(self._tail, NODE_BYTES, self.report['heap']['before'])
        self._phase = 'nodes-before' if self._next else 'pool-2'

    def _sketch_node(self, data, address):
        require(self._sketch is None, 'duplicate sketch node')
        base, size = struct.unpack_from('<I', data, 32)[0], struct.unpack_from('<I', data, 92)[0]
        require(data[71] == 1 and size == PINNED_LAYOUT['bss_size'], 'sketch BSS ownership or size differs')
        require(struct.unpack_from('<II', data, 184) == (16, 0x0812ad30) and data[192] == 0,
                'sketch resident section table differs')
        sketch = dict(node_address=address, bss_address=base, runtime_address=base)
        self._check_sketch_extent(sketch, self.report['heap']['before'])
        return sketch

    def _accept_node(self, data):
        if self._phase == 'nodes-after':
            require(data == self._nodes[self._confirm_index]['bytes'], 'LLEXT node changed')
            self._confirm_index += 1
            if self._confirm_index == len(self._nodes):
                self._phase = 'llext-list-after'
            return
        address, raw_name = self._next, data[4:20]
        require(b'\0' in raw_name, 'unterminated node name')
        name = raw_name.split(b'\0', 1)[0]
        if name == b'sketch':
            self._sketch = self._sketch_node(data, address)
        self._nodes.append(dict(address=address, bytes=data))
        self.report['extension']['nodes'].append(dict(address=address, name_hex=name.hex()))
        self._next = struct.unpack_from('<I', data)[0]
        if self._next:
            require(len(self._nodes) < MAX_NODES and self._next not in [n['address'] for n in self._nodes],
                    'excess nodes or cyclic list')
            self._contained(self._next, NODE_BYTES, self.report['heap']['before'])
            return
        require(self._tail == address, 'list tail is not last node')
        self._phase = 'runtime-first' if self._sketch else 'pool-2'

    def _accept_read(self, data):
        phase = self._phase
        if phase.startswith(('loader-', 'sketch-')):
            self._accept_flash(data)
        elif phase.startswith('pool-'):
            self._accept_pool(data)
        elif phase.startswith('heap-descriptor-'):
            self._accept_descriptor(data)
        elif phase.startswith('llext-list-'):
            self._accept_list(data)
        elif phase.startswith('nodes-'):
            self._accept_node(data)
        else:
            self._samples[phase] = data
            self._phase = {'runtime-first': 'transaction-first', 'transaction-first': 'pool-2',
                'runtime-second': 'transaction-second', 'transaction-second': self._confirmation_phase()}[phase]
            if phase == 'transaction-second':
                self.report['app_samples'] = decode_app_samples(*(self._samples[name] for name in
                    ('runtime-first', 'transaction-first', 'runtime-second', 'transaction-second')))

    def _retain_blob(self, target, record):
        if target.exists() and not target.is_symlink():
            p0.no_symlinks(target)
            if target.is_file():
                record.update(bytes_present=target.stat().st_size, sha256=p0.file_hash(target))

    def read(self, label, address, size, region='ram') -> bytes:
        target, record = None, None
        try:
            require(type(label) is str and p0.uint32(address) and type(size) is int,
                    'invalid memory purpose or extent')
            require((label, address, size, region) == self._expected_read() and label not in self._purposes,
                    'read differs from the next unused fixed purpose')
            if region == 'ram':
                p0.ram_range(address, size)
                require(size <= RAM_BLOCK_BYTES, 'RAM read exceeds16KiB')
            else:
                require(size <= FLASH_BLOCK_BYTES, 'flash read exceeds64KiB')
            counts = self.report['counts']
            require(counts['reads'] < MAX_READS and size <= MAX_BYTES - counts['requested_bytes'],
                    'memory request ceiling exceeded')
            require(re.fullmatch(r'/[A-Za-z0-9_./-]+', str(self.folder)) and '..' not in self.folder.parts,
                    'unsafe output path for fixed MEM-AP command')
            target = self.folder / f'{counts["reads"]:02d}-{label}.bin'
            require(not target.exists() and not target.is_symlink(), 'read output already exists')
            self._remaining()
            counts['reads'] += 1
            counts['requested_bytes'] += size
            self._purposes.add(label)
            record = dict(purpose=label, address=address, address_hex=f'0x{address:08x}', size=size,
                region=region, file=target.name, requested_at_utc=utc_now(), requested_monotonic=time.monotonic())
            self.report['reads'].append(record)
            argv = [str(OPENOCD), '-f', str(CONFIG), '-c',
                    f'dump_image {{{target}}} 0x{address:08x} {size}', '-c', 'shutdown']
            self._read_command = tuple(argv)
            self.run(argv, attach=True)
            p0.no_symlinks(target)
            require(target.is_file() and target.stat().st_size == size, 'short or oversized memory read')
            data = target.read_bytes()
            self._retain_blob(target, record)
            self._remaining()
            self._accept_read(data)
            self._remaining()
            return data
        except Exception as error:
            self._failed = True
            if record is not None:
                record.update(error_type=type(error).__name__, error=str(error))
            raise
        finally:
            self._read_command = None
            if record is not None:
                self._retain_blob(target, record)
                record.update(completed_at_utc=utc_now(), completed_monotonic=time.monotonic())


def _references(capture):
    loader_elf, package, sketch = LOADER_ELF.read_bytes(), LOADER.read_bytes(), BINARY_PATH.read_bytes()
    for path, data, expected in ((LOADER_ELF, loader_elf, EXPECTED_HASHES[LOADER_ELF]),
                                (LOADER, package, EXPECTED_HASHES[LOADER]), (BINARY_PATH, sketch, BINARY_HASH)):
        require(hashlib.sha256(data).hexdigest() == expected, 'reference changed after identity check: ' + str(path))
        capture._remaining()
    loader = p0.loader_image(loader_elf)
    require(len(loader) == len(package) == LOADER_BYTES and len(sketch) == BINARY_BYTES,
            'pinned reference size differs')
    different = [i for i, (a, b) in enumerate(zip(loader, package)) if a != b]
    capture.report['loader_identity'] = dict(reference='pinned ELF nonempty PT_LOAD physical bytes',
        size=LOADER_BYTES, expected_sha256=hashlib.sha256(loader).hexdigest(),
        package_binary_sha256=hashlib.sha256(package).hexdigest(), package_binary_matches=loader == package,
        package_binary_different_bytes=len(different), package_binary_first_differences=[
            dict(offset=i, elf=loader[i], binary=package[i]) for i in different[:16]])
    capture._references = dict(loader=loader, sketch=sketch)
    capture._remaining()


def check_identities(capture, artifact_dir) -> tuple[Path, Path]:
    try:
        capture._remaining()
        require(not capture._identities, 'identity checks cannot be repeated')
        directory = Path(artifact_dir)
        require(directory == ARTIFACT_DIR, 'only the exact pinned artifact directory is accepted')
        p0.no_symlinks(directory)
        require({p.name for p in directory.iterdir()} == {'app.ino.elf', 'app.ino.elf-zsk.bin'},
                'artifact directory must contain exactly the pinned pair')
        for path, expected in {**EXPECTED_HASHES, ELF_PATH: ELF_HASH, BINARY_PATH: BINARY_HASH}.items():
            capture._remaining()
            actual = p0.file_hash(path)
            capture.report['file_hashes'][str(path)] = actual
            require(actual == expected, 'file identity mismatch: ' + str(path))
            capture._remaining()
        require(ELF_PATH.stat().st_size == BINARY_PATH.stat().st_size == BINARY_BYTES,
                'pinned ELF/ZSK extent differs')
        capture.report['maximum_read_plan'] = _read_plan()
        _references(capture)
        capture._identities = True
        capture.run([OPENOCD, '--version'])
        command = capture.report['commands'][-1]
        capture.report['versions'] = dict(python=sys.version, core='arduino:zephyr@1.0.0',
            openocd=command.get('stdout', '') + command.get('stderr', ''), readelf=capture.run([READELF, '--version']))
        capture._remaining()
        return ELF_PATH, BINARY_PATH
    except Exception:
        capture._failed = True
        raise


def _validate_bss(headers):
    require(re.search(r'Type:\s+REL\b', headers) and re.search(r'Class:\s+ELF32\b', headers)
            and 'little endian' in headers and re.search(r'Machine:\s+ARM\b', headers),
            'final ELF must be ELF32 little-endian ARM ET_REL')
    rows = re.findall(r'^\s*\[\s*(\d+)\]\s+(\S+)\s+(\S+)\s+([0-9a-fA-F]+)\s+'
        r'([0-9a-fA-F]+)\s+([0-9a-fA-F]+)\s+\S+\s+(\S+)\s+\d+\s+\d+\s+(\d+)\s*$',
        headers, re.MULTILINE)
    bss = [row for row in rows if row[1] == '.bss']
    require(len(bss) == 1, 'missing or duplicate BSS')
    row = bss[0]
    require((int(row[0]), row[2], int(row[3], 16), int(row[4], 16), int(row[5], 16), row[6], int(row[7]))
            == (8, 'NOBITS', 87872, 92384, 167272, 'WA', 8), 'exact final BSS layout differs')


def _validate_symbol(symbols):
    matches = [line.split() for line in symbols.splitlines()
               if line.split() and line.split()[-1] == '_ZN12_GLOBAL__N_17runtimeE']
    require(len(matches) == 1 and len(matches[0]) == 8, 'missing or duplicate exact Runtime symbol')
    _, value, size, kind, binding, visibility, section, _ = matches[0]
    require((kind, binding, visibility, section) == ('OBJECT', 'LOCAL', 'DEFAULT', '8')
            and int(value, 16) == 0 and int(size) == 166376, 'Runtime symbol layout differs')


def read_layout(capture, elf) -> dict:
    try:
        capture._remaining()
        require(Path(elf) == ELF_PATH and not capture._layout, 'layout must be read once for pinned ELF')
        _validate_bss(capture.run([READELF, '-h', '-S', '-W', elf]))
        capture._remaining()
        _validate_symbol(capture.run([READELF, '-s', '-W', elf]))
        capture._remaining()
        capture.report['layout'] = dict(PINNED_LAYOUT)
        capture._layout, capture._phase = True, 'loader-before'
        return capture.report['layout']
    except Exception:
        capture._failed = True
        raise


def collect(capture, artifact_dir) -> dict:
    require(not capture._used and not capture._failed, 'this Capture instance is already consumed')
    capture._used = True
    capture._started = time.monotonic()
    capture._active = True
    capture.report.update(_initial_report(capture.folder))
    capture.report.update(started_at_utc=utc_now(), started_monotonic=capture._started)
    try:
        capture._remaining()
        desired = capture.folder
        if desired is None:
            name = datetime.now(timezone.utc).strftime('app-default-%Y%m%dT%H%M%S-%f')
            desired = CAPTURE_ROOT / f'{name}-{os.getpid()}'
        capture.folder = p0.fresh_directory(desired)
        capture._output_created = True
        capture.report['output_directory'] = str(capture.folder)
        capture._remaining()
        elf, _ = check_identities(capture, artifact_dir)
        read_layout(capture, elf)
        while capture._phase != 'finished':
            label, address, size, region = capture._expected_read()
            capture.read(label, address, size, region)
        capture._remaining()
        capture.report['extension'].update(status='PRESENT' if capture._sketch else 'ABSENT',
                                           sketch=capture._sketch)
        capture.report['collection_status'] = 'CAPTURED'
        capture._remaining()
    except Exception as error:
        capture._failed = True
        capture.report['collection_status'] = 'FAILED'
        capture.report['extension'].update(status='UNKNOWN', sketch=None)
        capture.report['errors'].append(dict(type=type(error).__name__, message=str(error)))
    finally:
        finished_at = utc_now()
        finished = time.monotonic()
        if finished - capture._started >= TOTAL_SECONDS and not capture._failed:
            capture._failed = True
            capture.report['collection_status'] = 'FAILED'
            capture.report['extension'].update(status='UNKNOWN', sketch=None)
            capture.report['errors'].append(dict(type='TimeoutError', message='600-second deadline at final validation'))
        capture._active = False
        capture.report.update(finished_at_utc=finished_at, finished_monotonic=finished,
                              duration_seconds=finished - capture._started)
    return capture.report


def _successful(report):
    samples = report.get('app_samples')
    return (report.get('collection_status') == 'CAPTURED' and report['extension']['status'] == 'PRESENT'
            and samples is not None and not samples['errors']
            and samples['runtime_observation'] == 'RUNNING_COUNTER_ADVANCED'
            and samples['transaction_fault_sampled'] is False)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description='Passively sample the exact default app and allocator')
    parser.add_argument('--artifact-dir', required=True)
    parser.add_argument('--output')
    args = parser.parse_args(argv)
    report = {}
    capture = Capture(Path(args.output) if args.output else None, report)
    try:
        collect(capture, args.artifact_dir)
    except Exception as error:
        report['collection_status'] = 'FAILED'
        report['errors'].append(dict(type=type(error).__name__, message=str(error)))
    if capture._output_created:
        try:
            with (capture.folder / 'capture.json').open('x', encoding='utf-8') as stream:
                stream.write(json.dumps(report, indent=2, allow_nan=False) + '\n')
        except Exception as error:
            report['collection_status'] = 'FAILED'
            report['errors'].append(dict(type=type(error).__name__, message=str(error)))
    print(json.dumps(report, indent=2, allow_nan=False))
    return 0 if _successful(report) else 1


if __name__ == '__main__':
    raise SystemExit(main())
