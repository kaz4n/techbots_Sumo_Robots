# Tests D227's frozen commissioning upload interface without native operations.
# Derives all profile identities and reply expectations from the contract.
# Host fixtures never create physical qualification or motor-run permission.
import copy
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import shlex
import subprocess
import sys
from types import SimpleNamespace
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
STATIC = 'state/analysis/P7_static_startup_raw/'
PROFILES = ('b4_stand', 'p3_drive', 'p3_turn', 'p3_stop', 'p4_reactive', 'p4_timing', 'p5_abort_timing')
SOURCE = '1234567890abcdef' * 4
RUN = '34567890abcdef12' * 2
BOOT = '55c386b9-fe6d-4388-a7f4-1d91e0bb49d8'
PARENT = '/home/arduino/sumox26_codex_build'
FQBN = 'arduino:zephyr:unoq:link_mode=static'
NATIVE = ['adb', '-s', 'synthetic-target', 'shell', '-T']
SOURCE_PATHS = dict(helper='state/analysis/P7_static_link_probe_raw/static_remote.py',
    support=STATIC + 'capture_remote.py', upload=STATIC + 'upload_remote.py',
    inherited_adapter='tools/match_upload.py', adapter='tools/commissioning_app_upload.py')


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def canonical(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True,
                       allow_nan=False) + '\n').encode('ascii')


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def selection(profile='b4_stand', motors=0, source=SOURCE):
    return dict(profile=profile, motors_allowed=motors, compile_attempt='fixture01',
                source_sha256=source, run_id=RUN)


def paths(selected):
    suffix = sha((selected['source_sha256'] + '\0' + selected['compile_attempt']).encode())[:12]
    owner = 'commission-' + selected['profile'] + '-m' + str(selected['motors_allowed']) + '-' + suffix
    remote = PARENT + '/' + owner
    return dict(owner=owner, output='state/analysis/P7_commissioning_build_raw/' + owner,
                stage='build/stage/' + owner + '/app', remote=remote, build=remote + '/build',
                artifacts=remote + '/artifacts', sketch=PARENT + '/' + selected['source_sha256'] + '/app')


def expected_profile(uploader, selected):
    located = paths(selected)
    files = dict(uploader.FILE_PATHS)
    files.update(raw=located['build'] + '/app.ino.bin',
                 sketch=located['build'] + '/app.ino.bin-zsk.bin',
                 exported=located['artifacts'] + '/app.ino.bin-zsk.bin')
    return dict(fixed=dict(schema='fixed-commissioning-app-upload-v1', run_id=selected['run_id'],
                source_sha256=selected['source_sha256'], output=PARENT + '/commission-upload-' + selected['run_id']),
        schema_prefix='commissioning-app-upload-', files=files,
        absent=uploader.ABSENT[:-3] + tuple(located['sketch'] + '/sketch.' + ext for ext in ('yaml', 'yml', 'json')),
        argv=['/usr/bin/arduino-cli', '--config-file', '/dev/null', 'upload', '--fqbn', FQBN,
              '--input-file', files['raw'], located['sketch']])


def bindings(uploader, selected):
    profile = expected_profile(uploader, selected)
    return {**profile['fixed'], 'boot_id': BOOT, 'uid': 1000,
        'files': {key: dict(path=value, bytes=8, sha256='a' * 64) for key, value in profile['files'].items()},
        'directories': {name: ['fixture'] for name in uploader.DIRECTORIES},
        'absent': list(profile['absent'])}


def reply(selected, payload_sha='b' * 64):
    report = dict(schema='commissioning-app-upload-result-v1', run_id=selected['run_id'],
        source_sha256=selected['source_sha256'], status='UPLOADED', attempts=1,
        started_utc='2026-09-26T10:00:00+00:00', finished_utc='2026-09-26T10:00:01+00:00',
        started_monotonic=10.0, finished_monotonic=11.0,
        subprocess=dict(returncode=0, timed_out=False, reaped=True), stdout='synthetic upload\n',
        stderr='', first_error=None, postcheck_errors=[])
    raw = canonical(report)
    return dict(schema='commissioning-app-action-v1', selection=copy.deepcopy(selected),
        payload_sha256=payload_sha, remote_result_path=PARENT + '/commission-upload-' + selected['run_id'] + '/upload_result.json',
        full_result_bytes=len(raw), full_result_sha256=sha(raw),
        report={key: value for key, value in report.items() if key not in ('stdout', 'stderr')}, first_error=None)


class StrSubclass(str):
    pass


class IntSubclass(int):
    pass


class CommissioningUploadTests(unittest.TestCase):
    def setUp(self):
        self.subject = load(ROOT / SOURCE_PATHS['adapter'], '_d227_upload_subject')
        self.uploader = load(ROOT / SOURCE_PATHS['upload'], '_d227_frozen_uploader')
        old = load(ROOT / 'tools/match_deploy.py', '_d227_pure_bindings')
        self.support = old.binding_support((ROOT / SOURCE_PATHS['support']).read_bytes())
        self.selected = selection()
        self.sources = {key: (ROOT / value).read_bytes() for key, value in SOURCE_PATHS.items()}
        self.bound = bindings(self.uploader, self.selected)
        guard = mock.patch.object(subprocess, 'Popen', side_effect=AssertionError('Native child forbidden'))
        guard.start(); self.addCleanup(guard.stop)

    def profile(self, selected=None):
        return self.subject.commissioning_profile(self.uploader, self.support, **(selected or self.selected))

    def command(self, **changes):
        value = dict(sources=self.sources, bindings=self.bound, selection=self.selected, native_prefix=NATIVE)
        value.update(changes)
        return self.subject.build_command(**value)

    def validate(self, value, selected=None):
        text = value if isinstance(value, str) else canonical(value).decode()
        return self.subject.validate_reply(text, selected or self.selected, 'b' * 64)

    def test_all_fourteen_exact_static_profiles(self):
        for profile in PROFILES:
            for motors in (0, 1):
                chosen = selection(profile, motors)
                with self.subTest(profile=profile, motors=motors):
                    self.assertEqual(self.profile(chosen), expected_profile(self.uploader, chosen))
        self.assertEqual(self.uploader.FILE_PATHS['cli'], '/usr/bin/arduino-cli')

    def test_profile_independence_and_exact_precompiled_command(self):
        first, second = self.profile(), self.profile()
        first['files']['raw'] = '/tmp/untrusted'
        first['argv'].append('--reset')
        self.assertEqual(second, expected_profile(self.uploader, self.selected))
        self.assertNotIn('compile', second['argv'])
        self.assertNotIn('wait_linux_boot=no', ' '.join(second['argv']))

    def test_every_selection_field_rejects_nonexact_or_invalid_values(self):
        replacements = dict(profile=(None, StrSubclass('b4_stand'), 'app', 'B4_STAND'),
            motors_allowed=(True, False, IntSubclass(0), 0.0, '0', -1, 2),
            compile_attempt=(None, '../escape', 'A', 'a' * 25, StrSubclass('fixture01')),
            source_sha256=(None, SOURCE.upper(), SOURCE[:-1], StrSubclass(SOURCE)),
            run_id=(None, RUN.upper(), RUN[:-1], StrSubclass(RUN)))
        for field, values in replacements.items():
            for value in values:
                bad = dict(self.selected, **{field: value})
                with self.subTest(field=field, value=repr(value)), self.assertRaises((ValueError, TypeError)):
                    self.profile(bad)

    def test_command_preserves_isolation_controlled_environment_and_windows_bound(self):
        command = self.command()
        self.assertIs(type(command), list)
        self.assertIn('-I', command); self.assertIn('-B', command)
        self.assertIn('/usr/bin/env', command); self.assertIn('-i', command)
        self.assertLessEqual(len(subprocess.list2cmdline([*NATIVE, shlex.join(command)]).encode('utf-16-le')) // 2 + 1, 30000)

    def test_frozen_source_drift_and_missing_roles_refuse(self):
        for role in SOURCE_PATHS:
            if role == 'adapter':
                continue
            changed = dict(self.sources, **{role: self.sources[role] + b'\n'})
            with self.subTest(role=role), self.assertRaises((ValueError, TypeError)):
                self.command(sources=changed)
        for role in SOURCE_PATHS:
            changed = dict(self.sources); del changed[role]
            with self.subTest(missing=role), self.assertRaises((ValueError, TypeError)):
                self.command(sources=changed)

    def test_binding_cross_profile_motor_package_boot_and_extra_fields_refuse(self):
        mutations = []
        for profile, motors in (('p3_drive', 0), ('b4_stand', 1)):
            mutations.append(bindings(self.uploader, selection(profile, motors)))
        for change in (dict(boot_id='not-a-boot'), dict(uid=True), dict(extra=None)):
            mutations.append(dict(self.bound, **change))
        changed = copy.deepcopy(self.bound); changed['files']['exported']['sha256'] = 'b' * 64; mutations.append(changed)
        for index, value in enumerate(mutations):
            with self.subTest(index=index), self.assertRaises((ValueError, TypeError)):
                self.command(bindings=value)

    def test_valid_compact_reply_binds_selection_payload_and_durable_report(self):
        result = self.validate(reply(self.selected))
        self.assertIsNotNone(result)

    def test_reply_rejects_identity_paths_status_and_inexact_success(self):
        base = reply(self.selected)
        mutations = [dict(base, payload_sha256='c' * 64), dict(base, remote_result_path='/tmp/other'),
                     dict(base, full_result_bytes=True), dict(base, full_result_sha256='bad'),
                     dict(base, extra=True)]
        for field, value in (('motors_allowed', 1), ('profile', 'p3_drive'), ('compile_attempt', 'other01')):
            mutations.append(dict(base, selection=dict(self.selected, **{field: value})))
        for field, value in (('attempts', True), ('attempts', 2), ('status', 'FAILED'),
                             ('first_error', {'type': 'Failure', 'message': 'synthetic'}),
                             ('postcheck_errors', [{'check': 'identity'}])):
            mutations.append(dict(base, report=dict(base['report'], **{field: value})))
        mutations.append(dict(base, report=dict(base['report'], subprocess=dict(returncode=True, timed_out=False, reaped=True))))
        for index, value in enumerate(mutations):
            with self.subTest(index=index), self.assertRaises((ValueError, TypeError)):
                self.validate(value)

    def test_reply_rejects_duplicates_nonfinite_and_oversize(self):
        raw = canonical(reply(self.selected)).decode()
        mutations = ['{"schema":"x",' + raw[1:], raw.replace('10.0', 'NaN'),
                     raw.replace('10.0', 'Infinity'), ' ' * 1048577 + raw]
        for text in mutations:
            with self.subTest(prefix=text[:30]), self.assertRaises((ValueError, TypeError)):
                self.validate(text)


if __name__ == '__main__':
    unittest.main()
