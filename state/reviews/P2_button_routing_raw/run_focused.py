"""Independently execute frozen final D087 host binaries; no board operations."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent / (sys.argv[1] if len(sys.argv) > 1 else 'final_focused')
OUT.mkdir(exist_ok=False)
hash_file = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
paths = [p for tree in ('src', 'tests', 'host') for p in (ROOT / tree).rglob('*')
         if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc']
frozen = {p.relative_to(ROOT).as_posix(): hash_file(p) for p in sorted(paths)}
baseline_tests = subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', 'c10f473', 'tests'], cwd=ROOT, text=True).splitlines()
changed_old = subprocess.check_output(['git', 'diff', '--name-only', 'c10f473', '--', 'tests'], cwd=ROOT, text=True).splitlines()
assert changed_old == ['tests/tooling/test_p0_config.py'], changed_old
environment = os.environ.copy()
environment['ASAN_OPTIONS'] = 'detect_leaks=1:halt_on_error=1'
environment['UBSAN_OPTIONS'] = 'halt_on_error=1:print_stacktrace=1'
commands = []
with tempfile.TemporaryDirectory(prefix='d087-focused-', dir='/dev/shm') as temporary:
    for mode, source_dir in [('normal', 'host'), ('sanitizer', 'host-sanitize')]:
        for target in ['sumox26_tests', 'motor_gate_enabled_tests']:
            binary = ROOT / 'build' / source_dir / target
            copy = Path(temporary) / (mode + '_' + target)
            shutil.copy2(binary, copy)
            expected = hash_file(binary)
            assert hash_file(copy) == expected
            argv = [str(copy), '--test-case=*D087*', '--no-colors']
            started = datetime.now(timezone.utc).isoformat()
            begin = time.monotonic()
            result = subprocess.run(argv, cwd=ROOT, env=environment, capture_output=True, text=True)
            label = mode + '_' + target
            (OUT / (label + '.stdout')).write_text(result.stdout)
            (OUT / (label + '.stderr')).write_text(result.stderr)
            commands.append(dict(argv=argv, original_binary=str(binary), sha256=expected,
                                 started=started, elapsed_s=time.monotonic() - begin,
                                 returncode=result.returncode,
                                 binary_drift=hash_file(binary) != expected))
            (OUT / 'commands.json').write_text(json.dumps(commands, indent=2) + '\n')
            print(label, result.returncode, result.stdout[-400:], flush=True)
drift = [name for name, digest in frozen.items() if hash_file(ROOT / name) != digest]
receipt = dict(commands=commands, frozen_files=frozen, drift=drift,
               legacy_test_count=len(baseline_tests), legacy_tests_changed=changed_old,
               reviewed_legacy_change='Config test only adds D087 declaration allowlist and new defaults assertion; old locked and behavioral assertions unchanged',
               baseline='c10f473', scope='Copied native binaries only; no MCU or transport')
(OUT / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
assert not drift
assert all(c['returncode'] == 0 and not c['binary_drift'] for c in commands)
