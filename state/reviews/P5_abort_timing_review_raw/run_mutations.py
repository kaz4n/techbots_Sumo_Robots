"""Run bounded D135 producer faults using one copied source and existing M1 objects."""
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
probe = out / 'mutation_probes.cc'
private = out / 'private_spec_probes.cc'
assert hashlib.sha256(private.read_bytes()).hexdigest() == 'f9eb1025f49238d985c7f5adf9c433cf3272433049deea09d6e92de23c8487ca'
record_path, log_path = out / (label + '_mutations.json'), out / (label + '_mutations.txt')
assert not record_path.exists() and not log_path.exists(), 'Preserve prior receipts'
work = build / ('private_d135_faults_' + label)
assert build.is_dir() and not work.exists(), 'Need existing production build and a new workspace'
directory = build / 'CMakeFiles/opener_timing_m1_tests.dir'
flags_text = (directory / 'flags.make').read_text()
flags = []
for key in ('CXX_DEFINES', 'CXX_INCLUDES', 'CXX_FLAGS'):
    match = re.search(r'^' + key + r' = (.*)$', flags_text, re.M)
    assert match, key
    flags.extend(shlex.split(match.group(1)))
assert '-DMOTORS_ALLOWED=1' in flags and '-DSUMOX_P5_ABORT_TIMING=1' in flags
link = shlex.split((directory / 'link.txt').read_text())
excluded = {'test_abort_codec.cc.o', 'test_abort_openers.cc.o', 'test_abort_robot.cc.o',
            'test_abort_runtime.cc.o', 'test_abort_recording.cc.o', 'test_abort_timing_safety.cc.o'}
receive = 'void Robot::receive(const RobotInput& input) {\n'
save = '    prepareFrame(input);\n}'
faults = [
    (1, 'fsm_robot.cpp', '            opener_active_ = false;\n            routeNormal(true);',
     '            opener_active_ = false;\n            /* Isolated missing actual route. */'),
    (2, 'fsm_robot.cpp', '            markOpenerHandover();',
     '            markOpenerHandover();\n            tick_.selected = core::State::SEARCH;'),
    (3, 'fsm_opener_timing.cpp', '    tick_.abort_token = result_.token;',
     '    tick_.abort_token = result_.token ^ (std::uint64_t{1} << 32U);'),
    (4, 'fsm_robot.cpp', save,
     '    prepareFrame(input);\n    pending_.abort_handover = false;\n}'),
    (5, 'fsm_robot.cpp', receive, receive +
     '    if (abort_trace_phase_ == AbortTracePhase::RECEIPT) pending_.valid = false;\n'),
    (6, 'fsm_robot.cpp', receive, receive +
     '    if (pending_.valid && pending_.abort_handover) abort_trace_phase_ = AbortTracePhase::WAITING;\n'),
    (7, 'fsm_robot.cpp', save, '    prepareFrame(input);\n'
     '    if (abort_trace_phase_ == AbortTracePhase::RECEIPT) next_token_ = 0U;\n}'),
    (8, 'fsm_robot.cpp', save, '    prepareFrame(input);\n'
     '    if (attempt_go_ && abort_trace_phase_ == AbortTracePhase::WAITING) next_token_ = 0U;\n}'),
]
originals = {name: (source / 'src/core' / name).read_bytes() for _, name, _, _ in faults}
record = {'label': label, 'start_utc': datetime.now(timezone.utc).isoformat(),
          'source': str(source), 'build': str(build), 'work': str(work),
          'scope': 'post-review isolated copied-source producer faults, synthetic M1 callbacks',
          'runner_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
          'probe_sha256': hashlib.sha256(probe.read_bytes()).hexdigest(),
          'source_sha256': {name: hashlib.sha256(data).hexdigest() for name, data in originals.items()},
          'compile_flags': flags, 'cases': []}
env = os.environ.copy()
env['ASAN_OPTIONS'] = 'detect_leaks=1:halt_on_error=1'
env['UBSAN_OPTIONS'] = 'halt_on_error=1:print_stacktrace=1'
work.mkdir()
status = 0
with log_path.open('xb') as log:
    try:
        for number, name, before, after in faults:
            text = originals[name].decode('utf-8').replace('\r\n', '\n')
            assert text.count(before) == 1, 'Injection anchor changed: ' + str(number)
            mutated = text.replace(before, after)
            copied = work / ('case_' + str(number) + '_' + name)
            copied.write_text(mutated, encoding='utf-8')
            obj, test_obj = work / f'case_{number}.o', work / f'probe_{number}.o'
            executable = work / f'case_{number}'
            filtered, removed, replaced, retained = [], set(), 0, {}
            output_replaced = False
            for index, value in enumerate(link):
                basename = value.rsplit('/', 1)[-1]
                if index and link[index - 1] == '-o':
                    filtered.append(str(executable)); output_replaced = True
                elif basename in excluded:
                    removed.add(basename)
                elif basename == name + '.o':
                    filtered.append(str(obj)); replaced += 1
                else:
                    filtered.append(value)
                    if value.endswith('.o'):
                        assert '/tests/' not in value, 'Unexpected public test object'
                        retained[value] = hashlib.sha256((build / value).read_bytes()).hexdigest()
            assert removed == excluded and replaced == 1 and output_replaced
            assert any(value.endswith('/motor_gate_main.cpp.o') for value in retained)
            filtered.append(str(test_obj))
            case = {'case': number, 'original': name, 'before': before, 'after': after,
                    'mutated_sha256': hashlib.sha256(copied.read_bytes()).hexdigest(),
                    'retained_object_sha256': retained, 'commands': []}
            record['cases'].append(case)
            commands = ([link[0], *flags, '-I' + str(source / 'src/core'),
                         '-c', str(copied), '-o', str(obj)],
                        [link[0], *flags, '-I' + str(source / 'tests'),
                         f'-DD135_FAULT_CASE={number}', '-c', str(probe), '-o', str(test_obj)],
                        filtered, [str(executable), '--test-case=D135 isolated producer fault'])
            for command in commands:
                log.write(('COMMAND ' + shlex.join(command) + '\n').encode()); log.flush()
                result = subprocess.run(command, cwd=build, env=env, stdout=log, stderr=subprocess.STDOUT)
                case['commands'].append({'argv': command, 'returncode': result.returncode})
                log.flush()
                if result.returncode:
                    status = result.returncode
                    break
            if status:
                break
    except (AssertionError, OSError, ValueError) as error:
        status = 1; record['runner_error'] = str(error)
        log.write(('RUNNER ERROR: ' + str(error) + '\n').encode())
record['original_sources_unchanged'] = all((source / 'src/core' / name).read_bytes() == data
                                         for name, data in originals.items())
if not record['original_sources_unchanged']:
    status = 1
record['returncode'] = status
record['end_utc'] = datetime.now(timezone.utc).isoformat()
record_path.write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8')
print(label, 'isolated mutations exit', status)
print(log_path.read_text(errors='replace')[-2000:])
sys.exit(status)
