# Observes one fixed static diagnostic packet through the existing validators.
# Keeps board artifact bytes local while retaining descriptor and postcheck evidence.
# Tested by independent D188 fixtures before any separately admitted native use.
import hashlib
import os
from pathlib import Path
import types


REMOTE = '/home/arduino/sumox26_codex_build/app-motor-fault-static01'
BUILD = REMOTE + '/build'
ARTIFACTS = REMOTE + '/artifacts'
PROJECT = 'app_motor_fault.ino'
FQBN = 'arduino:zephyr:unoq:link_mode=static'
FLAGS = '-DMATCH=0 -DMOTORS_ALLOWED=0 -DSUMOX_MOTOR_FAULT_PROBE=1'
CORE = '/home/arduino/.arduino15/packages/arduino/hardware/zephyr/1.0.0'
LOADER = CORE + '/firmwares/zephyr-arduino_uno_q_stm32u585xx.elf'
TLS = CORE + '/variants/arduino_uno_q_stm32u585xx/tls-syms.S'
LOADER_SHA = '39d4a4fd47241663323f6e04f94dd8f5a9f9ad6582cf1df37f9709b74026adcd'
TLS_SHA = '68bb147615813666d528b9bd650e02fb8e240f0db841939e8460d7a52fd2ee70'
PINS = {
    'helper': '8ba9b190c38e728013a383348c60c287b0366607f65f703161cf7f2e142d36f8',
    'adapter': '3e5d49e4a70c0cf6197e26b1ba5ce2b7e07601bf5d9250ba430f90d1f9eab270',
    'extension': 'cd52a29a32b8ae1da4bea51dd55d9011386dd4be0ca537195bb124d13031d6c0',
    'base': 'd30372dd4b8fb8c2661d00affc4a215cc88e3f62511995ff6303827bed4b7368',
}
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
    require(type(bundle) is dict and set(bundle) == set(PINS), 'Invalid artifact source bundle')
    for name, digest in PINS.items():
        raw = bundle[name]
        require(type(raw) is bytes and 0 < len(raw) <= 65536 and
                hashlib.sha256(raw).hexdigest() == digest, 'Artifact source changed: ' + name)
    helper = types.ModuleType('_sumox_d188_reader')
    exec(compile(bundle['helper'], '<checked-static-reader>', 'exec'), helper.__dict__)
    adapter = types.ModuleType('_sumox_d188_adapter')
    adapter.__file__ = '/sumox-source/tools/app_motor_fault_static_policy.py'
    exec(compile(bundle['adapter'], adapter.__file__, 'exec'), adapter.__dict__)

    def checked_extension(name):
        require(name == adapter._ARTIFACTS, 'Unexpected artifact dependency')
        return bundle['extension']

    adapter._checked_source = checked_extension
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
        exported_flat_package=payloads['artifacts/' + PROJECT + '.bin-zsk.bin'])


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
    result = dict(schema='app-motor-fault-static-artifacts-v1', status='FAILED',
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
