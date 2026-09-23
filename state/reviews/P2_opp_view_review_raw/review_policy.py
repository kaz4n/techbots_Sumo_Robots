"""Execute only mocked local D107 build-policy suites in a private WSL copy."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import time

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
receipt = OUT / ('policy_' + str(time.time_ns()) + '.json')
record = {'scope': 'Private WSL copy; mocked build tools only; no board or network', 'commands': []}
with tempfile.TemporaryDirectory(prefix='d107-policy-review-') as temp:
    copied = Path(temp)
    for folder in ('tools', 'tests'):
        shutil.copytree(ROOT / folder, copied / folder,
                        ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
    # The unchanged legacy suites read their original D100 compiler fixture.
    fixture = Path('state/analysis/P2_app_build_raw/default_receipt')
    shutil.copytree(ROOT / fixture, copied / fixture)
    record['copied_hashes'] = {p.relative_to(copied).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                               for p in copied.rglob('*') if p.is_file()}
    receipt.write_text(json.dumps(record, indent=2) + '\n')
    env = dict(os.environ, PYTHONPATH='tests/tooling', PYTHONDONTWRITEBYTECODE='1')
    for modules in (['tests.tooling.test_opp_view_policy'],
                    ['tests.tooling.test_app_build_policy', 'tests.tooling.test_app_build_overrides',
                     'tests.tooling.test_runtime_inert_policy']):
        argv = ['python3', '-m', 'unittest', *modules, '-v']
        result = subprocess.run(argv, cwd=copied, env=env, text=True,
                                capture_output=True, timeout=300)
        record['commands'].append(dict(argv=argv, returncode=result.returncode,
                                       stdout=result.stdout, stderr=result.stderr))
        receipt.write_text(json.dumps(record, indent=2) + '\n')
        print(result.stderr[-1000:], flush=True)
        assert result.returncode == 0
    record['verdict'] = 'PASS_MOCKED_NEW_AND_UNCHANGED_POLICY_SUITES'
    receipt.write_text(json.dumps(record, indent=2) + '\n')
print(receipt)
