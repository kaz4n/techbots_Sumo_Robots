# Checks the D215 B4 ABI extension against the independent 313-expression plan.
# Reuses accepted D209 fixture data and unchanged guard identities, not new implementation.
# Root runs this frozen focused oracle only after separate source and test seals.
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
SUBJECT = RAW + '/inspect_static_abi.py'
OLD_TEST = 'tests/tooling/test_ordinary_app_abi.py'
OLD_SUBJECT = 'state/analysis/P7_ordinary_app_static_compile_raw/inspect_static_abi.py'
OLD_PINS = {
    OLD_TEST: (44414, '0a88018a27c011965ea7d36b43163c22a595267ce6d1a22fcc14ce01b4ce4ef5'),
    OLD_SUBJECT: (44449, 'f816a52366d7031f860d5cdd93e0715905df4b675a24e89d8dbb1d2b63eda97d'),
}
OWNER = '/home/arduino/sumox26_codex_build/b4-app-m0-static01'
HEAD = '1234567890abcdef1234567890abcdef12345678'
SOURCE = '9044ebbb3cd3b2dbb7aa5984dd5ff23bfff697372f1f29d56693af9ea5eaf31a'
PREFIX = '/home/arduino/.arduino15/packages/zephyr/tools/arm-zephyr-eabi/1.0.1/bin/arm-zephyr-eabi-'
FLAGS = ('-DMATCH=0 -DMOTORS_ALLOWED=0 -DSUMOX_B4_STAND=1 '
         '-DSUMOX_P3_DRIVE_TEST=0 -DSUMOX_P3_TURN_TRIAL=0 -DSUMOX_P3_STOP_TRIAL=0 '
         '-DSUMOX_P4_REACTIVE=0 -DSUMOX_TIMING_EVIDENCE=0 '
         '-DSUMOX_P5_ABORT_TIMING=0 -DSUMOX_MOTOR_FAULT_PROBE=0')
ADDED_TYPES = ('stand_sequence::Report', 'recorder::AttemptRecorder',
               'recorder::AttemptSummary', 'recorder::FrameBuffer',
               'logframe::EventBuffer', 'logframe::TickStatistics',
               'logframe::FrameBytes', 'logframe::EventBytes')
SUBFIELDS = {'robot.stand': 'stand_sequence::Report', 'robot.stand_stopping': 'bool'}
MEMBERS = {
    'FrameBuffer.payloads_': ('sizeof(((recorder::FrameBuffer*)0)->payloads_)', 125025),
    'FrameBuffer.statuses_': ('sizeof(((recorder::FrameBuffer*)0)->statuses_)', 1251),
    'EventBuffer.events_': ('sizeof(((logframe::EventBuffer*)0)->events_)', 32768),
    'FrameBuffer.first_': ('sizeof(((recorder::FrameBuffer*)0)->first_)', 4),
    'FrameBuffer.size_': ('sizeof(((recorder::FrameBuffer*)0)->size_)', 4),
    'EventBuffer.size_': ('sizeof(((logframe::EventBuffer*)0)->size_)', 4),
    'stand_sequence::Phase': ('sizeof(stand_sequence::Phase)', 1),
    'stand_sequence::Reason': ('sizeof(stand_sequence::Reason)', 1),
    'recorder::AttemptPhase': ('sizeof(recorder::AttemptPhase)', 1),
    'logframe::PackStatus': ('sizeof(logframe::PackStatus)', 1),
    'core::Mode': ('sizeof(core::Mode)', 1),
}
ADDED_ENUMS = {
    'stand_sequence::Phase': {'NOT_STARTED': 0, 'DRIVE': 1, 'BRAKE': 2, 'COAST': 3,
                              'COMPLETE': 4, 'INTERRUPTED': 5, 'FAULT': 6},
    'stand_sequence::Reason': {'NONE': 0, 'STOP': 1, 'EDGE': 2, 'CLOCK_ORDER': 3, 'CLOCK_GAP': 4},
    'recorder::AttemptPhase': {'EMPTY': 0, 'RECORDING': 1, 'DRAINING': 2, 'SEALED': 3, 'INTERRUPTED': 4},
    'logframe::PackStatus': {'OK': 0, 'CLAMPED': 1, 'INVALID': 2},
    'core::Mode': {'SIDESTEP_R': 1, 'SIDESTEP_L': 2, 'DIRECT': 3, 'ARC_R': 4, 'ARC_L': 5, 'WAIT': 6},
}
SIZES = {'stand_sequence::Report': 20, 'recorder::AttemptRecorder': 160000,
         'recorder::AttemptSummary': 128, 'recorder::FrameBuffer': 126320,
         'logframe::EventBuffer': 32784, 'logframe::TickStatistics': 24,
         'logframe::FrameBytes': 25, 'logframe::EventBytes': 8}
ALIGNS = dict.fromkeys(ADDED_TYPES, 4)
ALIGNS.update({'recorder::AttemptRecorder': 8, 'recorder::AttemptSummary': 8,
               'logframe::TickStatistics': 8, 'logframe::FrameBytes': 1,
               'logframe::EventBytes': 1})
CAPACITIES = dict(frame_bytes=25, frames=5001, frame_status_bytes=1251,
                  event_bytes=8, events=4096, index_bytes=4)
PROFILE = dict(project='app.ino', fqbn='arduino:zephyr:unoq:link_mode=static',
               flags=FLAGS, motors_allowed=0, source_sha256=SOURCE)
GUARDS = ('require', '_stamp', '_plain_chain', '_read_handle', 'pinned', '_verify', 'main')


def checked_old(name):
    raw = (ROOT / name).read_bytes()
    if (len(raw), hashlib.sha256(raw).hexdigest()) != OLD_PINS[name]:
        raise AssertionError('Accepted oracle input changed: ' + name)
    return raw


def module(raw, path, name):
    value = types.ModuleType(name)
    value.__file__ = str(path)
    value.__dict__['__builtins__'] = dict(vars(builtins))
    exec(compile(raw, str(path), 'exec'), value.__dict__)
    return value


def function_spans(raw):
    lines = raw.splitlines(keepends=True)
    return {node.name: b''.join(lines[node.lineno - 1:node.end_lineno])
            for node in ast.parse(raw).body if isinstance(node, ast.FunctionDef)}


def added_expressions():
    answer = []
    for name in ADDED_TYPES:
        for label, function in (('SIZE', 'sizeof'), ('ALIGN', 'alignof')):
            answer += ['echo SUMOX_' + label + ' ' + name + '\\n', 'p/d ' + function + '(' + name + ')']
        answer += ['echo SUMOX_LAYOUT ' + name + '\\n', 'ptype /o ' + name]
    answer += ['echo SUMOX_OFFSET transaction_.recorder_\\n',
               'p/d (unsigned long)&((app::Runtime*)0)->transaction_.recorder_']
    for name in SUBFIELDS:
        answer += ['echo SUMOX_SUBOFFSET ' + name + '\\n',
                   'p/d (unsigned long)&((app::TransactionReport*)0)->' + name]
    for name, (expression, unused) in MEMBERS.items():
        answer += ['echo SUMOX_MEMBER_SIZE ' + name + '\\n', 'p/d ' + expression]
    for kind, values in ADDED_ENUMS.items():
        for name in values:
            answer += ['echo SUMOX_ENUM ' + kind + '::' + name + '\\n',
                       'p/d (unsigned int)' + kind + '::' + name]
    return answer


def commands(expressions):
    gdb = [PREFIX + 'gdb', '-nx', '-nh', '-batch', '-iex', 'set auto-load no',
           OWNER + '/build/app.ino_debug.elf', '-ex', 'set language c++',
           '-ex', 'set may-call-functions off']
    for expression in expressions:
        gdb += ['-ex', expression]
    return [[PREFIX + 'readelf', '--version'], [PREFIX + 'gdb', '--version'],
            [PREFIX + 'readelf', '-hSWs', OWNER + '/build/app.ino.elf'], gdb]


def ptype(name, size, body):
    return ('/* offset | size */ type = struct ' + name + ' {\n' + body +
            '\n/* total size (bytes): ' + str(size) + ' */\n}\n')


def fixture_layouts():
    # Independent synthetic offsets include real nested ptype syntax, not target addresses.
    stand = ('/* 0 | 1 */ stand_sequence::Phase phase;\n'
             '/* 1 | 1 */ stand_sequence::Reason reason;\n'
             '/* 2 | 1 */ uint8_t segment;\n/* 4 | 4 */ float duty_l;\n'
             '/* 8 | 4 */ float duty_r;\n/* 12 | 1 */ bool fresh;\n'
             '/* 13 | 1 */ bool phase_changed;')
    report = ('/* 0 | 1 */ app::Phase phase;\n'
              '/* 32 | 400 */ struct fsm::RobotResult {\n'
              '/* 32 | 20 */ struct stand_sequence::Report {\n'
              '/* 32 | 1 */ stand_sequence::Phase phase;\n'
              '/* 36 | 4 */ float duty_l;\n/* 40 | 4 */ float duty_r;\n'
              '/* total size (bytes): 20 */\n} stand;\n'
              '/* 52 | 1 */ bool stand_stopping;\n/* 56 | 8 */ uint64_t token;\n'
              '/* total size (bytes): 400 */\n} robot;\n'
              '/* 432 | 80 */ unsigned char tail[80];')
    robot = ('/* 0 | 20 */ struct stand_sequence::Report {\n' + stand +
             '\n/* total size (bytes): 20 */\n} stand;\n'
             '/* 20 | 1 */ bool stand_stopping;\n/* 24 | 8 */ uint64_t token;')
    result = {
        'app::TransactionReport': ptype('app::TransactionReport', 512, report),
        'fsm::RobotResult': ptype('fsm::RobotResult', 400, robot),
        'stand_sequence::Report': ptype('stand_sequence::Report', 20, stand),
        'recorder::FrameBuffer': ptype('recorder::FrameBuffer', 126320,
            '/* 0 | 125025 */ logframe::FrameBytes payloads_[5001];\n'
            '/* 125025 | 1251 */ uint8_t statuses_[1251];\n'
            '/* 126276 | 4 */ size_t first_;\n/* 126280 | 4 */ size_t size_;\n'
            '/* 126284 | 4 */ uint32_t overwritten_;\n'
            '/* 126288 | 4 */ uint32_t rejected_status_;\n'
            '/* 126292 | 4 */ uint32_t clamped_;\n/* 126296 | 4 */ uint32_t invalid_;'),
        'logframe::EventBuffer': ptype('logframe::EventBuffer', 32784,
            '/* 0 | 32768 */ logframe::EventBytes events_[4096];\n'
            '/* 32768 | 4 */ size_t size_;\n/* 32772 | 4 */ uint32_t rejected_;\n'
            '/* 32776 | 1 */ bool overflowed_;'),
        'recorder::AttemptRecorder': ptype('recorder::AttemptRecorder', 160000,
            '/* 0 | 126320 */ recorder::FrameBuffer frames_;\n'
            '/* 126320 | 32784 */ logframe::EventBuffer events_;\n'
            '/* 159104 | 128 */ recorder::AttemptSummary summary_;\n'
            '/* 159232 | 8 */ uint64_t highest_token_;\n'
            '/* 159240 | 8 */ uint64_t stopping_token_;\n'
            '/* 159248 | 1 */ core::State previous_state_;\n'
            '/* 159249 | 1 */ recorder::AttemptPhase phase_;\n'
            '/* 159250 | 1 */ bool terminal_seen_;'),
        'recorder::AttemptSummary': ptype('recorder::AttemptSummary', 128,
            '/* 0 | 8 */ uint64_t epoch_token;\n/* 8 | 8 */ uint64_t last_frame_token;\n'
            '/* 16 | 4 */ uint32_t release_us;\n/* 20 | 1 */ core::Mode mode;\n'
            '/* 24 | 4 */ uint32_t observed_results;\n'
            '/* 64 | 24 */ logframe::TickStatistics ticks;\n'
            '/* 88 | 1 */ bool upstream_event_overflow;'),
        'logframe::TickStatistics': ptype('logframe::TickStatistics', 24,
            '/* 0 | 8 */ uint64_t ticks;\n/* 8 | 8 */ uint64_t overruns;\n'
            '/* 16 | 4 */ uint32_t max_us;\n/* 20 | 1 */ bool saturated;'),
        'logframe::FrameBytes': ptype('logframe::FrameBytes', 25, '/* 0 | 25 */ uint8_t data[25];'),
        'logframe::EventBytes': ptype('logframe::EventBytes', 8, '/* 0 | 8 */ uint8_t data[8];'),
    }
    return result


def replace_layout(old, result, kind, block):
    text = old.text(result, 3)
    pattern = r'(SUMOX_LAYOUT ' + re.escape(kind) + r'\n).*?(?=^SUMOX_|\Z)'
    changed, count = re.subn(pattern, lambda found: found[1] + block, text, flags=re.M | re.S)
    if count != 1:
        raise AssertionError('Fixture layout marker is not unique')
    old.replace_text(result, 3, changed)


def packet(old, *, shift=0):
    result, layout = old.packet(sizes_override={
        'app::Runtime': 200000, 'app::Transaction': 190000, 'fsm::RobotResult': 400})
    elf = old.text(result, 2).replace(' 4096 OBJECT ', ' 200000 OBJECT ')
    elf = elf.replace(format(old.ADDRESS + 6144, 'x'), format(old.ADDRESS + 210000, 'x'))
    elf = elf.replace('002000 00 WA', '040000 00 WA')
    old.replace_text(result, 2, elf)
    layout['sections'][0]['size'] = 262144
    layout['bss_zero']['end'] = old.ADDRESS + 262144
    for name, block in fixture_layouts().items():
        if name not in ADDED_TYPES:
            replace_layout(old, result, name, block)
    text = old.text(result, 3)
    for name in ADDED_TYPES:
        text += ('SUMOX_SIZE ' + name + '\n$4 = ' + str(SIZES[name]) + '\n'
                 'SUMOX_ALIGN ' + name + '\n$5 = ' + str(ALIGNS[name]) + '\n'
                 'SUMOX_LAYOUT ' + name + '\n' + fixture_layouts()[name])
    text += 'SUMOX_OFFSET transaction_.recorder_\n$6 = ' + str(4096 + shift) + '\n'
    text += 'SUMOX_SUBOFFSET robot.stand\n$7 = 32\n'
    text += 'SUMOX_SUBOFFSET robot.stand_stopping\n$8 = 52\n'
    for name, (unused, value) in MEMBERS.items():
        text += 'SUMOX_MEMBER_SIZE ' + name + '\n$9 = ' + str(value) + '\n'
    for kind, names in ADDED_ENUMS.items():
        for name, value in names.items():
            text += 'SUMOX_ENUM ' + kind + '::' + name + '\n$10 = ' + str(value) + '\n'
    old.replace_text(result, 3, text)
    for record, expected in zip(result['commands'], commands(old.expected_expressions() + added_expressions())):
        record['argv'] = expected
    result['scope'] = 'D215_STATIC_FILE_ONLY_ABI'
    return result, layout


class B4AbiExtension(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not sys.dont_write_bytecode:
            raise AssertionError('Use Python -B; no bytecode artifacts')
        cls.old_raw = checked_old(OLD_SUBJECT)
        cls.old = module(checked_old(OLD_TEST), ROOT / OLD_TEST, '_d215_old_oracle_data')
        # Root's independent execution freeze binds this new source before tests.
        cls.raw = (ROOT / SUBJECT).read_bytes()

    def setUp(self):
        for owner, names in ((subprocess, ('run', 'Popen', 'call', 'check_call', 'check_output')),
                             (socket, ('socket', 'create_connection'))):
            for name in names:
                patch = mock.patch.object(owner, name, side_effect=AssertionError('External operation: ' + name))
                patch.start()
                self.addCleanup(patch.stop)
        self.subject = module(self.raw, ROOT / SUBJECT, '_d215_independent_subject')

    def loaded(self):
        return self.subject.load_reader(root=ROOT)

    def reject(self, reader, result, layout):
        with self.assertRaises(ValueError):
            reader.summarize(result, layout)

    def test_passive_import_and_seven_guard_cli_bodies_remain_exact(self):
        with ExitStack() as stack:
            for owner, names in ((Path, ('read_bytes', 'read_text', 'open', 'write_bytes', 'write_text', 'mkdir')),
                                 (builtins, ('open',)), (io, ('open',)), (os, ('open',))):
                for name in names:
                    stack.enter_context(mock.patch.object(owner, name, side_effect=AssertionError('Import I/O')))
            result = module(self.raw, ROOT / SUBJECT, '_d215_passive_import')
        self.assertTrue(callable(result.load_reader))
        before, after = function_spans(self.old_raw), function_spans(self.raw)
        for name in GUARDS:
            self.assertEqual(after[name], before[name], name)

    def test_exact_313_expressions_keep_185_prefix_and_four_file_commands(self):
        reader = self.loaded()
        expressions = self.old.expected_expressions() + added_expressions()
        self.assertEqual(len(self.old.expected_expressions()), 185)
        self.assertEqual(len(added_expressions()), 128)
        self.assertEqual(len(expressions), 313)
        seen = []
        def gdb(path, selected):
            seen.append((path, selected))
            return commands(selected)[3]
        actual = reader.queries(types.SimpleNamespace(PREFIX=PREFIX, gdb=gdb))
        self.assertEqual(seen, [(OWNER + '/build/app.ino_debug.elf', expressions)])
        self.assertEqual(actual, commands(expressions))
        self.assertFalse(any('\n' in item for item in expressions))
        self.assertFalse(any(word in ' '.join(expressions) for word in ('target ', 'attach ', 'call ', 'dump ', 'config::')))
        self.assertEqual(self.subject.SUBFIELDS, SUBFIELDS)
        self.assertEqual(self.subject.MEMBER_SIZES, MEMBERS)

    def test_wrong_tool_prefix_or_unguarded_gdb_argv_refuses(self):
        reader = self.loaded()
        for backend in (types.SimpleNamespace(PREFIX='/other/', gdb=lambda p, e: commands(e)[3]),
                        types.SimpleNamespace(PREFIX=PREFIX, gdb=lambda p, e: ['gdb', p])):
            with self.subTest(backend=backend), self.assertRaises(ValueError):
                reader.queries(backend)

    def test_complete_b4_schema_profile_capacities_and_separate_nested_subfields(self):
        reader = self.loaded()
        result, layout = packet(self.old)
        answer = reader.summarize(result, layout)
        self.assertEqual(set(answer), {'schema', 'status', 'objects', 'sizes', 'alignments', 'layouts',
                                      'windows', 'enums', 'limitation', 'subfields', 'member_sizes', 'capacities', 'profile'})
        self.assertEqual(answer['schema'], 'b4-app-m0-static-abi-v1')
        self.assertEqual(answer['status'], 'STATIC_ABI_OBSERVED')
        self.assertEqual(answer['profile'], PROFILE)
        self.assertIs(type(answer['profile']['motors_allowed']), int)
        self.assertEqual(answer['capacities'], CAPACITIES)
        self.assertEqual(answer['member_sizes'], {name: value for name, (unused, value) in MEMBERS.items()})
        self.assertEqual(set(answer['sizes']), set(self.old.TYPES) | set(ADDED_TYPES))
        self.assertEqual(set(answer['windows']), set(self.old.WINDOWS) | {'transaction_.recorder_'})
        recorder = answer['windows']['transaction_.recorder_']
        self.assertEqual(recorder, dict(object='runtime', type='recorder::AttemptRecorder',
            offset=4096, address=self.old.ADDRESS + 4096, bytes=160000, alignment=8))
        self.assertEqual(set(answer['subfields']), set(SUBFIELDS))
        for name, kind in SUBFIELDS.items():
            offset = 32 if name == 'robot.stand' else 52
            self.assertEqual(answer['subfields'][name], dict(parent='transaction_.report_', type=kind,
                offset=offset, address=self.old.ADDRESS + 512 + offset,
                bytes=20 if name == 'robot.stand' else 1, alignment=4 if name == 'robot.stand' else 1))
        for name, expected in ADDED_ENUMS.items():
            self.assertEqual(answer['enums'][name], expected)
        for name, expected in fixture_layouts().items():
            self.assertEqual(answer['layouts'][name], expected)
        self.assertIn('MCU', answer['limitation'])

    def test_relocated_recorder_uses_observations_and_summary_is_pure(self):
        reader = self.loaded()
        for shift in (0, 1024):
            result, layout = packet(self.old, shift=shift)
            before, prior = copy.deepcopy(result), copy.deepcopy(layout)
            with ExitStack() as stack:
                for owner, names in ((Path, ('read_bytes', 'read_text', 'open', 'write_bytes', 'write_text', 'mkdir')),
                                     (builtins, ('open',)), (io, ('open',)), (os, ('open',))):
                    for name in names:
                        stack.enter_context(mock.patch.object(owner, name, side_effect=AssertionError('Summary I/O')))
                answer = reader.summarize(result, layout)
            self.assertEqual(answer['windows']['transaction_.recorder_']['address'], self.old.ADDRESS + 4096 + shift)
            self.assertEqual(result, before)
            self.assertEqual(layout, prior)

    def test_every_added_marker_rejects_missing_duplicate_reordered_and_unknown(self):
        reader = self.loaded()
        result, layout = packet(self.old)
        original = self.old.text(result, 3)
        markers = [item[5:-2] for item in added_expressions() if item.startswith('echo ')]
        self.assertEqual(len(markers), 64)
        for marker in markers:
            mutations = (original.replace(marker + '\n', '', 1),
                         original.replace(marker + '\n', marker + '\n' + marker + '\n', 1),
                         original.replace(marker + '\n', 'SUMOX_UNKNOWN extra\n', 1),
                         marker + '\n' + original.replace(marker + '\n', '', 1))
            for number, text in enumerate(mutations):
                with self.subTest(marker=marker, mutation=number):
                    changed = copy.deepcopy(result)
                    self.old.replace_text(changed, 3, text)
                    self.reject(reader, changed, layout)

    def test_new_numeric_answers_reject_negative_fraction_duplicate_and_junk(self):
        reader = self.loaded()
        result, layout = packet(self.old)
        new_markers = {item[5:-2] for item in added_expressions() if item.startswith('echo ') and 'SUMOX_LAYOUT ' not in item}
        self.assertEqual(len(new_markers), 56)
        for marker in new_markers:
            label, name = marker[len('SUMOX_'):].split(' ', 1)
            for value in ('-1', '1.0', '1\n$99 = 1', '1 trailing'):
                with self.subTest(marker=marker, value=value):
                    changed = copy.deepcopy(result)
                    self.old.numeric(changed, label, name, value)
                    self.reject(reader, changed, layout)

    def test_each_added_layout_rejects_empty_unavailable_wrong_type_and_unbalanced(self):
        reader = self.loaded()
        for kind in ADDED_TYPES:
            for body in ('', '<optimized out>\n', 'type = struct wrong::Type {}\n',
                         'type = struct ' + kind + ' {\n'):
                with self.subTest(kind=kind, body=body):
                    result, layout = packet(self.old)
                    replace_layout(self.old, result, kind, body)
                    self.reject(reader, result, layout)

    def test_added_type_sizes_and_alignments_keep_existing_bounds(self):
        reader = self.loaded()
        for kind in ADDED_TYPES:
            for label, value in (('SIZE', 0), ('SIZE', 1048577), ('ALIGN', 0), ('ALIGN', 3), ('ALIGN', 32)):
                with self.subTest(kind=kind, label=label, value=value):
                    result, layout = packet(self.old)
                    self.old.numeric(result, label, kind, value)
                    self.reject(reader, result, layout)

    def test_recorder_window_requires_initialized_owner_containment_alignment_and_nonoverlap(self):
        reader = self.loaded()
        for offset in (4097, 200000 - 160000 + 8, 512, 2048, 2304):
            with self.subTest(offset=offset):
                result, layout = packet(self.old)
                self.old.numeric(result, 'OFFSET', 'transaction_.recorder_', offset)
                self.reject(reader, result, layout)

    def test_each_array_extent_is_exact_and_packed_status_capacity_is_not_rounded_down(self):
        reader = self.loaded()
        for name in tuple(MEMBERS)[:3]:
            for value in (0, MEMBERS[name][1] - 1, MEMBERS[name][1] + 1):
                with self.subTest(name=name, value=value):
                    result, layout = packet(self.old)
                    self.old.numeric(result, 'MEMBER_SIZE', name, value)
                    self.reject(reader, result, layout)

    def test_all_three_indices_require_exact_four_bytes_including_mixed_widths(self):
        reader = self.loaded()
        for name in tuple(MEMBERS)[3:6]:
            for width in (1, 2, 8, 0):
                with self.subTest(name=name, width=width):
                    result, layout = packet(self.old)
                    self.old.numeric(result, 'MEMBER_SIZE', name, width)
                    self.reject(reader, result, layout)
        result, layout = packet(self.old)
        for name in tuple(MEMBERS)[3:6]:
            self.old.numeric(result, 'MEMBER_SIZE', name, 8)
        self.reject(reader, result, layout)

    def test_five_enum_widths_require_one_byte(self):
        reader = self.loaded()
        for name in tuple(MEMBERS)[6:]:
            for width in (0, 2, 4):
                with self.subTest(name=name, width=width):
                    result, layout = packet(self.old)
                    self.old.numeric(result, 'MEMBER_SIZE', name, width)
                    self.reject(reader, result, layout)

    def test_each_of_26_enum_members_must_equal_its_declared_value(self):
        reader = self.loaded()
        self.assertEqual(sum(map(len, ADDED_ENUMS.values())), 26)
        for kind, names in ADDED_ENUMS.items():
            for name, value in names.items():
                with self.subTest(kind=kind, name=name):
                    result, layout = packet(self.old)
                    self.old.numeric(result, 'ENUM', kind + '::' + name, value + 1)
                    self.reject(reader, result, layout)

    def test_wire_element_sizes_are_exact(self):
        reader = self.loaded()
        for kind, width in (('logframe::FrameBytes', 25), ('logframe::EventBytes', 8)):
            for changed in (width - 1, width + 1):
                with self.subTest(kind=kind, changed=changed):
                    result, layout = packet(self.old)
                    self.old.numeric(result, 'SIZE', kind, changed)
                    self.reject(reader, result, layout)

    def test_resident_arrays_and_indices_must_fit_their_observed_parent(self):
        reader = self.loaded()
        for kind, size in (('recorder::FrameBuffer', 125025 + 1251 + 4 + 4 - 1),
                           ('logframe::EventBuffer', 32768 + 4 - 1),
                           ('recorder::AttemptRecorder', 126320 + 32784 + 128 - 1),
                           ('recorder::AttemptSummary', 23)):
            with self.subTest(kind=kind):
                result, layout = packet(self.old)
                self.old.numeric(result, 'SIZE', kind, size)
                self.reject(reader, result, layout)

    def test_robot_container_requires_unique_direct_member_and_matching_type_name(self):
        reader = self.loaded()
        original = fixture_layouts()['app::TransactionReport']
        variants = (
            original.replace('struct fsm::RobotResult', 'struct wrong::RobotResult'),
            original.replace('} robot;', '} another_member;'),
            original.replace('/* 32 | 400 */', '/* 32 | 392 */'),
            original.replace('/* 32 | 400 */', '/* 120 | 400 */'),
            original.replace('/* 32 | 400 */', '/* 33 | 400 */'),
            original.replace('/* 432 | 80 */ unsigned char tail[80];',
                '/* 32 | 400 */ struct fsm::RobotResult {\n/* 32 | 1 */ bool nested;\n} robot;'),
            ptype('app::TransactionReport', 512,
                '/* 0 | 480 */ struct wrapper {\n' + original.split('{\n', 1)[1].rsplit('}', 1)[0] + '\n} wrapper_;'),
        )
        for number, block in enumerate(variants):
            with self.subTest(number=number):
                result, layout = packet(self.old)
                replace_layout(self.old, result, 'app::TransactionReport', block)
                self.reject(reader, result, layout)

    def test_stand_subfields_require_robot_containment_alignment_and_each_other_nonoverlap(self):
        reader = self.loaded()
        for name, offset in (('robot.stand', 0), ('robot.stand', 33), ('robot.stand', 416),
                             ('robot.stand_stopping', 0), ('robot.stand_stopping', 432),
                             ('robot.stand_stopping', 40)):
            with self.subTest(name=name, offset=offset):
                result, layout = packet(self.old)
                self.old.numeric(result, 'SUBOFFSET', name, offset)
                self.reject(reader, result, layout)

    def test_ordinary_185_expression_packet_is_not_b4_abi_evidence(self):
        reader = self.loaded()
        result, layout = self.old.packet()
        self.reject(reader, result, layout)

    def test_real_b4_source_and_artifact_admission_refuses_ordinary_and_m1_metadata(self):
        reader = self.loaded()
        owner = reader.StaticAbi(HEAD)
        owner.compiler.CompileDiagnostic.admission(owner)
        self.assertEqual(owner.source_sha256, SOURCE)
        self.assertEqual(owner.inputs['schema'], 'b4-app-m0-static-inputs-v1')
        self.assertEqual(owner.inputs_path, ROOT / RAW / 'inputs_static.json')
        owner.build_path, owner.artifacts = OWNER + '/build', OWNER + '/artifacts'
        owner.validate_layout = types.MethodType(owner.compiler.CompileDiagnostic.validate_layout, owner)
        raw = (ROOT / RAW / 'native_static01/artifacts.json').read_bytes()
        owner.compiler.CompileDiagnostic.validate_artifact_reply(owner, raw.decode())
        old = (ROOT / 'state/analysis/P7_ordinary_app_static_compile_raw/native_static01/artifacts.json').read_text()
        with self.assertRaises(ValueError):
            owner.compiler.CompileDiagnostic.validate_artifact_reply(owner, old)
        for value in (1, True, '0'):
            with self.subTest(motors_allowed=value):
                changed = json.loads(raw)
                changed['layout']['motors_allowed'] = value
                with self.assertRaises(ValueError):
                    owner.compiler.CompileDiagnostic.validate_artifact_reply(owner, json.dumps(changed))
        self.assertFalse(owner.claimed)


if __name__ == '__main__':
    unittest.main(verbosity=2)
