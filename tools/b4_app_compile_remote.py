# Observes one fixed inhibited B4 ordinary-app static artifact packet.
# Binds checked snapshots to the accepted policy and retains descriptor evidence.
# Tested by independent D214 controlled cases before any admitted native use.
import hashlib
import os
from pathlib import Path
import types


REMOTE = '/home/arduino/sumox26_codex_build/b4-app-m0-static01'
BUILD = REMOTE + '/build'
ARTIFACTS = REMOTE + '/artifacts'
PROJECT = 'app.ino'
FQBN = 'arduino:zephyr:unoq:link_mode=static'
FLAGS = '-DMATCH=0 -DMOTORS_ALLOWED=0 -DSUMOX_B4_STAND=1 -DSUMOX_P3_DRIVE_TEST=0 -DSUMOX_P3_TURN_TRIAL=0 -DSUMOX_P3_STOP_TRIAL=0 -DSUMOX_P4_REACTIVE=0 -DSUMOX_TIMING_EVIDENCE=0 -DSUMOX_P5_ABORT_TIMING=0 -DSUMOX_MOTOR_FAULT_PROBE=0'
CORE = '/home/arduino/.arduino15/packages/arduino/hardware/zephyr/1.0.0'
LOADER = CORE + '/firmwares/zephyr-arduino_uno_q_stm32u585xx.elf'
TLS = CORE + '/variants/arduino_uno_q_stm32u585xx/tls-syms.S'
LOADER_SHA = '39d4a4fd47241663323f6e04f94dd8f5a9f9ad6582cf1df37f9709b74026adcd'
TLS_SHA = '68bb147615813666d528b9bd650e02fb8e240f0db841939e8460d7a52fd2ee70'
PINS = {'helper': '8ba9b190c38e728013a383348c60c287b0366607f65f703161cf7f2e142d36f8', 'policy': 'aadccdbb0a92338a90a789251f691a42e029c7f73b312b638b85d04c5d2d4ddf', 'adapter': '3e5d49e4a70c0cf6197e26b1ba5ce2b7e07601bf5d9250ba430f90d1f9eab270', 'common': 'adc7f42a3325381c3cf15122409dfe9d92db7ca187cb242e416fef356be667f8', 'static_policy': 'ec3d8a5e8c4910bbdbbb96fb5123c8bb42b294ce9342c76db73b8d3b5eab7775', 'reference': '1dc8ac6dec8534536acfcc4da73516416ea465cfcc1a349900fd13e210144a2b', 'extension': 'cd52a29a32b8ae1da4bea51dd55d9011386dd4be0ca537195bb124d13031d6c0', 'base': 'd30372dd4b8fb8c2661d00affc4a215cc88e3f62511995ff6303827bed4b7368'}
SIZES = {'helper': 33321, 'policy': 4055, 'adapter': 8262, 'common': 14956, 'static_policy': 4836, 'reference': 17809, 'extension': 3718, 'base': 18322}
SNAPSHOT_PATHS = {'adapter': 'tools/app_motor_fault_static_policy.py', 'common': 'tools/app_build_policy.py', 'static_policy': 'state/analysis/P7_static_link_probe_raw/static_policy.py', 'reference': 'state/analysis/P7_static_link_probe_raw/static_reference.json', 'extension': 'state/analysis/P7_static_link_probe_raw/static_native_artifacts.py'}
SUFFIX_LIMITS = {'.elf': 16777216, '_debug.elf': 16777216,
                 '_temp.elf': 16777216, '.bin': 786416,
                 '.bin-zsk.bin': 786432, '.elf-zsk.bin': 16777216,
                 '.map': 16777216}
FILE_LIMITS = {'build/' + PROJECT + suffix: limit
               for suffix, limit in SUFFIX_LIMITS.items()}
FILE_LIMITS['artifacts/' + PROJECT + '.bin-zsk.bin'] = 786432


def require(condition, message):
    if not condition:
        raise ValueError(message)


def error_value(error):
    return {'type': type(error).__name__, 'message': str(error)}


def load_bundle(bundle):
    require(type(bundle) is dict and all(type(name) is str for name in bundle) and
            set(bundle) == set(PINS), 'Invalid artifact source bundle')
    bundle = dict(bundle)
    for name, digest in PINS.items():
        raw = bundle[name]
        require(type(raw) is bytes and len(raw) == SIZES[name] and len(raw) <= 65536 and
                hashlib.sha256(raw).hexdigest() == digest, 'Artifact source changed: ' + name)
    helper = types.ModuleType('_sumox_d214_reader')
    exec(compile(bundle['helper'], '<checked-static-reader>', 'exec'), helper.__dict__)
    adapter = types.ModuleType('_sumox_d214_policy')
    adapter.__file__ = '/sumox-source/tools/b4_app_static_policy.py'
    exec(compile(bundle['policy'], adapter.__file__, 'exec'), adapter.__dict__)
    return helper, adapter


def installed(helper, root_fd, path, limit, digest):
    parent, name = path.rsplit('/', 1)
    with helper.directory(root_fd, parent) as folder:
        raw, identity = helper.read_file(folder, name, limit)
    record = helper.file_record('regular', identity, helper.sha256(raw))
    require(record['sha256'] == digest, 'Installed input changed: ' + name)
    return raw, record


def artifact_files(helper, root_fd, build_path, artifacts_path, records):
    payloads = {}
    for group, path in (('build', build_path), ('artifacts', artifacts_path)):
        with helper.directory(root_fd, path) as folder:
            for key, limit in FILE_LIMITS.items():
                selected, name = key.split('/')
                if selected == group:
                    records[key], payloads[key] = helper.observe_file(folder, name, limit)
    require(set(records) == set(FILE_LIMITS) and
            all(value['state'] == 'regular' for value in records.values()),
            'Incomplete, empty, linked, oversized or unstable artifact packet')
    return payloads


def first_observation(helper, adapter, root_fd, bundle, result):
    payloads = artifact_files(helper, root_fd, result['build_path'],
                             result['artifacts_path'], result['files'])
    _, result['loader'] = installed(helper, root_fd, LOADER, 16777216, LOADER_SHA)
    tls, result['tls_source'] = installed(helper, root_fd, TLS, 65536, TLS_SHA)
    inputs = {key.split('/')[1]: raw for key, raw in payloads.items() if key.startswith('build/')}
    result['layout'] = adapter.validate_artifacts(inputs, tls, bundle['base'],
        exported_flat_package=payloads['artifacts/' + PROJECT + '.bin-zsk.bin'],
        motors_allowed=0, snapshots={path: bundle[name] for name, path in SNAPSHOT_PATHS.items()})


def final_observation(helper, root_fd, name, result):
    require(root_fd is not None, 'Filesystem root was not opened')
    if name == 'files':
        after = {}
        artifact_files(helper, root_fd, result['build_path'], result['artifacts_path'], after)
        require(after == result['files'], 'Artifact identities changed after validation')
    else:
        path, limit, digest = ((LOADER, 16777216, LOADER_SHA) if name == 'loader'
                               else (TLS, 65536, TLS_SHA))
        _, after = installed(helper, root_fd, path, limit, digest)
        require(after == result[name], 'Installed identity changed after validation: ' + name)


def inspect_artifacts(build_path, artifacts_path, bundle, *, fs_root=Path('/')):
    require(type(build_path) is str and build_path == BUILD and
            type(artifacts_path) is str and artifacts_path == ARTIFACTS,
            'Unexpected static diagnostic artifact paths')
    require(isinstance(fs_root, Path) and fs_root.is_absolute(), 'Absolute filesystem root required')
    helper, adapter = load_bundle(bundle)
    result = dict(schema='b4-app-m0-static-artifacts-v1', status='FAILED',
        build_path=build_path, artifacts_path=artifacts_path, files={}, loader=None,
        tls_source=None, layout=None, postchecks=[], first_error=None)
    root_fd = None
    try:
        try:
            root_fd = os.open(fs_root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC)
            first_observation(helper, adapter, root_fd, bundle, result)
        except Exception as error:
            result['first_error'] = error_value(error)
        for name in ('loader', 'tls_source', 'files'):
            try:
                final_observation(helper, root_fd, name, result)
                row = dict(name=name, status='PASS', error=None)
            except Exception as error:
                value = error_value(error)
                result['first_error'] = result['first_error'] or value
                row = dict(name=name, status='FAILED', error=value)
            result['postchecks'].append(row)
    finally:
        if root_fd is not None:
            try:
                os.close(root_fd)
            except Exception as error:
                result['first_error'] = result['first_error'] or error_value(error)
    if result['first_error'] is None:
        result['status'] = 'ARTIFACTS_CHECKED'
    return result
