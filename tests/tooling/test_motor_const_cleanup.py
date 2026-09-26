# Retains D200 cleanup guards through independently checked metadata fixtures.
# Adds D206 exact lineage, observed current payload and earlier inode/path refusals.
# No actual credentials, process handles, device calls or cleanup are permitted.
import ast
import hashlib
import json
from pathlib import Path
import sys
import types
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
RAW = 'state/analysis/P7_motor_const_cleanup_raw/'
FIXTURE = RAW + 'cleanup_fixture_derivation01.json'
FIXTURE_PIN = None  # Sealed before any subject inspection or execution.
NEW_METHODS = (
    'test_exact_four_recipe_six_wrapper_steps_preserve_all_other_bytes',
    'test_saved_inventory_binds_current_package_and_current_digest_is_accepted',
    'test_all_earlier_inodes_and_retained_paths_refuse_without_fallback',
)


def identity(raw):
    return dict(bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest())


def checked(name, pin):
    raw = (ROOT / name).read_bytes()
    if identity(raw) != dict(bytes=pin['bytes'], sha256=pin['sha256']):
        raise AssertionError('D206 frozen fixture input differs: ' + name)
    return raw


def project(raw, steps):
    for row in steps:
        old, new = row['old'].encode(), row['new'].encode()
        if identity(raw) != row['before'] or raw.count(old) != row['count']:
            raise AssertionError('D206 independent fixture count/input differs')
        raw = raw.replace(old, new)
        if identity(raw) != row['after']:
            raise AssertionError('D206 independent fixture output differs')
    return raw


def historical(spec):
    raw = project(checked(spec['historical']['path'], spec['historical']), spec['oracle_steps'])
    if identity(raw) != spec['oracle_projected']:
        raise AssertionError('D206 private D200 oracle differs')
    value = types.ModuleType('_d206_private_d200_oracle')
    value.__file__ = str(ROOT / spec['historical']['path'])
    exec(compile(raw, value.__file__, 'exec'), value.__dict__)
    return value


def functions(raw):
    lines = raw.splitlines(keepends=True)
    return {node.name: b''.join(lines[node.lineno-1:node.end_lineno])
            for node in ast.parse(raw).body if isinstance(node, ast.FunctionDef)}


def additional_cases(prior, oracle, spec):
    class CurrentCleanupContract(unittest.TestCase):
        def test_exact_four_recipe_six_wrapper_steps_preserve_all_other_bytes(self):
            derivation = json.loads(checked(spec['recipe']['path'], spec['recipe']))
            for kind, expected_count, function_count in (('recipe', 4, 9), ('wrapper', 6, 14)):
                record = derivation[kind]
                raw = checked(record['input'], derivation['inputs'][record['input']])
                self.assertEqual(len(record['steps']), expected_count)
                expected = project(raw, record['steps'])
                actual = prior.checked(record['proposed_output'])
                self.assertEqual(actual, expected)
                self.assertEqual(identity(actual), record['expected'])
                before, after = functions(raw), functions(actual)
                self.assertEqual(set(before), set(after)); self.assertEqual(len(after), function_count)
                for name, old_body in before.items():
                    new_body = old_body
                    for row in record['steps']:
                        new_body = new_body.replace(row['old'].encode(), row['new'].encode())
                    self.assertEqual(after[name], new_body, name)
            current = prior.checked(RAW + 'cleanup_remoteocd04.py')
            private = project(current, derivation['private_projection']['steps'])
            self.assertEqual(identity(private), derivation['private_projection']['expected'])
            wrapper = oracle.definitions('cleanup_root05.py')
            self.assertEqual(wrapper.PROJECTION_OLD.count(b'continue'), 1)
            self.assertEqual(wrapper.PROJECTION_NEW.count(b'raise'), 1)
            self.assertEqual(wrapper.STAGE, derivation['fresh_owners']['stage'])
            self.assertEqual(derivation['fresh_owners']['result'], wrapper.STAGE + '/result_root05.json')
            self.assertEqual(sum(derivation[k]['expected']['bytes'] for k in ('recipe', 'wrapper')) + 33321, 50660)

        def test_saved_inventory_binds_current_package_and_current_digest_is_accepted(self):
            derivation = json.loads(checked(spec['recipe']['path'], spec['recipe']))
            binding = derivation['current_inventory_binding']; name = binding['receipt']
            receipt = json.loads(checked(name, derivation['inputs'][name]))
            self.assertEqual(receipt['returncode'], 0); self.assertEqual(receipt['stderr'], '')
            self.assertIsNone(receipt['first_error']); self.assertEqual(receipt['local_input_closure'], 'PASS')
            observed = json.loads(receipt['stdout'])
            self.assertEqual(observed['directory_before'], observed['directory_after'])
            self.assertEqual(observed['directory_before'], binding['observed_directory'])
            self.assertEqual((observed['directory_before']['dev'], observed['directory_before']['ino']), (34, 1452))
            self.assertEqual(observed['identity_before'], observed['identity_after'])
            self.assertEqual(observed['identity_before'], binding['board_identity'])
            self.assertIs(observed['exact_three_d201_copies'], True)
            self.assertIs(observed['expected_originals_match'], True)
            self.assertEqual(len(observed['closing_checks']), 5)
            self.assertTrue(all(row['status'] == 'PASS' for row in observed['closing_checks']))
            recipe = oracle.definitions('cleanup_remoteocd04.py')
            expected = {key: (row['bytes'], row['sha256'], row['retained_path']) for key, row in binding['files'].items()}
            self.assertEqual(recipe.PINS, expected)
            self.assertEqual(sum(row[0] for row in expected.values()), 2399928)
            for key, pin in expected.items():
                self.assertEqual((observed['files'][key]['bytes'], observed['files'][key]['sha256']), pin[:2])
                self.assertEqual((observed['originals'][key]['bytes'], observed['originals'][key]['sha256'], observed['originals'][key]['path']), pin)
            pin = recipe.PINS[prior.PAYLOAD_NAME]
            self.assertEqual(pin, (95520, 'e400078166394d0f8ea44b601e9ba2948992c4f263c5c7ee5fb3942433c143d0',
                '/home/arduino/sumox26_codex_build/app-motor-settle-static01/build/app_motor_observe.ino.bin-zsk.bin'))
            digest = mock.Mock(return_value=types.SimpleNamespace(hexdigest=lambda: pin[1]))
            recipe.hashlib = types.SimpleNamespace(sha256=digest)
            recipe.checked_bytes(b'x' * 95520, pin)
            digest.assert_called_once_with(b'x' * 95520)
            self.assertIs(binding['protected_handle_clearance'], False)
            self.assertIs(binding['root05_absence_observed'], False)

        def test_all_earlier_inodes_and_retained_paths_refuse_without_fallback(self):
            for inode in (33, 869, 1172):
                recipe = oracle.definitions('cleanup_remoteocd04.py')
                helper, reads = oracle.MetadataContract.directory_fixture(self, recipe, inode)
                with self.subTest(inode=inode), self.assertRaisesRegex(ValueError, 'Scratch directory identity changed'):
                    recipe.cleanup(helper, 40, {'use_checks': [], 'removed': []})
                recipe.inventory.assert_not_called()
                self.assertEqual(reads, [(pin[2], pin[0]) for pin in recipe.PINS.values()])
            for old_owner in ('app-motor-fault-static01', 'app-motor-observe-static01', 'app-motor-const-static01'):
                recipe = oracle.definitions('cleanup_remoteocd04.py')
                helper, _ = oracle.MetadataContract.directory_fixture(self, recipe, 1452)
                selected = []; old_path = '/home/arduino/sumox26_codex_build/' + old_owner + '/build/' + prior.PAYLOAD_NAME
                def only_alternative(root, path, limit):
                    selected.append(path)
                    if path == prior.PAYLOAD_PATH:
                        raise FileNotFoundError('Current retained package absent')
                    return b'controlled alternative exists' if path == old_path else b'controlled retained support'
                helper.logical_read = only_alternative
                with self.subTest(owner=old_owner), self.assertRaisesRegex(FileNotFoundError, 'Current retained package absent'):
                    recipe.cleanup(helper, 40, {'use_checks': [], 'removed': []})
                self.assertEqual(selected[-1], prior.PAYLOAD_PATH)
                self.assertNotIn(old_path, selected); recipe.inventory.assert_not_called()
    return CurrentCleanupContract


def load_tests(loader, standard, pattern):
    if not sys.flags.isolated or not sys.dont_write_bytecode:
        raise RuntimeError('Independent D206 tests require Python -I -B')
    spec = json.loads(checked(FIXTURE, FIXTURE_PIN)); prior = historical(spec)
    retained = prior.load_tests(loader, unittest.TestSuite(), pattern)
    if retained.countTestCases() != 49:
        raise AssertionError('All 49 historical methods required')
    oracle = prior.private_oracle(); case = additional_cases(prior, oracle, spec)
    suite = unittest.TestSuite([standard, retained])
    suite.addTests(case(name) for name in NEW_METHODS)
    if suite.countTestCases() != 52:
        raise AssertionError('Expected 49 retained and three current cleanup methods')
    return suite


if __name__ == '__main__':
    unittest.main(verbosity=2)
