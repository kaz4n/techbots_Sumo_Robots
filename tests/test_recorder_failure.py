# Exercises the fixed recorder ABI and passive status capture with synthetic data.
# Rejects boundary drift and malformed status bytes without contacting any board.
# Run serially with Python -B -m unittest discover -s tests -p test_recorder_failure.py.
import base64
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest

ROOT = Path(__file__).absolute().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import recorder_failure_abi as abi
import recorder_failure_capture as capture


def load(path):
    spec = importlib.util.spec_from_file_location('_fixture_' + Path(path).stem, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def fixture():
    parser, reader, old = load(abi.D209), load(abi.D173), load(abi.D188)
    sizes = dict(zip(abi.TYPES, (163840, 120, 160000, 2048, 1500, 40, 200, 1)))
    aligns = {name: (1 if name == 'bool' else 4 if name == abi.TYPES[6] else 8) for name in abi.TYPES}
    window_offsets = dict(runner_report=40, transfer_report=161088, transaction_report=159040,
                          session=163000, native_status=1, native_cleanup_verified=192,
                          native_initialized=193, native_attempted=194, native_active=195, native_poisoned=196)
    offsets = {}
    order = ('phase failure dump_setup setup_completed go_seen service_only reset_pending reset_done counters_saturated').split()
    offsets.update({'runner_report.' + name: i for i, name in enumerate(order)})
    words = ('setup_completed_us last_poll_us next_release_us epochs missed_releases maximum_lateness_us '
             'maximum_execution_us release_us stop_us reset_epoch_started_us request_us').split()
    offsets.update({'runner_report.' + name: 12 + 4 * i for i, name in enumerate(words)})
    offsets.update({'runner_report.' + name: 56 + 8 * i for i, name in enumerate(
        ('release_token stop_token reset_from_token request_token').split())})
    words = ('configure_enable_calls configure_pwm_calls write_enable_calls write_pwm_calls settle_calls '
             'enabled_en nonzero_pwm invalid_motor_calls').split()
    offsets.update({'runner_report.' + name: 88 + 4 * i for i, name in enumerate(words)})
    offsets.update(dict(zip(('transfer_report.' + x for x in 'phase reason session epoch bytes frames events crc'.split()),
                            (0, 1, 8, 16, 24, 28, 32, 36))))
    offsets.update(dict(zip(('transaction_report.' + x for x in
        'phase fault decision_made finished timing_valid started_us decision_us completed_us execution_us'.split()),
        (0, 1, 2, 3, 4, 8, 12, 16, 20))))
    numbers, layouts = {}, {}
    for name in abi.TYPES:
        numbers['SIZE ' + name], numbers['ALIGN ' + name] = sizes[name], aligns[name]
        layouts[name] = 'type = bool\n' if name == 'bool' else 'type = struct ' + name + ' {\n int field;\n}\n'
    for key, (_, _, name) in abi.WINDOWS.items():
        numbers['OFFSET ' + key] = window_offsets[key]
        numbers['EXTENT ' + key] = sizes[name] if name else (8 if key == 'session' else 1)
    for parent, member, width, kind in abi.FIELDS:
        if member:
            key = parent + '.' + member
            numbers['FIELD ' + key], numbers['WIDTH ' + key] = offsets[key], width
    for name, values in abi.ENUMS.items():
        numbers['ENUM_WIDTH ' + name] = 1
        numbers.update({'ENUM ' + name + '::' + value: i for i, value in enumerate(values)})
    chunks, counter = [], 0
    for expression in abi.expressions():
        if not expression.startswith('echo SUMOX_'):
            continue
        key = expression[len('echo SUMOX_'):-2]
        counter += 1
        chunks.append('SUMOX_' + key + '\n')
        chunks.append(layouts[key[7:]] if key.startswith('LAYOUT ') else '$' + str(counter) + ' = ' + str(numbers[key]) + '\n')
    elf = (' Type: EXEC (Executable file)\n'
           ' [ 4] .data PROGBITS 20013890 000100 0000d0 00 WA 0 0 4\n'
           ' [ 5] .bss NOBITS 20013960 000200 0282a0 00 WA 0 0 8\n'
           ' 1: 20013960 163840 OBJECT LOCAL DEFAULT 5 _ZN12_GLOBAL__N_16runnerE\n'
           ' 2: 20013890 200 OBJECT LOCAL DEFAULT 4 _ZN12_GLOBAL__N_111native_dumpE\n')
    layout = dict(sections=[dict(name='.data', address=0x20013890, size=208, load_address=0x0810D670),
                            dict(name='.bss', address=0x20013960, size=164512)],
                  bss_zero=dict(start=0x20013960, end=0x2003BAc4),
                  data_copy=dict(destination=0x20013890, bytes=208, source=0x0810D670))
    rows = []
    for command, text in zip(abi.queries(reader), ('readelf version', 'gdb version', elf, ''.join(chunks))):
        rows.append(dict(argv=command, deadline_seconds=60, reap_seconds=5,
            execution=dict(returncode=0, timed_out=False, reaped=True), stdout_bytes=len(text.encode()),
            stdout_base64=base64.b64encode(text.encode()).decode(), stderr_bytes=0, stderr_base64=''))
    result = dict(status='OBSERVED', first_error=None, commands=rows)
    return parser, reader, old, result, layout


def summary(items=None):
    parser, reader, old, result, layout = fixture() if items is None else items
    return abi.summarize(result, layout, parser, reader, old.checked_command)


def change_stream(items, index, old, new):
    row = items[3]['commands'][index]
    raw = base64.b64decode(row['stdout_base64']).decode()
    assert old in raw
    raw = raw.replace(old, new).encode()
    row['stdout_base64'], row['stdout_bytes'] = base64.b64encode(raw).decode(), len(raw)


def make_spec():
    raw = json.dumps(summary()).encode()
    return capture.build_spec(raw, hashlib.sha256(raw).hexdigest(), abi)


def samples(spec):
    return [(label + '.' + str(i), row['address'], bytes(row['bytes']))
            for label in ('first', 'second') for i, row in enumerate(spec['ranges'])]


class AbiTests(unittest.TestCase):
    def test_prepare_composes_pinned_file_only_lifecycle(self):
        owner = abi.prepare_owner('1' * 40)
        self.assertEqual(owner.reviewed_head, '1' * 40)
        self.assertEqual(owner.inputs['reviewed_head'], abi.COMPILE_HEAD)
        self.assertEqual(len(owner.inputs['files']), 144)
        # This controlled host fixture skips only the live clean-HEAD/ADB gate.
        # prepare() contains no transport; any accidental call fails the fixture.
        owner.local = lambda: None
        owner.direct = lambda *a, **k: self.fail('prepare must not contact a board')
        result = owner.prepare()
        self.assertEqual(result['file_commands'], 4)
        self.assertLessEqual(result['command_units'], 30000)
        self.assertEqual(len(owner.remote_pins), 12)
        self.assertIn('D230_FILE_ONLY_ABI', owner.program)
        self.assertNotIn('D188_STATIC_FILE_ONLY_ABI', owner.program)

    def test_inherited_execute_retains_failure_and_closure(self):
        owner = abi.prepare_owner('1' * 40)
        writes, closing = {}, []
        with tempfile.TemporaryDirectory(prefix='sumox-recorder-fixture-') as folder:
            owner.output = Path(folder) / 'owner'
            owner.prepare = lambda: {}
            owner.executor = {'write': lambda path, value: writes.update({path.name: copy.deepcopy(value)})}
            owner.remote_pins, owner.commands, owner.program = {}, [], ''
            owner.bootstrap = 'synthetic-never-executed'
            owner.local_pins = {}
            owner.local = lambda: closing.append(True)
            def failed(*args):
                raise ValueError('synthetic first transport failure')
            owner.direct = failed
            with self.assertRaisesRegex(ValueError, 'synthetic first transport failure'):
                owner.execute()
            self.assertTrue(owner.claimed)
            self.assertEqual(closing, [True])
            self.assertEqual(writes['local_result.json']['status'], 'FAILED')
            self.assertEqual(writes['local_result.json']['final_checks'], [dict(name='local', status='PASS')])

    def test_exact_queries_file_only(self):
        commands = abi.queries(load(abi.D173))
        self.assertEqual(len(commands), 4)
        self.assertIn('set may-call-functions off', commands[-1])
        self.assertIn('set auto-load no', commands[-1])
        self.assertTrue(commands[2][-1].endswith('/recorder.ino.elf'))
        self.assertFalse(any(x.startswith(('target ', 'attach ', 'call ', 'x/')) for x in abi.expressions()))

    def test_valid_data_native_and_bss_runner(self):
        value = summary()
        self.assertEqual(value['objects']['native_dump']['section_name'], '.data')
        self.assertEqual(value['objects']['runner']['section_name'], '.bss')
        self.assertEqual(len(value['layouts']), 8)
        self.assertEqual(set(value['fields']), {p + ('.' + m if m else '') for p, m, w, k in abi.FIELDS})

    def test_initialized_data_boundary_refusals(self):
        for old, new in [('20013890 200 OBJECT', '2001389c 200 OBJECT'),
                         ('DEFAULT 4 _ZN12_GLOBAL__N_111native_dumpE', 'DEFAULT 3 _ZN12_GLOBAL__N_111native_dumpE'),
                         ('20013890 200 OBJECT LOCAL DEFAULT 4', '20013960 200 OBJECT LOCAL DEFAULT 5')]:
            with self.subTest(new=new):
                items = fixture(); change_stream(items, 2, old, new)
                with self.assertRaises(ValueError): summary(items)

    def test_data_copy_and_bss_zero_not_section_size(self):
        for mutation in ('data', 'bss'):
            items = fixture()
            if mutation == 'data': items[4]['data_copy']['bytes'] -= 1
            else: items[4]['bss_zero']['end'] = 0x20013960 + 163839
            with self.assertRaises(ValueError): summary(items)

    def test_duplicate_symbol_and_layout(self):
        items = fixture(); change_stream(items, 2, ' 2: 20013890', ' 2: 20013890')
        row = items[3]['commands'][2]
        raw = base64.b64decode(row['stdout_base64']) + b' 3: 20013890 200 OBJECT LOCAL DEFAULT 4 _ZN12_GLOBAL__N_111native_dumpE\n'
        row['stdout_base64'], row['stdout_bytes'] = base64.b64encode(raw).decode(), len(raw)
        with self.assertRaises(ValueError): summary(items)
        items = fixture(); change_stream(items, 3, 'type = bool\n', 'type = bool\ntype = bool\n')
        with self.assertRaises(ValueError): summary(items)

    def test_marker_enum_field_refusals(self):
        for old, new in [('SUMOX_OFFSET session', 'SUMOX_OFFSET unexpected'),
                         ('SUMOX_WIDTH runner_report.phase', 'SUMOX_FIELD runner_report.phase'),
                         ('SUMOX_ENUM app::Fault::NONE', 'SUMOX_ENUM app::Fault::MISSING')]:
            items = fixture(); change_stream(items, 3, old, new)
            with self.assertRaises(ValueError): summary(items)

    def test_wrong_numeric_width_enum_and_field_overlap(self):
        for marker, value in [('WIDTH runner_report.phase', 2),
                              ('ENUM app::Fault::NONE', 99),
                              ('FIELD runner_report.go_seen', 3)]:
            items = fixture(); row = items[3]['commands'][3]
            text = base64.b64decode(row['stdout_base64']).decode()
            import re
            text, count = re.subn('(SUMOX_' + re.escape(marker) + r'\n\$\d+ = )\d+',
                                 lambda m: m[1] + str(value), text)
            self.assertEqual(count, 1)
            raw = text.encode(); row['stdout_base64'], row['stdout_bytes'] = base64.b64encode(raw).decode(), len(raw)
            with self.assertRaises(ValueError): summary(items)

    def test_stream_checks(self):
        for key, value in [('deadline_seconds', True), ('stderr_bytes', 1)]:
            items = fixture(); items[3]['commands'][0][key] = value
            with self.assertRaises(ValueError): summary(items)

    def test_window_outside_and_overlap(self):
        parser, reader, old, result, layout = fixture()
        blocks = {'SUMOX_OFFSET ' + key: '$1 = 0\n' for key in abi.WINDOWS}
        value = summary()
        for key, w in value['windows'].items():
            blocks['SUMOX_EXTENT ' + key] = '$1 = ' + str(w['bytes']) + '\n'
        with self.assertRaises(ValueError):
            abi.checked_windows(parser, blocks, value['objects'], value['sizes'], value['alignments'])

    def test_descriptor_helpers_are_exact(self):
        names = {'_stamp', '_plain_chain', '_read_handle', 'pinned'}
        self.assertEqual(abi.component((ROOT / abi.D209).read_bytes(), names),
                         abi.component((ROOT / abi.SELF).read_bytes(), names))


class CaptureTests(unittest.TestCase):
    def test_full_flash_before_ram_after_ram(self):
        spec = make_spec(); plan = capture.read_plan(spec)
        self.assertEqual(sum(x[2] for x in plan[:6]), 263680 + 55104)
        self.assertEqual(sum(x[2] for x in plan[-6:]), 263680 + 55104)
        self.assertLess(sum(x[2] for x in plan[6:-6]), 32768)
        self.assertTrue(all(x[1] % 4 == x[2] % 4 == 0 for x in plan[6:-6]))

    def test_raw_missing_stays_incomplete(self):
        spec = make_spec()
        self.assertIsNone(capture.decode_snapshot(spec, [], 'first'))
        result = capture.analysis(spec, [], dict.fromkeys(capture.FLASH_KEYS, False))
        self.assertEqual(result['coherence'], 'UNPROVEN')
        self.assertIsNone(result['equalities'])

    def test_valid_fields_and_invalid_boolean_enum(self):
        spec = make_spec(); raw = samples(spec)
        value = capture.decode_snapshot(spec, raw, 'first')
        self.assertFalse(value['session_matches_expected'])
        for key, bad in [('runner_report.go_seen', 2), ('native_status', 255)]:
            broken = copy.deepcopy(raw)
            field = spec['abi']['fields'][key]
            target = spec['abi']['windows'][field['window']]['address'] + field['offset']
            for i, (name, start, body) in enumerate(broken):
                if name.startswith('first.') and start <= target < start + len(body):
                    body = bytearray(body); body[target - start] = bad
                    broken[i] = name, start, bytes(body)
            result = capture.analysis(spec, broken, dict.fromkeys(capture.FLASH_KEYS, True))
            self.assertEqual(len(result['decode_errors']), 1)
            self.assertIsNone(result['first'])
            self.assertEqual(result['coherence'], 'UNPROVEN')

    def test_spec_hash_and_window_mutation(self):
        raw = json.dumps(summary()).encode()
        with self.assertRaises(ValueError): capture.build_spec(raw, '0' * 64, abi)
        value = json.loads(raw); value['windows']['session']['offset'] += 1
        raw = json.dumps(value).encode()
        with self.assertRaises(ValueError): capture.build_spec(raw, hashlib.sha256(raw).hexdigest(), abi)

    def test_first_flash_mismatch_stops_before_ram(self):
        spec = make_spec()
        deps = SimpleNamespace(capture=SimpleNamespace(Capture=object), p0=SimpleNamespace(ram_range=lambda a, b: None))
        cls = capture.capture_type(deps, spec, hashlib.sha256(capture.canonical(spec)).hexdigest())
        obj = cls(); obj.plan = capture.read_plan(spec); obj.samples = []
        obj.report = dict(first_error=None, analysis=None)
        obj.loader, obj.sketch = bytes(263680), bytes(55104)
        seen = []
        def read(index, item):
            seen.append(item)
            obj.samples.append((item[0], item[1], b'x' * item[2]))
        obj.one_read, obj.budget = read, lambda: None
        with self.assertRaises(ValueError): obj.gather()
        self.assertEqual(len(seen), 5)
        self.assertFalse(any(name.startswith(('first.', 'second.')) for name, _, _ in seen))

    def test_two_snapshots_and_final_flash(self):
        spec = make_spec(); deps = SimpleNamespace(capture=SimpleNamespace(Capture=object))
        cls = capture.capture_type(deps, spec, hashlib.sha256(capture.canonical(spec)).hexdigest())
        obj = cls(); obj.plan = capture.read_plan(spec); obj.samples = []
        obj.report = dict(first_error=None, analysis=None, reads=[], counts=dict(commands=0, reads=0, requested_bytes=0))
        obj.loader, obj.sketch, pauses = bytes(263680), bytes(55104), []
        def read(index, item):
            obj.samples.append((item[0], item[1], bytes(item[2])))
            obj.report['reads'].append(item)
            obj.report['counts']['commands'] += 1; obj.report['counts']['reads'] += 1
            obj.report['counts']['requested_bytes'] += item[2]
        obj.one_read, obj.budget, obj.pause = read, lambda: None, lambda: pauses.append(True)
        obj.gather()
        self.assertEqual(pauses, [True]); self.assertTrue(obj.complete())
        self.assertEqual(obj.report['analysis']['coherence'], 'UNPROVEN')


if __name__ == '__main__':
    unittest.main()
