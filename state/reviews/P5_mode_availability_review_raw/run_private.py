"""Link frozen D134 probes to the coordinator's existing production objects."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import os
import re
import shlex
import subprocess
import sys


source, build, label = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve(), sys.argv[3]
assert re.fullmatch(r'[A-Za-z0-9_]+', label), 'Unsafe receipt label'
out = Path(__file__).resolve().parent
probe = out / 'private_modes.cc'
record_path = out / (label + '_private.json')
log_path = out / (label + '_private.txt')
assert not record_path.exists() and not log_path.exists(), 'Preserve original receipts'
freeze = json.loads((out / 'private_freeze.json').read_text(encoding='utf-8-sig'))
for name, expected in freeze['files'].items():
    assert hashlib.sha256((out / name).read_bytes()).hexdigest() == expected, name
assert build.is_dir(), 'Coordinator build is unavailable; do not rebuild implicitly'
record = {
    'label': label, 'start_utc': datetime.now(timezone.utc).isoformat(),
    'source': str(source), 'build': str(build),
    'runner_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    'frozen_private_sha256': freeze['files'],
    'source_config_sha256': hashlib.sha256((source / 'src/config.h').read_bytes()).hexdigest(),
    'targets': [], 'commands': [],
}
environment = os.environ.copy()
environment['ASAN_OPTIONS'] = 'detect_leaks=1:halt_on_error=1'
environment['UBSAN_OPTIONS'] = 'halt_on_error=1:print_stacktrace=1'
excluded = {'test_mode_availability.cc.o', 'test_mode_availability_safety.cc.o'}
status = 0
with log_path.open('xb') as log:
    try:
        for motor in (0, 1):
            target_name = f'mode_availability_m{motor}_tests'
            directory = build / 'CMakeFiles' / (target_name + '.dir')
            flags_text = (directory / 'flags.make').read_text()
            flags = []
            for key in ('CXX_DEFINES', 'CXX_INCLUDES', 'CXX_FLAGS'):
                match = re.search(r'^' + key + r' = (.*)$', flags_text, re.M)
                assert match, key
                flags.extend(shlex.split(match.group(1)))
            assert f'-DMOTORS_ALLOWED={motor}' in flags, 'Motor profile mismatch'
            link = shlex.split((directory / 'link.txt').read_text())
            assert link, 'Missing original link command'
            output = build / f'private_d134_m{motor}'
            obj = build / f'private_d134_m{motor}.o'
            filtered, removed, retained = [], set(), []
            output_replaced = False
            for index, value in enumerate(link):
                name = value.rsplit('/', 1)[-1]
                if index and link[index - 1] == '-o':
                    filtered.append(str(output)); output_replaced = True
                elif name in excluded:
                    removed.add(name)
                else:
                    filtered.append(value)
                    if value.endswith('.o'):
                        assert (build / value).is_file(), 'Missing original object: ' + value
                        retained.append(value)
            assert output_replaced, 'Original link output not found'
            assert removed == excluded, 'Unexpected public test object set'
            assert any(value.endswith('/motor_gate_main.cpp.o') for value in retained), 'Missing genuine test main'
            filtered.append(str(obj))
            compile_command = [link[0], *flags, '-I' + str(source / 'tests'),
                               '-c', str(probe), '-o', str(obj)]
            record['targets'].append({
                'name': target_name, 'motor': motor, 'excluded_objects': sorted(removed),
                'retained_objects': len(retained), 'compile_flags': flags,
            })
            for command in (compile_command, filtered, [str(output)]):
                log.write(('COMMAND ' + shlex.join(command) + '\n').encode()); log.flush()
                result = subprocess.run(command, cwd=build, env=environment,
                                        stdout=log, stderr=subprocess.STDOUT)
                record['commands'].append({'motor': motor, 'argv': command,
                                           'returncode': result.returncode})
                log.flush()
                if result.returncode:
                    status = result.returncode
                    break
            if status:
                break
    except (OSError, AssertionError, ValueError) as error:
        status = 1
        record['runner_error'] = str(error)
        log.write(('RUNNER ERROR: ' + str(error) + '\n').encode())
record['returncode'] = status
record['end_utc'] = datetime.now(timezone.utc).isoformat()
record_path.write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8')
print(label, 'private exit', status)
print(log_path.read_text(errors='replace')[-1600:])
sys.exit(status)
