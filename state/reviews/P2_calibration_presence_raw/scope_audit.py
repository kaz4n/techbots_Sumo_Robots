"""Bind D083 reviewed bytes and independently compare every pre-existing test."""
import hashlib
import json
from pathlib import Path
import subprocess

root = Path(__file__).resolve().parents[3]
out = Path(__file__).resolve().parent
baseline = '06e7d0d'


def git(*args):
    return subprocess.check_output(['git', *args], cwd=root)


def sha(data):
    return hashlib.sha256(data).hexdigest()


existing = git('ls-tree', '-r', '--name-only', baseline, 'src', 'tests', 'host',
               'bench/p0_matrix', 'bench/p0_timing', 'bench/p0_adc',
               'bench/p0_gpio', 'bench/p0_qtr').decode().splitlines()
protected = [name for name in existing
             if name not in ('src/core/countdown.cpp', 'src/core/countdown.h')]
changed = []
newline_only = []
for name in protected:
    old = git('show', baseline + ':' + name)
    current = (root / name).read_bytes()
    if old != current:
        if old.replace(b'\r\n', b'\n') == current.replace(b'\r\n', b'\n'):
            newline_only.append(name)
        else:
            changed.append({'path': name, 'baseline': sha(old), 'current': sha(current)})
reviewed = ['src/core/countdown.cpp', 'src/core/countdown.h',
            'tests/test_calibration_presence.cpp',
            'bench/p2_calibration_compile/p2_calibration_compile.ino',
            'state/analysis/P2_calibration_presence_contract.md']
result = dict(baseline=baseline, contract_commit='3c356ec',
              protected_files_compared=len(protected),
              protected_semantic_changes=changed,
              working_copy_CRLF_vs_git_LF=newline_only,
              hashes={name: sha((root/name).read_bytes()) for name in reviewed},
              protected_git_diff=git('diff', baseline, '--', *protected).decode())
(out / 'scope_audit.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result))
assert not changed and not result['protected_git_diff']
