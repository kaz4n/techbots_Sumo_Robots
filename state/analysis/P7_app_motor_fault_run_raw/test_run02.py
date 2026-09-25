# Projects the frozen D189 oracles onto D190's fixed metadata-only fresh attempt.
# Preserves all 59 original methods and independently checks exact variants and run01 refusal.
# Freeze before Python -B execution; original files stay untouched and inherited RAM seams remain.
import ast
import contextlib
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import types
import unittest
from unittest import mock

HERE = Path(__file__).resolve().parent
OLD_RUN = 'app-motor-fault-21df6ae8-run01'
NEW_RUN = 'app-motor-fault-21df6ae8-run02'
OLD_ADAPTER = 'd796489fc812a509f5ef1edbcd487a4a3afe4adc76960a94ba9c1d3ec075e10a'
NEW_ADAPTER = 'a77fb7d458ceb88f939ce785250d7c49727c56db231a9688890bef808c0c9162'
OLD_CONTRACT = 'state/analysis/P7_app_motor_fault_caller_contract.md'
NEW_CONTRACT = 'state/analysis/P7_app_motor_fault_run02_contract.md'
OLD_REVIEW = 'state/reviews/P7_app_motor_fault_caller_review.md'
NEW_REVIEW = 'state/reviews/P7_app_motor_fault_run02_review.md'
TRANSFORM_PIN = 'ac92332441757b0daf03a6c33a5ef0b8cfb9dad6a3db25d8f74420aa25a99248'
RUN_DECLARATION = ("RUN_ID = '" + OLD_RUN + "'", "RUN_ID = '" + NEW_RUN + "'", 1)
ORACLE_PINS = {
    'test_remote.py': '44f7651b70ffc06697fb2932f4bab01a8ecc8c47d2b31fe779af356596d73bb2',
    'test_actions.py': '2035499ecb3195fdc4bb68f37ada7b88dac0f93abfbc1c70668e6c31d3fe2297',
    'test_run.py': '83c5fea689bac3f5eac0e83cf76137774d8e1a02d401017079e014ea1a0c0d8e',
}
# These expectations are specified independently from run02_transform.json.
SUBJECTS = {
    'remote.py': ('remote_run02.py', OLD_ADAPTER, (RUN_DECLARATION,)),
    'actions.py': ('actions_run02.py',
        '509b15a3e65fa0fee8b215dc55dbad14bf9770f7af30c314d7b2bfc25b83db62',
        (RUN_DECLARATION, (OLD_ADAPTER, NEW_ADAPTER, 1))),
    'run.py': ('run02.py',
        'd0f0e0d0d1cd1de38932eb84d75330cdeafe4986fd38bf28e42edc3b7f82b0f8',
        (RUN_DECLARATION,
         ("'inert_run01_scope.json'", "'inert_run02_scope.json'", 1),
         ("'native_inert_run01'", "'native_inert_run02'", 1),
         ("'preparation.json'", "'preparation_run02.json'", 2),
         ("'run.py'", "'run02.py'", 2),
         ("'actions.py'", "'actions_run02.py'", 3),
         ("'remote.py'", "'remote_run02.py'", 3),
         (repr(OLD_CONTRACT), repr(NEW_CONTRACT), 1),
         (repr(OLD_REVIEW), repr(NEW_REVIEW), 1),
         ("    'test_run.py', 'test_actions.py', 'test_remote.py')) + (",
          "    'test_run.py', 'test_actions.py', 'test_remote.py', 'test_run02.py')) + (", 1))),
}
ORACLE_CHANGES = {
    'test_remote.py': (
        ("RUN = '" + OLD_RUN + "'", "RUN = '" + NEW_RUN + "'", 1),
        ("HERE / 'remote.py'", "HERE / 'remote_run02.py'", 3),
        ("RUN.replace('run01', 'run02')", "RUN.replace('run02', 'run01')", 1)),
    'test_actions.py': (
        ("HERE / 'actions.py'", "HERE / 'actions_run02.py'", 1),
        (OLD_ADAPTER, NEW_ADAPTER, 1)),
    'test_run.py': (
        ("'inert_run01_scope.json'", "'inert_run02_scope.json'", 1),
        ("'native_inert_run01'", "'native_inert_run02'", 1),
        ("'preparation.json'", "'preparation_run02.json'", 1),
        ("'run.py'", "'run02.py'", 3),
        ("'actions.py'", "'actions_run02.py'", 1),
        ("'remote.py'", "'remote_run02.py'", 2),
        (repr(OLD_CONTRACT), repr(NEW_CONTRACT), 1),
        ("'P7_app_motor_fault_caller_review.md'", "'P7_app_motor_fault_run02_review.md'", 1),
        ("'state/analysis/P7_app_motor_fault_run_contract.md', *REVIEW_FILES)",
         "'state/analysis/P7_app_motor_fault_run_contract.md', *REVIEW_FILES, RAW + 'test_run02.py')", 1)),
}
CLASSES = {'test_remote.py': ('Contract', 'Lifecycle'),
           'test_actions.py': ('ActionsContract',), 'test_run.py': ('CallerContract',)}
COUNTS = {'test_remote.py': 26, 'test_actions.py': 13, 'test_run.py': 20}
_PRIVATE_ORACLES = None


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def pinned(name, expected):
    raw = (HERE / name).read_bytes()
    if sha(raw) != expected:
        raise AssertionError('Frozen original changed: ' + name)
    return raw


def substituted(raw, replacements):
    for old, new, count in replacements:
        old, new = old.encode('utf-8'), new.encode('utf-8')
        if raw.count(old) != count:
            raise AssertionError('Metadata substitution count differs: ' + repr(old))
        raw = raw.replace(old, new)
    return raw


def inventory(raw):
    result = []
    for node in ast.parse(raw).body:
        if isinstance(node, ast.ClassDef):
            result.extend(node.name + '.' + method.name for method in node.body
                          if isinstance(method, ast.FunctionDef) and method.name.startswith('test_'))
    return sorted(result)


def private_oracles():
    global _PRIVATE_ORACLES
    if _PRIVATE_ORACLES is not None:
        return _PRIVATE_ORACLES
    if not (sys.platform.startswith('linux') and sys.flags.dont_write_bytecode and sys.dont_write_bytecode):
        raise RuntimeError('Run this frozen driver with Linux Python -B')
    for original, (destination, expected, changes) in SUBJECTS.items():
        if (HERE / destination).read_bytes() != substituted(pinned(original, expected), changes):
            raise AssertionError('Variant differs before subject execution: ' + destination)
    modules = {}
    with contextlib.ExitStack() as stack:
        stack.enter_context(mock.patch.object(subprocess, 'Popen', side_effect=AssertionError('Native child forbidden')))
        stack.enter_context(mock.patch.object(subprocess, 'run', side_effect=AssertionError('Native process forbidden')))
        for filename, expected in ORACLE_PINS.items():
            original = pinned(filename, expected)
            projected = substituted(original, ORACLE_CHANGES[filename])
            if inventory(projected) != inventory(original) or len(inventory(original)) != COUNTS[filename]:
                raise AssertionError('Frozen method inventory changed: ' + filename)
            name = '_d190_private_' + Path(filename).stem
            module = types.ModuleType(name)
            module.__file__ = str(HERE / filename)
            modules[filename] = module
            sys.modules[name] = module
            aliases = {Path(key).stem: value for key, value in modules.items() if key != filename}
            with mock.patch.dict(sys.modules, aliases):
                exec(compile(projected, str(HERE / filename), 'exec'), module.__dict__)
    _PRIVATE_ORACLES = modules
    return modules


class Run02MetadataContract(unittest.TestCase):
    def test_all_frozen_oracles_and_59_methods_are_preserved_privately(self):
        modules = private_oracles()
        total = 0
        for filename, expected in ORACLE_PINS.items():
            raw = pinned(filename, expected)
            self.assertEqual(inventory(raw), inventory(substituted(raw, ORACLE_CHANGES[filename])))
            selected = [getattr(modules[filename], name) for name in CLASSES[filename]]
            count = sum(unittest.defaultTestLoader.loadTestsFromTestCase(item).countTestCases() for item in selected)
            self.assertEqual(count, COUNTS[filename])
            total += count
        self.assertEqual(total, 59)
        remote, actions, caller = (modules[name] for name in ORACLE_PINS)
        self.assertEqual(remote.RUN, NEW_RUN)
        self.assertIs(actions.remote_oracle, remote)
        self.assertIs(caller.remote_oracle, remote)
        self.assertIs(caller.actions_oracle, actions)
        self.assertEqual(len(caller.SCOPE_FILES), 12)
        self.assertTrue({caller.RAW + name for name in ORACLE_PINS} <= set(caller.SCOPE_FILES))
        self.assertIn(caller.RAW + 'test_run02.py', caller.SCOPE_FILES)

    def test_variants_are_exact_independent_metadata_projections_of_pinned_originals(self):
        manifest = json.loads(pinned('run02_transform.json', TRANSFORM_PIN))
        self.assertEqual(manifest['schema'], 'sumox26-d190-run02-transform-v1')
        self.assertEqual(manifest['status'], 'GENERATED_NOT_EXECUTED')
        self.assertEqual((manifest['source_run_id'], manifest['destination_run_id']), (OLD_RUN, NEW_RUN))
        self.assertEqual(len(manifest['files']), 3)
        prefix = 'state/analysis/P7_app_motor_fault_run_raw/'
        for index, (original, (destination, expected, replacements)) in enumerate(SUBJECTS.items()):
            with self.subTest(subject=destination):
                before = pinned(original, expected)
                after = (HERE / destination).read_bytes()
                self.assertEqual(after, substituted(before, replacements))
                row = manifest['files'][index]
                self.assertEqual(row['baseline'], {'path': prefix + original, 'bytes': len(before), 'sha256': expected})
                self.assertEqual(row['destination'], {'path': prefix + destination, 'bytes': len(after), 'sha256': sha(after)})
                self.assertEqual(row['substitutions'], [dict(old=old, new=new, count=count)
                                                        for old, new, count in replacements])
                ast.parse(after)
                if original == 'remote.py':
                    self.assertEqual((len(after), sha(after)), (10518, NEW_ADAPTER))
                if original == 'actions.py':
                    sentinel = b'motor-fault-8f592937-run01'
                    self.assertEqual(after.count(sentinel), before.count(sentinel))
                    self.assertGreater(after.count(sentinel), 0)

    def test_consumed_run01_is_refused_by_run02_remote_actions_and_local_scope(self):
        modules = private_oracles()
        remote_oracle, action_oracle, caller_oracle = (modules[name] for name in ORACLE_PINS)
        with mock.patch.object(subprocess, 'Popen', side_effect=AssertionError('Native child forbidden')), \
             mock.patch.object(subprocess, 'run', side_effect=AssertionError('Native process forbidden')):
            remote = remote_oracle.load(HERE / 'remote_run02.py', '_d190_old_run_remote_refusal')
            dependencies = remote.load_dependencies(remote_oracle.dependency_sources())
            with self.assertRaises(Exception):
                remote.selected_profile(dependencies.capture, OLD_RUN)
            actions = action_oracle.load(HERE / 'actions_run02.py', '_d190_old_run_action_refusal')
            old_bindings = remote_oracle.bindings('upload')
            old_bindings.update(run_id=OLD_RUN, output=remote_oracle.PARENT + '/' + OLD_RUN + '-upload')
            with self.assertRaises(Exception):
                actions.build_command('upload', action_oracle.sources(), old_bindings, action_oracle.ADAPTER_PIN)
            case_type = caller_oracle.CallerContract
            case_type.setUpClass()
            case = case_type('test_scope_shape_source_caller_and_identity_are_exact')
            try:
                case.setUp()
                old_owner = case.root / caller_oracle.RAW / 'native_inert_run01'
                old_owner.mkdir()
                sentinel = old_owner / 'consumed-run01.txt'
                sentinel.write_bytes(b'Preserve consumed old attempt\n')
                case.scope['run_id'] = OLD_RUN
                case.save_scope()
                case.rejected()
                self.assertEqual(sentinel.read_bytes(), b'Preserve consumed old attempt\n')
                self.assertEqual(case.events, [])
            finally:
                case.doCleanups()


def load_tests(loader, unused_suite, unused_pattern):
    """One explicit 62-method suite; do not discover the old files a second time."""
    suite = loader.loadTestsFromTestCase(Run02MetadataContract)
    modules = private_oracles()
    for filename, names in CLASSES.items():
        for name in names:
            suite.addTests(loader.loadTestsFromTestCase(getattr(modules[filename], name)))
    if suite.countTestCases() != 62:
        raise AssertionError('Expected exactly 59 inherited and three D190 methods')
    return suite


if __name__ == '__main__':
    unittest.main(verbosity=2)
