# Runs the single reviewed inert static compile with complete command receipts.
# Keeps uncertain transport completion and structural evidence separate from runtime acceptance.
# Tested by independent controlled-command fixtures under the frozen D143 contracts.
import argparse
import base64
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import re
import shlex
import stat
import subprocess
import sys
import types
import zlib

ROOT = Path(__file__).resolve().parents[3]
RAW = 'state/analysis/P7_static_link_probe_raw/'
SOURCE = 'fcddbd8ef5ba4c92a2080b03e9343ac78c2406b13d9514793aa147e02f0d1da2'
BOARD = '2629958581'
ADB = 'C:/Users/narut/AppData/Local/Arduino15/packages/arduino/tools/adb/32.0.0/adb.exe'
ADB_SHA = 'e79dc8fc3c6385192bdccd7ff7eabe3d5c1ec292475a06b04d82759f07655982'
DATA = '/home/arduino/.arduino15'
USER = '/home/arduino/Arduino'
REMOTE = '/home/arduino/sumox26_codex_build'
SKETCH = REMOTE + '/' + SOURCE + '/app'
PINS = {
    'tools/board_tool.py': '3f2dac6d2b0f75209d335f5045e5233aab2dea8ca9edd740b69a652476ddf2bc',
    'tools/app_build_policy.py': 'd5a4ce59870574ac601c3d8837b472adf7eec81e86982794fa16a7b3b354a7c6',
    'tools/app_build_commands.json': '63f6c41e34bae9fce1d945c3271b3fe86343f27544affe25ae14788438d62e1d',
    'tools/app_build_pins.json': '55720e65b03f6cd28964c675ceeec76619824cd11525549fbac0503b8efa972b',
    RAW + 'static_policy.py': 'ec3d8a5e8c4910bbdbbb96fb5123c8bb42b294ce9342c76db73b8d3b5eab7775',
    RAW + 'static_reference.json': '1dc8ac6dec8534536acfcc4da73516416ea465cfcc1a349900fd13e210144a2b',
    RAW + 'additional_pins.json': 'd8dc249656cef0a852af8385d59fbdd3e9e30ace2dcb113921bf7964483fe924',
    'state/analysis/P7_default_qualification_raw/reuse_stage.py': '78e173296c1d4366e4866b947b017814d69be2055c739cf1d96d0980eb40900e',
    'state/analysis/P7_default_qualification_raw/working_source_manifest.json': 'c106c0fb8baaf0a6f2536558da0084bd7d236c4ee8e77a4110b60107ad073391',
    'state/analysis/P7_default_qualification_raw/checked_stage_manifest.json': '56ab12b990ebe664941677e29dfef783197bc98c3a9de1985b54d57bb30da56a',
    'state/analysis/P7_static_link_probe_contract.md': 'd9090cc49a657bdaf08d47def5b9f1fdc8b7da620e19335a0a10b338da32abae',
    RAW + 'static_artifacts.py': 'd30372dd4b8fb8c2661d00affc4a215cc88e3f62511995ff6303827bed4b7368',
    'state/analysis/P7_static_artifact_contract.md': 'b6a18e4d27e500d6306587141cbb27bcd7e546ce9bb507f148f28591634bec54',
    'state/analysis/P7_static_runner_contract.md': '35473ed0eb59b9d7fd097cb25554b591ec6bd470703504e1a525219b2fdba7e7',
    'state/analysis/P7_static_remote_contract_draft.md': 'a4be3733d40632b4ae79e3bbbab3300f720b8f7f13f3337d35d96dfc90373b39',
    RAW + 'static_bootstrap.txt': 'a6bb46737bea18fc564e77bbd7124c20771258b4fe4ca41a17cbd4cce9798419',
    RAW + 'static_remote.py': 'fa209bee067f416f7f7619e350562806b333b4d3e6faf902a7f51878eb231e1b',
}
LIMITS = {name: 16777216 for name in (
    'app.ino.elf', 'app.ino_debug.elf', 'app.ino_temp.elf',
    'app.ino.elf-zsk.bin', 'app.ino.map')}
LIMITS.update({'app.ino.bin': 786416, 'app.ino.bin-zsk.bin': 786432})
OUTPUTS = {'build/' + name: limit for name, limit in LIMITS.items()}
OUTPUTS['artifacts/app.ino.bin-zsk.bin'] = 786432
TIMEOUTS = dict(inventory=30, source=60, claim=30, absent=30, artifacts=60,
                layout=120, read=60, postcheck=90)
ALLOCATIONS = {
    '.text': (1, (6,)), '.static_thread_data_area': (1, (2, 3)),
    '.preinit_array': (16, (2, 3)), '.init_array': (14, (2, 3)),
    '.fini_array': (15, (2, 3)), '.rodata': (1, (2,)),
    '.ARM.extab': (1, (2,)), '.ARM': (0x70000001, (2, 130)),
    '.data': (1, (3, 7)), '.bss': (8, (3,)),
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def keys(value, names):
    require(type(value) is dict and set(value) == set(names.split()), 'Unexpected object schema')
    return value


def integer(value):
    require(type(value) is int and value >= 0, 'Expected nonnegative integer')
    return value


def digest(value):
    require(type(value) is str and re.fullmatch('[0-9a-f]{64}', value), 'Invalid SHA256')
    return value


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def unique(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, 'Duplicate JSON key')
        result[key] = value
    return result


def finite(token):
    value = float(token)
    require(math.isfinite(value), 'Nonfinite JSON number')
    return value


def decode(text):
    def reject(token):
        raise ValueError('Nonfinite JSON constant: ' + token)
    try:
        return json.loads(text, object_pairs_hook=unique, parse_float=finite,
                          parse_constant=reject)
    except (TypeError, RecursionError, OverflowError) as error:
        raise ValueError('Malformed JSON') from error


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'),
                      ensure_ascii=True, allow_nan=False).encode('utf-8')


def encoded(raw, compress=False):
    return base64.b64encode(zlib.compress(raw, 9) if compress else raw).decode('ascii')


def decoded(value):
    require(type(value) is str, 'Expected base64 text')
    try:
        raw = base64.b64decode(value, validate=True)
    except (ValueError, UnicodeError) as error:
        raise ValueError('Malformed base64') from error
    require(encoded(raw) == value, 'Noncanonical base64')
    return raw


def safe_path(path, kind):
    require(isinstance(path, Path) and path.is_absolute(), 'Expected absolute Path')
    try:
        require(path == path.resolve(strict=True), 'Noncanonical path')
        for entry in (path, *path.parents):
            info = entry.lstat()
            require(not stat.S_ISLNK(info.st_mode) and
                    not getattr(info, 'st_file_attributes', 0) & 1024, 'Linked local path')
        info = path.stat()
    except OSError as error:
        raise ValueError('Missing or inaccessible local path') from error
    require((stat.S_ISREG if kind == 'file' else stat.S_ISDIR)(info.st_mode),
            'Wrong local path type')


def verify_inputs():
    raw = {}
    for name, expected in PINS.items():
        path = ROOT / name
        require(path.is_relative_to(ROOT), 'Input outside repository')
        safe_path(path, 'file')
        raw[name] = path.read_bytes()
        require(sha(raw[name]) == expected, 'Pinned input changed: ' + name)
    return raw


def guard_nested_policy():
    path = ROOT / 'tools/app_build_policy.py'
    require(sys.dont_write_bytecode, 'Run the scoped probe with python -B')
    require(not os.path.lexists(importlib.util.cache_from_source(str(path))),
            'Current-interpreter common-policy bytecode cache must be absent')
    safe_path(path, 'file')
    require(sha(path.read_bytes()) == PINS['tools/app_build_policy.py'], 'Nested policy source changed')


def load_module(name, relative, raw):
    nested = relative == RAW + 'static_policy.py'
    if nested:
        guard_nested_policy()
    module = types.ModuleType(name)
    module.__file__ = str(ROOT / relative)
    exec(compile(raw[relative], module.__file__, 'exec'), module.__dict__)
    if nested:
        guard_nested_policy()
    return module


def validate_request(compile_only, run_id, receipt_dir, command):
    require(compile_only is True, 'Explicit compile-only required')
    require(type(run_id) is str and re.fullmatch('[0-9a-f]{32}', run_id), 'Invalid run ID')
    require(callable(command), 'A command adapter is required')
    require(isinstance(receipt_dir, Path) and receipt_dir.is_absolute(), 'Invalid receipt path')
    safe_path(receipt_dir.parent, 'directory')
    require(receipt_dir == receipt_dir.absolute() and receipt_dir.name not in ('', '.', '..'),
            'Noncanonical receipt path')
    require(not os.path.lexists(receipt_dir), 'Receipt directory already exists')


def identity(value):
    keys(value, 'user uid gid home sysname release machine boot_id python')
    require(value['user'] == 'arduino' and value['home'] == '/home/arduino', 'Wrong remote account')
    require(integer(value['uid']) > 0, 'Remote root is not accepted')
    integer(value['gid'])
    require(value['sysname'] == 'Linux' and value['machine'] == 'aarch64', 'Wrong remote platform')
    require(type(value['release']) is str and value['release'], 'Missing kernel release')
    require(type(value['boot_id']) is str and re.fullmatch(
        '[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', value['boot_id']), 'Invalid boot ID')
    version = value['python']
    require(type(version) is list and len(version) == 3, 'Wrong Python version shape')
    for item in version:
        integer(item)
    require(tuple(version) >= (3, 9, 0), 'Python is too old')


def resources(value, minimum):
    keys(value, 'available_ram_bytes root_available_bytes tmp_available_bytes')
    for name, amount in value.items():
        integer(amount)
        floor = 512 * 1024**2 if name == 'available_ram_bytes' else 1024**3
        require(not minimum or amount >= floor, 'Insufficient remote resources')


def checked_claim(value, run_id, boot):
    keys(value, 'run_id boot_id directories')
    require(value['run_id'] == run_id and value['boot_id'] == boot, 'Claim identity changed')
    keys(value['directories'], 'run build artifacts')
    for entry in value['directories'].values():
        keys(entry, 'device inode')
        for item in entry.values():
            integer(item)


def checked_file(record, limit):
    keys(record, 'state identity sha256')
    require(record['state'] == 'regular', 'Artifact is not a nonempty regular file')
    keys(record['identity'], 'device inode bytes mtime_ns ctime_ns')
    for item in record['identity'].values():
        integer(item)
    require(0 < record['identity']['bytes'] <= limit, 'Artifact exceeds bound')
    digest(record['sha256'])


def checked_files(value):
    require(type(value) is dict and value.keys() == OUTPUTS.keys(), 'Wrong artifact set')
    for name, record in value.items():
        checked_file(record, OUTPUTS[name])
    a, b = value['build/app.ino.bin-zsk.bin'], value['artifacts/app.ino.bin-zsk.bin']
    require((a['sha256'], a['identity']['bytes']) == (b['sha256'], b['identity']['bytes']),
            'Export differs from canonical flat package')


def artifact_identities(files):
    return {name: {'bytes': files['build/' + name]['identity']['bytes'],
                   'sha256': files['build/' + name]['sha256']} for name in LIMITS}


def interval(value, start, limit):
    keys(value, 'start end remaining')
    for item in value.values():
        integer(item)
    require(value['start'] == start and start <= value['end'] <= limit and
            value['remaining'] == limit - value['end'], 'Invalid layout interval')


def section_rows(rows, flash_end, ram_end):
    require(type(rows) is list and len(rows) <= len(ALLOCATIONS), 'Invalid section list')
    names, end = set(), 0
    for row in rows:
        keys(row, 'name type flags address size alignment load_address')
        name = row['name']
        require(type(name) is str and name in ALLOCATIONS and name not in names, 'Invalid section name')
        names.add(name)
        for key in ('type', 'flags', 'address', 'size', 'alignment'):
            integer(row[key])
        kind, flags = ALLOCATIONS[name]
        require(row['type'] == kind and row['flags'] in flags, 'Invalid section type/flags')
        align = row['alignment']
        require(align == 0 or align & (align - 1) == 0, 'Invalid alignment')
        require(not align or row['address'] % align == 0, 'Unaligned section')
        require(row['size'] > 0 and row['address'] >= end, 'Overlapping or empty section')
        end = row['address'] + row['size']
        in_ram = name in ('.data', '.bss')
        low, high = (0x20013890, ram_end) if in_ram else (0x08100010, flash_end)
        require(low <= row['address'] < end <= high, 'Section outside region')
        if name == '.bss':
            require(row['load_address'] is None, 'BSS has a load address')
        else:
            load = integer(row['load_address'])
            require(0x08100010 <= load < load + row['size'] <= flash_end, 'Load outside flash')
            require(in_ram or load == row['address'], 'Flash section has different LMA')
    require({'.text', '.data', '.bss'} <= names, 'Required section missing')


def checked_layout(report, files):
    keys(report, 'status entry flash ram data_copy bss_zero sections weak_undefined artifacts')
    require(report['status'] == 'STATIC_LAYOUT_PACKAGE_PASS' and
            integer(report['entry']) == 0x08100011, 'Invalid structural status/entry')
    interval(report['flash'], 0x08100010, 0x081C0000)
    interval(report['ram'], 0x20013890, 0x20053890)
    data, bss = report['data_copy'], report['bss_zero']
    keys(data, 'source destination bytes')
    keys(bss, 'start end bytes')
    for item in [*data.values(), *bss.values()]:
        integer(item)
    require(0x08100010 <= data['source'] <= data['source'] + data['bytes'] <= report['flash']['end'],
            'Invalid initialization source')
    require(0x20013890 <= data['destination'] <= data['destination'] + data['bytes'] <= bss['start'],
            'Invalid initialization destination')
    require(0x20013890 <= bss['start'] <= bss['end'] <= report['ram']['end'] and
            bss['bytes'] == bss['end'] - bss['start'], 'Invalid zero range')
    section_rows(report['sections'], report['flash']['end'], report['ram']['end'])
    weak = report['weak_undefined']
    require(type(weak) is list and all(type(x) is str and 0 < len(x) <= 4096 for x in weak),
            'Invalid weak-symbol list')
    require(weak == sorted(set(weak)), 'Weak-symbol list is not unique/sorted')
    require(type(report['artifacts']) is dict and report['artifacts'].keys() == LIMITS.keys(),
            'Wrong layout artifact set')
    for item in report['artifacts'].values():
        keys(item, 'bytes sha256')
        integer(item['bytes'])
        digest(item['sha256'])
    require(report['artifacts'] == artifact_identities(files), 'Layout artifact identity drift')


def utc():
    return datetime.now(timezone.utc).isoformat()


def error_record(error):
    return {'class': type(error).__name__, 'message': str(error)}


def output_record(value):
    if isinstance(value, bytes):
        return {'encoding': 'base64', 'data': encoded(value)}
    if value is None or type(value) is str:
        return value
    return {'encoding': 'python-type', 'type': type(value).__name__}


def write_json(path, value, exclusive=False):
    with path.open('x' if exclusive else 'w', encoding='utf-8', newline='\n') as stream:
        json.dump(value, stream, ensure_ascii=True, allow_nan=False, separators=(',', ':'))
        stream.write('\n')


class Probe:
    def __init__(self, run_id, receipt_dir, command, raw):
        self.run_id, self.receipt_dir, self.command, self.raw = run_id, receipt_dir, command, raw
        self.remote_root = REMOTE + '/_app_builds/static-app-probe-v1/' + SOURCE + '/bench-default/' + run_id
        self.build, self.export = self.remote_root + '/build', self.remote_root + '/artifacts'
        self.phase, self.sequence = 'local_admission', 0
        self.query_attempts, self.compile_attempts, self.terminal = 0, 0, False
        self.postcheck_errors = []
        self.first_identity, self.claim, self.files = None, None, None
        self.board = load_module('static_board', 'tools/board_tool.py', raw)
        self.common = load_module('static_common', 'tools/app_build_policy.py', raw)
        self.policy = load_module('static_fixed_policy', RAW + 'static_policy.py', raw)
        self.stage_check = load_module('static_reuse', 'state/analysis/P7_default_qualification_raw/reuse_stage.py', raw)
        base = 'state/analysis/P7_default_qualification_raw/'
        self.source_manifest = decode(raw[base + 'working_source_manifest.json'])
        self.stage_raw = raw[base + 'checked_stage_manifest.json']
        self.stage_manifest = decode(self.stage_raw)
        self.stage, self.stage_receipt = self.stage_check.verifiedStage(
            self.board, 'app', self.source_manifest, self.stage_manifest)
        self.stage_files = {name: {'bytes': (self.stage / name).stat().st_size, 'sha256': value}
                            for name, value in self.stage_manifest['files'].items()}
        self.pins = self.common.installed_pins(DATA)
        for template, value in decode(raw[RAW + 'additional_pins.json']).items():
            name = template.replace('@DATA_DIR@', DATA)
            require(name not in self.pins, 'Duplicate dependency pin')
            self.pins[name] = digest(value)
        require(len(self.pins) == 26, 'Wrong installed dependency count')
        boot = raw[RAW + 'static_bootstrap.txt'].decode('utf-8')
        require(boot.count('@HELPER_SHA256@') == 1, 'Wrong bootstrap template')
        self.boot = boot.replace('@HELPER_SHA256@', PINS[RAW + 'static_remote.py'])
        self.helper_encoded = encoded(raw[RAW + 'static_remote.py'], True)

    def dispatch(self, board, argv, *, capture=True, timeout=60):
        require(board == BOARD and capture is True, 'Wrong transport identity')
        line = subprocess.list2cmdline([ADB, '-s', BOARD, 'shell', '-T', shlex.join(argv)])
        require(len(line.encode('utf-16-le')) // 2 + 1 <= 30000, 'Windows command limit exceeded')
        self.sequence += 1
        path = self.receipt_dir / f'{self.sequence:04d}.json'
        record = dict(sequence=self.sequence, phase=self.phase, board=board, argv=argv,
                      timeout=timeout, start_utc=utc())
        write_json(path, record, exclusive=True)
        if self.phase == 'query':
            self.query_attempts += 1
        if self.phase == 'compile':
            self.compile_attempts += 1
        try:
            result = self.command(board, argv, capture=capture, timeout=timeout)
        except Exception as error:
            code = error.returncode if isinstance(error, subprocess.CalledProcessError) else None
            record.update(end_utc=utc(), returncode=code, error=error_record(error),
                          stdout=output_record(getattr(error, 'stdout', None)),
                          stderr=output_record(getattr(error, 'stderr', None)))
            try:
                write_json(path, record)
            except Exception:
                # A partial planned receipt cannot justify replacing the transport failure.
                pass
            raise
        code = getattr(result, 'returncode', None)
        valid = (isinstance(result, subprocess.CompletedProcess) and type(code) is int and
                 type(result.stdout) is str and type(result.stderr) is str)
        malformed = None if valid else ValueError('Malformed command result')
        if self.phase == 'compile' and valid and code == 0:
            self.terminal = True
        record.update(end_utc=utc(), returncode=code if type(code) is int else None,
                      error=None if valid else error_record(malformed),
                      stdout=output_record(getattr(result, 'stdout', None)),
                      stderr=output_record(getattr(result, 'stderr', None)))
        write_json(path, record)
        if malformed:
            raise malformed
        if code != 0:
            raise subprocess.CalledProcessError(code, argv, result.stdout, result.stderr)
        return result

    def helper(self, action, *args):
        self.phase = action if action != 'postcheck' else 'remote_postcheck'
        argv = ['python3', '-I', '-B', '-c', self.boot, self.helper_encoded,
                action, self.run_id, *args]
        result = self.dispatch(BOARD, argv, timeout=TIMEOUTS[action])
        require(result.stderr == '', 'Unexpected helper stderr')
        require(action != 'layout' or len(result.stdout.encode('utf-8')) <= 1048576, 'Oversize layout report')
        reply = keys(decode(result.stdout), 'schema action run_id ok data error')
        require(reply['schema'] == 'static-remote-v1' and reply['action'] == action and
                reply['run_id'] == self.run_id and reply['ok'] is True and reply['error'] is None,
                'Invalid helper response identity/status')
        require(type(reply['data']) is dict, 'Invalid helper data')
        return reply['data']

    def cli(self, label, argv, timeout=60):
        self.phase = label
        return self.dispatch(BOARD, argv, timeout=timeout).stdout

    def check_inventory(self, data, minimum=True):
        identity(data['identity'])
        resources(data['resources'], minimum)
        require(type(data['compiler_candidates']) is list and not data['compiler_candidates'], 'Compiler already active')
        if self.first_identity is None:
            self.first_identity = data['identity']
        require(data['identity'] == self.first_identity, 'Remote identity changed')

    def inventory(self):
        data = self.helper('inventory')
        keys(data, 'identity resources compiler_candidates')
        self.check_inventory(data)

    def check_source(self, data):
        keys(data, 'path source_sha256 file_count total_bytes files')
        require(data['path'] == SKETCH and data['source_sha256'] == SOURCE and
                integer(data['file_count']) == 102, 'Wrong source identity')
        require(type(data['files']) is dict and data['files'].keys() == self.stage_files.keys(), 'Wrong source set')
        for item in data['files'].values():
            keys(item, 'bytes sha256')
            integer(item['bytes'])
            digest(item['sha256'])
        require(data['files'] == self.stage_files and integer(data['total_bytes']) ==
                sum(x['bytes'] for x in self.stage_files.values()), 'Remote source drift')

    def source(self):
        self.check_source(self.helper('source', encoded(self.stage_raw, True)))

    def overrides(self):
        self.phase = 'overrides'
        self.common.check_overrides(self.dispatch, BOARD, DATA, USER, SKETCH)

    def installed_pins(self):
        self.phase = 'installed_pins'
        self.common.verify_hashes(self.dispatch, BOARD, self.pins)

    def local_pins(self):
        verify_inputs()

    def local_stage(self):
        self.stage_check.verifiedStage(self.board, 'app', self.source_manifest, self.stage_manifest)

    def check_claim(self, value):
        checked_claim(value, self.run_id, self.first_identity['boot_id'])
        require(self.claim is None or value == self.claim, 'Claim directory replacement')

    def claim_remote(self):
        data = self.helper('claim')
        keys(data, 'claim created')
        self.check_claim(data['claim'])
        created = data['created']
        allowed = [REMOTE + '/_app_builds']
        for part in ('static-app-probe-v1', SOURCE, 'bench-default', self.run_id, 'build'):
            allowed.append(allowed[-1] + '/' + part)
        allowed.append(self.export)
        require(type(created) is list and all(type(x) is str and x in allowed for x in created), 'Invalid created paths')
        require(created == [x for x in allowed if x in created] and
                created[-3:] == [self.remote_root, self.build, self.export], 'Invalid claim creation order')
        self.claim = data['claim']

    def claim_token(self):
        return encoded(canonical(self.claim))

    def absent(self):
        data = self.helper('absent', self.claim_token())
        keys(data, 'claim outputs')
        self.check_claim(data['claim'])
        require(data['outputs'] == {name: 'absent' for name in OUTPUTS}, 'Stale outputs detected')

    def compiler_argv(self, query=False):
        flags = '-DMATCH=0 -DMOTORS_ALLOWED=0'
        argv = ['arduino-cli', 'compile', '--jobs', '1', '--json', '--fqbn',
                'arduino:zephyr:unoq:link_mode=static', '--build-path', self.build,
                '--output-dir', self.export, '--build-property', 'compiler.cpp.extra_flags=' + flags,
                '--build-property', 'compiler.c.extra_flags=' + flags, '--build-property',
                'build.library_discovery_phase_flag=-DARDUINO_LIBRARY_DISCOVERY_PHASE=0']
        return [*argv, *(['--show-properties=expanded'] if query else []), SKETCH]

    def prepare(self):
        self.inventory()
        self.common.validate_cli(self.cli('version', ['arduino-cli', 'version']))
        core = self.cli('core', ['arduino-cli', 'core', 'list'])
        rows = [x.split() for x in core.splitlines() if x.split() and x.split()[0] == 'arduino:zephyr']
        require(len(rows) == 1 and len(rows[0]) >= 2 and rows[0][1] == '1.0.0', 'Wrong or duplicate installed core')
        for name, expected in (('data', DATA), ('user', USER)):
            text = self.cli(name, ['arduino-cli', 'config', 'get', 'directories.' + name, '--json'])
            require(self.common.resolved_directory(text) == expected, 'Wrong CLI directory')
        self.source()
        self.overrides()
        self.installed_pins()
        self.claim_remote()
        self.absent()
        query = self.cli('query', self.compiler_argv(True), 300)
        self.policy.validate_preflight(query, build_path=self.build, data_dir=DATA)
        self.phase = 'local_pins'
        self.local_pins()
        self.phase = 'local_stage'
        self.local_stage()
        self.source()
        self.overrides()
        self.installed_pins()
        self.inventory()
        self.absent()

    def remote_postcheck(self):
        data = self.helper('postcheck', self.claim_token(), encoded(self.stage_raw, True))
        keys(data, 'claim identity resources compiler_candidates source files')
        self.check_claim(data['claim'])
        self.check_inventory(data, minimum=False)
        self.check_source(data['source'])
        checked_files(data['files'])
        require(self.files is None or data['files'] == self.files, 'Artifact drift after collection')
        if self.files is None:
            self.files = data['files']

    def postchecks(self, local_only=False):
        first = None
        names = ('local_pins', 'local_stage') if local_only else (
            'local_pins', 'local_stage', 'remote_postcheck', 'installed_pins', 'overrides')
        for name in names:
            self.phase = name
            try:
                getattr(self, name)()
            except Exception as error:
                first = first or (error, self.phase)
                self.postcheck_errors.append(dict(check=name, **error_record(error)))
        return first

    def collect(self):
        data = self.helper('artifacts', self.claim_token())
        keys(data, 'claim files')
        self.check_claim(data['claim'])
        checked_files(data['files'])
        require(data['files'] == self.files, 'Artifact metadata changed')
        data = self.helper('layout', self.claim_token(), encoded(self.raw[RAW + 'static_artifacts.py'], True))
        keys(data, 'claim validator_sha256 files report')
        self.check_claim(data['claim'])
        require(data['validator_sha256'] == PINS[RAW + 'static_artifacts.py'], 'Wrong structural validator')
        checked_files(data['files'])
        require(data['files'] == self.files, 'Layout file identity changed')
        checked_layout(data['report'], self.files)
        return data['report'], self.read_elf()

    def read_elf(self):
        record = self.files['build/app.ino.elf']
        size, parts, offset = record['identity']['bytes'], [], 0
        while offset < size:
            length = min(262144, size - offset)
            data = self.helper('read', self.claim_token(), 'app.ino.elf', str(offset), str(length), record['sha256'])
            keys(data, 'claim name file offset length chunk_sha256 base64')
            self.check_claim(data['claim'])
            checked_file(data['file'], LIMITS['app.ino.elf'])
            require(data['name'] == 'app.ino.elf' and data['file'] == record and
                    integer(data['offset']) == offset and integer(data['length']) == length, 'Wrong ELF chunk identity')
            chunk = decoded(data['base64'])
            require(len(chunk) == length and sha(chunk) == digest(data['chunk_sha256']), 'Corrupt ELF chunk')
            parts.append(chunk)
            offset += length
        raw = b''.join(parts)
        require(len(raw) == size and sha(raw) == record['sha256'], 'Incomplete ELF collection')
        return raw

    def execute(self):
        self.prepare()
        failure = None
        try:
            text = self.cli('compile', self.compiler_argv(), 1800)
            self.policy.validate_compile_result(text, build_path=self.build, data_dir=DATA)
        except Exception as error:
            if not self.compile_attempts:
                raise
            failure = (error, self.phase)
        post = self.postchecks(local_only=not self.terminal)
        failure = failure or post
        if failure:
            self.phase = failure[1]
            raise failure[0]
        try:
            layout, raw = self.collect()
        except Exception as error:
            failure = (error, self.phase)
        post = self.postchecks()
        failure = failure or post
        if failure:
            self.phase = failure[1]
            raise failure[0]
        self.phase = 'result_write'
        path = self.receipt_dir / 'app.ino.elf'
        with path.open('xb') as stream:
            stream.write(raw)
        return dict(status='STATIC_COMPILE_COLLECTED', source_sha256=SOURCE,
                    run_id=self.run_id, receipt_dir=str(self.receipt_dir), remote_root=self.remote_root,
                    build_path=self.build, artifact_path=self.export, query_attempts=self.query_attempts,
                    compile_attempts=self.compile_attempts, layout=layout,
                    artifacts=artifact_identities(self.files),
                    final_elf=dict(path=str(path), bytes=len(raw), sha256=sha(raw)))


def run_probe(*, compile_only, run_id, receipt_dir, command):
    validate_request(compile_only, run_id, receipt_dir, command)
    probe = Probe(run_id, receipt_dir, command, verify_inputs())
    receipt_dir.mkdir(mode=0o700)
    try:
        write_json(receipt_dir / 'inputs.json', dict(pins=PINS, stage=probe.stage_receipt,
                   runner_sha256=sha(Path(__file__).read_bytes())), exclusive=True)
        result = probe.execute()
        write_json(receipt_dir / 'result.json', result, exclusive=True)
        return result
    except Exception as error:
        unknown = probe.compile_attempts > 0 and not probe.terminal
        result = dict(status='COMPILE_OUTCOME_UNKNOWN' if unknown else 'FAILED', phase=probe.phase,
                      query_attempts=probe.query_attempts, compile_attempts=probe.compile_attempts,
                      error=error_record(error), postcheck_errors=probe.postcheck_errors)
        try:
            write_json(receipt_dir / 'result.json', result, exclusive=True)
        except OSError:
            # A failing evidence destination must not replace the original operation error.
            pass
        raise


def parse_request(argv):
    parser = argparse.ArgumentParser(description='One reviewed static/M0 compile-only probe', allow_abbrev=False)
    parser.add_argument('--compile-only', action='store_true', required=True)
    parser.add_argument('--run-id', required=True)
    if argv in (['--help'], ['-h']):
        return parser.parse_args(argv)
    if (type(argv) is not list or len(argv) != 3 or argv[:2] != ['--compile-only', '--run-id'] or
            type(argv[2]) is not str or not re.fullmatch('[0-9a-f]{32}', argv[2])):
        parser.error('use exactly --compile-only --run-id <32 lowercase hexadecimal digits>')
    return parser.parse_args(argv)


def main(argv=None):
    request = parse_request(sys.argv[1:] if argv is None else argv)
    try:
        require(os.environ.get('SUMO_TRANSPORT') == 'adb' and os.environ.get('SUMO_ADB_SERIAL') == BOARD,
                'Exact existing ADB configuration required')
        configured = os.environ.get('SUMO_ADB_EXECUTABLE', '')
        require(configured.replace('\\', '/').casefold() == ADB.casefold(), 'Wrong ADB path')
        safe_path(Path(configured), 'file')
        require(sha(Path(configured).read_bytes()) == ADB_SHA, 'ADB executable changed')
        raw = verify_inputs()
        board = load_module('static_launch_board', 'tools/board_tool.py', raw)
        result = run_probe(compile_only=request.compile_only, run_id=request.run_id,
                           receipt_dir=ROOT / RAW / 'runs' / request.run_id, command=board.remote)
        print(json.dumps(result, separators=(',', ':')))
        return 0
    except Exception as error:
        print(type(error).__name__ + ': ' + str(error), file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
