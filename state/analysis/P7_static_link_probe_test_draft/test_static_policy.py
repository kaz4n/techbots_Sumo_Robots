# Independently exercises the reviewed static/M0 public JSON policy contract.
# Keeps synthetic policy acceptance separate from compilation and hardware evidence.
# Run only after freeze_policy.json binds this draft and its reviewed reference.
import builtins
import copy
from contextlib import ExitStack
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import re
import socket
import subprocess
import sys
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[3]
DRAFT = Path(__file__).resolve().parent
RAW = ROOT / 'state/analysis/P7_static_link_probe_raw'
REFERENCE = RAW / 'static_reference.json'
FREEZE = DRAFT / 'freeze_policy.json'
BUILD = '/synthetic/static-probe/run-once/build'
DATA = '/synthetic/arduino-data'
PLATFORM_SUFFIX = '/packages/arduino/hardware/zephyr/1.0.0'
COMPILER_SUFFIX = '/packages/zephyr/tools/arm-zephyr-eabi/1.0.1'
VARIANT = 'arduino_uno_q_stm32u585xx'
FQBN = 'arduino:zephyr:unoq:link_mode=static'
FLAGS = '-DMATCH=0 -DMOTORS_ALLOWED=0'
PREFIXES = ('recipe.', 'compiler.', 'build.link', 'build.check_command',
            'build.zsk_args', 'build.postbuild.', 'tools.ctags.', 'preproc.',
            'build.compiler_path', 'build.crossprefix', 'build.zip.pattern')


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def expanded_reference(reference, build=BUILD, data=DATA):
    return {key: value.replace('@BUILD_PATH@', build).replace('@DATA_DIR@', data)
            for key, value in reference.items()}


def public_properties(reference, build=BUILD, data=DATA):
    platform = data + PLATFORM_SUFFIX
    properties = {
        'build.fqbn': FQBN,
        'build.core': 'arduino',
        'build.variant': VARIANT,
        'runtime.platform.path': platform,
        'build.variant.path': platform + '/variants/' + VARIANT,
        'build.project_name': 'app.ino',
        'build.library_discovery_phase_flag': '-DARDUINO_LIBRARY_DISCOVERY_PHASE=0',
        'build.boot_mode': 'wait',
        'upload.extension': 'bin-zsk.bin',
        'build.path': build,
        'runtime.tools.arm-zephyr-eabi-1.0.1.path': data + COMPILER_SUFFIX,
        'build.extra_flags': '',
        'build.extra_ldflags': '',
    }
    properties.update(expanded_reference(reference, build, data))
    return properties


def public_envelope(reference, build=BUILD, data=DATA):
    platform = {'id': 'arduino:zephyr', 'version': '1.0.0',
                'install_dir': data + PLATFORM_SUFFIX}
    properties = public_properties(reference, build, data)
    return {
        'success': True,
        'error': '',
        'upload_result': {},
        'compiler_out': 'Synthetic only; no compiler has run.\n',
        'compiler_err': '',
        'builder_result': {
            'build_path': build,
            'board_platform': dict(platform),
            'build_platform': dict(platform),
            'used_libraries': [],
            'build_properties': [key + '=' + value for key, value in properties.items()],
        },
    }


def replace_property(envelope, key, value):
    values = envelope['builder_result']['build_properties']
    prefix = key + '='
    values[:] = [item for item in values if not item.startswith(prefix)]
    if value is not None:
        values.append(prefix + value)


def io_tripwires(replacement_reference=None):
    stack = ExitStack()
    permitted = os.path.normcase(os.path.abspath(REFERENCE))
    for module, attribute in ((builtins, 'open'), (io, 'open')):
        original = getattr(module, attribute)

        def read_reference(file, mode='r', *args, _open=original, **kwargs):
            path = os.path.normcase(os.path.abspath(os.fspath(file)))
            if path != permitted or mode not in ('r', 'rt', 'rb'):
                raise AssertionError('Policy attempted unapproved file I/O')
            if replacement_reference is not None:
                if mode == 'rb':
                    return io.BytesIO(replacement_reference)
                return io.StringIO(replacement_reference.decode('utf-8'))
            return _open(file, mode, *args, **kwargs)

        stack.enter_context(mock.patch.object(module, attribute, read_reference))
    prohibited = {
        subprocess: ('Popen', 'run', 'call', 'check_call', 'check_output'),
        socket: ('socket', 'create_connection', 'getaddrinfo'),
        os: ('system', 'popen', 'open', 'stat', 'lstat', 'listdir', 'scandir',
             'readlink', 'access', 'mkdir', 'makedirs', 'remove', 'unlink',
             'rename', 'replace', 'rmdir', 'removedirs', 'chmod', 'chdir'),
    }
    for module, names in prohibited.items():
        for name in names:
            stack.enter_context(mock.patch.object(
                module, name, side_effect=AssertionError('Policy I/O tripwire: ' + name)))
    return stack


class StaticPolicyContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        freeze = json.loads(FREEZE.read_text(encoding='utf-8'))
        if freeze.get('status') != 'FROZEN_FOR_AUTHORIZED_HOST_TEST':
            raise RuntimeError('Coordinator must freeze and authorize this draft first')
        for relative, expected in freeze['inputs_sha256'].items():
            actual = hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()
            if actual != expected:
                raise RuntimeError('Frozen policy test input changed: ' + relative)
        cls.reference = json.loads(REFERENCE.read_text(encoding='utf-8'))
        cls.dynamic_reference = json.loads(
            (ROOT / 'tools/app_build_commands.json').read_text(encoding='utf-8'))
        sys.path.insert(0, str(ROOT / 'tools'))
        sys.path.insert(0, str(RAW))
        cls.policy = load_module('independent_static_policy_under_test', RAW / 'static_policy.py')
        cls.dynamic = load_module('independent_dynamic_policy', ROOT / 'tools/app_build_policy.py')
        cls.validators = ('validate_preflight', 'validate_compile_result')

    def valid(self):
        return public_envelope(self.reference)

    def call(self, name, text, build=BUILD, data=DATA, replacement_reference=None):
        with io_tripwires(replacement_reference):
            return getattr(self.policy, name)(text, build_path=build, data_dir=data)

    def reject_text(self, text, names=None, build=BUILD, data=DATA):
        for name in names or self.validators:
            with self.subTest(validator=name):
                with self.assertRaises(ValueError):
                    self.call(name, text, build, data)

    def reject(self, envelope, names=None, build=BUILD, data=DATA):
        self.reject_text(json.dumps(envelope), names, build, data)

    def test_complete_reference_has_original_84_controlled_keys(self):
        self.assertEqual(len(self.reference), 84)
        self.assertEqual(set(self.reference), set(self.dynamic_reference))
        self.assertTrue(all(key.startswith(PREFIXES) for key in self.reference))
        self.assertTrue(all(isinstance(value, str) for value in self.reference.values()))
        placeholders = set(re.findall(r'@[A-Z_]+@', '\n'.join(self.reference.values())))
        self.assertEqual(placeholders, {'@BUILD_PATH@', '@DATA_DIR@'})
        self.assertEqual(self.reference['compiler.c.extra_flags'], FLAGS)
        self.assertEqual(self.reference['compiler.cpp.extra_flags'], FLAGS)
        self.assertEqual(self.reference['build.link_mode'], 'static')
        self.assertEqual(self.reference['build.check_command-static'], 'true')
        self.assertEqual(self.reference['build.zsk_args.mode-static'], '-prelinked')

    def test_reference_raw_bytes_are_pinned_even_when_semantics_are_unchanged(self):
        original = REFERENCE.read_bytes()
        for replacement in (b' ' + original, original + b'\n', b'{"corrupt":'):
            for name in self.validators:
                with self.subTest(validator=name, replacement_hash=hashlib.sha256(replacement).hexdigest()):
                    with self.assertRaises(ValueError):
                        self.call(name, json.dumps(self.valid()), replacement_reference=replacement)

    def test_coherent_reference_and_command_tampering_cannot_redefine_policy(self):
        changed = dict(self.reference)
        key = 'recipe.hooks.prebuild.1.pattern'
        changed[key] += ' UNREVIEWED'
        replacement = json.dumps(changed, sort_keys=True).encode('utf-8')
        for envelope in (self.valid(), public_envelope(changed)):
            for name in self.validators:
                with self.subTest(validator=name, coherent=envelope != self.valid()):
                    with self.assertRaises(ValueError):
                        self.call(name, json.dumps(envelope), replacement_reference=replacement)

    def test_exact_synthetic_profile_returns_all_properties_without_mutation(self):
        envelope = self.valid()
        original = copy.deepcopy(envelope)
        for name in self.validators:
            with self.subTest(validator=name):
                actual = self.call(name, json.dumps(envelope))
                self.assertEqual(actual, public_properties(self.reference))
                self.assertTrue(all(isinstance(k, str) and isinstance(v, str)
                                    for k, v in actual.items()))
                self.assertEqual(envelope, original)

    def test_distinct_clean_synthetic_roots_are_valid(self):
        build, data = '/other/new-build', '/other/data'
        for name in self.validators:
            self.assertEqual(self.call(name, json.dumps(public_envelope(self.reference, build, data)),
                                       build, data), public_properties(self.reference, build, data))

    def test_optional_cli_output_fields_can_be_absent(self):
        envelope = self.valid()
        for key in ('error', 'upload_result', 'compiler_out', 'compiler_err'):
            del envelope[key]
        del envelope['builder_result']['used_libraries']
        for name in self.validators:
            self.assertEqual(self.call(name, json.dumps(envelope)), public_properties(self.reference))

    def test_malformed_json_and_nontext_fail_with_valueerror(self):
        for text in ('', ' ', '{', '[]', 'null', '1', 'true', '"text"',
                     '{} trailing', '\ufeff{}', None, 1, [], {}, b'{}', bytearray(b'{}')):
            with self.subTest(text=repr(text)):
                self.reject_text(text)

    def test_duplicate_json_keys_at_all_envelope_levels_fail(self):
        text = json.dumps(self.valid())
        for old, new in (
                ('"success": true', '"success": false, "success": true'),
                ('"build_path": ', '"build_path": "/bad", "build_path": '),
                ('"id": "arduino:zephyr"', '"id": "bad", "id": "arduino:zephyr"')):
            self.assertIn(old, text)
            with self.subTest(fragment=old):
                self.reject_text(text.replace(old, new, 1))

    def test_nonfinite_json_fails_even_in_uninterpreted_fields(self):
        for token in ('NaN', 'Infinity', '-Infinity', '1e999', '-1e999'):
            text = json.dumps(self.valid())[:-1] + ', "unused": ' + token + '}'
            with self.subTest(token=token):
                self.reject_text(text)

    def test_success_must_be_true_boolean(self):
        for value in (False, None, 0, 1, 'true', [], {}):
            envelope = self.valid()
            envelope['success'] = value
            with self.subTest(value=repr(value)):
                self.reject(envelope)
        envelope = self.valid()
        del envelope['success']
        self.reject(envelope)

    def test_error_upload_and_output_types_fail_closed(self):
        cases = {
            'error': ('failed', None, False, 0, [], {}),
            'upload_result': ({'success': True}, None, False, 0, '', []),
            'compiler_out': (None, False, 0, [], {}),
            'compiler_err': (None, False, 0, [], {}),
        }
        for key, values in cases.items():
            for value in values:
                envelope = self.valid()
                envelope[key] = value
                with self.subTest(key=key, value=repr(value)):
                    self.reject(envelope)

    def test_builder_is_required_and_must_be_object(self):
        for value in (None, False, 1, '', [], {}):
            envelope = self.valid()
            envelope['builder_result'] = value
            with self.subTest(value=repr(value)):
                self.reject(envelope)
        envelope = self.valid()
        del envelope['builder_result']
        self.reject(envelope)

    def test_builder_platform_identity_and_version_are_exact(self):
        for section in ('board_platform', 'build_platform'):
            for key, value in (('id', 'other:zephyr'), ('id', None),
                               ('version', '1.0.1'), ('version', 1),
                               ('install_dir', DATA + PLATFORM_SUFFIX + '-other')):
                envelope = self.valid()
                envelope['builder_result'][section][key] = value
                with self.subTest(section=section, key=key, value=value):
                    self.reject(envelope)
            for value in (None, '', [], {}):
                envelope = self.valid()
                envelope['builder_result'][section] = value
                self.reject(envelope)
            envelope = self.valid()
            del envelope['builder_result'][section]
            self.reject(envelope)

    def test_both_matching_platforms_still_bind_to_resolved_data_directory(self):
        envelope = public_envelope(self.reference, BUILD, '/wrong/data')
        self.reject(envelope)

    def test_invalid_requested_paths_fail_valueerror(self):
        paths = (None, 12, '', '/', 'relative', '//host/path', '/tmp/../build',
                 '/tmp/./build', '/tmp//build', '/tmp/build/', '/tmp/a\\b',
                 '/tmp/"bad', "/tmp/'bad", '/tmp/`bad', '/tmp/$bad',
                 '/tmp/line\nbreak', '/tmp/null\0byte', '/tmp/\x7f')
        for path in paths:
            with self.subTest(build=repr(path)):
                self.reject(self.valid(), build=path)
            with self.subTest(data=repr(path)):
                self.reject(self.valid(), data=path)

    def test_builder_and_effective_build_paths_both_bind_to_request(self):
        envelope = self.valid()
        envelope['builder_result']['build_path'] = BUILD + '-other'
        self.reject(envelope)
        envelope = self.valid()
        replace_property(envelope, 'build.path', BUILD + '-other')
        self.reject(envelope)
        envelope = public_envelope(self.reference, BUILD + '-other')
        self.reject(envelope)

    def test_property_container_and_entries_are_strict(self):
        for value in (None, '', 1, {}, [], ['no-equals'], ['=empty-key'], [None], [1], [{}]):
            envelope = self.valid()
            envelope['builder_result']['build_properties'] = value
            with self.subTest(value=repr(value)):
                self.reject(envelope)
        envelope = self.valid()
        del envelope['builder_result']['build_properties']
        self.reject(envelope)

    def test_duplicate_property_rejected_even_if_values_identical(self):
        for key in ('build.fqbn', 'compiler.c.extra_flags', 'recipe.c.combine.1.pattern'):
            envelope = self.valid()
            values = envelope['builder_result']['build_properties']
            existing = next(item for item in values if item.startswith(key + '='))
            values.append(existing)
            with self.subTest(key=key):
                self.reject(envelope)

    def test_every_controlled_property_is_required(self):
        for key in self.reference:
            envelope = self.valid()
            replace_property(envelope, key, None)
            with self.subTest(missing=key):
                self.reject(envelope)

    def test_every_controlled_property_is_exact_including_inactive_hooks(self):
        for key in self.reference:
            envelope = self.valid()
            old = expanded_reference(self.reference)[key]
            replace_property(envelope, key, old + ' UNREVIEWED')
            with self.subTest(changed=key):
                self.reject(envelope)

    def test_extra_controlled_keys_rejected_for_every_public_prefix(self):
        for prefix in PREFIXES:
            envelope = self.valid()
            key = prefix + 'unreviewed_test_hook'
            self.assertNotIn(key, self.reference)
            replace_property(envelope, key, '')
            with self.subTest(extra=key):
                self.reject(envelope)

    def test_required_uncontrolled_metadata_cannot_be_deleted_or_changed(self):
        properties = public_properties(self.reference)
        keys = set(properties) - set(self.reference)
        for key in sorted(keys):
            for value in (None, properties[key] + ' UNREVIEWED'):
                envelope = self.valid()
                replace_property(envelope, key, value)
                with self.subTest(key=key, value=value):
                    self.reject(envelope)

    def test_only_fixed_static_m0_wait_profile_is_admitted(self):
        cases = {
            'build.fqbn': ('arduino:zephyr:unoq', 'arduino:zephyr:unoq:link_mode=dynamic',
                           FQBN + ',wait_linux_boot=no', FQBN + ':wait_linux_boot=no',
                           FQBN + ',wait_linux_boot=yes'),
            'build.link_mode': ('dynamic', '', 'static '),
            'build.boot_mode': ('immediate', 'app', ''),
            'build.project_name': ('runtime_inert.ino', 'other.ino'),
            'build.library_discovery_phase_flag': ('', '-DARDUINO_LIBRARY_DISCOVERY_PHASE=1'),
            'compiler.c.extra_flags': ('-DMATCH=1 -DMOTORS_ALLOWED=1', FLAGS + ' -DEXTRA=1'),
            'compiler.cpp.extra_flags': ('-DMATCH=0 -DMOTORS_ALLOWED=1', FLAGS + ' -DEXTRA=1'),
        }
        for key, values in cases.items():
            for value in values:
                envelope = self.valid()
                replace_property(envelope, key, value)
                with self.subTest(key=key, value=value):
                    self.reject(envelope)

    def test_compiler_root_and_variant_path_must_match_installed_pins(self):
        for key, value in (
                ('runtime.tools.arm-zephyr-eabi-1.0.1.path', DATA + COMPILER_SUFFIX + '-other'),
                ('runtime.tools.arm-zephyr-eabi-1.0.1.path', '/different' + COMPILER_SUFFIX),
                ('compiler.path', DATA + COMPILER_SUFFIX + '/other-bin/'),
                ('runtime.platform.path', '/different' + PLATFORM_SUFFIX),
                ('build.variant.path', DATA + PLATFORM_SUFFIX + '/variants/other')):
            envelope = self.valid()
            replace_property(envelope, key, value)
            with self.subTest(key=key, value=value):
                self.reject(envelope)

    def test_actual_compile_rejects_every_external_library_or_malformed_list(self):
        for value in ([{'name': 'UnreviewedLibrary'}], ['CoreImpersonation'],
                      [None], {}, '', None, False, 0):
            envelope = self.valid()
            envelope['builder_result']['used_libraries'] = value
            with self.subTest(libraries=repr(value)):
                self.reject(envelope, ('validate_compile_result',))

    def test_dynamic_commands_cannot_be_relabelled_static(self):
        envelope = self.valid()
        for key, value in self.dynamic_reference.items():
            value = value.replace('@SAFETY_FLAGS@', FLAGS).replace('@BOOT_ARGUMENT@', '')
            value = value.replace('@DATA_DIR@', DATA).replace('@BUILD_PATH@', BUILD)
            replace_property(envelope, key, value)
        replace_property(envelope, 'build.link_mode', 'static')
        self.reject(envelope)

    def test_ordinary_production_policy_still_rejects_static(self):
        text = json.dumps(self.valid())
        with self.assertRaises(ValueError):
            self.dynamic.validate_preflight(text, FQBN, FLAGS, BUILD, DATA)
        with self.assertRaises(ValueError):
            self.dynamic.validate_result(text, FQBN, FLAGS, BUILD)


if __name__ == '__main__':
    unittest.main(verbosity=2)
