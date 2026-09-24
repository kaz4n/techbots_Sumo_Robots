"""Link independent frozen review probes to coordinator-built production objects."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import os
import re
import shlex
import subprocess
import sys

source, build, label = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3]
assert re.fullmatch(r'[A-Za-z0-9_]+', label)
out = Path(__file__).resolve().parent
probe = out / 'private_probes.cc'
record_path = out / (label + '_private.json')
assert not record_path.exists(), 'Keep original review receipts'
record = {'label': label, 'start': datetime.now(timezone.utc).isoformat(),
          'probe_sha256': hashlib.sha256(probe.read_bytes()).hexdigest(),
          'source': str(source), 'build': str(build), 'commands': []}
freeze = json.loads((out / 'private_freeze.json').read_text())
assert record['probe_sha256'] == freeze['sha256']
environment = os.environ.copy()
environment['ASAN_OPTIONS'] = 'detect_leaks=1:halt_on_error=1'
environment['UBSAN_OPTIONS'] = 'halt_on_error=1:print_stacktrace=1'
status = 0
with (out / (label + '_private.txt')).open('wb') as log:
    for motor in (0, 1):
        directory = build / 'CMakeFiles' / f'push_through_m{motor}_tests.dir'
        flags_text = (directory / 'flags.make').read_text()
        flags = []
        for key in ('CXX_DEFINES', 'CXX_INCLUDES', 'CXX_FLAGS'):
            match = re.search(r'^' + key + r' = (.*)$', flags_text, re.M)
            assert match, key
            flags += shlex.split(match.group(1))
        target = build / f'private_d131_m{motor}'
        obj = build / f'private_d131_m{motor}.o'
        compile_command = ['c++', *flags, '-I' + str(source / 'tests'),
                           '-c', str(probe), '-o', str(obj)]
        supplement_commands = []
        supplement_objects = []
        if '-DSUMOX_TIMING_EVIDENCE=1' in flags:
            timing_probe = out / 'private_timing_policy.cc'
            timing_hash = hashlib.sha256(timing_probe.read_bytes()).hexdigest()
            assert timing_hash == json.loads((out / 'private_timing_freeze.json').read_text())['sha256']
            record['timing_probe_sha256'] = timing_hash
            timing_object = build / f'private_timing_policy_m{motor}.o'
            supplement_commands.append(['c++', *flags, '-I' + str(source / 'tests'),
                                        '-c', str(timing_probe), '-o', str(timing_object)])
            supplement_objects.append(str(timing_object))
        link = shlex.split((directory / 'link.txt').read_text())
        filtered = []
        replaced_output = False
        for index, value in enumerate(link):
            if index and link[index - 1] == '-o':
                filtered.append(str(target)); replaced_output = True
            elif value.endswith('.o') and ('test_push_through.cc.o' in value or
                                          'test_push_through_safety.cc.o' in value or
                                          'test_push_through_timing.cc.o' in value):
                continue
            else:
                filtered.append(value)
        assert replaced_output
        filtered.append(str(obj))
        filtered.extend(supplement_objects)
        for command in (compile_command, *supplement_commands, filtered, [str(target)]):
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
record['returncode'] = status
record['end'] = datetime.now(timezone.utc).isoformat()
record_path.write_text(json.dumps(record, indent=2) + '\n')
print(label, 'private exit', status)
print((out / (label + '_private.txt')).read_text(errors='replace')[-7000:])
sys.exit(status)
