# Tests D199 entry bytes and fixed observations from its independent contract.
# Retains19 historical methods with explicit metadata fixtures plus4 focused checks.
# Synthetic instructions validate parsing only; freeze precedes new subject reads.
import ast
import base64
import builtins
import copy
import hashlib
import json
from pathlib import Path
import sys
import types
import unittest
from unittest import mock

ROOT = Path(__file__).absolute().parents[2]
RAW = 'state/analysis/P7_motor_settle_compile_raw'
WRAPPER = RAW + '/inspect_static_entry.py'
ABI = RAW + '/inspect_static_abi.py'
PARSER = 'state/analysis/P7_app_motor_fault_compile_raw/inspect_static_entry.py'
CONTRACT = 'state/analysis/P7_motor_settle_entry_contract.md'
CONTRACT_PIN = (19485, 'af8ce726bf49b79fecc07548bd78a808d788894ea9e9e1b59daa69eae8a54e7d')
BINDING = RAW + '/entry_binding01.json'
HISTORICAL = 'tests/tooling/test_app_motor_observe_entry.py'
HISTORICAL_PIN = (29705, 'b7db0b43ae5e487cd6475e0b6dd6272d33a8316bcfba64a07f6c2a3e2c0415d8')
ABI_ORACLE = 'tests/tooling/test_motor_settle_abi.py'
ABI_ORACLE_PIN = (30983, '96763b42d61b80654503f4093d32ac3b174ab2152fdfb795b3801304e4e2b252')
OWNER = '/home/arduino/sumox26_codex_build/app-motor-settle-static01'
SCOPE = '/home/arduino/sumox26_codex_build/app-motor-settle-entry-static01'
PINS = {
    ABI: (16106, '0f2b37c906a8ad78d596a1256af94d67d3d47793f6025a5e9dc4449d928002ea'),
    PARSER: (10317, 'cb9ee5bbd5ca8a74510185d77e7d880acf1a03f05608a5ea1459e534a287fa34'),
    RAW + '/native_abi_static01/result.json': (905572, '230ef847f74e84d032a87336f74a4817d4cd8317a0ea5abc72c54fdd0d03eb6e'),
    RAW + '/native_abi_static01/abi.json': (5410, '069ed01bee9fba11159a4d93d156b8ada35ea5c11414b77870d80b6182d59941'),
    RAW + '/native_abi_static01/local_result.json': (275, 'eb68ef2e125445ad94fc5c0dc251c2a411d55120ab1299e205a1674b572576f9'),
    'state/reviews/P7_motor_settle_abi_actual_review.md': (7312, 'a7c3993ab5e0d008b4464bf93f89b5877447992fa8e3197d8c869812e11f874f'),
    RAW + '/native_static01/artifacts.json': (9648, 'e18384c14c0b1367667b265ab4c532a4010be65697460a1cd45487bccd9eca10'),
    BINDING: (20870, '6234676242fdd7e61136fd2a1f66fabb0242b10ee597ef2bf6555a9444ecfd2b'),
}
FIXTURE_CHANGES = (
    ("('global_initializer', 'candidate_rate', 'candidate_period')",
     "('global_initializer', 'candidate_rate', 'candidate_period', 'publish_settle')", 1),
    ('D194_STATIC_FILE_ONLY_ENTRY', 'D199_STATIC_FILE_ONLY_ENTRY', 2),
    ('D194_STATIC_FILE_ONLY_ABI02', 'D199_STATIC_FILE_ONLY_ABI', 1),
    ('08116238', '081162d8', 6), ('0811623c', '081162dc', 4),
    ('0x16228', '0x162c8', 1),
    ('self.assertEqual(len(self.ranges), 27)', 'self.assertEqual(len(self.ranges), 29)', 1),
    ("self.assertEqual(len(answer['disassembly']), 27)", "self.assertEqual(len(answer['disassembly']), 29)", 1),
    ("self.assertEqual(len(writes[2][1]['disassembly']), 27)", "self.assertEqual(len(writes[2][1]['disassembly']), 29)", 1),
    ('SUMOX_ENTRY_27\\n', 'SUMOX_ENTRY_29\\n', 1),
    ('test_all_six_inputs_are_verified_before_private_execution',
     'test_all_nine_inputs_are_verified_before_private_execution', 1),
    ('test_exact_four_file_queries_and_all_twenty_seven_ranges',
     'test_exact_four_file_queries_and_all_twenty_nine_ranges', 1),
)
ADDED = {
    'publish_settle': (0x08110d60, 0x08110d9c,
        '_ZN6motors12_GLOBAL__N_113publishSettleENS_17SettleProbeReasonEjjhh', 'LOCAL'),
    'motor_settle': (0x081115bc, 0x081116e0, '_ZN6motors8UnoQPort6settleEPv', 'GLOBAL'),
}


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def checked(name, pin):
    raw = (ROOT / name).read_bytes()
    if (len(raw), digest(raw)) != pin:
        raise AssertionError('Frozen entry oracle input changed: ' + name)
    return raw


def module(raw, path, name):
    value = types.ModuleType(name); value.__file__ = str(path)
    value.__dict__['__builtins__'] = dict(vars(builtins))
    exec(compile(raw, str(path), 'exec'), value.__dict__)
    return value


def replace_checked(raw, changes):
    for before, after, count in changes:
        before, after = before.encode(), after.encode()
        if raw.count(before) != count:
            raise AssertionError('Independent fixture occurrence: ' + repr(before))
        raw = raw.replace(before, after)
    return raw


def binding():
    return json.loads(checked(BINDING, PINS[BINDING]))


def projection(raw, kind):
    spec = binding()['projection']; identity = spec[kind + '_input']
    if type(raw) is not bytes or (len(raw), digest(raw)) != (identity['bytes'], identity['sha256']):
        raise AssertionError('Independent projection input identity')
    rows = spec[kind + '_replacements']
    value = replace_checked(raw, [(row['old'], row['new'], row['count']) for row in rows])
    identity = spec[kind + '_output']
    if (len(value), digest(value)) != (identity['bytes'], identity['sha256']):
        raise AssertionError('Independent projection output identity')
    return value


def set_up_inputs(cls):
    if not sys.dont_write_bytecode:
        raise RuntimeError('Independent entry oracle requires Python -B')
    cls.raw = (ROOT / WRAPPER).read_bytes()
    cls.inputs = {name: checked(name, pin) for name, pin in PINS.items()}
    cls.contract = checked(CONTRACT, CONTRACT_PIN)
    cls.binding = json.loads(cls.inputs[BINDING])
    helpers = module(checked(ABI_ORACLE, ABI_ORACLE_PIN), ROOT / ABI_ORACLE, '_entry_d199_abi_oracle')
    cls.support = helpers.helper('base')
    cls.projected02 = helpers.projection(helpers.input_projection())
    cls.ranges = tuple((row['label'], row['start'], row['end'],
        tuple(symbol['name'] for symbol in row['symbols'])) for row in cls.binding['ranges'])
    cls.bounds = {row['name']: row['value'] for row in cls.binding['initialization']['bounds']}
    if (len(cls.inputs), len(cls.ranges)) != (8, 29):
        raise AssertionError('Expected eight originals and29 fixed groups')


def private_oracle():
    raw = checked(HISTORICAL, HISTORICAL_PIN); lines = raw.splitlines(keepends=True)
    node = next(n for n in ast.parse(raw).body if isinstance(n, ast.ClassDef) and n.name == 'EntryContract')
    before = b''.join(lines[node.lineno-1:node.end_lineno])
    if raw.count(before) != 1: raise AssertionError('Unique historical entry class')
    raw = raw.replace(before, replace_checked(before, FIXTURE_CHANGES))
    if (len(raw), digest(raw)) != (29721, '1b03c64cb653d96fbe6b83d21d3a668c6c3ebf4556a7bb0e1233a108f17e0454'):
        raise AssertionError('Private entry fixture identity')
    oracle = module(raw, ROOT / HISTORICAL, '_d199_private_entry_oracle')
    oracle.RAW, oracle.WRAPPER, oracle.ABI02 = RAW, WRAPPER, ABI
    oracle.CONTRACT, oracle.CONTRACT_SHA, oracle.PINS = CONTRACT, CONTRACT_PIN[1], dict(PINS)
    oracle.OWNER, oracle.SCOPE = OWNER, SCOPE
    oracle.reader_projection = lambda raw: projection(raw, 'reader')
    oracle.parser_projection = lambda raw: projection(raw, 'parser')
    oracle.EntryContract.setUpClass = classmethod(set_up_inputs)
    for name, method in vars(FocusedEntry).items():
        if name.startswith('test_'): setattr(oracle.EntryContract, name, method)
    return oracle


class FocusedEntry:
    def test_binding_matches_accepted_symbols_and_separate_report_without_invented_contents(self):
        historical = module(self.inputs[PARSER], ROOT / PARSER, '_entry_symbol_reader_only')
        actual = json.loads(self.inputs[RAW + '/native_abi_static01/result.json'])
        elf_bytes = base64.b64decode(actual['commands'][2]['stdout_base64'], validate=True)
        self.assertEqual((len(elf_bytes), digest(elf_bytes)),
            (158956, '4aece135bfa9e429227e0ee17c59b54db1a1bf100fdc714de0076361f7ee1e8b'))
        rows = historical.symbol_rows(elf_bytes.decode())
        self.assertEqual(len(self.ranges), 29)
        self.assertEqual(sum(len(row['symbols']) for row in self.binding['ranges']), 31)
        for group in self.binding['ranges']:
            for symbol in group['symbols']:
                self.assertEqual(rows[symbol['name']], [(symbol['value'], symbol['bytes'],
                    symbol['type'], symbol['binding'], symbol['section'])])
                self.assertEqual((symbol['value'], symbol['bytes']),
                    (group['start'] | 1, group['end'] - group['start']))
        for symbol in self.binding['initialization']['bounds']:
            self.assertEqual(rows[symbol['name']], [(symbol['value'], 0, 'NOTYPE', symbol['binding'], 2)])
        probe = self.binding['settle_probe']
        self.assertEqual(rows[probe['name']], [(0x2003d3e8, 28, 'OBJECT', 'LOCAL', 5)])
        accepted = json.loads(self.inputs[RAW + '/native_abi_static01/abi.json'])['settle_probe']
        self.assertEqual((accepted['symbol'], accepted['address'], accepted['bytes']),
            (probe['name'], probe['value'], probe['bytes']))
        self.assertIs(self.binding['initialization']['contents_observed'], False)
        self.assertEqual(self.binding['initialization']['expected_pointer'], 0x08100105)
        self.assertEqual((self.binding['disassembly_groups'], self.binding['gdb_expressions']), (29, 59))

    def test_added_functions_require_exact_unique_binding_thumb_size_type_and_section(self):
        reader = self.loaded(); result, layout, _, rows = self.packet()
        elf = self.support.stream_text(result, 2)
        for label, (start, end, name, bind) in ADDED.items():
            matches = [row for row in self.ranges if row[0] == label]
            self.assertEqual(matches, [(label, start, end, (name,))])
            row = rows[name]; self.assertEqual(elf.count(row), 1)
            wrong_bind = 'GLOBAL' if bind == 'LOCAL' else 'LOCAL'
            variants = ('', row + row, row.replace(bind, wrong_bind),
                row.replace(f'{start | 1:08x}', f'{start:08x}'),
                row.replace(f' {end-start} FUNC', f' {end-start+2} FUNC'),
                row.replace('FUNC', 'OBJECT'), row.replace('DEFAULT 1', 'DEFAULT 2'))
            for bad in variants:
                with self.subTest(label=label, row=bad):
                    self.assertNotEqual(row, bad)
                    value = copy.deepcopy(result)
                    self.support.replace_text(value, 2, elf.replace(row, bad))
                    self.reject(lambda: reader.summarize(value, layout))

    def test_each_added_range_requires_its_markers_and_complete_disassembly(self):
        reader = self.loaded(); result, layout, blocks, _ = self.packet()
        debug = self.support.stream_text(result, 3)
        for label in ADDED:
            indices = [i for i, row in enumerate(self.ranges) if row[0] == label]
            self.assertEqual(len(indices), 1); index = indices[0]
            marker = f'SUMOX_ENTRY_{index:02d}\n'; block = blocks[index]
            self.assertEqual(debug.count(marker), 1); self.assertEqual(debug.count(block), 1)
            lines = block.splitlines(keepends=True)
            bad_blocks = (''.join(lines[:-2] + lines[-1:]),
                ''.join(lines[:2] + [lines[1]] + lines[2:]),
                block.replace('f000 f800 fixture-wide', 'zzzz fixture-wide'),
                block.replace('End of assembler dump.\n', ''))
            variants = [debug.replace(marker, ''), debug.replace(marker, marker + marker)]
            for bad in bad_blocks:
                self.assertNotEqual(block, bad); variants.append(debug.replace(block, bad))
            for changed in variants:
                with self.subTest(label=label):
                    self.assertNotEqual(debug, changed)
                    value = copy.deepcopy(result); self.support.replace_text(value, 3, changed)
                    self.reject(lambda: reader.summarize(value, layout))

    def test_direct_entry_summary_does_not_call_abi_summary_or_require_abi_tags(self):
        execute = builtins.exec; inherited_summaries = []
        def observed_exec(code, namespace, *args):
            value = execute(code, namespace, *args)
            if namespace.get('__file__') == str(ROOT / ABI):
                original = namespace['load_reader']
                def loaded(*args, **kwargs):
                    reader = original(*args, **kwargs)
                    forbidden = mock.Mock(side_effect=AssertionError('Inherited ABI summary called'))
                    reader.summarize = forbidden; inherited_summaries.append(forbidden)
                    return reader
                namespace['load_reader'] = loaded
            return value
        self.subject.__dict__['__builtins__']['exec'] = observed_exec
        reader = self.loaded(); self.assertEqual(len(inherited_summaries), 1)
        result, layout, _, _ = self.packet(); before = copy.deepcopy(result)
        for tag in ('SUMOX_SIZE', 'SUMOX_ALIGN', 'SUMOX_FIELD_OFFSET', 'SUMOX_REASON', 'polls'):
            self.assertNotIn(tag, self.support.stream_text(result, 3))
        answer = reader.summarize(result, layout)
        inherited_summaries[0].assert_not_called()
        self.assertEqual(answer['status'], 'STATIC_ENTRY_OBSERVED')
        self.assertEqual(len(answer['disassembly']), 29)
        for key in ('settle_probe', 'polls_alignment_type', 'readelf_size_projection'):
            self.assertNotIn(key, answer)
        self.assertEqual(result, before)


def load_tests(loader, standard, pattern):
    oracle = private_oracle()
    suite = loader.loadTestsFromTestCase(oracle.EntryContract)
    if suite.countTestCases() != 23: raise AssertionError('Expected19 historical+4 focused entry methods')
    return unittest.TestSuite([standard, suite])


if __name__ == '__main__':
    unittest.main(verbosity=2)
