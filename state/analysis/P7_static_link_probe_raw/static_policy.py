# Validates the single reviewed static/M0 profile without invoking a build.
# Keeps this experiment separate from unchanged production dynamic admission.
# Tested by the independently frozen D141 synthetic policy and I/O cases.
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[3]
REFERENCE = Path(__file__).with_name('static_reference.json')
REFERENCE_SHA256 = '1dc8ac6dec8534536acfcc4da73516416ea465cfcc1a349900fd13e210144a2b'
FQBN = 'arduino:zephyr:unoq:link_mode=static'
FLAGS = '-DMATCH=0 -DMOTORS_ALLOWED=0'
_spec = importlib.util.spec_from_file_location(
    'sumox_static_common_policy', ROOT / 'tools/app_build_policy.py')
_common = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_common)


def _finite_float(token):
    value = float(token)
    if not math.isfinite(value):
        raise ValueError('Nonfinite JSON number: ' + token)
    return value


def _check_json(text):
    if not isinstance(text, str):
        raise ValueError('Static policy expects JSON text')
    # parse_constant alone misses finite-looking exponent tokens such as 1e999.
    try:
        json.loads(text, object_pairs_hook=_common.unique_object,
                   parse_constant=_common.invalid_constant,
                   parse_float=_finite_float)
    except (TypeError, OverflowError, RecursionError) as error:
        raise ValueError('Malformed static compiler JSON') from error


def _read_reference():
    try:
        raw = REFERENCE.read_bytes()
    except OSError as error:
        raise ValueError('Missing reviewed static command reference') from error
    if hashlib.sha256(raw).hexdigest() != REFERENCE_SHA256:
        raise ValueError('Reviewed static command reference bytes changed')
    return _common.decode(raw.decode('utf-8'))


def _expected_metadata(build_path, data_dir):
    platform = data_dir + _common.PLATFORM_SUFFIX
    return {
        'build.fqbn': FQBN,
        'build.core': 'arduino',
        'build.variant': _common.VARIANT,
        'runtime.platform.path': platform,
        'build.variant.path': platform + '/variants/' + _common.VARIANT,
        'build.project_name': 'app.ino',
        'build.library_discovery_phase_flag': _common.DISCOVERY,
        'build.boot_mode': 'wait',
        'build.link_mode': 'static',
        'build.path': build_path,
        'runtime.tools.arm-zephyr-eabi-1.0.1.path': data_dir + _common.COMPILER_SUFFIX,
        'compiler.path': data_dir + _common.COMPILER_SUFFIX + '/bin/',
        'compiler.c.extra_flags': FLAGS,
        'compiler.cpp.extra_flags': FLAGS,
        'build.extra_flags': '',
        'build.extra_ldflags': '',
        'upload.extension': 'bin-zsk.bin',
    }


def _validate_commands(properties, build_path, data_dir):
    reference = _read_reference()
    controlled = {key: value for key, value in properties.items()
                  if key.startswith(_common.COMMAND_PREFIXES)}
    if controlled.keys() != reference.keys():
        raise ValueError('Missing or unreviewed static command property')
    substitutions = {'BUILD_PATH': build_path, 'DATA_DIR': data_dir}
    for key, template in reference.items():
        # Tokens occurring inside a supplied path remain literal path bytes.
        expected = re.sub(r'@(BUILD_PATH|DATA_DIR)@',
                          lambda match: substitutions[match[1]], template)
        if controlled[key] != expected:
            raise ValueError('Unreviewed static command property: ' + key)


def _validate(text, build_path, data_dir, compiled):
    build_path = _common.absolute_path(build_path)
    data_dir = _common.absolute_path(data_dir)
    _check_json(text)
    builder, platform = _common.validated_builder(text, build_path)
    if platform != data_dir + _common.PLATFORM_SUFFIX:
        raise ValueError('Static core differs from the resolved data directory')
    if compiled:
        libraries = builder.get('used_libraries', [])
        if not isinstance(libraries, list) or libraries:
            raise ValueError('Static probe rejects every external library')
    properties = _common.properties_from(builder)
    for key, expected in _expected_metadata(build_path, data_dir).items():
        if properties.get(key) != expected:
            raise ValueError('Static property differs from the fixed profile: ' + key)
    _validate_commands(properties, build_path, data_dir)
    return properties


def validate_preflight(text, *, build_path, data_dir):
    """Validate one properties-only result; this does not establish a build."""
    return _validate(text, build_path, data_dir, False)


def validate_compile_result(text, *, build_path, data_dir):
    """Validate compiler metadata; artifact feasibility remains a separate check."""
    return _validate(text, build_path, data_dir, True)
