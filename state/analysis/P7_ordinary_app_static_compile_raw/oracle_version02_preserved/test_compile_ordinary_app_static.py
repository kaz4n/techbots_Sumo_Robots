# Derives D208 expectations from its contract and hash-pinned historical fixtures.
# Keeps ordinary mapping, guarded admission and artifact evidence independently checked.
# Frozen before subject inspection; controlled host endpoints never contact a board.
import ast
import builtins
from contextlib import ExitStack
import copy
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import types
import unittest
from unittest import mock
try:
    import pwd
except ImportError:
    pwd = None

ROOT = Path(__file__).resolve().parents[2]
RAW = 'state/analysis/P7_ordinary_app_static_compile_raw'
SUBJECT = 'tools/compile_ordinary_app_static.py'
CONTRACT = 'state/analysis/P7_ordinary_app_static_compile_contract.md'
FIXTURE = RAW + '/fixture_derivation02.json'
FIXTURE_PIN = {'bytes': 76087, 'sha256': '1565b1824f1b02cf7506f0c72e43910a61f69f794bec17931d673f0b0cea427e'}
PLAN = None
_CACHE = {}
SIX = ('source_names', 'source_mapping', '__init__', 'admission', 'source_admission', 'stage')


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def checked(path, identity):
    raw = Path(path).read_bytes()
    if {'bytes': len(raw), 'sha256': sha(raw)} != identity:
        raise AssertionError('Frozen oracle input differs: ' + str(path))
    return raw


def plan():
    global PLAN
    if PLAN is None:
        if FIXTURE_PIN is None:
            raise AssertionError('Independent fixture freeze is unfinished')
        PLAN = json.loads(checked(ROOT / FIXTURE, FIXTURE_PIN))
    return PLAN


def original(name):
    return checked(ROOT / name, plan()['inputs'][name])


def private_module(raw, path, name):
    module = types.ModuleType(name)
    module.__file__ = str(path)
    module.__dict__['__builtins__'] = dict(vars(builtins))
    exec(compile(raw, str(path), 'exec'), module.__dict__)
    return module


def subject_raw():
    return checked(ROOT / SUBJECT, plan()['implementation']['launcher'])


def launcher():
    return private_module(subject_raw(), ROOT / SUBJECT, '_d208_independent_subject')


def replacements(raw, rows):
    for row in rows:
        old, new = row['old'].encode(), row['new'].encode()
        if raw.count(old) != row['count']:
            raise AssertionError('Frozen fixture occurrence differs: ' + repr(old[:80]))
        raw = raw.replace(old, new)
    return raw


def field_projection(kind, raw):
    row = plan()['contract_projections'][kind]
    if {'bytes': len(raw), 'sha256': sha(raw)} != row['original']:
        raise AssertionError('Original projection input differs')
    output = replacements(raw, row['steps'])
    if {'bytes': len(output), 'sha256': sha(output)} != row['expected']:
        raise AssertionError('Independent metadata projection differs')
    return output


def method_spans(raw, wanted=SIX):
    lines = raw.splitlines(keepends=True)
    selected = {}
    for node in ast.walk(ast.parse(raw)):
        if isinstance(node, ast.FunctionDef) and node.name in wanted:
            if node.name in selected:
                raise AssertionError('Duplicate source method')
            selected[node.name] = (b''.join(lines[node.lineno-1:node.end_lineno]),
                                   ast.dump(node.args, include_attributes=False))
    if set(selected) != set(wanted):
        raise AssertionError('Changed source method inventory')
    return selected


def check_caller_boundary(actual):
    recipe = plan()['caller_metadata']
    before = replacements(original(recipe['source']), recipe['steps'])
    if {'bytes': len(actual), 'sha256': sha(actual)} != plan()['implementation']['caller']:
        raise AssertionError('Sealed projected caller identity differs')
    old, new = method_spans(before), method_spans(actual)
    restored = actual
    for name in SIX:
        if new[name][1] != old[name][1] or restored.count(new[name][0]) != 1:
            raise AssertionError('Changed method signature or ambiguous span: ' + name)
        restored = restored.replace(new[name][0], old[name][0], 1)
    if restored != before:
        raise AssertionError('Bytes outside the six permitted caller seams changed')
    return actual


def check_launcher_boundary(raw):
    baseline = original('tools/compile_motor_const.py')
    stable = tuple(plan()['unchanged_launcher_functions'])
    before, after = method_spans(baseline, stable), method_spans(raw, stable)
    if before != after:
        raise AssertionError('Historical launcher bootstrap body changed')
    module = private_module(raw, ROOT / SUBJECT, '_d208_boundary_subject')
    if dict(module.ORIGINALS) != {name: (row['bytes'], row['sha256'])
                               for name, row in plan()['original_subjects'].items()}:
        raise AssertionError('Original byte identities changed')
    expected = plan()['implementation']
    if set(module.PROJECTED) != set(module.ORIGINALS):
        raise AssertionError('Projected identity filename set differs')
    for label, path in (('caller', module.CALLER_SOURCE), ('adapter', module.ADAPTER_SOURCE),
                        ('remote', module.REMOTE_SOURCE)):
        if module.PROJECTED[path] != (expected[label]['bytes'], expected[label]['sha256']):
            raise AssertionError('Concrete projected identity missing or changed')
    check_caller_boundary(module.project_caller(original(module.CALLER_SOURCE)))
    return module


def fixture(key):
    spec = plan()['fixtures'][key]
    raw = replacements(original(spec['source']), spec['steps'])
    if {'bytes': len(raw), 'sha256': sha(raw)} != spec['projected']:
        raise AssertionError('Fixture projection identity differs: ' + key)
    if spec.get('select'):
        tree = ast.parse(raw)
        lines = raw.splitlines(keepends=True)
        pieces = []
        for node in tree.body:
            if isinstance(node, (ast.ClassDef, ast.FunctionDef)) and node.name in spec['select']:
                pieces.append(b''.join(lines[node.lineno-1:node.end_lineno]))
        raw = b'import unittest\n' + b'\n'.join(pieces)
        if {'bytes': len(raw), 'sha256': sha(raw)} != spec['selection']:
            raise AssertionError('Fixture selection identity differs')
    module = private_module(raw, ROOT / spec['source'], '_d208_fixture_' + key)
    return module


def remote_fixture():
    result = fixture('remote')
    prior = result.load
    def load(path, name):
        if Path(path) == ROOT / 'tools/app_motor_fault_compile_remote.py':
            owner = launcher()
            raw = owner.project_remote(original('tools/app_motor_fault_compile_remote.py'))
            if raw != field_projection('remote', original('tools/app_motor_fault_compile_remote.py')):
                raise AssertionError('Actual remote differs from contract')
            return private_module(raw, path, name)
        return prior(path, name)
    result.load = load
    result.BUNDLE = dict(result.BUNDLE, adapter=('tools/app_motor_fault_static_policy.py',
                        plan()['implementation']['adapter']['sha256']))
    def bundle():
        values = {}
        owner = launcher()
        for name, (path, digest) in result.BUNDLE.items():
            raw = owner.project_adapter(original(path)) if name == 'adapter' else original(path)
            if sha(raw) != digest:
                raise AssertionError('Checked remote bundle differs: ' + name)
            values[name] = raw
        return values
    result.checked_bundle = bundle
    return result


def adapter_fixture():
    result = fixture('adapter')
    prior = result.load_module
    def load(name, path):
        path = Path(path)
        if path.name == 'app_motor_fault_static_policy.py' and path.parent.name == 'tools':
            source = checked(path, plan()['original_subjects']['tools/app_motor_fault_static_policy.py'])
            actual = launcher().project_adapter(source)
            if actual != field_projection('adapter', source):
                raise AssertionError('Actual adapter differs from contract')
            return private_module(actual, path, name)
        return prior(name, path)
    result.load_module = load
    return result


def caller_fixture():
    result = fixture('caller')
    prior = result.load
    def load(path, name):
        if Path(path) == ROOT / SUBJECT:
            return launcher().load_caller(root=ROOT)
        if Path(path) == ROOT / 'tests/tooling/test_app_motor_fault_compile_remote.py':
            return remote_fixture()
        return prior(path, name)
    result.load = load
    result.FIXED = [*result.FIXED, 'tools/compile_app_motor_fault.py', 'tools/match_deploy.py']
    return result


def projection_fixture():
    result = fixture('projection')
    result.LAUNCHER, result.CONTRACT, result.RAW = SUBJECT, CONTRACT, RAW
    result.PROJECT, result.REMOTE = 'app.ino', '/home/arduino/sumox26_codex_build/ordinary-app-static01'
    result.PROJECTED = {name: (row['bytes'], row['sha256']) for name, row in
                       plan()['implementation'].items() if name in ('caller', 'adapter', 'remote')}
    result.SUBSTITUTIONS = {name: tuple((r['old'].encode(), r['new'].encode(), r['count'])
                          for r in rows) for name, rows in {
                          'caller': plan()['caller_metadata']['steps'],
                          'adapter': plan()['contract_projections']['adapter']['steps'],
                          'remote': plan()['contract_projections']['remote']['steps']}.items()}
    result.subject_raw = subject_raw
    result.check_caller_boundary = check_caller_boundary
    result.expected_projection = field_projection
    result.MATCH_DEPLOY_SHA = plan()['inputs']['tools/match_deploy.py']['sha256']
    return result


def later_fixture(key):
    result = fixture(key)
    result.__dict__.update(ROOT=ROOT, SUBJECT=SUBJECT, CONTRACT=CONTRACT,
        SUBJECT_PIN=(plan()['implementation']['launcher']['bytes'],
                     plan()['implementation']['launcher']['sha256']),
        CONTRACT_PIN=(plan()['inputs'][CONTRACT]['bytes'], plan()['inputs'][CONTRACT]['sha256']),
        CONTRACT_SHA=plan()['inputs'][CONTRACT]['sha256'],
        OLD_LAUNCHER='tools/compile_app_motor_observe.py',
        OLD_LAUNCHER_PIN=(plan()['inputs']['tools/compile_app_motor_observe.py']['bytes'],
                          plan()['inputs']['tools/compile_app_motor_observe.py']['sha256']),
        BASELINE='tools/compile_motor_settle_probe.py',
        BASELINE_PIN=(plan()['inputs']['tools/compile_motor_settle_probe.py']['bytes'],
                      plan()['inputs']['tools/compile_motor_settle_probe.py']['sha256']),
        MOTOR_SOURCE='src/hal/motor_port_unoq.cpp',
        MOTOR_PIN=(plan()['inputs']['src/hal/motor_port_unoq.cpp']['bytes'],
                   plan()['inputs']['src/hal/motor_port_unoq.cpp']['sha256']),
        checked=lambda path,size,digest: checked(path,{'bytes':size,'sha256':digest}),
        sha=sha, private_module=private_module, check_launcher_boundary=check_launcher_boundary,
        check_caller_boundary=check_caller_boundary, field_projection=field_projection,
        json=json, Path=Path, sys=sys, unittest=unittest)
    return result


def checked_selection(suite, expected, label):
    if suite.countTestCases() != expected:
        raise AssertionError('Historical method count differs: ' + label)
    return suite


def load_tests(loader, standard, pattern):
    if not sys.dont_write_bytecode:
        raise AssertionError('D208 oracles require Python -B')
    base, projection = caller_fixture(), projection_fixture()
    groups = [checked_selection(unittest.TestSuite(loader.loadTestsFromTestCase(getattr(base, name))
              for name in ('LocalAdmissionContract','ArtifactReplyContract','PreflightContract','ExecutionContract')),
              40,'D188'),
              checked_selection(loader.loadTestsFromTestCase(projection.ProjectionContract),16,'D193 bootstrap'),
              checked_selection(loader.loadTestsFromTestCase(projection.additional_owner_cases(base)),3,'D193 owner')]
    for key, cls, factory, count in [('d198','DerivativeIdentityTests','new_owner_cases',6),
                                      ('d203','DerivativeContractTests','additional_owner_cases',4)]:
        layer = later_fixture(key)
        group = unittest.TestSuite([loader.loadTestsFromTestCase(getattr(layer, cls)),
                                  loader.loadTestsFromTestCase(getattr(layer, factory)(base))])
        groups.append(checked_selection(group,count,key))
    inherited = checked_selection(unittest.TestSuite(groups),69,'all caller obligations')
    extras = ordinary_cases(base)
    result = unittest.TestSuite([standard, inherited, loader.loadTestsFromTestCase(extras)])
    if result.countTestCases() != plan()['counts']['caller_total']:
        raise AssertionError('Final caller inventory differs')
    return result


def ordinary_cases(base):
    class OrdinaryContract(base.CallerFixture):
        def map(self, owner, additions=None, removals=()):
            names = owner.source_names()
            code = dict(owner.code)
            for name in names:
                code[name] = (self.root / name).read_bytes()
            for name in removals:
                names.remove(name); code.pop(name)
            return owner.source_mapping(code, names)

        def test_current_ordinary_numeric_inventory_mapping_and_real_helper_are_exact(self):
            calls = []
            previous = sys.getprofile()
            def observed(frame, event, value):
                if event == 'return' and frame.f_code.co_name == 'app_source_hash':
                    calls.append((frame.f_globals.get('__file__'), value))
            owner = self.owner()
            try:
                sys.setprofile(observed); owner.local()
            finally:
                sys.setprofile(previous)
            self.assertEqual(len(owner.source_names()), 105)
            self.assertEqual(len(owner.expected_stage), 104)
            self.assertEqual(sum(len(owner.code[name]) for name in owner.source_names()), 764405)
            self.assertEqual(owner.source_sha256,
                '9044ebbb3cd3b2dbb7aa5984dd5ff23bfff697372f1f29d56693af9ea5eaf31a')
            self.assertTrue(calls)
            self.assertTrue(all(Path(path) == self.root / 'tools/match_deploy.py' and
                                value == owner.source_sha256 for path, value in calls))
            self.assertEqual(owner.expected_stage, {k:sha(v) for k,v in self.expected.items()})
            self.assertNotIn('src/motor_fault.h', owner.expected_stage)
            self.assertNotIn('src/motor_fault.cpp', owner.expected_stage)
            self.assertFalse(any(name.startswith('bench/') for name in owner.source_names()))

        def test_config_probe_and_seventeen_grants_are_unchanged_with_two_flags(self):
            owner = self.owner(); owner.local()
            self.assertEqual(owner.flags, '-DMATCH=0 -DMOTORS_ALLOWED=0')
            self.assertEqual(owner.fqbn, 'arduino:zephyr:unoq:link_mode=static')
            self.assertEqual(owner.startup, 'default')
            self.assertEqual(owner.code['src/config.h'], original('src/config.h'))
            self.assertEqual(owner.code['src/app/app.ino'], original('src/app/app.ino'))
            self.assertEqual(owner.code['src/app/configured_setup.h'], original('src/app/configured_setup.h'))
            import re
            text=owner.code['src/config.h'].decode()
            grants=dict(re.findall(r'inline constexpr std::uint32_t (APP_GRANT_[A-Z_]+) = ([01])U;',text))
            self.assertEqual(len(grants),17)
            self.assertEqual(set(grants.values()),{'0'})
            self.assertIn('#define SUMOX_MOTOR_FAULT_PROBE 0',text)

        def test_nested_local_top_level_and_path_order_mapping_agree_with_real_helper(self):
            owner=self.owner();owner.local()
            additions={'src/app/d208.h':b'// h\n','src/app/d208/z.h':b'// nested\n',
                       'src/app/src/local_unit.cpp':b'// local\n',
                       'src/app/readme.txt':b'fixture\n','src/app/ignored/readme.txt':b'unmapped\n'}
            for name,raw in additions.items():
                p=self.root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw)
            mapped,digest=self.map(owner)
            expected=base.expected_stage(self.root)
            self.assertEqual(mapped,{k:sha(v) for k,v in expected.items()})
            self.assertEqual(digest,base.source_hash(expected))
            helper=owner.base.module_from(self.root,'tools/match_deploy.py',original('tools/match_deploy.py'))
            self.assertEqual(helper.app_source_hash(self.root),digest)
            self.assertIn('src/local_unit.cpp',mapped);self.assertIn('readme.txt',mapped)
            self.assertNotIn('ignored/readme.txt',mapped)
            self.assertNotEqual(sorted(mapped),sorted(mapped,key=Path))

        def test_each_empty_or_file_reserved_local_owner_is_refused(self):
            for reserved in ('config.h','core','hal','app'):
                owner=self.owner();owner.local()
                p=self.root/'src/app/src'/reserved
                p.parent.mkdir(parents=True,exist_ok=True);p.mkdir()
                with self.subTest(reserved=reserved,kind='empty'):
                    self.reject(lambda:self.map(owner))
                p.rmdir();p.write_bytes(b'unreviewed')
                with self.subTest(reserved=reserved,kind='file'):
                    self.reject(lambda:self.map(owner))
                p.unlink()

        def test_missing_app_and_each_top_level_override_are_rejected_by_mapper(self):
            owner=self.owner();owner.local()
            self.reject(lambda:self.map(owner,removals=('src/app/app.ino',)))
            for name in ('sketch.yaml','sketch.yml','sketch.json'):
                p=self.root/'src/app'/name;p.write_bytes(b'override')
                with self.subTest(name=name):self.reject(lambda:self.map(owner))
                p.unlink()

        def test_case_folded_destinations_and_reserved_portable_names_are_refused(self):
            owner=self.owner();owner.local()
            names=owner.source_names();code=dict(owner.code)
            names.add('src/core/TYPES.h');code['src/core/TYPES.h']=b'case collision'
            self.reject(lambda:owner.source_mapping(code,names))
            # On Windows a reserved device basename cannot be created; exercise
            # the mapper's portable-name validation directly through checked inputs.
            names=owner.source_names();code=dict(owner.code)
            names.add('src/core/con.h');code['src/core/con.h']=b'bad portable name'
            self.reject(lambda:owner.source_mapping(code,names))

        def test_unmapped_source_stays_in_manifest_and_is_rechecked(self):
            owner=self.owner();owner.local()
            self.assertIn('src/app/.gitkeep',owner.source_names())
            self.assertNotIn('.gitkeep',owner.expected_stage)
            omitted=dict(self.files);omitted.pop('src/app/.gitkeep')
            self.manifest(files=omitted);self.reject(self.owner().check)
            self.manifest();p=self.root/'src/app/.gitkeep';p.write_bytes(b'changed')
            self.reject(owner.local)

        def test_match_helper_pin_cannot_be_repaired_in_manifest(self):
            p=self.root/'tools/match_deploy.py'
            p.write_bytes(p.read_bytes()+b'\n# unreviewed\n')
            self.manifest(files=dict(self.files,**{'tools/match_deploy.py':sha(p.read_bytes())}))
            self.reject(self.owner().check)

        def test_real_helper_disagreement_stops_re_admission(self):
            owner=self.owner();owner.local()
            real=owner.base.module_from;seen=[]
            def load(root,name,raw):
                module=real(root,name,raw)
                if name=='tools/match_deploy.py':
                    original_hash=module.app_source_hash
                    def disagree(root):
                        seen.append(original_hash(root))
                        return '0'*64
                    module.app_source_hash=disagree
                return module
            with mock.patch.object(owner.base,'module_from',side_effect=load):
                self.reject(owner.local)
            self.assertEqual(seen,[self.source])
            self.assertFalse(owner.output.exists())

        def test_each_projected_output_pin_is_enforced_before_private_execution(self):
            module=launcher()
            for kind,path in (('caller',module.CALLER_SOURCE),('adapter',module.ADAPTER_SOURCE),
                              ('remote',module.REMOTE_SOURCE)):
                previous=module.PROJECTED[path]
                for wrong in ((previous[0]+1,previous[1]),(previous[0],'0'*64)):
                    module.PROJECTED[path]=wrong
                    with self.subTest(kind=kind,wrong=wrong):
                        self.reject(lambda:getattr(module,'project_'+kind)(original(path)))
                module.PROJECTED[path]=previous

        def test_const_consumed_owners_and_stale_source_manifest_artifacts_stay_rejected(self):
            paths=('state/analysis/P7_motor_const_compile_raw/native_static01/retained',
                   'build/stage/app-motor-const-static01/retained')
            for name in paths:
                p=self.root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b'old const')
            before=base.file_set(self.root)
            self.owner().check();self.assertEqual(base.file_set(self.root),before)
            self.manifest(schema='app-motor-const-static-inputs-v1');self.reject(self.owner().check)
            self.manifest(source_sha256='4bc3a2e6ebb497d43a433aa887ab8388dd3dab075a4f44918ed614db30034cd2')
            self.reject(self.owner().check);self.manifest()
            owner=self.owner();owner.local()
            for key,value in [('schema','app-motor-const-static-artifacts-v1'),
                              ('build_path','/home/arduino/sumox26_codex_build/app-motor-const-static01/build'),
                              ('artifacts_path','/home/arduino/sumox26_codex_build/app-motor-const-static01/artifacts')]:
                reply=self.remote_fixture.synthetic_reply();reply[key]=value
                with self.subTest(key=key):self.reject(lambda:owner.validate_artifact_reply(json.dumps(reply)))
    return OrdinaryContract


if __name__ == '__main__':
    unittest.main(verbosity=2)

