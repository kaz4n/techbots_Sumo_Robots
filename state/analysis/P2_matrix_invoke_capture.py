"""Invoke the one reviewed D088 read-only runtime capture on the identified board."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(root / 'tools'))
import board_tool as board

raw = root / 'state/analysis/P2_matrix_raw'
approval = json.loads((raw / 'review/approved_inert_sources.json').read_text())
assert board.transport() == 'adb' and board.target() == '2629958581'
destination = '/home/arduino/sumox26-ui-capture-e50c6da3'
files = [root / 'state/analysis/P2_matrix_runtime_capture.py',
         root / 'tools/p0_capture.py', root / 'tools/p0_mem_read.cfg']
expected = {
    'P2_matrix_runtime_capture.py': approval['capture_wrapper_sha256'],
    'p0_capture.py': '885c4e4206aea4ac9e03c4e92e48258db2a0ae302ff83a86430e6913afeeb57c',
    'p0_mem_read.cfg': '89d16a28a1489c23ec743be55ade39824f9ca5213b02b20ef4785079122e4339',
}
for path in files:
    assert hashlib.sha256(path.read_bytes()).hexdigest() == expected[path.name]
board.remote(board.target(), ['mkdir', '-p', destination])
for path in files:
    subprocess.run([board.adb_executable(), '-s', board.target(), 'push', str(path),
                    destination + '/' + path.name], check=True, stdin=subprocess.DEVNULL)
check = """import hashlib,json,pathlib,sys
p=pathlib.Path(sys.argv[1]); expected=json.loads(sys.argv[2])
for name,digest in expected.items():
 assert hashlib.sha256((p/name).read_bytes()).hexdigest()==digest,name
print('Remote capture files match reviewed hashes')
"""
board.remote(board.target(), ['python3', '-c', check, destination, json.dumps(expected)])
artifact = (os.environ['SUMO_REMOTE_ROOT'] + '/'
            'e50c6da38bba5131e426d8c076e7aa7c8aad5961f60a6eb1387b1f2412aab6af/'
            'ui_matrix/artifacts/bench-default')
args = ['python3', destination + '/P2_matrix_runtime_capture.py', '--artifact-dir', artifact]
try:
    result = board.remote(board.target(), args, capture=True, timeout=150)
except subprocess.CalledProcessError as error:
    (raw / 'runtime_failed_stdout.txt').write_text(error.stdout or '', encoding='utf-8')
    (raw / 'runtime_failed_stderr.txt').write_text(error.stderr or '', encoding='utf-8')
    raise
(raw / 'runtime_stdout.txt').write_text(result.stdout, encoding='utf-8')
(raw / 'runtime_stderr.txt').write_text(result.stderr, encoding='utf-8')
report = json.loads(result.stdout)
(raw / 'runtime_report.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
folder = report['capture_directory']
assert folder.startswith('/home/arduino/sumox26-capture/') and '..' not in folder
assert not (raw / 'runtime_run1').exists()
subprocess.run([board.adb_executable(), '-s', board.target(), 'pull', folder,
                str(raw / 'runtime_run1')], check=True, stdin=subprocess.DEVNULL)
print(json.dumps(dict(status=report['status'], capture_directory=folder,
                      counter=report.get('counter'), argv=args)))
