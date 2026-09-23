"""Capture independent-author host commands without shell expansion."""
import json
import hashlib
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[4]
RAW = Path(__file__).parent
mode = sys.argv[1]
if mode == 'syntax':
    commands = [['g++', '-std=c++17', '-Wall', '-Wextra', '-Wpedantic', '-Werror',
                 '-fno-exceptions', '-fno-rtti', '-DDOCTEST_CONFIG_NO_EXCEPTIONS',
                 '-I', 'src', '-isystem', 'host/third_party', '-fsyntax-only', str(path)]
                for path in sorted((ROOT/'tests').glob('test_button_*.cpp'))]
elif mode == 'focused':
    commands = [[str(ROOT/'build/host'/binary), '--no-colors', '--test-case=*D087*']
                for binary in ('sumox26_tests', 'motor_gate_enabled_tests')]
elif mode == 'tooling':
    commands = [[sys.executable, '-B', '-m', 'unittest', 'tests.tooling.test_button_decoder', '-v']]
else:
    raise SystemExit('unknown mode')
result_code = 0
for command in commands:
    name = f'{mode}_{time.time_ns()}'
    (RAW/f'{name}.command.json').write_text(json.dumps(command, indent=2)+'\n')
    binary = Path(command[0])
    paths = list((ROOT/'tests').glob('test_button_*.cpp'))
    paths += list((ROOT/'src/core').glob('*.cpp'))
    paths += [ROOT/'src/hal/ui.cpp', ROOT/'src/hal/motors.cpp', ROOT/'src/config.h']
    if binary.is_file():
        paths.append(binary)
    (RAW/f'{name}.identity.json').write_text(json.dumps(
        {str(path):hashlib.sha256(path.read_bytes()).hexdigest() for path in paths}, indent=2)+'\n')
    result = subprocess.run(command, cwd=ROOT, capture_output=True)
    (RAW/f'{name}.stdout').write_bytes(result.stdout)
    (RAW/f'{name}.stderr').write_bytes(result.stderr)
    (RAW/f'{name}.status.txt').write_text(str(result.returncode)+'\n')
    print('COMMAND', json.dumps(command), 'STATUS', result.returncode, flush=True)
    print(result.stdout.decode(errors='replace')[-12000:], flush=True)
    print(result.stderr.decode(errors='replace')[-12000:], flush=True)
    result_code = result.returncode or result_code
sys.exit(result_code)
