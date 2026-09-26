# Checks the ordinary application commissioning profiles using reviewed byte snapshots.
# Keeps commissioning metadata separate from permission to upload or run motors.
# Tested by independent D222 profile, metadata and artifact contract cases.
import hashlib
from pathlib import Path


PROJECT = 'app.ino'
FQBN = 'arduino:zephyr:unoq:link_mode=static,wait_linux_boot=no'
_ROOT = Path(__file__).absolute().parents[1]
_ADAPTER = 'tools/app_motor_fault_static_policy.py'
_RAW = 'state/analysis/P7_static_link_probe_raw/'
SNAPSHOT_PINS = {
    _ADAPTER: (8262, '3e5d49e4a70c0cf6197e26b1ba5ce2b7e07601bf5d9250ba430f90d1f9eab270'),
    'tools/app_build_policy.py': (14956, 'adc7f42a3325381c3cf15122409dfe9d92db7ca187cb242e416fef356be667f8'),
    _RAW + 'static_policy.py': (4836, 'ec3d8a5e8c4910bbdbbb96fb5123c8bb42b294ce9342c76db73b8d3b5eab7775'),
    _RAW + 'static_reference.json': (17809, '1dc8ac6dec8534536acfcc4da73516416ea465cfcc1a349900fd13e210144a2b'),
    _RAW + 'static_native_artifacts.py': (3718, 'cd52a29a32b8ae1da4bea51dd55d9011386dd4be0ca537195bb124d13031d6c0'),
}


PROFILES = ('match',)
_MACROS = ('SUMOX_B4_STAND', 'SUMOX_P3_DRIVE_TEST', 'SUMOX_P3_TURN_TRIAL',
           'SUMOX_P3_STOP_TRIAL', 'SUMOX_P4_REACTIVE', 'SUMOX_TIMING_EVIDENCE',
           'SUMOX_P5_ABORT_TIMING', 'SUMOX_MOTOR_FAULT_PROBE')
_ENABLED = dict(match=())


def safety_flags(profile, *, motors_allowed):
    if type(profile) is not str or profile not in PROFILES:
        raise ValueError('Exact commissioning profile required')
    if type(motors_allowed) is not int or motors_allowed != 1:
        raise ValueError('Explicit integer motors_allowed 0 or 1 required')
    values = [('MATCH', 1), ('MOTORS_ALLOWED', motors_allowed)]
    values.extend((name, int(index in _ENABLED[profile]))
                  for index, name in enumerate(_MACROS))
    return ' '.join('-D' + name + '=' + str(value) for name, value in values)


def _snapshots(values):
    if type(values) is not dict or any(type(name) is not str for name in values):
        raise ValueError('Exactly five reviewed policy snapshots required')
    saved = dict(values)
    if saved.keys() != SNAPSHOT_PINS.keys():
        raise ValueError('Exactly five reviewed policy snapshots required')
    for name, (size, digest) in SNAPSHOT_PINS.items():
        body = saved[name]
        if (type(body) is not bytes or len(body) != size or
                hashlib.sha256(body).hexdigest() != digest):
            raise ValueError('Reviewed policy snapshot differs: ' + name)
    return saved


def _policy(profile, motors_allowed, snapshots):
    flags = safety_flags(profile, motors_allowed=motors_allowed)
    saved = _snapshots(snapshots)
    namespace = {'__name__': '_sumox_commissioning_static_policy',
                 '__file__': str(_ROOT / _ADAPTER)}
    exec(compile(saved[_ADAPTER], namespace['__file__'], 'exec'), namespace)
    # Every dependency read is satisfied from this call's checked immutable bytes.
    namespace['_checked_source'] = lambda name: saved[name]
    namespace.update(PROJECT=PROJECT, FQBN=FQBN, FLAGS=flags)
    namespace['_ALIASES'] = {PROJECT + suffix: PROJECT + suffix for suffix in (
        '.elf', '_debug.elf', '_temp.elf', '.bin', '.bin-zsk.bin', '.elf-zsk.bin', '.map')}
    default_metadata = namespace['_metadata_policy']
    namespace['_metadata_policy'] = lambda: immediate_metadata(default_metadata())
    return namespace



def immediate_metadata(policy):
    original = policy['_expected_metadata']
    def expected(build_path, data_dir):
        values = original(build_path, data_dir)
        values.update({'build.fqbn': FQBN, 'build.boot_mode': 'immediate'})
        return values
    reference = policy['_read_reference']()
    for index in (1, 2):
        key = 'recipe.hooks.objcopy.postobjcopy.' + str(index) + '.pattern'
        if reference[key].count(' -prelinked  ') != 1:
            raise ValueError('Reviewed package recipe changed')
        reference[key] = reference[key].replace(' -prelinked  ', ' -prelinked -immediate ')
    policy['_expected_metadata'] = expected
    policy['_read_reference'] = lambda: dict(reference)
    return policy


def immediate_artifacts(artifacts, native_tls_source, frozen_validator_source, saved):
    extension = {'__name__': '_match_static_native_tls'}
    exec(compile(saved[_RAW + 'static_native_artifacts.py'], '<checked-native-tls>', 'exec'), extension)
    frozen = extension['load_frozen']
    def load(native, source):
        base = frozen(native, source)
        original = base['package_header']
        def header(length):
            value = original(length)
            if len(value) != 16 or value[14] != 2:
                raise ValueError('Reviewed prelinked header changed')
            return value[:14] + bytes([6]) + value[15:]
        base['package_header'] = header
        return base
    extension['load_frozen'] = load
    return extension['validate_artifacts'](artifacts, native_tls_source, frozen_validator_source)


def validate_preflight(text, *, build_path, data_dir, profile, motors_allowed, snapshots):
    """Check the selected commissioning properties; this grants no build or run permission."""
    policy = _policy(profile, motors_allowed, snapshots)
    return policy['validate_preflight'](text, build_path=build_path, data_dir=data_dir)


def validate_compile_result(text, *, build_path, data_dir, profile, motors_allowed, snapshots):
    """Check completed compiler metadata; hardware acceptance stays separate."""
    policy = _policy(profile, motors_allowed, snapshots)
    return policy['validate_compile_result'](text, build_path=build_path, data_dir=data_dir)


def validate_artifacts(artifacts, native_tls_source, frozen_validator_source, *,
                       exported_flat_package, profile, motors_allowed, snapshots):
    """Preserve complete ELF/TLS/package checks for exactly seven app files."""
    flags = safety_flags(profile, motors_allowed=motors_allowed)
    saved = _snapshots(snapshots)
    if (type(exported_flat_package) is not bytes or type(artifacts) is not dict or
            exported_flat_package != artifacts.get(PROJECT + '.bin-zsk.bin')):
        raise ValueError('Exported flat package must equal the build package bytes')
    report = immediate_artifacts(artifacts, native_tls_source, frozen_validator_source, saved)
    aliases = {PROJECT + suffix: PROJECT + suffix for suffix in (
        '.elf', '_debug.elf', '_temp.elf', '.bin', '.bin-zsk.bin', '.elf-zsk.bin', '.map')}
    return dict(status='STATIC_MATCH_APP_LAYOUT_PACKAGE_PASS', profile=profile,
        motors_allowed=motors_allowed, project=PROJECT, fqbn=FQBN, flags=flags,
        artifact_aliases=aliases, artifact_sha256={name: hashlib.sha256(data).hexdigest()
        for name, data in artifacts.items()}, validator_report=report)
