# Tests the fixed production static/Immediate tuple and its actual caller seams.
# Reuses reviewed synthetic ELF/Git fixtures while deriving new expectations explicitly.
# No native transport, physical qualification or human permission is supplied.
import ast
import base64
import bz2
import copy
import hashlib
import json
from pathlib import Path
import sys
import types
import unittest
from unittest import mock

ROOT = Path(__file__).absolute().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / 'tools')]
from tests.tooling import test_commissioning_deploy as old
from tests.tooling.test_commissioning_app_upload import load, RUN, canonical, sha

FQBN = 'arduino:zephyr:unoq:link_mode=static,wait_linux_boot=no'
MACROS = ('SUMOX_B4_STAND', 'SUMOX_P3_DRIVE_TEST', 'SUMOX_P3_TURN_TRIAL',
          'SUMOX_P3_STOP_TRIAL', 'SUMOX_P4_REACTIVE', 'SUMOX_TIMING_EVIDENCE',
          'SUMOX_P5_ABORT_TIMING', 'SUMOX_MOTOR_FAULT_PROBE')
FLAGS = ' '.join(['-DMATCH=1', '-DMOTORS_ALLOWED=1'] + ['-D' + name + '=0' for name in MACROS])
TOOLS = ('compile_match_static.py', 'match_static_policy.py', 'match_static_compile_remote.py',
         'match_static_upload.py', 'deploy_match_static.py', 'run_match_identified_delivery.py')
CONTRACT = 'state/analysis/P7_match_static_contract.md'


def packet_immediate(packet):
    result = dict(packet)
    for name in ('app.ino.bin-zsk.bin', 'app.ino.elf-zsk.bin'):
        assert result[name][14] == 2
        result[name] = result[name][:14] + bytes([6]) + result[name][15:]
    return result


def metadata_immediate(value):
    result = copy.deepcopy(value)
    props = result['builder_result']['build_properties']
    result['builder_result']['build_properties'] = [item.replace(
        'build.fqbn=arduino:zephyr:unoq:link_mode=static', 'build.fqbn=' + FQBN).replace(
        'build.boot_mode=wait', 'build.boot_mode=immediate').replace(
        ' -prelinked  ', ' -prelinked -immediate ') for item in props]
    return result


def fixture_module():
    # Only the existing fixture definitions are projected; no historical tests run.
    path = ROOT / 'tests/tooling/test_commissioning_deploy.py'
    source = path.read_text()
    changes = (('compile_commissioning_app.py', 'compile_match_static.py'),
        ('commissioning_app_static_policy.py', 'match_static_policy.py'),
        ('deploy_commissioning_app.py', 'deploy_match_static.py'),
        ('P7_commissioning_deploy_contract.md', 'P7_match_static_contract.md'),
        ('commissioning-app-static', 'match-static-app-static'),
        ('commissioning-app-deploy', 'match-static-app-deploy'),
        ("profile='b4_stand', motors=0", "profile='match', motors=1"),
        ("'operational_commissioning'", "'operational_match'"),
        ("'startup': 'default'", "'startup': 'immediate'"),
        ('packet = self.fx.packet()', 'packet = packet_immediate(self.fx.packet())'),
        ("        self.command = ['arduino-cli'", "        self.metadata = metadata_immediate(self.metadata)\n        self.command = ['arduino-cli'"))
    for before, after in changes:
        assert before in source, before
        source = source.replace(before, after)
    namespace = types.ModuleType('_match_static_fixture')
    namespace.__file__ = str(path)
    exec(compile(source, str(path), 'exec'), namespace.__dict__)
    namespace.FQBN = FQBN
    namespace.GATES = dict(match='SYNTHETIC-UNUSED')
    namespace.expected_flags = lambda profile, motors: FLAGS
    namespace.packet_immediate, namespace.metadata_immediate = packet_immediate, metadata_immediate
    namespace.SOURCE_PATHS = dict(namespace.SOURCE_PATHS, adapter='tools/match_static_upload.py')
    original_paths = namespace.paths
    namespace.paths = lambda selection: {k: v.replace('commission-', 'match-static-').replace(
        'P7_commissioning_build_raw', 'P7_match_static_raw') for k, v in original_paths(selection).items()}
    def bindings(uploader, selected):
        adapter = load(ROOT / 'tools/match_static_upload.py', '_match_binding_fixture')
        profile = adapter.commissioning_profile(uploader, None, **selected)
        return {**profile['fixed'], 'boot_id': old.BOOT, 'uid': 1000,
            'files': {key: dict(path=value, bytes=8, sha256='a' * 64) for key, value in profile['files'].items()},
            'directories': {name: ['fixture'] for name in uploader.DIRECTORIES}, 'absent': list(profile['absent'])}
    namespace.bindings = bindings
    old_reply = namespace.reply
    namespace.reply = lambda selected, digest: json.loads(canonical(old_reply(selected, digest)).replace(
        b'commissioning-app', b'match-static-app').replace(b'commission-upload-', b'match-static-upload-'))
    return namespace


FX = fixture_module()


class MatchFixture(FX.DeployFixture):
    def setUp(self):
        super().setUp()
        self.app = load(ROOT / 'tools/run_match_identified_delivery.py', '_match_delivery')

    def refresh(self, *, image=True, authorization=True):
        for role, body in self.receipts.items():
            self.request['build_receipts'][role] = old.put(self.root,
                self.located['output'] + '/' + old.ROLES[role], body)
        if self.qual is not None and self.qual['schema'] != 'match-operation-qualification-v1':
            self.qual = dict(schema='match-operation-qualification-v1', source_sha256=self.request['source_sha256'],
                raw_sha256=self.bound['files']['raw']['sha256'], package_sha256=self.bound['files']['sketch']['sha256'],
                operation_image_sha256='', operation='ring', verdict='QUALIFIED_FOR_IDENTIFIED_OPERATION',
                reviewer='synthetic-only', limitations=['NO HARDWARE AUTHORITY'], evidence=[self.measurement])
            self.auth['schema'] = 'match-human-authorization-v1'
        if image:
            identity = {key: self.request[key] for key in ('target', 'transport', 'source_sha256')}
            identity.update(fqbn=FQBN, operation=self.qual['operation'])
            identity.update({key: self.bound[key] for key in ('files', 'directories', 'absent')})
            self.qual['operation_image_sha256'] = sha(canonical(identity))
        self.request['qualification'] = old.put_json(self.root, 'state/analysis/synthetic_qualification.json', self.qual)
        if authorization:
            self.auth['request_sha256'] = sha(canonical(self.request))
        auth = old.put_json(self.root, 'state/analysis/synthetic_authorization.json', self.auth)
        self.scope = dict(schema='match-static-app-deploy-v1', request=self.request, authorization=auth)
        old.put_json(self.root, old.SCOPE, self.scope)
        self.head = self.commit()

    def identified(self):
        for name in ('run_match_identified_delivery.py', 'run_recorder_delivery.py',
                     'dump_match.py', 'validate_csv_bundle.py'):
            old.put(self.root, 'tools/' + name, (ROOT / 'tools' / name).read_bytes())
        body = self.operational_config()
        for name in ('DUMP_ENABLED', 'DUMP_SETUP_PHASE', 'DUMP_EXCLUSIVE_UART', 'DUMP_READY_PIN_OWNED'):
            body = body.replace(('APP_GRANT_' + name + ' = 0U;').encode(),
                                ('APP_GRANT_' + name + ' = 1U;').encode())
        body = body.replace(b'APP_DUMP_RECEIVE_STREAM_ID = 0U;', b'APP_DUMP_RECEIVE_STREAM_ID = 1U;')
        body = body.replace(b'APP_DUMP_SESSION_ID = 0U;', f'APP_DUMP_SESSION_ID = {int(RUN[:16],16)}U;'.encode())
        self.make(config=body)
        self.request['target'] = self.app.TARGET
        self.refresh()
        return self.app.admit(self.root, old.SCOPE, self.head, now=old.NOW)


class Admission(MatchFixture):
    def test_complete_compiler_policy_remote_bundle_and_exact_upload_tuple(self):
        scope = self.admit()
        self.assertEqual((self.owner.fqbn, self.owner.flags, self.owner.startup), (FQBN, FLAGS, 'immediate'))
        self.assertEqual(self.owner.expected_stage, json.loads(self.receipts['staged_files']))
        current = self.compiler.make_owner(dict(action='--check-only', profile='match',
            motors_allowed=1, attempt='seam01', reviewed_head=self.head), root=self.root)
        current.admission()
        policy = current.static_policy()
        policy.validate_preflight(self.receipts['properties_stdout'].decode(),
            build_path=self.owner.build_path, data_dir='/home/arduino/.arduino15')
        remote = load(ROOT / 'tools/match_static_compile_remote.py', '_match_remote')
        bundle = {key: self.owner.code[name] for key, name in self.owner._module.BUNDLE_PATHS.items()}
        # The remote helper is Linux-only; no pwd operation occurs while loading definitions.
        with mock.patch.dict(sys.modules, {'pwd': types.ModuleType('pwd')}):
            primitive, sources = remote.load_bundle(bundle, profile='match', motors_allowed=1,
                attempt='fixture01', source_digest=self.owner.source_sha256)
        self.assertEqual(primitive.REMOTE, self.owner.remote)
        self.assertEqual(set(sources), set(bundle) - {'primitive'})
        command, unused, checks = self.subject.prepare(self.board(), scope)
        payload = json.loads(bz2.decompress(base64.b85decode(command[-1])))
        adapter = load(ROOT / 'tools/match_static_upload.py', '_match_upload_payload')
        projected = adapter.load_module('projected', payload['sources']['adapter']['source'].encode())
        profile = projected.commissioning_profile(self.uploader, None, **payload['selection'])
        self.assertEqual(profile['argv'][4:8], ['--fqbn', FQBN, '--input-file', self.located['build'] + '/app.ino.bin'])
        self.assertNotIn('compile', profile['argv'])
        self.assertEqual(len(checks), 2)

    def test_real_qualification_authority_and_compiler_metadata_refusals(self):
        self.assertNotIn('gate', self.qual)
        for change in ('authority', 'image', 'compile'):
            prior = copy.deepcopy((self.auth, self.qual, self.receipts))
            if change == 'authority': self.auth['reply'] = 'STAND OK'
            if change == 'image': self.qual['package_sha256'] = 'a' * 64
            if change == 'compile': self.receipts['properties_stdout'] = self.receipts['properties_stdout'].replace(
                b'build.boot_mode=immediate', b'build.boot_mode=wait')
            self.refresh()
            with self.subTest(change=change): self.reject()
            self.auth, self.qual, self.receipts = prior
        self.refresh()
        self.qual['operation'] = 'stand'; self.auth['reply'] = 'STAND OK'; self.refresh()
        self.admit()


    def test_one_production_upload_closes_and_consumes_the_paired_owner(self):
        deploy, scope, unused = self.identified()
        self.app.reserve(deploy, scope)
        board, calls = FX.LifecycleTests.setup_remote(self)
        board.target = lambda: self.app.TARGET
        result = deploy.upload_precompiled(board, old.SCOPE, self.head, now=old.NOW, _delivery=scope['delivery'])
        self.assertEqual((result['status'], result['attempts'], len(calls)), ('ACCEPTED', 1, 5))
        self.assertTrue((scope['delivery_owner'] / 'upload/outcome.json').is_file())
        with self.assertRaises(ValueError):
            deploy.upload_precompiled(board, old.SCOPE, self.head, now=old.NOW, _delivery=scope['delivery'])
        self.assertEqual(len(calls), 5)

    def test_paired_production_identity_receiver_and_session_consumption(self):
        deploy, scope, board = self.identified()
        with self.assertRaisesRegex(ValueError, 'separately qualified'):
            deploy.check_only(board, old.SCOPE, self.head, now=old.NOW)
        receiver, owner, commands, dump = self.app.receiver_scope(scope, board)
        self.assertIs(receiver.accept_capture, self.app.accept_capture)
        self.assertEqual(owner.session, int(RUN[:16], 16))
        self.assertEqual(owner.reviewed_head, self.compile_head)
        self.assertEqual([bound for unused, bound in commands.allowed], [915, 5])
        self.app.reserve(deploy, scope)
        self.assertIn('match_identified_delivery_', str(scope['delivery_owner']))
        with self.assertRaises(ValueError): self.app.admit(self.root, old.SCOPE, self.head, now=old.NOW)
        (scope['delivery_owner'] / 'claim.json').write_bytes(b'{}\n')
        with self.assertRaisesRegex(ValueError, 'claim changed'):
            deploy.upload_precompiled(board, old.SCOPE, self.head, now=old.NOW, _delivery=scope['delivery'])


class Policy(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        old.DeployFixture.setUpClass()
        cls.fx = old.DeployFixture.fx
        cls.policy = load(ROOT / 'tools/match_static_policy.py', '_match_policy')

    def test_only_closed_tuple_and_immediate_header_with_full_body_checks(self):
        kwargs = dict(profile='match', motors_allowed=1, snapshots=self.fx.snapshots)
        packet = packet_immediate(self.fx.packet())
        def validate(value):
            return self.policy.validate_artifacts(value, self.fx.native_source, self.fx.frozen_source,
                exported_flat_package=value['app.ino.bin-zsk.bin'], **kwargs)
        result = validate(packet)
        self.assertEqual(result['flags'], FLAGS)
        self.assertEqual(result['fqbn'], FQBN)
        self.assertEqual(result['validator_report']['status'], 'STATIC_NATIVE_TLS_LAYOUT_PACKAGE_PASS')
        for flag in (0, 2, 4, 7):
            bad = dict(packet)
            for name in ('app.ino.bin-zsk.bin', 'app.ino.elf-zsk.bin'):
                bad[name] = bad[name][:14] + bytes([flag]) + bad[name][15:]
            with self.subTest(flag=flag), self.assertRaises(ValueError): validate(bad)
        bad = dict(packet); bad['app.ino.bin-zsk.bin'] = bad['app.ino.bin-zsk.bin'][:-1] + b'x'
        with self.assertRaises(ValueError): validate(bad)
        for profile, motor in (('p4_reactive', 1), ('match', 0), ('match', True)):
            with self.assertRaises(ValueError): self.policy.safety_flags(profile, motors_allowed=motor)

    def test_compiler_request_refuses_other_tuples_and_legacy_policy_is_unchanged(self):
        compiler = load(ROOT / 'tools/compile_match_static.py', '_match_compile')
        argv = ['--check-only', '--profile', 'match', '--motors-allowed', '1', '--attempt', 'fixture01', '--reviewed-head', 'a'*40]
        self.assertEqual(compiler.parse_request(argv)['profile'], 'match')
        for index, value in ((2, 'b4_stand'), (4, '0'), (6, '../escape')):
            bad = list(argv); bad[index] = value
            with self.assertRaises(ValueError): compiler.parse_request(bad)
        legacy = load(ROOT / 'tools/commissioning_app_static_policy.py', '_unchanged_policy')
        self.assertEqual(legacy.FQBN, 'arduino:zephyr:unoq:link_mode=static')
        with self.assertRaises(ValueError): legacy.safety_flags('match', motors_allowed=1)


if __name__ == '__main__':
    unittest.main()
