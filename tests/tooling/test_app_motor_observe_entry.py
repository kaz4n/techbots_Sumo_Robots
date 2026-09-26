# Tests the observer entry contract using historical public parser interfaces.
# Synthetic complete ELF/disassembly packets establish host parsing, not MCU behavior.
# Freeze before execution; the independent author has not read the new wrapper.
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
import socket
import subprocess
import sys
import tempfile
import types
import unittest
from unittest import mock

ROOT = Path(__file__).absolute().parents[2]
RAW = 'state/analysis/P7_app_motor_observe_compile_raw'
WRAPPER = RAW + '/inspect_static_entry.py'
ABI02 = RAW + '/inspect_static_abi02.py'
PARSER = 'state/analysis/P7_app_motor_fault_compile_raw/inspect_static_entry.py'
CONTRACT = 'state/analysis/P7_app_motor_observe_entry_contract.md'
CONTRACT_SHA = '437f8cb87b7456f0dfc766e506830e0f5ba23cc5b605de5957ff458b5603caaa'
ORACLE02 = 'tests/tooling/test_app_motor_observe_abi02.py'
ORACLE02_SHA = '9e50373e9c0f9d26ecd1e6f4097aa90bf7f346fa42476183b50ed2d0c1feddc3'
PINS = {
    ABI02: (8219, 'a0a5aef19538059450bcb723b6f74cca4d9b7008454760285e8818540ceca421'),
    PARSER: (10317, 'cb9ee5bbd5ca8a74510185d77e7d880acf1a03f05608a5ea1459e534a287fa34'),
    RAW + '/native_abi_static02/result.json': (893020, 'a5e67635f43b96b813885687fbafe743cfc3ec6a93d089a66453ca574c0676da'),
    RAW + '/native_abi_static02/abi.json': (3704, 'dfc34596b65d3a82e21e28c3acf9fb1535bec2eb3b489d270c593c9fe3eab3a7'),
    RAW + '/native_abi_static02/local_result.json': (275, '3f17b83efc79026b46d519646798f70d9cf898b0c4a0bef2e06e6da4da0e84a7'),
}
READER_SHA = '93729533a1d02e54f6812142aa94cf38e7a93a04d5e03d8a5fc4902386f6a421'
PARSER_SHA = '6a82a9e5381aace9375673678bd763db95f93ad5de6d90d8d26abea2e2852767'
HEAD = '1234567890abcdef1234567890abcdef12345678'
OWNER = '/home/arduino/sumox26_codex_build/app-motor-observe-static01'
SCOPE = '/home/arduino/sumox26_codex_build/app-motor-observe-entry-static01'
REJECT = (ValueError, TypeError, OSError, RuntimeError, SystemExit, KeyError)
ADDRESS_ROWS = (
    ('08103b58', '08103b5c', 2), ('08103bb0', '08103bb4', 2), ('08103c08', '08103c20', 2),
    ('08103c94', '08103cac', 2), ('08103d24', '08103d3c', 2), ('08103d78', '08103d98', 1),
    ('0810c760', '0810c780', 1), ('0810c774', '0810c794', 1), ('08110bfc', '08110c1c', 1),
    ('08110bfe', '08110c1e', 1), ('08110c70', '08110c90', 1), ('08110cd8', '08110cf8', 2),
    ('08110d10', '08110d30', 1), ('08110ed8', '08110ef8', 1), ('08110f64', '08110f84', 1),
    ('0811326c', '0811328c', 1), ('08113290', '081132b0', 1), ('08115bec', '08115c0c', 1),
    ('08115c7c', '08115c9c', 2), ('08115cfc', '08115d1c', 1), ('08115f6c', '08115f8c', 1),
    ('08115f74', '08115f94', 2), ('08115f7c', '08115f9c', 1), ('0811602c', '0811604c', 1),
    ('08116036', '08116056', 1), ('08116044', '08116064', 1), ('08116046', '08116066', 1),
    ('08116048', '08116068', 1), ('08116074', '08116094', 2), ('081160e0', '08116100', 1),
    ('08116218', '08116238', 4), ('0811621c', '0811623c', 1))


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def module(raw, path, name):
    value = types.ModuleType(name); value.__file__ = str(path)
    value.__dict__['__builtins__'] = dict(vars(builtins))
    exec(compile(raw, str(path), 'exec'), value.__dict__)
    return value


def replace_checked(raw, replacements):
    for old, new, count in replacements:
        if raw.count(old) != count: raise AssertionError('Independent count: ' + repr(old))
        raw = raw.replace(old, new)
    return raw


def reader_projection(raw):
    replacements = (
        (b"'/inspect_static_abi02.py'", b"'/inspect_static_entry.py'", 1),
        (b"'native_abi_static02'", b"'native_entry_static01'", 1),
        (b'app-motor-observe-abi-static02', b'app-motor-observe-entry-static01', 1),
        (b'D194_STATIC_FILE_ONLY_ABI02', b'D194_STATIC_FILE_ONLY_ENTRY', 2),
        (b'STATIC_ABI_CHECKED', b'STATIC_ENTRY_CHECKED', 1),
        (b'STATIC_ABI_OBSERVED', b'STATIC_ENTRY_OBSERVED', 2),
        (b"'file-abi'", b"'file-entry'", 1), (b"'abi.json'", b"'entry.json'", 1),
        (b'StaticAbi', b'StaticEntry', 2))
    value = replace_checked(raw, replacements)
    if (len(value), digest(value)) != (16955, READER_SHA): raise AssertionError('Reader projection identity')
    return value


def parser_projection(raw):
    old = b'/home/arduino/sumox26_codex_build/app-motor-fault-static01/build/app_motor_fault.ino'
    new = (OWNER + '/build/app_motor_observe.ino').encode()
    replacements = [(old, new, 1), (b'15app_motor_fault', b'17app_motor_observe', 6)]
    replacements += [(('0x' + old).encode(), ('0x' + new).encode(), count) for old, new, count in ADDRESS_ROWS]
    value = replace_checked(raw, replacements)
    if (len(value), digest(value)) != (10333, PARSER_SHA): raise AssertionError('Parser projection identity')
    return value


def function_sources(raw):
    lines = raw.splitlines(keepends=True)
    return {node.name: b''.join(lines[node.lineno - 1:node.end_lineno])
            for node in ast.parse(raw).body if isinstance(node, ast.FunctionDef)}


class EntryContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not sys.dont_write_bytecode: raise RuntimeError('Entry oracle requires Python -B')
        cls.raw = (ROOT / WRAPPER).read_bytes()
        cls.inputs = {name: (ROOT / name).read_bytes() for name in PINS}
        for name, raw in cls.inputs.items():
            if (len(raw), digest(raw)) != PINS[name]: raise AssertionError('Fixed input changed: ' + name)
        cls.contract = (ROOT / CONTRACT).read_bytes()
        if digest(cls.contract) != CONTRACT_SHA: raise AssertionError('Entry contract changed')
        raw = (ROOT / ORACLE02).read_bytes()
        if digest(raw) != ORACLE02_SHA: raise AssertionError('Historical ABI02 oracle changed')
        cls.abi02_helpers = module(raw, ROOT / ORACLE02, '_entry_checked_abi02_helpers')
        old_oracle = (ROOT / cls.abi02_helpers.ORACLE).read_bytes()
        if digest(old_oracle) != cls.abi02_helpers.ORACLE_SHA: raise AssertionError('Historical ABI oracle changed')
        cls.support = module(old_oracle, ROOT / cls.abi02_helpers.ORACLE, '_entry_checked_abi_helpers')
        original_reader = (ROOT / cls.support.ORIGINAL).read_bytes()
        if digest(original_reader) != cls.support.PINS[cls.support.ORIGINAL][1]: raise AssertionError('Old reader changed')
        cls.projected02 = cls.abi02_helpers.expected_projection(cls.support.expected_projection(original_reader))
        old = module(cls.inputs[PARSER], ROOT / PARSER, '_entry_historical_public_parser')
        addresses = {int(before, 16): int(after, 16) for before, after, _ in ADDRESS_ROWS}
        cls.ranges = tuple((label, addresses.get(start, start), addresses.get(end, end),
            tuple(name.replace('15app_motor_fault', '17app_motor_observe') for name in aliases))
            for label, start, end, aliases in old.RANGES)
        cls.bounds = {name: addresses[address] for name, address in old.BOUNDS.items()}

    def setUp(self):
        self.subject = module(self.raw, ROOT / WRAPPER, '_entry_independent_subject')
        for owner, names in ((subprocess, ('run', 'Popen', 'call', 'check_call', 'check_output')),
                             (socket, ('socket', 'create_connection'))):
            for name in names:
                patch = mock.patch.object(owner, name, side_effect=AssertionError('External effect: ' + name))
                patch.start(); self.addCleanup(patch.stop)

    def reject(self, call):
        with self.assertRaises(REJECT): call()

    def scratch(self):
        temp = tempfile.TemporaryDirectory(prefix='sumox-entry-', dir='/dev/shm' if sys.platform == 'linux' else None)
        self.addCleanup(temp.cleanup)
        return Path(temp.name).resolve()

    def loaded(self):
        return self.subject.load_reader(root=ROOT)

    def packet(self, hexadecimal=False, wide='f000 f800'):
        rows, blocks = {}, []
        for label, start, end, aliases in self.ranges:
            binding = 'LOCAL' if label in ('global_initializer', 'candidate_rate', 'candidate_period') else (
                'WEAK' if label in ('init_variant', 'main') else 'GLOBAL')
            size = hex(end - start) if hexadecimal else str(end - start)
            for name in aliases: rows[name] = f' 1: {start | 1:08x} {size} FUNC {binding} DEFAULT 1 {name}\n'
            lines = [f'Dump of assembler code from 0x{start:08x} to 0x{end:08x}:\n']
            cursor = start
            if end - start >= 4:
                lines.append(f'0x{cursor:08x} <fixture+0>: {wide} fixture-wide\n'); cursor += 4
            while cursor < end:
                lines.append(f'0x{cursor:08x} <fixture>: bf00 nop\n'); cursor += 2
            lines.append('End of assembler dump.\n'); blocks.append(''.join(lines))
        for name, address in self.bounds.items():
            binding = 'GLOBAL' if name.startswith('__static_thread') else 'LOCAL'
            rows[name] = f' 2: {address:08x} 0 NOTYPE {binding} DEFAULT 2 {name}\n'
        elf = (' Type: EXEC (Executable file)\n' + ''.join(rows.values()) +
               "Hex dump of section '.init_array':\n 0x08116238 05011008 ....\n")
        debug = ''.join(f'SUMOX_ENTRY_{index:02d}\n' + block for index, block in enumerate(blocks)) + 'SUMOX_ENTRY_END\n'
        records = [self.support.record(['readelf', '--version'], 'fixture\n'),
                   self.support.record(['gdb', '--version'], 'fixture\n'),
                   self.support.record(['readelf', '-hSWs', '-x', '.init_array'], elf),
                   self.support.record(['gdb', 'disassemble'], debug)]
        result = dict(scope='D194_STATIC_FILE_ONLY_ENTRY', status='OBSERVED', first_error=None,
                      commands=records, final_checks=[dict(path='board_identity', status='PASS')])
        layout = {'sections': [dict(name='.text', address=0x08100010, size=0x16228),
                               dict(name='.init_array', address=0x08116238, size=4)]}
        return result, layout, blocks, rows

    def executing_owner(self):
        reader = self.loaded(); owner = reader.StaticEntry.__new__(reader.StaticEntry)
        owner.output = self.scratch() / 'exclusive-entry'
        result, layout, _, _ = self.packet()
        owner.packet = {'layout': {'validator_report': layout}}
        owner.commands = [row['argv'] for row in result['commands']]
        owner.remote_pins = {}; owner.inputs = {'files': {}}; owner.local_pins = {}
        owner.program = 'controlled program'; owner.bootstrap = 'controlled bootstrap'
        owner.claimed = False; owner.counter = 0
        owner.base = reader.loaded(reader.LEGACY, reader.HARD_PINS[reader.LEGACY])
        owner.prepare = mock.Mock(return_value={'status': 'STATIC_ENTRY_CHECKED'})
        owner.local = mock.Mock(return_value=None)
        owner.direct = mock.Mock(return_value=(types.SimpleNamespace(stdout=json.dumps(result), stderr=''), None))
        writes = []
        owner.executor = {'write': lambda path, value: writes.append((path.name, copy.deepcopy(value)))}
        return reader, owner, result, writes

    def test_passive_import_and_exact_bootstrap_source(self):
        with ExitStack() as stack:
            for owner, names in ((Path, ('open', 'read_bytes', 'read_text', 'write_bytes', 'write_text', 'mkdir')),
                                 (builtins, ('open',)), (io, ('open',)), (os, ('open',))):
                for name in names: stack.enter_context(mock.patch.object(owner, name, side_effect=AssertionError('Import I/O')))
            value = module(self.raw, ROOT / WRAPPER, '_entry_passive_import')
        for name in ('project_reader', 'project_parser', 'load_reader', 'main'): self.assertTrue(callable(getattr(value, name)))
        old, new = function_sources(self.inputs[ABI02]), function_sources(self.raw)
        for name in ('require', '_stamp', '_plain_chain', '_read_handle', 'pinned'):
            self.assertEqual(new[name], old[name], name)

    def test_both_projectors_produce_exact_contract_bytes_without_io(self):
        pairs = (('project_reader', self.projected02, reader_projection(self.projected02)),
                 ('project_parser', self.inputs[PARSER], parser_projection(self.inputs[PARSER])))
        self.subject.__dict__['__builtins__']['exec'] = mock.Mock(side_effect=AssertionError('Projector executed'))
        with mock.patch.object(Path, 'read_bytes', side_effect=AssertionError('Projector read')), \
                mock.patch.object(os, 'open', side_effect=AssertionError('Projector opened')):
            for name, raw, expected in pairs:
                actual = getattr(self.subject, name)(raw)
                self.assertIs(type(actual), bytes); self.assertEqual(actual, expected)

    def test_projectors_reject_types_lengths_hashes_counts_and_newlines(self):
        for name, raw in (('project_reader', self.projected02), ('project_parser', self.inputs[PARSER])):
            bad = (None, True, raw.decode(), bytearray(raw), memoryview(raw), b'', raw[:-1], raw + b'\n',
                   b'x' + raw[1:], raw.replace(b'\n', b'\r\n'), raw + b'\n# 0x08116218',
                   raw.replace(b'StaticAbi', b'Changed', 1))
            for value in bad:
                if type(value) is bytes and value == raw: continue
                with self.subTest(projector=name, kind=type(value).__name__):
                    self.reject(lambda: getattr(self.subject, name)(value))

    def test_invalid_cli_or_missing_B_refuses_before_input_loading(self):
        bad = (None, True, '', [], ('--execute', '--reviewed-head', HEAD), ['--help'],
               ['--execute', '--reviewed-head', HEAD.upper()], ['--execute', '--reviewed-head', 1],
               ['--execute', '--reviewed-head', HEAD + '0'], ['--reviewed-head', HEAD, '--execute'],
               ['--execute', '--reviewed-head', HEAD, '--owner', 'old'])
        with mock.patch.object(self.subject, 'load_reader', side_effect=AssertionError('Invalid CLI loaded')):
            for value in bad: self.reject(lambda: self.subject.main(value))
            with mock.patch.object(sys, 'dont_write_bytecode', False):
                self.reject(lambda: self.subject.main(['--check-only', '--reviewed-head', HEAD]))

    def test_main_delegates_once_and_preserves_result_or_primary_exception(self):
        for action in ('--check-only', '--execute'):
            args = [action, '--reviewed-head', HEAD]; private = types.SimpleNamespace(main=mock.Mock(return_value=17))
            with mock.patch.object(self.subject, 'load_reader', return_value=private) as loader:
                self.assertEqual(self.subject.main(args), 17)
                loader.assert_called_once_with(root=self.subject.ROOT); private.main.assert_called_once_with(args)
        error = RuntimeError('delegated original failure'); private.main.side_effect = error
        with mock.patch.object(self.subject, 'load_reader', return_value=private):
            with self.assertRaises(RuntimeError) as caught: self.subject.main(args)
            self.assertIs(caught.exception, error)

    def test_all_six_inputs_are_verified_before_private_execution(self):
        inputs = {**self.inputs, CONTRACT: self.contract}
        for failed in inputs:
            root = self.scratch()
            for name, raw in inputs.items():
                path = root / name; path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes(raw)
            (root / failed).write_bytes(inputs[failed] + b'\n')
            self.subject.__dict__['__builtins__']['exec'] = mock.Mock(side_effect=AssertionError('Unpinned private execution'))
            self.reject(lambda: self.subject.load_reader(root=root))
            self.subject.__dict__['__builtins__']['exec'].assert_not_called()

    def test_original_first_composition_and_no_historical_entry_load_or_main(self):
        events = []; execute = builtins.exec; supplementary = self.subject.project_reader
        def observed_exec(code, namespace, *args):
            value = execute(code, namespace, *args)
            if namespace.get('__file__') == str(ROOT / ABI02):
                original = namespace['project_reader']
                def previous(raw): events.append('abi02'); return original(raw)
                namespace['project_reader'] = previous
            if namespace.get('__file__') == str(ROOT / PARSER):
                namespace['load'] = mock.Mock(side_effect=AssertionError('Historical entry load called'))
                namespace['main'] = mock.Mock(side_effect=AssertionError('Historical entry main called'))
            return value
        def current(raw):
            events.append('entry'); self.assertEqual(raw, self.projected02); return supplementary(raw)
        self.subject.__dict__['__builtins__']['exec'] = observed_exec
        with mock.patch.object(self.subject, 'project_reader', current): reader = self.loaded()
        self.assertEqual(events, ['abi02', 'entry'])
        result, layout, _, _ = self.packet()
        self.assertEqual(reader.summarize(result, layout)['status'], 'STATIC_ENTRY_OBSERVED')

    def test_private_direct_entry_functions_pins_and_fresh_owner(self):
        abi = module(self.inputs[ABI02], ROOT / ABI02, '_entry_prior_abi_fixture').load_reader(root=ROOT)
        prior = dict(abi.HARD_PINS); registered = dict(sys.modules)
        reader, other = self.loaded(), self.loaded()
        self.assertIsNot(reader, other); self.assertNotIn(reader, sys.modules.values())
        for name, value in registered.items(): self.assertIs(sys.modules[name], value)
        for name, value in prior.items(): self.assertEqual(reader.HARD_PINS[name], value)
        for name, (_, value) in PINS.items(): self.assertEqual(reader.HARD_PINS[name], value)
        self.assertEqual(reader.HARD_PINS[CONTRACT], CONTRACT_SHA); self.assertEqual(abi.HARD_PINS, prior)
        self.assertIs(reader.queries.__globals__, reader.summarize.__globals__)
        self.assertIsNot(reader.queries.__globals__, reader.__dict__)
        self.assertEqual(reader.queries.__globals__['__file__'], str(ROOT / PARSER))
        owner = reader.StaticEntry(HEAD)
        self.assertEqual(reader.SELF, WRAPPER); self.assertEqual(reader.OWNER, OWNER)
        self.assertEqual(owner.output, ROOT / RAW / 'native_entry_static01'); self.assertEqual(owner.remote, SCOPE)
        self.assertEqual(owner.local_pins[WRAPPER], digest(self.raw))

    def test_exact_four_file_queries_and_all_twenty_seven_ranges(self):
        reader = self.loaded(); captured = []
        backend = types.SimpleNamespace(PREFIX='/fixed/tool-',
            gdb=lambda path, expressions: captured.append((path, expressions)) or ['gdb', path, *expressions])
        commands = reader.queries(backend)
        self.assertEqual(commands[:3], [['/fixed/tool-readelf', '--version'], ['/fixed/tool-gdb', '--version'],
            ['/fixed/tool-readelf', '-hSWs', '-x', '.init_array', OWNER + '/build/app_motor_observe.ino.elf']])
        expected = []
        for index, (_, start, end, _) in enumerate(self.ranges):
            expected += [f'echo SUMOX_ENTRY_{index:02d}\\n', f'disassemble /r 0x{start:08x},0x{end:08x}']
        expected += ['echo SUMOX_ENTRY_END\\n']
        self.assertEqual(len(self.ranges), 27); self.assertEqual(len(commands), 4)
        self.assertEqual(captured, [(OWNER + '/build/app_motor_observe.ino_debug.elf', expected)])

    def test_full_synthetic_entry_summary_decimal_hex_and_opcode_widths_preserves_raw(self):
        reader = self.loaded()
        for hexadecimal, wide in ((False, 'f000 f800'), (True, 'f000f800')):
            result, layout, blocks, _ = self.packet(hexadecimal, wide)
            before, old_layout = copy.deepcopy(result), copy.deepcopy(layout)
            answer = reader.summarize(result, layout)
            self.assertEqual(answer['status'], 'STATIC_ENTRY_OBSERVED')
            self.assertEqual(answer['initialization'], dict(address=0x08116238, bytes_hex='05011008',
                pointer=0x08100105, bounds=self.bounds))
            self.assertEqual(len(answer['disassembly']), 27)
            for row, bounds, block in zip(answer['disassembly'], self.ranges, blocks):
                label, start, end, aliases = bounds
                self.assertEqual(row, dict(name=label, start=start, end=end, symbols=aliases,
                    instruction_rows=(end-start)//2 - int(end-start >= 4), validated_bytes=end-start,
                    raw_block_sha256=digest(block.encode())))
            self.assertIn('semantic review pending', answer['limitation'])
            self.assertNotIn('polls_alignment_type', answer); self.assertNotIn('readelf_size_projection', answer)
            self.assertEqual(result, before); self.assertEqual(layout, old_layout)

    def test_symbol_address_size_type_binding_section_and_Thumb_failures(self):
        reader = self.loaded(); result, layout, _, rows = self.packet(); original = self.support.stream_text(result, 2)
        row = rows['entry_point']
        bad_rows = [row.replace('08100011', '08100010'), row.replace(' 184 FUNC', ' 186 FUNC'),
                    row.replace('FUNC', 'NOTYPE'), row.replace('GLOBAL', 'LOCAL'), row.replace('DEFAULT 1', 'DEFAULT 2')]
        for bad in bad_rows:
            self.assertNotEqual(row, bad)
            value = copy.deepcopy(result); self.support.replace_text(value, 2, original.replace(row, bad))
            self.reject(lambda: reader.summarize(value, layout))
        value = copy.deepcopy(result); self.support.replace_text(value, 2, original.replace('EXEC (Executable file)', 'DYN (Shared object file)'))
        self.reject(lambda: reader.summarize(value, layout))
        short = copy.deepcopy(layout); short['sections'][0]['size'] = 1
        self.reject(lambda: reader.summarize(result, short))

    def test_missing_duplicate_constructor_aliases_and_initialization_bound_tuples_refuse(self):
        reader = self.loaded(); result, layout, _, rows = self.packet(); original = self.support.stream_text(result, 2)
        aliases = [name for label, _, _, names in self.ranges if label in ('runner_constructor', 'trace_constructor') for name in names]
        self.assertEqual(len(aliases), 4)
        for name in ('setup', *aliases, *self.bounds):
            for changed in (original.replace(rows[name], ''), original + rows[name]):
                value = copy.deepcopy(result); self.support.replace_text(value, 2, changed)
                self.reject(lambda: reader.summarize(value, layout))
        name = '__init_array_start'
        for bad in (rows[name].replace('LOCAL', 'GLOBAL'), rows[name].replace('08116238', '0811623c')):
            value = copy.deepcopy(result); self.support.replace_text(value, 2, original.replace(rows[name], bad))
            self.reject(lambda: reader.summarize(value, layout))

    def test_initializer_section_span_dump_and_little_endian_pointer_are_required(self):
        reader = self.loaded(); result, layout, _, _ = self.packet(); original = self.support.stream_text(result, 2)
        for sections in ([layout['sections'][0]], layout['sections'] + [layout['sections'][1]],
                         [layout['sections'][0], dict(name='.init_array', address=0x08116238, size=8)],
                         [layout['sections'][0], dict(name='.init_array', address=0x0811623c, size=4)]):
            self.reject(lambda: reader.summarize(result, {'sections': sections}))
        marker = "Hex dump of section '.init_array':"
        for changed in (original.replace(marker, 'missing dump'), original + marker,
                        original.replace('0x08116238 05011008', '0x0811623c 05011008'),
                        original.replace('05011008', '08100105'), original.replace('05011008', '04011008'),
                        original + ' 0x0811623c 00000000 ....\n'):
            value = copy.deepcopy(result); self.support.replace_text(value, 2, changed)
            self.reject(lambda: reader.summarize(value, layout))

    def test_markers_require_exact_unique_order_and_final_marker(self):
        reader = self.loaded(); result, layout, _, _ = self.packet(); original = self.support.stream_text(result, 3)
        for changed in (original.replace('SUMOX_ENTRY_00\n', ''), original + 'SUMOX_ENTRY_00\n',
                        original.replace('SUMOX_ENTRY_00', 'SUMOX_ENTRY_01', 1),
                        original.replace('SUMOX_ENTRY_END\n', ''), original + 'SUMOX_ENTRY_27\n',
                        original.replace('SUMOX_ENTRY_00', 'SWAP').replace('SUMOX_ENTRY_01', 'SUMOX_ENTRY_00').replace('SWAP', 'SUMOX_ENTRY_01')):
            value = copy.deepcopy(result); self.support.replace_text(value, 3, changed)
            self.reject(lambda: reader.summarize(value, layout))

    def test_disassembly_headers_end_markers_instruction_format_gaps_overlap_and_coverage(self):
        reader = self.loaded(); result, layout, blocks, _ = self.packet(); original = self.support.stream_text(result, 3)
        block = blocks[0]; lines = block.splitlines(keepends=True)
        bad = [block.replace('0x081000c8:', '0x081000ca:'), block + lines[0],
               block.replace('End of assembler dump.\n', ''), block + 'End of assembler dump.\n',
               block.replace('f000 f800 fixture-wide', 'f00 fixture-wide'),
               block.replace('f000 f800 fixture-wide', 'zzzz fixture-wide'),
               block.replace('0x08100010 <fixture+0>', '0x08100012 <fixture+0>'),
               ''.join(lines[:2] + lines[3:]), ''.join(lines[:2] + [lines[1]] + lines[2:]),
               ''.join(lines[:-2] + lines[-1:])]
        for changed_block in bad:
            self.assertNotEqual(changed_block, block)
            value = copy.deepcopy(result); self.support.replace_text(value, 3, original.replace(block, changed_block, 1))
            self.reject(lambda: reader.summarize(value, layout))

    def test_real_prepare_composes_only_entry_commands_without_claiming(self):
        reader = self.loaded(); owner = reader.StaticEntry(HEAD)
        owner.compiler.CompileDiagnostic.admission(owner)
        owner.local = mock.Mock(return_value=None); owner.output = self.scratch() / 'exclusive-entry'
        with mock.patch.object(reader.shutil, 'disk_usage', return_value=types.SimpleNamespace(free=268435456)):
            value = owner.prepare()
        self.assertEqual(value['status'], 'STATIC_ENTRY_CHECKED'); self.assertEqual(value['file_commands'], 4)
        self.assertLessEqual(value['command_units'], 30000); self.assertEqual(len(owner.remote_pins), 12)
        self.assertEqual(owner.build_path, OWNER + '/build'); self.assertEqual(owner.remote, SCOPE)
        self.assertIn('D194_STATIC_FILE_ONLY_ENTRY', owner.program)
        self.assertIn('-nx', owner.commands[3]); self.assertIn('-nh', owner.commands[3])
        self.assertIn('set auto-load no', owner.commands[3]); self.assertIn('set may-call-functions off', owner.commands[3])
        self.assertFalse(owner.output.exists()); self.assertFalse(owner.claimed)

    def test_execute_retains_raw_entry_summary_labels_and_local_closure(self):
        _, owner, result, writes = self.executing_owner(); before = copy.deepcopy(result)
        closure = owner.execute()
        self.assertEqual([name for name, _ in writes], ['inputs.json', 'result.json', 'entry.json', 'local_result.json'])
        self.assertEqual(writes[1][1], before); self.assertEqual(result, before)
        self.assertEqual(writes[2][1]['status'], 'STATIC_ENTRY_OBSERVED'); self.assertEqual(len(writes[2][1]['disassembly']), 27)
        self.assertEqual(closure['status'], 'STATIC_ENTRY_OBSERVED')
        owner.direct.assert_called_once_with(owner.bootstrap, 'file-entry', 400); owner.local.assert_called_once_with()

    def test_scope_stream_and_parser_failures_retain_raw_and_attempt_local_closure(self):
        for reason in ('scope', 'stderr', 'parser'):
            _, owner, result, writes = self.executing_owner()
            if reason == 'scope': result['scope'] = 'D194_STATIC_FILE_ONLY_ABI02'
            elif reason == 'stderr': result['commands'][3].update(stderr_bytes=1, stderr_base64='eA==')
            else: self.support.replace_text(result, 3, self.support.stream_text(result, 3).replace('SUMOX_ENTRY_END\n', ''))
            owner.direct.return_value = (types.SimpleNamespace(stdout=json.dumps(result), stderr=''), None)
            self.reject(owner.execute)
            self.assertEqual(writes[1][1], result); self.assertNotIn('entry.json', [name for name, _ in writes])
            self.assertEqual(writes[-1][1]['status'], 'FAILED'); owner.local.assert_called_once_with()

    def test_consumed_owner_refusal_and_primary_failure_survives_closure_errors(self):
        _, owner, _, writes = self.executing_owner(); owner.output.mkdir()
        self.reject(owner.execute); owner.direct.assert_not_called(); self.assertFalse(writes)
        _, owner, _, writes = self.executing_owner(); primary = RuntimeError('child failure'); close = OSError('write failure')
        owner.direct.side_effect = primary; owner.local.side_effect = ValueError('local failure')
        def write(path, value):
            writes.append((path.name, copy.deepcopy(value)))
            if path.name == 'local_result.json': raise close
        owner.executor['write'] = write
        with self.assertRaises(RuntimeError) as caught: owner.execute()
        self.assertIs(caught.exception, primary); self.assertIs(primary.__cause__, close)
        self.assertEqual(primary.local_closure['first_error']['message'], str(primary))
        self.assertEqual(primary.local_closure['final_checks'][0]['status'], 'FAILED')


if __name__ == '__main__':
    unittest.main(verbosity=2)
