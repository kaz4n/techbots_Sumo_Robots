# Checks D099-R1 effective command integrity using the saved actual default receipt.
# Keeps safety metadata intact while independently mutating recipes and build hooks.
# Run with unittest; validators are opaque and these tests never contact a board.
import copy
import hashlib
import importlib
import json
from pathlib import Path
import shutil
import sys
import unittest


PROJECT = Path(__file__).resolve().parents[2]
FIXTURES = PROJECT / 'tests/fixtures/app_build_overrides'
RECEIPT = PROJECT / 'state/analysis/P2_app_build_raw/default_receipt/compile.stdout.json'
FQBN = 'arduino:zephyr:unoq'
FLAGS = '-DMATCH=0 -DMOTORS_ALLOWED=0'
RECEIPT_SHA256 = '416a0f71c229863fc8e4325138b9eae8897bd439979bb4afac84c21a4e08ca69'
DATA_DIR = '/home/arduino/.arduino15'
CONTROLLED_PREFIXES = ('compiler.', 'recipe.', 'build.link', 'build.check',
                       'build.zsk', 'build.postbuild')
CONTROLLED_ALIASES = ('build.compiler_path', 'build.crossprefix', 'build.zip.pattern')


def sample():
    return json.loads(RECEIPT.read_text(encoding='utf-8'))


def properties(document):
    return dict(entry.split('=', 1) for entry in document['builder_result']['build_properties'])


def set_property(document, key, value):
    entries = document['builder_result']['build_properties']
    entries[:] = [entry for entry in entries if entry.split('=', 1)[0] != key]
    entries.append(key + '=' + value)


def relocated(document, data_dir, build_path, match=False, immediate=False):
    result = copy.deepcopy(document)
    previous = result['builder_result']['build_path']
    flags = '-DMATCH=1 -DMOTORS_ALLOWED=1' if match else FLAGS
    for key, value in properties(result).items():
        value = value.replace(previous, build_path).replace(DATA_DIR, data_dir)
        value = value.replace(FLAGS, flags)
        if immediate and key in ('recipe.hooks.objcopy.postobjcopy.1.pattern',
                                 'recipe.hooks.objcopy.postobjcopy.2.pattern'):
            # Pinned platform.txt: three empty argument slots become Immediate.
            value = value.replace('    "', '   -immediate "')
        set_property(result, key, value)
    set_property(result, 'build.boot_mode', 'immediate' if immediate else 'wait')
    set_property(result, 'build.fqbn', FQBN + (':wait_linux_boot=no' if immediate else ''))
    result['builder_result']['build_path'] = build_path
    for kind in ('board_platform', 'build_platform'):
        result['builder_result'][kind]['install_dir'] = (
            result['builder_result'][kind]['install_dir'].replace(DATA_DIR, data_dir))
    return result


class EffectiveAppBuildTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        sys.path.insert(0, str(PROJECT / 'tools'))
        # The author imports only the documented public validator, not its source.
        cls.policy = importlib.import_module('app_build_policy')
        cls.original = sample()
        cls.expected = properties(cls.original)
        cls.build_path = cls.original['builder_result']['build_path']
        cls.cases = json.loads((FIXTURES / 'mutations.json').read_text(encoding='utf-8'))

    def validate(self, document):
        return self.policy.validate_result(json.dumps(document), FQBN, FLAGS, self.build_path)

    def reject_change(self, key, replacement):
        document = copy.deepcopy(self.original)
        self.assertIn(key, self.expected, 'A replacement must target actual receipt evidence')
        self.assertNotEqual(self.expected[key], replacement)
        set_property(document, key, replacement)
        for flag_key in ('compiler.c.extra_flags', 'compiler.cpp.extra_flags'):
            self.assertEqual(FLAGS, properties(document)[flag_key])
        with self.assertRaises(ValueError, msg='Accepted changed effective property: ' + key):
            self.validate(document)

    def check_group(self, group):
        for case in self.cases[group]:
            with self.subTest(property=case['key']):
                value = case.get('value')
                if 'append' in case:
                    value = self.expected[case['key']] + case['append']
                if 'replace' in case:
                    before, after = case['replace']
                    self.assertIn(before, self.expected[case['key']])
                    value = self.expected[case['key']].replace(before, after)
                self.reject_change(case['key'], value)

    def test_D099R1_actual_saved_default_receipt_is_accepted(self):
        self.assertEqual(RECEIPT_SHA256, hashlib.sha256(RECEIPT.read_bytes()).hexdigest())
        self.assertEqual(self.expected, self.validate(self.original))

    def test_D099R1_ordinary_metadata_and_property_order_remain_allowed(self):
        document = copy.deepcopy(self.original)
        set_property(document, 'ordinary.unrelated.property', 'left=middle=right')
        document['builder_result']['build_properties'].reverse()
        self.assertEqual(properties(document), self.validate(document))

    def test_D099R1_reviewer_recipe_drops_controlled_safety_flags(self):
        key = 'recipe.cpp.o.pattern'
        self.assertIn(FLAGS, self.expected[key])
        self.reject_change(key, self.expected[key].replace(FLAGS, '-DMATCH=1 -DMOTORS_ALLOWED=1'))

    def test_D099R1_reviewer_compiler_command_changes(self):
        self.reject_change('compiler.cpp.cmd', 'unreviewed-compiler')

    def test_D099R1_reviewer_existing_prebuild_hook_changes(self):
        self.reject_change('recipe.hooks.prebuild.1.pattern', 'unreviewed-hook')

    def test_D099R1_compile_recipes_cannot_drop_or_override_effective_safety_flags(self):
        for key in ('recipe.c.o.pattern', 'recipe.cpp.o.pattern', 'recipe.S.o.pattern'):
            for replacement in ('', '-DMATCH=1 -DMOTORS_ALLOWED=1',
                                FLAGS + ' -UMOTORS_ALLOWED -DMOTORS_ALLOWED=1'):
                with self.subTest(property=key, replacement=replacement):
                    self.assertIn(FLAGS, self.expected[key])
                    self.reject_change(key, self.expected[key].replace(FLAGS, replacement))

    def test_D099R1_compile_recipes_cannot_redirect_executable_or_source(self):
        for key in ('recipe.c.o.pattern', 'recipe.cpp.o.pattern', 'recipe.S.o.pattern'):
            for before, after in ((self.expected['compiler.path'], '/unreviewed/bin/'),
                                  ('{source_file}', '/unreviewed/source.cpp'),
                                  ('{object_file}', '/unreviewed/object.o')):
                with self.subTest(property=key, before=before):
                    self.assertIn(before, self.expected[key])
                    self.reject_change(key, self.expected[key].replace(before, after))

    def test_D099R1_compiler_tools_flags_and_response_paths_are_constrained(self):
        self.check_group('compiler')

    def test_D099R1_link_commands_and_numbered_recipes_are_constrained(self):
        self.check_group('link')

    def test_D099R1_packaging_and_startup_commands_are_constrained(self):
        self.check_group('startup_and_packaging')

    def test_D099R1_existing_hooks_cannot_be_replaced_or_extended(self):
        for key in ('recipe.hooks.prebuild.1.pattern',
                    'recipe.hooks.linking.postlink.1.pattern',
                    'recipe.hooks.objcopy.postobjcopy.1.pattern',
                    'recipe.hooks.objcopy.postobjcopy.2.pattern'):
            for value in ('unreviewed-hook', self.expected[key] + ' unreviewed-argument'):
                with self.subTest(property=key, value=value):
                    self.reject_change(key, value)

    def test_D099R1_unknown_hooks_and_numbered_recipes_are_rejected(self):
        for key in self.cases['added_commands']:
            with self.subTest(property=key):
                self.assertNotIn(key, self.expected)
                document = copy.deepcopy(self.original)
                set_property(document, key, 'unreviewed-command')
                with self.assertRaises(ValueError, msg='Accepted additional command: ' + key):
                    self.validate(document)

    def test_D099R1_required_command_entries_cannot_be_missing(self):
        for key in self.cases['required_commands']:
            with self.subTest(property=key):
                self.assertIn(key, self.expected)
                document = copy.deepcopy(self.original)
                entries = document['builder_result']['build_properties']
                entries[:] = [entry for entry in entries if entry.split('=', 1)[0] != key]
                with self.assertRaises(ValueError, msg='Accepted missing command: ' + key):
                    self.validate(document)

    def test_D099R1_required_command_entries_cannot_be_empty(self):
        for key in self.cases['required_commands']:
            with self.subTest(property=key):
                self.assertTrue(self.expected[key])
                self.reject_change(key, '')

    def test_D100_every_reviewed_effective_property_cannot_change_or_disappear(self):
        keys = [key for key in self.expected
                if key.startswith(CONTROLLED_PREFIXES) or key in CONTROLLED_ALIASES]
        self.assertEqual(84, len(keys), 'Public D100 reference scope in saved receipt')
        for key in keys:
            for operation in ('replace', 'remove'):
                with self.subTest(property=key, operation=operation):
                    document = copy.deepcopy(self.original)
                    if operation == 'replace':
                        set_property(document, key, self.expected[key] + ' unreviewed')
                    else:
                        entries = document['builder_result']['build_properties']
                        entries[:] = [item for item in entries if item.split('=', 1)[0] != key]
                    with self.assertRaises(ValueError):
                        self.validate(document)

    def test_D100_documented_modes_and_data_build_path_relocations(self):
        for match, immediate in ((False, False), (False, True), (True, True)):
            for data in (DATA_DIR, '/relocated/data path'):
                with self.subTest(match=match, immediate=immediate, data=data):
                    build = '/relocated/build path/native-app-v1/build'
                    document = relocated(self.original, data, build, match, immediate)
                    fqbn = FQBN + (':wait_linux_boot=no' if immediate else '')
                    flags = '-DMATCH=1 -DMOTORS_ALLOWED=1' if match else FLAGS
                    actual = self.validate_at(document, fqbn, flags, build, data)
                    self.assertEqual(properties(document), actual)

    def validate_at(self, document, fqbn, flags, build, data):
        return self.policy.validate_result(json.dumps(document), fqbn, flags, build)


class PreflightAppBuildTests(EffectiveAppBuildTests):
    # Reuse the exact independently derived mutation matrix for the precompile seam.
    def validate(self, document):
        return self.policy.validate_preflight(
            json.dumps(document), FQBN, FLAGS, self.build_path, DATA_DIR)

    def validate_at(self, document, fqbn, flags, build, data):
        return self.policy.validate_preflight(json.dumps(document), fqbn, flags, build, data)

    def test_D100_preflight_requires_expected_resolved_data_root(self):
        with self.assertRaises(ValueError):
            self.policy.validate_preflight(json.dumps(self.original), FQBN, FLAGS,
                                           self.build_path, '/different/data')

    def test_D100_preflight_rejects_incomplete_or_unsuccessful_envelope(self):
        for key, value in (('success', False), ('success', 1), ('error', 'preflight failed'),
                           ('builder_result', None), ('builder_result', {})):
            with self.subTest(key=key, value=value):
                document = copy.deepcopy(self.original)
                document[key] = value
                with self.assertRaises(ValueError):
                    self.validate(document)

    def test_D100_preflight_rejects_duplicate_keys_nonfinite_and_extra_json(self):
        original = json.dumps(self.original)
        for text in ('[]', original + original, '{"success":true,"success":true}',
                     original[:-1] + ',"unexpected":NaN}', 'warning\n' + original):
            with self.subTest(text=text[:50]), self.assertRaises(ValueError):
                self.policy.validate_preflight(text, FQBN, FLAGS, self.build_path, DATA_DIR)


class ResolvedDirectoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        sys.path.insert(0, str(PROJECT / 'tools'))
        cls.policy = importlib.import_module('app_build_policy')

    def test_D100_resolved_normalized_absolute_strings_accept_without_reinterpretation(self):
        for directory in ('/fixture/.arduino15', '/fixture/Arduino', '/data with spaces',
                          '/literal;path'):
            with self.subTest(directory=directory):
                self.assertEqual(directory, self.policy.resolved_directory(
                    ' \n' + json.dumps(directory) + '\t\n'))

    def test_D100_resolved_directory_rejects_wrong_type_malformed_or_multiple_values(self):
        for text in ('', '{}', '[]', 'null', 'true', '0', 'NaN', '"/data" "other"',
                     'warning\n"/data"', '"/data"\nwarning', '"unterminated'):
            with self.subTest(text=text), self.assertRaises(ValueError):
                self.policy.resolved_directory(text)

    def test_D100_resolved_directory_rejects_relative_root_or_unnormalized_strings(self):
        for directory in ('', '/', '.', 'relative/data', '../data', '~/data',
                          'C:/data', '//data', '/data/', '/data//child',
                          '/data/./child', '/data/../child', '/data\nchild',
                          '/data\rchild', '/data\\child', '/data\x00child',
                          '/literal$(path)', '/literal`path`', '/literal"quote',
                          "/literal'quote"):
            with self.subTest(directory=directory), self.assertRaises(ValueError):
                self.policy.resolved_directory(json.dumps(directory))


class PreflightCommandTests(unittest.TestCase):
    def setUp(self):
        from test_tools import ToolContractTests
        self.rig = ToolContractTests('runTest')
        self.rig.setUp()
        self.addCleanup(self.rig.doCleanups)
        self.rig.env['APP_OVERRIDE_BASE_HELPER'] = str(PROJECT / 'tests/tooling/fake_command.py')
        for command in ('arduino-cli', 'sha256sum', 'sh'):
            target = self.rig.remote_bin / command
            shutil.copyfile(FIXTURES / 'fault_command.py', target)
            target.chmod(0o755)

    def compile(self, *options, fault='', changes=None):
        environment = dict(changes or {}, APP_OVERRIDE_FAULT=fault)
        return self.rig.run_tool('app', '--compile-only', *options, changes=environment)

    def assert_precompile_rejection(self, result):
        self.assertNotEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertNotIn('COMPILE command completed', result.stdout)
        self.assertNotIn('APP BUILD CHECKED', result.stdout)
        self.assertEqual([], self.rig.commands('compile'))
        self.rig.assert_no_motion_command()

    def property_queries(self):
        return [event['args'] for event in self.rig.events if event['kind'] == 'properties_query']

    def test_D100_all_modes_preflight_matches_real_argv_and_pins_bracket_compile(self):
        for options in ((), ('--startup', 'default'), ('--startup', 'immediate'), ('--match',)):
            with self.subTest(options=options):
                result = self.compile(*options)
                self.assertEqual(0, result.returncode, result.stdout + result.stderr)
                real, = self.rig.commands('compile')
                query, = self.property_queries()
                self.assertEqual(real, [arg for arg in query if arg != '--show-properties=expanded'])
                self.assertEqual(1, query.count('--show-properties=expanded'))
                self.assertEqual(1, real.count('--json'))
                self.assertNotIn('--show-properties=expanded', real)
                self.rig.assert_no_motion_command()
                self.assert_order_and_paths(real)

    def assert_order_and_paths(self, real):
        events = self.rig.events
        compile_index = next(i for i, event in enumerate(events)
                             if event['kind'] == 'arduino' and event['args'] == real)
        query_index = next(i for i, event in enumerate(events) if event['kind'] == 'properties_query')
        hash_indices = [i for i, event in enumerate(events) if event['kind'] == 'sha256sum']
        self.assertTrue(any(i < query_index for i in hash_indices))
        self.assertLess(query_index, compile_index)
        self.assertTrue(any(i > compile_index for i in hash_indices))
        pre_files = {arg for i in hash_indices if i < compile_index
                     for arg in events[i]['args'] if arg != '--'}
        post_files = {arg for i in hash_indices if i > compile_index
                      for arg in events[i]['args'] if arg != '--'}
        self.assertEqual(18, len(pre_files))
        self.assertTrue(pre_files.issubset(post_files))
        configs = self.rig.commands('config')
        self.assertCountEqual([['config', 'get', 'directories.data', '--json'],
                               ['config', 'get', 'directories.user', '--json']], configs)
        probe, = [event['args'] for event in events if event['kind'] == 'override_execution']
        root = '/fixture/.arduino15/packages/arduino/hardware/zephyr/1.0.0'
        self.assertEqual(['/fixture/.arduino15/packages/platform.txt',
                          '/fixture/Arduino/hardware/platform.txt',
                          root + '/platform.local.txt', root + '/boards.local.txt',
                          real[-1] + '/sketch.yaml', real[-1] + '/sketch.yml'], probe[3:])
        probe_index = next(i for i, event in enumerate(events) if event['kind'] == 'override_execution')
        self.assertLess(probe_index, query_index)

    def test_D100_malformed_resolved_directories_stop_before_properties_or_compile(self):
        for which in ('data', 'user'):
            for defect in ('relative', 'empty', 'malformed', 'object', 'multiple', 'null', 'nonzero'):
                with self.subTest(directory=which, defect=defect):
                    result = self.compile(fault='directory_' + which + '_' + defect)
                    self.assert_precompile_rejection(result)
                    self.assertEqual([], self.property_queries())

    def test_D100_each_global_local_and_remote_profile_file_stops_before_preflight(self):
        for index in range(6):
            with self.subTest(path_index=index):
                result = self.compile(fault='override_file_' + str(index))
                self.assert_precompile_rejection(result)
                self.assertEqual([], self.property_queries())
                self.assertIn('Unreviewed app override:', result.stderr)

    def test_D100_each_dangling_override_or_remote_profile_symlink_is_not_absence(self):
        for index in range(6):
            with self.subTest(path_index=index):
                result = self.compile(fault='override_link_' + str(index))
                self.assert_precompile_rejection(result)
                self.assertEqual([], self.property_queries())
                self.assertIn('Unreviewed app override:', result.stderr)

    def test_D100_precompile_pin_failures_stop_before_properties_or_compile(self):
        for fault in ('prepin_changed', 'prepin_missing', 'prepin_malformed'):
            with self.subTest(fault=fault):
                self.assert_precompile_rejection(self.compile(fault=fault))
                self.assertEqual([], self.property_queries())
                self.assertTrue(any(event['kind'] == 'sha256sum' for event in self.rig.events))

    def test_D100_malformed_failed_or_changed_properties_stop_before_real_compile(self):
        for defect in ('malformed', 'nonzero', 'unsuccessful', 'recipe', 'compiler',
                       'hook', 'new_hook', 'numbered_link', 'missing_recipe', 'data_root'):
            with self.subTest(defect=defect):
                self.assert_precompile_rejection(self.compile(fault='preflight_' + defect))
                self.assertEqual(1, len(self.property_queries()))

    def test_D100_preflight_stdout_stderr_failure_evidence_is_retained_separately(self):
        result = self.compile(fault='preflight_failure')
        self.assert_precompile_rejection(result)
        self.assertEqual(1, len(self.property_queries()))
        files = [path.read_text(encoding='utf-8')
                 for path in (self.rig.root / 'build/app-receipts').rglob('*') if path.is_file()]
        expected = '{"success":false,"error":"retained preflight failure",' \
                   '"compiler_out":"retained preflight inner stdout\\n",' \
                   '"compiler_err":"retained preflight inner stderr\\n"}\n'
        self.assertIn(expected, files)
        self.assertIn('retained preflight outer stderr\n', files)
        self.assertNotIn(expected + 'retained preflight outer stderr\n', files)

    def test_D100_local_sketch_profiles_fail_before_transport_lookup(self):
        for filename in ('sketch.yaml', 'sketch.yml'):
            with self.subTest(filename=filename):
                path = self.rig.root / 'src/app' / filename
                path.write_text('default_profile: unreviewed\n')
                try:
                    result = self.compile(changes={'SUMO_SSH_TARGET': None,
                                                   'SUMO_TRANSPORT': 'invalid'})
                    self.assert_precompile_rejection(result)
                    self.assertEqual([], self.rig.events)
                    self.assertNotIn('SUMO_SSH_TARGET', result.stdout + result.stderr)
                    self.assertIn('sketch', (result.stdout + result.stderr).lower())
                finally:
                    path.unlink()


if __name__ == '__main__':
    unittest.main()
