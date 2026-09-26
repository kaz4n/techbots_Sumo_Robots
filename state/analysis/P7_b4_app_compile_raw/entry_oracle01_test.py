# Checks the D217 B4 entry binding with accepted D210 oracle data and fresh symbols.
# Proves inherited parser bodies unchanged and focuses new checks on B4 metadata.
# Root freezes source and oracle before running this eight-method host-only suite.
import ast
import base64
import builtins
from contextlib import ExitStack
import copy
import hashlib
import io
import json
import os
from pathlib import Path
import re
import socket
import subprocess
import sys
import types
import unittest
from unittest import mock


ROOT = Path(__file__).absolute().parents[2]
RAW = 'state/analysis/P7_b4_app_compile_raw'
OLD_RAW = 'state/analysis/P7_ordinary_app_static_compile_raw'
SUBJECT = RAW + '/inspect_static_entry.py'
CONTRACT = 'state/analysis/P7_b4_app_entry_contract.md'
BINDING = RAW + '/entry_binding01.json'
OLD_SUBJECT = OLD_RAW + '/inspect_static_entry.py'
OLD_BINDING = OLD_RAW + '/entry_binding01.json'
OLD_FIXTURE = OLD_RAW + '/entry_fixture_derivation01.json'
PARSER = 'state/analysis/P7_app_motor_fault_compile_raw/inspect_static_entry.py'
ABI = RAW + '/inspect_static_abi.py'
OWNER = '/home/arduino/sumox26_codex_build/b4-app-m0-static01'
SCOPE = 'D217_STATIC_FILE_ONLY_ENTRY'
SOURCE = '9044ebbb3cd3b2dbb7aa5984dd5ff23bfff697372f1f29d56693af9ea5eaf31a'
HEAD = '1234567890abcdef1234567890abcdef12345678'
PREFIX = '/home/arduino/.arduino15/packages/zephyr/tools/arm-zephyr-eabi/1.0.1/bin/arm-zephyr-eabi-'
PINNED = {
    CONTRACT: (7264, 'bcc3072ccb1a219c3cf70ab92ce78d6e140fb4b619b2a370fc56d112a6daa543'),
    BINDING: (78168, 'fb2ab19d0cd0337f7d74a9578eee58d2e0029bf8a45ad6851a9ddbf558c79d55'),
    OLD_SUBJECT: (18546, '5bcb6e12424237cb2701d271e2704281dedca76688d786eac1076daf8f9b3e0b'),
    OLD_BINDING: (106946, '36cafffcfebc647b5019b438705fa42a8be94edfb5d8b67deac2508878c6ae89'),
    OLD_FIXTURE: (172635, '40f3d0a6f32a9dd4d9a23d6449f054cba1985a7809486100835d18344eef3a39'),
    PARSER: (10317, 'cb9ee5bbd5ca8a74510185d77e7d880acf1a03f05608a5ea1459e534a287fa34'),
    ABI: (32744, '4b31dfed3508ebd612abd7de31c5d25e5983c57b802fc55946d3996cf259943d'),
    RAW + '/native_abi_static01/result.json':
        (597470, 'ac0f379ad7da6d02d9cce4f1035405f48fd4f9fcf19de4bb7bcec7f31cf8f69a'),
    RAW + '/native_static01/artifacts.json':
        (9484, '0acaa30a4ba01ac5c9ff8c8fddc66c4bec94e033b1194ec63271f12affb6c085'),
}
CHANGED = {'robot_constructor': (1440, 1484), 'robot_result_constructor': (192, 208),
           'transaction_apply_decision': (288, 292), 'gate_apply': (248, 252)}


def identity(raw):
    return {'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}


def checked(path, pin=None):
    raw = (ROOT / path).read_bytes()
    pin = PINNED[path] if pin is None else pin
    expected = pin if type(pin) is dict else {'bytes': pin[0], 'sha256': pin[1]}
    if identity(raw) != {'bytes': expected['bytes'], 'sha256': expected['sha256']}:
        raise AssertionError('Independent D217 input changed: ' + path)
    return raw


def project(raw, steps):
    for step in steps:
        old, new = step['old'].encode('ascii'), step['new'].encode('ascii')
        if identity(raw) != step['before'] or raw.count(old) != step['count']:
            raise AssertionError('Independent projection input/count changed')
        raw = raw.replace(old, new)
        if identity(raw) != step['after']:
            raise AssertionError('Independent projection output changed')
    return raw


def assignment(raw, name):
    nodes = [node for node in ast.parse(raw).body if isinstance(node, ast.Assign)
             and any(isinstance(target, ast.Name) and target.id == name for target in node.targets)]
    if len(nodes) != 1:
        raise AssertionError('Expected one data assignment: ' + name)
    return ast.literal_eval(nodes[0].value)


def functions(raw):
    text = raw.decode('utf-8')
    return {node.name: ast.get_source_segment(text, node).encode('utf-8')
            for node in ast.parse(text).body if isinstance(node, ast.FunctionDef)}


def module(raw, path, name):
    value = types.ModuleType(name)
    value.__file__ = str(ROOT / path)
    value.__dict__['__builtins__'] = dict(vars(builtins))
    exec(compile(raw, value.__file__, 'exec'), value.__dict__)
    return value


def guarded_gdb(path, expressions):
    args = [PREFIX + 'gdb', '-nx', '-nh', '-batch', '-iex', 'set auto-load no', path,
            '-ex', 'set language c++', '-ex', 'set may-call-functions off']
    for expression in expressions:
        args += ['-ex', expression]
    return args


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


def replace_text(result, index, text):
    result['commands'][index]['stdout_base64'] = base64.b64encode(text.encode()).decode('ascii')


def stream_text(result, index):
    return base64.b64decode(result['commands'][index]['stdout_base64'], validate=True).decode()


class B4EntryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not sys.dont_write_bytecode:
            raise RuntimeError('D217 independent oracle requires Python -B')
        cls.inputs = {name: checked(name) for name in PINNED}
        cls.binding = json.loads(cls.inputs[BINDING])
        cls.old_binding = json.loads(cls.inputs[OLD_BINDING])
        old_plan = json.loads(cls.inputs[OLD_FIXTURE])
        original = checked(old_plan['reader_base'], old_plan['inputs'][old_plan['reader_base']])
        ordinary = project(original, old_plan['ordinary_abi_projection_steps'])
        b4_source = cls.inputs[ABI]
        if identity(ordinary) != {'bytes': 12965, 'sha256':
                '7fb42d51a3f42f99c7e7890b4f4c1dc90360c2d84c09d3bbde7ccea4d1138aea'}:
            raise AssertionError('Accepted ordinary reader projection differs')
        for old, new, count in assignment(b4_source, 'METADATA_STEPS'):
            if ordinary.count(old) != count:
                raise AssertionError('Accepted B4 metadata seam differs')
            ordinary = ordinary.replace(old, new)
        for old, new in assignment(b4_source, 'SHAPE_STEPS'):
            if ordinary.count(old) != 1:
                raise AssertionError('Accepted B4 shape seam differs')
            ordinary = ordinary.replace(old, new)
        if identity(ordinary) != {'bytes': 13204, 'sha256':
                '069af034c960acc478b11ec8c516da58121a8adf2d936531309d298d7ca3feba'}:
            raise AssertionError('Accepted B4 reader input differs')
        cls.reader_input = ordinary
        cls.expected_reader = project(ordinary, cls.binding['projection']['reader']['steps'])
        cls.expected_parser = project(cls.inputs[PARSER], cls.binding['projection']['parser']['steps'])
        cls.old_parser = project(cls.inputs[PARSER], cls.old_binding['projection']['parser']['steps'])
        cls.ranges = tuple((group['label'], group['start'], group['end'],
                           tuple(symbol['name'] for symbol in group['symbols']))
                          for group in cls.binding['ranges'])
        cls.bounds = {row['name']: row['value'] for row in cls.binding['initialization']['bounds']}
        cls.raw = (ROOT / SUBJECT).read_bytes()

    def setUp(self):
        for owner, names in ((subprocess, ('run', 'Popen', 'call', 'check_call', 'check_output')),
                             (socket, ('socket', 'create_connection'))):
            for name in names:
                patch = mock.patch.object(owner, name, side_effect=AssertionError('External effect: ' + name))
                patch.start()
                self.addCleanup(patch.stop)
        self.subject = module(self.raw, SUBJECT, '_d217_independent_subject')

    def loaded(self):
        return self.subject.load_reader(root=ROOT)

    def packet(self, hexadecimal=False, wide='f000 f800'):
        # Accepted D210 fixture algorithm, with fresh immutable group/bound data.
        rows, blocks = {}, []
        for index, (label, start, end, aliases) in enumerate(self.ranges):
            bind = self.binding['ranges'][index]['binding']
            length = hex(end - start) if hexadecimal else str(end - start)
            for name in aliases:
                rows[name] = f' 1: {start | 1:08x} {length} FUNC {bind} DEFAULT 1 {name}\n'
            lines = [f'Dump of assembler code from 0x{start:08x} to 0x{end:08x}:\n']
            cursor = start
            if end - start >= 4:
                lines.append(f'0x{cursor:08x} <fixture+0>: {wide} fixture-wide\n')
                cursor += 4
            while cursor < end:
                lines.append(f'0x{cursor:08x} <fixture>: bf00 nop\n')
                cursor += 2
            lines.append('End of assembler dump.\n')
            blocks.append(''.join(lines))
        for name, address in self.bounds.items():
            bind = 'GLOBAL' if name.startswith('__static_thread') else 'LOCAL'
            rows[name] = f' 2: {address:08x} 0 NOTYPE {bind} DEFAULT 2 {name}\n'
        elf = (' Type: EXEC (Executable file)\n' + ''.join(rows.values()) +
               "Hex dump of section '.init_array':\n 0x081131e4 01011008 ....\n")
        debug = ''.join(f'SUMOX_ENTRY_{index:02d}\n' + block for index, block in enumerate(blocks))
        debug += 'SUMOX_ENTRY_END\n'
        records = [{'argv': argv, 'stdout_base64': base64.b64encode(text.encode()).decode('ascii')}
                   for argv, text in zip(expected_commands(self.ranges), ('fixture\n', 'fixture\n', elf, debug))]
        result = {'scope': SCOPE, 'status': 'OBSERVED', 'first_error': None, 'commands': records,
                  'final_checks': [{'path': 'board_identity', 'status': 'PASS'}]}
        layout = {'sections': [{'name': '.text', 'address': 0x08100010, 'size': 0x131d4},
                               {'name': '.init_array', 'address': 0x081131e4, 'size': 4}]}
        return result, layout, blocks, rows

    def test_passive_wrapper_and_all_inherited_function_bodies_have_only_declared_metadata_changes(self):
        with ExitStack() as stack:
            for owner, names in ((builtins, ('open',)), (io, ('open',)), (os, ('open',)),
                                 (Path, ('read_bytes', 'read_text', 'open', 'mkdir', 'write_bytes'))):
                for name in names:
                    stack.enter_context(mock.patch.object(owner, name, side_effect=AssertionError('Import I/O')))
            module(self.raw, SUBJECT, '_d217_passive_import')
        old, new = functions(self.inputs[OLD_SUBJECT]), functions(self.raw)
        self.assertEqual(set(new), set(old))
        self.assertEqual(len(old), 12)
        for name, body in old.items():
            expected = body.replace(b'_sumox_d210_entry_', b'_sumox_d217_entry_') if name == 'load_reader' else body
            self.assertEqual(new[name], expected, name)
        old_parser, new_parser = functions(self.old_parser), functions(self.expected_parser)
        self.assertEqual(set(new_parser), set(old_parser))
        for name, body in old_parser.items():
            expected = body
            if name == 'queries':
                expected = expected.replace(b'ordinary-app-static01', b'b4-app-m0-static01')
            if name == 'initializer':
                self.assertEqual(body.count(b'0x081158f0'), 3)
                expected = expected.replace(b'0x081158f0', b'0x081131e4')
            self.assertEqual(new_parser[name], expected, name)
        self.assertEqual(self.subject.project_reader(self.reader_input), self.expected_reader)
        self.assertEqual(self.subject.project_parser(self.inputs[PARSER]), self.expected_parser)
        self.assertEqual(identity(self.expected_reader), {'bytes': 13226, 'sha256':
            '5df04ffc6c532d236006bb67bfa772493d8b2dc165b5523e4777300a04f0bba9'})
        self.assertEqual(identity(self.expected_parser), {'bytes': 14256, 'sha256':
            'dd011caad902b86cc6e47fded3be1695e4a96f84581e6a654acf38a2c96a1bfc'})
        self.assertEqual(assignment(self.expected_parser, 'RANGES'), self.ranges)
        self.assertEqual(assignment(self.expected_parser, 'BOUNDS'), self.bounds)
        self.assertEqual([row['count'] for row in self.binding['projection']['reader']['steps']],
                         [1, 1, 1, 2, 1, 1, 1, 1, 2])
        self.assertEqual([row['count'] for row in self.binding['projection']['parser']['steps']], [1] * 9)

    def test_complete_fresh_symbol_census_preserves_64groups_77aliases_and_exact_four_size_changes(self):
        result = json.loads(self.inputs[RAW + '/native_abi_static01/result.json'])
        raw = base64.b64decode(result['commands'][2]['stdout_base64'], validate=True)
        self.assertEqual(identity(raw), {'bytes': 141182, 'sha256':
            'd0a1d7441c1113d81217aa49239284ce86e44e0329d8ac1b15df34d80e870513'})
        elf = raw.decode('ascii')
        rows = re.findall(r'^[ \t]*(\d+):[ \t]+([0-9a-fA-F]+)[ \t]+(0x[0-9a-fA-F]+|\d+)'
                          r'[ \t]+(\S+)[ \t]+(\S+)[ \t]+(\S+)[ \t]+(\S+)(?:[ \t]+(.*?))?[ \t]*$', elf, re.M)
        self.assertEqual([int(row[0]) for row in rows], list(range(2037)))
        self.assertEqual(re.findall(r"Symbol table '([^']+)' contains (\d+) entries:", elf), [('.symtab', '2037')])
        symbols = {}
        for index, value, length, kind, bind, visibility, section, name in rows:
            symbols.setdefault(name, []).append((int(value, 16), int(length, 16 if length.startswith('0x') else 10),
                                                kind, bind, visibility, section))
        old_groups = self.old_binding['ranges']
        self.assertEqual([group['label'] for group in self.binding['ranges']], [group['label'] for group in old_groups])
        changes = {}
        for old, current in zip(old_groups, self.binding['ranges']):
            self.assertEqual([s['name'] for s in current['symbols']], [s['name'] for s in old['symbols']])
            self.assertEqual(current['binding'], old['binding'])
            self.assertEqual(current['end'] - current['start'], current['bytes'])
            if current['bytes'] != old['bytes']:
                changes[current['label']] = (old['bytes'], current['bytes'])
            for symbol in current['symbols']:
                self.assertEqual(symbols[symbol['name']], [(current['start'] | 1, current['bytes'],
                    'FUNC', current['binding'], 'DEFAULT', '1')])
                self.assertIn(symbol['raw_line'] + '\n', elf)
        self.assertEqual(changes, CHANGED)
        self.assertEqual((len(self.ranges), sum(len(group[3]) for group in self.ranges),
                          sum(group[2] - group[1] for group in self.ranges)), (64, 77, 10488))
        for bound in self.binding['initialization']['bounds']:
            self.assertEqual(symbols[bound['name']], [(bound['value'], 0, 'NOTYPE', bound['binding'], 'DEFAULT', '2')])
        self.assertIs(self.binding['initialization']['contents_observed'], False)
        self.assertEqual(self.binding['initialization']['expected_pointer'], 0x08100101)

    def test_current_composition_uses_exact_four_file_queries_129expressions_and_fresh_owner(self):
        reader = self.loaded()
        backend = types.SimpleNamespace(PREFIX=PREFIX, gdb=guarded_gdb)
        commands = reader.queries(backend)
        self.assertEqual(commands, expected_commands(self.ranges))
        self.assertEqual(len(commands), 4)
        self.assertEqual(len(commands[3][11:]) // 2, 129)
        self.assertEqual(commands[3][-1], 'echo SUMOX_ENTRY_END\\n')
        self.assertTrue(all('\n' not in word for command in commands for word in command))
        owner = reader.StaticEntry(HEAD)
        self.assertEqual(reader.SELF, SUBJECT)
        self.assertEqual(reader.OWNER, OWNER)
        self.assertEqual(reader.SOURCE, SOURCE)
        self.assertEqual(owner.output, ROOT / RAW / 'native_entry_static01')
        self.assertEqual(owner.remote, '/home/arduino/sumox26_codex_build/b4-app-m0-entry-static01')
        self.assertFalse(owner.claimed)
        self.assertIn(CONTRACT, reader.HARD_PINS)
        self.assertIn(BINDING, reader.HARD_PINS)
        self.assertEqual(set(self.subject.ORIGINALS), {OLD_SUBJECT, ABI, PARSER, BINDING,
            RAW + '/native_abi_static01/local_result.json', RAW + '/native_abi_static01/abi.json',
            RAW + '/native_abi_static01/result.json', RAW + '/native_static01/artifacts.json',
            'state/reviews/P7_b4_app_abi_actual_review.md'})
        self.assertIn(b'D217_STATIC_FILE_ONLY_ENTRY', self.expected_reader)
        self.assertNotIn(b'D215_STATIC_FILE_ONLY_ABI', self.expected_reader)

    def test_positive_complete_b4_packet_preserves_inputs_and_instruction_only_summary(self):
        reader = self.loaded()
        for hexadecimal, wide in ((False, 'f000 f800'), (True, 'f000f800')):
            with self.subTest(hexadecimal=hexadecimal, wide=wide):
                result, layout, blocks, _ = self.packet(hexadecimal, wide)
                before = copy.deepcopy((result, layout))
                answer = reader.summarize(result, layout)
                self.assertEqual(set(answer), {'status', 'initialization', 'disassembly', 'limitation'})
                self.assertEqual(answer['status'], 'STATIC_ENTRY_OBSERVED')
                self.assertEqual(answer['initialization'], {'address': 0x081131e4, 'bytes_hex': '01011008',
                    'pointer': 0x08100101, 'bounds': self.bounds})
                self.assertEqual(len(answer['disassembly']), 64)
                self.assertEqual(sum(row['validated_bytes'] for row in answer['disassembly']), 10488)
                for observed, expected, block in zip(answer['disassembly'], self.ranges, blocks):
                    label, start, end, aliases = expected
                    self.assertEqual(observed, {'name': label, 'start': start, 'end': end, 'symbols': aliases,
                        'instruction_rows': 1 + (end - start - 4) // 2 if end - start >= 4 else 1,
                        'validated_bytes': end - start, 'raw_block_sha256': hashlib.sha256(block.encode()).hexdigest()})
                self.assertEqual(answer['limitation'],
                    'File instructions only; semantic review pending, no MCU execution or runtime acceptance')
                self.assertEqual((result, layout), before)

    def test_changed_b4_ranges_refuse_stale_sizes_missing_aliases_and_incomplete_coverage(self):
        reader = self.loaded()
        result, layout, blocks, rows = self.packet()
        elf, debug = stream_text(result, 2), stream_text(result, 3)
        for index, (label, start, end, aliases) in enumerate(self.ranges):
            if label not in CHANGED:
                continue
            for alias in aliases:
                original = rows[alias]
                stale = original.replace(f' {end - start} FUNC', f' {CHANGED[label][0]} FUNC')
                for replacement in (stale, ''):
                    with self.subTest(label=label, alias=alias, symbol=True):
                        changed = copy.deepcopy(result)
                        replace_text(changed, 2, elf.replace(original, replacement, 1))
                        with self.assertRaises(ValueError):
                            reader.summarize(changed, layout)
            lines = blocks[index].splitlines(keepends=True)
            incomplete = ''.join(lines[:-2] + lines[-1:])
            changed = copy.deepcopy(result)
            replace_text(changed, 3, debug.replace(blocks[index], incomplete, 1))
            with self.subTest(label=label, coverage=True), self.assertRaises(ValueError):
                reader.summarize(changed, layout)
        wrong_text = copy.deepcopy(layout)
        wrong_text['sections'][0]['size'] = self.ranges[20][2] - 0x08100010 - 2
        with self.assertRaises(ValueError):
            reader.summarize(result, wrong_text)

    def test_current_initializer_address_six_bounds_and_pointer_are_required(self):
        reader = self.loaded()
        result, layout, _, rows = self.packet()
        elf = stream_text(result, 2)
        for name, address in self.bounds.items():
            with self.subTest(bound=name):
                changed = copy.deepcopy(result)
                bad = rows[name].replace(f'{address:08x}', f'{address + 4:08x}', 1)
                replace_text(changed, 2, elf.replace(rows[name], bad, 1))
                with self.assertRaises(ValueError):
                    reader.summarize(changed, layout)
        for old, new in (('0x081131e4 01011008', '0x081158f0 01011008'),
                         ('0x081131e4 01011008', '0x081131e4 01001008')):
            changed = copy.deepcopy(result)
            replace_text(changed, 2, elf.replace(old, new, 1))
            with self.subTest(initializer=new), self.assertRaises(ValueError):
                reader.summarize(changed, layout)
        wrong_section = copy.deepcopy(layout)
        wrong_section['sections'][1]['address'] = 0x081158f0
        with self.assertRaises(ValueError):
            reader.summarize(result, wrong_section)

    def test_real_current_b4_admission_refuses_ordinary_manifest_artifacts_and_wrong_profile(self):
        reader = self.loaded()
        owner = reader.StaticEntry(HEAD)
        owner.compiler.CompileDiagnostic.admission(owner)
        self.assertEqual(owner.source_sha256, SOURCE)
        self.assertEqual(owner.inputs['schema'], 'b4-app-m0-static-inputs-v1')
        self.assertEqual(owner.inputs_path, ROOT / RAW / 'inputs_static.json')
        owner.build_path, owner.artifacts = OWNER + '/build', OWNER + '/artifacts'
        owner.validate_layout = types.MethodType(owner.compiler.CompileDiagnostic.validate_layout, owner)
        current = self.inputs[RAW + '/native_static01/artifacts.json']
        owner.compiler.CompileDiagnostic.validate_artifact_reply(owner, current.decode())
        stale = reader.StaticEntry(HEAD)
        stale.inputs_path = ROOT / OLD_RAW / 'inputs_static.json'
        with self.assertRaises(ValueError):
            stale.compiler.CompileDiagnostic.admission(stale)
        old_artifacts = (ROOT / OLD_RAW / 'native_static01/artifacts.json').read_text()
        with self.assertRaises(ValueError):
            owner.compiler.CompileDiagnostic.validate_artifact_reply(owner, old_artifacts)
        for field, value in (('motors_allowed', 1), ('flags', self.binding['profile']['flags'].replace(
                '-DSUMOX_B4_STAND=1', '-DSUMOX_B4_STAND=0'))):
            with self.subTest(profile_field=field):
                changed = json.loads(current)
                changed['layout'][field] = value
                with self.assertRaises(ValueError):
                    owner.compiler.CompileDiagnostic.validate_artifact_reply(owner, json.dumps(changed))
        self.assertFalse(owner.claimed)

    def test_stale_ordinary_bound_inputs_refuse_before_any_private_source_execution(self):
        pairs = ((ABI, OLD_RAW + '/inspect_static_abi.py'),
                 (RAW + '/native_abi_static01/abi.json', OLD_RAW + '/native_abi_static01/abi.json'),
                 (RAW + '/native_static01/artifacts.json', OLD_RAW + '/native_static01/artifacts.json'),
                 (BINDING, OLD_BINDING))
        for target, old_path in pairs:
            with self.subTest(target=target):
                stale = (ROOT / old_path).read_bytes()
                self.assertNotEqual(stale, (ROOT / target).read_bytes())
                original = self.subject.pinned
                def stale_input(path, expected, *args, target=target, stale=stale):
                    return stale if Path(path) == ROOT / target else original(path, expected, *args)
                forbidden = mock.Mock(side_effect=AssertionError('Stale private source execution'))
                with mock.patch.object(self.subject, 'pinned', stale_input), mock.patch.dict(
                        self.subject.__dict__['__builtins__'], {'exec': forbidden}):
                    with self.assertRaises(ValueError):
                        self.subject.load_reader(root=ROOT)
                    forbidden.assert_not_called()


if __name__ == '__main__':
    unittest.main(verbosity=2)
