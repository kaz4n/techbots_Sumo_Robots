"""Independently bind D084 review inputs and unchanged established tests to Git."""
import hashlib
import json
from pathlib import Path
import subprocess

root = Path(__file__).resolve().parents[3]
out = Path(__file__).resolve().parent
baseline = 'c72921c'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def git(*args):
    return subprocess.check_output(['git', *args], cwd=root)


paths = git('ls-tree', '-r', '--name-only', baseline, 'tests', 'src/config.h',
            'src/app', 'tools/board_tool.py').decode().splitlines()
protected = {}
for name in paths:
    old = git('show', baseline + ':' + name)
    current = (root/name).read_bytes()
    equal = old.replace(b'\r\n', b'\n') == current.replace(b'\r\n', b'\n')
    protected[name] = {'baseline_sha256': sha(old), 'current_sha256': sha(current),
                       'equal_after_crlf_normalization': equal}
assert all(value['equal_after_crlf_normalization'] for value in protected.values())
production = {p.relative_to(root).as_posix(): sha(p.read_bytes())
              for folder in ('src', 'bench/p2_imu_integration_compile')
              for p in sorted((root/folder).rglob('*')) if p.is_file()}
tests = {p.relative_to(root).as_posix(): sha(p.read_bytes()) for p in [
    root/'tests/test_imu_adapter.cpp', root/'tests/test_imu_provenance.cpp',
    root/'tests/test_imu_integration.cpp', root/'tests/tooling/test_imu_integration.py']}
contract = root/'state/analysis/P2_imu_integration_contract.md'
result = {'baseline': baseline, 'head': git('rev-parse', 'HEAD').decode().strip(),
          'contract_sha256': sha(contract.read_bytes()), 'protected': protected,
          'production': production, 'new_tests': tests,
          'diff_names': git('diff', '--name-only', baseline).decode().splitlines(),
          'untracked': git('ls-files', '--others', '--exclude-standard').decode().splitlines()}
(out/'scope_audit.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps({'protected_unchanged':len(protected), 'production_files':len(production),
                  'new_tests':len(tests), 'contract_sha256':result['contract_sha256']}))
