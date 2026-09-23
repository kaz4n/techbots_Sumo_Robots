"""Run the independent D092 tests without reading production source bodies."""
import datetime
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
BUILD = Path('/tmp/sumox_d092_author')
BUILD.mkdir(parents=True, exist_ok=True)
stamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
receipts = []
sources = sorted((ROOT / 'src/core').glob('*.cpp')) + [
    ROOT / item for item in ('src/hal/motors.cpp', 'src/hal/recorder.cpp',
                            'src/hal/recorder_frames.cpp', 'tests/test_tick_timing.cpp',
                            'host/motor_gate_main.cpp')]
for enabled in (0, 1):
    binary = BUILD / ('timing_enabled' if enabled else 'timing_default')
    command = ['g++', '-std=c++17', '-O0', '-g', '-Wall', '-Wextra', '-Wpedantic',
               '-Werror', '-fno-exceptions', '-fno-rtti', '-DDOCTEST_CONFIG_NO_EXCEPTIONS',
               f'-DMOTORS_ALLOWED={enabled}', '-I' + str(ROOT / 'src'),
               '-isystem', str(ROOT / 'host/third_party'), *map(str, sources), '-o', str(binary)]
    for stage, argv in [('build', command), ('test', [str(binary), '--no-colors'])]:
        result = subprocess.run(argv, cwd=ROOT, text=True, capture_output=True, check=False)
        receipt = {'stage': stage, 'motors_allowed': enabled, 'command': argv,
                   'returncode': result.returncode, 'stdout': result.stdout, 'stderr': result.stderr}
        receipts.append(receipt)
        (OUT / (stamp + '.json')).write_text(json.dumps(receipts, indent=2) + '\n')
        print(f'MOTORS_ALLOWED={enabled} {stage} rc={result.returncode}', flush=True)
        print(result.stdout, flush=True)
        print(result.stderr, flush=True)
        if result.returncode and stage == 'build':
            break
manifest = {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in [ROOT / 'tests/test_tick_timing.cpp', ROOT / 'tests/fixtures/tick_timing_fixture.h']}
(OUT / (stamp + '_source_hashes.json')).write_text(json.dumps(manifest, indent=2) + '\n')
raise SystemExit(any(item['returncode'] for item in receipts))
