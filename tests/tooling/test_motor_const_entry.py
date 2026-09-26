# Preserves D199 entry assertions through frozen data-only fixture projections.
# Adds D205 current bindings, fixed projections and stale-owner/closure negatives.
# Independent freeze precedes implementation reads; synthetic instructions are not target semantics.
import ast
import base64
import builtins
import copy
import hashlib
import json
from pathlib import Path
import re
import sys
import types
import unittest
from unittest import mock

ROOT = Path(__file__).absolute().parents[2]
RAW = 'state/analysis/P7_motor_const_compile_raw'
SUBJECT = RAW + '/inspect_static_entry.py'
DERIVATION = RAW + '/entry_fixture_derivation01.json'
DERIVATION_PIN = {'bytes': 40005, 'sha256': '7e699de06f8a37313fb614aedcbfff4d9fb09cfedba6b9bb855135ca84d52918'}
NEW_METHODS = (
    'test_exact_wrapper_reader_parser_recipes_and_unchanged_function_bodies',
    'test_every_projection_occurrence_count_refuses_drift',
    'test_complete_symbol_census_helper_absence_and_all_current_ranges',
    'test_current_inputs_refuse_exact_stale_d199_bytes_before_private_execution',
    'test_current_source_manifest_artifacts_refuse_stale_d199_evidence',
    'test_consumed_d199_owner_and_scope_cannot_be_reused',
    'test_all_thirteen_remote_closures_are_required_with_raw_preservation',
)


def identity(raw):
    return dict(bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest())


def checked(name, pin):
    raw = (ROOT / name).read_bytes()
    if identity(raw) != dict(bytes=pin['bytes'], sha256=pin['sha256']):
        raise AssertionError('D205 independent input differs: ' + name)
    return raw


def data():
    return json.loads(checked(DERIVATION, DERIVATION_PIN))


def project(raw, rows):
    for row in rows:
        old, new = row['old'].encode('ascii'), row['new'].encode('ascii')
        if identity(raw) != row['before'] or raw.count(old) != row['count']:
            raise AssertionError('D205 independent projection count/input differs')
        raw = raw.replace(old, new)
        if identity(raw) != row['after']:
            raise AssertionError('D205 independent projection output differs')
    return raw


def functions(raw):
    lines = raw.splitlines(keepends=True)
    return {node.name: b''.join(lines[node.lineno-1:node.end_lineno])
            for node in ast.parse(raw).body if isinstance(node, ast.FunctionDef)}


def prior_oracle(spec):
    raw = project(checked(spec['historical']['path'], spec['historical']), spec['oracle_steps'])
    if identity(raw) != spec['oracle_projected']:
        raise AssertionError('D205 private historical oracle differs')
    value = types.ModuleType('_d205_private_d199_entry_oracle')
    value.__file__ = str(ROOT / spec['historical']['path'])
    value.__dict__['__builtins__'] = dict(vars(builtins))
    exec(compile(raw, value.__file__, 'exec'), value.__dict__)
    return value


def prepared(case, oracle):
    reader = case.loaded(); owner = reader.StaticEntry(oracle.HEAD)
    owner.compiler.CompileDiagnostic.admission(owner)
    owner.local = mock.Mock(return_value=None)
    owner.output = case.scratch() / 'exclusive-current-entry'
    patch = mock.patch.object(reader.shutil, 'disk_usage', return_value=types.SimpleNamespace(free=268435456))
    patch.start(); case.addCleanup(patch.stop)
    return reader, owner


def additional_cases(oracle, spec):
    class CurrentEntryContract(oracle.EntryContract):
        def test_exact_wrapper_reader_parser_recipes_and_unchanged_function_bodies(self):
            recipe = json.loads(checked(spec['recipe']['path'], spec['recipe']))
            old = checked(recipe['predecessor']['path'], recipe['predecessor'])
            self.assertEqual(len(recipe['ordered_wrapper_substitutions']), 12)
            self.assertEqual([row['count'] for row in recipe['ordered_wrapper_substitutions']], [1] * 12)
            expected = project(old, recipe['ordered_wrapper_substitutions'])
            self.assertEqual(self.raw, expected)
            self.assertEqual(identity(expected), spec['prospective_subject'])
            before, after = functions(old), functions(self.raw)
            self.assertEqual(set(before), set(after))
            for name in before:
                expected_body = before[name]
                if name == 'load_reader':
                    expected_body = expected_body.replace(b'_sumox_d199_entry_abi', b'_sumox_d205_entry_abi')
                    expected_body = expected_body.replace(b'_sumox_d199_entry_parser', b'_sumox_d205_entry_parser')
                self.assertEqual(after[name], expected_body, name)
            abi = functions(self.inputs[oracle.ABI02])
            for name in ('require', '_stamp', '_plain_chain', '_read_handle', 'pinned'):
                self.assertEqual(after[name], abi[name], name)
            for kind, raw in (('reader', self.projected02), ('parser', self.inputs[oracle.PARSER])):
                rows = self.binding['projection'][kind]['steps']
                self.assertEqual(len(rows), 9 if kind == 'reader' else 7)
                expected = project(raw, rows)
                self.assertEqual(getattr(self.subject, 'project_' + kind)(raw), expected)
            rows = self.binding['projection']['parser']['steps']
            self.assertTrue(rows[1]['old'].startswith('RANGES = ('))
            self.assertTrue(rows[2]['old'].startswith('BOUNDS = '))
            self.assertEqual([row['count'] for row in rows], [1] * 7)
            parsed = self.subject.project_parser(self.inputs[oracle.PARSER])
            old_functions, new_functions = functions(self.inputs[oracle.PARSER]), functions(parsed)
            self.assertEqual(set(old_functions), set(new_functions))
            for name, raw in old_functions.items():
                expected = raw
                for row in rows:
                    expected = expected.replace(row['old'].encode(), row['new'].encode())
                self.assertEqual(new_functions[name], expected, name)
            self.assertIn(b'pointer == 0x08100105', new_functions['initializer'])

        def test_every_projection_occurrence_count_refuses_drift(self):
            for kind, raw, name in (('reader', self.projected02, 'READER_REPLACEMENTS'),
                                   ('parser', self.inputs[oracle.PARSER], 'PARSER_REPLACEMENTS')):
                original = getattr(self.subject, name)
                expected = tuple((row['old'].encode(), row['new'].encode(), row['count'])
                                 for row in self.binding['projection'][kind]['steps'])
                self.assertEqual(original, expected)
                for index, row in enumerate(expected):
                    altered = list(original); altered[index] = (row[0], row[1], row[2] + 1)
                    with self.subTest(kind=kind, index=index), mock.patch.object(self.subject, name, tuple(altered)):
                        with self.assertRaisesRegex(ValueError, '^Entry projection occurrence count changed$'):
                            getattr(self.subject, 'project_' + kind)(raw)

        def test_complete_symbol_census_helper_absence_and_all_current_ranges(self):
            result = json.loads(self.inputs[RAW + '/native_abi_static01/result.json'])
            text = base64.b64decode(result['commands'][2]['stdout_base64'], validate=True).decode('ascii')
            rows = re.findall(r'^[ \t]*(\d+):[ \t]+([0-9a-fA-F]+)[ \t]+(\S+)[ \t]+(\S+)[ \t]+(\S+)[ \t]+(\S+)[ \t]+(\S+)(?:[ \t]+(.*?))?[ \t]*$', text, re.M)
            self.assertEqual([int(row[0]) for row in rows], list(range(2299)))
            self.assertEqual(re.findall(r"Symbol table '([^']+)' contains (\d+) entries:", text), [('.symtab', '2299')])
            names = [row[7] for row in rows]
            inventory = self.binding['helper_name_inventory']['helpers']
            for token in ('candidateRate', 'expectedRate', 'expectedPeriod', 'liveRateValid', 'storeSettleSample', 'settleProbeReport'):
                self.assertEqual([name for name in names if token in name], [])
                self.assertEqual(inventory[token]['name_token_rows'], [])
            candidate = '_ZN6motors12_GLOBAL__N_115candidatePeriodEj'
            self.assertEqual([name for name in names if 'candidatePeriod' in name], [candidate])
            self.assertEqual(len(inventory['candidatePeriod']['exact_rows']), 1)
            prior = json.loads(checked(spec['old_binding']['path'], spec['old_binding']))
            labels = [row[0] for row in self.ranges]
            self.assertEqual(labels, [row['label'] for row in prior['ranges'] if row['label'] != 'candidate_rate'] +
                             ['timer_valid', 'bank_valid', 'write_pwm', 'map_channel'])
            self.assertEqual((len(labels), sum(len(row[3]) for row in self.ranges),
                              sum(row[2] - row[1] for row in self.ranges)), (32, 34, 3834))
            expected = spec['current_added_ranges']
            self.assertEqual({row[0]: [row[1], row[2], list(row[3])] for row in self.ranges if row[0] in expected}, expected)
            reader = self.loaded(); commands = reader.queries(types.SimpleNamespace(
                PREFIX='fixed-', gdb=lambda path, expressions: expressions))
            self.assertEqual(len(commands[3]), 65)
            self.assertEqual(commands[3][-1], 'echo SUMOX_ENTRY_END\\n')
            self.assertEqual(commands[3][:-1:2], [f'echo SUMOX_ENTRY_{i:02d}\\n' for i in range(32)])

        def test_current_inputs_refuse_exact_stale_d199_bytes_before_private_execution(self):
            inputs = {**self.inputs, oracle.CONTRACT: self.contract}
            for target, pin in spec['stale_inputs'].items():
                stale = checked(pin['path'], pin)
                self.assertNotEqual(stale, inputs[target])
                root = self.scratch()
                for name, raw in inputs.items():
                    path = root / name; path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_bytes(stale if name == target else raw)
                execute = mock.Mock(side_effect=AssertionError('Stale private execution'))
                self.subject.__dict__['__builtins__']['exec'] = execute
                with self.subTest(target=target):
                    self.reject(lambda: self.subject.load_reader(root=root))
                    execute.assert_not_called()

        def test_current_source_manifest_artifacts_refuse_stale_d199_evidence(self):
            reader, owner = prepared(self, oracle)
            self.assertEqual(owner.source_sha256, spec['source_sha256'])
            self.assertEqual(owner.inputs_path, ROOT / RAW / 'inputs_static.json')
            old = spec['stale_manifest']; path = self.scratch() / 'stale-inputs.json'
            path.write_bytes(checked(old['path'], old))
            stale = reader.StaticEntry(oracle.HEAD); stale.inputs_path = path
            self.reject(lambda: stale.compiler.CompileDiagnostic.admission(stale))
            report = owner.prepare()
            self.assertEqual(report['source_sha256'], spec['source_sha256'])
            self.assertEqual(owner.packet['schema'], 'app-motor-const-static-artifacts-v1')
            old = spec['stale_inputs'][RAW + '/native_static01/artifacts.json']
            self.reject(lambda: owner.compiler.CompileDiagnostic.validate_artifact_reply(owner, checked(old['path'], old).decode()))
            old = spec['stale_outcome']; raw = checked(old['path'], old); original = reader.pinned
            def stale_outcome(path, expected, *args):
                return raw if Path(path) == ROOT / reader.OUTCOME else original(path, expected, *args)
            with mock.patch.object(reader, 'pinned', stale_outcome):
                self.reject(owner.prepare)
            self.assertFalse(owner.output.exists()); self.assertFalse(owner.claimed)

        def test_consumed_d199_owner_and_scope_cannot_be_reused(self):
            reader = self.loaded(); owner = reader.StaticEntry(oracle.HEAD)
            self.assertEqual(reader.SELF, SUBJECT); self.assertEqual(reader.SOURCE, spec['source_sha256'])
            self.assertEqual(reader.OWNER, self.binding['build_owner'])
            self.assertEqual(owner.output, ROOT / RAW / 'native_entry_static01')
            self.assertEqual(owner.remote, '/home/arduino/sumox26_codex_build/app-motor-const-entry-static01')
            owner.source_sha256, owner.boot, owner.claimed = spec['source_sha256'], reader.BOOT, True
            old_path = 'state/analysis/P7_motor_settle_compile_raw/native_entry_static01/result.json'
            owner.git_state = mock.Mock(return_value=(oracle.HEAD, [('??', old_path)]))
            with mock.patch.object(reader, 'pinned', return_value=b'controlled identity'), mock.patch.object(
                    owner.compiler.CompileDiagnostic, 'admission', return_value=None):
                self.reject(owner.local)
                owner.git_state.return_value = (oracle.HEAD, [])
                owner.source_sha256 = spec['old_source_sha256']; self.reject(owner.local)
            for scope in ('D199_STATIC_FILE_ONLY_ENTRY', 'D204_STATIC_FILE_ONLY_ABI', 'D194_STATIC_FILE_ONLY_ENTRY'):
                _, attempt, result, writes = self.executing_owner(); result['scope'] = scope
                attempt.direct.return_value = (types.SimpleNamespace(stdout=json.dumps(result), stderr=''), None)
                self.reject(attempt.execute)
                self.assertEqual(writes[1], ('result.json', result))
                self.assertNotIn('entry.json', [name for name, _ in writes])
                self.assertEqual(writes[-1][1]['status'], 'FAILED'); attempt.local.assert_called_once_with()

        def test_all_thirteen_remote_closures_are_required_with_raw_preservation(self):
            _, owner = prepared(self, oracle); owner.prepare()
            artifact_pins = {self.binding['build_owner'] + '/' + name: row['sha256']
                             for name, row in self.binding['artifact_pins'].items()}
            self.assertEqual({name: owner.remote_pins[name] for name in artifact_pins}, artifact_pins)
            self.assertEqual(len(owner.remote_pins), 12)
            paths = [*owner.remote_pins, 'board_identity']; self.assertEqual(len(paths), 13)
            for failed in [None, *paths]:
                _, attempt, result, writes = self.executing_owner()
                attempt.remote_pins = dict(owner.remote_pins)
                result['final_checks'] = [dict(path=name, status='FAILED' if name == failed else 'PASS') for name in paths]
                before = copy.deepcopy(result)
                attempt.direct.return_value = (types.SimpleNamespace(stdout=json.dumps(result), stderr=''), None)
                with self.subTest(failed=failed):
                    if failed is None:
                        self.assertEqual(attempt.execute()['status'], 'STATIC_ENTRY_OBSERVED')
                        self.assertIn('entry.json', [name for name, _ in writes])
                    else:
                        self.reject(attempt.execute)
                        self.assertNotIn('entry.json', [name for name, _ in writes])
                        self.assertEqual(writes[-1][1]['status'], 'FAILED')
                    self.assertEqual(writes[1], ('result.json', before)); self.assertEqual(result, before)
                    attempt.local.assert_called_once_with()
    return CurrentEntryContract


def load_tests(loader, standard, pattern):
    if not sys.dont_write_bytecode:
        raise RuntimeError('D205 independent tests require Python -B')
    spec = data(); prior = prior_oracle(spec); oracle = prior.private_oracle()
    retained = loader.loadTestsFromTestCase(oracle.EntryContract)
    if retained.countTestCases() != 23:
        raise AssertionError('All 23 historical entry methods required')
    case = additional_cases(oracle, spec)
    suite = unittest.TestSuite([standard, retained])
    suite.addTests(case(name) for name in NEW_METHODS)
    if suite.countTestCases() != 30:
        raise AssertionError('Expected 23 retained and seven current entry methods')
    return suite


if __name__ == '__main__':
    unittest.main(verbosity=2)
