"""Run the narrow D229 histogram and real Runtime host checks, serially.

Retains exact command output and source pins; creates no board artifact or claim.
Uses the repository's checked doctest, Runtime fixture and heap-operation probe.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import time

ROOT = Path(__file__).resolve().parents[2]
BASELINE = '004dc7cff534896a851901f9d7d0ba6066cae060'
HAL = ('motors.cpp', 'recorder.cpp', 'recorder_frames.cpp', 'recorder_csv.cpp',
       'recorder_dump.cpp', 'power_inputs.cpp', 'ui.cpp', 'imu_heading.cpp',
       'imu_adapter.cpp', 'line_qtr_adapter.cpp', 'qtr_cal.cpp',
       'qtr_cal_format.cpp', 'ui_display.cpp')
APP = ('transaction.cpp', 'runtime.cpp', 'runtime_inputs.cpp', 'runtime_dump.cpp',
       'runtime_service.cpp', 'runtime_calibration.cpp', 'transaction_service.cpp')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--raw', type=Path, required=True)
    parser.add_argument('--git-dir', type=Path, help='Translated metadata path for a Windows worktree under WSL')
    args = parser.parse_args()
    git = ['git']
    if args.git_dir:
        git += ['--git-dir', str(args.git_dir.resolve()), '--work-tree', str(ROOT)]
    raw = args.raw.resolve()
    raw.mkdir(parents=True, exist_ok=False)
    scratch = Path(tempfile.mkdtemp(prefix='sumo-d229-', dir='/dev/shm'))
    receipt = {'schema': 'd229-focused-host-v1', 'target_evidence': False,
               'started_unix': time.time(), 'scratch': str(scratch), 'commands': []}
    paths = [p for p in (ROOT / 'src').rglob('*') if p.is_file()]
    paths += [p for p in (ROOT / 'tests/fixtures').rglob('*') if p.is_file()]
    paths += [ROOT / name for name in ('tests/test_epoch_timing.cpp',
              'tests/test_runtime_epoch_timing.cpp', 'tests/native_app_runtime/allocation_probe.cc',
              'host/motor_gate_main.cpp', 'host/third_party/doctest.h',
              'state/analysis/P7_epoch_timing_contract.md')]
    paths.append(Path(__file__).resolve())

    def pins():
        return {str(p.relative_to(ROOT)): {'bytes': p.stat().st_size,
                'sha256': hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(paths)}

    def command(argv, timeout=300):
        argv = list(map(str, argv))
        number = len(receipt['commands'])
        started = time.time()
        try:
            result = subprocess.run(argv, cwd=ROOT, capture_output=True, timeout=timeout)
            code, stdout, stderr = result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired as error:
            code, stdout, stderr = 124, error.stdout or b'', (error.stderr or b'') + b'\nTIMEOUT\n'
        (raw / f'{number:02d}.stdout').write_bytes(stdout)
        (raw / f'{number:02d}.stderr').write_bytes(stderr)
        receipt['commands'].append({'argv': argv, 'returncode': code,
                                    'seconds': time.time() - started})
        print(f'{number:02d} rc={code} {Path(argv[0]).name}', flush=True)
        if code:
            raise RuntimeError(f'Command {number} failed; original output retained at {raw}')
        return stdout

    try:
        receipt['pins_before'] = pins()
        receipt['base'] = command([*git, 'rev-parse', 'HEAD']).decode().strip()
        compiler = shutil.which('g++')
        if compiler is None:
            raise RuntimeError('Requires existing Linux/WSL g++')
        command([compiler, '--version'])
        receipt['baseline_commit'] = BASELINE
        baseline_header = command([*git, 'show', BASELINE + ':src/app/runtime.h'])
        (scratch / 'baseline_runtime.h').write_bytes(baseline_header)
        receipt['baseline_runtime_header_sha256'] = hashlib.sha256(baseline_header).hexdigest()
        probe = scratch / 'baseline_size.cc'
        probe.write_text('#include "baseline_runtime.h"\n#include <cstdio>\n'
                         'int main() { std::printf("D229 baseline host Runtime size=%zu\\n", '
                         'sizeof(app::Runtime)); }\n')
        common = [compiler, '-std=c++17', '-O1', '-Wall', '-Wextra', '-Wpedantic',
                  '-Werror', '-fno-exceptions', '-fno-rtti', '-DMATCH=0', '-DMOTORS_ALLOWED=0',
                  '-I', ROOT / 'src', '-I', ROOT / 'src/app', '-I', ROOT / 'tests',
                  '-isystem', ROOT / 'host/third_party']
        command([*common, probe, '-o', scratch / 'baseline_size'])
        command([scratch / 'baseline_size'])
        sources = sorted((ROOT / 'src/core').glob('*.cpp'))
        sources += [ROOT / 'src/hal' / p for p in HAL]
        sources += [ROOT / 'src/app' / p for p in APP]
        sources += [ROOT / p for p in ('tests/test_epoch_timing.cpp',
                    'tests/test_runtime_epoch_timing.cpp',
                    'tests/native_app_runtime/allocation_probe.cc', 'host/motor_gate_main.cpp')]
        binary = scratch / 'epoch_timing_tests'
        command([*common, '-fsanitize=undefined', '-fno-sanitize-recover=all',
                 '-DDOCTEST_CONFIG_NO_EXCEPTIONS_BUT_WITH_ALL_ASSERTS',
                 '-Wl,--wrap=malloc,--wrap=calloc,--wrap=realloc,--wrap=free',
                 *sources, '-o', binary])
        output = command([binary, '--no-colors'])
        print(output.decode(), end='', flush=True)
        if b'Status: SUCCESS!' not in output:
            raise RuntimeError('Missing successful doctest summary')
        receipt['pins_after'] = pins()
        if receipt['pins_before'] != receipt['pins_after']:
            raise RuntimeError('Source changed during focused validation')
        receipt['status'] = 'PASS_HOST_ONLY'
    except BaseException as error:
        receipt['status'] = 'FAIL'
        receipt['error'] = repr(error)
        raise
    finally:
        receipt['finished_unix'] = time.time()
        receipt['scratch_bytes_before_cleanup'] = sum(p.stat().st_size for p in scratch.rglob('*') if p.is_file())
        shutil.rmtree(scratch)
        receipt['scratch_removed'] = not scratch.exists()
        (raw / 'result.json').write_text(json.dumps(receipt, indent=2) + '\n')


if __name__ == '__main__':
    main()
