# Checks the D238 identity and unchanged eight-byte failure record using synthetic layouts.
# Reuses D230 fixture construction and exact production parsers without board access.
# Runs only new projection/composition seams; inherited lifecycle tests stay unchanged.
import ast
import base64
import copy
import hashlib
import json
from pathlib import Path
import re
import sys
import types
import unittest

ROOT = Path(__file__).absolute().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import recorder_six_result_abi as abi
import recorder_six_result_capture as capture
import run_recorder_six_result_capture as caller


def fixture_module():
    path = ROOT / 'tests/test_recorder_failure.py'
    raw = path.read_text().split('class AbiTests(unittest.TestCase):')[0]
    raw = raw.replace('recorder_failure_abi', 'recorder_six_result_abi')
    raw = raw.replace('recorder_failure_capture', 'recorder_six_result_capture')
    raw = raw.replace('1500, 40, 200, 1)', '1500, 40, 208, 1, 8)')
    raw = raw.replace("1 if name == 'bool'", "1 if name in ('bool', abi.TYPES[8])")
    raw = raw.replace('native_poisoned=196)', 'native_poisoned=196, first_failure=200, packet_started_us=188)')
    raw = raw.replace("else (8 if key == 'session' else 1)",
                      "else (8 if key == 'session' else 4 if key == 'packet_started_us' else 1)")
    raw = raw.replace('    numbers, layouts = {}, {}',
        "    offsets.update({'first_failure.' + name: i for i, name in enumerate(\n"
        "        'reason site cleanup cleanup_ownership packet_offset packet_size payload_size ownership_evaluated'.split())})\n"
        '    numbers, layouts = {}, {}')
    raw = raw.replace('20013890 200 OBJECT', '20013890 208 OBJECT')
    module = types.ModuleType('fresh_synthetic_fixture')
    module.__file__ = str(path)
    exec(compile(raw, str(path), 'exec'), module.__dict__)
    return module


def put(spec, samples, key, value):
    field = spec['abi']['fields'][key]
    address = spec['abi']['windows'][field['window']]['address'] + field['offset']
    answer = []
    for name, base, raw in samples:
        body = bytearray(raw)
        if base <= address < base + len(body):
            body[address - base:address - base + field['bytes']] = value.to_bytes(field['bytes'], 'little')
        answer.append((name, base, bytes(body)))
    return answer


class SixResultTests(unittest.TestCase):
    def test_complete_reverse_projection_and_no_stale_executable_identity(self):
        records = json.loads((ROOT / abi.RAW / 'derivation01.json').read_bytes())
        for record in records.values():
            raw = (ROOT / record['path']).read_bytes()
            self.assertEqual(dict(bytes=len(raw), sha256=abi.sha(raw)), record['after'])
            for node in ast.walk(ast.parse(raw)):
                if isinstance(node, ast.Constant) and isinstance(node.value, (str, int)):
                    self.assertNotIn(node.value, (55104, 144, 109, 3997245574426120340, 572412568535289530))
                    if isinstance(node.value, str):
                        self.assertNotIn('377911abefabd094', node.value)
                        self.assertNotIn('004dc7cff534896a851901f9d7d0ba6066cae060', node.value)
                        for stale in ('07f19e32c483ceba', 'ce4e69390d21d9a91231581a186be4a63213135e',
                                      '29cb1e76193e4b7c562d1fd842039f61367a82c2651a2303c09518d35a0c7ce9',
                                      'b13a32b5e92993a49f165b907d5d6036fa933e1680bb23ff2738620b294fd584'):
                            self.assertNotIn(stale, node.value)
            for step in reversed(record['steps']):
                self.assertEqual(raw.count(step['new'].encode()), step['count'])
                raw = raw.replace(step['new'].encode(), step['old'].encode())
            self.assertEqual(raw, (ROOT / record['template']).read_bytes())

    def test_exact_d231_enum_field_inventory_and_all_fresh_queries(self):
        header = (ROOT / 'src/hal/dump_uart_unoq.h').read_text()
        for name in ('FailureSite', 'CleanupDisposition'):
            body = re.search(r'enum class ' + name + r' : std::uint8_t \{(.*?)\};', header, re.S)[1]
            self.assertEqual(abi.ENUMS['recorder::dump::' + name], body.replace(',', ' ').split())
        self.assertEqual(len(abi.FIELDS), 65)
        self.assertEqual(len(abi.WINDOWS), 12)
        self.assertEqual(len(abi.TYPES), 9)
        fields = [row for row in abi.FIELDS if row[0] == 'first_failure']
        self.assertEqual([row[1] for row in fields],
            'reason site cleanup cleanup_ownership packet_offset packet_size payload_size ownership_evaluated'.split())
        self.assertTrue(all(row[2] == 1 for row in fields))
        expressions = abi.expressions()
        self.assertEqual(expressions.count('p/d sizeof(recorder::dump::FailureRecord)'), 1)
        for parent, member, width, kind in fields:
            self.assertIn('p/d sizeof(((recorder::dump::FailureRecord*)0)->' + member + ')', expressions)
        plan = json.loads((ROOT / abi.RAW / 'plan.json').read_bytes())
        self.assertEqual(plan['expressions'], expressions)

    def test_packet_start_exact_uint32_queries_bounds_and_schema(self):
        f = fixture_module(); good = f.summary(); spec = f.make_spec()
        self.assertEqual(abi.WINDOWS['packet_started_us'], ('native_dump', 'started_us_', None))
        self.assertEqual([field for field in abi.FIELDS if field[0] == 'packet_started_us'],
                         [('packet_started_us', '', 4, 'uint')])
        self.assertEqual(good['windows']['packet_started_us']['bytes'], 4)
        self.assertIn('p/d sizeof(((recorder::dump::UnoQDumpPort*)0)->started_us_)', abi.expressions())
        self.assertIn('p/d (unsigned long)&((recorder::dump::UnoQDumpPort*)0)->started_us_', abi.expressions())
        for value in (0, 100000, 0xfffffff0, 0xffffffff):
            samples = put(spec, f.samples(spec), 'packet_started_us', value)
            self.assertEqual(capture.decode_snapshot(spec, samples, 'first')['fields']['packet_started_us'], value)
        for marker, value in [('EXTENT packet_started_us', 3), ('OFFSET packet_started_us', 208),
                              ('OFFSET packet_started_us', 189), ('OFFSET packet_started_us', 192)]:
            items = f.fixture(); row = items[3]['commands'][3]
            text = base64.b64decode(row['stdout_base64']).decode()
            text, count = re.subn(r'(SUMOX_' + re.escape(marker) + r'\n\$\d+ = )\d+',
                                  lambda match: match[1] + str(value), text)
            self.assertEqual(count, 1)
            row['stdout_base64'] = base64.b64encode(text.encode()).decode()
            row['stdout_bytes'] = len(text.encode())
            with self.assertRaises(ValueError): f.summary(items)
        for kind in ('missing', 'width', 'kind'):
            changed = copy.deepcopy(good)
            if kind == 'missing': del changed['windows']['packet_started_us']
            else: changed['fields']['packet_started_us'][{'width': 'bytes', 'kind': 'kind'}[kind]] = 1 if kind == 'width' else 'bool'
            raw = json.dumps(changed).encode()
            with self.assertRaises(ValueError): capture.build_spec(raw, abi.sha(raw), abi)

    def test_first_record_extent_overlap_and_field_width_refuse(self):
        f = fixture_module()
        good = f.summary()
        self.assertEqual(good['windows']['first_failure']['bytes'], 8)
        self.assertEqual(good['objects']['native_dump']['section_name'], '.data')
        for marker, value in [('EXTENT first_failure', 7), ('OFFSET first_failure', 201),
                              ('FIELD first_failure.site', 0), ('WIDTH first_failure.reason', 2)]:
            items = f.fixture()
            row = items[3]['commands'][3]
            text = base64.b64decode(row['stdout_base64']).decode()
            text, count = re.subn(r'(SUMOX_' + re.escape(marker) + r'\n\$\d+ = )\d+',
                                  lambda m: m[1] + str(value), text)
            self.assertEqual(count, 1)
            row['stdout_base64'] = base64.b64encode(text.encode()).decode()
            row['stdout_bytes'] = len(text.encode())
            with self.assertRaises(ValueError):
                f.summary(items)

    def test_all_first_failure_enum_values_and_original_progress_decode(self):
        f = fixture_module(); spec = f.make_spec()
        values = {'reason': 9, 'site': 12, 'cleanup': 4, 'cleanup_ownership': 1,
                  'packet_offset': 37, 'packet_size': 79, 'payload_size': 64, 'ownership_evaluated': 1}
        samples = f.samples(spec)
        for key, value in values.items():
            samples = put(spec, samples, 'first_failure.' + key, value)
        observed = capture.analysis(spec, samples, dict.fromkeys(capture.FLASH_KEYS, True))
        self.assertEqual(observed['coherence'], 'UNPROVEN')
        decoded = observed['first']['fields']
        self.assertEqual(decoded['first_failure.reason']['name'], 'TIMEOUT')
        self.assertEqual(decoded['first_failure.site']['name'], 'TRANSMIT_DEADLINE')
        self.assertEqual(decoded['first_failure.cleanup']['name'], 'VERIFIED')
        for name in ('packet_offset', 'packet_size', 'payload_size', 'ownership_evaluated'):
            self.assertEqual(decoded['first_failure.' + name], values[name])
        for key in ('reason', 'site', 'cleanup', 'cleanup_ownership'):
            field = spec['abi']['fields']['first_failure.' + key]
            for name, value in spec['abi']['enums'][field['kind']].items():
                decoded = capture.decode_snapshot(spec, put(spec, f.samples(spec), 'first_failure.' + key, value), 'first')
                self.assertEqual(decoded['fields']['first_failure.' + key]['name'], name)

    def test_invalid_first_record_bool_or_enum_preserves_raw_failure(self):
        f = fixture_module(); spec = f.make_spec()
        for key in ('reason', 'site', 'cleanup', 'cleanup_ownership', 'ownership_evaluated'):
            samples = put(spec, f.samples(spec), 'first_failure.' + key, 255)
            observed = capture.analysis(spec, samples, dict.fromkeys(capture.FLASH_KEYS, True))
            self.assertEqual(len(observed['decode_errors']), 2)
            self.assertIsNone(observed['first'])
            self.assertEqual(observed['coherence'], 'UNPROVEN')
            self.assertTrue(any(255 in body for name, address, body in samples))

    def test_real_file_owner_composes_145_inputs_110_staged_without_transport(self):
        owner = abi.prepare_owner('1' * 40)
        self.assertEqual(len(owner.inputs['files']), 145)
        self.assertEqual(len(owner.code), 145)
        owner.local = lambda: None
        owner.direct = lambda *a, **k: self.fail('No native transport allowed')
        result = owner.prepare()
        self.assertEqual(result['file_commands'], 4)
        self.assertEqual(len(owner.remote_pins), 12)
        self.assertIn('D238_FILE_ONLY_ABI', owner.program)
        self.assertNotIn('D233_FILE_ONLY_ABI', owner.program)
        self.assertLessEqual(result['command_units'], 30000)

    def test_real_capture_projection_and_complete_new_flash_plan(self):
        f = fixture_module(); spec = f.make_spec()
        plan = capture.read_plan(spec)
        self.assertEqual(plan[5], ('before.sketch.0', 0x08100000, 55376))
        self.assertEqual(plan[-6], ('after.sketch.0', 0x08100000, 55376))
        self.assertEqual(sum(size for name, addr, size in plan[:6]), 319056)
        self.assertEqual(sum(size for name, addr, size in plan[-6:]), 319056)
        self.assertTrue(all(name.startswith(('first.', 'second.')) for name, addr, size in plan[6:-6]))
        source = caller.adapter_source(spec, (ROOT / 'tools/recorder_six_result_capture.py').read_bytes())
        pin = dict(path=capture.bindings()['output'] + '-adapter/remote.py', bytes=len(source), sha256=abi.sha(source))
        legacy = caller.old_caller(ROOT)
        actual, counts = caller.project_actions(legacy.actions, spec, pin)
        self.assertEqual(actual, plan)
        self.assertEqual(counts['requested_bytes'], sum(size for name, addr, size in plan))
        self.assertIn(capture.RUN_ID, legacy.actions._RETRIEVAL_SOURCE)
        self.assertNotIn('377911abefabd094', legacy.actions._RETRIEVAL_SOURCE)
        self.assertEqual(capture.BASE_FILES['sketch'][:2],
            (55376, '3b4812a7a57ec964437d6d1048f96724e3fed5d0a3f9419acd26adbcd5e70a5d'))


if __name__ == '__main__':
    unittest.main()
