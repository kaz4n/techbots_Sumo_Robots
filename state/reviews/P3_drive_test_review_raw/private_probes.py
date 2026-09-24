"""Independent D123 config and policy probes; never executes firmware or transport."""
import copy
import hashlib
import importlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'tools'))
policy = importlib.import_module('app_build_policy')
FLAGS = '-DMATCH=0 -DMOTORS_ALLOWED=0 -DSUMOX_P3_DRIVE_TEST=1'
FQBN = 'arduino:zephyr:unoq'
BUILD = '/fixture/native-app-v1/source/default/run-one/build'
raw = (ROOT / 'tests/fixtures/app_build_policy/valid_result.json').read_text()
fixture = json.loads(raw.replace('app.ino', 'drive_test.ino').replace(
    '-DMATCH=0 -DMOTORS_ALLOWED=0', FLAGS))
checks = []

for name, defines, accepted in (
    ('legacy_default', [], True),
    ('explicit_default', ['SUMOX_P3_DRIVE_TEST=0'], True),
    ('p3_m0', ['SUMOX_P3_DRIVE_TEST=1', 'MOTORS_ALLOWED=0'], True),
    ('p3_m1_host', ['SUMOX_P3_DRIVE_TEST=1', 'MOTORS_ALLOWED=1'], True),
    ('p3_match_refusal', ['SUMOX_P3_DRIVE_TEST=1', 'MATCH=1'], False),
    ('p3_b4_refusal', ['SUMOX_P3_DRIVE_TEST=1', 'SUMOX_B4_STAND=1'], False),
    ('p3_negative_refusal', ['SUMOX_P3_DRIVE_TEST=-1'], False),
    ('p3_two_refusal', ['SUMOX_P3_DRIVE_TEST=2'], False),
    ('p3_empty_refusal', ['SUMOX_P3_DRIVE_TEST='], False),
    ('legacy_match', ['SUMOX_P3_DRIVE_TEST=0', 'MATCH=1', 'MOTORS_ALLOWED=1'], True),
    ('legacy_b4', ['SUMOX_P3_DRIVE_TEST=0', 'SUMOX_B4_STAND=1'], True),
):
    command = ['g++', '-std=c++17', '-fsyntax-only', '-x', 'c++', '-I',
               str(ROOT / 'src'), *['-D' + item for item in defines], '-']
    result = subprocess.run(command, input='#include "config.h"\nint main() {}\n',
                            text=True, capture_output=True, timeout=15)
    passed = (result.returncode == 0) == accepted
    checks.append(dict(name=name, kind='config_compile_only', command=command,
                       expected_accept=accepted, returncode=result.returncode,
                       stdout=result.stdout, stderr=result.stderr, passed=passed))

def validate(value):
    return policy.validate_result(json.dumps(value), FQBN, FLAGS, BUILD,
                                  project='drive_test.ino')

valid = validate(fixture)
checks.append(dict(name='private_positive_fixture', kind='tooling', passed=
                   valid['compiler.cpp.extra_flags'] == FLAGS))
for key, value in (
    ('compiler.S.extra_flags', '-DSUMOX_P3_DRIVE_TEST=1'),
    ('compiler.c.elf.extra_flags', '-DSUMOX_P3_DRIVE_TEST=1'),
    ('build.extra_flags', '-DSUMOX_P3_DRIVE_TEST=0'),
    ('build.extra_ldflags', '-Wl,--defsym,SUMOX_P3_DRIVE_TEST=0'),
    ('build.boot_mode', 'immediate'),
    ('compiler.c.extra_flags', FLAGS.replace('TEST=1', 'TEST=(1)')),
    ('compiler.cpp.extra_flags', FLAGS + ' -USUMOX_P3_DRIVE_TEST'),
    ('build.project_name', 'drive_test.ino '),
):
    value_fixture = copy.deepcopy(fixture)
    entries = value_fixture['builder_result']['build_properties']
    index = next(i for i, text in enumerate(entries) if text.startswith(key + '='))
    entries[index] = key + '=' + value
    try:
        validate(value_fixture)
    except ValueError as error:
        checks.append(dict(name=key, kind='tooling_refusal', passed=True, reason=str(error)))
    else:
        checks.append(dict(name=key, kind='tooling_refusal', passed=False))

files = ['src/config.h', 'tools/app_build_policy.py', 'tools/board_tool.py',
         'bench/drive_test/drive_test.ino']
report = dict(result='PASS' if all(check['passed'] for check in checks) else 'FAIL',
              checks=checks, count=len(checks), hashes={path: hashlib.sha256(
                  (ROOT / path).read_bytes()).hexdigest() for path in files},
              limitations=['Config-only host compiler probes and synthetic policy inputs.',
                           'No profile C++ tests or executable firmware executed.',
                           'No board connection, upload, reset or motor action.'])
(OUT / 'private_probes.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(dict(result=report['result'], count=len(checks))))
raise SystemExit(0 if report['result'] == 'PASS' else 1)
