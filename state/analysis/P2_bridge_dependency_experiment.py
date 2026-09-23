"""Run only D098's exact isolated compile branches; never upload or alter packages."""
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys

root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(root / 'tools'))
import board_tool as board

source, branch = sys.argv[1:]
if not re.fullmatch('[0-9a-f]{64}', source) or branch not in ('control', 'candidate'):
    raise SystemExit('Expected exact source SHA256 and control/candidate')
stage = root / 'build/stage/app'
if board.source_hash(stage) != source:
    raise SystemExit('Current staged app is not the named source')
raw = root / 'state/analysis/P2_bridge_dependency_raw'
raw.mkdir(exist_ok=True)
receipt = raw / (source[:8] + '_' + branch + '.json')
if receipt.exists():
    raise SystemExit('Preserve previous experiment receipt')
remote_root = board.setting('SUMO_REMOTE_ROOT', r'/[A-Za-z0-9_./-]+')
sketch = remote_root + '/' + source + '/app'
output = remote_root + '/_dependency_probes/' + source + '/' + branch
files = {p.relative_to(stage).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
         for p in sorted(stage.rglob('*')) if p.is_file()}
verify = '''import hashlib,json,pathlib,sys
root=pathlib.Path(sys.argv[1]); expected=json.loads(sys.argv[2]); output=pathlib.Path(sys.argv[3])
if output.exists(): raise SystemExit('Existing experiment directory; refuse reuse')
for name,expected_hash in expected.items():
    p=root/name
    if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest()!=expected_hash:
        raise SystemExit('Source mismatch: '+name)
actual={p.relative_to(root).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
        for p in root.rglob('*') if p.is_file() and 'artifacts' not in p.relative_to(root).parts}
if actual!=expected: raise SystemExit('Unexpected source file set or bytes')
print(json.dumps(dict(source_files=len(expected),exact_file_set=True,output_absent=True)))
'''
verification_args = ['python3', '-c', verify, sketch, json.dumps(files), output]
board.verify_core(board.target())
verification = board.remote(board.target(), verification_args, capture=True, timeout=30)
args = ['arduino-cli', 'compile', '--fqbn', board.BASE_FQBN, '--verbose',
        '--build-path', output + '/build', '--output-dir', output + '/artifacts',
        '--build-property', 'compiler.cpp.extra_flags=-DMATCH=0 -DMOTORS_ALLOWED=0',
        '--build-property', 'compiler.c.extra_flags=-DMATCH=0 -DMOTORS_ALLOWED=0']
if branch == 'candidate':
    args += ['--build-property',
             'build.library_discovery_phase_flag=-DARDUINO_LIBRARY_DISCOVERY_PHASE=0']
args += [sketch]
started = datetime.now(timezone.utc).isoformat()
try:
    result = board.remote(board.target(), args, capture=True, timeout=600)
    code, stdout, stderr = result.returncode, result.stdout, result.stderr
except subprocess.CalledProcessError as error:
    code, stdout, stderr = error.returncode, error.stdout or '', error.stderr or ''
except subprocess.TimeoutExpired as error:
    code = 124
    stdout = error.stdout or b''
    stderr = error.stderr or b''
    stdout = stdout.decode(errors='replace') if isinstance(stdout, bytes) else stdout
    stderr = stderr.decode(errors='replace') if isinstance(stderr, bytes) else stderr
    stderr += '\nCOMPILE OBSERVATION TIMEOUT; verify remote process before any retry.\n'
output_name = source[:8] + '_' + branch
(raw / (output_name + '.stdout.txt')).write_text(stdout, encoding='utf-8')
(raw / (output_name + '.stderr.txt')).write_text(stderr, encoding='utf-8')
record = dict(source_sha256=source, branch=branch, argv=args, returncode=code,
              start_utc=started, end_utc=datetime.now(timezone.utc).isoformat(),
              source_files=files, source_verification_argv=verification_args,
              source_verification=json.loads(verification.stdout),
              build_path=output+'/build', output_path=output+'/artifacts',
              scope='Isolated compile-only experiment; no production flag adoption, upload, MCU or package change')
receipt.write_text(json.dumps(record, indent=2)+'\n')
print(json.dumps({k:record[k] for k in ('source_sha256','branch','returncode','build_path')}))
raise SystemExit(code)
