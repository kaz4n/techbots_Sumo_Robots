"""Reproduce D085 checks from an isolated Linux snapshot without board access."""
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

root = Path(__file__).resolve().parents[3]
evidence = Path(__file__).resolve().parent
label = sys.argv[1]
if not label.replace('_', '').isalnum():
    raise SystemExit('Expected a unique simple label')
out = evidence / label
out.mkdir(exist_ok=False)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def command(name, argv, cwd, env):
    started = datetime.now(timezone.utc).isoformat()
    result = subprocess.run(list(map(str, argv)), cwd=cwd, env=env,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            timeout=900, stdin=subprocess.DEVNULL)
    stream = out / (name + '.txt')
    stream.write_bytes(result.stdout)
    receipt = dict(argv=list(map(str, argv)), cwd=str(cwd), returncode=result.returncode,
                   started_utc=started, ended_utc=datetime.now(timezone.utc).isoformat(),
                   output_sha256=digest(stream), capture='raw combined output bytes')
    (out / (name + '.json')).write_text(json.dumps(receipt, indent=2)+'\n')
    print(json.dumps(receipt), flush=True)
    if result.returncode:
        print(result.stdout.decode(errors='replace'), flush=True)
        raise SystemExit(result.returncode)


with tempfile.TemporaryDirectory(prefix='d085-independent-review-', dir='/dev/shm') as tmp:
    stage = Path(tmp)
    for folder in ('src', 'tests', 'host', 'bench', 'tools', 'docs'):
        shutil.copytree(root/folder, stage/folder,
                        ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
    (stage/'state/analysis').mkdir(parents=True)
    shutil.copyfile(root/'state/analysis/P2_qtr_native_contract.md',
                    stage/'state/analysis/P2_qtr_native_contract.md')
    manifest = {p.relative_to(stage).as_posix(): digest(p)
                for p in sorted(stage.rglob('*')) if p.is_file()}
    (out/'snapshot_manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
    env = dict(os.environ, TMPDIR='/dev/shm', PYTHONDONTWRITEBYTECODE='1',
               SUMO_NATIVE_RECEIPT_DIR=str(out/'native_tooling'))
    for mode in ('normal', 'sanitized'):
        build = stage/('build-'+mode)
        flags = [] if mode == 'normal' else [
            '-DCMAKE_CXX_FLAGS=-fsanitize=address,undefined -fno-sanitize-recover=all',
            '-DCMAKE_EXE_LINKER_FLAGS=-fsanitize=address,undefined']
        command(mode+'_configure', ['cmake','-S',stage/'host','-B',build,
                                    '-DCMAKE_BUILD_TYPE=Debug',*flags], stage, env)
        command(mode+'_build', ['cmake','--build',build,'--parallel','2'], stage, env)
        command(mode+'_run', ['ctest','--test-dir',build,'--output-on-failure','-V'], stage, env)
    for module in sys.argv[2:]:
        command(module.rsplit('.',1)[-1], [sys.executable,'-m','unittest',module,'-v'], stage, env)
    changed = {name:(expected,digest(root/name) if (root/name).is_file() else None)
               for name,expected in manifest.items()
               if not (root/name).is_file() or expected != digest(root/name)}
    (out/'source_changed_during_run.json').write_text(json.dumps(changed, indent=2)+'\n')
    print(json.dumps(dict(snapshot_files=len(manifest), source_changes_during_run=len(changed))), flush=True)
