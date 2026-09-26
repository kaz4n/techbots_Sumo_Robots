# Tests ABI02 from its fixed supplementary contract and checked historical fixtures.
# Keeps current member-type confirmation separate from observed alignment and raw evidence.
# Freeze before execution; author has not read the new wrapper implementation.
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
WRAPPER = RAW + '/inspect_static_abi02.py'
ORIGINAL = RAW + '/inspect_static_abi.py'
CONTRACT = 'state/analysis/P7_app_motor_observe_abi02_contract.md'
CONTRACT_SHA = '772615cda21858c3ca32eea6a541d97ec79985054cdbdad5ea029c225a5d673c'
ORACLE = 'tests/tooling/test_app_motor_observe_abi.py'
ORACLE_SHA = 'b43b384aafc77499b4752af7633e2a94c98e67e955554f75490f5dc30e45bcbe'
RESULT = RAW + '/native_abi_static01/result.json'
CLOSURE = RAW + '/native_abi_static01/local_result.json'
EVIDENCE = 'e83afc5f10cec2ed72f88d6567f6f13e5809518e1b89f3d5988d988b297e78f5'
PINS = {
    ORIGINAL: (9318, '497f756e4eab440d659a4d26ef38ec8d92abdd9f92a5938d1da04705745f42d5'),
    RESULT: (893217, EVIDENCE),
    CLOSURE: (336, '589b78d1ff3cacbe96869f2f2c43d3fc546a9ff2cbfc26c34d1ad3a3d9b9ec01'),
}
INPUT_SIZE = 16833
INPUT_SHA = 'f359bebbbba176036891027412327b6b59e47d849e46c37cfe3363cd70a95c14'
OUTPUT_SIZE = 16937
OUTPUT_SHA = 'b03561df65e768cf582a42d520e6241a9cd02c3563685b87070bd3dfc820e981'
HEAD = '1234567890abcdef1234567890abcdef12345678'
OWNER = '/home/arduino/sumox26_codex_build/app-motor-observe-static01'
SCOPE = '/home/arduino/sumox26_codex_build/app-motor-observe-abi-static02'
TYPE_BLOCK = 'SUMOX_LAYOUT report_.polls\ntype = unsigned int\nSUMOX_SIZE bool'
TYPE_META = {'type': 'unsigned int', 'evidence_sha256': EVIDENCE}
REJECT = (ValueError, TypeError, OSError, RuntimeError, SystemExit, KeyError)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def module(raw, path, name):
    value = types.ModuleType(name)
    value.__file__ = str(path)
    value.__dict__['__builtins__'] = dict(vars(builtins))
    exec(compile(raw, str(path), 'exec'), value.__dict__)
    return value


def expected_projection(raw):
    if (len(raw), digest(raw)) != (INPUT_SIZE, INPUT_SHA):
        raise AssertionError('Independent ABI01 projected reader identity')
    pairs = ((b"'/inspect_static_abi.py'", b"'/inspect_static_abi02.py'", 1),
             (b"'native_abi_static01'", b"'native_abi_static02'", 1),
             (b'app-motor-observe-abi-static01', b'app-motor-observe-abi-static02', 1),
             (b'D194_STATIC_FILE_ONLY_ABI', b'D194_STATIC_FILE_ONLY_ABI02', 2),
             (b"expression + '(' + subject + ')'",
              b"expression + '(' + ('unsigned int' if name == 'report_.polls' and\n"
              b"                            label == 'ALIGN' else subject) + ')'", 1))
    for old, new, count in pairs:
        if raw.count(old) != count:
            raise AssertionError('Independent supplementary occurrence: ' + repr(old))
        raw = raw.replace(old, new)
    if (len(raw), digest(raw)) != (OUTPUT_SIZE, OUTPUT_SHA):
        raise AssertionError('Independent ABI02 projected reader identity')
    return raw


def function_sources(raw):
    lines = raw.splitlines(keepends=True)
    return {node.name: b''.join(lines[node.lineno - 1:node.end_lineno])
            for node in ast.parse(raw).body if isinstance(node, ast.FunctionDef)}


class Abi02Contract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not sys.dont_write_bytecode:
            raise RuntimeError('ABI02 independent oracle requires Python -B')
        cls.raw = (ROOT / WRAPPER).read_bytes()
        cls.inputs = {name: (ROOT / name).read_bytes() for name in PINS}
        for name, raw in cls.inputs.items():
            if (len(raw), digest(raw)) != PINS[name]:
                raise AssertionError('Fixed ABI02 provenance changed: ' + name)
        contract = (ROOT / CONTRACT).read_bytes()
        if digest(contract) != CONTRACT_SHA: raise AssertionError('ABI02 contract changed')
        cls.contract = contract
        oracle = (ROOT / ORACLE).read_bytes()
        if digest(oracle) != ORACLE_SHA: raise AssertionError('Historical oracle changed')
        cls.support = module(oracle, ROOT / ORACLE, '_abi02_checked_public_fixtures')
        old_source = (ROOT / cls.support.ORIGINAL).read_bytes()
        if digest(old_source) != cls.support.PINS[cls.support.ORIGINAL][1]:
            raise AssertionError('Historical ABI reader changed')
        cls.projected01 = cls.support.expected_projection(old_source)

    def setUp(self):
        self.subject = module(self.raw, ROOT / WRAPPER, '_abi02_independent_subject')
        for owner, names in ((subprocess, ('run', 'Popen', 'call', 'check_call', 'check_output')),
                             (socket, ('socket', 'create_connection'))):
            for name in names:
                patch = mock.patch.object(owner, name, side_effect=AssertionError('External effect: ' + name))
                patch.start(); self.addCleanup(patch.stop)

    def reject(self, call):
        with self.assertRaises(REJECT): call()

    def scratch(self):
        temp = tempfile.TemporaryDirectory(prefix='sumox-abi02-',
                   dir='/dev/shm' if sys.platform == 'linux' else None)
        self.addCleanup(temp.cleanup)
        return Path(temp.name).resolve()

    def loaded(self):
        return self.subject.load_reader(root=ROOT)

    def packet(self, token='0x400'):
        result, layout = self.support.packet(token)
        self.current_type(result)
        result['scope'] = 'D194_STATIC_FILE_ONLY_ABI02'
        return result, layout

    def current_type(self, result):
        text = self.support.stream_text(result, 3)
        old = 'SUMOX_LAYOUT report_.polls\ntype = controlled fixture\nSUMOX_SIZE bool'
        self.assertEqual(text.count(old), 1)
        self.support.replace_text(result, 3, text.replace(old, TYPE_BLOCK))

    def executing_owner(self):
        reader, owner, result, writes = self.support.LifecycleContract.executing_owner(self)
        self.current_type(result)
        result['scope'] = 'D194_STATIC_FILE_ONLY_ABI02'
        owner.direct.return_value = (types.SimpleNamespace(stdout=json.dumps(result), stderr=''), None)
        return reader, owner, result, writes

    def test_import_is_passive_and_public_helpers_exist(self):
        with ExitStack() as stack:
            for owner, names in ((Path, ('open', 'read_bytes', 'read_text', 'write_bytes', 'write_text', 'mkdir')),
                                 (builtins, ('open',)), (io, ('open',)), (os, ('open',))):
                for name in names:
                    stack.enter_context(mock.patch.object(owner, name, side_effect=AssertionError('Import I/O')))
            value = module(self.raw, ROOT / WRAPPER, '_abi02_passive_import')
        for name in ('project_reader', 'summarize', 'load_reader', 'main'):
            self.assertTrue(callable(getattr(value, name)))

    def test_bootstrap_helper_source_bodies_are_exactly_the_repaired_original(self):
        old, new = function_sources(self.inputs[ORIGINAL]), function_sources(self.raw)
        for name in ('_stamp', '_plain_chain', '_read_handle', 'pinned', 'require'):
            self.assertIn(name, old); self.assertIn(name, new)
            self.assertEqual(new[name], old[name], name)

    def test_exact_supplementary_projection_has_only_contract_changes_and_no_io(self):
        expected = expected_projection(self.projected01)
        self.subject.__dict__['__builtins__']['exec'] = mock.Mock(side_effect=AssertionError('Projection executed'))
        with mock.patch.object(Path, 'read_bytes', side_effect=AssertionError('Projection read')), \
                mock.patch.object(os, 'open', side_effect=AssertionError('Projection opened')):
            actual = self.subject.project_reader(self.projected01)
        self.assertIs(type(actual), bytes); self.assertEqual(actual, expected)
        self.assertEqual((len(actual), digest(actual)), (OUTPUT_SIZE, OUTPUT_SHA))

    def test_projection_refuses_unprojected_types_drift_counts_and_newlines(self):
        raw = self.projected01
        bad = (None, True, raw.decode(), bytearray(raw), memoryview(raw), b'', raw[:-1], raw + b'\n',
               raw.replace(b'\n', b'\r\n'), raw.replace(b"'native_abi_static01'", b"'native_abi_static02'"),
               raw + b'\n# D194_STATIC_FILE_ONLY_ABI', self.inputs[ORIGINAL])
        for value in bad:
            with self.subTest(type=type(value).__name__): self.reject(lambda: self.subject.project_reader(value))

    def test_invalid_cli_and_missing_B_refuse_before_loading(self):
        bad = (None, True, '', [], ('--execute', '--reviewed-head', HEAD), ['--help'],
               ['--execute', '--reviewed-head', HEAD.upper()], ['--execute', '--reviewed-head', 4],
               ['--execute', '--reviewed-head', HEAD + 'a'], ['--reviewed-head', HEAD, '--execute'],
               ['--execute', '--reviewed-head', HEAD, '--owner', 'old'])
        with mock.patch.object(self.subject, 'load_reader', side_effect=AssertionError('Invalid CLI loaded')):
            for value in bad:
                with self.subTest(value=value): self.reject(lambda: self.subject.main(value))
            with mock.patch.object(sys, 'dont_write_bytecode', False):
                self.reject(lambda: self.subject.main(['--check-only', '--reviewed-head', HEAD]))

    def test_valid_main_delegates_exactly_once_and_preserves_result_or_primary_error(self):
        for action in ('--check-only', '--execute'):
            args = [action, '--reviewed-head', HEAD]
            private = types.SimpleNamespace(main=mock.Mock(return_value=23))
            with mock.patch.object(self.subject, 'load_reader', return_value=private) as load:
                self.assertEqual(self.subject.main(args), 23)
                load.assert_called_once_with(root=self.subject.ROOT)
                private.main.assert_called_once_with(args)
        primary = RuntimeError('original main failure')
        private.main.side_effect = primary
        with mock.patch.object(self.subject, 'load_reader', return_value=private):
            with self.assertRaises(RuntimeError) as caught: self.subject.main(args)
            self.assertIs(caught.exception, primary)

    def test_all_four_provenance_checks_precede_any_private_execution(self):
        originals = {**self.inputs, CONTRACT: self.contract}
        for failed in originals:
            root = self.scratch()
            for name, raw in originals.items():
                path = root / name; path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes(raw)
            (root / failed).write_bytes(originals[failed] + b'\n')
            self.subject.__dict__['__builtins__']['exec'] = mock.Mock(side_effect=AssertionError('Unpinned exec'))
            self.reject(lambda: self.subject.load_reader(root=root))
            self.subject.__dict__['__builtins__']['exec'].assert_not_called()

    def test_projection_composition_calls_original_first_on_its_exact_result(self):
        events = []; actual_exec = builtins.exec
        supplementary = self.subject.project_reader
        def observed_exec(code, namespace, *args):
            result = actual_exec(code, namespace, *args)
            if namespace.get('__file__') == str(ROOT / ORIGINAL):
                original = namespace['project_reader']
                def first(raw):
                    events.append('original'); return original(raw)
                namespace['project_reader'] = first
            return result
        def second(raw):
            events.append('supplement')
            self.assertEqual(raw, self.projected01)
            return supplementary(raw)
        self.subject.__dict__['__builtins__']['exec'] = observed_exec
        with mock.patch.object(self.subject, 'project_reader', second): self.loaded()
        self.assertEqual(events, ['original', 'supplement'])

    def test_private_composition_preserves_all_inherited_pins_and_failed_provenance(self):
        old_wrapper = module(self.inputs[ORIGINAL], ROOT / ORIGINAL, '_abi02_original_wrapper_fixture')
        old = old_wrapper.load_reader(root=ROOT)
        old_pins = dict(old.HARD_PINS); registered = dict(sys.modules)
        reader, fresh = self.loaded(), self.loaded()
        self.assertIsNot(reader, fresh)
        self.assertNotIn(reader, sys.modules.values()); self.assertNotIn(fresh, sys.modules.values())
        self.assertNotEqual(reader.__name__, '__main__')
        for key, value in registered.items(): self.assertIs(sys.modules[key], value)
        for name, value in old_pins.items(): self.assertEqual(reader.HARD_PINS[name], value)
        for name, (_, value) in PINS.items(): self.assertEqual(reader.HARD_PINS[name], value)
        self.assertEqual(reader.HARD_PINS[CONTRACT], CONTRACT_SHA)
        self.assertEqual(old.HARD_PINS, old_pins)
        self.assertEqual(old.SELF, ORIGINAL); self.assertEqual(reader.SELF, WRAPPER)
        self.assertEqual(reader.SOURCE, old.SOURCE); self.assertEqual(reader.BOOT, old.BOOT)
        self.assertEqual(reader.OWNER, OWNER)
        self.assertEqual(json.loads(self.inputs[CLOSURE])['status'], 'FAILED')

    def test_only_polls_alignment_query_changes_and_existing_tags_windows_stay(self):
        old_wrapper = module(self.inputs[ORIGINAL], ROOT / ORIGINAL, '_abi02_previous_query_fixture')
        old, new = old_wrapper.load_reader(root=ROOT), self.loaded()
        backend = types.SimpleNamespace(PREFIX='/fixed/tool-', gdb=lambda path, expressions: ['gdb', path, *expressions])
        before, after = old.queries(backend), new.queries(backend)
        self.assertEqual(len(after), 4); self.assertEqual(before[:3], after[:3])
        self.assertEqual(before[3][:2], after[3][:2])
        differences = [(a, b) for a, b in zip(before[3], after[3]) if a != b]
        self.assertEqual(len(before[3]), len(after[3]))
        self.assertEqual(differences, [('p/d alignof(((app_motor_observe::Runner*)0)->report_.polls)',
                                        'p/d alignof(unsigned int)')])
        self.assertEqual(new.WINDOWS, old.WINDOWS); self.assertEqual(new.TYPES, old.TYPES)

    def test_new_owner_is_distinct_but_build_artifact_owner_stays_original(self):
        reader = self.loaded(); owner = reader.StaticAbi(HEAD)
        self.assertEqual(owner.output, ROOT / RAW / 'native_abi_static02')
        self.assertEqual(owner.remote, SCOPE)
        self.assertEqual(reader.OWNER, OWNER)
        self.assertEqual(owner.local_pins[WRAPPER], digest(self.raw))
        self.assertEqual(owner.local_pins[ORIGINAL], PINS[ORIGINAL][1])
        self.assertEqual(owner.inputs_path, ROOT / RAW / 'inputs_static.json')

    def test_current_type_confirmation_accepts_LF_or_CRLF_and_delegates_original_arguments(self):
        for ending in ('\n', '\r\n'):
            result, layout = self.packet(); text = self.support.stream_text(result, 3)
            self.support.replace_text(result, 3, text.replace('\n', ending))
            before, layout_before = copy.deepcopy(result), copy.deepcopy(layout)
            saved = {'status': 'controlled', 'readelf_size_projection': {'unchanged': True}}
            def summary(actual, actual_layout):
                self.assertIs(actual, result); self.assertIs(actual_layout, layout)
                return saved
            delegate = mock.Mock(side_effect=summary)
            answer = self.subject.summarize(result, layout, summary=delegate)
            delegate.assert_called_once_with(result, layout)
            self.assertEqual(answer, {**saved, 'polls_alignment_type': TYPE_META})
            self.assertNotIn('polls_alignment_type', saved)
            self.assertEqual(result, before); self.assertEqual(layout, layout_before)

    def test_type_confirmation_rejects_wrong_containers_base64_utf8_and_noncallable(self):
        result, layout = self.packet(); delegate = mock.Mock(side_effect=AssertionError('Invalid type delegated'))
        bad = [None, [], {'commands': []}, {'commands': result['commands'][:3]},
               {'commands': result['commands'] + [{}]}, {'commands': [None] * 4}]
        for encoded in ('@@', 'YQ===', base64.b64encode(b'\xff').decode()):
            value = copy.deepcopy(result); value['commands'][3]['stdout_base64'] = encoded; bad.append(value)
        for value in bad:
            with self.subTest(kind=type(value).__name__):
                self.reject(lambda: self.subject.summarize(value, layout, summary=delegate))
        delegate.assert_not_called()
        self.reject(lambda: self.subject.summarize(result, layout, summary=None))

    def test_type_confirmation_requires_exact_unique_contiguous_current_type_block(self):
        result, layout = self.packet(); original = self.support.stream_text(result, 3)
        bad = [original.replace(TYPE_BLOCK, ''), original + '\n' + TYPE_BLOCK + '\n',
               original + '\nSUMOX_LAYOUT report_.polls\n',
               original.replace('type = unsigned int\nSUMOX_SIZE bool', 'type = unsigned long\nSUMOX_SIZE bool'),
               original.replace(TYPE_BLOCK, TYPE_BLOCK.replace('unsigned int', 'uint32_t')),
               original.replace(TYPE_BLOCK, TYPE_BLOCK.replace('unsigned int', 'const unsigned int')),
               original.replace(TYPE_BLOCK, TYPE_BLOCK.replace('type =', 'type  =')),
               original.replace(TYPE_BLOCK, TYPE_BLOCK.replace('\nSUMOX_SIZE', '\n\nSUMOX_SIZE')),
               original.replace(TYPE_BLOCK, TYPE_BLOCK.replace('\nSUMOX_SIZE', '\nunexpected\nSUMOX_SIZE')),
               original.replace(TYPE_BLOCK, TYPE_BLOCK.replace('SUMOX_SIZE bool', 'SUMOX_ALIGN bool'))]
        for text in bad:
            value = copy.deepcopy(result); self.support.replace_text(value, 3, text)
            delegate = mock.Mock(side_effect=AssertionError('Unconfirmed type delegated'))
            with self.subTest(text=text[-110:]):
                self.reject(lambda: self.subject.summarize(value, layout, summary=delegate))
                delegate.assert_not_called()

    def test_complete_numeric_summary_keeps_normalization_observes_alignment_and_preserves_raw(self):
        reader = self.loaded()
        for token, alignment in (('1024', 2), ('0x400', 4), ('0x0400', 8)):
            result, layout = self.packet(token)
            text = self.support.stream_text(result, 3)
            self.support.replace_text(result, 3, text.replace('SUMOX_ALIGN report_.polls\n$1 = 4',
                                       'SUMOX_ALIGN report_.polls\n$1 = ' + str(alignment)))
            before, layout_before = copy.deepcopy(result), copy.deepcopy(layout)
            answer = reader.summarize(result, layout)
            self.assertEqual(answer['status'], 'STATIC_ABI_OBSERVED')
            self.assertEqual(answer['polls_alignment_type'], TYPE_META)
            self.assertEqual(answer['alignments']['report_.polls'], alignment)
            self.assertEqual(answer['windows']['report_.polls']['offset'], 248)
            self.assertEqual(answer['readelf_size_projection']['original_token'], token)
            self.assertEqual(result, before); self.assertEqual(layout, layout_before)

    def test_type_success_does_not_bypass_existing_numeric_and_BSS_guards(self):
        reader = self.loaded(); result, layout = self.packet(); text = self.support.stream_text(result, 3)
        for changed in (text.replace('SUMOX_ALIGN report_.polls\n$1 = 4', 'SUMOX_ALIGN report_.polls\n$1 = 3'),
                        text.replace('SUMOX_SIZE report_.polls\n$1 = 4', 'SUMOX_SIZE report_.polls\n$1 = 0'),
                        text.replace('SUMOX_OFFSET report_.polls\n$2 = 248', 'SUMOX_OFFSET report_.polls\n$2 = 1024')):
            value = copy.deepcopy(result); self.support.replace_text(value, 3, changed)
            self.reject(lambda: reader.summarize(value, layout))
        short = copy.deepcopy(layout); short['bss_zero']['end'] = 0x20020001
        self.reject(lambda: reader.summarize(result, short))

    def test_summary_primary_exception_is_not_replaced_or_retried(self):
        result, layout = self.packet(); error = RuntimeError('saved normalized summary failure')
        delegate = mock.Mock(side_effect=error)
        with self.assertRaises(RuntimeError) as caught: self.subject.summarize(result, layout, summary=delegate)
        self.assertIs(caught.exception, error); delegate.assert_called_once_with(result, layout)

    def test_real_prepare_keeps_file_only_command_counts_and_bound_without_claim(self):
        reader, owner = self.support.LifecycleContract.prepared_owner(self)
        value = owner.prepare()
        self.assertEqual(value['status'], 'STATIC_ABI_CHECKED')
        self.assertEqual(value['file_commands'], 4); self.assertLessEqual(value['command_units'], 30000)
        self.assertEqual(len(owner.remote_pins), 12); self.assertFalse(owner.output.exists())
        self.assertIn('D194_STATIC_FILE_ONLY_ABI02', owner.program)
        self.assertEqual(owner.remote, SCOPE); self.assertEqual(owner.build_path, OWNER + '/build')
        self.assertIn('p/d alignof(unsigned int)', owner.commands[3])
        self.assertFalse(owner.claimed)

    def test_execute_saves_original_raw_then_new_summary_and_independent_closure(self):
        _, owner, result, writes = self.executing_owner(); before = copy.deepcopy(result)
        closure = owner.execute()
        self.assertEqual([name for name, _ in writes], ['inputs.json', 'result.json', 'abi.json', 'local_result.json'])
        self.assertEqual(writes[1][1], before)
        self.assertEqual(writes[2][1]['polls_alignment_type'], TYPE_META)
        self.assertTrue(writes[2][1]['readelf_size_projection']['changed'])
        self.assertEqual(result, before); self.assertEqual(closure['status'], 'STATIC_ABI_OBSERVED')
        owner.direct.assert_called_once_with(owner.bootstrap, 'file-abi', 400)
        owner.local.assert_called_once_with()

    def test_old_scope_nonempty_stderr_and_current_type_failure_keep_failed_owner_closed(self):
        for reason in ('scope', 'stderr', 'type'):
            _, owner, result, writes = self.executing_owner()
            if reason == 'scope': result['scope'] = 'D194_STATIC_FILE_ONLY_ABI'
            elif reason == 'stderr':
                result['commands'][3].update(stderr_bytes=1, stderr_base64='eA==')
            else:
                text = self.support.stream_text(result, 3).replace('type = unsigned int', 'type = unsigned long')
                self.support.replace_text(result, 3, text)
            owner.direct.return_value = (types.SimpleNamespace(stdout=json.dumps(result), stderr=''), None)
            self.reject(owner.execute)
            self.assertEqual(writes[1][1], result)
            self.assertNotIn('abi.json', [name for name, _ in writes])
            self.assertEqual(writes[-1][1]['status'], 'FAILED')
            owner.local.assert_called_once_with(); self.assertTrue(owner.output.exists())

    def test_new_owner_cannot_be_reused_and_closing_errors_preserve_primary(self):
        _, owner, _, writes = self.executing_owner(); owner.output.mkdir()
        self.reject(owner.execute); owner.direct.assert_not_called(); self.assertFalse(writes)
        _, owner, _, writes = self.executing_owner()
        primary, close = RuntimeError('file child failure'), OSError('closure write failure')
        owner.direct.side_effect = primary; owner.local.side_effect = ValueError('local closure failure')
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
