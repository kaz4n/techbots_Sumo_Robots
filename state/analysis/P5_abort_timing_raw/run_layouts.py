# Compares D135 host type size/alignment with the committed pre-D135 baseline.
# Keeps legacy compatibility evidence separate from independent P5 measurements.
# Deferred header-only probes run serially with frozen inputs and owned scratch cleanup.
from datetime import datetime, timezone
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BASELINE = 'd6a8319e'
FREEZE = HERE / 'freeze.json'
TYPES = (
    ('Direct', 'openers::Direct'), ('Flank', 'openers::Flank'), ('Wait', 'openers::Wait'),
    ('Result', 'openers::Result'), ('FlankResult', 'openers::FlankResult'),
    ('WaitResult', 'openers::WaitResult'), ('RobotInput', 'fsm::RobotInput'),
    ('RobotResult', 'fsm::RobotResult'), ('Robot', 'fsm::Robot'),
    ('Transaction', 'app::Transaction'), ('Runtime', 'app::Runtime'),
    ('EventBatch', 'logframe::EventBatch'),
)
OLD_FLAGS = ('SUMOX_B4_STAND', 'SUMOX_P3_DRIVE_TEST', 'SUMOX_P3_TURN_TRIAL',
             'SUMOX_P3_STOP_TRIAL', 'SUMOX_P4_REACTIVE', 'SUMOX_TIMING_EVIDENCE')
PROBE = '''#include "app/runtime.h"
#include <cstdio>
static_assert(fsm::RobotResult::REACTIVE_PROFILE == bool(EXPECTED_REACTIVE));
static_assert(fsm::RobotResult::TIMING_EVIDENCE_PROFILE == bool(EXPECTED_TIMING));
#if defined(SUMOX_P5_ABORT_TIMING)
static_assert(SUMOX_P5_ABORT_TIMING == EXPECTED_P5);
static_assert(fsm::RobotResult::OPENER_TIMING_PROFILE == bool(EXPECTED_P5));
#else
static_assert(EXPECTED_P5 == 0);
#endif
int main() {
''' + ''.join('    std::printf("' + label + ' %zu %zu\\n", sizeof(' + name +
              '), alignof(' + name + '));\n' for label, name in TYPES) + '}\n'


def now():
    return datetime.now(timezone.utc).isoformat()


def digest(data):
    return hashlib.sha256(data).hexdigest()


def file_hash(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def contained(base, path):
    resolved = path.resolve()
    if not resolved.is_relative_to(base.resolve()) or resolved == base.resolve():
        raise ValueError('Path escapes required directory: ' + str(path))
    return resolved


def source_inventory(source):
    inventory = {}
    for path in sorted(source.rglob('*')):
        if path.is_symlink():
            raise ValueError('Source symlink is outside this exact-file probe: ' + str(path))
        if path.is_file():
            contained(source, path)
            inventory[path.relative_to(source.parent).as_posix()] = file_hash(path)
    return inventory


def inventory_hash(inventory):
    return digest(json.dumps(inventory, sort_keys=True, separators=(',', ':')).encode())


def verify_freeze(freeze):
    for name, expected in freeze.items():
        path = contained(ROOT, ROOT / name)
        if not path.is_file() or file_hash(path) != expected:
            raise ValueError('Frozen input mismatch: ' + name)
    return len(freeze)


def run(argv, record, log, environment, binary_stdout=False):
    entry = dict(argv=list(map(str, argv)), cwd=str(ROOT), started_utc=now())
    record['commands'].append(entry)
    log.write(('ARGV ' + json.dumps(entry['argv']) + '\n').encode())
    log.flush()
    try:
        result = subprocess.run(entry['argv'], cwd=ROOT, env=environment,
                                capture_output=True, check=False, timeout=60)
    except subprocess.TimeoutExpired as error:
        entry.update(returncode=124, ended_utc=now(), timeout_seconds=60)
        if error.stdout and not binary_stdout:
            log.write(error.stdout)
        if error.stderr:
            log.write(error.stderr)
        raise RuntimeError('Timed out: ' + repr(entry['argv'])) from error
    entry.update(returncode=result.returncode, ended_utc=now(),
                 stdout_sha256=digest(result.stdout), stderr_sha256=digest(result.stderr),
                 stdout_bytes=len(result.stdout), stderr_bytes=len(result.stderr))
    if not binary_stdout:
        log.write(result.stdout)
    log.write(result.stderr)
    log.flush()
    if result.returncode:
        raise RuntimeError('Command failed: ' + repr(entry['argv']))
    return result.stdout


def extract_src(data, destination):
    seen = set()
    with tarfile.open(fileobj=io.BytesIO(data), mode='r:') as archive:
        members = archive.getmembers()
        if not members:
            raise ValueError('Empty baseline archive')
        for member in members:
            path = PurePosixPath(member.name)
            if (path.is_absolute() or '..' in path.parts or not path.parts or
                    path.parts[0] != 'src' or not (member.isdir() or member.isfile()) or
                    '\\' in member.name or member.name in seen):
                raise ValueError('Unsafe or duplicate archive member: ' + member.name)
            seen.add(member.name)
            target = contained(destination, destination.joinpath(*path.parts))
            if member.isdir():
                target.mkdir(parents=True, exist_ok=True)
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                stream = archive.extractfile(member)
                if stream is None:
                    raise ValueError('Missing archive payload: ' + member.name)
                with stream, target.open('xb') as output:
                    shutil.copyfileobj(stream, output)


def copy_current(current, expected):
    for name, sha in expected.items():
        source = contained(ROOT / 'src', ROOT / name)
        target = contained(current, current / name)
        target.parent.mkdir(parents=True, exist_ok=True)
        with source.open('rb') as input_file, target.open('xb') as output:
            shutil.copyfileobj(input_file, output)
        if file_hash(target) != sha:
            raise ValueError('Source changed while copying: ' + name)


def profile_flags(profile, motors):
    flags = dict(MATCH=0, MOTORS_ALLOWED=motors)
    flags.update({name: 0 for name in OLD_FLAGS})
    flags['SUMOX_P4_REACTIVE'] = int(profile in ('reactive', 'timing'))
    flags['SUMOX_TIMING_EVIDENCE'] = int(profile == 'timing')
    if profile == 'p5':
        flags['SUMOX_P5_ABORT_TIMING'] = 1
    flags.update(EXPECTED_REACTIVE=flags['SUMOX_P4_REACTIVE'],
                 EXPECTED_TIMING=flags['SUMOX_TIMING_EVIDENCE'], EXPECTED_P5=int(profile == 'p5'))
    return ['-D' + name + '=' + str(value) for name, value in flags.items()]


def parse_layout(raw):
    rows = raw.decode('ascii').splitlines()
    if len(rows) != len(TYPES):
        raise ValueError('Unexpected layout row count')
    layout = {}
    for row, (expected, _) in zip(rows, TYPES):
        fields = row.split()
        if len(fields) != 3 or fields[0] != expected:
            raise ValueError('Unexpected layout row: ' + row)
        size, alignment = map(int, fields[1:])
        if size <= 0 or alignment <= 0 or size % alignment:
            raise ValueError('Invalid size/alignment: ' + row)
        layout[expected] = dict(size=size, alignment=alignment)
    return layout


def measure(source, profile, motors, scratch, probe, compiler, record, log, environment):
    key = source.name + '_' + profile + '_m' + str(motors)
    binary = contained(scratch, scratch / key)
    argv = [compiler, '-std=c++17', '-Wall', '-Wextra', '-Wpedantic', '-Werror',
            '-fno-exceptions', '-fno-rtti', *profile_flags(profile, motors),
            '-I', str(source / 'src'), str(probe), '-o', str(binary)]
    run(argv, record, log, environment)
    record['binary_sha256'][key] = file_hash(binary)
    record['layouts'][key] = parse_layout(run([str(binary)], record, log, environment))


def compare(record):
    for profile in ('default', 'reactive', 'timing'):
        for motors in (0, 1):
            before = record['layouts']['baseline_' + profile + '_m' + str(motors)]
            after = record['layouts']['current_' + profile + '_m' + str(motors)]
            differences = {name: dict(baseline=before[name], current=after[name])
                           for name, _ in TYPES if before[name] != after[name]}
            record['comparisons'][profile + '_m' + str(motors)] = dict(
                equal=not differences, compared_types=len(TYPES), differences=differences)
    record['p5_measurements'] = {str(m): record['layouts']['current_p5_m' + str(m)] for m in (0, 1)}
    if len(record['layouts']) != 14 or any(not row['equal'] for row in record['comparisons'].values()):
        raise ValueError('Legacy size/alignment regression or incomplete layout matrix')


def measure_all(scratch, expected, record, log, environment):
    baseline, current = scratch / 'baseline', scratch / 'current'
    baseline.mkdir()
    current.mkdir()
    git = ['git', '-c', 'safe.directory=' + str(ROOT)]
    revision = run(git + ['rev-parse', '--verify', BASELINE + '^{commit}'], record, log, environment).decode().strip()
    if not re.fullmatch(r'[0-9a-f]{40}', revision) or not revision.startswith(BASELINE):
        raise ValueError('Baseline revision did not resolve to the specified commit')
    record['baseline_commit'] = revision
    record['current_head'] = run(git + ['rev-parse', 'HEAD'], record, log, environment).decode().strip()
    archive = run(git + ['archive', '--format=tar', revision, 'src'], record, log, environment, True)
    record['baseline_archive_sha256'] = digest(archive)
    extract_src(archive, baseline)
    copy_current(current, expected)
    record['baseline_sources_before'] = source_inventory(baseline / 'src')
    copied = source_inventory(current / 'src')
    record['current_copy_before_sha256'] = inventory_hash(copied)
    if copied != expected:
        raise ValueError('Copied current source differs from frozen source')
    probe = scratch / 'layout_probe.cc'
    probe.write_text(PROBE, encoding='ascii')
    compiler = shutil.which('g++')
    if compiler is None:
        raise ValueError('WSL/Linux g++ is required')
    record['compiler_version'] = run([compiler, '--version'], record, log, environment).decode().splitlines()[0]
    for profile in ('default', 'reactive', 'timing'):
        for motors in (0, 1):
            for source in (baseline, current):
                measure(source, profile, motors, scratch, probe, compiler, record, log, environment)
    for motors in (0, 1):
        measure(current, 'p5', motors, scratch, probe, compiler, record, log, environment)
    compare(record)


def check_copies(scratch, expected, record):
    for name in ('baseline', 'current'):
        source = scratch / name / 'src'
        if not source.is_dir():
            continue
        inventory = source_inventory(source)
        reference = expected if name == 'current' else record.get('baseline_sources_before')
        record[name + '_copy_after_sha256'] = inventory_hash(inventory)
        record[name + '_copy_unchanged'] = reference is not None and inventory == reference
        if reference is not None and inventory != reference:
            raise ValueError('Probe modified copied source inputs: ' + name)


def execute(record, log, freeze, expected):
    scratch = None
    try:
        with tempfile.TemporaryDirectory(prefix='sumox_d135_layout_', dir='/dev/shm') as temporary:
            scratch = Path(temporary).resolve()
            if scratch.parent != Path('/dev/shm').resolve():
                raise ValueError('Unexpected scratch parent')
            record['scratch_path'] = str(scratch)
            environment = os.environ.copy()
            for key in ('CPATH', 'CPLUS_INCLUDE_PATH', 'C_INCLUDE_PATH', 'LIBRARY_PATH',
                        'GCC_EXEC_PREFIX', 'COMPILER_PATH'):
                environment.pop(key, None)
            environment['TMPDIR'] = str(scratch)
            try:
                measure_all(scratch, expected, record, log, environment)
            finally:
                record['scratch_bytes_before_cleanup'] = sum(path.stat().st_size
                    for path in scratch.rglob('*') if path.is_file())
                check_copies(scratch, expected, record)
    finally:
        record['scratch_released'] = scratch is not None and not scratch.exists()
        record['input_freeze_sha256_after'] = file_hash(FREEZE)
        if record['input_freeze_sha256_after'] != record['input_freeze_sha256']:
            raise ValueError('Input freeze changed during probe')
        record['frozen_inputs_verified_after'] = verify_freeze(freeze)
        current = source_inventory(ROOT / 'src')
        record['current_sources_after_sha256'] = inventory_hash(current)
        record['source_inputs_unchanged'] = current == expected
        if not record['source_inputs_unchanged'] or not record['scratch_released']:
            raise ValueError('Source verification or scratch cleanup failed')


def main():
    if len(sys.argv) != 2 or not re.fullmatch(r'[a-z][a-z0-9_]*', sys.argv[1]):
        raise SystemExit('Usage: TMPDIR=/dev/shm python3 run_layouts.py <new_label>')
    label = sys.argv[1]
    report_path, log_path = HERE / (label + '.json'), HERE / (label + '.txt')
    if report_path.exists() or log_path.exists():
        raise SystemExit('Refusing to overwrite existing layout evidence')
    record = dict(label=label, started_utc=now(), baseline_ref=BASELINE, commands=[], layouts={},
                  comparisons={}, binary_sha256={}, hardware_access=False, production_linked=False,
                  runner_sha256=file_hash(Path(__file__)), probe_sha256=digest(PROBE.encode('ascii')),
                  scope='Host sizeof/alignof only; no offsets, ABI calling convention, native fit or WCET claim',
                  p5_claim='Independent measurements only; no baseline equivalence required')
    code = 1
    with log_path.open('xb') as log:
        try:
            if sys.platform != 'linux' or not Path('/dev/shm').is_dir():
                raise ValueError('This runner requires Linux/WSL with /dev/shm')
            record['scratch_free_bytes_before'] = shutil.disk_usage('/dev/shm').free
            record['output_free_bytes_before'] = shutil.disk_usage(HERE).free
            freeze = json.loads(FREEZE.read_text())
            record['input_freeze_sha256'] = file_hash(FREEZE)
            record['frozen_inputs_verified_before'] = verify_freeze(freeze)
            expected = {name: sha for name, sha in freeze.items() if name.startswith('src/')}
            record['current_sources_before'] = source_inventory(ROOT / 'src')
            record['current_sources_before_sha256'] = inventory_hash(record['current_sources_before'])
            if not expected or record['current_sources_before'] != expected:
                raise ValueError('Frozen source inventory is incomplete or mismatched')
            execute(record, log, freeze, expected)
            code = 0
        except Exception as error:
            record['error'] = repr(error)
            log.write((repr(error) + '\n').encode())
    record.update(returncode=code, ended_utc=now(), log_sha256=file_hash(log_path))
    with report_path.open('x', encoding='utf-8') as output:
        json.dump(record, output, indent=2)
        output.write('\n')
    print(json.dumps(dict(returncode=code, comparisons=record['comparisons'],
                         p5_measurements=record.get('p5_measurements'), error=record.get('error'))))
    return code


if __name__ == '__main__':
    sys.exit(main())
