# Adapts the reviewed one-shot lifecycle to the exact inhibited ordinary application.
# Collects small file-observed ABI windows while preserving complete flash brackets.
# Independent contract fixtures exercise fixed admission, execution and failures.
import hashlib
import json
from pathlib import Path
import re
import sys
from types import ModuleType, SimpleNamespace

SOURCE = '9044ebbb3cd3b2dbb7aa5984dd5ff23bfff697372f1f29d56693af9ea5eaf31a'
RUN_ID = 'ordinary-app-9044ebbb-run01'
PARENT = '/home/arduino/sumox26_codex_build'
SKETCH = PARENT + '/' + SOURCE + '/app'
BUILD = PARENT + '/ordinary-app-static01/build'
DATA = '/home/arduino/.arduino15'
CORE = DATA + '/packages/arduino/hardware/zephyr/1.0.0'
DEPENDENCY_SHA256 = {
    'upload': 'e926b7ba5586475664b0541370e7cfb5c50e40d8dc8b47b18e35db3e0a0a25c1',
    'capture': '95b0344d01886b6db30d55aa18a536f9a481b82348e22643e7920d817dbfac3e',
    'helper': '8ba9b190c38e728013a383348c60c287b0366607f65f703161cf7f2e142d36f8'}
ARTIFACTS = {
    'raw': (92928, '6f5f531b114219d712d857b4ac89ad161ceb217211207788a27443b7d4ab6db7'),
    'sketch': (92944, '7fa9d41da043931e1237712e1e88bda4151c82933af2ecec97ce3a02184d23ad'),
    'loader': (2303728, '39d4a4fd47241663323f6e04f94dd8f5a9f9ad6582cf1df37f9709b74026adcd'),
    'loader_image': (263680, 'e9322826c422fb234ac8c2e79ea38a050d0dd8dc32b2a89f6930e0a0ff7ebab2')}
WINDOWS = (('report', 537115800, 600), ('transaction', 537113264, 504), ('previous', 537113768, 48), ('gate', 536951336, 88), ('grants', 537115776, 21), ('attempted_word', 537117352, 4), ('motor_port', 537117512, 40))


def load_dependencies(sources):
    if type(sources) is not dict or set(sources) != set(DEPENDENCY_SHA256):
        raise ValueError('Wrong dependency selections')
    for name, expected in DEPENDENCY_SHA256.items():
        raw = sources[name]
        if type(raw) is not bytes or hashlib.sha256(raw).hexdigest() != expected:
            raise ValueError('Pinned dependency differs: ' + name)
    modules = {}
    for name in DEPENDENCY_SHA256:
        module = ModuleType('_ordinary_app_private_' + name)
        module.__file__ = '<pinned-ordinary-app-' + name + '>'
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
        'fixed': {'schema': 'fixed-ordinary-app-upload-v1', 'run_id': RUN_ID,
                  'source_sha256': SOURCE, 'output': PARENT + '/' + RUN_ID + '-upload'},
        'schema_prefix': 'ordinary-app-upload-', 'files': files, 'absent': absent,
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


def checked_capture_bindings(dependencies, bindings):
    support = dependencies.capture
    support.keys(bindings, ('schema', 'run_id', 'source_sha256', 'boot_id', 'uid',
                            'output', 'files', 'loader_image'))
    fixed = {'schema': 'fixed-ordinary-app-capture-v1', 'run_id': RUN_ID,
             'source_sha256': SOURCE, 'output': PARENT + '/' + RUN_ID + '-capture'}
    for name, expected in fixed.items():
        support.require(type(bindings[name]) is str and bindings[name] == expected,
                        'Wrong binding: ' + name)
    support.require(type(bindings['boot_id']) is str and re.fullmatch(
        r'[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}', bindings['boot_id']),
        'Invalid boot identity')
    support.require(type(bindings['uid']) is int and bindings['uid'] == 1000,
                    'Wrong bound UID')
    support.keys(bindings['files'], support.FILE_NAMES)
    paths = selected_profile(support)['files']
    paths['config'] = ('/home/arduino/sumox26-capture-tools/app-default-'
                       'beeffff315b2e28a95a20dc1e26477fc924b2da26d1fdd8a8b36fb013ca110e1'
                       '/p0_mem_read.cfg')
    for name, pin in bindings['files'].items():
        support.check_pin(pin)
        support.require(pin['path'] == paths[name], 'Wrong capture path: ' + name)
    for name in ('sketch', 'loader'):
        _artifact(support, name, bindings['files'][name])
    support.check_pin(bindings['loader_image'], False)
    _artifact(support, 'loader_image', bindings['loader_image'])
    support.require(sys.flags.dont_write_bytecode, 'Python -B is required')
    return json.loads(support.json_bytes(bindings))


def _flash_plan(prefix, region):
    base, extent = (0x08000000, 263680) if region == 'loader' else (0x08100000, 92944)
    return tuple((prefix + '.' + region + '.' + str(index), base + offset,
                  min(65536, extent - offset))
                 for index, offset in enumerate(range(0, extent, 65536)))


def read_plan():
    first = tuple(('first.' + name, address, size) for name, address, size in WINDOWS)
    second = tuple(('second.' + name, address, size) for name, address, size in WINDOWS)
    return (_flash_plan('before', 'loader') + _flash_plan('before', 'sketch') +
            first + second + _flash_plan('after', 'sketch') + _flash_plan('after', 'loader'))


def upload(dependencies, *, fs_root=Path('/'), executor=None, clock=None, bindings=None):
    checked = checked_upload_bindings(dependencies, bindings)
    return dependencies.upload.upload_loader(
        dependencies.helper, dependencies.capture, fs_root=fs_root, executor=executor,
        clock=clock, bindings=checked, run_id=RUN_ID)


def _capture_type(dependencies):
    support = dependencies.capture

    class OrdinaryAppCapture(support.Capture):
        source = SOURCE
        result_schema = 'ordinary-app-capture-result-v1'
        attempt_schema = 'ordinary-app-capture-attempt-v1'

        def profile_bindings(self):
            return checked_capture_bindings(dependencies, self.input_bindings)

        def prepare_plan(self):
            self.plan = read_plan()
            self.report['analysis'] = {
                'schema': 'ordinary-app-capture-analysis-v1',
                'flash': {'before_loader': False, 'before_sketch': False,
                          'after_loader': False, 'after_sketch': False},
                'snapshots': [], 'coherence': 'UNPROVEN', 'pre_sample_wait': None}

        def check_image(self, label, begin, end, reference):
            observed = b''.join(item[2] for item in self.samples[begin:end])
            matches = observed == reference
            self.report['analysis']['flash'][label] = matches
            support.require(matches, 'Captured flash image differs: ' + label)

        def pre_sample_pause(self):
            support.require(self.budget() > 30, 'Insufficient budget before first sample')
            wait = {'requested_seconds': 30, 'before': self.now(), 'after': None}
            self.report['analysis']['pre_sample_wait'] = wait
            self.sleeper(30)
            wait['after'] = self.now()
            support.require(wait['after'] - wait['before'] >= 30,
                            'Initial observation delay was shorter than thirty seconds')
            self.budget()

        def gather(self):
            brackets = {4: ('before_loader', 0, 5, self.loader),
                        6: ('before_sketch', 5, 7, self.sketch),
                        22: ('after_sketch', 21, 23, self.sketch),
                        27: ('after_loader', 23, 28, self.loader)}
            for index, item in enumerate(self.plan):
                support.require(self.report['first_error'] is None,
                                'Earlier capture read failed')
                if index == 7:
                    self.pre_sample_pause()
                if index == 14:
                    self.pause()
                try:
                    self.one_read(index, item)
                finally:
                    self.report['analysis']['snapshots'] = [dict(record)
                        for record in self.report['reads']
                        if record['name'].startswith(('first.', 'second.'))]
                if index in brackets:
                    self.check_image(*brackets[index])
                self.budget()

        def complete(self):
            analysis = self.report['analysis']
            wait = analysis['pre_sample_wait'] if analysis is not None else None
            return (wait is not None and wait['after'] is not None and
                    wait['after'] - wait['before'] >= 30 and
                    all(analysis['flash'].values()) and
                    len(analysis['snapshots']) == 14 and self.report['counts'] ==
                    {'commands': 28, 'reads': 28, 'requested_bytes': 715858})

    return OrdinaryAppCapture


def collect(dependencies, loader_image, *, fs_root=Path('/'), executor=None,
            clock=None, sleeper=None, bindings=None):
    capture = _capture_type(dependencies)(
        dependencies.helper, None, loader_image, fs_root, executor, clock, sleeper,
        bindings, RUN_ID)
    return dependencies.capture._collect(capture)
