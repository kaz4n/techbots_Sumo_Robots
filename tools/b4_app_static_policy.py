# Checks the ordinary application B4 stand profile using reviewed byte snapshots.
# Keeps commissioning metadata separate from permission to upload or run motors.
# Tested by independent snapshot, metadata and artifact contract cases.
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


def safety_flags(motors_allowed):
    if type(motors_allowed) is not int or motors_allowed not in (0, 1):
        raise ValueError('Explicit integer motors_allowed 0 or 1 required')
    return ('-DMATCH=0 -DMOTORS_ALLOWED=' + str(motors_allowed) +
            ' -DSUMOX_B4_STAND=1 -DSUMOX_P3_DRIVE_TEST=0'
            ' -DSUMOX_P3_TURN_TRIAL=0 -DSUMOX_P3_STOP_TRIAL=0'
            ' -DSUMOX_P4_REACTIVE=0 -DSUMOX_TIMING_EVIDENCE=0'
            ' -DSUMOX_P5_ABORT_TIMING=0 -DSUMOX_MOTOR_FAULT_PROBE=0')


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


def _policy(motors_allowed, snapshots):
    flags = safety_flags(motors_allowed)
    saved = _snapshots(snapshots)
    namespace = {'__name__': '_sumox_b4_static_policy',
                 '__file__': str(_ROOT / _ADAPTER)}
    exec(compile(saved[_ADAPTER], namespace['__file__'], 'exec'), namespace)
    # Every dependency read is satisfied from this call's checked immutable bytes.
    namespace['_checked_source'] = lambda name: saved[name]
    namespace.update(PROJECT=PROJECT, FQBN=FQBN, FLAGS=flags)
    namespace['_ALIASES'] = {PROJECT + suffix: PROJECT + suffix for suffix in (
        '.elf', '_debug.elf', '_temp.elf', '.bin', '.bin-zsk.bin', '.elf-zsk.bin', '.map')}
    return namespace


def validate_preflight(text, *, build_path, data_dir, motors_allowed, snapshots):
    """Check the fixed B4 properties; this grants no build or run permission."""
    policy = _policy(motors_allowed, snapshots)
    return policy['validate_preflight'](text, build_path=build_path, data_dir=data_dir)


def validate_compile_result(text, *, build_path, data_dir, motors_allowed, snapshots):
    """Check completed compiler metadata; hardware acceptance stays separate."""
    policy = _policy(motors_allowed, snapshots)
    return policy['validate_compile_result'](text, build_path=build_path, data_dir=data_dir)


def validate_artifacts(artifacts, native_tls_source, frozen_validator_source, *,
                       exported_flat_package, motors_allowed, snapshots):
    """Preserve complete ELF/TLS/package checks for exactly seven app files."""
    policy = _policy(motors_allowed, snapshots)
    result = policy['validate_artifacts'](
        artifacts, native_tls_source, frozen_validator_source,
        exported_flat_package=exported_flat_package)
    result['status'] = 'STATIC_B4_APP_LAYOUT_PACKAGE_PASS'
    result['motors_allowed'] = motors_allowed
    return result

