# Checks ordinary entry observations against the adopted D210 contract and saved symbols.
# Retains scoped historical assertions with explicit independent fixture projections.
# Frozen host tests use synthetic instructions and block compiler, network and device calls.
import ast
import base64
import builtins
import copy
import hashlib
import json
from pathlib import Path
import re
import socket
import subprocess
import sys
import types
import unittest
from unittest import mock

ROOT = Path(__file__).absolute().parents[2]
RAW = 'state/analysis/P7_ordinary_app_static_compile_raw'
SUBJECT = RAW + '/inspect_static_entry.py'
CONTRACT = 'state/analysis/P7_ordinary_app_entry_contract.md'
FIXTURE = RAW + '/entry_fixture_derivation01.json'
FIXTURE_PIN = {'bytes': 172635, 'sha256': '40f3d0a6f32a9dd4d9a23d6449f054cba1985a7809486100835d18344eef3a39'}
PLAN = None
PREFIX = '/home/arduino/.arduino15/packages/zephyr/tools/arm-zephyr-eabi/1.0.1/bin/arm-zephyr-eabi-'
OWNER = '/home/arduino/sumox26_codex_build/ordinary-app-static01'


def identity(raw):
    return dict(bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest())


def checked(name, pin):
    value = (ROOT / name).read_bytes()
    if identity(value) != dict(bytes=pin['bytes'], sha256=pin['sha256']):
        raise AssertionError('Independent D210 pin differs: ' + name)
    return value


def data():
    global PLAN
    if PLAN is None:
        PLAN = json.loads(checked(FIXTURE, FIXTURE_PIN))
    return PLAN


def project(raw, steps):
    for step in steps:
        old, new = step['old'].encode('ascii'), step['new'].encode('ascii')
        if identity(raw) != step['before'] or raw.count(old) != step['count']:
            raise AssertionError('Independent D210 projection input/count differs')
        raw = raw.replace(old, new)
        if identity(raw) != step['after']:
            raise AssertionError('Independent D210 projection output differs')
    return raw


def module(raw, path, name):
    value = types.ModuleType(name)
    value.__file__ = str(ROOT / path)
    value.__dict__['__builtins__'] = dict(vars(builtins))
    exec(compile(raw, value.__file__, 'exec'), value.__dict__)
    return value


def fixture_module(kind):
    row = data()['fixtures'][kind]
    source = project(checked(row['path'], row['original']), row['steps'])
    if identity(source) != row['projected']:
        raise AssertionError('Independent fixture output differs')
    return module(source, row['path'], '_d210_' + kind + '_fixture')


def guarded_gdb(path, expressions):
    value = [PREFIX + 'gdb', '-nx', '-nh', '-batch', '-iex', 'set auto-load no', path,
             '-ex', 'set language c++', '-ex', 'set may-call-functions off']
    for expression in expressions:
        value += ['-ex', expression]
    return value


def expected_commands(ranges):
    expressions = []
    for index, (_, start, end, _) in enumerate(ranges):
        expressions += [f'echo SUMOX_ENTRY_{index:02d}\\n',
                        f'disassemble /r 0x{start:08x},0x{end:08x}']
    expressions += ['echo SUMOX_ENTRY_END\\n']
    build = OWNER + '/build/app.ino'
    return [[PREFIX + 'readelf', '--version'], [PREFIX + 'gdb', '--version'],
            [PREFIX + 'readelf', '-hSWs', '-x', '.init_array', build + '.elf'],
            guarded_gdb(build + '_debug.elf', expressions)]


def set_up_inputs(cls):
    if not sys.dont_write_bytecode:
        raise RuntimeError('D210 independent oracle requires Python -B')
    spec = data()
    cls.raw = checked(SUBJECT, spec['prospective_subject'])
    cls.inputs = {name: checked(name, pin) for name, pin in spec['originals'].items()}
    cls.contract = checked(CONTRACT, spec['inputs'][CONTRACT])
    cls.binding = json.loads(cls.inputs[RAW + '/entry_binding01.json'])
    support = spec['support']
    cls.support = module(checked(support['path'], support), support['path'], '_d210_record_support')
    source = checked(spec['reader_base'], spec['inputs'][spec['reader_base']])
    cls.projected02 = project(source, spec['ordinary_abi_projection_steps'])
    if identity(cls.projected02) != cls.binding['projection']['reader']['input']:
        raise AssertionError('Ordinary reader input differs')
    cls.ranges = tuple((g['label'], g['start'], g['end'],
                       tuple(s['name'] for s in g['symbols'])) for g in cls.binding['ranges'])
    cls.bounds = {s['name']: s['value'] for s in cls.binding['initialization']['bounds']}
    if len(cls.inputs) != 8 or len(cls.ranges) != 64:
        raise AssertionError('Expected eight originals and64 ordinary groups')


def set_up_case(self):
    for owner, names in ((subprocess, ('run', 'Popen', 'call', 'check_call', 'check_output')),
                         (socket, ('socket', 'create_connection'))):
        for name in names:
            patch = mock.patch.object(owner, name, side_effect=AssertionError('External effect: ' + name))
            patch.start()
            self.addCleanup(patch.stop)
    self.subject = module(self.raw, SUBJECT, '_d210_independent_subject')


def historical():
    spec = data()
    oracle = fixture_module('base')
    oracle.RAW, oracle.WRAPPER, oracle.ABI02 = RAW, SUBJECT, RAW + '/inspect_static_abi.py'
    oracle.CONTRACT, oracle.CONTRACT_SHA = CONTRACT, spec['inputs'][CONTRACT]['sha256']
    oracle.PINS = {name: (pin['bytes'], pin['sha256']) for name, pin in spec['originals'].items()}
    oracle.OWNER, oracle.SCOPE = OWNER, spec['remote_scope']
    oracle.PREFIX, oracle.guarded_gdb, oracle.expected_commands = PREFIX, guarded_gdb, expected_commands
    oracle.reader_projection = lambda raw: project(raw, spec['binding_projection']['reader']['steps'])
    oracle.parser_projection = lambda raw: project(raw, spec['binding_projection']['parser']['steps'])
    oracle.EntryContract.setUpClass = classmethod(set_up_inputs)
    oracle.EntryContract.setUp = set_up_case
    focused = fixture_module('direct')
    focused.ABI = oracle.ABI02
    name = spec['direct_method']
    setattr(oracle.EntryContract, name, getattr(focused.FocusedEntry, name))
    return oracle


def check_census(case):
    result = json.loads(case.inputs[RAW + '/native_abi_static01/result.json'])
    elf = base64.b64decode(result['commands'][2]['stdout_base64'], validate=True)
    case.assertEqual(identity(elf), data()['elf_identity'])
    text = elf.decode('ascii')
    tuples = re.findall(r'^[ \t]*(\d+):[ \t]+([0-9a-fA-F]+)[ \t]+(\S+)[ \t]+(\S+)'
                        r'[ \t]+(\S+)[ \t]+(\S+)[ \t]+(\S+)(?:[ \t]+(.*?))?[ \t]*$', text, re.M)
    case.assertEqual([int(row[0]) for row in tuples], list(range(2234)))
    case.assertEqual(re.findall(r"Symbol table '([^']+)' contains (\d+) entries:", text), [('.symtab', '2234')])
    rows = {}
    for index, value, length, kind, bind, visibility, section, name in tuples:
        rows.setdefault(name, []).append((int(value, 16), int(length, 16 if length.startswith('0x') else 10),
                                         kind, bind, visibility, section))
    for group in case.binding['ranges']:
        for symbol in group['symbols']:
            case.assertEqual(rows[symbol['name']], [(group['start'] | 1, group['bytes'], 'FUNC',
                                                    group['binding'], 'DEFAULT', '1')])
    constructors = [g for g in case.binding['ranges'] if g['category'] == 'constructors']
    case.assertEqual((len(constructors), sum(len(g['symbols']) for g in constructors)), (13, 26))
    case.assertEqual((sum(g['binding'] == 'GLOBAL' for g in constructors),
                      sum(g['binding'] == 'WEAK' for g in constructors)), (4, 9))
    for name, recorded in case.binding['objects_from_raw_symbols'].items():
        row = recorded[0]
        case.assertEqual(rows[name], [(row['value'], row['bytes'], 'OBJECT', 'LOCAL', 'DEFAULT', str(row['section']))])
    abi = json.loads(case.inputs[RAW + '/native_abi_static01/abi.json'])
    case.assertEqual(case.binding['typed_objects_from_accepted_abi'], abi['objects'])
    for token in case.binding['constructor_absent_func_tokens']:
        case.assertEqual([r for r in tuples if r[3] == 'FUNC' and token in r[7]], [])
    case.assertIs(case.binding['initialization']['contents_observed'], False)
    case.assertEqual(case.binding['initialization']['expected_pointer'], 0x08100101)


def check_all_groups(case, reader):
    result, layout, blocks, rows = case.packet()
    elf, debug = (case.support.stream_text(result, index) for index in (2, 3))
    for index, (label, start, end, aliases) in enumerate(case.ranges):
        binding = case.binding['ranges'][index]['binding']
        for name in aliases:
            row = rows[name]
            wrong_binding = 'GLOBAL' if binding != 'GLOBAL' else 'LOCAL'
            variants = ('', row + row, row.replace(binding, wrong_binding),
                        row.replace(f'{start | 1:08x}', f'{start:08x}'),
                        row.replace(f' {end-start} FUNC', f' {end-start+2} FUNC'),
                        row.replace('FUNC', 'OBJECT'), row.replace('DEFAULT 1', 'DEFAULT 2'))
            for bad in variants:
                with case.subTest(label=label, alias=name, variant=bad):
                    case.assertNotEqual(row, bad)
                    value = copy.deepcopy(result)
                    case.support.replace_text(value, 2, elf.replace(row, bad))
                    case.reject(lambda: reader.summarize(value, layout))
        marker = f'SUMOX_ENTRY_{index:02d}\n'
        lines = blocks[index].splitlines(keepends=True)
        incomplete = ''.join(lines[:-2] + lines[-1:])
        for changed in (debug.replace(marker, '', 1), debug.replace(marker, marker + marker, 1),
                        debug.replace(blocks[index], incomplete, 1)):
            with case.subTest(label=label, marker_or_coverage=True):
                case.assertNotEqual(changed, debug)
                value = copy.deepcopy(result)
                case.support.replace_text(value, 3, changed)
                case.reject(lambda: reader.summarize(value, layout))


def check_stale_ordinary_and_const(case):
    inputs = {**case.inputs, CONTRACT: case.contract}
    for target, pin in data()['stale_d205_inputs'].items():
        stale = checked(pin['path'], pin)
        case.assertNotEqual(stale, inputs[target])
        root = case.scratch()
        for name, raw in inputs.items():
            path = root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(stale if name == target else raw)
        execute = mock.Mock(side_effect=AssertionError('Stale private execution'))
        with mock.patch.dict(case.subject.__dict__['__builtins__'], {'exec': execute}):
            case.reject(lambda: case.subject.load_reader(root=root))
            execute.assert_not_called()
    reader = case.loaded()
    owner = reader.StaticEntry('1234567890abcdef1234567890abcdef12345678')
    owner.source_sha256, owner.boot, owner.claimed = data()['source_sha256'], reader.BOOT, True
    owner.git_state = mock.Mock()
    with mock.patch.object(reader, 'pinned', return_value=b'controlled identity'), mock.patch.object(
            owner.compiler.CompileDiagnostic, 'admission', return_value=None):
        for old_path in (RAW + '/native_abi_static01/result.json',
                         'state/analysis/P7_motor_const_compile_raw/native_entry_static01/result.json'):
            case.assertNotEqual(old_path, RAW + '/native_entry_static01/result.json')
            owner.git_state.return_value = ('1234567890abcdef1234567890abcdef12345678', [('??', old_path)])
            case.reject(owner.local)


def ordinary_cases(oracle):
    class OrdinaryBindingContract(oracle.EntryContract):
        def test_ordinary_complete_symbol_binding_all_groups_aliases_constructor_classes_and_initialized_objects(self):
            self.assertEqual((len(self.ranges), sum(len(g[3]) for g in self.ranges),
                              sum(g[2]-g[1] for g in self.ranges)), (64, 77, 10420))
            check_census(self)
            reader = self.loaded()
            backend = types.SimpleNamespace(PREFIX=PREFIX, gdb=guarded_gdb)
            commands = reader.queries(backend)
            self.assertEqual(commands, expected_commands(self.ranges))
            self.assertEqual(len(commands[3][11:]) // 2, 129)
            self.assertEqual(commands[3][-1], 'echo SUMOX_ENTRY_END\\n')
            check_all_groups(self, reader)
            check_stale_ordinary_and_const(self)
    return OrdinaryBindingContract


def load_tests(loader, standard, pattern):
    if not sys.dont_write_bytecode:
        raise RuntimeError('Independent entry tests require Python -B')
    spec = data()
    oracle = historical()
    additions = fixture_module('current').additional_cases(oracle, spec)
    ordinary = ordinary_cases(oracle)
    suite = unittest.TestSuite([standard])
    suite.addTests(oracle.EntryContract(name) for name in spec['base_methods'])
    suite.addTest(oracle.EntryContract(spec['direct_method']))
    suite.addTests(additions(name) for name in spec['current_methods'])
    suite.addTests(ordinary(name) for name in spec['new_methods'])
    if suite.countTestCases() != 27:
        raise AssertionError('Expected19+1+6+1 explicitly selected D210 methods')
    return suite


if __name__ == '__main__':
    unittest.main(verbosity=2)
