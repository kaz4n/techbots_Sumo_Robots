# Compiles only the approved B7 application profile, never uploads it.
# Reuses a checked private D222 caller while preserving its frozen public paths.
# Tested by B7 grammar, selection, policy and controlled caller fixtures.
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import sys
import types


ROOT = Path(__file__).absolute().parents[1]
BASE = 'tools/compile_commissioning_app.py'
BASE_PIN = (17992, '038a74777db7d26a15ff543d311fc4df2503e6f6b8e3b08fabcfb1c853220462')
CALLER = 'tools/compile_b7_app.py'
POLICY = 'tools/b7_app_static_policy.py'
REMOTE_HELPER = 'tools/b7_app_compile_remote.py'
CONTRACT = 'state/analysis/P2_b7_build_contract.md'
RAW = 'state/analysis/P2_b7_build_raw'
PROFILES = ('b7_brownout',)
ADDITIONAL = {CALLER, POLICY, REMOTE_HELPER, CONTRACT}
MACROS = ('SUMOX_B4_STAND', 'SUMOX_P3_DRIVE_TEST', 'SUMOX_P3_TURN_TRIAL',
          'SUMOX_P3_STOP_TRIAL', 'SUMOX_P4_REACTIVE', 'SUMOX_TIMING_EVIDENCE',
          'SUMOX_P5_ABORT_TIMING', 'SUMOX_MOTOR_FAULT_PROBE')


def require(condition, message):
    if not condition:
        raise ValueError(message)


def checked_request(value):
    keys = {'action', 'profile', 'motors_allowed', 'attempt', 'reviewed_head'}
    require(type(value) is dict and set(value) == keys and
            all(type(key) is str for key in value), 'Invalid request fields')
    require(type(value['action']) is str and value['action'] in ('--check-only', '--execute'),
            'Invalid action')
    _selection(value['profile'], value['motors_allowed'], value['attempt'])
    require(type(value['reviewed_head']) is str and
            re.fullmatch('[0-9a-f]{40}', value['reviewed_head']), 'Invalid reviewed HEAD')
    return dict(value)


def _selection(profile, motors_allowed, attempt):
    require(type(profile) is str and profile in PROFILES, 'Exact B7 profile required')
    require(type(motors_allowed) is int and motors_allowed in (0, 1), 'Exact motor integer required')
    require(type(attempt) is str and re.fullmatch('[a-z][a-z0-9_]{0,23}', attempt), 'Invalid attempt')


def parse_request(argv):
    require(type(argv) is list and all(type(item) is str for item in argv), 'Exact argument list required')
    require(len(argv) == 9 and argv[1::2] ==
            ['--profile', '--motors-allowed', '--attempt', '--reviewed-head'],
            'Expected action --profile b7_brownout --motors-allowed 0|1 --attempt TOKEN --reviewed-head HEAD')
    require(argv[4] in ('0', '1'), 'Explicit motor integer required')
    return checked_request(dict(action=argv[0], profile=argv[2], motors_allowed=int(argv[4]),
                                attempt=argv[6], reviewed_head=argv[8]))


def build_paths(profile, motors_allowed, attempt, source_digest):
    _selection(profile, motors_allowed, attempt)
    require(type(source_digest) is str and re.fullmatch('[0-9a-f]{64}', source_digest),
            'Invalid source digest')
    digest = hashlib.sha256((source_digest + '\0' + attempt).encode()).hexdigest()
    owner = 'commission-' + profile + '-m' + str(motors_allowed) + '-' + digest[:12]
    remote = '/home/arduino/sumox26_codex_build/' + owner
    stage = 'build/stage/' + owner
    return dict(owner=owner, output=RAW + '/' + owner, stage_owner=stage, stage=stage + '/app',
                remote=remote, build=remote + '/build', artifacts=remote + '/artifacts',
                sketch='/home/arduino/sumox26_codex_build/' + source_digest + '/app')


def _flags(profile, motors_allowed):
    _selection(profile, motors_allowed, 'selection')
    return ' '.join(['-DMATCH=0', '-DMOTORS_ALLOWED=' + str(motors_allowed)] +
                    ['-D' + name + '=0' for name in MACROS] + ['-DSUMOX_B7_BROWNOUT=1'])


def _checked_base(root):
    path = root / BASE
    for item in (*reversed(path.parents), path):
        info = item.lstat()
        require((stat.S_ISREG(info.st_mode) if item == path else stat.S_ISDIR(info.st_mode)) and
                not getattr(info, 'st_file_attributes', 0) & 1024, 'Nonplain bootstrap path')
    before = path.stat()
    require(before.st_nlink == 1 and before.st_size == BASE_PIN[0], 'Invalid bootstrap identity')
    flags = os.O_RDONLY | getattr(os, 'O_BINARY', 0) | getattr(os, 'O_NOFOLLOW', 0)
    with os.fdopen(os.open(path, flags), 'rb') as stream:
        opened = os.fstat(stream.fileno())
        raw = stream.read(BASE_PIN[0] + 1)
        closed = os.fstat(stream.fileno())
    stamp = lambda info: (info.st_dev, info.st_ino, info.st_mode, info.st_nlink,
                         info.st_size, info.st_mtime_ns)
    require(stamp(before) == stamp(opened) == stamp(closed) == stamp(path.stat()) and
            len(raw) == BASE_PIN[0] and hashlib.sha256(raw).hexdigest() == BASE_PIN[1],
            'Checked D222 bootstrap changed')
    module = types.ModuleType('_sumox_b7_checked_d222')
    module.__file__ = str(path)
    exec(compile(raw, str(path), 'exec'), module.__dict__)
    return module


def load_caller(request, *, root=ROOT):
    request, root = checked_request(request), Path(root).absolute()
    base = _checked_base(root)
    base.PROFILES, base.ROOT = PROFILES, root
    base.CALLER, base.POLICY, base.REMOTE_HELPER = CALLER, POLICY, REMOTE_HELPER
    base.CONTRACT, base.RAW = CONTRACT, RAW
    base.ADDITIONAL = base.ADDITIONAL | ADDITIONAL
    base.REQUIRED = base.REQUIRED | ADDITIONAL
    base._flags, base.build_paths = _flags, build_paths
    module = base.load_caller(request, root=root)
    module.HARD_PINS = dict(module.HARD_PINS, **{BASE: BASE_PIN[1]})
    return module


def make_owner(request, *, root=ROOT):
    request = checked_request(request)
    return load_caller(request, root=root).CompileDiagnostic(request['reviewed_head'], root=root)


def main(argv):
    request = parse_request(argv)
    require(sys.dont_write_bytecode, 'Python -B required')
    owner = make_owner(request, root=ROOT)
    try:
        result = owner.check() if request['action'] == '--check-only' else owner.run()
    except Exception as error:
        print(json.dumps(getattr(error, 'compile_outcome', dict(status='FAILED', first_error=dict(
            type=type(error).__name__, message=str(error)))), indent=2), file=sys.stderr)
        raise
    print(json.dumps(result, indent=2))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
