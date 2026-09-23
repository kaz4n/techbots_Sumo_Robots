"""Run frozen D087 host checks in a separate Linux checkout without board access."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
label, *modules = sys.argv[1:]
tooling_only = '--tooling-only' in modules
modules = [name for name in modules if name != '--tooling-only']
assert label.replace('_', '').isalnum()
receipt = OUT / label
receipt.mkdir(exist_ok=False)
commands = []
started = datetime.now(timezone.utc).isoformat()
environment = os.environ.copy()
environment['TMPDIR'] = '/dev/shm'
environment['PYTHONDONTWRITEBYTECODE'] = '1'
environment['ASAN_OPTIONS'] = 'detect_leaks=1:halt_on_error=1'
environment['UBSAN_OPTIONS'] = 'halt_on_error=1:print_stacktrace=1'

with tempfile.TemporaryDirectory(prefix='d087-review-', dir='/dev/shm') as temporary:
    stage = Path(temporary)
    for name in ('src', 'tests', 'host', 'tools', 'bench', 'docs'):
        shutil.copytree(ROOT / name, stage / name,
                        ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
    (stage / 'state/analysis').mkdir(parents=True)
    shutil.copyfile(ROOT / 'state/analysis/P2_button_routing_contract.md',
                    stage / 'state/analysis/P2_button_routing_contract.md')
    frozen = {p.relative_to(stage).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
              for p in sorted(stage.rglob('*')) if p.is_file()}

    def run(name, argv):
        with (receipt / (name + '.txt')).open('w') as output:
            result = subprocess.run(argv, cwd=stage, env=environment,
                                    stdout=output, stderr=subprocess.STDOUT)
        commands.append({'name': name, 'argv': list(map(str, argv)), 'returncode': result.returncode})
        (receipt / 'commands.json').write_text(json.dumps(commands, indent=2) + '\n')
        return result.returncode

    status = 0
    for mode in (() if tooling_only else ('normal', 'sanitizer')):
        build = stage / ('build-' + mode)
        flags = ['-DCMAKE_CXX_FLAGS=-fsanitize=address,undefined -fno-omit-frame-pointer',
                 '-DCMAKE_EXE_LINKER_FLAGS=-fsanitize=address,undefined'] if mode == 'sanitizer' else []
        plans = [('configure', ['cmake', '-S', str(stage / 'host'), '-B', str(build), '-DCMAKE_BUILD_TYPE=Debug', *flags]),
                 ('build', ['cmake', '--build', str(build), '--parallel', '2']),
                 ('test', ['ctest', '--test-dir', str(build), '--output-on-failure', '-V'])]
        for name, argv in plans:
            status = run(mode + '_' + name, argv)
            if status:
                break
        if status:
            break
    if not status and modules:
        status = run('tooling', ['python3', '-m', 'unittest', *modules, '-v'])
    author = stage / 'state/analysis/P2_button_routing_raw/author'
    if author.exists():
        shutil.copytree(author, receipt / 'tooling_native')
    drift = [name for name, digest in frozen.items()
             if not (ROOT / name).is_file() or hashlib.sha256((ROOT / name).read_bytes()).hexdigest() != digest]
    data = {'started': started, 'ended': datetime.now(timezone.utc).isoformat(),
            'status': status, 'frozen_files': frozen, 'live_drift': drift,
            'commands': commands, 'scope': 'Independent frozen host-only checkout; no board operation'}
    (receipt / 'receipt.json').write_text(json.dumps(data, indent=2) + '\n')
    print(json.dumps({'status': status, 'files': len(frozen), 'drift': drift}))
raise SystemExit(status)
