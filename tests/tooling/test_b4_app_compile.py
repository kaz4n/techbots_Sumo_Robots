# Tests the fixed B4 M0 compile integration from its adopted public contract.
# Retains checked ordinary admission and artifact lifecycle fixtures without a board.
# The independent oracle is sealed before either new implementation is inspected.
import ast
import base64
import builtins
import copy
import hashlib
import io
import json
import os
from pathlib import Path
import sys
import subprocess
import types
import unittest
import zlib
from unittest import mock
from contextlib import ExitStack, contextmanager, redirect_stdout


ROOT = Path(__file__).resolve().parents[2]
RAW = 'state/analysis/P7_b4_app_compile_raw'
ORACLE = RAW + '/oracle01.json'
SUBJECT = 'tools/compile_b4_app_static.py'
REMOTE_SUBJECT = 'tools/b4_app_compile_remote.py'
POLICY = 'tools/b4_app_static_policy.py'
CONTRACT = 'state/analysis/P7_b4_app_compile_contract.md'
FLAGS = ('-DMATCH=0 -DMOTORS_ALLOWED=0 -DSUMOX_B4_STAND=1'
         ' -DSUMOX_P3_DRIVE_TEST=0 -DSUMOX_P3_TURN_TRIAL=0'
         ' -DSUMOX_P3_STOP_TRIAL=0 -DSUMOX_P4_REACTIVE=0'
         ' -DSUMOX_TIMING_EVIDENCE=0 -DSUMOX_P5_ABORT_TIMING=0'
         ' -DSUMOX_MOTOR_FAULT_PROBE=0')
SOURCE = '9044ebbb3cd3b2dbb7aa5984dd5ff23bfff697372f1f29d56693af9ea5eaf31a'
ATTEMPT = 'b4-app-m0-static01'
REMOTE = '/home/arduino/sumox26_codex_build/' + ATTEMPT
BUILD, ARTIFACTS = REMOTE + '/build', REMOTE + '/artifacts'
_SEAL = None
_REMOTE_FIXTURE = None


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def checked(name):
    info = seal()
    identity = info['subjects'][name] if name in info['subjects'] else info['inputs'][name]
    raw = (ROOT / name).read_bytes()
    if {'bytes': len(raw), 'sha256': sha(raw)} != identity:
        raise AssertionError('Frozen oracle input differs: ' + name)
    return raw


def seal():
    global _SEAL
    if _SEAL is None:
        value = json.loads((ROOT / ORACLE).read_bytes())
        if value['schema'] != 'd214-independent-compile-oracle-v1' or value['status'] != 'FINAL':
            raise AssertionError('Independent oracle is not frozen')
        body = Path(__file__).read_bytes()
        if value['oracle'] != {'bytes': len(body), 'sha256': sha(body)}:
            raise AssertionError('Oracle body changed after freeze')
        _SEAL = value
    return _SEAL


def private(raw, path, name):
    module = types.ModuleType(name)
    module.__file__ = str(path)
    module.__dict__['__builtins__'] = dict(vars(builtins))
    exec(compile(raw, str(path), 'exec'), module.__dict__)
    return module


def load_checked(name, label):
    return private(checked(name), ROOT / name, label)


def replace_checked(raw, steps):
    for row in steps:
        old, new = row['old'].encode(), row['new'].encode()
        if raw.count(old) != row['count']:
            raise AssertionError('Historical fixture occurrence changed: ' + repr(old[:80]))
        raw = raw.replace(old, new)
    return raw


def fixture_bytes(kind):
    spec = seal()['fixtures'][kind]
    raw = checked(spec['source'])
    if spec.get('baseline'):
        historical = json.loads(checked(spec['baseline']['path']))['fixtures'][spec['baseline']['key']]
        if historical['source'] != spec['source']:
            raise AssertionError('Historical fixture source selection changed')
        raw = replace_checked(raw, historical['steps'])
        if {'bytes': len(raw), 'sha256': sha(raw)} != historical['projected']:
            raise AssertionError('Accepted D208 fixture bytes changed')
    raw = replace_checked(raw, spec['steps'])
    if spec.get('select_function'):
        lines = raw.splitlines(keepends=True)
        selected = [node for node in ast.parse(raw).body if isinstance(node, ast.FunctionDef)
                    and node.name == spec['select_function']]
        if len(selected) != 1:
            raise AssertionError('Ordinary mapping fixture selection changed')
        node = selected[0]
        raw = b''.join(lines[node.lineno - 1:node.end_lineno]) + b'\n'
    if {'bytes': len(raw), 'sha256': sha(raw)} != spec['projected']:
        raise AssertionError('Historical fixture projection changed: ' + kind)
    return raw


def load_fixture(kind):
    spec = seal()['fixtures'][kind]
    return private(fixture_bytes(kind), ROOT / spec['source'], '_d214_fixture_' + kind)


def bundle():
    return {key: checked(path) for key, path in seal()['interface']['bundle_sources'].items()}


def snapshots():
    return {name: checked(name) for name in seal()['interface']['snapshot_sources']}


def remote_fixture():
    global _REMOTE_FIXTURE
    if _REMOTE_FIXTURE is not None:
        return _REMOTE_FIXTURE
    result = load_fixture('remote')
    prior = result.load
    def load(path, name):
        if Path(path) == ROOT / 'tools/app_motor_fault_compile_remote.py':
            return load_checked(REMOTE_SUBJECT, name)
        relative = Path(path).relative_to(ROOT).as_posix()
        checked(relative)
        return prior(path, name)
    result.load = load
    result.BUNDLE = {key: (path, seal()['inputs'].get(path, seal()['subjects'].get(path))['sha256'])
                     for key, path in seal()['interface']['bundle_sources'].items()}
    result.checked_bundle = bundle
    _REMOTE_FIXTURE = result
    return result


def caller_fixture():
    result = load_fixture('caller')
    prior = result.load
    def load(path, name):
        if Path(path) == ROOT / SUBJECT:
            return load_checked(SUBJECT, '_d214_launcher').load_caller(root=ROOT)
        if Path(path) == ROOT / 'tests/tooling/test_app_motor_fault_compile_remote.py':
            return remote_fixture()
        relative = Path(path).relative_to(ROOT).as_posix()
        checked(relative)
        return prior(path, name)
    result.load = load
    result.FIXED = list(seal()['interface']['required_files'])
    original_controlled = result.CallerFixture.controlled
    def controlled(case, owner, **kwargs):
        original_controlled(case, owner, **kwargs)
        previous = owner.direct
        endpoint = SourceEndpoint(case, owner, previous)
        case.patch(owner, 'direct', endpoint)
        owner.fixture_source_endpoint = endpoint
        return owner
    result.CallerFixture.controlled = controlled
    result.admit_source_for_program = admit_source_for_program
    return result


def source_record(raw):
    return dict(identity=[3, 41, 0o100600, 1, 1000, 1000, len(raw), 123, 123], sha256=sha(raw))


class SourceEndpoint:
    """Portable transport double; descriptor guards run separately on Linux."""
    def __init__(self, case, owner, fallback=None):
        self.case, self.owner, self.fallback = case, owner, fallback
        self.data, self.calls, self.failures = b'', [], {}

    def __call__(self, program, label, timeout=90):
        if label not in ('artifact-source-first', 'artifact-source-second', 'artifact-sources-final'):
            if self.fallback is None: raise AssertionError('Unexpected transfer label: ' + label)
            return self.fallback(program, label, timeout)
        self.calls.append((label, program))
        self.case.events.append(('direct', label, timeout))
        folder = self.case.folder(self.owner, label)
        if label in self.failures: raise self.failures[label]
        _, packed = self.owner._artifact_payload()
        if label == 'artifact-source-first':
            self.case.assertEqual(self.data, b'')
            chunk = packed[:16384]
            self.case.assertIn(base64.b64encode(chunk).decode(), program)
            self.data = chunk
        elif label == 'artifact-source-second':
            self.case.assertEqual(self.data, packed[:16384])
            chunk = packed[16384:]
            self.case.assertIn(base64.b64encode(chunk).decode(), program)
            self.data += chunk
        return subprocess.CompletedProcess([], 0, json.dumps(source_record(self.data)).encode(), b''), folder


def admit_source_for_program(case, owner):
    # New payload prerequisite for the unchanged inherited argv assertions.
    endpoint = SourceEndpoint(case, owner)
    with mock.patch.object(owner, 'direct', endpoint):
        owner.prepare_artifact_sources()
    return endpoint


class DescriptorFixture:
    """Execute only source IO/decoding in a private RAM tree, never the board preamble."""
    def __init__(self, case, owner):
        self.case, self.owner = case, owner
        self.root = case.root / 'payload-descriptor-sandbox'
        self.remote = self.root / REMOTE.lstrip('/')
        self.remote.mkdir(parents=True, mode=0o700)
        self.remote.chmod(0o700)
        self.path = self.remote / 'artifact-sources.zlib'
        self.handles = set()

    def execute(self, program, decode_only=False):
        prefix = self.owner.preamble()
        self.case.assertTrue(program.startswith(prefix))
        tree = ast.parse(program[len(prefix):])
        if decode_only:
            ends = [i for i, node in enumerate(tree.body) if isinstance(node, ast.Assign)
                    and isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Attribute)
                    and node.value.func.attr == 'inspect_artifacts']
            self.case.assertEqual(len(ends), 1)
            tree.body = tree.body[:ends[0]]
        opened, closed = os.open, os.close
        def open_local(path, flags, mode=0o777, *, dir_fd=None):
            if str(path) == '/' and dir_fd is None:
                path = str(self.root)
            elif dir_fd not in self.handles or Path(str(path)).is_absolute():
                raise AssertionError('Descriptor program escaped its fixture: ' + str(path))
            fd = opened(path, flags, mode, dir_fd=dir_fd)
            self.handles.add(fd)
            return fd
        def close_local(fd):
            self.case.assertIn(fd, self.handles)
            try: return closed(fd)
            finally: self.handles.remove(fd)
        namespace = dict(os=os, json=json, hashlib=hashlib, REMOTE=REMOTE,
                         identity=dict(uid=1000, user='arduino'))
        # Standard imports are retained; only native identity/process preamble is replaced.
        exec('import stat,re,base64,zlib,types\nfrom pathlib import Path', namespace)
        output = io.StringIO()
        try:
            with mock.patch.object(os, 'open', open_local), mock.patch.object(os, 'close', close_local), \
                    redirect_stdout(output):
                exec(compile(tree, '<owned-source-descriptor-fixture>', 'exec'), namespace)
        finally:
            leaked = set(self.handles)
            for fd in tuple(self.handles):
                closed(fd); self.handles.remove(fd)
            self.case.assertFalse(leaked, 'Every descriptor must close on success and failure')
        return namespace if decode_only else json.loads(output.getvalue())

    def transfer(self, action, token='', previous=None):
        return self.execute(self.owner.artifact_source_program(action, token=token, previous=previous))


def ordinary_fixture(base):
    # The eight selected source-mapping methods and their helper are unchanged.
    raw = fixture_bytes('ordinary')
    module = private(raw, ROOT / 'tests/tooling/test_compile_ordinary_app_static.py',
                     '_d214_ordinary_mapping_cases')
    module.__dict__.update(ROOT=ROOT, original=checked, sha=sha, Path=Path,
                           sys=sys, mock=mock, unittest=unittest)
    return module.ordinary_cases(base)


def caller_additions(base):
    class B4CallerContract(base.CallerFixture):
        def test_closed_manifest_and_profile_use_current_source_without_grant_changes(self):
            owner = self.owner(); owner.local()
            self.assertEqual(set(owner.inputs['files']), set(seal()['interface']['required_files']) |
                             set(owner.source_names()))
            self.assertEqual(owner.source_sha256, SOURCE)
            self.assertEqual(owner.flags, FLAGS)
            self.assertEqual(owner.startup, 'default')
            self.assertEqual(owner.fqbn, 'arduino:zephyr:unoq:link_mode=static')
            self.assertEqual(owner.stage_path, self.root / 'build/stage' / ATTEMPT / 'app')
            for name in ('src/config.h', 'src/app/configured_setup.h', 'src/app/app.ino'):
                self.assertEqual(owner.code[name], checked(name))
            self.assertNotIn('bench/', '\n'.join(owner.source_names()))

        def test_both_real_metadata_validators_observe_explicit_M0_snapshots(self):
            owner = self.owner(); owner.local(); policy = owner.static_policy()
            seen = []; previous = sys.getprofile()
            def profile(frame, event, value):
                if event == 'call' and frame.f_code.co_name in (
                        'validate_preflight', 'validate_compile_result') and \
                        'SNAPSHOT_PINS' in frame.f_globals:
                    seen.append((frame.f_code.co_name, frame.f_locals.get('motors_allowed'),
                                 copy.deepcopy(frame.f_locals.get('snapshots'))))
            sys.setprofile(profile)
            try:
                raw = self.metadata()
                first = policy.validate_preflight(raw, build_path=BUILD, data_dir=base.DATA)
                second = policy.validate_compile_result(raw, build_path=BUILD, data_dir=base.DATA)
            finally:
                sys.setprofile(previous)
            self.assertEqual(first, second)
            self.assertEqual(first['compiler.cpp.extra_flags'], FLAGS)
            self.assertEqual(first['compiler.c.extra_flags'], FLAGS)
            self.assertEqual([row[0] for row in seen], ['validate_preflight', 'validate_compile_result'])
            expected = {name: checked(name) for name in seal()['interface']['snapshot_sources']}
            for _, mode, snapshots in seen:
                self.assertIs(type(mode), int); self.assertEqual(mode, 0)
                self.assertEqual(snapshots, expected)

        def test_real_metadata_refuses_ordinary_M1_MATCH_short_reordered_extra_and_immediate(self):
            owner = self.owner(); owner.local(); policy = owner.static_policy(); raw = self.metadata()
            variants = [raw.replace(FLAGS, '-DMATCH=0 -DMOTORS_ALLOWED=0'),
                        raw.replace(FLAGS, FLAGS.replace('MOTORS_ALLOWED=0', 'MOTORS_ALLOWED=1')),
                        raw.replace(FLAGS, FLAGS.replace('MATCH=0', 'MATCH=1')),
                        raw.replace(FLAGS, FLAGS.rsplit(' ', 1)[0]),
                        raw.replace(FLAGS, ' '.join(reversed(FLAGS.split()))),
                        raw.replace(FLAGS, FLAGS + ' -DMATCH=0')]
            envelope = json.loads(raw)
            for key in ('build.fqbn', 'build.boot_mode'):
                changed = copy.deepcopy(envelope)
                props = changed['builder_result']['build_properties']
                indexes = [i for i, value in enumerate(props) if value.startswith(key + '=')]
                self.assertEqual(len(indexes), 1)
                props[indexes[0]] = key + ('=arduino:zephyr:unoq:link_mode=dynamic'
                                          if key == 'build.fqbn' else '=immediate')
                variants.append(json.dumps(changed))
            for text in variants:
                self.assertNotEqual(text, raw)
                for method in (policy.validate_preflight, policy.validate_compile_result):
                    with self.subTest(method=method.__name__, text=text[:80]):
                        self.reject(lambda: method(text, build_path=BUILD, data_dir=base.DATA))

        def test_all_new_snapshot_and_policy_pins_survive_manifest_repair(self):
            names = [POLICY, *seal()['interface']['snapshot_sources']]
            for name in names:
                path = self.root / name; before = path.read_bytes()
                path.write_bytes(before + b'\n# unreviewed snapshot\n')
                self.manifest(files=dict(self.files, **{name: sha(path.read_bytes())}))
                with self.subTest(path=name): self.reject(self.owner().check)
                path.write_bytes(before); self.manifest()

        def test_B4_layout_mode_exact_integer_and_stale_ordinary_are_refused(self):
            owner = self.owner(); owner.local(); original = self.remote_fixture.synthetic_reply()
            self.assertEqual(owner.validate_artifact_reply(json.dumps(original)), original)
            self.assertIs(type(original['layout']['motors_allowed']), int)
            self.assertEqual(original['layout']['motors_allowed'], 0)
            bad_values = [True, False, 1, -1, None, 0.0, '0']
            for mode in bad_values:
                changed = copy.deepcopy(original); changed['layout']['motors_allowed'] = mode
                before = copy.deepcopy(changed)
                with self.subTest(mode=repr(mode)):
                    self.reject(lambda: owner.validate_artifact_reply(json.dumps(changed)))
                self.assertEqual(changed, before)
            changed = copy.deepcopy(original); del changed['layout']['motors_allowed']
            self.reject(lambda: owner.validate_artifact_reply(json.dumps(changed)))
            for key, value in [('schema', 'ordinary-app-static-artifacts-v1'),
                               ('build_path', '/home/arduino/sumox26_codex_build/ordinary-app-static01/build')]:
                changed = copy.deepcopy(original); changed[key] = value
                self.reject(lambda: owner.validate_artifact_reply(json.dumps(changed)))
            changed = copy.deepcopy(original)
            changed['layout']['status'] = 'STATIC_ORDINARY_APP_LAYOUT_PACKAGE_PASS'
            self.reject(lambda: owner.validate_artifact_reply(json.dumps(changed)))

        def test_old_ordinary_owners_remain_intact_but_old_schema_cannot_be_admitted(self):
            for name in ('state/analysis/P7_ordinary_app_static_compile_raw/native_static01/retained',
                         'build/stage/ordinary-app-static01/retained'):
                path = self.root / name; path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(b'old owner remains historical')
            before = base.file_set(self.root); self.owner().check()
            self.assertEqual(base.file_set(self.root), before)
            self.manifest(schema='ordinary-app-static-inputs-v1')
            self.reject(self.owner().check)
            self.assertFalse((self.root / RAW / 'native_static01').exists())

        def test_actual_payload_has_exact_eight_sources_and_bounded_byte_roundtrip(self):
            owner = self.owner(); owner.local()
            raw, packed = owner._artifact_payload()
            self.assertIs(type(raw), bytes); self.assertIs(type(packed), bytes)
            self.assertLessEqual(len(raw), 262144)
            self.assertGreater(len(packed), 16384); self.assertLessEqual(len(packed), 32768)
            self.assertEqual(zlib.decompress(packed), raw)
            self.assertEqual(zlib.compress(raw, 9), packed)
            packet = json.loads(raw)
            self.assertEqual(set(packet), {'source', 'bundle'})
            self.assertEqual(packet['source'].encode(), checked(REMOTE_SUBJECT))
            self.assertEqual({key: value.encode() for key, value in packet['bundle'].items()}, bundle())
            self.assertEqual(len(packet['bundle']), 8)
            self.assertEqual(raw, json.dumps(packet, sort_keys=True, separators=(',', ':')).encode())

        def test_no_alternative_profile_CLI_or_mutated_D208_bootstrap_is_admitted(self):
            launcher = load_checked(SUBJECT, '_d214_cli_only')
            for option, value in (('--motors-allowed', '1'), ('--profile', 'M1'),
                                  ('--flags', FLAGS), ('--upload', 'true')):
                argv = ['--execute', '--reviewed-head', base.HEAD, option, value]
                with self.subTest(option=option), mock.patch.object(
                        Path, 'read_bytes', side_effect=AssertionError('Invalid CLI performed I/O')):
                    self.reject(lambda: launcher.parse_request(argv))
            path = self.root / 'tools/compile_ordinary_app_static.py'; before = path.read_bytes()
            path.write_bytes(before + b'\n# changed predecessor\n')
            self.reject(lambda: launcher.load_caller(root=self.root))
            self.assertFalse((self.root / RAW / 'native_static01').exists())
    return B4CallerContract


def transfer_cases(base):
    class SourceTransferContract(base.CallerFixture):
        def prepared(self):
            owner = self.owner(); owner.local(); owner.prepare(); owner.claim()
            return owner

        def test_exact_transfer_order_single_compile_and_closing(self):
            owner = self.controlled(self.owner()); result = owner.run()
            labels = [row[1] for row in self.events if row[0] == 'direct']
            wanted = ['artifact-source-first', 'artifact-source-second', 'artifacts',
                      'artifacts-final', 'artifact-sources-final']
            self.assertEqual([label for label in labels if label in wanted][:3], wanted[:3])
            for label in wanted: self.assertEqual(labels.count(label), 1)
            for label in wanted[3:]: self.assertGreater(labels.index(label), labels.index('artifacts'))
            self.assertEqual(labels[:labels.index(wanted[0])].count('checked-command'), 2)
            self.assertEqual((owner.compiler_calls, owner.query_calls), (1, 1))
            self.assertEqual(result['status'], 'COMPILE_CHECKED')
            rows = [row for row in result['final_checks'] if row['name'] == 'artifact_sources']
            self.assertEqual(len(rows), 1); self.assertEqual(rows[0]['status'], 'PASS')
            _, packed = owner._artifact_payload()
            self.assertEqual(owner.fixture_source_endpoint.data, packed)
            self.assertEqual(owner.artifact_sources_identity, source_record(packed))
            self.assertIs(owner.artifact_sources_attempted, True)
            count = len(owner.fixture_source_endpoint.calls)
            self.reject(owner.prepare_artifact_sources)
            self.assertEqual(len(owner.fixture_source_endpoint.calls), count)

        def test_attempt_consumed_before_local_payload_failure(self):
            owner = self.prepared()
            self.assertIs(owner.artifact_sources_attempted, False)
            self.assertIsNone(owner.artifact_sources_identity)
            primary = ValueError('fixture payload packing failed')
            with mock.patch.object(owner, '_artifact_payload', side_effect=primary), \
                    mock.patch.object(owner, 'direct', side_effect=AssertionError('Unexpected transport')):
                with self.assertRaises(ValueError) as caught: owner.prepare_artifact_sources()
                self.assertIs(caught.exception, primary)
                self.assertIs(owner.artifact_sources_attempted, True)
                self.reject(owner.prepare_artifact_sources)
            self.assertIsNone(owner.artifact_sources_identity)

        def failed_transfer(self, label):
            owner = self.controlled(self.owner()); endpoint = owner.fixture_source_endpoint
            primary = subprocess.TimeoutExpired(['source-only-fixture'], 90, output=b'partial')
            endpoint.failures[label] = primary
            with self.assertRaises(subprocess.TimeoutExpired) as caught: owner.run()
            self.assertIs(caught.exception, primary)
            outcome = primary.compile_outcome
            self.assertEqual(outcome['status'], 'FAILED')
            self.assertEqual(outcome['first_error']['message'], str(primary))
            self.assertEqual((owner.compiler_calls, owner.query_calls), (1, 1))
            self.assertIs(owner.artifact_sources_attempted, True)
            self.assertIsNone(owner.artifact_sources_identity)
            self.assertEqual(sum(row[0] == label for row in endpoint.calls), 1)
            self.assertFalse(any(row[1] == 'artifacts' for row in self.events if row[0] == 'direct'))
            rows = [row for row in outcome['final_checks'] if row['name'] == 'artifact_sources']
            self.assertEqual(len(rows), 1); self.assertEqual(rows[0]['status'], 'FAILED')
            self.assertGreaterEqual(len(outcome['final_checks']), 8)
            self.assertTrue(any(row[0] == 'policy' for row in self.events))
            before = len(endpoint.calls); self.reject(owner.prepare_artifact_sources)
            self.assertEqual(len(endpoint.calls), before)

        def test_first_transfer_timeout_is_not_retried_and_all_closures_run(self):
            self.failed_transfer('artifact-source-first')

        def test_second_transfer_timeout_retains_partial_failure_and_all_closures(self):
            self.failed_transfer('artifact-source-second')

        def test_complete_payload_final_read_failure_invalidates_compile(self):
            owner = self.controlled(self.owner()); endpoint = owner.fixture_source_endpoint
            primary = OSError('fixture immutable payload disappeared')
            endpoint.failures['artifact-sources-final'] = primary
            with self.assertRaises((OSError, ValueError, RuntimeError)) as caught: owner.run()
            outcome = caught.exception.compile_outcome
            self.assertEqual(outcome['status'], 'FAILED')
            rows = [row for row in outcome['final_checks'] if row['name'] == 'artifact_sources']
            self.assertEqual(len(rows), 1); self.assertEqual(rows[0]['status'], 'FAILED')
            self.assertIn(str(primary), str(rows[0]['error']))
            self.assertEqual((owner.compiler_calls, owner.query_calls), (1, 1))

        def test_checked_transfer_reply_requires_exact_record_and_all_numeric_fields(self):
            owner = self.owner(); raw = b'x' * 16384; valid = source_record(raw)
            self.assertEqual(owner.checked_source_reply(json.dumps(valid), len(raw), sha(raw)), valid)
            variants = [None, [], {}, dict(valid, extra=1), dict(valid, sha256='A' * 64),
                        dict(valid, sha256='0' * 64), dict(valid, identity=valid['identity'][:-1])]
            for index in range(9):
                for bad in (-1, True, 2**64, 1.5, '1', None):
                    changed = copy.deepcopy(valid); changed['identity'][index] = bad; variants.append(changed)
            for index, bad in ((2, 0o100644), (3, 2), (4, 0), (5, 0), (6, len(raw) + 1)):
                changed = copy.deepcopy(valid); changed['identity'][index] = bad; variants.append(changed)
            for value in variants:
                with self.subTest(record=value):
                    self.reject(lambda: owner.checked_source_reply(json.dumps(value), len(raw), sha(raw)))
            for text in ('', '[]', 'NaN', '{"sha256":"duplicate",' + json.dumps(valid)[1:]):
                self.reject(lambda: owner.checked_source_reply(text, len(raw), sha(raw)))

        def test_actual_full_native_argv_fits_both_transfers_read_and_artifact(self):
            owner = self.prepared(); _, packed = owner._artifact_payload()
            first, full = source_record(packed[:16384]), source_record(packed)
            for record in (first, full):
                for index in (0, 1, 7, 8): record['identity'][index] = 2**64 - 1
            owner.artifact_sources_attempted, owner.artifact_sources_identity = True, full
            programs = [owner.artifact_source_program('first', token=base64.b64encode(packed[:16384]).decode()),
                        owner.artifact_source_program('second', token=base64.b64encode(packed[16384:]).decode(), previous=first),
                        owner.artifact_source_program('read', previous=full), owner.artifact_program()]
            captured = []
            def process(argv, **kwargs):
                captured.append(argv); return subprocess.CompletedProcess(argv, 0, b'{}', b'')
            with mock.patch.object(subprocess, 'run', process):
                for index, program in enumerate(programs): owner.direct(program, 'argv-' + str(index))
                self.assertEqual(len(captured), 4)
                for argv in captured:
                    self.assertEqual(argv[1:3], ['-s', base.BOARD])
                    native = [base.ADB, *argv[1:]]
                    self.assertLessEqual(len(subprocess.list2cmdline(native).encode('utf-16-le')) // 2 + 1, 30000)
                captured.clear(); self.reject(lambda: owner.direct('x' * 40000, 'oversize'))
                self.assertFalse(captured)

        @unittest.skipUnless(sys.platform == 'linux', 'Real source-payload descriptor fixtures require Linux')
        def test_descriptor_two_transfers_roundtrip_and_final_read_decode_real_sources(self):
            owner = self.prepared(); fs = DescriptorFixture(self, owner); _, packed = owner._artifact_payload()
            first = fs.transfer('first', base64.b64encode(packed[:16384]).decode())
            self.assertEqual(fs.path.read_bytes(), packed[:16384])
            full = fs.transfer('second', base64.b64encode(packed[16384:]).decode(), first)
            self.assertEqual(fs.path.read_bytes(), packed)
            self.assertEqual(full['sha256'], sha(packed)); self.assertEqual(full['identity'][6], len(packed))
            self.assertEqual(fs.transfer('read', previous=full), full)
            owner.artifact_sources_attempted, owner.artifact_sources_identity = True, full
            decoded = fs.execute(owner.artifact_program(), decode_only=True)
            self.assertEqual(decoded['source'], checked(REMOTE_SUBJECT))
            self.assertEqual(decoded['bundle'], bundle())
            self.assertEqual(fs.path.read_bytes(), packed)
            self.assertEqual({path.name for path in fs.remote.iterdir()}, {'artifact-sources.zlib'})

        @unittest.skipUnless(sys.platform == 'linux', 'Real source-payload descriptor fixtures require Linux')
        def test_first_transfer_refuses_existing_regular_symlink_and_hardlink_without_mutation(self):
            owner = self.prepared(); fs = DescriptorFixture(self, owner); _, packed = owner._artifact_payload()
            target = fs.remote / 'preserved-target'; target.write_bytes(b'retained fixture')
            for kind in ('regular', 'symlink', 'hardlink'):
                if kind == 'regular': fs.path.write_bytes(b'old partial')
                elif kind == 'symlink': fs.path.symlink_to(target)
                else: os.link(target, fs.path)
                before = fs.path.read_bytes()
                with self.subTest(kind=kind):
                    self.reject(lambda: fs.transfer('first', base64.b64encode(packed[:16384]).decode()))
                self.assertEqual(fs.path.read_bytes(), before)
                self.assertEqual(target.read_bytes(), b'retained fixture')
                fs.path.unlink()

        @unittest.skipUnless(sys.platform == 'linux', 'Real source-payload descriptor fixtures require Linux')
        def test_second_transfer_refuses_prior_record_hash_mode_link_and_byte_drift(self):
            owner = self.prepared(); fs = DescriptorFixture(self, owner); _, packed = owner._artifact_payload()
            for kind in ('record', 'hash', 'mode', 'hardlink', 'bytes'):
                first = fs.transfer('first', base64.b64encode(packed[:16384]).decode())
                if kind == 'record': first['identity'][1] += 1
                elif kind == 'hash': first['sha256'] = '0' * 64
                elif kind == 'mode': fs.path.chmod(0o644)
                elif kind == 'hardlink': os.link(fs.path, fs.remote / 'second-link')
                else: fs.path.write_bytes(b'!' + packed[1:16384])
                before = fs.path.read_bytes()
                with self.subTest(kind=kind):
                    self.reject(lambda: fs.transfer('second', base64.b64encode(packed[16384:]).decode(), first))
                self.assertEqual(fs.path.read_bytes(), before)
                fs.path.unlink()
                if kind == 'hardlink': (fs.remote / 'second-link').unlink()

        @unittest.skipUnless(sys.platform == 'linux', 'Real source-payload descriptor fixtures require Linux')
        def test_read_refuses_complete_payload_replacement_trailing_or_corrupt_bytes(self):
            owner = self.prepared(); fs = DescriptorFixture(self, owner); _, packed = owner._artifact_payload()
            for kind in ('replacement', 'trailing', 'bytes', 'symlink'):
                first = fs.transfer('first', base64.b64encode(packed[:16384]).decode())
                full = fs.transfer('second', base64.b64encode(packed[16384:]).decode(), first)
                if kind == 'replacement':
                    moved = fs.remote / 'retained-complete'; fs.path.rename(moved)
                    fs.path.write_bytes(packed); fs.path.chmod(0o600)
                elif kind == 'symlink':
                    moved = fs.remote / 'retained-complete'; fs.path.rename(moved); fs.path.symlink_to(moved)
                else: fs.path.write_bytes(packed + b'junk' if kind == 'trailing' else b'!' + packed[1:])
                before = fs.path.read_bytes()
                with self.subTest(kind=kind): self.reject(lambda: fs.transfer('read', previous=full))
                self.assertEqual(fs.path.read_bytes(), before)
                fs.path.unlink()
                if kind in ('replacement', 'symlink'): moved.unlink()

        @unittest.skipUnless(sys.platform == 'linux', 'Real source-payload descriptor fixtures require Linux')
        def test_primary_write_failure_survives_secondary_close_errors_and_all_closes(self):
            owner = self.prepared(); fs = DescriptorFixture(self, owner); _, packed = owner._artifact_payload()
            primary = OSError('primary source write failure'); closed = []; real_close = os.close
            def secondary(fd):
                real_close(fd); closed.append(fd)
                raise OSError('secondary close failure')
            with mock.patch.object(os, 'write', side_effect=primary), mock.patch.object(os, 'close', secondary):
                with self.assertRaises(OSError) as caught:
                    fs.transfer('first', base64.b64encode(packed[:16384]).decode())
            self.assertIs(caught.exception, primary)
            self.assertGreaterEqual(len(closed), 2)
            self.assertFalse(fs.handles)
    return SourceTransferContract


class PortableRemoteContract(unittest.TestCase):
    def setUp(self):
        self.subject = load_checked(REMOTE_SUBJECT, '_d214_remote_portable')
        self.fixture = remote_fixture(); self.values = bundle()

    def test_exact_bundle_admission_real_artifacts_and_no_input_mutation(self):
        helper, policy = self.subject.load_bundle(self.values)
        packet = self.fixture.artifact_packet(); before = copy.deepcopy(packet)
        tls = checked('state/analysis/P7_static_tls_raw/observed/tls-syms.S')
        base = checked('state/analysis/P7_static_link_probe_raw/static_artifacts.py')
        saved = snapshots()
        with mock.patch.object(Path, 'read_bytes', side_effect=AssertionError('Policy reread source')):
            result = policy.validate_artifacts(packet, tls, base,
                exported_flat_package=packet['app.ino.bin-zsk.bin'],
                motors_allowed=0, snapshots=saved)
        self.assertEqual(result, self.fixture.expected_layout(packet))
        self.assertEqual(packet, before)
        self.assertEqual(self.values, bundle())
        self.assertTrue(callable(helper.directory))

    def test_closed_bundle_names_types_and_every_changed_source_refuse_before_execution(self):
        class DictSubclass(dict): pass
        class StringSubclass(str): pass
        class BytesSubclass(bytes): pass
        first = next(iter(self.values))
        subclass_key = dict(self.values); value = subclass_key.pop(first)
        subclass_key[StringSubclass(first)] = value
        invalid = [None, [], {}, dict(self.values, extra=b'x'), DictSubclass(self.values), subclass_key]
        for key in self.values:
            missing = dict(self.values); del missing[key]; invalid.append(missing)
            for value in (b'', self.values[key] + b'\n', bytearray(self.values[key]),
                          BytesSubclass(self.values[key]), None):
                invalid.append(dict(self.values, **{key: value}))
        for values in invalid:
            with self.subTest(keys=list(values) if isinstance(values, dict) else repr(values)), \
                    mock.patch.object(builtins, 'exec', side_effect=AssertionError('Bad bundle executed')):
                with self.assertRaises((ValueError, TypeError)):
                    self.subject.load_bundle(values)

    def test_real_artifact_policy_refuses_corrupt_ELF_even_with_coherent_export(self):
        _, policy = self.subject.load_bundle(self.values)
        packet = self.fixture.artifact_packet(); raw = packet['app.ino.elf']
        packet['app.ino.elf'] = b'BAD!' + raw[4:]
        tls = checked('state/analysis/P7_static_tls_raw/observed/tls-syms.S')
        base = checked('state/analysis/P7_static_link_probe_raw/static_artifacts.py')
        with self.assertRaises((ValueError, TypeError, RuntimeError)):
            policy.validate_artifacts(packet, tls, base,
                exported_flat_package=packet['app.ino.bin-zsk.bin'],
                motors_allowed=0, snapshots=snapshots())

    def test_remote_first_observation_binds_M0_snapshots_and_inspect_disallows_overrides(self):
        helper, policy = self.subject.load_bundle(self.values)
        packet = self.fixture.artifact_packet()
        tls = checked('state/analysis/P7_static_tls_raw/observed/tls-syms.S')
        payloads = {'build/' + name: body for name, body in packet.items()}
        payloads['artifacts/app.ino.bin-zsk.bin'] = packet['app.ino.bin-zsk.bin']
        result = dict(build_path=BUILD, artifacts_path=ARTIFACTS, files={})
        def installed(unused_helper, unused_fd, path, limit, digest):
            self.assertIn(path, (self.fixture.LOADER, self.fixture.TLS))
            return (tls if path == self.fixture.TLS else b'loader'), {'sha256': digest}
        with mock.patch.object(self.subject, 'artifact_files', return_value=payloads), \
                mock.patch.object(self.subject, 'installed', side_effect=installed), \
                mock.patch.object(policy, 'validate_artifacts', wraps=policy.validate_artifacts) as called:
            self.subject.first_observation(helper, policy, -1, self.values, result)
        self.assertEqual(called.call_count, 1)
        args, kwargs = called.call_args
        self.assertEqual(args, (packet, tls, self.values['base']))
        self.assertEqual(kwargs, dict(exported_flat_package=packet['app.ino.bin-zsk.bin'],
                                      motors_allowed=0, snapshots=snapshots()))
        self.assertIs(type(kwargs['motors_allowed']), int)
        self.assertEqual(result['layout'], self.fixture.expected_layout(packet))
        for mode in (1, True, False, 0):
            with self.subTest(mode=repr(mode)), self.assertRaises((TypeError, ValueError)):
                self.subject.inspect_artifacts(BUILD, ARTIFACTS, self.values, motors_allowed=mode)

    def test_wrong_paths_fail_before_descriptor_access(self):
        for value in ('/tmp/arbitrary', BUILD + '/', BUILD + '/..', '', None, 7,
                      '/home/arduino/sumox26_codex_build/ordinary-app-static01/build'):
            for name in ('build_path', 'artifacts_path'):
                kwargs = dict(build_path=BUILD, artifacts_path=ARTIFACTS, bundle=self.values)
                kwargs[name] = value
                with self.subTest(name=name, value=value), mock.patch.object(
                        self.subject.os, 'open', side_effect=AssertionError('Invalid path opened')):
                    with self.assertRaises((ValueError, TypeError)):
                        self.subject.inspect_artifacts(**kwargs)


def load_tests(loader, standard, pattern):
    if not sys.dont_write_bytecode:
        raise AssertionError('D214 oracle requires Python -B')
    info = seal()
    for name in info['inputs']:
        checked(name)
    base, remote = caller_fixture(), remote_fixture()
    groups = [standard]
    for name in ('LocalAdmissionContract', 'ArtifactReplyContract', 'PreflightContract', 'ExecutionContract'):
        groups.append(loader.loadTestsFromTestCase(getattr(base, name)))
    ordinary = ordinary_fixture(base)
    groups.append(unittest.TestSuite(ordinary(name) for name in info['selection']['ordinary']))
    groups.append(loader.loadTestsFromTestCase(remote.RemoteArtifactContract))
    groups.append(loader.loadTestsFromTestCase(caller_additions(base)))
    groups.append(loader.loadTestsFromTestCase(transfer_cases(base)))
    suite = unittest.TestSuite(groups)
    if suite.countTestCases() != info['counts']['methods']:
        raise AssertionError('D214 exact method inventory changed')
    return suite


if __name__ == '__main__':
    unittest.main(verbosity=2)
