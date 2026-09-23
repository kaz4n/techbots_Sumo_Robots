# Checks D099 app build identity, strict result parsing, and compile/upload boundaries.
# Keeps independent contract expectations separate from opaque production tooling.
# Run with Python unittest under WSL; all transport and compile results are synthetic.
import importlib
import json
from pathlib import Path
import shutil
import sys
import unittest


PROJECT = Path(__file__).resolve().parents[2]
FIXTURES = PROJECT / 'tests/fixtures/app_build_policy'
FQBN = 'arduino:zephyr:unoq'
FLAGS = '-DMATCH=0 -DMOTORS_ALLOWED=0'
BUILD_PATH = '/fixture/native-app-v1/source/default/run-one/build'
CLI = 'arduino-cli  Version: 1.5.1 Commit: 01f3d4f2b Date: 2026-06-05T10:22:11Z\n'
EXTRA_FLAGS = ('compiler.c.elf.extra_flags', 'compiler.S.extra_flags',
               'build.extra_flags', 'build.extra_ldflags', 'compiler.ldflags',
               'compiler.libraries.ldflags')


def sample():
    return json.loads((FIXTURES / 'valid_result.json').read_text(encoding='utf-8'))


def properties(document):
    return document['builder_result']['build_properties']


def set_property(document, key, value):
    entries = properties(document)
    # Deliberate mode changes also update saved expanded commands. Boot metadata
    # stays independent so the existing final mismatched-boot negative stays real.
    current = dict(entry.split('=', 1) for entry in entries)
    old = current.get(key, '')
    if key in ('compiler.c.extra_flags', 'compiler.cpp.extra_flags') and old:
        entries[:] = [entry.replace(old, value) if entry.startswith('recipe.') else entry
                      for entry in entries]
    if key == 'build.fqbn':
        old_boot = '-immediate' if 'wait_linux_boot=no' in old else ''
        new_boot = '-immediate' if 'wait_linux_boot=no' in value else ''
        entries[:] = [entry.replace('/zephyr-sketch-tool"   ' + old_boot + ' ',
                                   '/zephyr-sketch-tool"   ' + new_boot + ' ')
                      if entry.startswith('recipe.hooks.objcopy.postobjcopy.') else entry
                      for entry in entries]
    entries[:] = [entry for entry in entries if entry.split('=', 1)[0] != key]
    entries.append(key + '=' + value)


class AppBuildParserTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        sys.path.insert(0, str(PROJECT / 'tools'))
        # Import public validators as opaque code; do not inspect implementation.
        cls.policy = importlib.import_module('app_build_policy')

    def validate(self, document, fqbn=FQBN, flags=FLAGS, path=BUILD_PATH):
        return self.policy.validate_result(json.dumps(document), fqbn, flags, path)

    def reject(self, document):
        with self.assertRaises(ValueError):
            self.validate(document)

    def test_D099_pinned_cli_accepts_surrounding_whitespace(self):
        for text in (CLI, CLI.strip(), '\n \t' + CLI + ' \n'):
            with self.subTest(text=text):
                self.assertIsNone(self.policy.validate_cli(text))

    def test_D099_cli_wrong_missing_or_ambiguous_identity_is_rejected(self):
        cases = ('', '{}', CLI.replace('1.5.1', '1.5.2'),
                 CLI.replace('01f3d4f2b', '01f3d4f2c'),
                 CLI.replace('Commit: 01f3d4f2b ', ''),
                 CLI.replace('Version: 1.5.1 ', ''),
                 CLI.replace('Date: 2026-06-05T10:22:11Z', ''),
                 CLI + CLI, 'unverified\n' + CLI, CLI + 'unverified')
        for text in cases:
            with self.subTest(text=text), self.assertRaises(ValueError):
                self.policy.validate_cli(text)

    def test_D099_omitted_and_empty_libraries_accept_after_complete_envelope(self):
        for explicit in (False, True):
            doc = sample()
            if explicit:
                doc['builder_result']['used_libraries'] = []
            actual = self.validate(doc)
            self.assertEqual(dict(entry.split('=', 1) for entry in properties(doc)), actual)
            self.assertEqual('left=middle=right', actual['ordinary.unrelated.property'])

    def test_D099_default_immediate_and_match_properties_are_distinct(self):
        for match, immediate in ((False, False), (False, True), (True, True)):
            doc = sample()
            fqbn = FQBN + (':wait_linux_boot=no' if immediate else '')
            flags = f'-DMATCH={int(match)} -DMOTORS_ALLOWED={int(match)}'
            for key, value in (('build.fqbn', fqbn), ('compiler.c.extra_flags', flags),
                               ('compiler.cpp.extra_flags', flags),
                               ('build.boot_mode', 'immediate' if immediate else 'wait')):
                set_property(doc, key, value)
            self.assertEqual(fqbn, self.validate(doc, fqbn, flags)['build.fqbn'])
            set_property(doc, 'build.boot_mode', 'wait' if immediate else 'immediate')
            with self.assertRaises(ValueError):
                self.validate(doc, fqbn, flags)

    def test_D099_optional_output_strings_errors_and_upload_envelope(self):
        for key in ('compiler_out', 'compiler_err', 'upload_result'):
            doc = sample()
            del doc[key]
            self.validate(doc)
        doc = sample()
        doc['error'] = ''
        self.validate(doc)
        for key in ('compiler_out', 'compiler_err', 'error'):
            for value in (None, False, 0, [], {}):
                with self.subTest(key=key, value=value):
                    doc = sample()
                    doc[key] = value
                    self.reject(doc)
        doc['error'] = 'build failed despite success marker'
        self.reject(doc)

    def test_D099_result_must_be_one_strict_json_object(self):
        text = json.dumps(sample())
        cases = ('', '[]', 'null', 'true', '1', '"result"', text[:-1],
                 text + text, 'warning\n' + text, text + '\nwarning',
                 '{"success": true,}', text[:-1] + ',"unexpected": NaN}',
                 text[:-1] + ',"unexpected": Infinity}',
                 text[:-1] + ',"unexpected": -Infinity}')
        for value in cases:
            with self.subTest(value=value[:60]), self.assertRaises(ValueError):
                self.policy.validate_result(value, FQBN, FLAGS, BUILD_PATH)
        self.policy.validate_result('\n \t' + text + '\n', FQBN, FLAGS, BUILD_PATH)

    def test_D099_duplicate_keys_are_rejected_at_every_object_depth(self):
        text = json.dumps(sample())
        cases = (text.replace('"success": true', '"success": false, "success": true'),
                 text.replace('"success": true', '"success": true, "success": true'),
                 text.replace('"build_path":', '"build_path": "old", "build_path":'),
                 text.replace('"version": "1.0.0"',
                              '"version": "1.0.0", "version": "1.0.0"', 1),
                 text[:-1] + ', "extra": {"x": 1, "x": 1}}')
        for value in cases:
            with self.subTest(value=value[:100]), self.assertRaises(ValueError):
                self.policy.validate_result(value, FQBN, FLAGS, BUILD_PATH)

    def test_D099_success_must_be_present_boolean_true(self):
        for value in (None, False, 0, 1, 'true', [], {}):
            doc = sample()
            doc['success'] = value
            self.reject(doc)
        doc = sample()
        del doc['success']
        self.reject(doc)

    def test_D099_builder_object_and_fresh_build_path_are_required(self):
        for value in (None, False, 0, '', [], [sample()['builder_result']]):
            doc = sample()
            doc['builder_result'] = value
            self.reject(doc)
        doc = sample()
        del doc['builder_result']
        self.reject(doc)
        for value in (None, False, '', [], {}, BUILD_PATH + '-stale', '/other/build'):
            doc = sample()
            doc['builder_result']['build_path'] = value
            self.reject(doc)
        del doc['builder_result']['build_path']
        self.reject(doc)

    def test_D099_library_omission_cannot_rescue_an_incomplete_envelope(self):
        for doc in ({'success': True}, {'success': True, 'builder_result': {}},
                    {'success': True, 'builder_result': {'used_libraries': []}},
                    {'success': False, 'builder_result': sample()['builder_result']}):
            self.reject(doc)

    def test_D099_any_external_library_or_wrong_library_type_fails(self):
        for value in (None, False, '', {}, 0, [None], [{}], ['RouterBridge'],
                      [{'name': 'Arduino_RouterBridge', 'version': '0.4.3'}],
                      [{'name': 'IndependentPhaseFixture', 'version': '1.0.0'}]):
            with self.subTest(libraries=value):
                doc = sample()
                doc['builder_result']['used_libraries'] = value
                self.reject(doc)

    def test_D099_compile_only_upload_result_is_absent_or_empty_object(self):
        for value in (None, False, 0, '', [], [None], {'success': True}, {'port': ''}):
            doc = sample()
            doc['upload_result'] = value
            self.reject(doc)

    def test_D099_both_platforms_require_exact_id_version_and_absolute_root(self):
        for key in ('board_platform', 'build_platform'):
            for value in (None, False, 0, '', [], {}):
                doc = sample()
                doc['builder_result'][key] = value
                self.reject(doc)
            for field, values in (('id', ('', 'arduino:avr', None, 1)),
                                  ('version', ('', '1.0.1', None, 1)),
                                  ('install_dir', ('', 'relative/1.0.0', None, 1))):
                for value in values:
                    with self.subTest(platform=key, field=field, value=value):
                        doc = sample()
                        doc['builder_result'][key][field] = value
                        self.reject(doc)
                doc = sample()
                del doc['builder_result'][key][field]
                self.reject(doc)
            doc = sample()
            del doc['builder_result'][key]
            self.reject(doc)

    def test_D099_platform_roots_and_variant_path_must_agree(self):
        for key in ('board_platform', 'build_platform'):
            doc = sample()
            doc['builder_result'][key]['install_dir'] = '/other/zephyr/1.0.0'
            self.reject(doc)
        for key in ('runtime.platform.path', 'build.variant.path', 'compiler.path'):
            for value in ('', 'relative/path', '/other/path', '/tmp/1.0.0'):
                doc = sample()
                set_property(doc, key, value)
                self.reject(doc)

    def test_D099_property_collection_requires_unique_well_formed_strings(self):
        for value in (None, False, '', {}, [], [None], [1], [True], [{}], ['noequals'],
                      ['=empty-key'], ['noequals', 'x=1']):
            doc = sample()
            doc['builder_result']['build_properties'] = value
            self.reject(doc)
        for addition in ('broken', '=value', 0, None, {}, properties(sample())[0],
                         'build.fqbn=arduino:avr:uno', 'ordinary.unrelated.property=new'):
            doc = sample()
            properties(doc).append(addition)
            self.reject(doc)

    def test_D099_each_required_property_missing_or_changed_fails(self):
        required = ('build.fqbn', 'build.core', 'build.variant', 'build.project_name',
                    'runtime.platform.path', 'build.variant.path', 'compiler.path',
                    'runtime.tools.arm-zephyr-eabi-1.0.1.path',
                    'build.library_discovery_phase_flag', 'compiler.c.extra_flags',
                    'compiler.cpp.extra_flags', 'build.link_mode',
                    'build.link_args.dynamic', 'build.boot_mode')
        for key in required:
            for mutation in ('missing', 'changed'):
                with self.subTest(key=key, mutation=mutation):
                    doc = sample()
                    entries = properties(doc)
                    entries[:] = [x for x in entries if x.split('=', 1)[0] != key]
                    if mutation == 'changed':
                        entries.append(key + '=unreviewed')
                    self.reject(doc)

    def test_D099_controlled_safety_flags_cannot_be_overridden_or_appended(self):
        for key in ('compiler.c.extra_flags', 'compiler.cpp.extra_flags'):
            for value in ('', '-DMATCH=1 -DMOTORS_ALLOWED=1',
                          FLAGS + ' -DMOTORS_ALLOWED=1', FLAGS + ' -DOTHER=1',
                          '-DMOTORS_ALLOWED=0 -DMATCH=0'):
                doc = sample()
                set_property(doc, key, value)
                self.reject(doc)
        doc = sample()
        set_property(doc, 'build.library_discovery_phase_flag',
                     '-DARDUINO_LIBRARY_DISCOVERY_PHASE=1')
        self.reject(doc)

    def test_D099_unreviewed_extra_build_or_link_flags_fail(self):
        for key in EXTRA_FLAGS:
            for value in ('-DUNREVIEWED=1', ' ', '-e alternate_entry'):
                with self.subTest(key=key, value=value):
                    doc = sample()
                    set_property(doc, key, value)
                    self.reject(doc)


class AppBuildCommandTests(unittest.TestCase):
    def setUp(self):
        # Reuse only existing isolated executable/transport scaffolding.
        from test_tools import ToolContractTests
        self.rig = ToolContractTests('runTest')
        self.rig.setUp()
        self.addCleanup(self.rig.doCleanups)
        self.rig.env['APP_POLICY_BASE_HELPER'] = str(PROJECT / 'tests/tooling/fake_command.py')
        for command in ('arduino-cli', 'sha256sum'):
            destination = self.rig.remote_bin / command
            shutil.copyfile(FIXTURES / 'fault_command.py', destination)
            destination.chmod(0o755)

    def compile(self, *options, changes=None):
        return self.rig.run_tool('app', '--compile-only', *options, changes=changes)

    def assert_no_success(self, result):
        self.assertNotEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertNotIn('COMPILE command completed', result.stdout)
        self.assertNotIn('APP BUILD CHECKED', result.stdout)

    def assert_compile_boundary(self, result):
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        command, = self.rig.commands('compile')
        self.assertIn('--json', command)
        forbidden = {'upload', 'reset', 'start', 'monitor', '--upload', '--preprocess',
                     '--show-properties', '--only-compilation-database',
                     '--skip-libraries-discovery'}
        self.assertFalse(forbidden & set(command))
        self.assertEqual([], self.rig.commands('upload'))
        self.assertIn('native-app-v1', result.stdout)
        return command

    def test_D099_default_immediate_match_use_exact_fixed_compile_properties(self):
        cases = (((), False, False), (('--startup', 'default'), False, False),
                 (('--startup', 'immediate'), False, True), (('--match',), True, True))
        for options, match, immediate in cases:
            with self.subTest(options=options):
                command = self.assert_compile_boundary(self.compile(*options))
                fqbn = command[command.index('--fqbn') + 1]
                self.assertEqual(FQBN + (':wait_linux_boot=no' if immediate else ''), fqbn)
                props = [command[i + 1] for i, x in enumerate(command)
                         if x == '--build-property']
                flags = f'-DMATCH={int(match)} -DMOTORS_ALLOWED={int(match)}'
                self.assertCountEqual(['compiler.cpp.extra_flags=' + flags,
                                       'compiler.c.extra_flags=' + flags,
                                       'build.library_discovery_phase_flag='
                                       '-DARDUINO_LIBRARY_DISCOVERY_PHASE=0'], props)

    def test_D099_every_app_upload_is_rejected_before_transport_lookup(self):
        for options in ((), ('--match',), ('--startup', 'immediate'),
                        ('--startup', 'default'), ('--match', '--startup', 'immediate')):
            for target in ('app', 'src/app'):
                with self.subTest(target=target, options=options):
                    result = self.rig.run_tool(target, *options,
                        changes={'SUMO_SSH_TARGET': None, 'SUMO_TRANSPORT': 'invalid'})
                    self.assert_no_success(result)
                    self.assertEqual([], self.rig.events)
                    self.assertTrue((result.stdout + result.stderr).strip())
                    self.assertNotIn('SUMO_SSH_TARGET', result.stdout + result.stderr)

    def test_D099_build_and_output_paths_are_fresh_and_outside_sketch(self):
        paths = []
        for options in ((), (), ('--startup', 'immediate'), ('--match',)):
            command = self.assert_compile_boundary(self.compile(*options))
            build = Path(command[command.index('--build-path') + 1])
            output = Path(command[command.index('--output-dir') + 1])
            sketch = Path(command[-1])
            for path in (build, output):
                self.assertTrue(path.is_absolute())
                self.assertIn('native-app-v1', path.parts)
                self.assertFalse(path.is_relative_to(sketch))
            self.assertNotEqual(build, output)
            paths.append((build, output))
        self.assertEqual(len(paths), len(set(paths)))

    def test_D099_bench_commands_keep_original_dependency_behavior(self):
        for options in ((), ('--startup', 'immediate'), ('--match',)):
            result = self.rig.run_tool('bench/p0_matrix', '--compile-only', *options)
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            command, = self.rig.commands('compile')
            self.assertNotIn('--json', command)
            self.assertNotIn('--build-path', command)
            self.assertFalse(any('library_discovery_phase_flag' in x for x in command))
            self.assertNotIn('native-app-v1', ' '.join(command))
            self.assertEqual([], self.rig.commands('upload'))

    def test_D099_arbitrary_flag_or_policy_arguments_never_reach_compile(self):
        for option in ('--build-property', '--extra-flags', '--policy', '--fqbn',
                       '--show-properties', '--skip-libraries-discovery', '--upload'):
            result = self.compile(option, 'unreviewed')
            self.assert_no_success(result)
            self.assertEqual([], self.rig.events)

    def test_D099_compiler_failure_retains_error_and_never_reports_success(self):
        result = self.compile(changes={'APP_POLICY_FAULT': 'compile_failure'})
        self.assert_no_success(result)
        self.assertEqual(43, result.returncode)
        self.assertEqual(1, len(self.rig.commands('compile')))
        self.assertEqual([], self.rig.commands('upload'))
        receipts = self.rig.root / 'build/app-receipts'
        files = [path for path in receipts.rglob('*') if path.is_file()]
        content = [path.read_text(encoding='utf-8') for path in files]
        self.assertIn('retained outer stderr\n', content)
        expected = '{"success":false,"error":"fixture failed","compiler_out":' \
                   '"retained inner stdout\\n","compiler_err":"retained inner stderr\\n"}\n'
        self.assertIn(expected, content)
        self.assertNotIn(expected + 'retained outer stderr\n', content)

    def test_D099_wrong_cli_identity_and_core_stop_before_compilation(self):
        for fault in ('cli_version', 'cli_commit'):
            result = self.compile(changes={'APP_POLICY_FAULT': fault})
            self.assert_no_success(result)
            self.assertEqual([], self.rig.commands('compile'))
        for version in ('', '0.9.0', '1.0.1'):
            result = self.compile(changes={'FAKE_CORE_VERSION': version})
            self.assert_no_success(result)
            self.assertEqual([], self.rig.commands('compile'))

    def test_D099_nonzero_process_rejects_even_successful_json(self):
        result = self.compile(changes={'APP_POLICY_FAULT': 'compile_nonzero_success'})
        self.assert_no_success(result)
        self.assertEqual(43, result.returncode)
        self.assertEqual(1, len(self.rig.commands('compile')))
        self.assertEqual([], self.rig.commands('upload'))

    def test_D099_result_rejection_is_wired_into_real_public_compile_command(self):
        for fault in ('compile_malformed', 'compile_libraries',
                      'compile_property_drift', 'compile_failed_flag'):
            with self.subTest(fault=fault):
                result = self.compile(changes={'APP_POLICY_FAULT': fault})
                self.assert_no_success(result)
                self.assertEqual(1, len(self.rig.commands('compile')))
                self.assertEqual([], self.rig.commands('upload'))

    def test_D099_changed_or_missing_dependency_and_artifact_evidence_fail(self):
        for fault in ('changed_pin', 'missing_pin', 'empty_artifact', 'missing_artifact',
                      'malformed_hash', 'extra_hash', 'reordered_hash', 'hash_wrong_path'):
            with self.subTest(fault=fault):
                result = self.compile(changes={'APP_POLICY_FAULT': fault})
                self.assert_no_success(result)
                self.assertEqual([], self.rig.commands('upload'))
                self.assertTrue(any(event['kind'] == 'sha256sum' for event in self.rig.events))

    def test_D099_success_checks_all_three_elfs_package_and_installed_pins(self):
        command = self.assert_compile_boundary(self.compile())
        build = Path(command[command.index('--build-path') + 1])
        output = Path(command[command.index('--output-dir') + 1])
        requested = [Path(arg) for event in self.rig.events if event['kind'] == 'sha256sum'
                     for arg in event['args'] if arg != '--']
        expected = {build / 'app.ino.elf', build / 'app.ino_debug.elf',
                    build / 'app.ino_temp.elf', output / 'app.ino.elf-zsk.bin'}
        self.assertTrue(expected.issubset(set(requested)))
        installed = {path for path in requested if str(path).startswith('/fixture/.arduino15/')}
        self.assertEqual(18, len(installed))
        calls = [event['args'] for event in self.rig.events if event['kind'] == 'arduino']
        self.assertLess(calls.index(['version']), calls.index(command))


if __name__ == '__main__':
    unittest.main()
