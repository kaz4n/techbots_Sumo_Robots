"""Compile frozen helper and private properties locally; never touch hardware."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
FILES = ('src/core/turn_trial.cpp', 'src/core/turn_trial.h',
         'src/core/motion.cpp', 'src/core/motion.h', 'src/config.h',
         'state/analysis/P3_turn_trial_contract.md')
hashes = {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in FILES}
if hashes['src/core/turn_trial.cpp'] != 'cc88727fa5a19117ceb88ad3c4b068ea4df815a8570f7d5c7b80c23ae4d3d62f':
    raise RuntimeError('Reviewed source differs from expected frozen implementation')
work = Path(tempfile.mkdtemp(prefix='sumox_d124_review_', dir='/dev/shm'))
commands = []
for profile in ('normal', 'sanitizer'):
    binary = work / profile
    command = ['g++', '-std=c++17', '-Wall', '-Wextra', '-Wpedantic', '-Werror',
               '-fno-exceptions', '-fno-rtti', '-I', str(ROOT / 'src'),
               str(OUT / 'private_properties.cc'), str(ROOT / 'src/core/turn_trial.cpp'),
               str(ROOT / 'src/core/motion.cpp'), '-o', str(binary)]
    if profile == 'sanitizer':
        command += ['-fsanitize=address,undefined', '-fno-omit-frame-pointer', '-fno-pie', '-no-pie']
    for action, argv in (('compile', command), ('run', [str(binary)])):
        result = subprocess.run(argv, text=True, capture_output=True, timeout=90)
        (OUT / (profile + '_' + action + '.log')).write_text(result.stdout + result.stderr)
        commands.append(dict(profile=profile, action=action, command=argv, exit_code=result.returncode))
        if result.returncode:
            (OUT / 'private_validation.json').write_text(json.dumps(dict(
                result='FAIL', commands=commands, hashes=hashes), indent=2) + '\n')
            raise SystemExit(result.returncode)
after = {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in FILES}
report = dict(result='PASS' if after == hashes else 'FAIL', commands=commands, hashes=hashes,
              finished_utc=datetime.now(timezone.utc).isoformat(),
              unchanged_after_execution=(after == hashes),
              limits='Pure host request properties only; no Robot/Gate/target or physical acceptance.')
(OUT / 'private_validation.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report))
raise SystemExit(0 if report['result'] == 'PASS' else 1)
