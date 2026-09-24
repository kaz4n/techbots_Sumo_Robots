# Reads the single reviewed A1 diagnostic through bounded, read-only MEM-AP commands.
# Keeps byte collection, frozen failure evidence and physical acceptance separate.
# Independent D114 literal ABI and command-fixture tests cover this pinned collector.
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

OPENOCD, READELF, CONFIG = p0.OPENOCD, p0.READELF, p0.CONFIG
LOADER, LOADER_ELF, LOADER_SIZE = p0.LOADER, p0.LOADER_ELF, p0.LOADER_SIZE
CAPTURE_ROOT, SRAM, LIST_ADDRESS = p0.CAPTURE_ROOT, p0.SRAM, p0.LIST_ADDRESS
SOURCE_HASH = '396bcc45fbaf30d38b170bf0c0063c555d5e88cdad512829b86a52ffede18642'
ARTIFACT_DIR = Path('/home/arduino/sumox26-capture-input/ui_adc_probe_' + SOURCE_HASH)
ELF_PATH = ARTIFACT_DIR / 'ui_adc_probe.ino.elf'
BINARY_PATH = ARTIFACT_DIR / 'ui_adc_probe.ino.elf-zsk.bin'
ELF_HASH = '76e23fe03631d5cc2144578d35ca78b9bafd44158e0d18b2ab026922e4c9d05b'
BINARY_HASH = '567fb90da6965cf74efc5ac2221e543d6d2150e3bf70ddae3e2346e6646c7fb9'
EXPECTED_HASHES = {**p0.EXPECTED_HASHES,
    READELF: 'c37462dcd380ae1039eb8a0aab379a619415e1100472291ffea2eae34161092e',
    Path(__file__).absolute().with_name('p0_capture.py'):
        '885c4e4206aea4ac9e03c4e92e48258db2a0ae302ff83a86430e6913afeeb57c',
}
PINNED_LAYOUT = {
    'bss_section': 8, 'bss_address': 5776, 'bss_file_offset': 6616,
    'bss_size': 9893, 'bss_alignment': 4,
    'symbol': '_ZN12_GLOBAL__N_16runnerE', 'symbol_value': 0,
    'symbol_size': 9892, 'symbol_binding': 'LOCAL',
    'symbol_type': 'OBJECT', 'symbol_visibility': 'DEFAULT',
    'runner_offset': 0, 'report_offset': 16, 'report_size': 132,
    'captures_offset': 148, 'capture_stride': 76, 'capture_count': 128,
}
MAXIMUM_READ_PLAN = {'reads': 22, 'bytes': 588016, 'commands': 26, 'extension_nodes': 3}
MAX_READS, MAX_BYTES, MAX_RAM_READ = 48, 2097152, 16384
MAX_COMMANDS, SEQUENCE_SECONDS, COMMAND_SECONDS = 64, 600.0, 30.0
FLASH_BLOCK_BYTES, MAX_EXTENSION_NODES, NODE_BYTES = 65536, 3, 196
RUNNER_BYTES, BINARY_BYTES = 9892, 19840
UINT32_MAX, HALF_RANGE = 0xffffffff, 0x80000000
PERIOD_US, CONVERSION_US = 1000, 100
REPORT_FLAGS = ('fresh', 'clock_fault', 'counter_saturated', 'sample_seen',
                'last_read_accepted', 'decode_matches_sample')
TIMING_NAMES = ('setup_timing', 'read_timing', 'poll_timing')
CAPTURE_WORDS = ('call_started_us', 'call_returned_us', 'poll_closed_us',
                 'source_us', 'read_us', 'poll_us', 'missed_before')
require = p0.require


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def _words(blob, offset, names):
    return dict(zip(names, struct.unpack_from('<' + 'I' * len(names), blob, offset)))


def _sample(blob, offset):
    result = dict(status=blob[offset], shutdown=blob[offset + 1],
                  raw=struct.unpack_from('<H', blob, offset + 2)[0])
    result.update(_words(blob, offset + 4, ('started_us', 'completed_us', 'sequence')))
    result['valid'] = blob[offset + 16]
    return result


def _decoded(blob, offset):
    evidence = dict(zip(('explicit_values', 'contract_valid', 'presence', 'level'),
                        blob[offset + 4:offset + 8]))
    evidence['raw'] = struct.unpack_from('<H', blob, offset + 8)[0]
    evidence.update(_words(blob, offset + 12, ('sequence', 'started_us', 'completed_us')))
    return dict(qualification=blob[offset], evidence=evidence, candidate_mask=blob[offset + 24])


def _timing(blob, offset):
    result = _words(blob, offset, ('calls', 'measured_calls', 'last_us', 'maximum_us'))
    result['last_valid'] = blob[offset + 16]
    return result


def _report(blob):
    offset = PINNED_LAYOUT['report_offset']
    result = dict(phase=blob[offset], fault=blob[offset + 1])
    result.update(zip(REPORT_FLAGS, blob[offset + 2:offset + 8]))
    result['setup'] = dict(zip(('status', 'shutdown', 'ready'), blob[offset + 8:offset + 11]))
    result['sample'], result['decoded'] = _sample(blob, offset + 12), _decoded(blob, offset + 32)
    result.update(_words(blob, offset + 60, ('captured_samples', 'not_due', 'missed_releases')))
    for name, relative in zip(TIMING_NAMES, (72, 92, 112)):
        result[name] = _timing(blob, offset + relative)
    return result


def _capture(blob, index):
    offset = PINNED_LAYOUT['captures_offset'] + index * PINNED_LAYOUT['capture_stride']
    result = dict(sample=_sample(blob, offset), decoded=_decoded(blob, offset + 20))
    result.update(_words(blob, offset + 48, CAPTURE_WORDS))
    return result


def _check(errors, condition, code, path):
    error = {'code': code, 'path': path}
    if not condition and error not in errors:
        errors.append(error)


def _domains(errors, fields, path, enums=(), booleans=()):
    for name, lower, upper in enums:
        _check(errors, lower <= fields[name] <= upper, 'ENUM', path + '.' + name)
    for name in booleans:
        _check(errors, fields[name] in (0, 1), 'BOOL', path + '.' + name)


def _sample_domains(errors, sample, path):
    _domains(errors, sample, path, (('status', 0, 14), ('shutdown', 0, 2)), ('valid',))


def _decoded_domains(errors, decoded, path):
    _domains(errors, decoded, path, (('qualification', 0, 5), ('candidate_mask', 0, 15)))
    _domains(errors, decoded['evidence'], path + '.evidence',
             (('presence', 1, 3), ('level', 0, 3)), ('explicit_values', 'contract_valid'))


def _report_domains(errors, report):
    _domains(errors, report, 'report', (('phase', 0, 4), ('fault', 0, 7)), REPORT_FLAGS)
    _domains(errors, report['setup'], 'report.setup',
             (('status', 0, 14), ('shutdown', 0, 2)), ('ready',))
    _sample_domains(errors, report['sample'], 'report.sample')
    _decoded_domains(errors, report['decoded'], 'report.decoded')


def _validate_timing(errors, timing, path):
    _domains(errors, timing, path, booleans=('last_valid',))
    _check(errors, timing['measured_calls'] <= timing['calls'], 'TIMING', path + '.measured_calls')
    _check(errors, timing['last_us'] <= timing['maximum_us'] < HALF_RANGE, 'TIMING', path)
    if timing['last_valid']:
        _check(errors, timing['measured_calls'] > 0, 'TIMING', path + '.last_valid')
    if timing['measured_calls'] == 0:
        _check(errors, timing['last_us'] == timing['maximum_us'] == timing['last_valid'] == 0,
               'TIMING', path)


def _validate_phase(errors, report):
    phase, fault, count = (report[key] for key in ('phase', 'fault', 'captured_samples'))
    _check(errors, count <= 128, 'COUNT', 'report.captured_samples')
    if phase == 3:
        _check(errors, count == 128 and fault == 0, 'PHASE', 'report.phase')
    elif phase == 4:
        _check(errors, count < 128 and fault != 0, 'PHASE', 'report.phase')
    elif phase in (0, 1, 2):
        _check(errors, count < 128 and fault == 0, 'PHASE', 'report.phase')
    if phase in (0, 1):
        _check(errors, count == 0, 'COUNT', 'report.captured_samples')
    if report['clock_fault']:
        _check(errors, phase == 4, 'PHASE', 'report.clock_fault')
    if fault == 7:
        _check(errors, report['clock_fault'] == 1, 'PHASE', 'report.fault')


def _delta(later, earlier):
    return (later - earlier) & UINT32_MAX


def _capture_timing(errors, record, path):
    sample, started = record['sample'], record['call_started_us']
    offsets = [_delta(value, started) for value in (sample['started_us'], sample['completed_us'],
               record['call_returned_us'], record['poll_closed_us'])]
    _check(errors, offsets == sorted(offsets) and offsets[-1] < HALF_RANGE, 'TIMING', path)
    duration = _delta(sample['completed_us'], sample['started_us'])
    _check(errors, duration < CONVERSION_US and record['source_us'] == duration,
           'SOURCE', path + '.source_us')
    _check(errors, record['read_us'] == offsets[2], 'TIMING', path + '.read_us')
    _check(errors, record['poll_us'] == offsets[3], 'TIMING', path + '.poll_us')


def _capture_decoder(errors, record, path):
    decoded, sample = record['decoded'], record['sample']
    evidence = decoded['evidence']
    expected = dict(qualification=2, candidate_mask=0)
    for name, value in expected.items():
        _check(errors, decoded[name] == value, 'DECODER', path + '.decoded.' + name)
    for name, value in (('explicit_values', 1), ('contract_valid', 1), ('presence', 3), ('level', 0)):
        _check(errors, evidence[name] == value, 'DECODER', path + '.decoded.evidence.' + name)
    for name in ('raw', 'sequence', 'started_us', 'completed_us'):
        _check(errors, evidence[name] == sample[name], 'DECODER', path + '.decoded.evidence.' + name)


def _validate_capture(errors, record, index, previous):
    path = f'captures[{index}]'
    sample = record['sample']
    _sample_domains(errors, sample, path + '.sample')
    _decoded_domains(errors, record['decoded'], path + '.decoded')
    for name, expected in (('status', 0), ('shutdown', 0), ('valid', 1), ('sequence', index + 1)):
        _check(errors, sample[name] == expected, 'SOURCE', path + '.sample.' + name)
    _check(errors, sample['raw'] <= 16383, 'SOURCE', path + '.sample.raw')
    _capture_timing(errors, record, path)
    _capture_decoder(errors, record, path)
    if previous is None:
        _check(errors, record['missed_before'] == 0, 'SOURCE', path + '.missed_before')
        return
    age = _delta(record['call_started_us'], previous['sample']['started_us'])
    gap = _delta(record['call_started_us'], previous['poll_closed_us'])
    _check(errors, PERIOD_US <= age < HALF_RANGE and gap < HALF_RANGE,
           'SOURCE', path + '.call_started_us')
    _check(errors, record['missed_before'] == age // PERIOD_US - 1, 'SOURCE', path + '.missed_before')


def _complete_timing(errors, report, captures):
    setup, read, poll = (report[name] for name in TIMING_NAMES)
    _check(errors, setup['calls'] == setup['measured_calls'] == setup['last_valid'] == 1,
           'CONSISTENCY', 'report.setup_timing')
    _check(errors, read['calls'] == read['measured_calls'] == 128 and read['last_valid'] == 1,
           'CONSISTENCY', 'report.read_timing')
    _check(errors, poll['measured_calls'] == 128 and poll['last_valid'] == 1 and
           poll['calls'] == min(UINT32_MAX, 128 + report['not_due']),
           'CONSISTENCY', 'report.poll_timing')
    for name, field in (('read_timing', 'read_us'), ('poll_timing', 'poll_us')):
        timing = report[name]
        _check(errors, timing['last_us'] == captures[-1][field] and
               timing['maximum_us'] == max(record[field] for record in captures),
               'CONSISTENCY', 'report.' + name)


def _cross_records(errors, report, captures):
    missed = min(UINT32_MAX, sum(record['missed_before'] for record in captures))
    _check(errors, report['missed_releases'] >= missed, 'CONSISTENCY', 'report.missed_releases')
    if report['phase'] != 3 or len(captures) != 128:
        return
    _check(errors, report['setup'] == {'status': 0, 'shutdown': 0, 'ready': 1},
           'CONSISTENCY', 'report.setup')
    _check(errors, report['clock_fault'] == 0, 'CONSISTENCY', 'report.clock_fault')
    for name in ('sample_seen', 'last_read_accepted', 'decode_matches_sample'):
        _check(errors, report[name] == 1, 'CONSISTENCY', 'report.' + name)
    for name in ('sample', 'decoded'):
        _check(errors, report[name] == captures[-1][name], 'CONSISTENCY', 'report.' + name)
    _check(errors, report['missed_releases'] == missed, 'CONSISTENCY', 'report.missed_releases')
    _complete_timing(errors, report, captures)


def _decode_snapshot(blob):
    report, errors = _report(blob), []
    _report_domains(errors, report)
    for name in TIMING_NAMES:
        _validate_timing(errors, report[name], 'report.' + name)
    _validate_phase(errors, report)
    count = report['captured_samples']
    captures = None if count > 128 else [_capture(blob, index) for index in range(count)]
    if captures is not None:
        for index, record in enumerate(captures):
            _validate_capture(errors, record, index, captures[index - 1] if index else None)
        _cross_records(errors, report, captures)
    return dict(valid=not errors, errors=errors, report=report, captures=captures)


def decode_runner_pair(first: bytes, second: bytes) -> dict:
    require(type(first) is bytes and type(second) is bytes and
            len(first) == len(second) == RUNNER_BYTES, 'Runner inputs must be exactly9892 immutable bytes')
    snapshots = [_decode_snapshot(first), _decode_snapshot(second)]
    identical = first == second
    acquisition, frozen = 'UNAVAILABLE', False
    if identical and all(snapshot['valid'] for snapshot in snapshots):
        phase = snapshots[0]['report']['phase']
        acquisition = {3: 'COMPLETE_128', 4: 'FAULT'}.get(phase, 'NONTERMINAL')
        frozen = phase in (3, 4)
    return dict(schema_version=1, first_sha256=hashlib.sha256(first).hexdigest(),
                second_sha256=hashlib.sha256(second).hexdigest(), byte_identical=identical,
                snapshots=snapshots, frozen=frozen, acquisition=acquisition, physical_acceptance=False)


def fresh_directory(output):
    p0.no_symlinks(CAPTURE_ROOT, must_exist=False)
    CAPTURE_ROOT.mkdir(mode=0o700, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime('ui-adc-%Y%m%dT%H%M%S-%f')
    folder = Path(output) if output else CAPTURE_ROOT / f'{stamp}-{os.getpid()}'
    require(folder.parent == CAPTURE_ROOT and
            re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,95}', folder.name),
            'output must be a fresh direct child of the fixed capture root')
    p0.no_symlinks(folder, must_exist=False)
    folder.mkdir(mode=0o700, exist_ok=False)
    return folder


class Capture:
    def __init__(self, folder: Path, report: dict):
        self.folder, self.report = Path(folder), report
        self.read_count = self.read_bytes = 0
        self.deadline = time.monotonic() + SEQUENCE_SECONDS
        self.identities_verified = False
        self._failed = self._layout_verified = False
        self._metadata_index = self._flash_index = self._confirm_index = 0
        self._phase = 'loader-before'
        self._read_command = None
        self._purposes, self._nodes, self._matches = set(), [], []
        self._listing, self._references = None, {}
        self._next = self._tail = self._bss = None
        self.report.setdefault('commands', [])
        self.report.setdefault('reads', [])
        self.report.update(collection_integrity='FAILED', diagnostic=None, physical_acceptance=False,
                           local_identities_verified=False, flash_identity_verified=False,
                           final_flash_identity_verified=False)

    def _metadata_commands(self):
        return [(str(OPENOCD), '--version'), (str(READELF), '--version'),
                (str(READELF), '-hSW', str(ELF_PATH)), (str(READELF), '-sW', str(ELF_PATH))]

    def _command_allowed(self, argv, attach):
        require(not self._failed and self.identities_verified, 'local identity or prior failure blocks commands')
        if attach:
            require(self._read_command is not None and tuple(argv) == self._read_command,
                    'only the currently admitted MEM-AP read is permitted')
        else:
            allowed = self._metadata_commands()
            require(self._metadata_index < len(allowed) and tuple(argv) == allowed[self._metadata_index],
                    'command is outside the ordered metadata checks')
            self._metadata_index += 1

    def _finish_command(self, record, out, err):
        record.update(finished_at_utc=utc_now(), finished_monotonic=time.monotonic())
        for key, path in (('stdout', out), ('stderr', err)):
            if path.exists():
                p0.no_symlinks(path)
                with path.open('rb') as stream:
                    data = stream.read(65537)
                record[key] = data[:65536].decode('utf-8', errors='replace')
                record[key + '_truncated'] = len(data) > 65536

    def run(self, argv, attach=False):
        argv = [str(item) for item in argv]
        self._command_allowed(argv, attach)
        require(len(self.report['commands']) < MAX_COMMANDS, '64-command bound exceeded')
        started = time.monotonic()
        timeout = min(COMMAND_SECONDS, self.deadline - started)
        require(timeout > 0, '600-second sequence deadline exceeded')
        p0.no_symlinks(self.folder)
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
        except (OSError, subprocess.SubprocessError) as error:
            record.update(returncode=getattr(error, 'returncode', None), error=str(error))
        finally:
            self._finish_command(record, out, err)
        healthy = record.get('returncode') == 0 and record['finished_monotonic'] < self.deadline
        self._failed = not healthy
        require(healthy, 'command failed or exceeded sequence deadline')
        require(out.stat().st_size <= 2_000_000 and err.stat().st_size <= 2_000_000,
                'command text output exceeds bound')
        return out.read_text(encoding='utf-8', errors='replace')

    def _expected_read(self):
        require(self.identities_verified and self._layout_verified and not self._failed,
                'verified local identities/layout and healthy sequence are required')
        phase = self._phase
        if phase.startswith(('loader-', 'sketch-')):
            region = phase.split('-')[0]
            total, base = (LOADER_SIZE, 0x08000000) if region == 'loader' else (BINARY_BYTES, 0x08100000)
            offset = self._flash_index * FLASH_BLOCK_BYTES
            return f'{phase}-{self._flash_index:02d}', base + offset, min(FLASH_BLOCK_BYTES, total - offset), region
        require(self.report['flash_identity_verified'] is True, 'deployed identity required before private RAM')
        if phase in ('list-before', 'list-after'):
            return 'llext-' + phase, LIST_ADDRESS, 8, 'ram'
        if phase == 'nodes-before':
            require(len(self._nodes) < MAX_EXTENSION_NODES and self._next not in
                    [node['address'] for node in self._nodes], 'LLEXT traversal bound or cycle')
            return f'node-before-{len(self._nodes) + 1}', self._next, NODE_BYTES, 'ram'
        if phase == 'nodes-after':
            return f'node-after-{self._confirm_index + 1}', self._nodes[self._confirm_index]['address'], NODE_BYTES, 'ram'
        if phase in ('runner-first', 'runner-second'):
            return phase, self._bss + PINNED_LAYOUT['runner_offset'], RUNNER_BYTES, 'ram'
        raise ValueError('the finite memory sequence has finished')

    def _read_purpose(self, label, address, size, region):
        require(type(label) is str and p0.uint32(address) and type(size) is int and size > 0,
                'invalid memory purpose or extent')
        require((label, address, size, region) == self._expected_read(),
                'read differs from the next fixed purpose/address/extent')
        require(label not in self._purposes, 'memory purpose was already attempted')
        if region == 'ram':
            p0.ram_range(address, size)
            require(size <= MAX_RAM_READ, 'RAM read exceeds16KiB')
        else:
            base, total = (0x08000000, LOADER_SIZE) if region == 'loader' else (0x08100000, BINARY_BYTES)
            require(p0.in_range(address, size, (base, base + total)), 'flash read escapes pinned extent')

    def _accept_flash(self, data):
        region, when = self._phase.split('-')
        offset = self._flash_index * FLASH_BLOCK_BYTES
        reference = self._references[region]
        require(data == reference[offset:offset + len(data)], 'deployed flash differs from pinned bytes')
        self._flash_index += 1
        if self._flash_index * FLASH_BLOCK_BYTES < len(reference):
            return
        self._flash_index = 0
        if region == 'loader':
            self._phase = 'sketch-' + when
        elif when == 'before':
            self.report['flash_identity_verified'] = True
            self._phase = 'list-before'
        else:
            self.report['final_flash_identity_verified'] = True
            self._phase = 'complete'

    def _accept_list(self, data):
        if self._phase == 'list-after':
            require(data == self._listing, 'LLEXT list changed across Runner reads')
            self._phase = 'nodes-after'
            return
        self._listing = data
        self._next, self._tail = struct.unpack('<II', data)
        require(self._next != 0 and self._tail != 0, 'LLEXT list is empty or malformed')
        p0.ram_range(self._next, NODE_BYTES)
        p0.ram_range(self._tail, NODE_BYTES)
        self._phase = 'nodes-before'

    def _accept_node(self, data):
        if self._phase == 'nodes-after':
            require(data == self._nodes[self._confirm_index]['bytes'], 'LLEXT descriptor changed across Runner reads')
            self._confirm_index += 1
            if self._confirm_index == len(self._nodes):
                self._phase = 'loader-after'
            return
        address, name = self._next, data[4:20]
        require(b'\0' in name, 'unterminated LLEXT name')
        if name.split(b'\0', 1)[0] == b'sketch':
            base, size = struct.unpack_from('<I', data, 32)[0], struct.unpack_from('<I', data, 92)[0]
            require(size == PINNED_LAYOUT['bss_size'], 'runtime BSS differs from pinned layout')
            p0.ram_range(base, size)
            p0.ram_range(base + PINNED_LAYOUT['runner_offset'], RUNNER_BYTES)
            self._matches.append((base, address))
        self._nodes.append({'address': address, 'bytes': data})
        self._next = struct.unpack_from('<I', data)[0]
        if self._next:
            p0.ram_range(self._next, NODE_BYTES)
            require(len(self._nodes) < MAX_EXTENSION_NODES and self._next not in
                    [node['address'] for node in self._nodes], 'LLEXT traversal bound or cycle')
            return
        require(self._tail == address and len(self._matches) == 1, 'LLEXT tail or unique sketch mismatch')
        self._bss, owner = self._matches[0]
        self.report['extension'] = dict(node_address=owner, bss_address=self._bss,
            bss_size=PINNED_LAYOUT['bss_size'], visited_nodes=[node['address'] for node in self._nodes])
        self.report['symbol_addresses'] = {PINNED_LAYOUT['symbol']: self._bss + PINNED_LAYOUT['runner_offset']}
        self._phase = 'runner-first'

    def _accept_read(self, data):
        if self._phase.startswith(('loader-', 'sketch-')):
            self._accept_flash(data)
        elif self._phase.startswith('list-'):
            self._accept_list(data)
        elif self._phase.startswith('nodes-'):
            self._accept_node(data)
        elif self._phase == 'runner-first':
            self._phase = 'runner-second'
        elif self._phase == 'runner-second':
            self._phase = 'list-after'
        else:
            raise ValueError('unexpected read completion')

    def _partial_read(self, target, record):
        if target.exists() and not target.is_symlink():
            p0.no_symlinks(target)
            record['bytes_present'] = target.stat().st_size
            if target.is_file() and record['bytes_present'] <= record['size']:
                record['sha256'] = hashlib.sha256(target.read_bytes()).hexdigest()

    def read(self, label, address, size, region='ram'):
        self._read_purpose(label, address, size, region)
        require(self.read_count < MAX_READS and size <= MAX_BYTES - self.read_bytes,
                'memory read count or byte budget exceeded')
        require(re.fullmatch(r'/[A-Za-z0-9_./-]+', str(self.folder)) and '..' not in self.folder.parts,
                'output path is not safe for the fixed MEM-AP command')
        target = self.folder / f'{self.read_count:02d}-{label}.bin'
        require(not target.exists() and not target.is_symlink(), 'memory output already exists')
        self.read_count += 1
        self.read_bytes += size
        self._purposes.add(label)
        record = dict(address=address, address_hex=f'0x{address:08x}', size=size, region=region,
                      purpose=label, file=target.name, requested_at_utc=utc_now(),
                      requested_monotonic=time.monotonic())
        self.report['reads'].append(record)
        argv = [str(OPENOCD), '-f', str(CONFIG), '-c',
                f'dump_image {{{target}}} 0x{address:08x} {size}', '-c', 'shutdown']
        self._read_command = tuple(argv)
        try:
            self.run(argv, attach=True)
            p0.no_symlinks(target)
            require(target.is_file() and target.stat().st_size == size, 'short or oversized memory read')
            data = target.read_bytes()
            record.update(bytes_present=len(data), sha256=hashlib.sha256(data).hexdigest())
            self._accept_read(data)
            return data
        except (OSError, ValueError, subprocess.SubprocessError) as error:
            self._failed = True
            record['error'] = str(error)
            self._partial_read(target, record)
            raise
        finally:
            self._read_command = None
            record.update(completed_at_utc=utc_now(), completed_monotonic=time.monotonic())
            self.report.update(memory_read_attempts=self.read_count, memory_bytes_requested=self.read_bytes)


def _read_plan():
    flash_reads = (LOADER_SIZE + FLASH_BLOCK_BYTES - 1) // FLASH_BLOCK_BYTES
    flash_reads += (BINARY_BYTES + FLASH_BLOCK_BYTES - 1) // FLASH_BLOCK_BYTES
    reads = 2 * flash_reads + 2 + 2 * MAX_EXTENSION_NODES + 2
    total = 2 * (LOADER_SIZE + BINARY_BYTES) + 16 + 2 * MAX_EXTENSION_NODES * NODE_BYTES + 2 * RUNNER_BYTES
    plan = dict(reads=reads, bytes=total, commands=reads + 4, extension_nodes=MAX_EXTENSION_NODES)
    require(plan == MAXIMUM_READ_PLAN, 'pinned complete read plan changed')
    require(reads <= MAX_READS and total <= MAX_BYTES and reads + 4 <= MAX_COMMANDS and
            max(RUNNER_BYTES, NODE_BYTES, 8) <= MAX_RAM_READ, 'complete read plan exceeds a fixed ceiling')
    return plan


def _references(capture):
    loader_elf, packaged = LOADER_ELF.read_bytes(), LOADER.read_bytes()
    binary = BINARY_PATH.read_bytes()
    for path, data, expected in ((LOADER_ELF, loader_elf, EXPECTED_HASHES[LOADER_ELF]),
                                 (LOADER, packaged, EXPECTED_HASHES[LOADER]),
                                 (BINARY_PATH, binary, BINARY_HASH)):
        require(hashlib.sha256(data).hexdigest() == expected, f'reference changed after identity check: {path}')
    loader = p0.loader_image(loader_elf)
    require(len(loader) == len(packaged) == LOADER_SIZE and len(binary) == BINARY_BYTES,
            'pinned flash reference size differs')
    differences = [i for i, pair in enumerate(zip(loader, packaged)) if pair[0] != pair[1]]
    capture.report['loader_identity'] = dict(reference='pinned ELF nonempty PT_LOAD physical bytes',
        size=len(loader), expected_sha256=hashlib.sha256(loader).hexdigest(),
        package_binary_sha256=hashlib.sha256(packaged).hexdigest(), package_binary_matches=loader == packaged,
        package_binary_different_bytes=len(differences), package_binary_first_differences=[
            dict(offset=i, elf=loader[i], binary=packaged[i]) for i in differences[:16]])
    capture._references = {'loader': loader, 'sketch': binary}


def check_identities(capture, artifact_dir):
    require(not capture.identities_verified and not capture._failed, 'identity checks cannot be repeated')
    directory = Path(artifact_dir)
    require(directory == ARTIFACT_DIR, 'only the pinned ui_adc_probe artifact directory is accepted')
    p0.no_symlinks(directory)
    files = {**EXPECTED_HASHES, ELF_PATH: ELF_HASH, BINARY_PATH: BINARY_HASH}
    capture.report.setdefault('file_hashes', {})
    for path, expected in files.items():
        actual = p0.file_hash(path)
        capture.report['file_hashes'][str(path)] = actual
        require(actual == expected, f'file identity mismatch: {path}')
    require(ELF_PATH.stat().st_size == BINARY_PATH.stat().st_size == BINARY_BYTES,
            'pinned ELF/ZSK file size differs')
    capture.report['maximum_read_budget'] = _read_plan()
    _references(capture)
    capture.identities_verified = True
    capture.report['local_identities_verified'] = True
    capture.run([OPENOCD, '--version'])
    openocd = capture.report['commands'][-1]
    capture.report['versions'] = dict(python=sys.version, core='arduino:zephyr@1.0.0',
        openocd=openocd.get('stdout', '') + openocd.get('stderr', ''),
        readelf=capture.run([READELF, '--version']))
    return ELF_PATH, BINARY_PATH


def _bss_layout(headers):
    require(re.search(r'Type:\s+REL\b', headers) and re.search(r'Class:\s+ELF32\b', headers) and
            'little endian' in headers and re.search(r'Machine:\s+ARM\b', headers), 'unexpected final ELF format')
    rows = re.findall(r'^\s*\[\s*(\d+)\]\s+(\S+)\s+(\S+)\s+([0-9a-fA-F]+)\s+'
                      r'([0-9a-fA-F]+)\s+([0-9a-fA-F]+)\s+\S+\s+(\S+)\s+\d+\s+\d+\s+(\d+)\s*$',
                      headers, re.MULTILINE)
    bss = [row for row in rows if row[1] == '.bss']
    require(len(bss) == 1 and bss[0][2] == 'NOBITS' and bss[0][6] == 'WA', 'missing or duplicate BSS')
    row, expected = bss[0], PINNED_LAYOUT
    actual = (int(row[0]), int(row[3], 16), int(row[4], 16), int(row[5], 16), int(row[7]))
    require(actual == tuple(expected[name] for name in
            ('bss_section', 'bss_address', 'bss_file_offset', 'bss_size', 'bss_alignment')),
            'BSS differs from exact enabled ELF layout')


def _runner_symbol(symbols):
    expected = PINNED_LAYOUT
    matches = [line.split() for line in symbols.splitlines()
               if line.split() and line.split()[-1] == expected['symbol']]
    require(len(matches) == 1 and len(matches[0]) == 8, 'missing or duplicate exact Runner symbol')
    _, value, size, kind, binding, visibility, section, _ = matches[0]
    require((kind, binding, visibility, section) == ('OBJECT', 'LOCAL', 'DEFAULT', '8') and
            int(value, 16) == expected['symbol_value'] and int(size) == expected['symbol_size'],
            'Runner symbol differs from exact enabled layout')
    # readelf exposes ET_REL section-relative st_value; nm's VMA-added display is different.
    require(int(value, 16) == expected['runner_offset'] and
            expected['runner_offset'] + RUNNER_BYTES <= expected['bss_size'], 'Runner escapes relocated BSS')


def read_layout(capture, elf):
    require(Path(elf) == ELF_PATH and not capture._layout_verified, 'layout requires the one pinned ELF once')
    headers = capture.run([READELF, '-hSW', ELF_PATH])
    _bss_layout(headers)
    _runner_symbol(capture.run([READELF, '-sW', ELF_PATH]))
    capture.report['layout'] = dict(PINNED_LAYOUT)
    capture._layout_verified = True
    return capture.report['layout']


def collect(capture, artifact_dir):
    try:
        elf, _ = check_identities(capture, artifact_dir)
        read_layout(capture, elf)
        snapshots = {}
        for _ in range(MAXIMUM_READ_PLAN['reads']):
            if capture._phase == 'complete':
                break
            label, address, size, region = capture._expected_read()
            data = capture.read(label, address, size, region)
            if label in ('runner-first', 'runner-second'):
                snapshots[label] = data
        require(capture._phase == 'complete' and not capture._failed and
                capture.report['final_flash_identity_verified'] is True,
                'finite collection did not complete all identity brackets')
        capture.report['diagnostic'] = decode_runner_pair(snapshots['runner-first'], snapshots['runner-second'])
        capture.report['collection_integrity'] = 'VERIFIED'
        return capture.report
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        capture._failed = True
        capture.report.update(collection_integrity='FAILED', diagnostic=None, error=str(error))
        raise


def initial_report():
    return dict(schema_version=1, started_at_utc=utc_now(), source_sha256=SOURCE_HASH,
                collection_integrity='FAILED', diagnostic=None, physical_acceptance=False,
                commands=[], reads=[], file_hashes={}, limitations=[
                    'Floating bare A1 input: no voltage, physical button or wiring acceptance.',
                    'Two equal terminal snapshots are sampled consistency, not an atomic or future lease.',
                    'ADC may remain enabled/idle; elapsed micros are not calibrated physical timing.',
                    'A frozen FAULT records failed acquisition; no phase gate or full-app WCET claim.'])


def _successful_collection(report):
    diagnostic = report.get('diagnostic')
    return (report.get('collection_integrity') == 'VERIFIED' and type(diagnostic) is dict and
            diagnostic.get('frozen') is True and diagnostic.get('acquisition') in ('COMPLETE_128', 'FAULT'))


def main(argv=None):
    parser = argparse.ArgumentParser(description='Read the pinned bare-board A1 diagnostic without MCU writes')
    parser.add_argument('--artifact-dir', required=True)
    parser.add_argument('--output')
    args = parser.parse_args(argv)
    report, folder, started = initial_report(), None, time.monotonic()
    try:
        folder = fresh_directory(args.output)
        report['capture_directory'] = str(folder)
        collect(Capture(folder, report), args.artifact_dir)
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        report.update(collection_integrity='FAILED', diagnostic=None, error=str(error))
    report.update(finished_at_utc=utc_now(), capture_duration_seconds=time.monotonic() - started)
    output = json.dumps(report, indent=2, allow_nan=False)
    if folder is not None:
        try:
            with (folder / 'capture.json').open('x', encoding='utf-8') as stream:
                stream.write(output + '\n')
        except OSError as error:
            report.update(collection_integrity='FAILED', error=f'cannot save capture report: {error}')
            output = json.dumps(report, indent=2, allow_nan=False)
    print(output)
    return 0 if _successful_collection(report) else 1


if __name__ == '__main__':
    raise SystemExit(main())
