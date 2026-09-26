# Records the first serial D202 host validation attempts with immutable input pins.
# Keeps the new oracle, historical probe and locked motor suites in separate owners.
# No board access; exact commands and first failures remain available for review.
import datetime
import hashlib
import json
from pathlib import Path
import shlex
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[3]
RAW = Path(__file__).resolve().parent
WSL_ROOT = '/mnt/c/Users/narut/OneDrive/Desktop/Project/techbots_Sumo_Robots'
RAW_REL = RAW.relative_to(ROOT).as_posix()


def main():
    assert sys.dont_write_bytecode
    assert len(sys.argv) == 2 and sys.argv[1] in ('metadata',)
    group = sys.argv[1]
    owner = RAW / (group + '_corrected_linux02')
    freeze = json.loads((RAW / 'coordinator_freeze02.json').read_text())
    for name, pin in freeze['files'].items():
        data = (ROOT / name).read_bytes()
        assert len(data) == pin['bytes'] and hashlib.sha256(data).hexdigest() == pin['sha256'], name
    owner.mkdir()
    target = WSL_ROOT + '/' + RAW_REL + '/' + owner.name + '/commands'
    if group == 'metadata':
        argv = ['env', 'TMPDIR=/dev/shm', 'SUMO_EXPECTED_METADATA_RECEIPT_DIR=' + target,
                'python3', '-I', '-B', 'tests/tooling/test_motor_expected_metadata.py']
    elif group == 'probe':
        argv = ['env', 'TMPDIR=/dev/shm', 'SUMO_SETTLE_PROBE_RECEIPT_DIR=' + target,
                'python3', '-I', '-B', 'tests/tooling/test_motor_settle_probe.py']
    else:
        methods = ['test_b3_b6_b7_actual_native_default_disabled_contract',
                   'test_b3_b6_b7_actual_native_host_only_enabled_contract']
        script = ('import runpy,sys;sys.argv=' + repr(['test_motor_port_unoq.py'] +
                  ['NativeMotorPortTests.' + method for method in methods]) +
                  ';runpy.run_path("tests/tooling/test_motor_port_unoq.py",run_name="__main__")')
        argv = ['env', 'TMPDIR=/dev/shm', 'SUMO_NATIVE_RECEIPT_DIR=' + target,
                'python3', '-I', '-B', '-c', script]
    command = ['wsl', '-d', 'Ubuntu', '--', 'bash', '-lc',
               'cd ' + shlex.quote(WSL_ROOT) + ' && exec ' + shlex.join(argv)]
    start = time.monotonic()
    record = dict(schema='d202-host-invocation-v1', group=group, argv=command,
                  started=datetime.datetime.now().astimezone().isoformat())
    (owner / 'intent.json').write_text(json.dumps(record, indent=2) + '\n')
    try:
        result = subprocess.run(command, cwd=ROOT, capture_output=True, timeout=1800)
    except subprocess.TimeoutExpired as error:
        result = subprocess.CompletedProcess(command, -1, error.stdout or b'', error.stderr or b'')
        record['timed_out'] = True
    (owner / 'stdout').write_bytes(result.stdout)
    (owner / 'stderr').write_bytes(result.stderr)
    record.update(returncode=result.returncode, elapsed_seconds=time.monotonic()-start,
                  stdout_sha256=hashlib.sha256(result.stdout).hexdigest(),
                  stderr_sha256=hashlib.sha256(result.stderr).hexdigest())
    changed = [name for name, pin in freeze['files'].items()
               if hashlib.sha256((ROOT / name).read_bytes()).hexdigest() != pin['sha256']]
    record['changed_inputs'] = changed
    (owner / 'result.json').write_text(json.dumps(record, indent=2) + '\n')
    print(json.dumps(record))
    print(result.stdout.decode('utf-8', 'replace'))
    print(result.stderr.decode('utf-8', 'replace'))
    return 1 if result.returncode or changed else 0


if __name__ == '__main__':
    sys.exit(main())
