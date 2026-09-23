"""Strict syntax only; copied config profiles, no independent test-body reads."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import re
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[4]
RAW = Path(__file__).resolve().parent
config = (ROOT / 'src/config.h').read_text()
profiles = [{'UI_BENCH_SAMPLES': 128}, {'UI_BENCH_SAMPLES': 1}, {'UI_BENCH_SAMPLES': 0},
    {'TICK_US': 0}, {'TICK_US': 0x80000000}, {'VBAT_ADC_CONVERSION_US': 0},
    {'TICK_US': 1, 'VBAT_ADC_CONVERSION_US': 1}, {'BUTTON_WINDOWS_CONFIGURED': 2}]
result = {'start_utc': datetime.now(timezone.utc).isoformat(),
    'scope': 'Syntax only for owned translation units plus unchanged actual decoder; no behavioral test execution.',
    'compiler': subprocess.run(['g++', '--version'], capture_output=True, text=True, check=True).stdout,
    'profiles': []}
for profile in profiles:
    with tempfile.TemporaryDirectory(prefix='ui-bench-syntax-') as name:
        stage = Path(name)
        src = stage / 'src'
        src.mkdir()
        for module in ('hal', 'core'):
            for header in (ROOT / 'src' / module).glob('*.h'):
                destination = src / module / header.name
                destination.parent.mkdir(exist_ok=True)
                shutil.copyfile(header, destination)
        for filename in ('ui_bench.h', 'ui_bench_native.h', 'ui_bench.cpp', 'ui_bench_native.cpp'):
            shutil.copyfile(ROOT / 'bench/ui/src' / filename, src / filename)
        shutil.copyfile(ROOT / 'bench/ui/ui.ino', stage / 'ui.ino')
        shutil.copyfile(ROOT / 'src/hal/ui.cpp', src / 'hal/ui.cpp')
        temporary = config
        for symbol, value in profile.items():
            temporary, count = re.subn(r'(' + symbol + r'\s*=\s*)\d+U',
                lambda match: match[1] + str(value) + 'U', temporary)
            assert count == 1, (symbol, count)
        (src / 'config.h').write_text(temporary)
        (stage / 'Arduino.h').write_text('#pragma once\nunsigned long micros();\n')
        argv = ['g++', '-std=c++17', '-Wall', '-Wextra', '-Wpedantic', '-Werror',
            '-fno-exceptions', '-fno-rtti', '-fsyntax-only', '-x', 'c++', '-I', str(stage), '-I', str(src),
            str(src / 'ui_bench.cpp'), str(src / 'ui_bench_native.cpp'), str(stage / 'ui.ino'), str(src / 'hal/ui.cpp')]
        outcome = subprocess.run(argv, capture_output=True, text=True)
        result['profiles'].append({'config_overrides': profile, 'argv': argv, 'exit_code': outcome.returncode,
            'stdout': outcome.stdout, 'stderr': outcome.stderr,
            'temporary_config_sha256': hashlib.sha256(temporary.encode()).hexdigest()})
result['end_utc'] = datetime.now(timezone.utc).isoformat()
freeze = json.loads((RAW / 'first_source_freeze.json').read_text())
result['source_unchanged'] = all(hashlib.sha256((ROOT / item['path']).read_bytes()).hexdigest() == item['sha256']
    for item in freeze['files'])
destination = RAW / 'first_syntax.json'
assert not destination.exists(), 'Retain prior checks; select a new receipt name.'
destination.write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps({'profiles': len(result['profiles']), 'statuses': [x['exit_code'] for x in result['profiles']],
    'source_unchanged': result['source_unchanged']}))
raise SystemExit(any(item['exit_code'] for item in result['profiles']) or not result['source_unchanged'])
