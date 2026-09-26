# Uploads only the fixed inhibited B4 image through the accepted native lifecycle.
# Keeps existing installed-file and descriptor guards without capture or MCU reads.
# Focused independent fixtures verify the new fixed profile and attempt boundaries.
import hashlib
import json
from pathlib import Path
import re
import sys
from types import ModuleType, SimpleNamespace

SOURCE = '9044ebbb3cd3b2dbb7aa5984dd5ff23bfff697372f1f29d56693af9ea5eaf31a'
RUN_ID = 'b4-app-m0-9044ebbb-load01'
PARENT = '/home/arduino/sumox26_codex_build'
SKETCH = PARENT + '/' + SOURCE + '/app'
BUILD = PARENT + '/b4-app-m0-static01/build'
DATA = '/home/arduino/.arduino15'
CORE = DATA + '/packages/arduino/hardware/zephyr/1.0.0'
DEPENDENCY_SHA256 = {
    'upload': 'e926b7ba5586475664b0541370e7cfb5c50e40d8dc8b47b18e35db3e0a0a25c1',
    'capture': '95b0344d01886b6db30d55aa18a536f9a481b82348e22643e7920d817dbfac3e',
    'helper': '8ba9b190c38e728013a383348c60c287b0366607f65f703161cf7f2e142d36f8'}
ARTIFACTS = {
    'raw': (82896, '6fcad2f09c90bbc7dd72760e7a794305811d042a9d2e578e03d5154cc368a471'),
    'sketch': (82912, '84667b0a22ff7701059a266b6c82bb61de1f7ccec96280e4f13b5692bf785a28'),
    'loader': (2303728, '39d4a4fd47241663323f6e04f94dd8f5a9f9ad6582cf1df37f9709b74026adcd'),
    'loader_image': (263680, 'e9322826c422fb234ac8c2e79ea38a050d0dd8dc32b2a89f6930e0a0ff7ebab2')}


def load_dependencies(sources):
    if type(sources) is not dict or set(sources) != set(DEPENDENCY_SHA256):
        raise ValueError('Wrong dependency selections')
    for name, expected in DEPENDENCY_SHA256.items():
        raw = sources[name]
        if type(raw) is not bytes or hashlib.sha256(raw).hexdigest() != expected:
            raise ValueError('Pinned dependency differs: ' + name)
    modules = {}
    for name in DEPENDENCY_SHA256:
        module = ModuleType('_b4_app_private_' + name)
        module.__file__ = '<pinned-b4-app-' + name + '>'
        exec(compile(sources[name], module.__file__, 'exec'), module.__dict__)
        modules[name] = module
    modules['upload'].selected_profile = selected_profile
    return SimpleNamespace(**modules)


def selected_profile(support, run_id=RUN_ID):
    support.require(type(run_id) is str and run_id == RUN_ID, 'Wrong run identity')
    files = {
        'cli': '/usr/bin/arduino-cli',
        'remoteocd': DATA + '/packages/arduino/tools/remoteocd/0.1.1/remoteocd',
        'adb': DATA + '/packages/arduino/tools/adb/32.0.0/adb',
        'flash_config': CORE + '/variants/arduino_uno_q_stm32u585xx/flash_sketch.cfg',
        'openocd': '/opt/openocd/bin/openocd',
        'gpio_config': '/opt/openocd/openocd_gpiod.cfg',
        'target_config': '/opt/openocd/stm32u5x.cfg',
        'common_config': '/opt/openocd/stm32x5x_common.cfg',
        'swj': '/opt/openocd/share/openocd/scripts/target/swj-dp.tcl',
        'loader': CORE + '/firmwares/zephyr-arduino_uno_q_stm32u585xx.elf',
        'mem_helper': '/opt/openocd/share/openocd/scripts/mem_helper.tcl',
        'boards': CORE + '/boards.txt', 'platform': CORE + '/platform.txt',
        'installed': CORE + '/installed.json', 'index': DATA + '/package_index.json',
        'raw': BUILD + '/app.ino.bin',
        'sketch': BUILD + '/app.ino.bin-zsk.bin'}
    absent = (CORE + '/boards.local.txt', CORE + '/platform.local.txt',
              DATA + '/packages/platform.txt', '/home/arduino/Arduino/hardware',
              '/home/arduino/openocd_gpiod.cfg', '/home/arduino/stm32u5x.cfg',
              '/home/arduino/stm32x5x_common.cfg', '/home/arduino/mem_helper.tcl',
              '/home/arduino/target/swj-dp.tcl', '/opt/openocd/mem_helper.tcl',
              '/opt/openocd/target/swj-dp.tcl', SKETCH + '/sketch.yaml',
              SKETCH + '/sketch.yml', SKETCH + '/sketch.json')
    return {
        'fixed': {'schema': 'fixed-b4-app-upload-v1', 'run_id': RUN_ID,
                  'source_sha256': SOURCE, 'output': PARENT + '/' + RUN_ID + '-upload'},
        'schema_prefix': 'b4-app-upload-', 'files': files, 'absent': absent,
        'argv': ['/usr/bin/arduino-cli', '--config-file', '/dev/null', 'upload',
                 '--fqbn', 'arduino:zephyr:unoq:link_mode=static',
                 '--input-file', files['raw'], SKETCH]}


def _artifact(support, name, pin):
    size, sha = ARTIFACTS[name]
    support.require(type(pin['bytes']) is int and pin['bytes'] == size and
                    type(pin['sha256']) is str and pin['sha256'] == sha,
                    'Wrong exact artifact: ' + name)


def checked_upload_bindings(dependencies, bindings):
    support = dependencies.capture
    result = dependencies.upload.checked_bindings(support, bindings, RUN_ID)
    for name in ('raw', 'sketch', 'loader'):
        _artifact(support, name, result['files'][name])
    return result


def upload(dependencies, *, fs_root=Path('/'), executor=None, clock=None, bindings=None):
    checked = checked_upload_bindings(dependencies, bindings)
    return dependencies.upload.upload_loader(
        dependencies.helper, dependencies.capture, fs_root=fs_root, executor=executor,
        clock=clock, bindings=checked, run_id=RUN_ID)
