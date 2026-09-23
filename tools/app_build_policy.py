# Validates the pinned app-only native dependency build policy.
# Rejects library and toolchain drift before reporting a completed app build.
# Tested with independent malformed-result and controlled transport cases.
import hashlib
import json
from pathlib import Path, PurePosixPath
import re

POLICY = 'native-app-v1'
DISCOVERY = '-DARDUINO_LIBRARY_DISCOVERY_PHASE=0'
BASE_FQBN = 'arduino:zephyr:unoq'
VARIANT = 'arduino_uno_q_stm32u585xx'
COMPILER_ROOT = 'runtime.tools.arm-zephyr-eabi-1.0.1.path'


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('Duplicate JSON key: ' + key)
        result[key] = value
    return result


def invalid_constant(value):
    raise ValueError('Nonfinite JSON constant: ' + value)


def decode(text):
    return json.loads(text, object_pairs_hook=unique_object,
                      parse_constant=invalid_constant)


def validate_cli(text):
    pattern = r'arduino-cli\s+Version: 1\.5\.1 Commit: 01f3d4f2b Date: \S+'
    if not isinstance(text, str) or not re.fullmatch(pattern, text.strip()):
        raise ValueError('App policy requires Arduino CLI 1.5.1 commit 01f3d4f2b')


def absolute_path(value):
    if (not isinstance(value, str) or not value.startswith('/') or
            any(char in value for char in '\r\n\\') or
            '..' in PurePosixPath(value).parts or
            PurePosixPath(value).as_posix() != value or value == '/'):
        raise ValueError('App build result has an invalid absolute path')
    return value


def properties_from(builder):
    values = builder.get('build_properties')
    if not isinstance(values, list) or not values:
        raise ValueError('Missing app build properties')
    result = {}
    for item in values:
        if not isinstance(item, str) or '=' not in item:
            raise ValueError('Malformed app build property')
        key, value = item.split('=', 1)
        if not key or key in result:
            raise ValueError('Empty or duplicate app build property: ' + key)
        result[key] = value
    return result


def expected_properties(fqbn, flags, platform):
    if fqbn not in (BASE_FQBN, BASE_FQBN + ':wait_linux_boot=no'):
        raise ValueError('Unsupported app FQBN')
    if flags not in ('-DMATCH=0 -DMOTORS_ALLOWED=0', '-DMATCH=1 -DMOTORS_ALLOWED=1'):
        raise ValueError('Unsupported app safety flags')
    immediate = fqbn.endswith(':wait_linux_boot=no')
    if 'MATCH=1' in flags and not immediate:
        raise ValueError('MATCH requires Immediate startup')
    expected = {
        'build.fqbn': fqbn, 'build.core': 'arduino', 'build.variant': VARIANT,
        'runtime.platform.path': platform, 'build.variant.path': platform + '/variants/' + VARIANT,
        'build.project_name': 'app.ino', 'build.library_discovery_phase_flag': DISCOVERY,
        'compiler.c.extra_flags': flags, 'compiler.cpp.extra_flags': flags,
        'build.link_mode': 'dynamic', 'build.link_args.dynamic': '-e main',
        'build.boot_mode': 'immediate' if immediate else 'wait',
    }
    for key in ('compiler.c.elf.extra_flags', 'compiler.S.extra_flags',
                'build.extra_flags', 'build.extra_ldflags', 'compiler.ldflags',
                'compiler.libraries.ldflags'):
        expected[key] = ''
    return expected


def validate_result(text, fqbn, flags, build_path):
    result = decode(text)
    if not isinstance(result, dict) or result.get('success') is not True:
        raise ValueError('App compiler result is not a successful JSON object')
    if result.get('error', '') != '' or result.get('upload_result', {}) != {}:
        raise ValueError('Unexpected error/upload result in app compile')
    for key in ('compiler_out', 'compiler_err'):
        if key in result and not isinstance(result[key], str):
            raise ValueError('Malformed compiler output: ' + key)
    builder = result.get('builder_result')
    if not isinstance(builder, dict) or builder.get('build_path') != absolute_path(build_path):
        raise ValueError('Missing builder result or wrong app build path')
    platform = None
    for key in ('board_platform', 'build_platform'):
        item = builder.get(key)
        if not isinstance(item, dict) or item.get('id') != 'arduino:zephyr' or item.get('version') != '1.0.0':
            raise ValueError('Wrong app platform identity: ' + key)
        current = absolute_path(item.get('install_dir'))
        if platform is not None and current != platform:
            raise ValueError('Board and build platform paths differ')
        platform = current
    libraries = builder.get('used_libraries', [])
    if not isinstance(libraries, list) or libraries:
        raise ValueError('App native dependency policy rejects every external library')
    properties = properties_from(builder)
    for key, expected in expected_properties(fqbn, flags, platform).items():
        if properties.get(key) != expected:
            raise ValueError('App build property differs from pinned policy: ' + key)
    compiler = absolute_path(properties.get(COMPILER_ROOT))
    if properties.get('compiler.path') != compiler + '/bin/':
        raise ValueError('Unexpected compiler path')
    return properties


def verify_files(remote, board, properties, build_path, artifact_folder):
    pins = decode(Path(__file__).with_name('app_build_pins.json').read_text())
    roots = dict(platform=properties['runtime.platform.path'], compiler=properties[COMPILER_ROOT])
    expected = {roots[group] + '/' + name: value
                for group, files in pins.items() for name, value in files.items()}
    artifacts = [build_path + '/app.ino' + suffix
                 for suffix in ('.elf', '_debug.elf', '_temp.elf')]
    artifacts.append(artifact_folder + '/app.ino.elf-zsk.bin')
    paths = [*expected, *artifacts]
    result = remote(board, ['sha256sum', '--', *paths], capture=True)
    lines = result.stdout.splitlines()
    if len(lines) != len(paths):
        raise ValueError('Incomplete app dependency/artifact hashes')
    hashes = {}
    for name, line in zip(paths, lines):
        match = re.fullmatch(r'([0-9a-f]{64})  (.+)', line)
        if not match or match[2] != name:
            raise ValueError('Malformed app file hash or path')
        digest = match[1]
        if name in expected and digest != expected[name]:
            raise ValueError('Pinned app dependency bytes changed: ' + name)
        if name in artifacts and digest == hashlib.sha256(b'').hexdigest():
            raise ValueError('Empty app build artifact: ' + name)
        hashes[name] = digest
    return hashes
