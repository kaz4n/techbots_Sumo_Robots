# Checks the ordinary application commissioning profiles using reviewed byte snapshots.
# Keeps commissioning metadata separate from permission to upload or run motors.
# Tested by independent D222 profile, metadata and artifact contract cases.
import hashlib
from pathlib import Path


PROJECT = 'app.ino'
FQBN = 'arduino:zephyr:unoq:link_mode=static'
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


PROFILES = ('b4_stand', 'p3_drive', 'p3_turn', 'p3_stop', 'p4_reactive',
            'p4_timing', 'p5_abort_timing')
_MACROS = ('SUMOX_B4_STAND', 'SUMOX_P3_DRIVE_TEST', 'SUMOX_P3_TURN_TRIAL',
           'SUMOX_P3_STOP_TRIAL', 'SUMOX_P4_REACTIVE', 'SUMOX_TIMING_EVIDENCE',
           'SUMOX_P5_ABORT_TIMING', 'SUMOX_MOTOR_FAULT_PROBE')
_ENABLED = dict(b4_stand=(0,), p3_drive=(1,), p3_turn=(2,), p3_stop=(3,),
                p4_reactive=(4,), p4_timing=(4, 5), p5_abort_timing=(6,))


def safety_flags(profile, *, motors_allowed):
    if type(profile) is not str or profile not in PROFILES:
        raise ValueError('Exact commissioning profile required')
    if type(motors_allowed) is not int or motors_allowed not in (0, 1):
        raise ValueError('Explicit integer motors_allowed 0 or 1 required')
    values = [('MATCH', 0), ('MOTORS_ALLOWED', motors_allowed)]
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
    return namespace


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
    policy = _policy(profile, motors_allowed, snapshots)
    result = policy['validate_artifacts'](
        artifacts, native_tls_source, frozen_validator_source,
        exported_flat_package=exported_flat_package)
    result['status'] = 'STATIC_COMMISSIONING_APP_LAYOUT_PACKAGE_PASS'
    result['profile'] = profile
    result['motors_allowed'] = motors_allowed
    return result

