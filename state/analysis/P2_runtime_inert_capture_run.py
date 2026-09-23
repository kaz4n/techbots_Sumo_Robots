# Runs only the reviewed fixed D104 MEM-AP reader and preserves its raw receipt.
# Separates successful collection from actual experiment acceptance.
# Local guard tests and independent review precede any execution on the bare UNO Q.
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
import board_tool as board

RAW = ROOT / 'state/analysis/P2_runtime_inert_raw'
REVIEW = ROOT / 'state/reviews/P2_runtime_inert_review_raw/final_approval.json'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')


def main():
    review = json.loads(REVIEW.read_text())
    assert review['verdict'] == 'PASS_SCOPED_SOURCE_AND_CAPTURE_REVIEW'
    assert board.target() == '2629958581' and board.transport() == 'adb'
    assert review['source_sha256'] == '2bd817c4e535324964a031cdd44720f26fd145a3cd317ab7b3ced089f35db7e5'
    assert sha(ROOT / 'tools/runtime_capture.py') == review['capture_sha256']
    assert sha(ROOT / 'tools/board_tool.py') == review['board_tool_sha256']
    files = [ROOT / 'tools' / name for name in
             ('runtime_capture.py', 'recorder_heap.py', 'p0_capture.py', 'p0_mem_read.cfg')]
    tool_folder = '/home/arduino/sumox26-capture-tools/runtime-' + review['capture_sha256'][:12]
    folder = '/home/arduino/sumox26-capture/runtime-d104-capture1'
    local = RAW / 'runtime_run1'
    assert not local.exists(), 'Preserve existing evidence; no implicit retry'
    record_path = RAW / 'capture_run1_command.json'
    with record_path.open('x', encoding='utf-8') as stream:
        stream.write(json.dumps(dict(status='ATTEMPT_STARTED', utc=datetime.now(timezone.utc).isoformat())))
    sync = []
    result = board.remote(board.target(), ['mkdir', '-p', tool_folder], capture=True)
    sync.append(dict(argv=result.args, returncode=result.returncode, stdout=result.stdout, stderr=result.stderr))
    for path in files:
        argv = [board.adb_executable(), '-s', board.target(), 'push', str(path), tool_folder + '/' + path.name]
        result = subprocess.run(argv, capture_output=True, text=True, timeout=30)
        sync.append(dict(argv=argv, returncode=result.returncode, stdout=result.stdout, stderr=result.stderr))
        write(RAW / 'capture_tool_sync.json', dict(folder=tool_folder, commands=sync))
        if result.returncode != 0: raise RuntimeError('Capture tool sync failed')
    expected = {tool_folder + '/' + path.name: sha(path) for path in files}
    import app_build_policy
    observed = app_build_policy.verify_hashes(board.remote, board.target(), expected)
    write(RAW / 'capture_tool_hashes.json', observed)
    args = ['python3', tool_folder + '/runtime_capture.py', '--artifact-dir', review['artifact_dir'], '--output', folder]
    start = datetime.now(timezone.utc).isoformat()
    try:
        result = board.remote(board.target(), args, capture=True, timeout=620)
        code, out, err = result.returncode, result.stdout, result.stderr
    except subprocess.CalledProcessError as error:
        code, out, err = error.returncode, error.stdout, error.stderr
    except subprocess.TimeoutExpired as error:
        code, out, err = 124, error.stdout, str(error)
    except OSError as error:
        code, out, err = 126, '', str(error)
    if isinstance(out, bytes):
        out = out.decode('utf-8', errors='replace')
    if isinstance(err, bytes):
        err = err.decode('utf-8', errors='replace')
    write(record_path, dict(argv=args, returncode=code, stderr=err, start_utc=start,
                           end_utc=datetime.now(timezone.utc).isoformat()))
    (RAW / 'capture_run1_stdout.json').write_text(out or '', encoding='utf-8')
    argv = [board.adb_executable(), '-s', board.target(), 'pull', folder, str(local)]
    pulled = subprocess.run(argv, capture_output=True, text=True, timeout=90)
    write(RAW / 'capture_run1_pull.json', dict(argv=argv, returncode=pulled.returncode,
          stdout=pulled.stdout, stderr=pulled.stderr))
    if pulled.returncode != 0: raise RuntimeError('Capture evidence pull failed')
    manifest = {p.relative_to(local).as_posix(): sha(p) for p in local.rglob('*') if p.is_file()}
    write(RAW / 'capture_run1_manifest.json', manifest)
    report = json.loads((local / 'capture.json').read_text())
    print(json.dumps({key: report.get(key) for key in
          ('status', 'error', 'diagnostics', 'heap', 'capture_duration_seconds',
           'memory_read_attempts', 'memory_bytes_requested')}, indent=2))
    return code


if __name__ == '__main__':
    raise SystemExit(main())
