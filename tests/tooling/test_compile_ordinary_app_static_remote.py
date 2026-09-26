# Completes D208 remote and all D187 adapter obligations with explicit overlap.
# Preserves real descriptor/package validators and rejects consumed diagnostic owners.
# Frozen independently; synthetic host fixtures never invoke board or compiler tools.
from pathlib import Path
import hashlib
import sys
import types
import unittest

ROOT=Path(__file__).resolve().parents[2]
SUPPORT='tests/tooling/test_compile_ordinary_app_static.py'
SUPPORT_PIN={'bytes': 22397, 'sha256': 'a5c9ea91fee0816e3a19cd091d49cf2fbeeb885832f115e37f778654a3c96fce'}


def support():
    raw=(ROOT/SUPPORT).read_bytes()
    if {'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}!=SUPPORT_PIN:
        raise AssertionError('Frozen independent caller support differs')
    module=types.ModuleType('_d208_independent_remote_support')
    module.__file__=str(ROOT/SUPPORT)
    exec(compile(raw,module.__file__,'exec'),module.__dict__)
    return module


def remote_additions(fixture):
    class OrdinaryRemote(fixture.RemoteArtifactContract):
        def test_consumed_const_build_export_and_combined_owners_are_rejected(self):
            stale='/home/arduino/sumox26_codex_build/app-motor-const-static01'
            for fields in ({'build':stale+'/build'},{'artifacts':stale+'/artifacts'},
                           {'build':stale+'/build','artifacts':stale+'/artifacts'}):
                with self.subTest(fields=fields),self.assertRaises((ValueError,TypeError)):
                    self.inspect(**fields)
    return OrdinaryRemote


def adapter_additions(fixture):
    class IdentityAliases(fixture.ContractFixture):
        def test_identity_aliases_preserve_all_seven_objects_and_reject_diagnostic_probe_profile(self):
            packet=self.packet()
            report=self.artifacts(packet)
            self.assertEqual(report['artifact_aliases'],{name:name for name in packet})
            self.assertEqual(len(report['artifact_aliases']),7)
            self.assertEqual(report['flags'],'-DMATCH=0 -DMOTORS_ALLOWED=0')
            for project in ('app_motor_fault.ino','app_motor_observe.ino'):
                stale={name.replace('app.ino',project):value for name,value in packet.items()}
                with self.subTest(project=project):
                    self.reject_artifacts(stale,exported=packet['app.ino.bin-zsk.bin'])
            for key in ('compiler.c.extra_flags','compiler.cpp.extra_flags'):
                envelope=self.envelope()
                self.support.replace_property(envelope,key,
                    '-DMATCH=0 -DMOTORS_ALLOWED=0 -DSUMOX_MOTOR_FAULT_PROBE=1')
                self.reject_metadata(envelope)
    return IdentityAliases


def load_tests(loader,standard,pattern):
    if not sys.dont_write_bytecode:
        raise AssertionError('D208 oracles require Python -B')
    helper=support();remote=helper.remote_fixture();adapter=helper.adapter_fixture()
    groups=[helper.checked_selection(loader.loadTestsFromTestCase(remote.RemoteArtifactContract),14,'D188 remote'),
            helper.checked_selection(unittest.TestSuite(loader.loadTestsFromTestCase(getattr(adapter,name))
                for name in ('FixedMetadataContract','FixedArtifactContract','DependencyProvenanceContract')),33,'all D187')]
    d193=helper.fixture('remote193')
    d193.__dict__.update(ROOT=ROOT,PROJECT='app.ino',
        REMOTE='/home/arduino/sumox26_codex_build/ordinary-app-static01',
        ADAPTER_SOURCE='tools/app_motor_fault_static_policy.py',
        ORIGINAL_ADAPTER_SHA=helper.plan()['original_subjects']['tools/app_motor_fault_static_policy.py']['sha256'],
        PROJECTED_ADAPTER_SHA=helper.plan()['implementation']['adapter']['sha256'],
        checked=lambda path,digest: helper.checked(path,helper.plan()['inputs'][str(Path(path).relative_to(ROOT).as_posix())]),
        digest=helper.sha,unittest=unittest)
    cls=d193.extra_remote_cases(remote)
    groups.append(helper.checked_selection(unittest.TestSuite([
        cls('test_original_adapter_bundle_and_old_attempt_paths_are_rejected'),
        cls('test_success_binds_new_schema_names_aliases_and_projected_dependency_bytes'),
        loader.loadTestsFromTestCase(d193.extra_adapter_cases(adapter))]),3,'D193 supplements'))
    d198=helper.fixture('remote198');d198.unittest=unittest
    cls=d198.additional_cases(remote)
    groups.append(helper.checked_selection(unittest.TestSuite(cls(name) for name in (
        'test_previous_d193_build_and_artifact_paths_are_refused_separately_and_together',
        'test_new_owner_keeps_observer_project_and_existing_layout_status')),2,'D198 supplements'))
    d203=helper.fixture('remote203');d203.unittest=unittest
    cls=d203.additional_case(remote)
    groups.append(helper.checked_selection(unittest.TestSuite([
        cls('test_consumed_d198_build_artifacts_and_combined_paths_are_refused')]),1,'D203 supplement'))
    inherited=helper.checked_selection(unittest.TestSuite(groups),53,'38 historical plus 15 missing D187')
    result=unittest.TestSuite([standard,inherited,
        remote_additions(remote)('test_consumed_const_build_export_and_combined_owners_are_rejected'),
        loader.loadTestsFromTestCase(adapter_additions(adapter))])
    if result.countTestCases()!=helper.plan()['counts']['remote_total']:
        raise AssertionError('Final remote inventory differs')
    return result


if __name__=='__main__':
    unittest.main(verbosity=2)

