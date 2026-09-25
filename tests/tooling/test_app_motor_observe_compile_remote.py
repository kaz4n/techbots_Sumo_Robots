# Tests D193 actual projected remote and adapter against preserved D188/D187 oracles.
# Changes only private fixture identities and projected source selection, never assertions.
# Freeze before Python -B execution; synthetic artifacts and RAM files grant no native work.
import hashlib
from pathlib import Path
import sys
import types
import unittest

ROOT = Path(__file__).resolve().parents[2]
LAUNCHER = 'tools/compile_app_motor_observe.py'
REMOTE_SOURCE = 'tools/app_motor_fault_compile_remote.py'
ADAPTER_SOURCE = 'tools/app_motor_fault_static_policy.py'
REMOTE_ORACLE = 'tests/tooling/test_app_motor_fault_compile_remote.py'
ADAPTER_ORACLE = 'tests/tooling/test_app_motor_fault_static_policy.py'
ORIGINAL_REMOTE_SHA = '1428b9345d5f524b6c79ede2c30eabb240b6a45ef6a30a593063c3902054fec2'
ORIGINAL_ADAPTER_SHA = '3e5d49e4a70c0cf6197e26b1ba5ce2b7e07601bf5d9250ba430f90d1f9eab270'
PROJECTED_REMOTE_SHA = 'f7886c869980afc969082b66ce8d3fc35801fe7c11134b406af158f06049160c'
PROJECTED_ADAPTER_SHA = 'e3d23d5c6b2bd2d088f954a2dd2b574188edca8ca95d65a4432e54de759d169d'
REMOTE_ORACLE_SHA = 'db0ff0284eb7c528a852f39a57fcb668c72c098543b6d6813298fc2dfeddd80b'
ADAPTER_ORACLE_SHA = 'e6d52ec6b0d72e893511793e9d92003092499280454093c9b6622d0e18547d5c'
PROJECT = 'app_motor_observe.ino'
REMOTE = '/home/arduino/sumox26_codex_build/app-motor-observe-static01'


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def checked(path, sha):
    raw = path.read_bytes()
    if digest(raw) != sha:
        raise AssertionError('Historical oracle/source changed: ' + str(path))
    return raw


def private_module(raw, path, name):
    module = types.ModuleType(name)
    module.__file__ = str(path)
    exec(compile(raw, str(path), 'exec'), module.__dict__)
    return module


def fixture_metadata(raw):
    # Keep source-file ownership and paths original; project only fixture identities.
    protected = (REMOTE_SOURCE, ADAPTER_SOURCE)
    for index, name in enumerate(protected):
        raw = raw.replace(name.encode(), ('@PRESERVE_SOURCE_' + str(index) + '@').encode())
    for old, new in ((b'app_motor_fault', b'app_motor_observe'),
                     (b'app-motor-fault', b'app-motor-observe'),
                     (b'STATIC_APP_MOTOR_FAULT', b'STATIC_APP_MOTOR_OBSERVE')):
        raw = raw.replace(old, new)
    for index, name in enumerate(protected):
        raw = raw.replace(('@PRESERVE_SOURCE_' + str(index) + '@').encode(), name.encode())
    return raw


def projected_source(launcher, kind):
    path, original, expected, size = (
        (REMOTE_SOURCE, ORIGINAL_REMOTE_SHA, PROJECTED_REMOTE_SHA, 6897)
        if kind == 'remote' else (ADAPTER_SOURCE, ORIGINAL_ADAPTER_SHA, PROJECTED_ADAPTER_SHA, 8266))
    result = getattr(launcher, 'project_' + kind)(checked(ROOT / path, original))
    if type(result) is not bytes or len(result) != size or digest(result) != expected:
        raise AssertionError('Projected fixture source differs from frozen contract: ' + kind)
    return result


def remote_fixture(launcher):
    raw = fixture_metadata(checked(ROOT / REMOTE_ORACLE, REMOTE_ORACLE_SHA))
    fixture = private_module(raw, ROOT / REMOTE_ORACLE, '_d193_actual_remote_oracle')
    fixture.BUNDLE = dict(fixture.BUNDLE, adapter=(ADAPTER_SOURCE, PROJECTED_ADAPTER_SHA))
    inherited_load = fixture.load

    def load(path, name):
        if Path(path) == ROOT / REMOTE_SOURCE:
            return private_module(projected_source(launcher, 'remote'), path, '_d193_actual_remote')
        return inherited_load(path, name)

    def checked_bundle():
        result = {}
        for name, (path, expected) in fixture.BUNDLE.items():
            raw = projected_source(launcher, 'adapter') if name == 'adapter' else checked(ROOT / path, expected)
            if digest(raw) != expected:
                raise AssertionError('Projected remote bundle pin mismatch: ' + name)
            result[name] = raw
        return result

    fixture.load = load
    fixture.checked_bundle = checked_bundle
    return fixture


def adapter_fixture(launcher):
    raw = fixture_metadata(checked(ROOT / ADAPTER_ORACLE, ADAPTER_ORACLE_SHA))
    fixture = private_module(raw, ROOT / ADAPTER_ORACLE, '_d193_actual_adapter_oracle')
    inherited_load = fixture.load_module

    def load_module(name, path):
        if Path(path) == ROOT / ADAPTER_SOURCE:
            return private_module(projected_source(launcher, 'adapter'), path, '_d193_actual_adapter')
        return inherited_load(name, path)

    fixture.load_module = load_module
    return fixture


def extra_remote_cases(fixture):
    class ProjectedBundleContract(fixture.RemoteArtifactContract):
        def test_original_adapter_bundle_and_old_attempt_paths_are_rejected(self):
            bundle = dict(self.bundle, adapter=checked(ROOT / ADAPTER_SOURCE, ORIGINAL_ADAPTER_SHA))
            try:
                result = self.inspect(bundle)
            except (ValueError, TypeError):
                pass
            else:
                self.failure(result)
            for position in ('build', 'artifacts'):
                old = REMOTE.replace('observe', 'fault') + '/' + position
                with self.subTest(position=position), self.assertRaises((ValueError, TypeError)):
                    self.inspect(**{position: old})

        def test_success_binds_new_schema_names_aliases_and_projected_dependency_bytes(self):
            self.assertEqual(digest(self.bundle['adapter']), PROJECTED_ADAPTER_SHA)
            result = self.inspect()
            self.assertEqual(result['status'], 'ARTIFACTS_CHECKED')
            self.assertEqual(result['schema'], 'app-motor-observe-static-artifacts-v1')
            self.assertEqual(result['build_path'], REMOTE + '/build')
            self.assertEqual(result['artifacts_path'], REMOTE + '/artifacts')
            self.assertEqual(result['layout']['project'], PROJECT)
            aliases = {PROJECT + suffix: 'app.ino' + suffix for suffix in fixture.SUFFIXES}
            self.assertEqual(result['layout']['artifact_aliases'], aliases)
            self.assertEqual(set(result['files']), {'build/' + key for key in aliases} |
                             {'artifacts/' + PROJECT + '.bin-zsk.bin'})
            self.assertEqual(result['layout'], fixture.expected_layout(self.packet))

    return ProjectedBundleContract


def extra_adapter_cases(fixture):
    class OldIdentityContract(fixture.ContractFixture):
        def test_old_d188_project_is_rejected_even_with_coherent_properties_and_packet(self):
            envelope = self.envelope()
            properties = envelope['builder_result']['build_properties']
            envelope['builder_result']['build_properties'] = [
                value.replace(PROJECT, 'app_motor_fault.ino') for value in properties]
            self.reject_metadata(envelope)
            packet = {key.replace(PROJECT, 'app_motor_fault.ino'): value
                      for key, value in self.packet().items()}
            self.reject_artifacts(packet, exported=self.packet()[PROJECT + '.bin-zsk.bin'])

    return OldIdentityContract


def load_tests(loader, standard, pattern):
    if not sys.dont_write_bytecode:
        raise RuntimeError('D193 projected remote tests require Python -B')
    launcher = private_module((ROOT / LAUNCHER).read_bytes(), ROOT / LAUNCHER, '_d193_remote_launcher')
    remote = remote_fixture(launcher)
    adapter = adapter_fixture(launcher)
    suite = unittest.TestSuite([standard])
    inherited_remote = loader.loadTestsFromTestCase(remote.RemoteArtifactContract)
    inherited_metadata = loader.loadTestsFromTestCase(adapter.FixedMetadataContract)
    if inherited_remote.countTestCases() != 14 or inherited_metadata.countTestCases() != 15:
        raise AssertionError('Frozen D188/D187 inherited assertion inventory changed')
    suite.addTests(inherited_remote)
    suite.addTests(inherited_metadata)
    artifact_methods = ('test_exact_success_contains_unmodified_complete_legacy_report',
                        'test_real_validator_receives_exact_seven_original_byte_objects',
                        'test_each_required_actual_filename_and_only_those_names')
    suite.addTests(adapter.FixedArtifactContract(name) for name in artifact_methods)
    supplemental = extra_remote_cases(remote)
    suite.addTests(supplemental(name) for name in (
        'test_original_adapter_bundle_and_old_attempt_paths_are_rejected',
        'test_success_binds_new_schema_names_aliases_and_projected_dependency_bytes'))
    suite.addTests(loader.loadTestsFromTestCase(extra_adapter_cases(adapter)))
    if suite.countTestCases() != 35:
        raise AssertionError('Expected 14 remote + 15 metadata + 3 artifact + 3 supplemental cases')
    return suite


if __name__ == '__main__':
    unittest.main(verbosity=2)
