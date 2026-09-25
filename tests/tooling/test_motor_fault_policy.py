# Tests D163's literal default-inert checked compile route from its public contract.
# Keeps existing recipe, artifact, source and upload boundaries independently scoped.
# Uses synthetic public fixtures only; no board or compiler command is dispatched.
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import unittest
from unittest import mock
from . import test_opp_view_policy as fixture

ROOT = Path(__file__).resolve().parents[2]
SKETCH = 'bench/motor_fault'
PROJECT = 'motor_fault.ino'
FROZEN_INPUTS = {
    'tests/tooling/test_motor_stand_inhibit_policy.py':
        'f379a3a290b8ae84d2bd77ee53015b2eaa8c3dcba570831a9c4b526d9afc505f',
    'tests/tooling/test_opp_view_policy.py':
        '59155eebc8905f9b16ce00ccfa917ec8391237511557b31c8c96a643f220d59a',
    'tests/fixtures/app_build_policy/valid_result.json':
        'dd57c82e856c1510a6dcfa1006f0c0ebbbb7538eb2f35484de4be3a1cd567c5b',
    'tools/p0_inert_sources.json':
        'a1587931afa5f817bf8b93054f384918dc8cd36d4fb71c8f7b083d76e6128802',
}


class MotorFaultPolicyTests(unittest.TestCase):
    def validate(self, document, fqbn=fixture.FQBN, flags=fixture.FLAGS, project=PROJECT):
        return fixture.policy.validate_result(json.dumps(document), fqbn, flags,
                                              fixture.BUILD, project=project)

    def preflight(self, document, fqbn=fixture.FQBN, flags=fixture.FLAGS, project=PROJECT):
        return fixture.policy.validate_preflight(json.dumps(document), fqbn, flags,
            fixture.BUILD, fixture.DATA, project=project)

    def assert_no_target_calls(self, calls):
        for name in ('target', 'require_transport', 'stage', 'remote',
                     'compile_app', 'sync_sources', 'verify_core'):
            calls[name].assert_not_called()

    def test_exact_project_default_profile_passes_both_checked_boundaries(self):
        document = fixture.document(project=PROJECT)
        result = self.validate(document)
        self.assertEqual(result, self.preflight(document))
        self.assertEqual(PROJECT, result['build.project_name'])
        self.assertEqual('wait', result['build.boot_mode'])
        self.assertEqual(PROJECT, fixture.policy.selected_project(
            PROJECT, fixture.FQBN, fixture.FLAGS))

    def test_project_aliases_and_user_selected_unknown_projects_refuse(self):
        for project in ('motor_fault', 'Motor_Fault.ino', '../motor_fault.ino',
                        'motor_fault.ino.other', 'motor_fault.ino\n',
                        'motor_fault.ino;true', '', None, 0, []):
            for boundary in (self.validate, self.preflight):
                with self.subTest(project=project, boundary=boundary.__name__), self.assertRaises(ValueError):
                    boundary(fixture.document(project=PROJECT), project=project)

    def test_match_motor_immediate_and_unknown_macro_profiles_refuse(self):
        bad_flags = ('-DMATCH=1 -DMOTORS_ALLOWED=1', '-DMATCH=1 -DMOTORS_ALLOWED=0',
                     '-DMATCH=0 -DMOTORS_ALLOWED=1', fixture.FLAGS + ' -DOTHER=1', '')
        for fqbn in (fixture.FQBN, fixture.IMMEDIATE):
            for flags in bad_flags:
                with self.subTest(fqbn=fqbn, flags=flags), self.assertRaises(ValueError):
                    fixture.policy.selected_project(PROJECT, fqbn, flags)
        with self.assertRaises(ValueError):
            fixture.policy.selected_project(PROJECT, fixture.IMMEDIATE, fixture.FLAGS)
        for boundary in (self.validate, self.preflight):
            with self.subTest(boundary=boundary.__name__), self.assertRaises(ValueError):
                boundary(fixture.document(True, PROJECT), fqbn=fixture.IMMEDIATE)

    def test_every_effective_project_reference_is_specialized_and_mixed_names_refuse(self):
        original = fixture.document(project=PROJECT)
        changed = 0
        for index, value in enumerate(fixture.entries(original)):
            if PROJECT not in value:
                continue
            changed += 1
            for other in ('motor_stand.ino', 'app.ino', 'motor_fault_other.ino'):
                bad = copy.deepcopy(original)
                fixture.entries(bad)[index] = value.replace(PROJECT, other)
                for boundary in (self.validate, self.preflight):
                    with self.subTest(index=index, other=other, boundary=boundary.__name__), self.assertRaises(ValueError):
                        boundary(bad)
        self.assertGreaterEqual(changed, 6)

    def test_effective_recipe_changes_missing_commands_and_extra_hooks_refuse(self):
        original = fixture.document(project=PROJECT)
        selected = [i for i, value in enumerate(fixture.entries(original))
                    if value.startswith(('recipe.', 'compiler.')) and value.split('=', 1)[1]
                    and ('.pattern=' in value or '.cmd=' in value)]
        self.assertGreaterEqual(len(selected), 10)
        for index in selected:
            for action in ('change', 'remove'):
                bad = copy.deepcopy(original)
                if action == 'change':
                    fixture.entries(bad)[index] += ' unreviewed'
                else:
                    fixture.entries(bad).pop(index)
                for boundary in (self.validate, self.preflight):
                    with self.subTest(index=index, action=action, boundary=boundary.__name__), self.assertRaises(ValueError):
                        boundary(bad)
        for entry in ('recipe.hooks.prebuild.99.pattern=unexpected-command',
                      'recipe.c.combine.99.pattern=unexpected-command',
                      'compiler.cpp.extra_flags.other=-DUNREVIEWED=1'):
            bad = copy.deepcopy(original)
            fixture.entries(bad).append(entry)
            for boundary in (self.validate, self.preflight):
                with self.subTest(entry=entry, boundary=boundary.__name__), self.assertRaises(ValueError):
                    boundary(bad)

    def test_unsuccessful_compile_upload_claim_and_external_libraries_refuse(self):
        for key, value in (('success', False), ('success', 1), ('error', 'compile failed'),
                           ('upload_result', {'success': True}), ('compiler_err', [])):
            bad = fixture.document(project=PROJECT)
            bad[key] = value
            with self.subTest(key=key, value=value), self.assertRaises(ValueError):
                self.validate(bad)
        for libraries in ([{'name': 'Arduino_RouterBridge'}], ['Unexpected'], None, {}, '', 0):
            bad = fixture.document(project=PROJECT)
            bad['builder_result']['used_libraries'] = libraries
            with self.subTest(libraries=libraries), self.assertRaises(ValueError):
                self.validate(bad)

    def test_checked_artifact_hashes_use_all_four_literal_project_outputs(self):
        properties = self.validate(fixture.document(project=PROJECT))
        installed = fixture.policy.installed_pins(fixture.DATA)
        artifacts = [fixture.BUILD + '/' + PROJECT + suffix
                     for suffix in ('.elf', '_debug.elf', '_temp.elf')]
        artifacts.append(fixture.ARTIFACTS + '/' + PROJECT + '.elf-zsk.bin')
        expected = {**installed, **dict.fromkeys(artifacts, '1' * 64)}

        def remote(target, command, capture):
            self.assertEqual('fixture-board', target)
            self.assertTrue(capture)
            self.assertEqual(['sha256sum', '--'], command[:2])
            self.assertEqual(set(expected), set(command[2:]))
            return fixture.SimpleNamespace(stdout=''.join(
                expected[path] + '  ' + path + '\n' for path in command[2:]))

        result = fixture.policy.verify_files(remote, 'fixture-board', properties,
                                             fixture.BUILD, fixture.ARTIFACTS)
        self.assertEqual(expected, result)

    def test_missing_empty_or_wrong_project_artifacts_refuse(self):
        properties = self.validate(fixture.document(project=PROJECT))
        installed = fixture.policy.installed_pins(fixture.DATA)
        artifacts = [fixture.BUILD + '/' + PROJECT + suffix
                     for suffix in ('.elf', '_debug.elf', '_temp.elf')]
        artifacts.append(fixture.ARTIFACTS + '/' + PROJECT + '.elf-zsk.bin')
        for artifact in artifacts:
            for kind in ('missing', 'empty', 'wrong-name'):
                def remote(target, command, capture):
                    lines = []
                    for path in command[2:]:
                        digest = installed.get(path, '1' * 64)
                        if path == artifact:
                            if kind == 'missing':
                                continue
                            if kind == 'empty':
                                digest = hashlib.sha256(b'').hexdigest()
                            if kind == 'wrong-name':
                                path = path.replace(PROJECT, 'motor_stand.ino')
                        lines.append(digest + '  ' + path + '\n')
                    return fixture.SimpleNamespace(stdout=''.join(lines))
                with self.subTest(artifact=artifact, kind=kind), self.assertRaises(ValueError):
                    fixture.policy.verify_files(remote, 'fixture-board', properties,
                                                 fixture.BUILD, fixture.ARTIFACTS)

    def test_literal_default_compile_uses_only_existing_checked_project_route(self):
        for startup in (None, 'default'):
            with self.subTest(startup=startup), fixture.isolated_flash(SKETCH) as calls:
                fixture.board.flash(fixture.args(SKETCH, startup))
                source = '/fixture/root/' + 'a' * 64 + '/motor_fault'
                calls['compile_app'].assert_called_once_with('fixture-board', 'a' * 64,
                    source, '/fixture/root', fixture.FQBN, fixture.FLAGS, 'default', project=PROJECT)
                self.assertEqual([mock.call('fixture-board', ['mkdir', '-p', source])],
                                 calls['remote'].call_args_list)
                calls['verify_inert_source'].assert_not_called()
                calls['verify_runtime_artifacts'].assert_not_called()

    def test_upload_match_immediate_and_foreign_run_refuse_before_target(self):
        cases = []
        for startup in (None, 'default', 'immediate'):
            for match, compile_only in ((False, False), (True, False), (True, True), (False, True)):
                if not match and compile_only and startup != 'immediate':
                    continue
                cases.append(fixture.args(SKETCH, startup, match, compile_only))
        for compile_only in (False, True):
            request = fixture.args(SKETCH, compile_only=compile_only)
            request.run_ui_adc_probe = 'd114-ui-adc-01'
            cases.append(request)
        for request in cases:
            with self.subTest(request=request), fixture.isolated_flash(SKETCH) as calls:
                with self.assertRaises(ValueError):
                    fixture.board.flash(request)
                self.assert_no_target_calls(calls)

    def test_yaml_files_and_live_or_dangling_profile_links_refuse_before_target(self):
        for name in ('sketch.yaml', 'sketch.yml'):
            for kind in ('regular', 'live-link', 'dangling-link'):
                with self.subTest(name=name, kind=kind), fixture.isolated_flash(SKETCH) as calls:
                    folder = fixture.board.ROOT / SKETCH
                    folder.mkdir(parents=True)
                    profile = folder / name
                    if kind == 'regular':
                        profile.write_text('profile: unreviewed', encoding='utf-8')
                    else:
                        destination = fixture.board.ROOT / 'outside-profile'
                        if kind == 'live-link':
                            destination.write_text('profile: unreviewed', encoding='utf-8')
                        profile.symlink_to(destination)
                    with self.assertRaises(ValueError):
                        fixture.board.flash(fixture.args(SKETCH))
                    self.assert_no_target_calls(calls)

    def test_configuration_policy_compile_and_artifact_failure_propagate_exact_exception(self):
        failures = (('setting', ValueError('configuration refusal')),
                    ('compile_app', ValueError('checked policy refusal')),
                    ('compile_app', RuntimeError('checked artifact refusal')),
                    ('compile_app', subprocess.CalledProcessError(
                        43, ['fixture-compile'], output='saved stdout', stderr='saved stderr')))
        for callback, error in failures:
            with self.subTest(callback=callback, error=type(error).__name__), fixture.isolated_flash(SKETCH) as calls:
                calls[callback].side_effect = error
                with self.assertRaises(type(error)) as caught:
                    fixture.board.flash(fixture.args(SKETCH))
                self.assertIs(error, caught.exception)
                if callback == 'setting':
                    calls['compile_app'].assert_not_called()
                else:
                    calls['compile_app'].assert_called_once()
                for call in calls['remote'].call_args_list:
                    self.assertEqual('mkdir', call.args[1][0])
                calls['verify_inert_source'].assert_not_called()
                calls['verify_runtime_artifacts'].assert_not_called()

    def test_no_new_upload_manifest_key_or_historical_fixture_edit(self):
        manifest = json.loads((ROOT / 'tools/p0_inert_sources.json').read_text(encoding='utf-8'))
        self.assertNotIn(SKETCH, manifest)
        for name, digest in FROZEN_INPUTS.items():
            with self.subTest(path=name):
                self.assertEqual(digest, hashlib.sha256((ROOT / name).read_bytes()).hexdigest())


if __name__ == '__main__':
    unittest.main(verbosity=2)
