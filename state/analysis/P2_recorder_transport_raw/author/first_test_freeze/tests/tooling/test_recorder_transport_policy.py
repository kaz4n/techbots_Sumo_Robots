"""Test D116's literal default inert compile route from the adopted public seam.

Existing independent policy fixtures supply synthetic compiler/transport results.
The author reads no production tooling body and performs no board action.
"""
import copy
import json
from pathlib import Path
import unittest
from unittest import mock
from . import test_opp_view_policy as fixture

ROOT=Path(__file__).resolve().parents[2]
SKETCH='bench/recorder'
PROJECT='recorder.ino'


class RecorderTransportPolicyTests(unittest.TestCase):
    def validate(self,doc,fqbn=fixture.FQBN,flags=fixture.FLAGS):
        return fixture.policy.validate_result(json.dumps(doc),fqbn,flags,fixture.BUILD,project=PROJECT)

    def test_exact_default_project_has_checked_preflight_and_result(self):
        document=fixture.document(project=PROJECT)
        result=self.validate(document)
        before=fixture.policy.validate_preflight(json.dumps(document),fixture.FQBN,
            fixture.FLAGS,fixture.BUILD,fixture.DATA,project=PROJECT)
        self.assertEqual(before,result)
        self.assertEqual(result['build.project_name'],PROJECT)
        self.assertEqual(fixture.policy.selected_project(PROJECT,fixture.FQBN,fixture.FLAGS),PROJECT)

    def test_immediate_match_motor_and_unknown_macro_variants_refuse(self):
        for fqbn in (fixture.FQBN,fixture.IMMEDIATE):
            for flags in ('-DMATCH=1 -DMOTORS_ALLOWED=1','-DMATCH=1 -DMOTORS_ALLOWED=0',
                          '-DMATCH=0 -DMOTORS_ALLOWED=1',fixture.FLAGS+' -DOTHER=1',''):
                with self.subTest(fqbn=fqbn,flags=flags),self.assertRaises(ValueError):
                    fixture.policy.selected_project(PROJECT,fqbn,flags)
        with self.assertRaises(ValueError):
            fixture.policy.selected_project(PROJECT,fixture.IMMEDIATE,fixture.FLAGS)
        with self.assertRaises(ValueError):
            self.validate(fixture.document(True,PROJECT),fixture.IMMEDIATE)

    def test_mixed_project_effective_recipes_external_library_or_upload_claim_refuse(self):
        original=fixture.document(project=PROJECT)
        for index,entry in enumerate(fixture.entries(original)):
            if PROJECT not in entry: continue
            for other in ('recorder_other.ino','app.ino','ui_adc_probe.ino'):
                bad=copy.deepcopy(original);fixture.entries(bad)[index]=entry.replace(PROJECT,other)
                with self.subTest(index=index,other=other),self.assertRaises(ValueError):self.validate(bad)
        for key,value in (('success',False),('upload_result',{'success':True})):
            bad=copy.deepcopy(original);bad[key]=value
            with self.assertRaises(ValueError):self.validate(bad)
        bad=copy.deepcopy(original);bad['builder_result']['used_libraries']=[{'name':'Arduino_RouterBridge'}]
        with self.assertRaises(ValueError):self.validate(bad)

    def test_default_compile_uses_existing_checked_route_exact_project(self):
        for startup in (None,'default'):
            with self.subTest(startup=startup),fixture.isolated_flash(SKETCH) as calls:
                fixture.board.flash(fixture.args(SKETCH,startup))
                source='/fixture/root/'+'a'*64+'/recorder'
                calls['compile_app'].assert_called_once_with('fixture-board','a'*64,source,
                    '/fixture/root',fixture.FQBN,fixture.FLAGS,'default',project=PROJECT)
                self.assertEqual(calls['remote'].call_args_list,[mock.call('fixture-board',['mkdir','-p',source])])
                calls['verify_inert_source'].assert_not_called();calls['verify_runtime_artifacts'].assert_not_called()

    def test_every_upload_match_immediate_or_foreign_run_option_fails_before_staging(self):
        cases=[]
        for startup in (None,'default','immediate'):
            for match,compile_only in ((False,False),(True,False),(True,True),(False,True)):
                if not match and compile_only and startup!='immediate':continue
                cases.append(fixture.args(SKETCH,startup,match,compile_only))
        for compile_only in (False,True):
            request=fixture.args(SKETCH,compile_only=compile_only);request.run_ui_adc_probe='d114-ui-adc-01'
            cases.append(request)
        for request in cases:
            with self.subTest(request=request),fixture.isolated_flash(SKETCH) as calls:
                with self.assertRaises(ValueError):fixture.board.flash(request)
                for name in ('target','require_transport','stage','remote','compile_app','sync_sources'):
                    calls[name].assert_not_called()

    def test_profiles_including_dangling_symlinks_fail_before_target(self):
        for name in ('sketch.yaml','sketch.yml'):
            for dangling in (False,True):
                with self.subTest(name=name,dangling=dangling),fixture.isolated_flash(SKETCH) as calls:
                    folder=fixture.board.ROOT/SKETCH;folder.mkdir(parents=True);path=folder/name
                    if dangling:path.symlink_to(folder/'missing')
                    else:path.write_text('profile: unreviewed')
                    with self.assertRaises(ValueError):fixture.board.flash(fixture.args(SKETCH))
                    for entry in ('target','require_transport','stage','remote','compile_app'):
                        calls[entry].assert_not_called()

    def test_configuration_or_checked_compile_failure_propagates_without_fallback(self):
        for failure in ('setting','compile_app'):
            with self.subTest(failure=failure),fixture.isolated_flash(SKETCH) as calls:
                calls[failure].side_effect=ValueError('controlled checked refusal')
                with self.assertRaises(ValueError):fixture.board.flash(fixture.args(SKETCH))
                for call in calls['remote'].call_args_list:self.assertEqual(call.args[1][0],'mkdir')
                if failure=='setting':calls['compile_app'].assert_not_called()
                else:calls['compile_app'].assert_called_once()

    def test_no_new_inert_upload_manifest_key_exists(self):
        manifest=json.loads((ROOT/'tools/p0_inert_sources.json').read_text())
        self.assertNotIn(SKETCH,manifest)


if __name__=='__main__':
    unittest.main(verbosity=2)
