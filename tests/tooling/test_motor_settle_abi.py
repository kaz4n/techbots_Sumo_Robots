# Tests D199 from its frozen file-only ABI contract and checked prior oracles.
# Reuses46 behavioral assertions with current metadata and synthetic report fixtures.
# Freeze before subject inspection; all processes/network endpoints stay controlled.
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
RAW = 'state/analysis/P7_motor_settle_compile_raw'
WRAPPER = RAW + '/inspect_static_abi.py'
CONTRACT = 'state/analysis/P7_motor_settle_abi_contract.md'
CONTRACT_SHA = 'dfc762768731cf53ef1240a0d9eabface824ad96a72f3dfeaa1824c72332d956'
ABI02 = 'state/analysis/P7_app_motor_observe_compile_raw/inspect_static_abi02.py'
SOURCE = '117cc0e777341c893f4e618a97e3f196fd0bbf2427cb2a4b02543eb37d6522da'
OWNER = '/home/arduino/sumox26_codex_build/app-motor-settle-static01'
SCOPE = '/home/arduino/sumox26_codex_build/app-motor-settle-abi-static01'
HEAD = '1234567890abcdef1234567890abcdef12345678'
PROBE_SYMBOL = '_ZN6motors12_GLOBAL__N_119settle_probe_reportE'
PROBE_ADDRESS = 0x20021800  # Unrelated synthetic address, never a target observation.
SAMPLE, REPORT, REASON = ('motors::SettleProbeSample', 'motors::SettleProbeReport',
                          'motors::SettleProbeReason')
PINS = {
    ABI02: (8219, 'a0a5aef19538059450bcb723b6f74cca4d9b7008454760285e8818540ceca421'),
    'tools/compile_motor_settle_probe.py': (7570, 'b98a5f54e2be122162e76074673190f52ef4218c766d517125b48127bb4b8b62'),
    RAW + '/inputs_static.json': (13432, 'aa314548521968fd3b1b7b1ef415da3c72c90a6bc914d0a9204ff707bcd7d282'),
    RAW + '/native_static01/result.json': (1608, '9b7f0c445cc84ad6d526445bf8e93ea189f718f0c883da8a1bf5cf077e741af5'),
    RAW + '/native_static01/artifacts.json': (9648, 'e18384c14c0b1367667b265ab4c532a4010be65697460a1cd45487bccd9eca10'),
}
ORACLES = {
    'base': ('tests/tooling/test_app_motor_observe_abi.py', 'b43b384aafc77499b4752af7633e2a94c98e67e955554f75490f5dc30e45bcbe'),
    'abi02': ('tests/tooling/test_app_motor_observe_abi02.py', '9e50373e9c0f9d26ecd1e6f4097aa90bf7f346fa42476183b50ed2d0c1feddc3'),
    'mode': ('tests/tooling/test_app_motor_observe_abi_windows_mode.py', '9777060b05f041f409a822e30c68c1630192b0354d6462b89f47cb1a2b1ac687'),
}
FIELDS = (
    (SAMPLE, 'elapsed_us', 0, 4), (SAMPLE, 'poll_index', 4, 4),
    (SAMPLE, 'reason', 8, 1), (SAMPLE, 'fresh_mask', 9, 1),
    (SAMPLE, 'valid', 10, 1), (SAMPLE, 'reserved', 11, 1),
    (REPORT, 'current', 0, 12), (REPORT, 'first_failure', 12, 12),
    (REPORT, 'has_current', 24, 1), (REPORT, 'has_failure', 25, 1),
    (REPORT, 'reserved', 26, 2),
)
REASONS = ('NONE', 'SUCCESS', 'NULL_CONTEXT', 'PRECONDITION', 'INITIAL_BANK',
           'POLL_DEADLINE', 'POLL_BANK', 'FINAL_DEADLINE', 'POLL_LIMIT')
NEW_TAGS = tuple((label, kind + '.' + member, value)
    for kind, member, offset, width in FIELDS
    for label, value in (('FIELD_OFFSET', offset), ('FIELD_WIDTH', width))) + tuple(
    ('REASON', name, value) for value, name in enumerate(REASONS))
REJECT = (ValueError, TypeError, RuntimeError, OSError, SystemExit, KeyError)
ABI_SELECTED = (
    'test_decimal_and_hex_normalize_only_private_copy_with_exact_metadata',
    'test_polls_size_and_offset_are_observed_instead_of_assumed',
    'test_summary_rejects_bad_container_counts_rows_base64_and_utf8',
    'test_normalizer_rejects_missing_duplicate_malformed_zero_oversized_symbols',
    'test_parser_rejects_exec_section_symbol_size_and_bss_bounds',
    'test_parser_rejects_missing_duplicate_tags_and_alignment_windows',
    'test_command_receipts_reject_argv_execution_deadlines_streams_and_stderr',
)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def checked(name, digest, size=None):
    raw = (ROOT / name).read_bytes()
    if sha(raw) != digest or (size is not None and len(raw) != size):
        raise AssertionError('Frozen input changed: ' + name)
    return raw


def module(raw, path, name):
    result = types.ModuleType(name); result.__file__ = str(path)
    result.__dict__['__builtins__'] = dict(vars(builtins))
    exec(compile(raw, str(path), 'exec'), result.__dict__)
    return result


def helper(kind):
    path, digest = ORACLES[kind]
    return module(checked(path, digest), ROOT / path, '_d199_historical_' + kind)


def input_projection():
    base, second = helper('base'), helper('abi02')
    path = base.ORIGINAL; size, digest = base.PINS[path]
    return second.expected_projection(base.expected_projection(checked(path, digest, size)))


def projection(raw):
    if (len(raw), sha(raw)) != (16937, 'b03561df65e768cf582a42d520e6241a9cd02c3563685b87070bd3dfc820e981'):
        raise AssertionError('Expected original-first ABI02 bytes')
    pairs = (
        (b'P7_app_motor_observe_compile_raw', b'P7_motor_settle_compile_raw', 1),
        (b"'/inspect_static_abi02.py'", b"'/inspect_static_abi.py'", 1),
        (b'tools/compile_app_motor_observe.py', b'tools/compile_motor_settle_probe.py', 1),
        (b"'native_abi_static02'", b"'native_abi_static01'", 1),
        (b'app-motor-observe-abi-static02', b'app-motor-settle-abi-static01', 1),
        (b'app-motor-observe-static01', b'app-motor-settle-static01', 1),
        (b'D194_STATIC_FILE_ONLY_ABI02', b'D199_STATIC_FILE_ONLY_ABI', 2),
        (b'3a08ddeb437c47940a1a6b2ba8e63f7843e5b242ca68ae38c27849bd4e33dbb0', SOURCE.encode(), 1),
        (b'70e1f016cec041b40c98c7c5dd5ee20223d75c4a876c76d2fcdea3d790d63827', PINS['tools/compile_motor_settle_probe.py'][1].encode(), 1),
        (b'aa350c657fbff328dc139793c4ccd09c86ce45e05bdc7acaa20822498beb7d6e', PINS[RAW + '/inputs_static.json'][1].encode(), 1),
        (b'24d12778bbb337a5cba411fadab5c5e7a8fd69f99beee7b68ac110c31613622b', PINS[RAW + '/native_static01/result.json'][1].encode(), 1),
        (b'5ceba77dde7c493d66398bfd6d8e0e27e56345612290cb8fef9328f24b87625b', PINS[RAW + '/native_static01/artifacts.json'][1].encode(), 1),
        (b"'countdown::Result', 'report_.polls')", b"'countdown::Result', 'motors::SettleProbeSample',\n         'motors::SettleProbeReport', 'motors::SettleProbeReason', 'report_.polls')", 1),
        (b"    build = OWNER + '/build/app_motor_observe.ino'\n", b"    expressions += settle_expressions()\n    build = OWNER + '/build/app_motor_observe.ino'\n", 1),
    )
    for before, after, count in pairs:
        if raw.count(before) != count: raise AssertionError('Projection occurrence: ' + repr(before))
        raw = raw.replace(before, after)
    if (len(raw), sha(raw)) != (17061, '67ff238ce7a9f847e53d98fb4f3c47f02bbea12c51a1062457f1583a9399acc6'):
        raise AssertionError('Independent projected identity differs')
    return raw


def expressions():
    result = []
    for kind, member, _, _ in FIELDS:
        key = kind + '.' + member
        result += ['echo SUMOX_FIELD_OFFSET ' + key + '\\n',
                   'p/d (unsigned long)&((' + kind + '*)0)->' + member,
                   'echo SUMOX_FIELD_WIDTH ' + key + '\\n',
                   'p/d sizeof(((' + kind + '*)0)->' + member + ')']
    for name in REASONS:
        result += ['echo SUMOX_REASON ' + name + '\\n',
                   'p/d (unsigned int)motors::SettleProbeReason::' + name]
    return result


def text(result, index):
    return base64.b64decode(result['commands'][index]['stdout_base64']).decode()


def replace_text(result, index, value):
    raw = value.encode(); result['commands'][index].update(
        stdout_base64=base64.b64encode(raw).decode(), stdout_bytes=len(raw))


def extend_packet(result, layout, report_token='28', report_address=PROBE_ADDRESS):
    debug = text(result, 3); blocks = []
    for name, size, alignment in ((SAMPLE, 12, 4), (REPORT, 28, 4), (REASON, 1, 1)):
        blocks += ['SUMOX_SIZE ' + name, '$1 = ' + str(size),
                   'SUMOX_ALIGN ' + name, '$1 = ' + str(alignment),
                   'SUMOX_LAYOUT ' + name, 'type = controlled synthetic probe type']
    marker = 'SUMOX_SIZE report_.polls\n'
    if debug.count(marker) != 1: raise AssertionError('Synthetic polls marker')
    debug = debug.replace(marker, '\n'.join(blocks) + '\n' + marker)
    old = 'SUMOX_LAYOUT report_.polls\ntype = controlled fixture\nSUMOX_SIZE bool'
    if debug.count(old) != 1: raise AssertionError('Synthetic polls type block')
    debug = debug.replace(old, 'SUMOX_LAYOUT report_.polls\ntype = unsigned int\nSUMOX_SIZE bool')
    for label, name, value in NEW_TAGS:
        debug += 'SUMOX_' + label + ' ' + name + '\n$9 = ' + str(value) + '\n'
    replace_text(result, 3, debug)
    replace_text(result, 2, text(result, 2) +
        f' 92: {report_address:08x} {report_token} OBJECT LOCAL DEFAULT 7 {PROBE_SYMBOL}\n')
    result['scope'] = 'D199_STATIC_FILE_ONLY_ABI'
    return result, layout


def set_up_inputs(cls):
    if not sys.dont_write_bytecode: raise RuntimeError('D199 oracle requires Python -B')
    cls.raw = (ROOT / WRAPPER).read_bytes()
    cls.inputs = {name: checked(name, digest, size) for name, (size, digest) in PINS.items()}
    cls.contract = checked(CONTRACT, CONTRACT_SHA)


def private_base():
    path, digest = ORACLES['base']; raw = checked(path, digest)
    if raw.count(b'D194_STATIC_FILE_ONLY_ABI') != 3: raise AssertionError('Historical scope occurrences')
    raw = raw.replace(b'D194_STATIC_FILE_ONLY_ABI', b'D199_STATIC_FILE_ONLY_ABI')
    if (len(raw), sha(raw)) != (46134, 'a7f77d9b640988fcd2fd891abdc4d4b2ac449058d23ce7b9e794fdd13fe7f358'):
        raise AssertionError('Historical scope-only projection changed')
    base = module(raw, ROOT / path, '_d199_private_behavior_oracle')
    base.WRAPPER, base.CONTRACT, base.CONTRACT_SHA = WRAPPER, CONTRACT, CONTRACT_SHA
    base.COMPILE_RAW, base.SOURCE, base.OWNER, base.SCOPE = RAW, SOURCE, OWNER, SCOPE
    base.LAUNCHER = 'tools/compile_motor_settle_probe.py'
    base.PINS = dict(PINS)
    original_packet = base.packet
    base.packet = lambda *args, **kwargs: extend_packet(*original_packet(*args, **kwargs))
    base.ContractCase.setUpClass = classmethod(set_up_inputs)
    return base


def function_sources(raw):
    lines = raw.splitlines(keepends=True)
    return {node.name: b''.join(lines[node.lineno-1:node.end_lineno])
            for node in ast.parse(raw).body if isinstance(node, ast.FunctionDef)}


class SettleAbiContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        set_up_inputs(cls); cls.base = private_base(); cls.projected_input = input_projection()

    def setUp(self):
        self.base.ContractCase.setUp(self)

    def loaded(self):
        return self.subject.load_reader(root=ROOT)

    def scratch(self):
        return self.base.ContractCase.scratch(self)

    def reject(self, call):
        with self.assertRaises(REJECT): call()

    def packet(self, token='1024', report_token='28', address=PROBE_ADDRESS):
        prior = helper('base')
        return extend_packet(*prior.packet(token), report_token=report_token, report_address=address)

    def test_passive_import_and_exact_original_bootstrap_bodies(self):
        with ExitStack() as stack:
            for owner, names in ((Path, ('open', 'read_bytes', 'read_text', 'write_bytes', 'write_text', 'mkdir')),
                                 (builtins, ('open',)), (io, ('open',)), (os, ('open',))):
                for name in names: stack.enter_context(mock.patch.object(owner, name, side_effect=AssertionError('Import I/O')))
            value = module(self.raw, ROOT / WRAPPER, '_d199_passive')
        for name in ('project_reader', 'settle_expressions', 'summarize', 'load_reader', 'main'):
            self.assertTrue(callable(getattr(value, name)))
        old, new = function_sources(self.inputs[ABI02]), function_sources(self.raw)
        for name in ('require', '_stamp', '_plain_chain', '_read_handle', 'pinned'):
            self.assertEqual(new[name], old[name])

    def test_exact_fourteen_projection_changes_and_no_execution_or_io(self):
        expected = projection(self.projected_input)
        self.subject.__dict__['__builtins__']['exec'] = mock.Mock(side_effect=AssertionError('Projection exec'))
        with mock.patch.object(Path, 'read_bytes', side_effect=AssertionError('Projection read')):
            actual = self.subject.project_reader(self.projected_input)
        self.assertIs(type(actual), bytes); self.assertEqual(actual, expected)

    def test_projection_rejects_types_drift_counts_newlines_and_already_projected(self):
        raw = self.projected_input
        for bad in (None, True, raw.decode(), bytearray(raw), memoryview(raw), b'', raw[:-1], raw+b'\n',
                    raw.replace(b'\n', b'\r\n'), projection(raw), raw+b'\n# D194_STATIC_FILE_ONLY_ABI02',
                    raw.replace(b"'native_abi_static02'", b"'native_abi_static01'")):
            with self.subTest(type=type(bad).__name__): self.reject(lambda: self.subject.project_reader(bad))

    def test_all_six_inputs_precede_any_private_execution(self):
        inputs = dict(self.inputs, **{CONTRACT: self.contract})
        for failed in inputs:
            root = self.scratch()
            for name, raw in inputs.items():
                path = root/name; path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes(raw)
            (root/failed).write_bytes(inputs[failed]+b'\n')
            self.subject.__dict__['__builtins__']['exec'] = mock.Mock(side_effect=AssertionError('Unpinned exec'))
            self.reject(lambda: self.subject.load_reader(root=root))
            self.subject.__dict__['__builtins__']['exec'].assert_not_called()

    def test_original_first_composition_and_private_extended_pins(self):
        events = []; execute = builtins.exec; projector = self.subject.project_reader
        def observed(code, namespace, *args):
            answer = execute(code, namespace, *args)
            if namespace.get('__file__') == str(ROOT/ABI02):
                saved = namespace['project_reader']
                def first(raw): events.append('ABI02'); return saved(raw)
                namespace['project_reader'] = first
                namespace['main'] = mock.Mock(side_effect=AssertionError('Historical main'))
            return answer
        def second(raw):
            events.append('D199'); self.assertEqual(raw, self.projected_input); return projector(raw)
        self.subject.__dict__['__builtins__']['exec'] = observed
        with mock.patch.object(self.subject, 'project_reader', second): reader = self.loaded()
        self.assertEqual(events, ['ABI02', 'D199'])
        old = module(self.inputs[ABI02], ROOT/ABI02, '_d199_prior_pins').load_reader(root=ROOT)
        retargeted = {'tools/compile_app_motor_observe.py',
            'state/analysis/P7_app_motor_observe_compile_raw/inputs_static.json',
            'state/analysis/P7_app_motor_observe_compile_raw/native_static01/result.json',
            'state/analysis/P7_app_motor_observe_compile_raw/native_static01/artifacts.json'}
        for name, digest in old.HARD_PINS.items():
            if name not in retargeted: self.assertEqual(reader.HARD_PINS[name], digest)
        for name, (_, digest) in PINS.items(): self.assertEqual(reader.HARD_PINS[name], digest)
        self.assertEqual(reader.HARD_PINS[CONTRACT], CONTRACT_SHA)
        self.assertNotIn(reader, sys.modules.values()); self.assertIsNot(reader, self.loaded())
        self.assertEqual(reader.SELF, WRAPPER); self.assertEqual(reader.SOURCE, SOURCE)
        owner = reader.StaticAbi(HEAD)
        self.assertEqual(owner.output, ROOT/RAW/'native_abi_static01'); self.assertEqual(owner.remote, SCOPE)
        self.assertEqual(reader.OWNER, OWNER); self.assertEqual(owner.inputs_path, ROOT/RAW/'inputs_static.json')

    def test_invalid_cli_and_missing_B_precede_loading_valid_main_delegates_once(self):
        invalid = (None, True, [], '', ('--execute','--reviewed-head',HEAD), ['--help'],
                   ['--execute','--reviewed-head',HEAD.upper()], ['--execute','--reviewed-head',1],
                   ['--execute','--reviewed-head',HEAD,'--owner','old'])
        with mock.patch.object(self.subject,'load_reader',side_effect=AssertionError('Invalid CLI loaded')):
            for args in invalid: self.reject(lambda: self.subject.main(args))
            with mock.patch.object(sys,'dont_write_bytecode',False):
                self.reject(lambda:self.subject.main(['--check-only','--reviewed-head',HEAD]))
        for action in ('--check-only','--execute'):
            args=[action,'--reviewed-head',HEAD]; private=types.SimpleNamespace(main=mock.Mock(return_value=37))
            with mock.patch.object(self.subject,'load_reader',return_value=private) as load:
                self.assertEqual(self.subject.main(args),37); load.assert_called_once_with(root=self.subject.ROOT)
                private.main.assert_called_once_with(args)
        error=RuntimeError('delegated first error'); private.main.side_effect=error
        with mock.patch.object(self.subject,'load_reader',return_value=private):
            with self.assertRaises(RuntimeError) as caught:self.subject.main(args)
            self.assertIs(caught.exception,error)

    def test_exact_fresh62_expressions_and_four_commands223_subject_order(self):
        expected=expressions(); first=self.subject.settle_expressions(); second=self.subject.settle_expressions()
        self.assertEqual(first,expected); self.assertIs(type(first),list); self.assertIsNot(first,second)
        first.append('controlled mutation'); self.assertEqual(self.subject.settle_expressions(),expected)
        reader=self.loaded(); captured=[]
        backend=types.SimpleNamespace(PREFIX='/fixed/tool-',gdb=lambda path,items:captured.append((path,items)) or ['gdb',path,*items])
        commands=reader.queries(backend); debug,items=captured[0]
        self.assertEqual(len(commands),4); self.assertEqual(len(items),223); self.assertEqual(len(expected),62)
        self.assertEqual(commands[:3],[['/fixed/tool-readelf','--version'],['/fixed/tool-gdb','--version'],
            ['/fixed/tool-readelf','-hSWs',OWNER+'/build/app_motor_observe.ino.elf']])
        self.assertEqual(debug,OWNER+'/build/app_motor_observe.ino_debug.elf')
        types_expected=list(self.base.TYPES); at=types_expected.index('report_.polls');types_expected[at:at]=[SAMPLE,REPORT,REASON]
        for label in ('SIZE','ALIGN','LAYOUT'):
            self.assertEqual([x for x in items if x.startswith('echo SUMOX_'+label+' ')],
                             ['echo SUMOX_'+label+' '+name+'\\n' for name in types_expected])
        self.assertEqual(reader.WINDOWS,self.base.WINDOWS);self.assertEqual(len(reader.WINDOWS),11)
        self.assertEqual(items[-62:],expected)
        self.assertIn('p/d alignof(unsigned int)',items)
        self.assertEqual(items[items.index('echo SUMOX_LAYOUT report_.polls\\n')+2],'echo SUMOX_SIZE bool\\n')
        self.assertFalse(any('SUMOX_VALID' in item or item.startswith(('target ','call ')) for item in items))

    def test_complete_separate_report_decimal_hex_and_exact_mappings_preserve_raw(self):
        reader=self.loaded()
        for runner_token,report_token in (('1024','28'),('0x400','0x1c'),('001024','0x01c')):
            result,layout=self.packet(runner_token,report_token);before=copy.deepcopy(result);old_layout=copy.deepcopy(layout)
            answer=reader.summarize(result,layout);probe=answer['settle_probe']
            self.assertEqual(probe,dict(symbol=PROBE_SYMBOL,address=PROBE_ADDRESS,bytes=28,alignment=4,section=7,
                fields={kind+'.'+member:dict(offset=offset,bytes=width) for kind,member,offset,width in FIELDS},
                reasons=dict(zip(REASONS,range(9)))))
            self.assertEqual(list(probe['fields']),[kind+'.'+member for kind,member,_,_ in FIELDS])
            self.assertEqual(list(probe['reasons']),list(REASONS));self.assertNotIn('valid_bits',probe)
            self.assertEqual(answer['status'],'STATIC_ABI_OBSERVED');self.assertEqual(len(answer['windows']),11)
            self.assertNotIn('settle_probe',answer['windows']);self.assertIn('report_.before_abort.previous',answer['windows'])
            self.assertIn('readelf_size_projection',answer);self.assertIn('polls_alignment_type',answer)
            self.assertEqual(result,before);self.assertEqual(layout,old_layout)

    def test_summary_once_on_deep_copies_even_if_delegate_mutates_them(self):
        result,layout=self.packet();saved=self.loaded().summarize(result,layout);saved.pop('settle_probe')
        before,old_layout=copy.deepcopy(result),copy.deepcopy(layout);seen=[]
        def delegate(packet,bounds):
            self.assertIsNot(packet,result);self.assertIsNot(bounds,layout)
            self.assertIsNot(packet['commands'][2],result['commands'][2])
            seen.append(True);packet['commands'].clear();bounds.clear();return saved
        answer=self.subject.summarize(result,layout,summary=delegate)
        self.assertEqual(seen,[True]);self.assertNotIn('settle_probe',saved)
        self.assertEqual({k:v for k,v in answer.items() if k!='settle_probe'},saved)
        self.assertEqual(result,before);self.assertEqual(layout,old_layout)

    def test_summary_primary_identity_non_dict_and_invalid_containers_fail(self):
        result,layout=self.packet();error=RuntimeError('saved original summary')
        delegate=mock.Mock(side_effect=error)
        with self.assertRaises(RuntimeError) as caught:self.subject.summarize(result,layout,summary=delegate)
        self.assertIs(caught.exception,error);self.assertEqual(delegate.call_count,1)
        self.reject(lambda:self.subject.summarize(result,layout,summary=lambda *_:[]))
        for bad in (None,[],{'commands':[]},{'commands':result['commands'][:3]},{'commands':[None]*4}):
            self.reject(lambda:self.subject.summarize(bad,layout,summary=lambda *_:{}))
        for bad in (None,[],True):self.reject(lambda:self.subject.summarize(result,bad,summary=lambda *_:{}))
        self.reject(lambda:self.subject.summarize(result,layout,summary=None))

    def test_new_numeric_tags_each_missing_duplicate_wrong_and_malformed_refuse(self):
        reader=self.loaded();result,layout=self.packet();original=text(result,3)
        for label,name,number in NEW_TAGS:
            marker='SUMOX_'+label+' '+name+'\n';block=marker+'$9 = '+str(number)+'\n'
            for changed in (original.replace(block,''),original+block,
                            original.replace(block,marker+'$9 = '+str(number+1)+'\n'),
                            original.replace(block,marker+'$9 = -1\n'),
                            original.replace(block,marker+'$9 = 1.0\n')):
                with self.subTest(label=label,name=name):
                    packet=copy.deepcopy(result);replace_text(packet,3,changed)
                    self.reject(lambda:reader.summarize(packet,layout))

    def test_new_tag_order_extra_unknown_and_non_numeric_lines_refuse(self):
        reader=self.loaded();result,layout=self.packet();original=text(result,3)
        first='SUMOX_FIELD_OFFSET '+SAMPLE+'.elapsed_us\n$9 = 0\n'
        second='SUMOX_FIELD_WIDTH '+SAMPLE+'.elapsed_us\n$9 = 4\n'
        for changed in (original.replace(first+second,second+first),original+'SUMOX_REASON UNKNOWN\n$9 = 9\n',
                        original+'SUMOX_FIELD_WIDTH '+REPORT+'.other\n$9 = 4\n',
                        original.replace(first,first.replace('$9 = 0','not a numeric answer'))):
            packet=copy.deepcopy(result);replace_text(packet,3,changed);self.reject(lambda:reader.summarize(packet,layout))

    def test_three_probe_type_sizes_and_alignments_are_observed_and_exact(self):
        reader=self.loaded();result,layout=self.packet();original=text(result,3)
        for kind,size,alignment in ((SAMPLE,12,4),(REPORT,28,4),(REASON,1,1)):
            for label,number in (('SIZE',size),('ALIGN',alignment)):
                block='SUMOX_'+label+' '+kind+'\n$1 = '+str(number)
                for changed in (0,number+1):
                    packet=copy.deepcopy(result);replace_text(packet,3,original.replace(block,block.rsplit(' ',1)[0]+' '+str(changed)))
                    self.reject(lambda:reader.summarize(packet,layout))

    def test_current_polls_type_guard_and_required_numeric_tags_remain_active(self):
        reader=self.loaded();result,layout=self.packet();original=text(result,3)
        for changed in (original.replace('type = unsigned int','type = unsigned long'),
                        original.replace('SUMOX_SIZE bool','SUMOX_ALIGN bool',1),
                        original.replace('SUMOX_OFFSET report_.before_abort.previous','MISSING_PREVIOUS')):
            packet=copy.deepcopy(result);replace_text(packet,3,changed);self.reject(lambda:reader.summarize(packet,layout))

    def test_exact_symbol_candidate_name_kind_binding_section_and_duplicates(self):
        reader=self.loaded();result,layout=self.packet();original=text(result,2);row=original.splitlines(keepends=True)[-1]
        for changed in (original.replace(row,''),original.replace(PROBE_SYMBOL,PROBE_SYMBOL+'x'),original+row,
                        original+row.replace('OBJECT','FUNC'),original+row.replace('LOCAL','GLOBAL'),
                        original.replace(row,row.replace('OBJECT','NOTYPE')),
                        original.replace(row,row.replace('LOCAL','GLOBAL')),
                        original.replace(row,row.replace('DEFAULT 7','HIDDEN 7')),
                        original.replace(row,row.replace('DEFAULT 7','DEFAULT ABS')),
                        original.replace(row,row.replace('DEFAULT 7','DEFAULT 8'))):
            packet=copy.deepcopy(result);replace_text(packet,2,changed);self.reject(lambda:reader.summarize(packet,layout))

    def test_symbol_size_tokens_alignment_zero_bounds_and_overlap(self):
        reader=self.loaded()
        for token in ('0','27','29','0x0','0x1b','0x1d','0X1c','-28','1e2','0xzz'):
            result,layout=self.packet(report_token=token);self.reject(lambda:reader.summarize(result,layout))
        for address in (PROBE_ADDRESS+1,0x20020000,0x200203fc,0x2001fff0,0x20022000-24):
            result,layout=self.packet(address=address);self.reject(lambda:reader.summarize(result,layout))
        for address in (0x20020400,0x20022000-28):
            result,layout=self.packet(address=address)
            self.assertEqual(reader.summarize(result,layout)['settle_probe']['address'],address)
        result,layout=self.packet();layout['bss_zero']['end']=PROBE_ADDRESS+27
        self.reject(lambda:reader.summarize(result,layout))

    def test_global_section_agreement_and_bss_zero_not_whole_section(self):
        reader=self.loaded();result,layout=self.packet();original=text(result,2)
        for changed in (original.replace('NOBITS','PROGBITS'),original.replace('002000','002004'),
                        original.replace('.bss NOBITS 20020000','.bss NOBITS 20020004')):
            packet=copy.deepcopy(result);replace_text(packet,2,changed);self.reject(lambda:reader.summarize(packet,layout))
        bounded=copy.deepcopy(layout);bounded['bss_zero']['end']=PROBE_ADDRESS
        self.reject(lambda:reader.summarize(result,bounded))
        self.assertLess(PROBE_ADDRESS+28,layout['sections'][0]['address']+layout['sections'][0]['size'])

    def test_bad_raw_encoding_on_either_new_input_stream_refuses_without_mutation(self):
        reader=self.loaded();result,layout=self.packet()
        for index in (2,3):
            for encoded in ('@@','YQ===',base64.b64encode(b'\xff').decode()):
                packet=copy.deepcopy(result);packet['commands'][index]['stdout_base64']=encoded;before=copy.deepcopy(packet)
                self.reject(lambda:reader.summarize(packet,layout));self.assertEqual(packet,before)

    def test_real_prepare_binds_d198_header_and_refuses_old_d193_artifact_packet(self):
        reader=self.loaded();owner=reader.StaticAbi(HEAD);owner.compiler.CompileDiagnostic.admission(owner)
        self.assertIn('src/hal/motor_settle_probe.h',owner.code)
        self.assertEqual(sha(owner.code['src/hal/motor_settle_probe.h']),'2eced554fce20ff938daf44866ee0bad6d99fa28e377af762bb0f037376b75a8')
        self.assertEqual(owner.source_sha256,SOURCE)
        owner.local=mock.Mock(return_value=None);owner.output=self.scratch()/'fresh-abi'
        with mock.patch.object(reader.shutil,'disk_usage',return_value=types.SimpleNamespace(free=268435456)):
            report=owner.prepare()
        self.assertEqual(report['file_commands'],4);self.assertLessEqual(report['command_units'],30000)
        self.assertFalse(owner.output.exists());self.assertFalse(owner.claimed)
        self.assertEqual(owner.build_path,OWNER+'/build');self.assertIn('SUMOX_FIELD_WIDTH',owner.program)
        old_name='state/analysis/P7_app_motor_observe_compile_raw/native_static01/artifacts.json'
        old=checked(old_name,'5ceba77dde7c493d66398bfd6d8e0e27e56345612290cb8fef9328f24b87625b')
        self.reject(lambda:owner.compiler.CompileDiagnostic.validate_artifact_reply(owner,old.decode()))

    def test_new_report_failure_retains_original_raw_and_independent_local_closure(self):
        for fault in ('symbol','field','reason'):
            _,owner,result,writes=self.base.LifecycleContract.executing_owner(self)
            if fault=='symbol':replace_text(result,2,text(result,2).replace(PROBE_SYMBOL,PROBE_SYMBOL+'x'))
            else:
                marker=('SUMOX_FIELD_OFFSET '+SAMPLE+'.elapsed_us' if fault=='field' else 'SUMOX_REASON NONE')
                replace_text(result,3,text(result,3).replace(marker,'MISSING_'+fault))
            owner.direct.return_value=(types.SimpleNamespace(stdout=json.dumps(result),stderr=''),None)
            self.reject(owner.execute)
            self.assertEqual(writes[1],('result.json',result));self.assertNotIn('abi.json',[name for name,_ in writes])
            self.assertEqual(writes[-1][1]['status'],'FAILED');owner.local.assert_called_once_with()


def load_tests(loader,standard,pattern):
    if not sys.dont_write_bytecode:raise RuntimeError('Use Python -B')
    base=private_base();suite=unittest.TestSuite([standard])
    inherited=unittest.TestSuite([loader.loadTestsFromTestCase(base.BootstrapContract),
        unittest.TestSuite(base.AbiContract(name) for name in ABI_SELECTED),
        loader.loadTestsFromTestCase(base.LifecycleContract)])
    mode=helper('mode');mode.SUBJECT=ROOT/WRAPPER
    inherited.addTests(loader.loadTestsFromTestCase(mode.WindowsExecutableModeContract))
    if inherited.countTestCases()!=46:raise AssertionError('Expected11 bootstrap+7 ABI+14 lifecycle+14 mode')
    suite.addTests(inherited)
    return suite


if __name__=='__main__':
    unittest.main(verbosity=2)
