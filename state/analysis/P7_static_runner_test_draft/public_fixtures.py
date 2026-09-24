# Builds independent fixed-protocol observations from public contracts and fixtures.
# Keeps runner command fakes separate from the implementation and actual transport.
# Loaded only after independent test freezes; never queries or compiles anything.
import base64
import hashlib
import json
from pathlib import Path
import re
import sys
import types
import zlib

ROOT = Path(__file__).resolve().parents[3]
RAW = ROOT / 'state/analysis/P7_static_link_probe_raw'
SOURCE = 'fcddbd8ef5ba4c92a2080b03e9343ac78c2406b13d9514793aa147e02f0d1da2'
RUN = '0123456789abcdef0123456789abcdef'
BOOT_ID = '11111111-2222-4333-8444-555555555555'
R = '/home/arduino/sumox26_codex_build'
S = R + '/' + SOURCE + '/app'
D = '/home/arduino/.arduino15'
USER = '/home/arduino/Arduino'
BOARD = '2629958581'
ADB = 'C:/Users/narut/AppData/Local/Arduino15/packages/arduino/tools/adb/32.0.0/adb.exe'
MANIFEST = ROOT / 'state/analysis/P7_default_qualification_raw/checked_stage_manifest.json'
MANIFEST_SHA = '56ab12b990ebe664941677e29dfef783197bc98c3a9de1985b54d57bb30da56a'
VALIDATOR_SHA = 'd30372dd4b8fb8c2661d00affc4a215cc88e3f62511995ff6303827bed4b7368'
TIMEOUTS = dict(inventory=30, source=60, claim=30, absent=30, artifacts=60,
                layout=120, read=60, postcheck=90)


def load(path, name):
    module = types.ModuleType(name)
    module.__file__ = str(path)
    sys.modules[name] = module
    exec(compile(path.read_bytes(), str(path), 'exec'), module.__dict__)
    return module


def digest(data):
    return hashlib.sha256(data).hexdigest()


def packed(data):
    return base64.b64encode(zlib.compress(data, 9)).decode('ascii')


def canonical(value):
    return base64.b64encode(json.dumps(value, sort_keys=True, separators=(',', ':'),
                                      ensure_ascii=True, allow_nan=False).encode()).decode()


def paths(run=RUN):
    root = R + '/_app_builds/static-app-probe-v1/' + SOURCE + '/bench-default/' + run
    return root, root + '/build', root + '/artifacts'


def claim(run=RUN):
    return {'run_id': run, 'boot_id': BOOT_ID,
            'directories': {key: {'device': 7, 'inode': inode}
                            for key, inode in (('run', 100), ('build', 101), ('artifacts', 102))}}


def identity():
    return dict(user='arduino', uid=1000, gid=1000, home='/home/arduino', sysname='Linux',
                release='synthetic-kernel', machine='aarch64', boot_id=BOOT_ID, python=[3, 12, 3])


def resources():
    return dict(available_ram_bytes=536870912, root_available_bytes=1073741824,
                tmp_available_bytes=1073741824)


def source_packet():
    raw = MANIFEST.read_bytes()
    if digest(raw) != MANIFEST_SHA:
        raise RuntimeError('Fixed source manifest changed')
    manifest = json.loads(raw)
    source = {}
    for name, expected in manifest['files'].items():
        value = (ROOT / 'build/stage/app' / name).read_bytes()
        if digest(value) != expected:
            raise RuntimeError('Established stage differs: ' + name)
        source[name] = value
    combined = hashlib.sha256()
    for name in sorted(source):
        combined.update(name.encode() + b'\0' + source[name])
    if len(source) != 102 or combined.hexdigest() != SOURCE:
        raise RuntimeError('Fixed source set/digest changed')
    observation = dict(path=S, source_sha256=SOURCE, file_count=102,
                       total_bytes=sum(map(len, source.values())),
                       files={name: {'bytes': len(data), 'sha256': digest(data)}
                              for name, data in source.items()})
    return raw, source, observation


def artifact_packet():
    fixture = load(ROOT / 'state/analysis/P7_static_artifact_test_draft/synthetic_elf.py',
                   'runner_public_elf_fixture')
    packet = fixture.packet()
    rows = [('.text', 1, 6, fixture.FLASH, 8, 4, fixture.FLASH),
            ('.rodata', 1, 2, fixture.FLASH + 16, 8, 4, fixture.FLASH + 16),
            ('.data', 1, 3, fixture.RAM, 8, 4, fixture.FLASH + 32),
            ('.bss', 8, 3, fixture.RAM + 8, fixture.BSS_END - fixture.RAM - 8, 8, None)]
    fields = ('name', 'type', 'flags', 'address', 'size', 'alignment', 'load_address')
    report = dict(status='STATIC_LAYOUT_PACKAGE_PASS', entry=fixture.FLASH | 1,
                  flash=dict(start=fixture.FLASH, end=fixture.FLASH + 40,
                             remaining=0x081c0000 - fixture.FLASH - 40),
                  ram=dict(start=fixture.RAM, end=fixture.BSS_END, remaining=0x20053890-fixture.BSS_END),
                  data_copy=dict(source=fixture.FLASH+32, destination=fixture.RAM, bytes=8),
                  bss_zero=dict(start=fixture.RAM+8, end=fixture.RAM+24, bytes=16),
                  sections=[dict(zip(fields, row)) for row in rows],
                  weak_undefined=['optional_weak_hook'],
                  artifacts={name: dict(bytes=len(data), sha256=digest(data)) for name, data in packet.items()})
    return packet, report


def file_records(packet):
    output = {'build/' + name: value for name, value in packet.items()}
    output['artifacts/app.ino.bin-zsk.bin'] = packet['app.ino.bin-zsk.bin']
    return {name: dict(state='regular', sha256=digest(data),
                       identity=dict(device=7, inode=1000+i, bytes=len(data), mtime_ns=123, ctime_ns=124))
            for i, (name, data) in enumerate(output.items())}


def envelope(action, data, run=RUN):
    return dict(schema='static-remote-v1', action=action, run_id=run, ok=True, data=data, error=None)


def compiler_result(run=RUN):
    _, build, _ = paths(run)
    reference = json.loads((RAW / 'static_reference.json').read_text())
    values = {'BUILD_PATH': build, 'DATA_DIR': D}
    properties = {key: re.sub(r'@(BUILD_PATH|DATA_DIR)@', lambda m: values[m[1]], value)
                  for key, value in reference.items()}
    platform = D + '/packages/arduino/hardware/zephyr/1.0.0'
    properties.update({'build.fqbn': 'arduino:zephyr:unoq:link_mode=static', 'build.core': 'arduino',
                       'build.variant': 'arduino_uno_q_stm32u585xx', 'build.project_name': 'app.ino',
                       'build.boot_mode': 'wait', 'upload.extension': 'bin-zsk.bin', 'build.path': build,
                       'build.extra_flags': '', 'build.extra_ldflags': '',
                       'build.library_discovery_phase_flag': '-DARDUINO_LIBRARY_DISCOVERY_PHASE=0',
                       'runtime.platform.path': platform,
                       'build.variant.path': platform + '/variants/arduino_uno_q_stm32u585xx',
                       'runtime.tools.arm-zephyr-eabi-1.0.1.path': D + '/packages/zephyr/tools/arm-zephyr-eabi/1.0.1'})
    core = dict(id='arduino:zephyr', version='1.0.0', install_dir=platform)
    return dict(success=True, error='', upload_result={}, compiler_out='', compiler_err='',
                builder_result=dict(build_path=build, board_platform=core, build_platform=dict(core),
                                    used_libraries=[], build_properties=[key+'='+value for key,value in properties.items()]))


def compiler_argv(run=RUN, query=False):
    _, build, artifacts = paths(run)
    argv = ['arduino-cli', 'compile', '--jobs', '1', '--json', '--fqbn',
            'arduino:zephyr:unoq:link_mode=static', '--build-path', build, '--output-dir', artifacts,
            '--build-property', 'compiler.cpp.extra_flags=-DMATCH=0 -DMOTORS_ALLOWED=0',
            '--build-property', 'compiler.c.extra_flags=-DMATCH=0 -DMOTORS_ALLOWED=0',
            '--build-property', 'build.library_discovery_phase_flag=-DARDUINO_LIBRARY_DISCOVERY_PHASE=0']
    return argv + (['--show-properties=expanded'] if query else []) + [S]


def override_argv():
    platform = D + '/packages/arduino/hardware/zephyr/1.0.0'
    paths_ = [D+'/packages/platform.txt', USER+'/hardware/platform.txt', platform+'/platform.local.txt',
              platform+'/boards.local.txt', S+'/sketch.yaml', S+'/sketch.yml']
    program = ('for path do if test -e "$path" || test -L "$path"; then '
               "printf 'Unreviewed app override: %s\\n' \"$path\" >&2; exit 1; fi; done")
    return ['sh', '-c', program, 'sumo-app-override-check', *paths_]


def installed_pins():
    base = json.loads((ROOT / 'tools/app_build_pins.json').read_text())
    roots = dict(platform=D+'/packages/arduino/hardware/zephyr/1.0.0',
                 compiler=D+'/packages/zephyr/tools/arm-zephyr-eabi/1.0.1')
    pins = {roots[group]+'/'+name: value for group, rows in base.items() for name,value in rows.items()}
    extra = json.loads((RAW / 'additional_pins.json').read_text())
    for template, value in extra.items():
        path = template.replace('@DATA_DIR@', D)
        if path in pins:
            raise RuntimeError('Duplicate installed pin')
        pins[path] = value
    if len(pins) != 26:
        raise RuntimeError('Wrong installed pin set')
    return pins
