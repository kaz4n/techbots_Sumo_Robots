# Samples the current recorder's small status windows without touching its UART.
# Reuses the reviewed passive Capture lifecycle and brackets RAM with full flash checks.
# Focused fixtures reject altered plans, invalid values and premature SRAM access.
import hashlib
import json
from pathlib import Path
import sys
from types import ModuleType, SimpleNamespace

SOURCE = '702ad99ee4f888c58de1715cb91512cb0a174a646d914db6ce9155489ffa63e8'
ATTEMPT = '377911abefabd094971ee6d089326604'
SESSION = 3997245574426120340
RUN_ID = 'recorder-377911abefabd094-failure-capture01'
ABI_SCHEMA = 'recorder-failure-abi-v1'
DEPENDENCIES = {
    'capture': (37525, '95b0344d01886b6db30d55aa18a536f9a481b82348e22643e7920d817dbfac3e'),
    'helper': (33321, '8ba9b190c38e728013a383348c60c287b0366607f65f703161cf7f2e142d36f8'),
    'p0': (18880, '885c4e4206aea4ac9e03c4e92e48258db2a0ae302ff83a86430e6913afeeb57c'),
}
FLASH_KEYS = ('before_loader', 'before_sketch', 'after_sketch', 'after_loader')
BASE_FILES = {
    'config': (694, '89d16a28a1489c23ec743be55ade39824f9ca5213b02b20ef4785079122e4339',
        '/home/arduino/sumox26-capture-tools/app-default-beeffff315b2e28a95a20dc1e26477fc924b2da26d1fdd8a8b36fb013ca110e1/p0_mem_read.cfg'),
    'loader': (2303728, '39d4a4fd47241663323f6e04f94dd8f5a9f9ad6582cf1df37f9709b74026adcd',
        '/home/arduino/.arduino15/packages/arduino/hardware/zephyr/1.0.0/firmwares/zephyr-arduino_uno_q_stm32u585xx.elf'),
    'openocd': (14435552, '04778a80c5c619ee4eef7505db91328f1d7e789107c496f2ddcf96d081f5b0ff', '/opt/openocd/bin/openocd'),
    'sketch': (55104, '91b6042a3f13e3650fc4b23892f88e69d4c0c56edebd6514662fa2d8cd8208c6',
        '/home/arduino/sumox26_codex_build/recorder-377911abefabd094/build/recorder.ino.bin-zsk.bin'),
    'swj': (1148, 'aad132008735bbafea3d18a304632c638f0fb99bfc19530c9f577eda2b10410a',
        '/opt/openocd/share/openocd/scripts/target/swj-dp.tcl'),
}


def require(value, message):
    if not value:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()


def same(left, right):
    return canonical(left) == canonical(right)


def bindings():
    return dict(schema='fixed-recorder-failure-capture-v1', run_id=RUN_ID,
        source_sha256=SOURCE, boot_id='55c386b9-fe6d-4388-a7f4-1d91e0bb49d8', uid=1000,
        output='/home/arduino/sumox26_codex_build/' + RUN_ID,
        files={key: dict(bytes=size, sha256=digest, path=path) for key, (size, digest, path) in BASE_FILES.items()},
        loader_image=dict(bytes=263680, sha256='e9322826c422fb234ac8c2e79ea38a050d0dd8dc32b2a89f6930e0a0ff7ebab2'))


def build_spec(abi_raw, expected_sha256, abi_module):
    require(type(abi_raw) is bytes and hashlib.sha256(abi_raw).hexdigest() == expected_sha256,
            'Accepted ABI identity differs')
    abi = json.loads(abi_raw)
    require(abi.get('schema') == ABI_SCHEMA and abi.get('status') == 'STATIC_ABI_OBSERVED' and
            abi.get('attempt') == ATTEMPT and type(abi.get('session')) is int and abi['session'] == SESSION and
            abi.get('source_sha256') == SOURCE and abi.get('compile_head') == abi_module.COMPILE_HEAD,
            'ABI profile differs')
    require(set(abi['windows']) == set(abi_module.WINDOWS) and set(abi['objects']) == {'runner', 'native_dump'},
            'ABI object/window inventory differs')
    require(abi['enums'] == {key: dict(zip(values, range(len(values)))) for key, values in abi_module.ENUMS.items()},
            'ABI enums differ')
    expected_fields = {p + ('.' + m if m else ''): (p, width, kind) for p, m, width, kind in abi_module.FIELDS}
    require(set(abi['fields']) == set(expected_fields), 'ABI field inventory differs')
    for key, (parent, width, kind) in expected_fields.items():
        field, window = abi['fields'][key], abi['windows'][parent]
        require(field['window'] == parent and type(field['bytes']) is int and field['bytes'] == width and
                field['kind'] == kind and type(field['offset']) is int and
                0 <= field['offset'] <= window['bytes'] - width, 'ABI field differs')
    ranges = []
    for key, (owner, member, name) in abi_module.WINDOWS.items():
        window, obj = abi['windows'][key], abi['objects'][owner]
        require(window['object'] == owner and window['member'] == member and window['type'] == name and
                all(type(window[k]) is int for k in ('address', 'offset', 'bytes', 'alignment')) and
                window['address'] == obj['address'] + window['offset'] and 0 <= window['offset'] and
                0 < window['bytes'] <= 16384 and window['offset'] + window['bytes'] <= obj['bytes'], 'ABI window differs')
        start, end = window['address'] & ~3, (window['address'] + window['bytes'] + 3) & ~3
        require(0x20000000 <= start < end <= 0x200C0000, 'ABI window outside SRAM')
        ranges.append((start, end))
    merged = []
    for start, end in sorted(ranges):
        if merged and start <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(end, merged[-1][1]))
        else:
            merged.append((start, end))
    require(1 <= len(merged) <= 10 and sum(end - start for start, end in merged) <= 16384,
            'Status read budget exceeded')
    return dict(schema='recorder-failure-spec-v1', abi_sha256=expected_sha256, abi=abi,
                ranges=[dict(address=start, bytes=end - start) for start, end in merged])


def read_plan(spec):
    prefix = [('before.loader.' + str(i), 0x08000000 + i * 65536, min(65536, 263680 - i * 65536))
              for i in range(5)] + [('before.sketch.0', 0x08100000, 55104)]
    middle = [(label + '.' + str(i), row['address'], row['bytes']) for label in ('first', 'second')
              for i, row in enumerate(spec['ranges'])]
    suffix = [('after.sketch.0', 0x08100000, 55104)] + [
        ('after.loader.' + str(i), 0x08000000 + i * 65536, min(65536, 263680 - i * 65536)) for i in range(5)]
    return tuple(prefix + middle + suffix)


def decode_snapshot(spec, samples, prefix):
    selected = {name: (address, raw) for name, address, raw in samples if name.startswith(prefix + '.')}
    if len(selected) != len(spec['ranges']):
        return None
    fields = {}
    for key, field in spec['abi']['fields'].items():
        window = spec['abi']['windows'][field['window']]
        address, width = window['address'] + field['offset'], field['bytes']
        spans = [(base, raw) for base, raw in selected.values() if base <= address and address + width <= base + len(raw)]
        require(len(spans) == 1, 'Field missing or multiply covered')
        base, raw = spans[0]
        value = int.from_bytes(raw[address - base:address - base + width], 'little')
        kind = field['kind']
        if kind == 'bool':
            require(value in (0, 1), 'Invalid bool bytes: ' + key)
            value = bool(value)
        elif kind != 'uint':
            table = spec['abi']['enums'][kind]
            require(value in table.values(), 'Invalid enum bytes: ' + key)
            value = dict(value=value, name=next(name for name, number in table.items() if number == value))
        fields[key] = value
    return dict(fields=fields, session_matches_expected=fields['session'] == SESSION)


def analysis(spec, samples, flash):
    result = dict(schema='recorder-failure-analysis-v1', flash=dict(flash),
                  abi_sha256=spec['abi_sha256'], first=None, second=None, equalities=None,
                  decode_errors=[], coherence='UNPROVEN')
    for label in ('first', 'second'):
        try:
            result[label] = decode_snapshot(spec, samples, label)
        except ValueError as error:
            result['decode_errors'].append(dict(snapshot=label, message=str(error)))
    if result['first'] is not None and result['second'] is not None:
        result['equalities'] = {key: left == result['second']['fields'][key]
                                for key, left in result['first']['fields'].items()}
    return result


def load_dependencies(sources):
    require(type(sources) is dict and set(sources) == set(DEPENDENCIES), 'Wrong dependency inventory')
    modules = {}
    for name, (size, digest) in DEPENDENCIES.items():
        raw = sources[name]
        require(type(raw) is bytes and len(raw) == size and hashlib.sha256(raw).hexdigest() == digest,
                'Pinned dependency differs: ' + name)
        module = ModuleType('_recorder_failure_private_' + name)
        module.__file__ = '<pinned-recorder-failure-' + name + '>'
        exec(compile(raw, module.__file__, 'exec'), module.__dict__)
        modules[name] = module
    return SimpleNamespace(**modules)


def capture_type(dependencies, fixed_spec, fixed_spec_sha256):
    require(hashlib.sha256(canonical(fixed_spec)).hexdigest() == fixed_spec_sha256, 'Capture spec differs')
    frozen = json.loads(canonical(fixed_spec))
    plan, count = read_plan(frozen), len(frozen['ranges'])
    counts = dict(commands=len(plan), reads=len(plan), requested_bytes=sum(row[2] for row in plan))

    class RecorderFailureCapture(dependencies.capture.Capture):
        source = SOURCE
        result_schema = 'recorder-failure-capture-result-v1'
        attempt_schema = 'recorder-failure-capture-attempt-v1'

        def profile_bindings(self):
            require(same(self.input_bindings, bindings()), 'Wrong fixed recorder binding')
            require(sys.flags.dont_write_bytecode, 'Python -B is required')
            return bindings()

        def prepare_plan(self):
            self.plan = plan
            for name, address, size in plan[6:6 + count * 2]:
                dependencies.p0.ram_range(address, size)
            self.report['analysis'] = analysis(frozen, [], dict.fromkeys(FLASH_KEYS, False))

        def gather(self):
            flash = dict.fromkeys(FLASH_KEYS, False)
            brackets = {4: ('before_loader', 0, 5, self.loader), 5: ('before_sketch', 5, 6, self.sketch),
                        6 + count * 2: ('after_sketch', 6 + count * 2, 7 + count * 2, self.sketch),
                        len(plan) - 1: ('after_loader', len(plan) - 5, len(plan), self.loader)}
            for index, item in enumerate(self.plan):
                require(self.report['first_error'] is None, 'Earlier capture read failed')
                if index == 6 + count:
                    self.pause()
                try:
                    self.one_read(index, item)
                    if index in brackets:
                        label, begin, end, reference = brackets[index]
                        flash[label] = b''.join(row[2] for row in self.samples[begin:end]) == reference
                        require(flash[label], 'Captured flash image differs: ' + label)
                finally:
                    self.report['analysis'] = analysis(frozen, self.samples, flash)
                self.budget()
            require(not self.report['analysis']['decode_errors'], 'Invalid scalar bytes; raw observations retained')

        def complete(self):
            value = self.report['analysis']
            return (same(self.report['counts'], counts) and len(self.report['reads']) == len(plan) and
                    all(value['flash'].values()) and value['first'] is not None and value['second'] is not None and
                    not value['decode_errors'])

    return RecorderFailureCapture


def collect(dependencies, *, spec, spec_sha256, input_bindings, fs_root=Path('/'),
            executor=None, clock=None, sleeper=None):
    capture = capture_type(dependencies, spec, spec_sha256)(
        dependencies.helper, None, dependencies.p0.loader_image, fs_root, executor,
        clock, sleeper, input_bindings, RUN_ID)
    return dependencies.capture._collect(capture)
