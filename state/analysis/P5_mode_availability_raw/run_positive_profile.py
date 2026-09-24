"""Run the supplemental D131 positive20/configured ASan+UBSan host profile.
Keep positive D131 timing coverage separate from the complete D129 zero profile.
Retain frozen-source receipts and release exclusively owned temporary builds.
"""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import traceback


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
DIRECTORIES = ('src', 'tests', 'host', 'bench')
TARGETS = tuple(f'{kind}_m{motor}_tests'
                for kind in ('push_through', 'timing_evidence') for motor in (0, 1))
REPLACEMENTS = {
    'EDGE_PUSH_THROUGH_MS = 0U': 'EDGE_PUSH_THROUGH_MS = 20U',
    'BUTTON_WINDOWS_CONFIGURED = 0U': 'BUTTON_WINDOWS_CONFIGURED = 1U',
    'BUTTON_LOW_RAW[4] = {0U, 0U, 0U, 0U}':
        'BUTTON_LOW_RAW[4] = {0U, 900U, 1900U, 2900U}',
    'BUTTON_HIGH_RAW[4] = {0U, 0U, 0U, 0U}':
        'BUTTON_HIGH_RAW[4] = {100U, 1100U, 2100U, 3100U}',
}
CASE_SUMMARY = (r'\[doctest\] test cases:\s*(\d+)\s*\|\s*(\d+) passed'
                r'\s*\|\s*(\d+) failed\s*\|\s*(\d+) skipped')


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def verify_source(freeze):
    for name, expected in freeze.items():
        path = ROOT / name
        if not path.is_file() or digest(path) != expected:
            raise ValueError(f'frozen source mismatch: {name}')


def source_identity(source):
    aggregate = hashlib.sha256()
    count = 0
    for path in sorted(source.rglob('*')):
        if not path.is_file():
            continue
        name = path.relative_to(source).as_posix()
        aggregate.update(f'{name}\0{digest(path)}\n'.encode('utf-8'))
        count += 1
    return {'files': count, 'sha256': aggregate.hexdigest(),
            'format': 'sorted relative POSIX path + NUL + SHA256 + LF'}


def make_fixture(scratch, freeze, record):
    source = scratch / 'fixture'
    for directory in DIRECTORIES:
        shutil.copytree(ROOT / directory, source / directory,
                        ignore=shutil.ignore_patterns('__pycache__'))
    for name, expected in freeze.items():
        if name.split('/')[0] in DIRECTORIES and digest(source / name) != expected:
            raise ValueError(f'copied source mismatch: {name}')
    record['copied_source_before_substitutions'] = source_identity(source)
    config = source / 'src/config.h'
    text = config.read_text(encoding='utf-8')
    for declaration in ('MODE_ARC_ENABLED = 1U', 'MODE_WAIT_ENABLED = 1U'):
        if text.count(declaration) != 1:
            raise ValueError(f'expected unchanged availability default: {declaration}')
    for before, after in REPLACEMENTS.items():
        if text.count(before) != 1:
            raise ValueError(f'expected one synthetic replacement: {before}')
        text = text.replace(before, after)
    config.write_text(text, encoding='utf-8', newline='\n')
    record['synthetic_replacements'] = REPLACEMENTS
    record['fixture_config_sha256'] = digest(config)
    record['fixture_source'] = source_identity(source)
    return source


def run_command(argv, log, environment, record, scope):
    log.write(('\nargv: ' + json.dumps(argv) + '\n').encode('utf-8'))
    log.flush()
    entry = {'argv': argv, 'scope': scope, 'start_utc': utc_now()}
    record['commands'].append(entry)
    start = log.tell()
    result = subprocess.run(argv, cwd=ROOT, env=environment,
                            stdout=log, stderr=subprocess.STDOUT)
    end = log.tell()
    entry.update(returncode=result.returncode, end_utc=utc_now(),
                 log_start_byte=start, log_end_byte=end)
    log.seek(start)
    raw_output = log.read(end - start)
    output = raw_output.decode('utf-8', errors='replace')
    log.seek(end)
    entry['output_sha256'] = hashlib.sha256(raw_output).hexdigest()
    summaries = re.findall(CASE_SUMMARY, output)
    if len(summaries) == 1:
        entry['cases'] = dict(zip(('selected', 'passed', 'failed', 'skipped'),
                                  map(int, summaries[0])))
    if result.returncode:
        raise subprocess.CalledProcessError(result.returncode, argv)
    return entry, output


def check_cases(entry, output, expected=None):
    matches = re.findall(CASE_SUMMARY, output)
    if len(matches) != 1:
        raise ValueError('expected exactly one doctest case summary')
    selected, passed, failed, skipped = map(int, matches[0])
    entry['cases'] = dict(selected=selected, passed=passed, failed=failed, skipped=skipped)
    if not selected or passed != selected or failed:
        raise ValueError('empty or unsuccessful selected case set')
    if expected is not None and selected != expected:
        raise ValueError(f'expected {expected} D131 cases, observed {selected}')
    if expected is None and skipped:
        raise ValueError('unfiltered push target unexpectedly skipped cases')


def run_binaries(build, log, environment, record):
    for target in TARGETS:
        argv = [str(build / target), '--no-colors=true']
        timing = target.startswith('timing_evidence')
        scope = 'D131 timing only; excludes legacy D129 cases' if timing else 'all push cases'
        if timing:
            argv += ['--test-case=*D131*']
            entry, output = run_command(argv + ['--list-test-cases'], log,
                                        environment, record, scope + ' (listing only)')
            counts = re.findall(r'unskipped test cases passing the current filters: (\d+)', output)
            if counts != ['5']:
                raise ValueError(f'expected five named D131 timing cases: {counts}')
            entry['listed_case_count'] = 5
        entry, output = run_command(argv, log, environment, record, scope)
        check_cases(entry, output, 5 if timing else None)


def run_profile(scratch, freeze, log, record):
    source = make_fixture(scratch, freeze, record)
    build = scratch / 'build'
    environment = os.environ.copy()
    environment.update(TMPDIR=str(scratch), CMAKE_BUILD_PARALLEL_LEVEL='1',
                       ASAN_OPTIONS='detect_leaks=1:halt_on_error=1',
                       UBSAN_OPTIONS='halt_on_error=1:print_stacktrace=1')
    record['environment_overrides'] = {key: environment[key] for key in
                                      ('TMPDIR', 'CMAKE_BUILD_PARALLEL_LEVEL',
                                       'ASAN_OPTIONS', 'UBSAN_OPTIONS')}
    compiler = ('-fsanitize=address,undefined -fno-omit-frame-pointer -fno-pie '
                '-DAPP_TEST_CONFIGURED_BUTTONS=1 -DSUMOX_TIMING_EVIDENCE=1')
    configure = ['cmake', '-S', str(source / 'host'), '-B', str(build),
                 '-DCMAKE_BUILD_TYPE=Debug',
                 '-DCMAKE_EXE_LINKER_FLAGS=-fsanitize=address,undefined -no-pie',
                 '-DCMAKE_CXX_FLAGS=' + compiler]
    try:
        run_command(configure, log, environment, record, 'configure positive20 fixture')
        run_command(['cmake', '--build', str(build), '--parallel', '1', '--target',
                     *TARGETS], log, environment, record, 'build four targets serially')
        run_binaries(build, log, environment, record)
    finally:
        cache = build / 'CMakeCache.txt'
        if cache.is_file():
            record['cmake_cache_sha256'] = digest(cache)
            lines = cache.read_text(encoding='utf-8', errors='replace').splitlines()
            record['compiler_binding'] = [line for line in lines if line.startswith(
                ('CMAKE_CXX_COMPILER:', 'CMAKE_CXX_COMPILER_VERSION:', 'CMAKE_GENERATOR:'))]
        record['fixture_source_after_run'] = source_identity(source)
        if record['fixture_source_after_run'] != record['fixture_source']:
            raise ValueError('fixture source changed during execution')


def main():
    if len(sys.argv) != 2 or not re.fullmatch(r'[A-Za-z0-9_]+', sys.argv[1]):
        raise SystemExit('usage: run_positive_profile.py UNIQUE_LABEL')
    label = sys.argv[1]
    json_path, log_path = OUT / (label + '.json'), OUT / (label + '.txt')
    if json_path.exists() or log_path.exists():
        raise SystemExit('refusing to overwrite prior evidence; use a unique label')
    record = dict(label=label, start_utc=utc_now(), commands=[], hardware_access=False,
                  duration_ms=20, arc=1, wait=1, sanitizer='ASan+UBSan',
                  scope='all push cases plus exactly five D131 timing cases per M0/M1',
                  legacy_D129_positive_claim=False,
                  legacy_D129_scope='complete legacy D129 belongs to separate zero full suite',
                  runner_sha256=digest(Path(__file__)), scratch_released=False)
    code, scratch_path = 1, None
    with json_path.open('x', encoding='utf-8') as receipt, log_path.open('x+b') as log:
        try:
            freeze_path = OUT / 'freeze.json'
            freeze_bytes = freeze_path.read_bytes()
            freeze = json.loads(freeze_bytes)
            record['input_freeze_sha256'] = hashlib.sha256(freeze_bytes).hexdigest()
            record['verified_source_files'] = len(freeze)
            verify_source(freeze)
            temporary_root = Path(os.environ.get('TMPDIR') or '/dev/shm').resolve()
            record['free_bytes_before'] = dict(output=shutil.disk_usage(OUT).free,
                                              scratch=shutil.disk_usage(temporary_root).free)
            with tempfile.TemporaryDirectory(prefix='sumox_d134_positive_',
                                             dir=temporary_root) as scratch:
                scratch_path = Path(scratch)
                record['scratch_path'] = str(scratch_path)
                run_profile(scratch_path, freeze, log, record)
            if freeze_path.read_bytes() != freeze_bytes:
                raise ValueError('freeze manifest changed during execution')
            verify_source(freeze)
            record['source_verified_after_run'] = True
            code = 0
        except Exception as error:
            code = error.returncode if isinstance(error, subprocess.CalledProcessError) else 1
            record['error'] = f'{type(error).__name__}: {error}'
            log.write(traceback.format_exc().encode('utf-8'))
        finally:
            record['scratch_released'] = scratch_path is not None and not scratch_path.exists()
            record.update(returncode=code, end_utc=utc_now())
            log.flush()
            record['log_sha256'] = digest(log_path)
            receipt.write(json.dumps(record, indent=2) + '\n')
    print(f'{label}: exit {code}; evidence {json_path}; scratch released={record["scratch_released"]}')
    return code


if __name__ == '__main__':
    sys.exit(main())
