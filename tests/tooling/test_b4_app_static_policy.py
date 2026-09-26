# Checks the adopted B4 snapshot policy independently of its implementation.
# Expectations come from the normative API and pinned historical validators.
# No new B4 implementation source has been inspected by this author.
import ast
import builtins
import copy
import hashlib
import importlib.util
import inspect
import io
import json
import os
import re
from pathlib import Path
import socket
import struct
import stat
import subprocess
import sys
import types
import unittest
from contextlib import ExitStack, contextmanager
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
SUBJECT = ROOT / 'tools/b4_app_static_policy.py'
RAW = 'state/analysis/P7_static_link_probe_raw/'
SNAPSHOT_PINS = {
    'tools/app_motor_fault_static_policy.py': (8262, '3e5d49e4a70c0cf6197e26b1ba5ce2b7e07601bf5d9250ba430f90d1f9eab270'),
    'tools/app_build_policy.py': (14956, 'adc7f42a3325381c3cf15122409dfe9d92db7ca187cb242e416fef356be667f8'),
    RAW + 'static_policy.py': (4836, 'ec3d8a5e8c4910bbdbbb96fb5123c8bb42b294ce9342c76db73b8d3b5eab7775'),
    RAW + 'static_reference.json': (17809, '1dc8ac6dec8534536acfcc4da73516416ea465cfcc1a349900fd13e210144a2b'),
    RAW + 'static_native_artifacts.py': (3718, 'cd52a29a32b8ae1da4bea51dd55d9011386dd4be0ca537195bb124d13031d6c0'),
}
PROJECT = 'app.ino'
FQBN = 'arduino:zephyr:unoq:link_mode=static'
SUFFIXES = ('.elf', '_debug.elf', '_temp.elf', '.bin', '.bin-zsk.bin', '.elf-zsk.bin', '.map')
ALIASES = {PROJECT + suffix: PROJECT + suffix for suffix in SUFFIXES}
BUILD = '/synthetic/b4/build'
DATA = '/synthetic/arduino-data'
APIS = ('validate_preflight', 'validate_compile_result', 'validate_artifacts')
METHODS = APIS[:2]
OLD_FLAGS = '-DMATCH=0 -DMOTORS_ALLOWED=0'

def flags(motors):
    return ('-DMATCH=0 -DMOTORS_ALLOWED=' + str(motors) +
            ' -DSUMOX_B4_STAND=1 -DSUMOX_P3_DRIVE_TEST=0'
            ' -DSUMOX_P3_TURN_TRIAL=0 -DSUMOX_P3_STOP_TRIAL=0'
            ' -DSUMOX_P4_REACTIVE=0 -DSUMOX_TIMING_EVIDENCE=0'
            ' -DSUMOX_P5_ABORT_TIMING=0 -DSUMOX_MOTOR_FAULT_PROBE=0')

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

@contextmanager
def no_effects_or_source_reads():
    with ExitStack() as stack:
        for owner, names in (
            (builtins, ('open',)),
            (io, ('open',)),
            (Path, ('open', 'read_bytes', 'read_text', 'write_bytes', 'write_text')),
            (subprocess, ('run', 'Popen', 'call', 'check_call', 'check_output')),
            (socket, ('socket', 'create_connection', 'getaddrinfo')),
            (os, ('open', 'system', 'popen', 'mkdir', 'makedirs',
                  'unlink', 'remove', 'rename', 'replace', 'rmdir', 'chmod')),
        ):
            for name in names:
                stack.enter_context(mock.patch.object(
                    owner, name, side_effect=AssertionError('Forbidden effect: ' + name)))
        yield

class DictSubclass(dict):
    pass

class StrSubclass(str):
    pass

class BytesSubclass(bytes):
    pass

class IntSubclass(int):
    pass

class SnapshotAdmissionCases:
    def test_all_public_apis_require_keyword_only_motors_and_snapshots(self):
        for name in APIS:
            call = getattr(self.policy, name)
            signature = inspect.signature(call)
            for key in ('motors_allowed', 'snapshots'):
                parameter = signature.parameters[key]
                self.assertEqual(parameter.kind, inspect.Parameter.KEYWORD_ONLY)
                self.assertIs(parameter.default, inspect.Parameter.empty)
            for missing in ('motors_allowed', 'snapshots'):
                args, kwargs = self.arguments(name, 0)
                del kwargs[missing]
                with self.subTest(name=name, missing=missing), no_effects_or_source_reads(), self.assertRaises(TypeError):
                    call(*args, **kwargs)

    def test_motors_rejects_every_nonexact_type_and_out_of_range_before_snapshots_or_exec(self):
        class Uninspectable:
            def __iter__(self):
                raise AssertionError('snapshot touched before motor admission')
            def __len__(self):
                raise AssertionError('snapshot touched before motor admission')
            def __getitem__(self, key):
                raise AssertionError('snapshot touched before motor admission')
        class HostileDict(dict):
            def keys(self):
                raise AssertionError('snapshot touched before motor admission')
            def items(self):
                raise AssertionError('snapshot touched before motor admission')
            def values(self):
                raise AssertionError('snapshot touched before motor admission')
            def __iter__(self):
                raise AssertionError('snapshot touched before motor admission')
            def __len__(self):
                raise AssertionError('snapshot touched before motor admission')
        invalid = (None, False, True, 0.0, 1.0, '0', '1', b'0', -1, 2, 255,
                   IntSubclass(0), IntSubclass(1))
        for name in APIS:
            for motors in invalid:
                for snapshots in (Uninspectable(), HostileDict()):
                    args, kwargs = self.arguments(name, 0)
                    kwargs.update(motors_allowed=motors, snapshots=snapshots)
                    baseline = dict(kwargs, snapshots=dict(self.snapshots))
                    with no_effects_or_source_reads(), \
                         mock.patch('builtins.exec', side_effect=AssertionError('exec before motor admission')), \
                         mock.patch('hashlib.sha256', side_effect=AssertionError('hash before motor admission')), \
                         self.assertRaises((TypeError, ValueError)) as expected:
                        getattr(self.policy, name)(*args, **baseline)
                    with self.subTest(name=name, motors=repr(motors)), no_effects_or_source_reads(), \
                         mock.patch('builtins.exec', side_effect=AssertionError('exec before admission')), \
                         mock.patch('hashlib.sha256', side_effect=AssertionError('hash before motor admission')), \
                         self.assertRaises((TypeError, ValueError)) as received:
                        getattr(self.policy, name)(*args, **kwargs)
                    self.assertIs(type(received.exception), type(expected.exception))
                    self.assertEqual(received.exception.args, expected.exception.args)

    def test_every_snapshot_shape_size_hash_and_exact_type_rejects_before_exec(self):
        invalid = [None, [], tuple(self.snapshots.items()), DictSubclass(self.snapshots)]
        for path, original in self.snapshots.items():
            for mode in ('missing', 'extra', 'path_subclass', 'path_object', 'path_bytes', 'int_key', 'bytes_subclass',
                         'bytearray', 'memoryview', 'string', 'empty', 'short', 'long',
                         'changed_same_width', 'oversize'):
                candidate = dict(self.snapshots)
                if mode == 'missing':
                    del candidate[path]
                elif mode == 'extra':
                    candidate[path + '.extra'] = original
                elif mode in ('path_subclass', 'path_object', 'path_bytes', 'int_key'):
                    del candidate[path]
                    key = {'path_subclass': StrSubclass(path), 'path_object': Path(path),
                           'path_bytes': path.encode(), 'int_key': 7}[mode]
                    candidate[key] = original
                else:
                    value = {
                        'bytes_subclass': lambda: BytesSubclass(original),
                        'bytearray': lambda: bytearray(original),
                        'memoryview': lambda: memoryview(original),
                        'string': lambda: original.decode(),
                        'empty': lambda: b'',
                        'short': lambda: original[:-1],
                        'long': lambda: original + b' ',
                        'changed_same_width': lambda: bytes([original[0] ^ 1]) + original[1:],
                        'oversize': lambda: bytes(65537),
                    }[mode]()
                    candidate[path] = value
                invalid.append(candidate)
        for name in APIS:
            for index, candidate in enumerate(invalid):
                args, kwargs = self.arguments(name, 0)
                kwargs['snapshots'] = candidate
                with self.subTest(name=name, candidate=index), no_effects_or_source_reads(), \
                     mock.patch('builtins.exec', side_effect=AssertionError('exec before admission')), \
                     self.assertRaises((TypeError, ValueError)):
                    getattr(self.policy, name)(*args, **kwargs)

    def test_each_call_revalidates_snapshots_without_cache_or_input_mutation(self):
        for name in APIS:
            snapshots = dict(self.snapshots)
            args, kwargs = self.arguments(name, 0)
            kwargs['snapshots'] = snapshots
            before = dict(snapshots)
            with no_effects_or_source_reads():
                getattr(self.policy, name)(*args, **kwargs)
            self.assertEqual(snapshots, before)
            for key, value in before.items():
                self.assertIs(snapshots[key], value)
            for path, original in before.items():
                snapshots[path] = bytes([original[0] ^ 1]) + original[1:]
                with no_effects_or_source_reads(), mock.patch('builtins.exec', side_effect=AssertionError('cached admission')), \
                     self.assertRaises((TypeError, ValueError)):
                    getattr(self.policy, name)(*args, **kwargs)
                snapshots[path] = original
            with no_effects_or_source_reads():
                getattr(self.policy, name)(*args, **kwargs)
            self.assertEqual(snapshots, before)

    def test_private_profiles_m0_m1_m0_are_isolated_and_original_modules_are_unchanged(self):
        for name in APIS:
            results = []
            for motors in (0, 1, 0):
                args, kwargs = self.arguments(name, motors)
                with no_effects_or_source_reads():
                    results.append(getattr(self.policy, name)(*args, **kwargs))
            self.assertEqual(results[0], results[2])
            if name == 'validate_artifacts':
                self.assertEqual([r['motors_allowed'] for r in results], [0, 1, 0])
                self.assertEqual([r['flags'] for r in results], [flags(m) for m in (0, 1, 0)])
                results[0]['artifact_aliases']['mutated'] = 'mutation'
                self.assertNotIn('mutated', results[2]['artifact_aliases'])
            else:
                self.assertNotEqual(results[0], results[1])
                self.assertEqual(results[0], self.properties(motors=0))
                self.assertEqual(results[1], self.properties(motors=1))
                results[0]['mutated'] = 'mutation'
                self.assertNotIn('mutated', results[2])
        self.assertEqual(self.snapshots, self.original_snapshots)

    def test_snapshot_map_is_copied_before_first_private_execution(self):
        original_exec = builtins.exec
        for name in APIS:
            caller_map = dict(self.snapshots)
            args, kwargs = self.arguments(name, 0)
            kwargs['snapshots'] = caller_map
            executed = []
            def observe_exec(source, globals=None, locals=None, **extra):
                if not executed:
                    caller_map.clear()
                    caller_map['unexpected'] = b'not admitted'
                executed.append(True)
                return original_exec(source, globals, locals, **extra)
            with no_effects_or_source_reads(), mock.patch('builtins.exec', side_effect=observe_exec):
                result = getattr(self.policy, name)(*args, **kwargs)
            self.assertTrue(executed)
            self.assertEqual(caller_map, {'unexpected': b'not admitted'})
            if name == 'validate_artifacts':
                self.assertEqual(result['status'], 'STATIC_B4_APP_LAYOUT_PACKAGE_PASS')
                self.assertEqual(result['motors_allowed'], 0)
            else:
                self.assertEqual(result, self.properties(motors=0))



    def test_existing_historical_module_names_and_globals_are_not_mutated(self):
        names = ('app_build_policy', 'static_policy', 'sumox_static_common_policy',
                 'app_motor_fault_static_policy')
        modules = {name: types.ModuleType(name) for name in names}
        for name, module in modules.items():
            module.sentinel = object()
            module.PROJECT = 'untouched-' + name
            module.FLAGS = 'untouched-flags'
        before = {name: dict(vars(module)) for name, module in modules.items()}
        with mock.patch.dict(sys.modules, modules):
            for motors in (0, 1, 0):
                for name in APIS:
                    args, kwargs = self.arguments(name, motors)
                    with no_effects_or_source_reads():
                        getattr(self.policy, name)(*args, **kwargs)
            for name, module in modules.items():
                self.assertIs(sys.modules[name], module)
                self.assertEqual(vars(module), before[name])

TLS = {'_TLS_MODULE_BASE_': 8, '_rand_next': 8, 'z_tls_current': 16,
       'errno': 20, '_strtok_last': 24, '_localtime_buf': 28}
TLS_SHA = '68bb147615813666d528b9bd650e02fb8e240f0db841939e8460d7a52fd2ee70'
BASE_SHA = 'd30372dd4b8fb8c2661d00affc4a215cc88e3f62511995ff6303827bed4b7368'
LOADER_SHA = '39d4a4fd47241663323f6e04f94dd8f5a9f9ad6582cf1df37f9709b74026adcd'

INPUT_PINS = {'state/analysis/P7_static_link_probe_test_draft/test_static_policy.py': {'bytes': 20240, 'sha256': '5c1b7a771c7982061e9a97db0c0dabd42f3a47a4ee8e5f6fff263a8845da36d1'}, 'state/analysis/P7_static_artifact_test_draft/synthetic_elf.py': {'bytes': 7632, 'sha256': '503a04ea49e6452725cc489101dd3dbf7b8231c2dddac9198fdb01b7bfb2f2ef'}, 'state/analysis/P7_static_native_tls_test_draft/synthetic_native_elf.py': {'bytes': 2542, 'sha256': '5a86d5dcde5822d87d51369f943605a702b3918e39fa992e1da4798402683e15'}, 'state/analysis/P7_static_tls_raw/observed/tls-syms.S': {'bytes': 977, 'sha256': '68bb147615813666d528b9bd650e02fb8e240f0db841939e8460d7a52fd2ee70'}, 'state/analysis/P7_static_link_probe_raw/static_artifacts.py': {'bytes': 18322, 'sha256': 'd30372dd4b8fb8c2661d00affc4a215cc88e3f62511995ff6303827bed4b7368'}, 'tests/tooling/test_app_motor_fault_static_policy.py': {'bytes': 36715, 'sha256': 'e6d52ec6b0d72e893511793e9d92003092499280454093c9b6622d0e18547d5c'}, 'state/analysis/P7_b4_app_policy_contract.md': {'bytes': 3996, 'sha256': '1d6ffa2f49ba5a7925e1fbfc70a80a73a22dc0b5cc04a936b318eb97159d52c7'}}

def checked(relative):
    raw = (ROOT / relative).read_bytes()
    expected = INPUT_PINS[relative]
    if (len(raw), sha(raw)) != (expected['bytes'], expected['sha256']):
        raise AssertionError('Historical fixture input drift: ' + relative)
    return raw

def load_bytes(name, raw, path):
    module = types.ModuleType(name)
    module.__file__ = str(path)
    with mock.patch.dict(sys.modules, {name: module}):
        exec(compile(raw, str(path), 'exec'), module.__dict__)
    return module

def digest(raw):
    return sha(raw)

def literal_once(template, build, data):
    values = {'BUILD_PATH': build, 'DATA_DIR': data}
    return re.sub(r'@(BUILD_PATH|DATA_DIR)@', lambda match: values[match[1]], template)

@contextmanager
def observed_calls(names):
    calls = []
    previous = sys.getprofile()
    def observe(frame, event, unused):
        if event == 'call' and frame.f_code.co_name in names:
            calls.append((frame.f_globals, dict(frame.f_locals)))
    sys.setprofile(observe)
    try:
        yield calls
    finally:
        sys.setprofile(previous)

class Fixture(unittest.TestCase):
    motors = 0

    @classmethod
    def setUpClass(cls):
        cls.snapshots = {}
        for path, expected in SNAPSHOT_PINS.items():
            raw = (ROOT / path).read_bytes()
            if (len(raw), sha(raw)) != expected:
                raise AssertionError('Snapshot fixture drift: ' + path)
            cls.snapshots[path] = raw
        cls.original_snapshots = dict(cls.snapshots)
        for path in INPUT_PINS:
            checked(path)
        cls.reference = json.loads(cls.snapshots[RAW + 'static_reference.json'])
        p = 'state/analysis/P7_static_link_probe_test_draft/test_static_policy.py'
        cls.support = load_bytes('_d213_metadata_fixtures', checked(p), ROOT / p)
        p = 'state/analysis/P7_static_artifact_test_draft/synthetic_elf.py'
        cls.base = load_bytes('synthetic_elf', checked(p), ROOT / p)
        p = 'state/analysis/P7_static_native_tls_test_draft/synthetic_native_elf.py'
        with mock.patch.dict(sys.modules, {'synthetic_elf': cls.base}):
            cls.fixture = load_bytes('_d213_native_fixtures', checked(p), ROOT / p)
        cls.native_source = checked('state/analysis/P7_static_tls_raw/observed/tls-syms.S')
        cls.frozen_source = checked(RAW + 'static_artifacts.py')
        # This is the first subject read by the oracle at its separately authorized run.
        subject_bytes = SUBJECT.read_bytes()
        with no_effects_or_source_reads():
            cls.policy = load_bytes('_d213_subject', subject_bytes, SUBJECT)

    @classmethod
    def tearDownClass(cls):
        if cls.snapshots != cls.original_snapshots:
            raise AssertionError('Caller snapshot fixture was mutated')
        for path, expected in SNAPSHOT_PINS.items():
            raw = (ROOT / path).read_bytes()
            if (len(raw), sha(raw)) != expected:
                raise AssertionError('Historical snapshot file was changed')

    def properties(self, build=BUILD, data=DATA, *, motors=None):
        motors = self.motors if motors is None else motors
        result = self.support.public_properties(self.reference, build, data)
        for key, template in self.reference.items():
            result[key] = literal_once(template.replace(OLD_FLAGS, flags(motors)), build, data)
        result['build.project_name'] = PROJECT
        return result

    def envelope(self, build=BUILD, data=DATA, *, motors=None):
        result = self.support.public_envelope(self.reference, build, data)
        result['builder_result']['build_properties'] = [
            key + '=' + value for key, value in self.properties(build, data, motors=motors).items()]
        return result

    def metadata(self, method, envelope, build=BUILD, data=DATA):
        text = json.dumps(envelope) if isinstance(envelope, dict) else envelope
        with no_effects_or_source_reads():
            return getattr(self.policy, method)(text, build_path=build, data_dir=data,
                    motors_allowed=self.motors, snapshots=dict(self.snapshots))

    def reject_metadata(self, envelope, build=BUILD, data=DATA, methods=METHODS):
        for method in methods:
            with self.subTest(method=method), self.assertRaises(ValueError):
                self.metadata(method, envelope, build, data)

    def packet(self, legacy=None):
        return dict(self.fixture.packet() if legacy is None else legacy)

    def direct_artifacts(self, packet, native, frozen, *, exported_flat_package):
        with no_effects_or_source_reads():
            return self.policy.validate_artifacts(packet, native, frozen,
                    exported_flat_package=exported_flat_package,
                    motors_allowed=self.motors, snapshots=dict(self.snapshots))

    def artifacts(self, packet, *, exported=None, native=None, frozen=None):
        if exported is None:
            exported = packet[PROJECT + '.bin-zsk.bin']
        with no_effects_or_source_reads():
            return self.direct_artifacts(packet, self.native_source if native is None else native,
                    self.frozen_source if frozen is None else frozen,
                    exported_flat_package=exported)

    def reject_artifacts(self, packet, **kwargs):
        with self.assertRaises(ValueError):
            self.artifacts(packet, **kwargs)

    def arguments(self, name, motors):
        kwargs = dict(motors_allowed=motors, snapshots=dict(self.snapshots))
        if name == 'validate_artifacts':
            packet = self.packet()
            kwargs['exported_flat_package'] = packet[PROJECT + '.bin-zsk.bin']
            return (packet, self.native_source, self.frozen_source), kwargs
        kwargs.update(build_path=BUILD, data_dir=DATA)
        return (json.dumps(self.envelope(motors=motors)),), kwargs

class MetadataCases:
    def test_constants_and_reference_substitution_counts_are_exact(self):
        self.assertEqual(flags(self.motors).split(), [
            '-DMATCH=0', '-DMOTORS_ALLOWED=' + str(self.motors), '-DSUMOX_B4_STAND=1',
            '-DSUMOX_P3_DRIVE_TEST=0', '-DSUMOX_P3_TURN_TRIAL=0', '-DSUMOX_P3_STOP_TRIAL=0',
            '-DSUMOX_P4_REACTIVE=0', '-DSUMOX_TIMING_EVIDENCE=0',
            '-DSUMOX_P5_ABORT_TIMING=0', '-DSUMOX_MOTOR_FAULT_PROBE=0'])
        self.assertEqual(len(self.reference), 84)
        self.assertEqual(sum(value.count('app.ino') for value in self.reference.values()), 24)
        self.assertEqual(sum(value.count(OLD_FLAGS) for value in self.reference.values()), 5)


    def test_both_interfaces_accept_and_return_complete_actual_properties(self):
        for method in METHODS:
            envelope = self.envelope()
            before = copy.deepcopy(envelope)
            with self.subTest(method=method):
                actual = self.metadata(method, envelope)
                self.assertEqual(actual, self.properties())
                self.assertTrue(all(type(k) is str and type(v) is str for k, v in actual.items()))
                self.assertEqual(envelope, before)


    def test_raw_text_and_caller_paths_reach_historical_validator_unchanged(self):
        build = '/synthetic/app.ino/@DATA_DIR@/build'
        data = '/synthetic/app.ino/@BUILD_PATH@/data'
        envelope = self.envelope(build, data)
        envelope['compiler_out'] = 'app.ino ' + OLD_FLAGS + ' @DATA_DIR@'
        text = json.dumps(envelope, indent=3)
        for method in METHODS:
            with observed_calls(METHODS) as calls:
                result = self.metadata(method, text, build, data)
            delegated = [args for scope, args in calls if scope is not self.policy.__dict__]
            self.assertTrue(delegated, 'The unchanged historical validator must run')
            for args in delegated:
                self.assertIs(args['text'], text)
                self.assertIs(args['build_path'], build)
                self.assertIs(args['data_dir'], data)
            self.assertEqual(result, self.properties(build, data))


    def test_inserted_paths_are_substituted_once_and_never_name_rewritten(self):
        cases = (('/literal/app.ino/build', '/literal/app.ino/data'),
                 ('/literal/@BUILD_PATH@/@DATA_DIR@/build', DATA),
                 (BUILD, '/literal/@DATA_DIR@/@BUILD_PATH@/data'),
                 ('/literal/@DATA_DIR@/build', '/literal/@BUILD_PATH@/data'))
        for build, data in cases:
            for method in METHODS:
                with self.subTest(method=method, build=build, data=data):
                    self.assertEqual(self.metadata(method, self.envelope(build, data), build, data),
                                     self.properties(build, data))


    def test_recursively_expanded_or_rewritten_command_paths_fail(self):
        build, data = '/literal/app.ino/@DATA_DIR@/build', DATA
        correct = self.properties(build, data)['recipe.c.combine.2.pattern']
        for wrong in (literal_once(correct, build, data), correct.replace('app.ino', 'app_motor_fault.ino')):
            envelope = self.envelope(build, data)
            self.assertNotEqual(wrong, correct)
            self.support.replace_property(envelope, 'recipe.c.combine.2.pattern', wrong)
            self.reject_metadata(envelope, build, data)


    def test_original_project_and_old_flags_fail_even_when_coherent(self):
        self.reject_metadata(self.support.public_envelope(self.reference, BUILD, DATA))
        for key, value in (('build.project_name', 'app_motor_fault.ino'),
                           ('compiler.c.extra_flags', OLD_FLAGS),
                           ('compiler.cpp.extra_flags', OLD_FLAGS)):
            envelope = self.envelope()
            self.support.replace_property(envelope, key, value)
            self.reject_metadata(envelope)


    def test_fixed_profile_rejects_each_unreviewed_alternative(self):
        cases = {
            'build.fqbn': ('arduino:zephyr:unoq', 'arduino:zephyr:unoq:link_mode=dynamic',
                           FQBN + ',wait_linux_boot=no', FQBN + ',wait_linux_boot=yes'),
            'build.link_mode': ('dynamic', '', 'static '),
            'build.boot_mode': ('immediate', 'app', ''),
            'build.project_name': ('other.ino', 'app_motor_fault.ino', PROJECT + ' '),
            'build.library_discovery_phase_flag': ('', '-DARDUINO_LIBRARY_DISCOVERY_PHASE=1'),
            'compiler.c.extra_flags': (flags(self.motors).replace('MATCH=0', 'MATCH=1'),
                                       flags(1 - self.motors),
                                       flags(self.motors).replace('PROBE=0', 'PROBE=1'), flags(self.motors) + ' -DEXTRA=1'),
            'compiler.cpp.extra_flags': (flags(self.motors).replace('MATCH=0', 'MATCH=1'),
                                         flags(1 - self.motors),
                                         flags(self.motors).replace('PROBE=0', 'PROBE=1'), flags(self.motors) + ' -DEXTRA=1'),
        }
        for key, values in cases.items():
            for value in values:
                envelope = self.envelope()
                self.support.replace_property(envelope, key, value)
                with self.subTest(key=key, value=value):
                    self.reject_metadata(envelope)


    def test_every_controlled_command_is_required_and_literal(self):
        expected = self.properties()
        for key in self.reference:
            for value in (None, expected[key] + ' UNREVIEWED'):
                envelope = self.envelope()
                self.support.replace_property(envelope, key, value)
                with self.subTest(key=key, value=value):
                    self.reject_metadata(envelope)


    def test_extra_controlled_keys_and_duplicate_properties_fail(self):
        for prefix in self.support.PREFIXES:
            envelope = self.envelope()
            self.support.replace_property(envelope, prefix + 'unreviewed', '')
            with self.subTest(extra=prefix):
                self.reject_metadata(envelope)
        for key in ('build.project_name', 'build.fqbn', *self.reference):
            envelope = self.envelope()
            rows = envelope['builder_result']['build_properties']
            rows.append(next(row for row in rows if row.startswith(key + '=')))
            with self.subTest(duplicate=key):
                self.reject_metadata(envelope)


    def test_all_required_uncontrolled_metadata_is_exact(self):
        properties = self.properties()
        for key in set(properties) - set(self.reference):
            for value in (None, properties[key] + ' UNREVIEWED'):
                envelope = self.envelope()
                self.support.replace_property(envelope, key, value)
                with self.subTest(key=key, value=value):
                    self.reject_metadata(envelope)


    def test_platform_version_core_and_variant_bind_to_caller_data(self):
        for section in ('board_platform', 'build_platform'):
            for field, value in (('id', 'other:zephyr'), ('version', '1.0.1'),
                                 ('install_dir', '/other/platform')):
                envelope = self.envelope()
                envelope['builder_result'][section][field] = value
                with self.subTest(section=section, field=field):
                    self.reject_metadata(envelope)
        self.reject_metadata(self.envelope(data='/different/data'))
        self.reject_metadata(self.envelope(build='/different/build'))


    def test_noncanonical_or_unsafe_path_arguments_fail(self):
        paths = (None, 1, '', '/', 'relative', '//host/path', '/tmp/../build',
                 '/tmp/./build', '/tmp//build', '/tmp/build/', '/tmp/a\\b',
                 '/tmp/"bad', "/tmp/'bad", '/tmp/`bad', '/tmp/$bad',
                 '/tmp/line\nbreak', '/tmp/null\0byte', '/tmp/\x7f')
        for path in paths:
            with self.subTest(build=repr(path)):
                self.reject_metadata(self.envelope(), build=path)
            with self.subTest(data=repr(path)):
                self.reject_metadata(self.envelope(), data=path)


    def test_compile_rejects_external_libraries_and_preserves_absent_default(self):
        for libraries in ([{'name': 'Unreviewed'}], ['Unreviewed'], [None], {}, '',
                          None, False, 0):
            envelope = self.envelope()
            envelope['builder_result']['used_libraries'] = libraries
            with self.subTest(libraries=repr(libraries)):
                self.reject_metadata(envelope, methods=('validate_compile_result',))
                self.assertEqual(self.metadata('validate_preflight', envelope), self.properties())
        envelope = self.envelope()
        del envelope['builder_result']['used_libraries']
        self.assertEqual(self.metadata('validate_compile_result', envelope), self.properties())


    def test_json_rejects_duplicates_nonfinite_malformed_and_wrong_types(self):
        text = json.dumps(self.envelope())
        bad = (None, False, 0, [], {}, b'{}', '', 'null', '[]', '1', '{',
               text + '{}', '{"success":true,' + text[1:],
               text.replace('"build_path":', '"build_path":"duplicate","build_path":', 1))
        for value in bad:
            with self.subTest(text=repr(value)[:100]):
                self.reject_metadata(value)
        for token in ('NaN', 'Infinity', '-Infinity', '1e10000'):
            with self.subTest(nonfinite=token):
                self.reject_metadata('{"unused":' + token + ',' + text[1:])


    def test_json_result_and_builder_shapes_remain_strict(self):
        cases = {'success': (False, 1, 'true', None),
                 'error': ('failed', None, False, 0, [], {}),
                 'upload_result': ({'success': True}, None, False, 0, '', []),
                 'compiler_out': (None, False, 0, [], {}),
                 'compiler_err': (None, False, 0, [], {}),
                 'builder_result': (None, False, 1, '', [], {})}
        for key, values in cases.items():
            for value in values:
                envelope = self.envelope()
                envelope[key] = value
                with self.subTest(key=key, value=value):
                    self.reject_metadata(envelope)
        for properties in (None, '', 1, {}, [], ['no-equals'], ['=empty'], [None]):
            envelope = self.envelope()
            envelope['builder_result']['build_properties'] = properties
            self.reject_metadata(envelope)


    def test_exact_order_all_ten_macros_and_coherent_opposite_profile_are_rejected(self):
        current = flags(self.motors)
        tokens = current.split()
        alternatives = [
            ' '.join(reversed(tokens)),
            ' '.join(tokens[:2] + tokens[3:]),
            current + ' ' + tokens[0],
            current + ' -DEXTRA=0',
            flags(1 - self.motors),
            current.replace('SUMOX_B4_STAND=1', 'SUMOX_B4_STAND=0'),
        ]
        for token in tokens[3:]:
            alternatives.append(current.replace(token, token[:-1] + '1'))
        for alternative in alternatives:
            self.assertNotEqual(alternative, current)
            envelope = self.envelope()
            properties = self.properties()
            for key, value in properties.items():
                if current in value:
                    self.support.replace_property(envelope, key, value.replace(current, alternative))
            self.reject_metadata(envelope)

class ArtifactCases:
    def expected_report(self, packet):
        fields = ('name', 'type', 'flags', 'address', 'size', 'alignment', 'load_address')
        flash, ram, bss_end = 0x08100010, 0x20013890, 0x20013c00
        rows = [('.text', 1, 6, flash, 8, 4, flash),
                ('.rodata', 1, 2, flash + 16, 8, 4, flash + 16),
                ('.data', 1, 3, ram, 8, 4, flash + 32),
                ('.bss', 8, 3, ram + 8, bss_end - ram - 8, 8, None)]
        return {
            'status': 'STATIC_NATIVE_TLS_LAYOUT_PACKAGE_PASS', 'entry': flash | 1,
            'flash': {'start': flash, 'end': flash + 40, 'remaining': 0x081c0000 - flash - 40},
            'ram': {'start': ram, 'end': bss_end, 'remaining': 0x20053890 - bss_end},
            'data_copy': {'source': flash + 32, 'destination': ram, 'bytes': 8},
            'bss_zero': {'start': ram + 8, 'end': ram + 24, 'bytes': 16},
            'sections': [dict(zip(fields, row)) for row in rows],
            'weak_undefined': ['optional_weak_hook'],
            'artifacts': {old: {'bytes': len(packet[actual]), 'sha256': digest(packet[actual])}
                          for actual, old in ALIASES.items()},
            'native_tls': {
                'source_sha256': TLS_SHA, 'loader_sha256': LOADER_SHA,
                'symbols': [{'name': name, 'value': value, 'size': 0, 'bind': 1,
                             'type': 6, 'other': 0, 'section': 0xfff1}
                            for name, value in sorted(TLS.items())]},
        }


    def expected(self, packet):
        return {'status': 'STATIC_B4_APP_LAYOUT_PACKAGE_PASS',
                'project': PROJECT, 'fqbn': FQBN, 'flags': flags(self.motors),
                'motors_allowed': self.motors,
                'artifact_aliases': dict(ALIASES),
                'artifact_sha256': {name: digest(value) for name, value in packet.items()},
                'validator_report': self.expected_report(packet)}


    def test_exact_success_contains_unmodified_complete_legacy_report(self):
        packet = self.packet()
        before = dict(packet)
        identities = {name: id(value) for name, value in packet.items()}
        result = self.artifacts(packet)
        self.assertEqual(result, self.expected(packet))
        self.assertEqual(json.loads(json.dumps(result, allow_nan=False)), result)
        self.assertEqual(packet, before)
        self.assertEqual({name: id(value) for name, value in packet.items()}, identities)
        self.assertEqual(self.artifacts(packet), result)


    def test_real_validator_receives_exact_seven_original_byte_objects(self):
        packet = self.packet()
        with observed_calls(('validate_artifacts',)) as calls:
            result = self.artifacts(packet)
        delegated = [args for scope, args in calls if scope is not self.policy.__dict__
                     and set(args.get('artifacts', ())) == set(ALIASES.values())]
        self.assertTrue(delegated, 'Real D147/D142 validation must run')
        native_calls = [args for args in delegated if 'native_tls_source' in args]
        self.assertTrue(native_calls, 'Exact D147 source/TLS validation must run')
        for args in delegated:
            for actual, old in ALIASES.items():
                self.assertIs(args['artifacts'][old], packet[actual])
        for args in native_calls:
            self.assertIs(args['native_tls_source'], self.native_source)
            self.assertIs(args['frozen_validator_source'], self.frozen_source)
        self.assertEqual(result, self.expected(packet))


    def test_returned_dictionaries_are_isolated_between_calls(self):
        packet = self.packet()
        result = self.artifacts(packet)
        result['artifact_aliases'].clear()
        result['artifact_sha256'].clear()
        result['validator_report']['native_tls']['symbols'][0]['value'] = 99
        self.assertEqual(self.artifacts(packet), self.expected(packet))


    def test_each_required_actual_filename_and_only_those_names(self):
        for missing in ALIASES:
            packet = self.packet()
            del packet[missing]
            with self.subTest(missing=missing):
                self.reject_artifacts(packet, exported=b'export is supplied separately')
        self.reject_artifacts({'app_motor_fault.ino' + suffix: self.fixture.packet()['app.ino' + suffix]
                               for suffix in SUFFIXES}, exported=b'legacy keys')
        for extra in (*('app_motor_fault.ino' + suffix for suffix in SUFFIXES),
                      'app_motor_fault.ino.hex', 'other.ino.elf', 7):
            packet = self.packet()
            packet[extra] = b'extra'
            with self.subTest(extra=extra):
                self.reject_artifacts(packet)


    def test_artifact_container_and_each_value_type_or_empty_are_rejected(self):
        for packet in (None, [], (), 'artifacts', list(self.packet().items())):
            self.reject_artifacts(packet, exported=b'flat')
        for name in ALIASES:
            for value in (b'', None, 'bytes', bytearray(b'bytes'), memoryview(b'bytes'),
                          BytesSubclass(b'bytes'), 1):
                packet = self.packet()
                exported = packet[PROJECT + '.bin-zsk.bin']
                packet[name] = value
                with self.subTest(name=name, value=repr(value)):
                    self.reject_artifacts(packet, exported=exported)


    def test_export_must_be_bytes_and_exactly_equal_build_flat_package(self):
        packet = self.packet()
        flat = packet[PROJECT + '.bin-zsk.bin']
        for export in (b'', b'x' + flat[1:], flat[:-1], flat + b'\0',
                       packet[PROJECT + '.bin'], bytearray(flat), memoryview(flat), '', False):
            with self.subTest(export=repr(export)[:60]):
                self.reject_artifacts(packet, exported=export)
        with self.assertRaises(ValueError):
            self.direct_artifacts(packet, self.native_source, self.frozen_source,
                                           exported_flat_package=None)
        equal_copy = bytes(bytearray(flat))
        self.assertEqual(self.artifacts(packet, exported=equal_copy), self.expected(packet))


    def test_native_and_frozen_source_types_bounds_and_hashes_remain_enforced(self):
        for field, source, bound in (('native', self.native_source, 65536),
                                     ('frozen', self.frozen_source, 32768)):
            for value in (b'', source + b'\n', b'x' * (bound + 1), bytearray(source),
                          memoryview(source), BytesSubclass(source), 'not bytes', 1, False):
                with self.subTest(field=field, value_type=type(value).__name__):
                    self.reject_artifacts(self.packet(), **{field: value})
        for native, frozen in ((None, self.frozen_source), (self.native_source, None)):
            with self.assertRaises(ValueError):
                packet = self.packet()
                self.direct_artifacts(packet, native, frozen,
                                               exported_flat_package=packet[PROJECT + '.bin-zsk.bin'])


    def alter(self, change, image=None):
        images = self.fixture.ELF_NAMES if image is None else (image,)
        return self.packet(self.base.mutate_elfs(self.fixture.packet(), change, images))


    def test_each_of_six_tls_names_is_required_in_every_elf(self):
        self.reject_artifacts(self.packet(self.base.packet()))
        for image in self.fixture.ELF_NAMES:
            for name in TLS:
                with self.subTest(image=image, name=name):
                    self.reject_artifacts(self.alter(lambda elf: self.fixture.replace_symbols(
                        elf, [row for row in self.fixture.symbol_rows(elf) if row[0] != name]), image))


    def test_each_tls_tuple_field_in_each_image_is_checked(self):
        changes = {'value': 9, 'size': 1, 'info': 0x26, 'other': 1, 'section': 3}
        for image in self.fixture.ELF_NAMES:
            for name in TLS:
                for field, value in changes.items():
                    with self.subTest(image=image, name=name, field=field):
                        self.reject_artifacts(self.alter(lambda elf: self.base.edit_symbol(
                            elf, name, field, value), image))


    def test_wrong_tls_type_duplicate_or_additional_symbols_fail(self):
        for image in self.fixture.ELF_NAMES:
            for name in TLS:
                for info in (0x10, 0x11, 0x12):
                    with self.subTest(image=image, name=name, info=info):
                        self.reject_artifacts(self.alter(lambda elf: self.base.edit_symbol(
                            elf, name, 'info', info), image))
                with self.subTest(image=image, duplicate=name):
                    self.reject_artifacts(self.alter(lambda elf: self.fixture.replace_symbols(
                        elf, self.fixture.symbol_rows(elf) +
                        [row for row in self.fixture.symbol_rows(elf) if row[0] == name]), image))
            for name in ('extra_tls', ''):
                self.reject_artifacts(self.alter(lambda elf: self.fixture.replace_symbols(
                    elf, self.fixture.symbol_rows(elf) + [(name, 8, 0, 0x16, 0, 0xfff1)]), image))


    def test_elf_identity_bounds_entry_and_initialization_rejections_propagate(self):
        changes = (lambda elf: b'NOPE' + elf[4:],
                   lambda elf: self.base.edit_header(elf, 'machine', 3),
                   lambda elf: self.base.edit_header(elf, 'entry', 0x08100013),
                   lambda elf: self.base.edit_header(elf, 'flags', 0x05000000),
                   lambda elf: self.base.edit_header(elf, 'shoff', len(elf) + 1),
                   lambda elf: self.base.edit_symbol(elf, '_sidata', 'value', 0x08100034),
                   lambda elf: self.base.edit_symbol(elf, '_ebss', 'value', 0x20014000),
                   lambda elf: self.base.edit_program(elf, 0, 'type', 7),
                   lambda elf: self.base.edit_section(elf, '.data', 'flags', 0x403))
        for image in self.fixture.ELF_NAMES:
            for index, change in enumerate(changes):
                with self.subTest(image=image, mutation=index):
                    self.reject_artifacts(self.alter(change, image))


    def test_all_three_allocated_images_must_agree(self):
        for image in self.fixture.ELF_NAMES:
            def change(elf):
                offset = self.base.section(elf, '.text')[2][4]
                return elf[:offset] + bytes([elf[offset] ^ 1]) + elf[offset + 1:]
            with self.subTest(image=image):
                self.reject_artifacts(self.alter(change, image))


    def test_flat_and_diagnostic_package_metadata_and_payload_rejections_propagate(self):
        for suffix in ('.bin-zsk.bin', '.elf-zsk.bin'):
            for offset in (7, 8, 12, 14, 15, 16):
                packet = self.packet()
                key = PROJECT + suffix
                value = packet[key]
                packet[key] = value[:offset] + bytes([value[offset] ^ 1]) + value[offset + 1:]
                with self.subTest(suffix=suffix, offset=offset):
                    self.reject_artifacts(packet)
        legacy = self.fixture.packet()
        for raw in (self.base.RAW + b'\0', self.base.RAW[:-1],
                    self.base.RAW[:8] + b'\1' + self.base.RAW[9:]):
            self.reject_artifacts(self.packet(self.base.replace_raw(legacy, raw)))


class SnapshotContract(SnapshotAdmissionCases, Fixture):
    pass

class MetadataM0(MetadataCases, Fixture):
    motors = 0

class MetadataM1(MetadataCases, Fixture):
    motors = 1

class ArtifactM0(ArtifactCases, Fixture):
    motors = 0

class ArtifactM1(ArtifactCases, Fixture):
    motors = 1

def load_tests(loader, unused, pattern):
    suite = unittest.TestSuite()
    for cls in (SnapshotContract, MetadataM0, MetadataM1, ArtifactM0, ArtifactM1):
        suite.addTests(loader.loadTestsFromTestCase(cls))
    if suite.countTestCases() != 65:
        raise AssertionError('Frozen selection must contain 65 methods')
    return suite

if __name__ == '__main__':
    unittest.main()
