# Captures focused D227 host checks with bounded children and persistent streams.
# Keeps Windows/Linux attempts separate and preserves first failures and pins.
# Only the explicitly listed unittest methods/modules run; no native board calls.
from pathlib import Path
import hashlib
import json
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[3]
RAW = Path(__file__).resolve().parent
NAMES = ('tools/deploy_commissioning_app.py', 'tools/commissioning_app_upload.py',
         'state/analysis/P7_commissioning_deploy_contract.md',
         'tests/tooling/test_commissioning_deploy.py', 'tests/tooling/test_commissioning_app_upload.py')


def pins():
    return {name: dict(bytes=len((ROOT / name).read_bytes()),
             sha256=hashlib.sha256((ROOT / name).read_bytes()).hexdigest()) for name in NAMES}


def main():
    platform, attempt, *tests = sys.argv[1:]
    if platform not in ('windows', 'linux') or not tests or not attempt.replace('_', '').isalnum():
        raise ValueError('Exact platform, new attempt and tests required')
    if any(not name.startswith('tests.tooling.test_commissioning_') for name in tests):
        raise ValueError('Unexpected test scope')
    output = RAW / attempt
    output.mkdir()
    before = pins()
    argv = (['python'] if platform == 'windows' else ['wsl', '-d', 'Ubuntu', '--', 'python3'])
    argv += ['-B', '-m', 'unittest', '-v', *tests]
    (output / 'inputs.json').write_text(json.dumps(before, indent=2, sort_keys=True) + '\n')
    start = time.monotonic()
    result = dict(argv=argv, returncode=None, error=None)
    try:
        with (output / 'stdout').open('xb') as stdout, (output / 'stderr').open('xb') as stderr:
            child = subprocess.run(argv, cwd=ROOT, stdout=stdout, stderr=stderr, timeout=600)
            result['returncode'] = child.returncode
    except BaseException as error:
        result['error'] = dict(type=type(error).__name__, message=str(error))
    result.update(elapsed_seconds=time.monotonic() - start, input_hashes=before,
                  inputs_unchanged=before == pins())
    (output / 'result.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(json.dumps(result))
    return 0 if result['returncode'] == 0 and result['inputs_unchanged'] else 1


if __name__ == '__main__':
    sys.exit(main())
