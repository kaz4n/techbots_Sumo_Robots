# Runs the fixed reviewed D114 passive collector once after its successful upload.
# Retains original command status, partial files and a checked transfer manifest.
# Scoped source review precedes execution; acquisition verdict stays in raw data.
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
import app_build_policy
import board_tool as board
import ui_adc_run as guard

RAW = ROOT / guard.RAW
TOOLS = '/home/arduino/sumox26-capture-tools/ui_adc_d114_run01'
FOLDER = '/home/arduino/sumox26-capture/ui-adc-d114-run01'
ARTIFACTS = '/home/arduino/sumox26-capture-input/ui_adc_probe_' + guard.SOURCE
MANIFEST_PROGRAM = r'''
import hashlib,json,pathlib,stat
p=pathlib.Path('/home/arduino/sumox26-capture/ui-adc-d114-run01')
assert p.is_dir() and not p.is_symlink()
for parent in p.parents: assert parent.is_dir() and not parent.is_symlink()
files=list(p.iterdir()); assert len(files)<=100
out={}; total=0
for f in files:
 s=f.lstat(); assert stat.S_ISREG(s.st_mode)
 assert s.st_size<=2097152
 total+=s.st_size; assert total<=10485760
 b=f.read_bytes(); assert len(b)==s.st_size
 out[f.name]={'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
print(json.dumps(out,sort_keys=True))
'''


def write(name, value):
    with (RAW / name).open('x', encoding='utf-8') as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.write('\n')


def command(argv, timeout):
    entry = dict(argv=argv, started_utc=datetime.now(timezone.utc).isoformat())
    try:
        result = board.remote(board.target(), argv, capture=True, timeout=timeout)
        entry.update(returncode=result.returncode, stdout=result.stdout, stderr=result.stderr)
    except (subprocess.SubprocessError, OSError) as error:
        entry.update(returncode=getattr(error, 'returncode', None), error=str(error),
                     stdout=guard.output_text(getattr(error, 'stdout', None)),
                     stderr=guard.output_text(getattr(error, 'stderr', None)))
    entry['finished_utc'] = datetime.now(timezone.utc).isoformat()
    return entry


def validate():
    assert board.target() == guard.TARGET and board.transport() == 'adb'
    run = json.loads(guard.safe_path(ROOT, guard.RUN_RECORD).read_text())
    approval_path = guard.safe_path(ROOT, guard.APPROVAL)
    approval = json.loads(approval_path.read_text())
    assert run['review_sha256'] == guard.file_hash(approval_path)
    assert approval['verdict'] == 'PASS_EXACT_INERT_ADC_SOURCE_TARGET_CAPTURE_GUARD'
    guard.identity(run)
    guard.identity(approval)
    for name, expected in approval['file_sha256'].items():
        assert guard.file_hash(guard.safe_path(ROOT, name)) == expected
    outcome = json.loads(guard.safe_path(ROOT, guard.OUTCOME).read_text())
    attempt = json.loads(guard.safe_path(ROOT, guard.ATTEMPT).read_text())
    assert attempt['approval_sha256'] == run['review_sha256']
    assert outcome['run_id'] == guard.RUN_ID and outcome['returncode'] == 0
    assert not outcome['timed_out'] and outcome['error'] is None
    return approval


def main():
    approval = validate()
    local = RAW / 'actual_run01'
    assert not local.exists(), 'Existing capture evidence is never reused'
    args = ['python3', TOOLS + '/ui_adc_capture.py', '--artifact-dir', ARTIFACTS,
            '--output', FOLDER]
    write('run01_capture_attempt.json', dict(argv=args, started_utc=datetime.now(timezone.utc).isoformat()))
    expected = {TOOLS + '/' + name: approval['file_sha256']['tools/' + name]
                for name in ('ui_adc_capture.py', 'p0_capture.py', 'p0_mem_read.cfg')}
    hashes = app_build_policy.verify_hashes(board.remote, board.target(), expected)
    write('run01_capture_tool_hashes.json', hashes)
    result = command(args, 620)
    write('run01_capture_command.json', result)
    manifest = command(['python3', '-c', MANIFEST_PROGRAM], 10)
    write('run01_capture_remote_manifest.json', manifest)
    assert manifest['returncode'] == 0, 'Evidence inventory failed; retain command result'
    expected_files = json.loads(manifest['stdout'])
    argv = [board.adb_executable(), '-s', board.target(), 'pull', FOLDER, str(local)]
    pull = subprocess.run(argv, capture_output=True, text=True, timeout=90)
    write('run01_capture_pull.json', dict(argv=argv, returncode=pull.returncode,
                                       stdout=pull.stdout, stderr=pull.stderr))
    assert pull.returncode == 0, 'Evidence transfer failed'
    actual = {}
    for path in local.iterdir():
        assert path.is_file() and not path.is_symlink()
        blob = path.read_bytes()
        actual[path.name] = dict(bytes=len(blob), sha256=hashlib.sha256(blob).hexdigest())
    write('run01_capture_local_manifest.json', actual)
    assert actual == expected_files, 'Transferred bytes differ from board originals'
    report = json.loads((local / 'capture.json').read_text())
    print(json.dumps({key: report.get(key) for key in ('collection_integrity', 'error',
          'diagnostic', 'capture_duration_seconds', 'memory_read_attempts', 'memory_bytes_requested')}, indent=2))
    return result['returncode'] if type(result['returncode']) is int else 1


if __name__ == '__main__':
    raise SystemExit(main())
