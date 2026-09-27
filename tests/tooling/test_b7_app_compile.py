# Tests the frozen D244 B7 build contract independently of its implementation.
# Reuses D222 synthetic artifacts and controlled endpoints without board effects.
# Freeze this oracle before execution; historical suites are not collected again.
import builtins
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import types
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
CALLER = 'tools/compile_b7_app.py'
POLICY = 'tools/b7_app_static_policy.py'
REMOTE = 'tools/b7_app_compile_remote.py'
CONTRACT = 'state/analysis/P2_b7_build_contract.md'
ADDITIONS = {CALLER, POLICY, REMOTE, CONTRACT}
HEAD = '0123456789abcdef0123456789abcdef01234567'
SOURCE = 'abcdef0123456789abcdef0123456789abcdef0123456789abcdef0123456789'
OLD_PINS = {
    'tools/compile_commissioning_app.py': (17992, '038a74777db7d26a15ff543d311fc4df2503e6f6b8e3b08fabcfb1c853220462'),
    'tools/commissioning_app_static_policy.py': (4779, '1e46cf058ccab40a2cb8e0aa9f3e9583b1f11d35fd22baaf93ff9b55d78ba931'),
    'tools/commissioning_app_compile_remote.py': (5305, '476f6025e55fa9c2bdd0f29341fb660197a9f7eead8fd34b7c71e277158014a3'),
}
MACROS = ('SUMOX_B4_STAND', 'SUMOX_P3_DRIVE_TEST', 'SUMOX_P3_TURN_TRIAL',
          'SUMOX_P3_STOP_TRIAL', 'SUMOX_P4_REACTIVE', 'SUMOX_TIMING_EVIDENCE',
          'SUMOX_P5_ABORT_TIMING', 'SUMOX_MOTOR_FAULT_PROBE')


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


OLD_CALLER = load(ROOT / 'tests/tooling/test_commissioning_app_compile.py', '_b7_old_caller_fixture')
OLD_POLICY = load(ROOT / 'tests/tooling/test_b4_app_static_policy.py', '_b7_old_policy_fixture')
PIPELINE = OLD_CALLER.pipeline_cases()
BASE = PIPELINE.__mro__[1].setUp.__globals__
BASE['FIXED'] = sorted(set(BASE['FIXED']) | ADDITIONS)


def request(motors=0, attempt='b7trial01', action='--check-only', head=HEAD):
    return dict(action=action, profile='b7_brownout', motors_allowed=motors,
                attempt=attempt, reviewed_head=head)


def flags(motors):
    return ' '.join(['-DMATCH=0', '-DMOTORS_ALLOWED=' + str(motors)] +
                    ['-D' + name + '=0' for name in MACROS] + ['-DSUMOX_B7_BROWNOUT=1'])


def paths(motors=0, attempt='b7trial01', source=SOURCE):
    result = OLD_CALLER.expected_paths('b7_brownout', motors, attempt, source)
    result['output'] = 'state/analysis/P2_b7_build_raw/' + result['owner']
    return result


class PublicContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.subject = load(ROOT / CALLER, '_b7_public_subject')

    def test_exact_grammar_types_and_only_b7_before_io(self):
        good = OLD_CALLER.argv('b7_brownout', 0, 'b7trial01')
        self.assertEqual(tuple(self.subject.PROFILES), ('b7_brownout',))
        for motors in (0, 1):
            for action in ('--check-only', '--execute'):
                self.assertEqual(self.subject.parse_request(OLD_CALLER.argv(
                    'b7_brownout', motors, 'b7trial01', action)), request(motors, action=action))
        invalid = [None, tuple(good), OLD_CALLER.ListSubclass(good), good[:-1],
                   good + ['--upload'], good + ['--flags', '-DMATCH=1']]
        for index, choices in ((0, ('--upload', '--reset')), (2, (*OLD_CALLER.PROFILES, 'match', 'B7_BROWNOUT')),
                               (4, ('true', '01', '2')), (6, ('../x', 'A', 'a' * 25)),
                               (8, (HEAD.upper(), HEAD[:-1]))):
            for value in choices:
                changed = list(good); changed[index] = value; invalid.append(changed)
        with mock.patch.object(Path, 'read_bytes', side_effect=AssertionError('Validation read source')):
            for value in invalid:
                with self.subTest(value=value), self.assertRaises((TypeError, ValueError)):
                    self.subject.parse_request(value)
            for motors in (True, False, 0.0, '0', OLD_CALLER.IntSubclass(0), -1, 2):
                with self.subTest(motors=motors), self.assertRaises((TypeError, ValueError)):
                    self.subject.checked_request(request(motors))
            for value in (None, OLD_CALLER.DictSubclass(request()), dict(request(), extra=True)):
                with self.assertRaises((TypeError, ValueError)):
                    self.subject.load_caller(value, root=ROOT)

    def test_paths_private_modules_and_unchanged_d222(self):
        original = load(ROOT / 'tools/compile_commissioning_app.py', '_b7_unchanged_d222')
        states = []
        for motors in (0, 1, 0):
            module = self.subject.load_caller(request(motors), root=ROOT)
            owner = module.CompileDiagnostic(HEAD, root=ROOT)
            states.append((module, owner))
            self.assertEqual(self.subject.build_paths('b7_brownout', motors, 'b7trial01', SOURCE), paths(motors))
            self.assertEqual(owner.flags, flags(motors))
            self.assertEqual(len(owner.flags.split()), 11)
            self.assertEqual(owner.fqbn, 'arduino:zephyr:unoq:link_mode=static')
            self.assertEqual(owner.output, ROOT / paths(motors, source=owner.source_sha256)['output'])
            self.assertEqual(set(original.REQUIRED) | ADDITIONS, set(module.REQUIRED))
            with self.assertRaises(ValueError):
                module.CompileDiagnostic('f' * 40, root=ROOT)
        self.assertEqual(states[0][1].flags, states[2][1].flags)
        self.assertEqual(len({id(module) for module, owner in states}), 3)
        self.assertEqual([module.FLAGS for module, owner in states], [flags(0), flags(1), flags(0)])
        self.assertEqual(set(original.PROFILES), set(OLD_CALLER.PROFILES))
        for name, pin in OLD_PINS.items():
            body = (ROOT / name).read_bytes()
            self.assertEqual((len(body), hashlib.sha256(body).hexdigest()), pin)
        for value in ('../escape', 'A', 'x' * 25, OLD_CALLER.StrSubclass('b7trial01')):
            with self.assertRaises((TypeError, ValueError)):
                self.subject.build_paths('b7_brownout', 0, value, SOURCE)


class PolicyContract(OLD_POLICY.Fixture):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.previous = cls.policy
        body = (ROOT / POLICY).read_bytes()
        with OLD_POLICY.no_effects_or_source_reads():
            cls.policy = OLD_POLICY.load_bytes('_b7_policy_subject', body, ROOT / POLICY)

    def envelope_for(self, motors):
        envelope = self.support.public_envelope(self.reference, OLD_POLICY.BUILD, OLD_POLICY.DATA)
        properties = self.support.public_properties(self.reference, OLD_POLICY.BUILD, OLD_POLICY.DATA)
        for key, template in self.reference.items():
            properties[key] = OLD_POLICY.literal_once(template.replace(
                OLD_POLICY.OLD_FLAGS, flags(motors)), OLD_POLICY.BUILD, OLD_POLICY.DATA)
        properties['build.project_name'] = 'app.ino'
        envelope['builder_result']['build_properties'] = [key + '=' + value for key, value in properties.items()]
        return envelope, properties

    def invoke(self, method, argument, motors=0, **changes):
        kwargs = dict(profile='b7_brownout', motors_allowed=motors, snapshots=dict(self.snapshots))
        if method == 'validate_artifacts':
            args = (argument, self.native_source, self.frozen_source)
            kwargs['exported_flat_package'] = argument['app.ino.bin-zsk.bin']
        else:
            args = (json.dumps(argument),)
            kwargs.update(build_path=OLD_POLICY.BUILD, data_dir=OLD_POLICY.DATA)
        kwargs.update(changes)
        with OLD_POLICY.no_effects_or_source_reads():
            return getattr(self.policy, method)(*args, **kwargs)

    def test_exact_metadata_both_modes_and_competing_tuple_refusals(self):
        self.assertEqual(tuple(self.policy.PROFILES), ('b7_brownout',))
        self.assertEqual(self.policy.SNAPSHOT_PINS, OLD_POLICY.SNAPSHOT_PINS)
        for motors in (0, 1):
            envelope, properties = self.envelope_for(motors)
            self.assertEqual(self.policy.safety_flags('b7_brownout', motors_allowed=motors), flags(motors))
            for method in OLD_POLICY.METHODS:
                self.assertEqual(self.invoke(method, envelope, motors), properties)
                wrong_flags = (flags(1 - motors), flags(motors).replace('B7_BROWNOUT=1', 'B7_BROWNOUT=0'),
                               flags(motors).replace('B4_STAND=0', 'B4_STAND=1'), flags(motors) + ' -DMATCH=0')
                for wrong in wrong_flags:
                    changed = copy.deepcopy(envelope)
                    changed['builder_result']['build_properties'] = [x.replace(flags(motors), wrong)
                        for x in changed['builder_result']['build_properties']]
                    with self.subTest(motors=motors, method=method, flags=wrong), self.assertRaises(ValueError):
                        self.invoke(method, changed, motors)
                changed = copy.deepcopy(envelope)
                self.support.replace_property(changed, 'build.boot_mode', 'immediate')
                with self.assertRaises(ValueError):
                    self.invoke(method, changed, motors)

    def test_actual_elf_tls_flat_export_and_source_checks_remain(self):
        packet = self.packet(); original = copy.deepcopy(packet)
        expected = self.previous.validate_artifacts(packet, self.native_source, self.frozen_source,
            exported_flat_package=packet['app.ino.bin-zsk.bin'], motors_allowed=0, snapshots=dict(self.snapshots))
        for motors in (0, 1):
            result = self.invoke('validate_artifacts', packet, motors)
            projected = dict(expected, status='STATIC_COMMISSIONING_APP_LAYOUT_PACKAGE_PASS',
                             profile='b7_brownout', motors_allowed=motors, flags=flags(motors))
            self.assertEqual(result, projected)
        self.assertEqual(packet, original)
        for suffix in ('.elf', '_debug.elf', '_temp.elf', '.bin-zsk.bin', '.elf-zsk.bin'):
            changed = dict(packet); name = 'app.ino' + suffix
            changed[name] = b'BAD!' + changed[name][4:]
            with self.subTest(artifact=name), self.assertRaises(ValueError):
                self.invoke('validate_artifacts', changed)
        with self.assertRaises(ValueError):
            self.invoke('validate_artifacts', packet, exported_flat_package=packet['app.ino.bin-zsk.bin'] + b'x')
        snapshots = dict(self.snapshots); key = next(iter(snapshots)); snapshots[key] += b'\n'
        with mock.patch.object(builtins, 'exec', side_effect=AssertionError('Bad snapshot executed')):
            with self.assertRaises(ValueError):
                self.invoke('validate_artifacts', packet, snapshots=snapshots)


class RemoteContract(unittest.TestCase):
    def setUp(self):
        if sys.platform == 'win32' and 'pwd' not in sys.modules:
            sentinel = types.ModuleType('pwd')
            sentinel.getpwuid = lambda *args: (_ for _ in ()).throw(AssertionError('Windows account call'))
            self.addCleanup(lambda: sys.modules.pop('pwd', None))
            sys.modules['pwd'] = sentinel
        self.subject = load(ROOT / REMOTE, '_b7_remote_subject')
        prefix = 'state/analysis/P7_static_link_probe_raw/'
        names = dict(helper=prefix + 'static_remote.py', policy=POLICY,
            adapter='tools/app_motor_fault_static_policy.py', common='tools/app_build_policy.py',
            static_policy=prefix + 'static_policy.py', reference=prefix + 'static_reference.json',
            extension=prefix + 'static_native_artifacts.py', base=prefix + 'static_artifacts.py',
            primitive='tools/b4_app_compile_remote.py')
        self.bundle = {name: (ROOT / path).read_bytes() for name, path in names.items()}
        self.selection = dict(profile='b7_brownout', motors_allowed=0, attempt='b7trial01', source_digest=SOURCE)

    def test_real_bundle_composition_and_all_changed_members_refuse_before_exec(self):
        primitive, sources = self.subject.load_bundle(self.bundle, **self.selection)
        self.assertEqual((primitive.REMOTE, primitive.BUILD, primitive.ARTIFACTS),
                         tuple(paths()[name] for name in ('remote', 'build', 'artifacts')))
        self.assertEqual(sources, {name: body for name, body in self.bundle.items() if name != 'primitive'})
        for key in self.bundle:
            for body in (self.bundle[key] + b'\n', bytearray(self.bundle[key])):
                changed = dict(self.bundle, **{key: body})
                with self.subTest(key=key), mock.patch.object(builtins, 'exec',
                        side_effect=AssertionError('Unverified bundle executed')), self.assertRaises((ValueError, TypeError)):
                    self.subject.load_bundle(changed, **self.selection)
        for profile in (*OLD_CALLER.PROFILES, 'match'):
            with self.assertRaises(ValueError):
                self.subject.owner_name(profile, 0, 'b7trial01', SOURCE)


class ControlledPipeline(PIPELINE):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.b7 = load(ROOT / CALLER, '_b7_controlled_subject')

    def setUp(self):
        super().setUp()
        (self.root / 'state/analysis/P2_b7_build_raw').mkdir(exist_ok=True)

    def owner(self, motors=0, attempt='b7controlled01'):
        owner = self.b7.make_owner(request(motors, attempt, '--execute', self.head), root=self.root)
        patched = mock.patch.dict(owner.admission.__func__.__globals__, {'_head_bytes': self.checked_head})
        patched.start(); self.addCleanup(patched.stop)
        self.patch(owner, 'git_state', lambda: (self.head, self.dirty))
        self.patch(owner.base, 'ADB', BASE['ADB'] if os.name == 'nt' else '/mnt/c/' + BASE['ADB'][3:])
        values = dict(FLAGS=owner.flags, BUILD=owner.build_path, ARTIFACTS=owner.artifacts,
                      REMOTE=owner.remote, ATTEMPT=owner.stage_attempt)
        BASE.update(values)
        for name, value in values.items():
            setattr(self.remote_fixture, name, value)
        return owner

    def test_b7_readonly_check_and_consumed_output_or_stage(self):
        owner = self.owner(); before = BASE['file_set'](self.root)
        with self.no_writes(), mock.patch.object(owner, 'direct', side_effect=AssertionError('Board call')):
            result = owner.check()
        self.assertEqual(BASE['file_set'](self.root), before)
        self.assertEqual((result['profile'], result['motors_allowed'], result['board_observed']),
                         ('b7_brownout', 0, False))
        self.assertEqual(owner.inputs['reviewed_head'], self.head)
        for path in (owner.output, owner.stage_owner):
            path.parent.mkdir(parents=True, exist_ok=True); path.mkdir()
            with mock.patch.object(owner, 'direct', side_effect=AssertionError('Board call')):
                self.reject(owner.check)
            path.rmdir()

    def test_b7_controlled_real_pipeline_is_one_compile_nine_closures_and_no_retry(self):
        owner = self.controlled(self.owner(motors=1))
        result = owner.run()
        self.assertEqual((result['status'], result['profile'], result['motors_allowed']),
                         ('COMPILE_CHECKED', 'b7_brownout', 1))
        self.assertEqual((owner.query_calls, owner.compiler_calls, len(self.packets)), (1, 1, 2))
        self.assertEqual([row['name'] for row in result['final_checks']],
            ['local', 'identity', 'initialization', 'builtins', 'remote_sources',
             'installed_pins', 'overrides', 'artifacts', 'artifact_sources'])
        self.assertTrue(all(row['status'] == 'PASS' for row in result['final_checks']))
        for packet in self.packets:
            command = packet['argv']
            self.assertIn('compiler.cpp.extra_flags=' + flags(1), command)
            self.assertIn('compiler.c.extra_flags=' + flags(1), command)
            self.assertTrue('--jobs=1' in command or command[command.index('--jobs') + 1] == '1')
            self.assertFalse(any(word in ('upload', '--upload', 'reset', 'monitor') for word in command))
        self.reject(owner.run)


def load_tests(loader, standard, pattern):
    # Select only these seven new methods; inherited historical tests stay preserved.
    return unittest.TestSuite([loader.loadTestsFromTestCase(PublicContract),
        loader.loadTestsFromTestCase(PolicyContract), loader.loadTestsFromTestCase(RemoteContract),
        ControlledPipeline('test_b7_readonly_check_and_consumed_output_or_stage'),
        ControlledPipeline('test_b7_controlled_real_pipeline_is_one_compile_nine_closures_and_no_retry')])


if __name__ == '__main__':
    if not sys.dont_write_bytecode:
        raise SystemExit('Run with Python -I -B')
    unittest.main(verbosity=2)
