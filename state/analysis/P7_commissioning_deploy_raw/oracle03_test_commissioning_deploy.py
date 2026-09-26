# Tests D227 deployment admission against actual temporary Git object identities.
# Reuses accepted synthetic compiler/ELF fixtures; all authority records are fake.
# No native child, board transport, physical grant or motor run is permitted.
from contextlib import ExitStack
import copy
from datetime import datetime, timedelta, timezone
import errno
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest import mock

from tests.tooling.test_commissioning_app_upload import (
    ROOT, STATIC, PROFILES, RUN, BOOT, FQBN, SOURCE_PATHS, load, canonical, sha,
    selection, paths, bindings, reply, StrSubclass)
from tests.tooling.test_commissioning_app_static_policy import expected_flags

NOW = datetime(2026, 9, 26, 10, 0, tzinfo=timezone.utc)
SCOPE = 'state/analysis/synthetic_commissioning_scope.json'
CONTRACT = 'state/analysis/P7_commissioning_deploy_contract.md'
SUBJECT = 'tools/deploy_commissioning_app.py'
CHECKS = ('pinmap', 'electrical', 'buttons', 'battery', 'line_calibration',
          'motor_inhibition', 'profile_parameters', 'source_clock')
GRANTS = ('APP_GRANT_OPPONENTS', 'APP_GRANT_ADC_PAIR', 'APP_GRANT_QTR_EXCLUSIVE_PADS',
    'APP_GRANT_IMU_ENABLED', 'APP_GRANT_IMU_POWER_CONFIRMED', 'APP_GRANT_IMU_MOUNTING_CONFIRMED',
    'APP_GRANT_DEFAULT_LINE_THRESHOLDS', 'APP_GRANT_MATRIX_ENABLED', 'APP_GRANT_MATRIX_NORMAL_STARTUP',
    'APP_GRANT_MATRIX_EXCLUSIVE_OWNER', 'APP_GRANT_DUMP_ENABLED', 'APP_GRANT_DUMP_SETUP_PHASE',
    'APP_GRANT_DUMP_EXCLUSIVE_UART', 'APP_GRANT_DUMP_READY_PIN_OWNED', 'APP_GRANT_DUMP_FRAMING_CLEAN',
    'APP_GRANT_LOCAL_SERVICE_RESET', 'APP_GRANT_CALIBRATION_OUTPUT')
FINAL_CHECKS = ('local', 'identity', 'initialization', 'builtins', 'remote_sources',
                'installed_pins', 'overrides', 'artifacts', 'artifact_sources')
GATES = dict(b4_stand='GATE P1 PASS', p3_drive='GATE P2 PASS', p3_turn='GATE P2 PASS',
             p3_stop='GATE P2 PASS', p4_reactive='GATE P3 PASS', p4_timing='GATE P3 PASS',
             p5_abort_timing='GATE P4 PASS')
ROLES = dict(inputs='inputs.json', intent='intent.json', staged_files='staged_files.json',
    result='result.json', artifacts='artifacts.json', compile_command='compile/compile.command.json',
    compile_stdout='compile/compile.stdout.json', compile_stderr='compile/compile.stderr.txt',
    properties_command='compile/properties.command.json', properties_stdout='compile/properties.stdout.json',
    properties_stderr='compile/properties.stderr.txt')


def put(root, name, raw):
    path = root / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(raw)
    return dict(path=name, bytes=len(raw), sha256=sha(raw))


def put_json(root, name, value):
    return put(root, name, canonical(value))


def record(raw, digest=None):
    return dict(state='regular', identity=dict(device=1, inode=2, bytes=len(raw), mtime_ns=3, ctime_ns=4),
                sha256=sha(raw) if digest is None else digest)


class DeployFixture(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.legacy_fixture = load(ROOT / 'tests/tooling/test_b4_app_static_policy.py', '_d227_static_fixture')
        cls.legacy_fixture.Fixture.setUpClass()
        cls.fx = cls.legacy_fixture.Fixture()
        cls.compiler = load(ROOT / 'tools/compile_commissioning_app.py', '_d227_d222_fixture')
        cls.policy = load(ROOT / 'tools/commissioning_app_static_policy.py', '_d227_policy_fixture')
        cls.uploader = load(ROOT / (STATIC + 'upload_remote.py'), '_d227_uploader_fixture')

    def setUp(self):
        directory = '/dev/shm' if sys.platform == 'linux' else None
        self.temp = tempfile.TemporaryDirectory(prefix='sumox_d227_', dir=directory)
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.subject = load(ROOT / SUBJECT, '_d227_deploy_subject')
        self.copy_names = set(self.compiler.REQUIRED) | set(SOURCE_PATHS.values()) | {
            SUBJECT, CONTRACT, 'tools/match_payload.py', STATIC + 'startup_run.py',
            STATIC + 'upload_bindings.json'}
        for name in self.copy_names:
            put(self.root, name, (ROOT / name).read_bytes())
        put(self.root, '.gitattributes', b'* -text\n')
        self.git('init', '-q')
        self.git('config', 'core.autocrlf', 'false')
        self.config = (ROOT / 'src/config.h').read_bytes()
        self.make()
        # A refused baseline must not masquerade as successful mutation coverage.
        self.admit()

    def git(self, *arguments):
        value = subprocess.run(['git', '-C', str(self.root), *arguments], capture_output=True,
                               timeout=30, check=True)
        return value.stdout.decode().strip()

    def commit(self):
        self.git('add', '-A')
        self.git('-c', 'user.name=synthetic-fixture', '-c', 'user.email=fixture@example.invalid',
                 'commit', '-q', '--allow-empty', '-m', 'Synthetic host fixture; no authority')
        return self.git('rev-parse', 'HEAD')

    def operational_config(self, *, imu=False):
        result = self.config.decode()
        enabled = GRANTS[:6] if imu else GRANTS[:3]
        for name in enabled:
            result = result.replace(name + ' = 0U;', name + ' = 1U;')
        result = result.replace('BUTTON_WINDOWS_CONFIGURED = 0U;', 'BUTTON_WINDOWS_CONFIGURED = 1U;')
        result = result.replace('BUTTON_LOW_RAW[4] = {0U, 0U, 0U, 0U};',
                                'BUTTON_LOW_RAW[4] = {0U, 100U, 200U, 300U};')
        result = result.replace('BUTTON_HIGH_RAW[4] = {0U, 0U, 0U, 0U};',
                                'BUTTON_HIGH_RAW[4] = {49U, 149U, 249U, 349U};')
        if imu:
            result = result.replace('APP_IMU_BODY_AXIS[3] = {0, 0, 0};',
                                    'APP_IMU_BODY_AXIS[3] = {1, -2, 3};')
        return result.encode()

    def make(self, profile='b4_stand', motors=0, *, config=None, turn_basis='timed_fallback'):
        body = self.config if config is None else config
        if motors and config is None:
            body = self.operational_config(imu=turn_basis == 'imu_accuracy')
        put(self.root, 'src/config.h', body)
        put(self.root, 'src/core/fixture.h', b'// SYNTHETIC CORE, not compiled for hardware\n')
        put(self.root, 'src/hal/fixture.h', b'// SYNTHETIC HAL, not compiled for hardware\n')
        put(self.root, 'src/app/app.ino', b'// SYNTHETIC fixture only\nvoid setup() {}\nvoid loop() {}\n')
        self.compile_head = self.commit()
        request = dict(action='--check-only', profile=profile, motors_allowed=motors,
                       attempt='fixture01', reviewed_head=self.compile_head)
        owner = self.compiler.make_owner(request, root=self.root)
        owner.admission()
        self.owner = owner
        self.selected = selection(profile, motors, owner.source_sha256)
        self.located = paths(self.selected)
        self.bound = bindings(self.uploader, self.selected)
        baseline = json.loads((ROOT / (STATIC + 'upload_bindings.json')).read_bytes())
        for name in self.bound['files']:
            if name not in ('raw', 'sketch', 'exported'):
                self.bound['files'][name] = copy.deepcopy(baseline['files'][name])
        self.bound['directories'] = copy.deepcopy(baseline['directories'])
        packet = self.fx.packet()
        layout = self.policy.validate_artifacts(packet, self.fx.native_source, self.fx.frozen_source,
            exported_flat_package=packet['app.ino.bin-zsk.bin'], profile=profile,
            motors_allowed=motors, snapshots=self.fx.snapshots)
        files = {'build/' + name: record(raw) for name, raw in packet.items()}
        files['artifacts/app.ino.bin-zsk.bin'] = record(packet['app.ino.bin-zsk.bin'])
        native = layout['validator_report']['native_tls']
        self.artifacts = dict(schema='commissioning-app-static-artifacts-v1', status='ARTIFACTS_CHECKED',
            profile=profile, motors_allowed=motors, attempt='fixture01', source_sha256=owner.source_sha256,
            build_path=self.located['build'], artifacts_path=self.located['artifacts'], files=files,
            loader=record(b'fixture-loader', native['loader_sha256']),
            tls_source=record(self.fx.native_source, native['source_sha256']), layout=layout,
            postchecks=[dict(name=name, status='PASS', error=None) for name in ('loader', 'tls_source', 'files')],
            first_error=None)
        self.artifacts['loader']['identity']['bytes'] = baseline['files']['loader']['bytes']
        for name, key in (('raw', 'build/app.ino.bin'), ('sketch', 'build/app.ino.bin-zsk.bin'),
                          ('exported', 'artifacts/app.ino.bin-zsk.bin')):
            observed = files[key]
            self.bound['files'][name].update(bytes=observed['identity']['bytes'], sha256=observed['sha256'])
        self.metadata = self.fx.envelope(build=self.located['build'])
        props = self.metadata['builder_result']['build_properties']
        self.metadata['builder_result']['build_properties'] = [
            value.replace(self.legacy_fixture.flags(0), expected_flags(profile, motors)) for value in props]
        self.command = ['arduino-cli', 'compile', '--json', '--fqbn', FQBN,
            '--build-path', self.located['build'], '--output-dir', self.located['artifacts'],
            '--build-property', 'compiler.cpp.extra_flags=' + expected_flags(profile, motors),
            '--build-property', 'compiler.c.extra_flags=' + expected_flags(profile, motors),
            '--build-property', 'build.library_discovery_phase_flag=-DARDUINO_LIBRARY_DISCOVERY_PHASE=0',
            self.located['sketch']]
        self.outcome = owner.identity('commissioning-app-static-compile-outcome-v1')
        self.outcome.update(status='COMPILE_CHECKED', first_error=None, compiler_calls=1, query_calls=1,
            final_checks=[dict(name=name, status='PASS', error=None) for name in FINAL_CHECKS],
            started_utc=NOW.isoformat(), finished_utc=NOW.isoformat(), transport_calls=25,
            artifacts=self.located['artifacts'], receipt=str(owner.output / 'artifacts.json'))
        self.intent = owner.identity('commissioning-app-static-intent-v1')
        self.intent.update(inputs_sha256=sha(owner.inputs_raw), stage=str(self.root / self.located['stage']),
            remote=self.located['remote'], sketch=self.located['sketch'], started_utc=NOW.isoformat())
        self.request = {**self.selected, 'mode': 'operational_commissioning' if motors else 'inhibited_diagnostic',
            'source_commit': self.compile_head, 'config_sha256': sha(body), 'startup': 'default',
            'target': 'synthetic-target', 'transport': 'adb', 'bindings': self.bound,
            'build_receipts': {}, 'qualification': None}
        self.receipts = dict(inputs=owner.inputs_raw, intent=canonical(self.intent),
            staged_files=canonical(owner.expected_stage), result=canonical(self.outcome),
            artifacts=canonical(self.artifacts), compile_command=canonical(self.command),
            compile_stdout=canonical(self.metadata), compile_stderr=b'',
            properties_command=canonical(self.command[:-1] + ['--show-properties=expanded', self.command[-1]]),
            properties_stdout=canonical(self.metadata), properties_stderr=b'')
        self.qual = self.auth = None
        self.measurement = put(self.root, 'state/analysis/synthetic_measurement.txt',
            b'SYNTHETIC UNIT TEST ONLY - no physical evidence, human grant or authorization\n')
        if motors:
            accepted = dict(verdict='PHYSICALLY_ACCEPTED', evidence=[self.measurement])
            enabled = [name for name in GRANTS if re.search(r'\b' + name + r'\s*=\s*1U;', body.decode())]
            self.qual = dict(schema='commissioning-operation-qualification-v1', operation_image_sha256='',
                operation='stand' if profile == 'b4_stand' else 'ring', verdict='QUALIFIED_FOR_IDENTIFIED_OPERATION',
                reviewer='synthetic-fixture-only', limitations=['Not actual evidence'],
                checks={name: copy.deepcopy(accepted) for name in CHECKS},
                grants={name: copy.deepcopy(accepted) for name in enabled},
                gate=dict(reply=GATES[profile], message_ref='synthetic-not-human', evidence=[self.measurement]),
                turn_basis=turn_basis if profile == 'p3_turn' else 'not_applicable')
            self.auth = dict(schema='commissioning-human-authorization-v1', request_sha256='',
                reply='STAND OK' if profile == 'b4_stand' else 'RING OK', message_ref='synthetic-not-human',
                issued_utc=(NOW - timedelta(minutes=5)).isoformat(), expires_utc=(NOW + timedelta(minutes=5)).isoformat())
        self.refresh()

    def refresh(self, *, image=True, authorization=True):
        for role, body in self.receipts.items():
            self.request['build_receipts'][role] = put(self.root, self.located['output'] + '/' + ROLES[role], body)
        authpin = None
        if self.qual is not None:
            if image:
                self.qual['operation_image_sha256'] = sha(canonical({k: v for k, v in self.request.items() if k != 'qualification'}))
            self.request['qualification'] = put_json(self.root, 'state/analysis/synthetic_qualification.json', self.qual)
        if self.auth is not None:
            if authorization:
                self.auth['request_sha256'] = sha(canonical(self.request))
            authpin = put_json(self.root, 'state/analysis/synthetic_authorization.json', self.auth)
        self.scope = dict(schema='commissioning-app-deploy-v1', request=self.request, authorization=authpin)
        put_json(self.root, SCOPE, self.scope)
        self.head = self.commit()

    def admit(self, **changes):
        options = dict(now=NOW); options.update(changes)
        return self.subject.load_scope(self.root, SCOPE, self.head, 'synthetic-target', 'adb', **options)

    def reject(self, **options):
        with self.assertRaises((ValueError, TypeError, OSError)):
            self.admit(**options)

    def board(self):
        return SimpleNamespace(ROOT=self.root, target=lambda: 'synthetic-target', transport=lambda: 'adb',
            adb_executable=lambda: 'adb', SSH_OPTIONS=[], require_transport=mock.Mock(),
            remote=mock.Mock(side_effect=AssertionError('Native transport forbidden')),
            report_app_error=mock.Mock())


class AdmissionTests(DeployFixture):
    def test_all_fourteen_tuples_with_real_git_and_complete_compile_validators(self):
        for profile in PROFILES:
            for motors in (0, 1):
                with self.subTest(profile=profile, motors=motors):
                    self.make(profile, motors)
                    result = self.admit()
                    self.assertEqual(result['request'], self.request)
                    self.assertEqual(result['selection'], self.selected)
                    self.assertEqual(result['request_sha256'], sha(canonical(self.request)))

    def test_check_only_is_local_read_only_and_does_not_claim(self):
        board = self.board()
        before = self.git('status', '--porcelain')
        value = self.subject.check_only(board, SCOPE, self.head, now=NOW)
        self.assertEqual(value['status'], 'ADMITTED_LOCAL')
        self.assertIs(value['board_observed'], False)
        self.assertEqual(value['mode'], 'inhibited_diagnostic')
        board.remote.assert_not_called(); board.require_transport.assert_not_called()
        self.assertFalse((self.root / ('state/analysis/commissioning_deploy_' + RUN)).exists())
        self.assertEqual(self.git('status', '--porcelain'), before)

    def test_source_commit_must_be_actual_matching_blob_even_if_manifest_is_coherent(self):
        original = self.compile_head
        self.make(config=self.config + b'\n// coherent replacement of originally reviewed source\n')
        self.request['source_commit'] = original
        changed = json.loads(self.receipts['inputs']); changed['reviewed_head'] = original
        self.receipts['inputs'] = canonical(changed)
        intent = json.loads(self.receipts['intent']); intent.update(reviewed_head=original,
            inputs_sha256=sha(self.receipts['inputs'])); self.receipts['intent'] = canonical(intent)
        result = json.loads(self.receipts['result']); result['reviewed_head'] = original
        self.receipts['result'] = canonical(result)
        self.refresh()
        with self.assertRaisesRegex(ValueError, 'Current input bytes differ from reviewed HEAD'):
            self.admit()

    def test_missing_source_commit_and_changed_reviewed_deploy_blobs_reject(self):
        self.request['source_commit'] = 'f' * 40
        self.refresh(); self.reject()
        self.make()
        path = self.root / SUBJECT; path.write_bytes(path.read_bytes() + b'\n# drift\n')
        self.reject()

    def test_profile_motor_startup_config_and_artifact_swaps_reject(self):
        for field, value in (('profile', 'p3_drive'), ('motors_allowed', 1), ('startup', 'immediate'),
                              ('config_sha256', 'a' * 64), ('mode', 'operational_commissioning')):
            original = self.request[field]
            self.request[field] = value; self.refresh()
            with self.subTest(field=field): self.reject()
            self.request[field] = original
        self.refresh()
        original = self.receipts['artifacts']
        changed = json.loads(original); changed['layout']['motors_allowed'] = True
        self.receipts['artifacts'] = canonical(changed); self.refresh(); self.reject()

    def test_compile_counts_closures_commands_properties_and_stderr_are_semantic(self):
        mutations = []
        for field, value in (('compiler_calls', True), ('query_calls', 0), ('status', 'FAILED')):
            changed = dict(self.outcome, **{field: value}); mutations.append(('result', canonical(changed)))
        changed = copy.deepcopy(self.outcome); changed['final_checks'][-1]['status'] = 'FAILED'
        mutations.append(('result', canonical(changed)))
        mutations.extend([('compile_command', canonical(self.command + ['--upload'])),
            ('compile_stdout', canonical(self.metadata).replace(b'-DMATCH=0', b'-DMATCH=1')),
            ('properties_stdout', canonical(self.metadata).replace(b'link_mode=static', b'link_mode=dynamic')),
            ('compile_stderr', b'synthetic warning')])
        for role, body in mutations:
            original = self.receipts[role]; self.receipts[role] = body; self.refresh()
            with self.subTest(role=role): self.reject()
            self.receipts[role] = original

    def test_inhibited_source_requires_exact_disabled_grants_axes_origin_and_syntax(self):
        changes = [self.config.replace(b'APP_GRANT_OPPONENTS = 0U;', b'APP_GRANT_OPPONENTS = 1U;'),
            self.config.replace(b'APP_GRANT_OPPONENTS = 0U;', b'APP_GRANT_OPPONENTS = false;'),
            self.config.replace(b'APP_IMU_BODY_AXIS[3] = {0, 0, 0}', b'APP_IMU_BODY_AXIS[3] = {1, 2, 3}'),
            self.config.replace(b'APP_DUMP_ORIGIN = 0U;', b'APP_DUMP_ORIGIN = 1U;'),
            self.config + b'\ninline constexpr std::uint32_t APP_GRANT_EXTRA = 0U;\n',
            self.config + b'\n#define APP_GRANT_OPPONENTS 1\n',
            self.config + b'\ninline constexpr std::uint32_t APP_GRANT_OPPONENTS = 0U;\n']
        for index, config in enumerate(changes):
            self.make(config=config)
            with self.subTest(index=index): self.reject()

    def test_operational_requires_source_grants_configured_buttons_and_every_evidence_check(self):
        self.make('p3_drive', 1, config=self.config); self.reject()
        self.make('p3_drive', 1); self.admit()
        for key in CHECKS:
            original = self.qual['checks'].pop(key); self.refresh()
            with self.subTest(check=key): self.reject()
            self.qual['checks'][key] = original
        for key in GRANTS[:3]:
            original = self.qual['grants'].pop(key); self.refresh()
            with self.subTest(grant=key): self.reject()
            self.qual['grants'][key] = original
        self.qual['grants'][GRANTS[3]] = copy.deepcopy(self.qual['grants'][GRANTS[0]])
        self.refresh(); self.reject()

    def test_operational_turn_basis_and_gates_are_profile_specific(self):
        self.make('p3_turn', 1, turn_basis='imu_accuracy'); self.admit()
        self.make('p3_turn', 1)
        self.qual['turn_basis'] = 'imu_accuracy'; self.refresh(); self.reject()
        self.make('p3_turn', 1)
        self.qual['gate']['reply'] = 'ASSUMED-PHYSICAL'; self.refresh(); self.reject()
        self.make('p5_abort_timing', 1)
        self.qual['gate']['reply'] = 'GATE P3 PASS'; self.refresh(); self.reject()

    def test_qualification_and_authorization_bind_entire_request_and_run(self):
        self.make('p3_stop', 1); self.admit()
        self.request['run_id'] = 'a' * 32
        self.refresh(image=False, authorization=False); self.reject()
        self.make('p3_stop', 1)
        self.qual['operation_image_sha256'] = 'a' * 64
        self.refresh(image=False); self.reject()
        self.make('p3_stop', 1)
        self.auth['request_sha256'] = 'a' * 64
        self.refresh(authorization=False); self.reject()

    def test_authorization_exact_reply_message_and_fresh_utc_window(self):
        self.make('b4_stand', 1); self.admit()
        changes = [('reply', 'RING OK'), ('message_ref', ''),
            ('issued_utc', (NOW + timedelta(seconds=1)).isoformat()),
            ('expires_utc', NOW.isoformat()),
            ('expires_utc', (NOW + timedelta(hours=2)).isoformat()),
            ('issued_utc', '2026-09-26T09:59:00'), ('issued_utc', '2026-09-26T13:59:00+04:00')]
        for field, value in changes:
            old = self.auth[field]; self.auth[field] = value; self.refresh()
            with self.subTest(field=field, value=value): self.reject()
            self.auth[field] = old

    def test_json_unknown_missing_duplicate_nonfinite_and_pin_path_types_refuse(self):
        for field in tuple(self.request):
            original = self.request.pop(field)
            put_json(self.root, SCOPE, dict(self.scope, request=self.request)); self.head = self.commit()
            with self.subTest(missing=field): self.reject()
            self.request[field] = original
        self.refresh()
        raw = canonical(self.scope).decode()
        for changed in ('{"schema":"duplicate",' + raw[1:], raw.replace('"motors_allowed":0', '"motors_allowed":NaN'),
                        raw.replace('"motors_allowed":0', '"motors_allowed":true')):
            put(self.root, SCOPE, changed.encode()); self.head = self.commit(); self.reject()
        self.refresh()
        pin = self.request['build_receipts']['inputs']
        for field, value in (('path', '../escape.json'), ('path', 'C:/escape.json'), ('bytes', True),
                              ('sha256', 'A' * 64)):
            old = pin[field]; pin[field] = value
            put_json(self.root, SCOPE, self.scope); self.head = self.commit()
            with self.subTest(pin_field=field): self.reject()
            pin[field] = old

    def test_cli_requires_exact_order_types_closed_fields_and_head(self):
        good = ['--check-only', '--scope', SCOPE, '--reviewed-head', self.head]
        self.assertEqual(self.subject.parse_request(good), dict(action='--check-only', scope=SCOPE, reviewed_head=self.head))
        bad = [tuple(good), good + ['--upload'], good[:-1], ['--execute', '--reviewed-head', self.head, '--scope', SCOPE]]
        for index in range(len(good)):
            changed = list(good); changed[index] = StrSubclass(changed[index]); bad.append(changed)
        for value in bad:
            with self.subTest(argv=value), self.assertRaises((ValueError, TypeError)):
                self.subject.parse_request(value)


class LifecycleTests(DeployFixture):
    def setup_remote(self, failure=None, closing_failure=False):
        board = self.board()
        calls = []
        baselines = [json.loads((ROOT / (STATIC + name + '.json')).read_bytes())
                     for name in ('cli_initialization_inventory', 'cli_builtin_files_inventory')]
        def remote(target, argv, capture=True, timeout=None):
            calls.append(list(argv))
            index = len(calls) - 1
            if index == 2:
                if failure is not None:
                    raise failure
                # Payload identity is a terminal argument under the inherited MATCH contract.
                payload_sha = next((item for item in reversed(argv) if re.fullmatch('[0-9a-f]{64}', item)), None)
                if payload_sha is None:
                    raise AssertionError('Upload command did not expose checked payload digest')
                return SimpleNamespace(returncode=0, stderr='', stdout=canonical(reply(self.selected, payload_sha)).decode())
            if closing_failure and index == 3:
                raise OSError('synthetic first closing failure')
            value = json.loads(baselines[index if index < 2 else index - 3]['stdout'])
            value['identity']['boot_id'] = BOOT
            return SimpleNamespace(returncode=0, stderr='', stdout=canonical(value).decode())
        board.remote.side_effect = remote
        return board, calls

    def test_success_one_upload_two_prerequisites_each_side_consumed_owner(self):
        board, calls = self.setup_remote()
        outcome = self.subject.upload_precompiled(board, SCOPE, self.head, now=NOW)
        self.assertEqual(outcome['status'], 'ACCEPTED'); self.assertEqual(outcome['attempts'], 1)
        self.assertEqual(len(calls), 5)
        path = self.root / ('state/analysis/commissioning_deploy_' + RUN)
        self.assertTrue((path / 'outcome.json').is_file())
        with self.assertRaises((ValueError, OSError)):
            self.subject.upload_precompiled(board, SCOPE, self.head, now=NOW)
        self.assertEqual(len(calls), 5)

    def test_admission_refusal_never_claims_or_contacts_board(self):
        self.request['startup'] = 'immediate'; self.refresh()
        board = self.board()
        with self.assertRaises((ValueError, OSError)):
            self.subject.upload_precompiled(board, SCOPE, self.head, now=NOW)
        board.remote.assert_not_called()
        self.assertFalse((self.root / ('state/analysis/commissioning_deploy_' + RUN)).exists())

    def test_timeout_unknown_preserves_primary_runs_closing_and_never_retries(self):
        error = subprocess.TimeoutExpired(['synthetic-upload'], 240, output=b'partial', stderr=b'problem')
        board, calls = self.setup_remote(error)
        with self.assertRaises(subprocess.TimeoutExpired) as raised:
            self.subject.upload_precompiled(board, SCOPE, self.head, now=NOW)
        self.assertIs(raised.exception, error)
        self.assertEqual(error.deploy_outcome['status'], 'UNKNOWN')
        self.assertEqual(error.deploy_outcome['attempts'], 1)
        self.assertEqual(len(calls), 5)

    def test_closing_failures_are_independent_and_never_accept(self):
        board, calls = self.setup_remote(closing_failure=True)
        with self.assertRaises(Exception) as raised:
            self.subject.upload_precompiled(board, SCOPE, self.head, now=NOW)
        self.assertEqual(len(calls), 5)
        self.assertEqual(raised.exception.deploy_outcome['status'], 'UNKNOWN')
        self.assertTrue(raised.exception.deploy_outcome['postcheck_errors'])

    def test_outcome_write_failure_cannot_be_success(self):
        board, calls = self.setup_remote()
        original = Path.open
        def guarded(path, *args, **kwargs):
            if path.name == 'outcome.json' and args and 'x' in args[0]:
                raise OSError(errno.ENOSPC, 'synthetic evidence write failure')
            return original(path, *args, **kwargs)
        with mock.patch.object(Path, 'open', guarded), self.assertRaises(OSError) as raised:
            self.subject.upload_precompiled(board, SCOPE, self.head, now=NOW)
        self.assertEqual(len(calls), 5)
        self.assertEqual(raised.exception.deploy_outcome['status'], 'UNKNOWN')


if __name__ == '__main__':
    unittest.main()
