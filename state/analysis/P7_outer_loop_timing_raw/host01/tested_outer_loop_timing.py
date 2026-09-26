"""Run focused D243 semantics and actual-entry retention checks with one compiler.

Records exact inputs/output before removing only its own temporary build folder.
No target transport, native application or physical measurement is executed.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import time

from tests.tooling.test_epoch_timing import HAL, APP

ROOT = Path(__file__).resolve().parents[2]

ENTRY_TYPES = r'''
#pragma once
#include "src/config.h"
#include <cstdint>
namespace fixture {
inline unsigned constructors=0, begins=0, steps=0, clocks=0;
inline std::uint32_t clock(void*) {
    constexpr std::uint32_t values[]={0U,5U,300000000U,300000009U};
    return values[clocks++];
}
}
namespace motors {
struct Port { void* context; std::uint32_t (*clockUs)(void*); };
struct UnoQPort { Port port() { return {nullptr,fixture::clock}; } };
}
namespace recorder::dump {
enum class Buffering { LEGACY_SINGLE,FIFO8 };
struct UnoQDumpPort { explicit UnoQDumpPort(Buffering) {} };
}
namespace app {
enum class RuntimePhase : std::uint8_t { NOT_STARTED,RUNNING,STOPPED,FAULT,STOP_OBSERVING };
enum class RuntimeFault : std::uint8_t { NONE,PORT,CLOCK,SERVICE_LIMIT,TRANSACTION,PROJECTION };
struct RuntimeReport {
    RuntimePhase phase=RuntimePhase::RUNNING;
    RuntimeFault fault=RuntimeFault::NONE;
    std::uint32_t epochs=0U;
    bool initialization_complete=false;
};
struct NativeSources { int adcPort() {return 1;} int port() {return 2;} };
inline int unoQDumpPort(recorder::dump::UnoQDumpPort&) { return 3; }
inline int configuredSetupGrants() { return 0; }
struct Runtime {
    RuntimeReport report_;
    Runtime(motors::Port,int,int,int) { ++fixture::constructors; }
    bool begin(int) { ++fixture::begins; return true; }
    bool step() { ++fixture::steps; ++report_.epochs; return true; }
    const RuntimeReport& report() const { return report_; }
};
}
'''
ENTRY_MAIN = r'''
#include "app.ino"
#include <cstring>
int main() {
    setup();
    for (unsigned i=0;i<4;++i) loop();
#if SUMOX_TIMING_EVIDENCE
    if (fixture::clocks!=4 || outer_loop_timing.data().status!=
        app::outer_loop_timing::Status::SEALED) return 1;
    if (outer_loop_timing.data().all.data().samples!=2 ||
        outer_loop_timing.data().completed.data().samples!=2 ||
        outer_loop_timing.data().drain_us!=9) return 2;
    unsigned char copy[sizeof outer_loop_timing];
    std::memcpy(copy,&outer_loop_timing,sizeof copy);
    loop();
    if (std::memcmp(copy,&outer_loop_timing,sizeof copy) || fixture::clocks!=4) return 3;
#else
    loop();
    if (fixture::clocks) return 4;
#endif
    return fixture::constructors!=1 || fixture::begins!=1 || fixture::steps!=5;
}
'''


def pins():
    paths = list((ROOT / 'src').rglob('*')) + list((ROOT / 'tests/fixtures').rglob('*'))
    paths += [ROOT / p for p in ('tests/test_outer_loop_timing.cpp',
        'tests/native_app_runtime/allocation_probe.cc', 'tests/tooling/test_epoch_timing.py',
        'tests/tooling/test_outer_loop_timing.py', 'host/motor_gate_main.cpp',
        'host/third_party/doctest.h', 'state/analysis/P7_outer_loop_timing_contract.md')]
    return {str(p.relative_to(ROOT)): {'bytes': p.stat().st_size,
        'sha256': hashlib.sha256(p.read_bytes()).hexdigest()}
        for p in sorted(paths) if p.is_file()}


def execute(raw, receipt, argv, timeout=240):
    number = len(receipt['commands'])
    started = time.time()
    try:
        result = subprocess.run(list(map(str, argv)), cwd=ROOT, capture_output=True, timeout=timeout)
        code, stdout, stderr = result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired as error:
        code, stdout, stderr = 124, error.stdout or b'', (error.stderr or b'') + b'\nTIMEOUT\n'
    (raw / f'{number:02d}.stdout').write_bytes(stdout)
    (raw / f'{number:02d}.stderr').write_bytes(stderr)
    receipt['commands'].append({'argv': list(map(str, argv)), 'returncode': code,
        'seconds': time.time() - started})
    print(f'{number:02d} rc={code} {Path(argv[0]).name}', flush=True)
    if code:
        raise RuntimeError(f'Command {number} failed; raw evidence retained')
    return stdout


def entry_stage(scratch):
    stage = scratch / 'entry'
    for folder in ('src/app', 'src/hal'):
        (stage / folder).mkdir(parents=True, exist_ok=True)
    (stage / 'fixture_types.h').write_text(ENTRY_TYPES)
    for name in ('src/app/native_sources_unoq.h', 'src/hal/motor_port_unoq.h',
                 'src/app/runtime.h', 'src/app/configured_setup.h'):
        (stage / name).write_text('#include "fixture_types.h"\n')
    for name in ('src/config.h', 'src/app/epoch_timing.h', 'src/app/outer_loop_timing.h'):
        shutil.copyfile(ROOT / name, stage / name)
    shutil.copyfile(ROOT / 'src/app/app.ino', stage / 'app.ino')
    (stage / 'main.cpp').write_text(ENTRY_MAIN)
    return stage


def entry_checks(scratch, run, receipt):
    stage = entry_stage(scratch)
    geometry = []
    for timing, match in ((0, 0), (0, 1), (1, 0)):
        binary = scratch / f'entry_{timing}_{match}'
        flags = [f'-DSUMOX_TIMING_EVIDENCE={timing}', f'-DSUMOX_P4_REACTIVE={timing}',
                 f'-DMATCH={match}', '-DMOTORS_ALLOWED=0']
        run(['g++', '-std=c++17', '-Os', '-flto', '-ffunction-sections', '-fdata-sections',
             '-Wl,--gc-sections', '-Wall', '-Wextra', '-Werror', *flags,
             '-I', stage, stage / 'main.cpp', '-o', binary])
        run([binary])
        symbols = run(['nm', '-S', '-C', binary]).decode()
        if (' outer_loop_timing' in symbols) != bool(timing):
            raise RuntimeError('Unexpected observer symbol retention/profile exclusion')
        geometry.append({'timing': timing, 'match': match, 'binary_bytes': binary.stat().st_size,
            'observer_symbols': [line for line in symbols.splitlines() if 'outer_loop_timing' in line]})
    # No diagnostic reference in this main: the actual entry escape must retain stores.
    (stage / 'main.cpp').write_text('#include "app.ino"\nint main(){setup();loop();loop();}\n')
    binary = scratch / 'retention'
    run(['g++', '-std=c++17', '-Os', '-flto', '-ffunction-sections', '-fdata-sections',
         '-Wl,--gc-sections', '-DSUMOX_TIMING_EVIDENCE=1', '-DSUMOX_P4_REACTIVE=1',
         '-DMATCH=0', '-DMOTORS_ALLOWED=0', '-I', stage, stage / 'main.cpp', '-o', binary])
    symbols = run(['nm', '-S', '-C', binary]).decode()
    if ' outer_loop_timing' not in symbols:
        raise RuntimeError('Unreferenced diagnostic object discarded')
    run(['objdump', '-d', '-C', binary])
    receipt['entry_geometry'] = geometry


def runtime_checks(scratch, run):
    sources = sorted((ROOT / 'src/core').glob('*.cpp'))
    sources += [ROOT / 'src/hal' / p for p in HAL] + [ROOT / 'src/app' / p for p in APP]
    sources += [ROOT / p for p in ('tests/test_outer_loop_timing.cpp', 'host/motor_gate_main.cpp')]
    binary = scratch / 'outer_loop_tests'
    run(['g++', '-std=c++17', '-O1', '-Wall', '-Wextra', '-Wpedantic', '-Werror',
         '-fno-exceptions', '-fno-rtti', '-DMATCH=0', '-DMOTORS_ALLOWED=0',
         '-DDOCTEST_CONFIG_NO_EXCEPTIONS_BUT_WITH_ALL_ASSERTS',
         '-fsanitize=undefined', '-fno-sanitize-recover=all',
         '-Wl,--wrap=malloc,--wrap=calloc,--wrap=realloc,--wrap=free',
         '-I', ROOT / 'src', '-I', ROOT / 'tests', '-isystem', ROOT / 'host/third_party',
         *sources, '-o', binary])
    output = run([binary, '--no-colors'])
    print(output.decode(), end='', flush=True)
    if b'Status: SUCCESS!' not in output:
        raise RuntimeError('Missing successful doctest closure')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--raw', type=Path, required=True)
    args = parser.parse_args()
    raw = args.raw.resolve()
    raw.mkdir(parents=True, exist_ok=False)
    scratch = Path(tempfile.mkdtemp(prefix='sumo-d243-', dir='/dev/shm'))
    receipt = {'schema': 'd243-focused-host-v1', 'target_evidence': False,
        'commands': [], 'started_unix': time.time(), 'scratch': str(scratch)}
    run = lambda argv: execute(raw, receipt, argv)
    try:
        receipt['pins_before'] = pins()
        run(['g++', '--version'])
        runtime_checks(scratch, run)
        entry_checks(scratch, run, receipt)
        receipt['pins_after'] = pins()
        if receipt['pins_before'] != receipt['pins_after']:
            raise RuntimeError('Inputs changed during focused validation')
        receipt['status'] = 'PASS_HOST_ONLY'
    except BaseException as error:
        receipt['status'], receipt['error'] = 'FAIL', repr(error)
        raise
    finally:
        receipt['finished_unix'] = time.time()
        receipt['scratch_bytes_before_cleanup'] = sum(p.stat().st_size for p in scratch.rglob('*') if p.is_file())
        shutil.rmtree(scratch)
        receipt['scratch_removed'] = not scratch.exists()
        (raw / 'result.json').write_text(json.dumps(receipt, indent=2) + '\n')


if __name__ == '__main__':
    main()
