# Checks the D111 literal IMU heading bench extension using fixed public compiler fixtures.
# Coordinator-authored expectations are separately executed and reviewed.
# All transports are substituted; these tests cannot upload or contact a board.
import copy
import json
import subprocess
import unittest
from unittest import mock
from . import test_opp_view_policy as fixture

PROJECT = 'imu_heading.ino'
SKETCH = 'bench/imu_heading'


class ImuHeadingBenchPolicyTests(unittest.TestCase):
    def validate(self, document, immediate=False):
        fqbn = fixture.IMMEDIATE if immediate else fixture.FQBN
        return fixture.policy.validate_result(json.dumps(document), fqbn,
            fixture.FLAGS, fixture.BUILD, project=PROJECT)

    def test_both_profiles_validate_result_preflight_and_selected_artifact_names(self):
        for immediate in (False, True):
            doc = fixture.document(immediate, PROJECT)
            props = self.validate(doc, immediate)
            fqbn = fixture.IMMEDIATE if immediate else fixture.FQBN
            before = fixture.policy.validate_preflight(json.dumps(doc), fqbn,
                fixture.FLAGS, fixture.BUILD, fixture.DATA, project=PROJECT)
            self.assertEqual(props, before)
            pins = fixture.policy.installed_pins(fixture.DATA)
            names = [fixture.BUILD + '/' + PROJECT + suffix for suffix in
                     ('.elf', '_debug.elf', '_temp.elf')]
            names.append(fixture.ARTIFACTS + '/' + PROJECT + '.elf-zsk.bin')
            def remote(board, command, capture):
                self.assertEqual(command, ['sha256sum', '--', *pins, *names])
                return fixture.SimpleNamespace(stdout=''.join(
                    pins.get(name, '1' * 64) + '  ' + name + '\n' for name in command[2:]))
            self.assertEqual(set([*pins, *names]), set(fixture.policy.verify_files(
                remote, 'fixture', props, fixture.BUILD, fixture.ARTIFACTS)))

    def test_every_mixed_project_reference_and_external_library_is_rejected(self):
        good = fixture.document(project=PROJECT)
        entries = fixture.entries(good)
        for index, value in enumerate(entries):
            if PROJECT not in value:
                continue
            for other in ('app.ino', 'opp_view.ino', 'qtr_raw.ino', 'vbat.ino', 'runtime_inert.ino'):
                bad = copy.deepcopy(good)
                fixture.entries(bad)[index] = value.replace(PROJECT, other)
                with self.subTest(index=index, project=other), self.assertRaises(ValueError):
                    self.validate(bad)
        bad = copy.deepcopy(good)
        bad['builder_result']['used_libraries'] = [{'name': 'Arduino_RouterBridge'}]
        with self.assertRaises(ValueError): self.validate(bad)

    def test_only_inert_flags_are_eligible_for_selected_project(self):
        for flags in ('-DMATCH=1 -DMOTORS_ALLOWED=1', '-DMATCH=0 -DMOTORS_ALLOWED=1',
                      '-DMATCH=1 -DMOTORS_ALLOWED=0', ''):
            with self.subTest(flags=flags), self.assertRaises(ValueError):
                fixture.policy.selected_project(PROJECT, fixture.FQBN, flags)
        self.assertEqual(PROJECT, fixture.policy.selected_project(PROJECT,
            fixture.FQBN, fixture.FLAGS))

    def test_both_compile_profiles_route_only_to_checked_build(self):
        for startup, fqbn, mode in ((None, fixture.FQBN, 'default'),
                                   ('default', fixture.FQBN, 'default'),
                                   ('immediate', fixture.IMMEDIATE, 'immediate')):
            with fixture.isolated_flash(SKETCH) as calls:
                fixture.board.flash(fixture.args(SKETCH, startup))
                source = '/fixture/root/' + 'a' * 64 + '/imu_heading'
                calls['compile_app'].assert_called_once_with('fixture-board', 'a' * 64,
                    source, '/fixture/root', fqbn, fixture.FLAGS, mode, project=PROJECT)
                self.assertEqual([mock.call('fixture-board', ['mkdir', '-p', source])],
                                 calls['remote'].call_args_list)
                calls['verify_inert_source'].assert_not_called()
                calls['verify_runtime_artifacts'].assert_not_called()

    def test_match_uploads_and_both_profiles_refuse_before_transport(self):
        for startup in (None, 'default', 'immediate'):
            for match, compile_only in ((True, True), (True, False), (False, False)):
                with fixture.isolated_flash(SKETCH) as calls:
                    with self.assertRaises(ValueError):
                        fixture.board.flash(fixture.args(SKETCH, startup, match, compile_only))
                    for name in ('target', 'require_transport', 'stage', 'remote', 'compile_app'):
                        calls[name].assert_not_called()

    def test_regular_and_dangling_profile_files_refuse_before_transport(self):
        for name in ('sketch.yaml', 'sketch.yml'):
            for link in (False, True):
                with fixture.isolated_flash(SKETCH) as calls:
                    folder = fixture.board.ROOT / SKETCH
                    folder.mkdir(parents=True)
                    path = folder / name
                    if link: path.symlink_to(folder / 'missing-profile')
                    else: path.write_text('profile: unreviewed')
                    with self.assertRaises(ValueError):
                        fixture.board.flash(fixture.args(SKETCH))
                    calls['target'].assert_not_called()
                    calls['compile_app'].assert_not_called()

    def test_checked_build_failure_propagates_without_generic_fallback_or_upload(self):
        for failure in (ValueError('policy refusal'), subprocess.CalledProcessError(2, ['compile'])):
            with fixture.isolated_flash(SKETCH) as calls:
                calls['compile_app'].side_effect = failure
                with self.assertRaises(type(failure)):
                    fixture.board.flash(fixture.args(SKETCH))
                self.assertEqual(1, len(calls['remote'].call_args_list))
                self.assertEqual('mkdir', calls['remote'].call_args.args[1][0])


if __name__ == '__main__':
    unittest.main(verbosity=2)
