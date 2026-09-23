"""Local reviewer build only. No stage, transport, hardware or shared build calls."""
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[3]
RAW = Path(__file__).resolve().parent
sources = sorted((ROOT / 'src/core').glob('*.cpp'))
sources += [ROOT / name for name in ('src/app/transaction.cpp', 'src/hal/motors.cpp',
                                    'src/hal/recorder.cpp', 'src/hal/recorder_frames.cpp')]
sources += [RAW / 'reviewer_cases.cpp']
manifest = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sources + list((ROOT / 'src').rglob('*.h'))}
results = []
with tempfile.TemporaryDirectory(prefix='d095-review-', dir='/dev/shm') as temp:
    for mode in (0, 1):
        binary = Path(temp) / f'cases-{mode}'
        command = ['g++', '-std=c++17', '-O1', '-Wall', '-Wextra', '-Werror',
                   '-Wpedantic', '-fno-exceptions', '-fno-rtti',
                   '-fsanitize=address,undefined', '-fno-sanitize-recover=all',
                   f'-DMOTORS_ALLOWED={mode}', '-I', str(ROOT / 'src'),
                   *map(str, sources), '-o', str(binary)]
        for args in (command, [str(binary)]):
            output = subprocess.run(args, capture_output=True, text=True)
            results.append(dict(argv=args, returncode=output.returncode,
                                stdout=output.stdout, stderr=output.stderr))
            (RAW / 'independent_results.json').write_text(json.dumps(
                dict(source_sha256=manifest, results=results), indent=2) + '\n')
            print(output.stdout, output.stderr, flush=True)
            if output.returncode:
                raise SystemExit(output.returncode)
