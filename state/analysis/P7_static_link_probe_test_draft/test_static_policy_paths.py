# Independently checks literal one-pass substitution in the static policy contract.
# Rejects recursive command-path expansion while preserving original frozen tests.
# Run only by the coordinator after freeze_paths.json binds this supplement.
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys
import unittest


ROOT = Path(__file__).resolve().parents[3]
DRAFT = Path(__file__).resolve().parent
RAW = ROOT / 'state/analysis/P7_static_link_probe_raw'
TOKENS = re.compile(r'@(BUILD_PATH|DATA_DIR)@')
NORMAL_BUILD = '/synthetic/path-literals/new-build'
NORMAL_DATA = '/synthetic/path-literals/arduino-data'


def literal_once(text, build, data):
    values = {'BUILD_PATH': build, 'DATA_DIR': data}
    return TOKENS.sub(lambda match: values[match[1]], text)


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class StaticPolicyPathLiterals(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        freeze = json.loads((DRAFT / 'freeze_paths.json').read_text(encoding='utf-8'))
        if freeze.get('status') != 'FROZEN_FOR_AUTHORIZED_HOST_TEST':
            raise RuntimeError('Coordinator must freeze this supplement before execution')
        for relative, expected in freeze['inputs_sha256'].items():
            actual = hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()
            if actual != expected:
                raise RuntimeError('Frozen path-regression input changed: ' + relative)
        cls.support = load_module('independent_static_policy_public_test_helpers',
                                  DRAFT / 'test_static_policy.py')
        cls.reference = json.loads((RAW / 'static_reference.json').read_text(encoding='utf-8'))
        sys.path.insert(0, str(ROOT / 'tools'))
        sys.path.insert(0, str(RAW))
        cls.policy = load_module('independent_static_policy_paths_under_test', RAW / 'static_policy.py')
        cls.validators = ('validate_preflight', 'validate_compile_result')

    def expected(self, build, data):
        # Existing helpers supply metadata only; overwrite every command from this oracle.
        result = self.support.public_properties(self.reference, build, data)
        result.update({key: literal_once(value, build, data)
                       for key, value in self.reference.items()})
        return result

    def envelope(self, build, data, commands=None):
        result = self.support.public_envelope(self.reference, build, data)
        properties = self.expected(build, data)
        if commands is not None:
            properties.update(commands)
        result['builder_result']['build_properties'] = [
            key + '=' + value for key, value in properties.items()]
        return result

    def call(self, name, envelope, build, data):
        with self.support.io_tripwires():
            return getattr(self.policy, name)(json.dumps(envelope), build_path=build, data_dir=data)

    def accept(self, build, data):
        envelope = self.envelope(build, data)
        for name in self.validators:
            with self.subTest(validator=name, build=build, data=data):
                self.assertEqual(self.call(name, envelope, build, data), self.expected(build, data))

    def reject_commands(self, build, data, commands):
        self.assertTrue(any(commands[key] != self.expected(build, data)[key] for key in commands))
        envelope = self.envelope(build, data, commands)
        self.assertEqual(envelope['builder_result']['build_path'], build)
        self.assertIn('build.path=' + build, envelope['builder_result']['build_properties'])
        for name in self.validators:
            with self.subTest(validator=name, build=build, data=data):
                with self.assertRaises(ValueError):
                    self.call(name, envelope, build, data)

    def test_one_pass_oracle_preserves_literal_inserted_tokens(self):
        build = '/literal/@DATA_DIR@/@BUILD_PATH@/build'
        data = '/literal/@BUILD_PATH@/@DATA_DIR@/data'
        self.assertEqual(literal_once('@BUILD_PATH@|@DATA_DIR@', build, data), build + '|' + data)
        self.assertEqual(literal_once('untouched/path', build, data), 'untouched/path')

    def test_distinct_normal_roots_remain_accepted(self):
        self.accept(NORMAL_BUILD, NORMAL_DATA)
        self.accept('/another/new-build', '/independent/data-root')

    def test_literal_data_token_in_build_root_is_preserved(self):
        for build in ('/literal/@DATA_DIR@/build', '/literal/pre@DATA_DIR@post/build'):
            self.accept(build, NORMAL_DATA)

    def test_literal_build_token_in_data_root_is_preserved(self):
        for data in ('/literal/@BUILD_PATH@/data', '/literal/pre@BUILD_PATH@post/data'):
            self.accept(NORMAL_BUILD, data)

    def test_self_named_tokens_in_path_values_are_preserved(self):
        self.accept('/literal/@BUILD_PATH@/build', NORMAL_DATA)
        self.accept(NORMAL_BUILD, '/literal/@DATA_DIR@/data')

    def test_both_path_roots_can_contain_both_literal_tokens(self):
        self.accept('/literal/@DATA_DIR@/@BUILD_PATH@/build',
                    '/literal/@BUILD_PATH@/@DATA_DIR@/data')

    def test_coherent_build_metadata_cannot_authorize_recursively_expanded_commands(self):
        build, data = '/literal/@DATA_DIR@/build', NORMAL_DATA
        commands = {key: literal_once(literal_once(value, build, data), build, data)
                    for key, value in self.reference.items()}
        self.reject_commands(build, data, commands)

    def test_recursive_single_command_drift_is_rejected_for_either_path_root(self):
        key = 'recipe.c.combine.2.pattern'
        for build, data in (('/literal/@DATA_DIR@/build', NORMAL_DATA),
                            (NORMAL_BUILD, '/literal/@BUILD_PATH@/data')):
            correct = literal_once(self.reference[key], build, data)
            wrong = literal_once(correct, build, data)
            self.assertNotEqual(correct, wrong)
            self.reject_commands(build, data, {key: wrong})


if __name__ == '__main__':
    unittest.main(verbosity=2)
