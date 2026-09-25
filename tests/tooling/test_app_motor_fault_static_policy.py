# Checks D187's fixed metadata and artifact adapter against its public contracts.
# Keeps synthetic host evidence separate from compilation, source identity and hardware.
# Freeze this file before running Python -B; dependency fault copies use owned RAM only.
import builtins
import copy
from contextlib import contextmanager, ExitStack
import hashlib
import io
import json
import os
from pathlib import Path
import re
import socket
import stat
import subprocess
import sys
import tempfile
import types
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[2]
ADAPTER = Path('tools/app_motor_fault_static_policy.py')
RAW = Path('state/analysis/P7_static_link_probe_raw')
PROJECT = 'app_motor_fault.ino'
FQBN = 'arduino:zephyr:unoq:link_mode=static'
OLD_FLAGS = '-DMATCH=0 -DMOTORS_ALLOWED=0'
FLAGS = OLD_FLAGS + ' -DSUMOX_MOTOR_FAULT_PROBE=1'
BUILD = '/synthetic/diagnostic/build'
DATA = '/synthetic/arduino-data'
METHODS = ('validate_preflight', 'validate_compile_result')
PINS = {
    Path('tools/app_build_policy.py'):
        'adc7f42a3325381c3cf15122409dfe9d92db7ca187cb242e416fef356be667f8',
    RAW / 'static_policy.py':
        'ec3d8a5e8c4910bbdbbb96fb5123c8bb42b294ce9342c76db73b8d3b5eab7775',
    RAW / 'static_reference.json':
        '1dc8ac6dec8534536acfcc4da73516416ea465cfcc1a349900fd13e210144a2b',
    RAW / 'static_native_artifacts.py':
        'cd52a29a32b8ae1da4bea51dd55d9011386dd4be0ca537195bb124d13031d6c0',
}
SUFFIXES = ('.elf', '_debug.elf', '_temp.elf', '.bin', '.bin-zsk.bin',
            '.elf-zsk.bin', '.map')
ALIASES = {PROJECT + suffix: 'app.ino' + suffix for suffix in SUFFIXES}
TLS = {'_TLS_MODULE_BASE_': 8, '_rand_next': 8, 'z_tls_current': 16,
       'errno': 20, '_strtok_last': 24, '_localtime_buf': 28}
TLS_SHA = '68bb147615813666d528b9bd650e02fb8e240f0db841939e8460d7a52fd2ee70'
BASE_SHA = 'd30372dd4b8fb8c2661d00affc4a215cc88e3f62511995ff6303827bed4b7368'
LOADER_SHA = '39d4a4fd47241663323f6e04f94dd8f5a9f9ad6582cf1df37f9709b74026adcd'


class BytesSubclass(bytes):
    pass


def digest(data):
    return hashlib.sha256(data).hexdigest()


def load_module(name, path):
    # Source remains opaque to the author; loading occurs only during the frozen run.
    module = types.ModuleType(name)
    module.__file__ = str(path)
    with mock.patch.dict(sys.modules, {name: module}):
        exec(compile(path.read_bytes(), str(path), 'exec'), module.__dict__)
    return module


def literal_once(template, build, data):
    values = {'BUILD_PATH': build, 'DATA_DIR': data}
    return re.sub(r'@(BUILD_PATH|DATA_DIR)@', lambda match: values[match[1]], template)


@contextmanager
def no_external_effects():
    with ExitStack() as stack:
        for owner, names in ((subprocess, ('Popen', 'run', 'call', 'check_call',
                                         'check_output')),
                             (socket, ('socket', 'create_connection', 'getaddrinfo')),
                             (os, ('system', 'popen', 'mkdir', 'makedirs', 'unlink',
                                   'remove', 'rename', 'replace', 'rmdir', 'chmod'))):
            for name in names:
                stack.enter_context(mock.patch.object(
                    owner, name, side_effect=AssertionError('External effect: ' + name)))
        for owner in (builtins, io):
            original = owner.open

            def readonly(file, mode='r', *args, _open=original, **kwargs):
                if any(flag in mode for flag in 'wax+'):
                    raise AssertionError('Unexpected write')
                return _open(file, mode, *args, **kwargs)

            stack.enter_context(mock.patch.object(owner, 'open', readonly))
        original_open = os.open

        def readonly_descriptor(path, flags, *args, **kwargs):
            if flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND):
                raise AssertionError('Unexpected descriptor write')
            return original_open(path, flags, *args, **kwargs)

        stack.enter_context(mock.patch.object(os, 'open', readonly_descriptor))
        yield


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


class ContractFixture(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.originals = {path: (ROOT / path).read_bytes() for path in PINS}
        for path, expected in PINS.items():
            if digest(cls.originals[path]) != expected:
                raise RuntimeError('Historical input changed: ' + str(path))
        cls.reference = json.loads(cls.originals[RAW / 'static_reference.json'])
        # Permitted public helpers supply fixture mechanics, never validator outcomes.
        helpers = ROOT / 'state/analysis/P7_static_link_probe_test_draft/test_static_policy.py'
        cls.support = load_module('d187_public_metadata_helpers', helpers)
        base_path = ROOT / 'state/analysis/P7_static_artifact_test_draft/synthetic_elf.py'
        cls.base = load_module('d187_synthetic_elf', base_path)
        native_path = ROOT / 'state/analysis/P7_static_native_tls_test_draft/synthetic_native_elf.py'
        with mock.patch.dict(sys.modules, {'synthetic_elf': cls.base}):
            cls.fixture = load_module('d187_synthetic_native_elf', native_path)
        cls.native_source = (ROOT / 'state/analysis/P7_static_tls_raw/observed/tls-syms.S').read_bytes()
        cls.frozen_source = (ROOT / RAW / 'static_artifacts.py').read_bytes()
        if digest(cls.native_source) != TLS_SHA or digest(cls.frozen_source) != BASE_SHA:
            raise RuntimeError('Opaque source fixture identity changed')
        with no_external_effects():
            cls.policy = load_module('d187_adapter_under_test', ROOT / ADAPTER)

    @classmethod
    def tearDownClass(cls):
        for path, before in cls.originals.items():
            if (ROOT / path).read_bytes() != before:
                raise AssertionError('Historical input mutated: ' + str(path))

    def properties(self, build=BUILD, data=DATA):
        result = self.support.public_properties(self.reference, build, data)
        for key, template in self.reference.items():
            adapted = template.replace('app.ino', PROJECT).replace(OLD_FLAGS, FLAGS)
            result[key] = literal_once(adapted, build, data)
        result['build.project_name'] = PROJECT
        return result

    def envelope(self, build=BUILD, data=DATA):
        result = self.support.public_envelope(self.reference, build, data)
        result['builder_result']['build_properties'] = [
            key + '=' + value for key, value in self.properties(build, data).items()]
        return result

    def metadata(self, method, envelope, build=BUILD, data=DATA, policy=None):
        text = json.dumps(envelope) if isinstance(envelope, dict) else envelope
        with no_external_effects():
            return getattr(policy or self.policy, method)(text, build_path=build, data_dir=data)

    def reject_metadata(self, envelope, build=BUILD, data=DATA, methods=METHODS):
        for method in methods:
            with self.subTest(method=method), self.assertRaises(ValueError):
                self.metadata(method, envelope, build, data)

    def packet(self, legacy=None):
        legacy = self.fixture.packet() if legacy is None else legacy
        return {actual: legacy[old] for actual, old in ALIASES.items()}

    def artifacts(self, packet, *, exported=None, native=None, frozen=None, policy=None):
        if exported is None:
            exported = packet[PROJECT + '.bin-zsk.bin']
        with no_external_effects():
            return (policy or self.policy).validate_artifacts(
                packet, self.native_source if native is None else native,
                self.frozen_source if frozen is None else frozen,
                exported_flat_package=exported)

    def reject_artifacts(self, packet, **kwargs):
        with self.assertRaises(ValueError):
            self.artifacts(packet, **kwargs)


class FixedMetadataContract(ContractFixture):
    def test_constants_and_reference_substitution_counts_are_exact(self):
        self.assertEqual((self.policy.PROJECT, self.policy.FQBN, self.policy.FLAGS),
                         (PROJECT, FQBN, FLAGS))
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
        for wrong in (literal_once(correct, build, data), correct.replace('app.ino', PROJECT)):
            envelope = self.envelope(build, data)
            self.assertNotEqual(wrong, correct)
            self.support.replace_property(envelope, 'recipe.c.combine.2.pattern', wrong)
            self.reject_metadata(envelope, build, data)

    def test_original_project_and_old_flags_fail_even_when_coherent(self):
        self.reject_metadata(self.support.public_envelope(self.reference))
        for key, value in (('build.project_name', 'app.ino'),
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
            'build.project_name': ('other.ino', 'app.ino', PROJECT + ' '),
            'build.library_discovery_phase_flag': ('', '-DARDUINO_LIBRARY_DISCOVERY_PHASE=1'),
            'compiler.c.extra_flags': (FLAGS.replace('MATCH=0', 'MATCH=1'),
                                       FLAGS.replace('MOTORS_ALLOWED=0', 'MOTORS_ALLOWED=1'),
                                       FLAGS.replace('PROBE=1', 'PROBE=0'), FLAGS + ' -DEXTRA=1'),
            'compiler.cpp.extra_flags': (FLAGS.replace('MATCH=0', 'MATCH=1'),
                                         FLAGS.replace('MOTORS_ALLOWED=0', 'MOTORS_ALLOWED=1'),
                                         FLAGS.replace('PROBE=1', 'PROBE=0'), FLAGS + ' -DEXTRA=1'),
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


class FixedArtifactContract(ContractFixture):
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
        return {'status': 'STATIC_APP_MOTOR_FAULT_LAYOUT_PACKAGE_PASS',
                'project': PROJECT, 'fqbn': FQBN, 'flags': FLAGS,
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
        self.reject_artifacts(self.fixture.packet(), exported=b'legacy keys')
        for extra in (*ALIASES.values(), 'app_motor_fault.ino.hex', 'other.ino.elf', 7):
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
            self.policy.validate_artifacts(packet, self.native_source, self.frozen_source,
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
                self.policy.validate_artifacts(packet, native, frozen,
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


class DependencyProvenanceContract(ContractFixture):
    @contextmanager
    def relocated(self):
        ram = os.environ.get('SUMOX_TEST_RAM_DIR')
        if ram is None and os.name == 'posix' and Path('/dev/shm').is_dir():
            ram = '/dev/shm'
        if not ram or not Path(ram).is_dir():
            self.skipTest('Set SUMOX_TEST_RAM_DIR to an owned RAM scratch directory')
        with tempfile.TemporaryDirectory(prefix='sumox-d187-', dir=ram) as temporary:
            root = Path(temporary)
            for path in (ADAPTER, *PINS):
                target = root / path
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes((ROOT / path).read_bytes())
            with no_external_effects():
                module = load_module('d187_relocated_adapter', root / ADAPTER)
            yield root, module

    def invoke(self, module, method):
        if method == 'validate_artifacts':
            return self.artifacts(self.packet(), policy=module)
        return self.metadata(method, self.envelope(), policy=module)

    def relevant_calls(self):
        for method in METHODS:
            for path in list(PINS)[:3]:
                yield method, path
        yield 'validate_artifacts', RAW / 'static_native_artifacts.py'

    def test_ordinary_relocated_minimal_tree_accepts_all_interfaces(self):
        with self.relocated() as (_, module):
            for method in METHODS:
                self.assertEqual(self.invoke(module, method), self.properties())
            result = self.invoke(module, 'validate_artifacts')
            self.assertEqual(result['status'], 'STATIC_APP_MOTOR_FAULT_LAYOUT_PACKAGE_PASS')

    def test_each_call_rechecks_missing_changed_oversized_and_nonfile_dependencies(self):
        for method, relative in self.relevant_calls():
            for kind in ('changed', 'missing', 'oversized', 'directory'):
                with self.subTest(method=method, path=str(relative), kind=kind):
                    with self.relocated() as (root, module):
                        self.invoke(module, method)
                        path = root / relative
                        if kind == 'changed':
                            path.write_bytes(path.read_bytes() + b'\n')
                        elif kind == 'oversized':
                            path.write_bytes(b'x' * 65537)
                        else:
                            path.unlink()
                            if kind == 'directory':
                                path.mkdir()
                        with self.assertRaises((ValueError, OSError)):
                            self.invoke(module, method)

    @unittest.skipIf(os.name == 'nt', 'Actual symlinks exercised on owned POSIX RAM')
    def test_each_dependency_symlink_and_its_ancestor_symlink_fail_after_import(self):
        for method, relative in self.relevant_calls():
            for ancestor in (False, True):
                with self.subTest(method=method, path=str(relative), ancestor=ancestor):
                    with self.relocated() as (root, module):
                        self.invoke(module, method)
                        path = root / relative
                        if ancestor:
                            path = path.parent
                        held = path.with_name(path.name + '-ordinary')
                        path.rename(held)
                        path.symlink_to(held, target_is_directory=ancestor)
                        with self.assertRaises((ValueError, OSError)):
                            self.invoke(module, method)

    def test_reparse_attribute_on_files_and_ancestors_is_rejected(self):
        original_lstat = os.lstat
        flag = getattr(stat, 'FILE_ATTRIBUTE_REPARSE_POINT', 0x400)
        for method, relative in self.relevant_calls():
            for ancestor in (False, True):
                target = ROOT / relative
                if ancestor:
                    target = target.parent

                def marked(path, *args, **kwargs):
                    observed = original_lstat(path, *args, **kwargs)
                    if Path(path) != target:
                        return observed
                    attributes = {name: getattr(observed, name) for name in dir(observed)
                                  if name.startswith('st_')}
                    attributes['st_file_attributes'] = flag
                    return types.SimpleNamespace(**attributes)

                with self.subTest(method=method, path=str(target)):
                    with mock.patch.object(os, 'lstat', marked):
                        with self.assertRaises((ValueError, OSError)):
                            self.invoke(self.policy, method)

    def test_adapter_does_not_mutate_other_historical_consumers(self):
        with mock.patch.dict(sys.modules):
            dynamic = load_module('app_build_policy', ROOT / 'tools/app_build_policy.py')
            sys.modules['app_build_policy'] = dynamic
            original = load_module('static_policy', ROOT / RAW / 'static_policy.py')
            sys.modules['static_policy'] = original
            text = json.dumps(self.support.public_envelope(self.reference))
            expected = self.support.public_properties(self.reference)
            for method in METHODS:
                self.assertEqual(getattr(original, method)(text, build_path=BUILD, data_dir=DATA),
                                 expected)
            with no_external_effects():
                adapter = load_module('d187_isolated_adapter', ROOT / ADAPTER)
            for method in METHODS:
                self.assertEqual(self.metadata(method, self.envelope(), policy=adapter),
                                 self.properties())
                self.assertEqual(getattr(original, method)(text, build_path=BUILD, data_dir=DATA),
                                 expected)
                with self.assertRaises(ValueError):
                    getattr(original, method)(json.dumps(self.envelope()),
                                              build_path=BUILD, data_dir=DATA)
            self.assertIs(sys.modules['app_build_policy'], dynamic)
            self.assertIs(sys.modules['static_policy'], original)


if __name__ == '__main__':
    unittest.main(verbosity=2)
