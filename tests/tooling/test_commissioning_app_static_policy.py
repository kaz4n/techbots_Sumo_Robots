# Tests D222 profile selection against independently enumerated identities.
# Reuses accepted synthetic compiler/ELF fixtures without rerunning old suites.
# Covers pure metadata, snapshot isolation and complete artifact checks offline.
import builtins
import copy
import importlib.util
import json
from pathlib import Path
import sys
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
SUBJECT = ROOT / 'tools/commissioning_app_static_policy.py'
PROFILES = {
    'b4_stand': ('SUMOX_B4_STAND',),
    'p3_drive': ('SUMOX_P3_DRIVE_TEST',),
    'p3_turn': ('SUMOX_P3_TURN_TRIAL',),
    'p3_stop': ('SUMOX_P3_STOP_TRIAL',),
    'p4_reactive': ('SUMOX_P4_REACTIVE',),
    'p4_timing': ('SUMOX_P4_REACTIVE', 'SUMOX_TIMING_EVIDENCE'),
    'p5_abort_timing': ('SUMOX_P5_ABORT_TIMING',),
}
MACROS = ('SUMOX_B4_STAND', 'SUMOX_P3_DRIVE_TEST', 'SUMOX_P3_TURN_TRIAL',
          'SUMOX_P3_STOP_TRIAL', 'SUMOX_P4_REACTIVE', 'SUMOX_TIMING_EVIDENCE',
          'SUMOX_P5_ABORT_TIMING', 'SUMOX_MOTOR_FAULT_PROBE')


def expected_flags(profile, motors):
    return ' '.join(['-DMATCH=0', '-DMOTORS_ALLOWED=' + str(motors)] +
                    ['-D' + name + '=' + str(int(name in PROFILES[profile]))
                     for name in MACROS])


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# Loading definitions does not collect or run the historical tests.
OLD = load(ROOT / 'tests/tooling/test_b4_app_static_policy.py', '_d222_b4_fixture')


class StrSubclass(str):
    pass


class IntSubclass(int):
    pass


class DictSubclass(dict):
    pass


class BytesSubclass(bytes):
    pass


class CommissioningPolicy(OLD.Fixture):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        raw = SUBJECT.read_bytes()
        with OLD.no_effects_or_source_reads():
            cls.policy = OLD.load_bytes('_d222_policy_subject', raw, SUBJECT)

    def envelope_for(self, profile, motors):
        result = self.support.public_envelope(self.reference, OLD.BUILD, OLD.DATA)
        properties = self.support.public_properties(self.reference, OLD.BUILD, OLD.DATA)
        for key, template in self.reference.items():
            properties[key] = OLD.literal_once(template.replace(
                OLD.OLD_FLAGS, expected_flags(profile, motors)), OLD.BUILD, OLD.DATA)
        properties['build.project_name'] = 'app.ino'
        result['builder_result']['build_properties'] = [
            key + '=' + value for key, value in properties.items()]
        return result, properties

    def arguments_for(self, method, profile='p3_drive', motors=0, snapshots=None):
        kwargs = dict(profile=profile, motors_allowed=motors,
                      snapshots=dict(self.snapshots) if snapshots is None else snapshots)
        if method == 'validate_artifacts':
            packet = self.packet()
            kwargs['exported_flat_package'] = packet['app.ino.bin-zsk.bin']
            return (packet, self.native_source, self.frozen_source), kwargs
        kwargs.update(build_path=OLD.BUILD, data_dir=OLD.DATA)
        envelope, _ = self.envelope_for('p3_drive', 0)
        if type(profile) is str and profile in PROFILES and type(motors) is int and motors in (0, 1):
            envelope, _ = self.envelope_for(profile, motors)
        return (json.dumps(envelope),), kwargs

    def invoke(self, method, args, kwargs):
        with OLD.no_effects_or_source_reads():
            return getattr(self.policy, method)(*args, **kwargs)

    def test_all_fourteen_literal_identities_and_constants(self):
        self.assertEqual(self.policy.PROJECT, 'app.ino')
        self.assertEqual(self.policy.FQBN, 'arduino:zephyr:unoq:link_mode=static')
        self.assertEqual(set(self.policy.PROFILES), set(PROFILES))
        self.assertEqual(len(self.policy.PROFILES), 7)
        self.assertEqual(self.policy.SNAPSHOT_PINS, OLD.SNAPSHOT_PINS)
        for profile in PROFILES:
            for motors in (0, 1):
                with self.subTest(profile=profile, motors=motors), OLD.no_effects_or_source_reads():
                    actual = self.policy.safety_flags(profile, motors_allowed=motors)
                    self.assertEqual(actual, expected_flags(profile, motors))
                    self.assertEqual(len(actual.split()), 10)

    def test_selection_types_fail_before_snapshots_or_execution(self):
        bad_profiles = (None, True, 0, [], {}, '', 'P3_DRIVE', 'p3-drive', 'app',
                        'p3_drive ', StrSubclass('p3_drive'))
        bad_motors = (None, True, False, -1, 2, 0.0, 1.0, '0', '1', IntSubclass(0))
        for profile, motors in [(v, 0) for v in bad_profiles] + [('p3_drive', v) for v in bad_motors]:
            with self.subTest(profile=repr(profile), motors=repr(motors)):
                with self.assertRaises((TypeError, ValueError)):
                    self.policy.safety_flags(profile, motors_allowed=motors)
                for method in OLD.APIS:
                    args, kwargs = self.arguments_for(method, profile, motors, snapshots={})
                    with mock.patch.object(builtins, 'exec', side_effect=AssertionError('Bad selection executed')):
                        with self.assertRaises((TypeError, ValueError)):
                            self.invoke(method, args, kwargs)

    def test_keyword_only_explicit_selection_is_required(self):
        with self.assertRaises(TypeError):
            self.policy.safety_flags('p3_drive')
        with self.assertRaises(TypeError):
            self.policy.safety_flags('p3_drive', 0)
        for method in OLD.APIS:
            args, kwargs = self.arguments_for(method)
            for missing in ('profile', 'motors_allowed', 'snapshots'):
                changed = dict(kwargs); del changed[missing]
                with self.subTest(method=method, missing=missing), self.assertRaises(TypeError):
                    self.invoke(method, args, changed)

    def test_snapshot_shape_type_hash_and_size_are_checked_before_execution(self):
        invalid = [None, [], {}, DictSubclass(self.snapshots), dict(self.snapshots, extra=b'x')]
        for key, raw in self.snapshots.items():
            missing = dict(self.snapshots); del missing[key]; invalid.append(missing)
            wrong_key = dict(missing); wrong_key[StrSubclass(key)] = raw; invalid.append(wrong_key)
            for value in (b'', raw + b'\n', raw[:-1], BytesSubclass(raw), bytearray(raw), None):
                invalid.append(dict(self.snapshots, **{key: value}))
        for index, snapshots in enumerate(invalid):
            for method in OLD.APIS:
                args, kwargs = self.arguments_for(method, snapshots=snapshots)
                # None is intentionally passed through rather than the fixture default.
                kwargs['snapshots'] = snapshots
                with self.subTest(index=index, method=method), mock.patch.object(
                        builtins, 'exec', side_effect=AssertionError('Bad snapshot executed')):
                    with self.assertRaises((ValueError, TypeError)):
                        self.invoke(method, args, kwargs)

    def test_real_metadata_accepts_all_profiles_and_returns_complete_properties(self):
        for profile in PROFILES:
            for motors in (0, 1):
                envelope, properties = self.envelope_for(profile, motors)
                for method in OLD.METHODS:
                    args, kwargs = self.arguments_for(method, profile, motors)
                    with self.subTest(profile=profile, motors=motors, method=method):
                        actual = self.invoke(method, (json.dumps(envelope),), kwargs)
                        self.assertEqual(actual, properties)

    def test_coherent_other_profile_and_other_motor_metadata_refuse(self):
        profiles = tuple(PROFILES)
        for index, profile in enumerate(profiles):
            for motors in (0, 1):
                alternatives = ((profiles[(index + 1) % len(profiles)], motors), (profile, 1 - motors))
                for other_profile, other_motors in alternatives:
                    envelope, _ = self.envelope_for(other_profile, other_motors)
                    for method in OLD.METHODS:
                        _, kwargs = self.arguments_for(method, profile, motors)
                        with self.subTest(profile=profile, motors=motors, alternative=alternatives,
                                          method=method), self.assertRaises(ValueError):
                            self.invoke(method, (json.dumps(envelope),), kwargs)

    def test_every_profile_rejects_flag_order_duplicates_missing_and_competing_bits(self):
        for profile in PROFILES:
            valid = expected_flags(profile, 0)
            alternatives = (' '.join(reversed(valid.split())), valid + ' -DMOTORS_ALLOWED=0',
                            valid.replace(' -DSUMOX_MOTOR_FAULT_PROBE=0', ''),
                            valid.replace('-DMATCH=0', '-DMATCH=1'),
                            valid.replace('-DSUMOX_MOTOR_FAULT_PROBE=0', '-DSUMOX_MOTOR_FAULT_PROBE=1'))
            for wrong in alternatives:
                envelope, _ = self.envelope_for(profile, 0)
                envelope['builder_result']['build_properties'] = [
                    value.replace(valid, wrong) for value in envelope['builder_result']['build_properties']]
                for method in OLD.METHODS:
                    _, kwargs = self.arguments_for(method, profile, 0)
                    with self.subTest(profile=profile, wrong=wrong, method=method), self.assertRaises(ValueError):
                        self.invoke(method, (json.dumps(envelope),), kwargs)

    def test_inherited_metadata_rejections_remain_effective(self):
        envelope, _ = self.envelope_for('p4_timing', 1)
        variants = []
        for key, replacement in (('build.fqbn', 'arduino:zephyr:unoq:wait_linux_boot=no:link_mode=static'),
                                 ('build.project_name', 'reactive_timing.ino'),
                                 ('build.link_mode', 'dynamic'), ('build.boot_mode', 'immediate'),
                                 ('compiler.cpp.extra_flags', '-DMATCH=0 -DMOTORS_ALLOWED=1')):
            changed = copy.deepcopy(envelope)
            changed['builder_result']['build_properties'] = [
                key + '=' + replacement if value.startswith(key + '=') else value
                for value in changed['builder_result']['build_properties']]
            variants.append(changed)
        changed = copy.deepcopy(envelope)
        changed['builder_result']['build_properties'].append('recipe.unreviewed.pattern=bad')
        variants.append(changed)
        changed = copy.deepcopy(envelope)
        changed['builder_result']['build_properties'].append(changed['builder_result']['build_properties'][0])
        variants.append(changed)
        for changed in variants:
            for method in OLD.METHODS:
                _, kwargs = self.arguments_for(method, 'p4_timing', 1)
                with self.subTest(method=method), self.assertRaises(ValueError):
                    self.invoke(method, (json.dumps(changed),), kwargs)
        changed = copy.deepcopy(envelope)
        changed['builder_result']['used_libraries'] = [{'name': 'Unreviewed'}]
        _, kwargs = self.arguments_for('validate_compile_result', 'p4_timing', 1)
        with self.assertRaises(ValueError):
            self.invoke('validate_compile_result', (json.dumps(changed),), kwargs)

    def test_all_profiles_preserve_complete_artifact_report_and_original_inputs(self):
        packet = self.packet(); before = copy.deepcopy(packet)
        old_policy = OLD.load_bytes('_d222_accepted_b4_policy', OLD.SUBJECT.read_bytes(), OLD.SUBJECT)
        expected = old_policy.validate_artifacts(packet, self.native_source, self.frozen_source,
            exported_flat_package=packet['app.ino.bin-zsk.bin'], motors_allowed=0,
            snapshots=dict(self.snapshots))
        for profile in PROFILES:
            for motors in (0, 1):
                expected.update(status='STATIC_COMMISSIONING_APP_LAYOUT_PACKAGE_PASS',
                                profile=profile, motors_allowed=motors,
                                flags=expected_flags(profile, motors))
                args, kwargs = self.arguments_for('validate_artifacts', profile, motors)
                with self.subTest(profile=profile, motors=motors):
                    report = self.invoke('validate_artifacts', args, kwargs)
                    self.assertEqual(report, expected)
                    self.assertIs(type(report['motors_allowed']), int)
                    self.assertEqual(packet, before)

    def test_elf_tls_package_and_export_failures_never_become_pass(self):
        for profile in PROFILES:
            args, kwargs = self.arguments_for('validate_artifacts', profile, 1)
            wrong_export = dict(kwargs, exported_flat_package=kwargs['exported_flat_package'] + b'x')
            with self.subTest(profile=profile, kind='export'), self.assertRaises(ValueError):
                self.invoke('validate_artifacts', args, wrong_export)
        for suffix in ('.elf', '_debug.elf', '_temp.elf', '.bin-zsk.bin', '.elf-zsk.bin'):
            args, kwargs = self.arguments_for('validate_artifacts', 'p4_timing', 0)
            packet = dict(args[0]); name = 'app.ino' + suffix
            packet[name] = b'BAD!' + packet[name][4:]
            if suffix == '.bin-zsk.bin':
                kwargs['exported_flat_package'] = packet[name]
            with self.subTest(artifact=name), self.assertRaises(ValueError):
                self.invoke('validate_artifacts', (packet, *args[1:]), kwargs)
        args, kwargs = self.arguments_for('validate_artifacts', 'p5_abort_timing', 0)
        for index in (1, 2):
            changed = list(args); changed[index] += b'\n'
            with self.subTest(source=index), self.assertRaises(ValueError):
                self.invoke('validate_artifacts', tuple(changed), kwargs)

    def test_profile_calls_are_isolated_and_revalidate_snapshots(self):
        original = dict(self.snapshots)
        order = (('p3_drive', 0), ('p4_timing', 1), ('p5_abort_timing', 0), ('p3_drive', 0))
        results = []
        for profile, motors in order:
            args, kwargs = self.arguments_for('validate_compile_result', profile, motors)
            results.append(self.invoke('validate_compile_result', args, kwargs))
        self.assertEqual(results[0], results[-1])
        results[0]['compiler.cpp.extra_flags'] = 'caller mutation'
        self.assertEqual(results[-1]['compiler.cpp.extra_flags'], expected_flags('p3_drive', 0))
        self.assertEqual(self.snapshots, original)
        args, kwargs = self.arguments_for('validate_compile_result', 'p3_drive', 0)
        key = next(iter(kwargs['snapshots'])); kwargs['snapshots'][key] += b'\n'
        with self.assertRaises(ValueError):
            self.invoke('validate_compile_result', args, kwargs)


if __name__ == '__main__':
    if not sys.dont_write_bytecode:
        raise SystemExit('Run with Python -I -B')
    unittest.main(verbosity=2)
