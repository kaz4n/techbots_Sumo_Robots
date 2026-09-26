# Retains 25 caller admission/lifecycle cases and five ordinary expectations.
# Real source mapping and helper hashes are checked against the accepted app.
# Transport, subprocesses and owners remain controlled host fixtures.
import copy
import hashlib
import json
from pathlib import Path
import sys
import types
import unittest
from unittest import mock

ROOT=Path(__file__).resolve().parents[2]
SUPPORT='tests/tooling/test_ordinary_app_actions.py'
SUPPORT_SHA='d7e5fefd3739288fd7f2076ddb8440d4a450a4f9dcbe945c72681989bad91847'
_SUPPORT=_PROVIDER=None


def load_support():
    global _SUPPORT
    if _SUPPORT is None:
        raw=(ROOT/SUPPORT).read_bytes()
        if hashlib.sha256(raw).hexdigest()!=SUPPORT_SHA:raise AssertionError('Frozen actions oracle differs')
        value=types.ModuleType('_d212_caller_support');value.__file__=str(ROOT/SUPPORT)
        exec(compile(raw,value.__file__,'exec'),value.__dict__);_SUPPORT=value
    return _SUPPORT


def private_oracle():
    global _PROVIDER
    if _PROVIDER is None:
        _PROVIDER=load_support().load_support().make_provider('run',{'D212_ACTION_ORACLE_SHA':SUPPORT_SHA})
    return _PROVIDER


class OrdinaryCaller(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        provider=private_oracle();provider.ObserverEvidence.setUpClass()
        cls.case_type=provider.ObserverEvidence
        cls.subject,cls.oracle=cls.case_type.subject,cls.case_type.oracle
        cls.manifest,cls.code=cls.case_type.manifest,cls.case_type.code

    def setUp(self):
        case=self.case_type('test_old_manifest_refused_before_projection_and_any_transport')
        case.setUp();self.addCleanup(case.doCleanups)

    def test_exact_nineteen_steps_and_private_caller_projection(self):
        support=load_support().load_support();support.assert_recipe(self,'run',19)
        spec=support.specification();data=json.loads(support.checked(ROOT/spec['derivation']['path'],spec['derivation']))
        record=data['private_caller_projection'];raw=support.checked(ROOT/record['input']['path'],record['input'])
        for row in record['steps']:
            self.assertEqual(raw.count(row['old'].encode()),row['count'])
            raw=raw.replace(row['old'].encode(),row['new'].encode())
        self.assertEqual(support.identity(raw),record['expected'])

    def test_real_125_file_ordinary_mapping_helper_digest_and_refusal_seams(self):
        support=load_support().load_support();spec=support.specification()
        self.assertEqual(len(self.manifest['files']),125)
        self.assertEqual(self.manifest['schema'],'ordinary-app-static-inputs-v1')
        self.assertEqual(self.subject.diagnostic.PROJECT,'app.ino')
        self.assertEqual(self.subject.PINS['tools/compile_ordinary_app_static.py'],
                         '40b5c765c01bc1749f6ea4534a4b7f274b681b5fa9295ab6f0c57fbf94d66a89')
        owner=types.SimpleNamespace(root=ROOT,base=self.subject.current)
        mapper=self.subject.diagnostic.CompileDiagnostic.source_mapping
        names=self.subject.diagnostic.CompileDiagnostic.source_names(owner)
        self.assertEqual(names,{n for n in self.code if n.startswith('src/')})
        mapped,digest=mapper(owner,self.code,names)
        self.assertEqual(digest,spec['source'])
        self.assertEqual(mapped,{n:v['sha256'] for n,v in self.oracle.source_projection(self.manifest).items()})
        helper=self.subject.current.module_from(ROOT,'tools/match_deploy.py',self.code['tools/match_deploy.py'])
        self.assertEqual(helper.app_source_hash(ROOT),digest)
        self.assertIn('app.ino',mapped)
        self.assertNotIn('app_motor_observe.ino',mapped)
        cases=[({'bench/fake.h':b'x'},set(names)|{'bench/fake.h'}),
               ({'src/app/src/core/fake.h':b'x'},set(names)|{'src/app/src/core/fake.h'}),
               ({'src/app/sketch.yaml':b'x'},set(names)|{'src/app/sketch.yaml'}),
               ({'src/app/APP.ino':b'x'},set(names)|{'src/app/APP.ino'}),
               ({'src/app/app.ino':b'x'*4194305},set(names)),
               ({},set(names)-{'src/app/app.ino'})]
        many={'src/hal/d212_extra_'+str(i)+'.h':b'x' for i in range(513)}
        cases.append((many,set(names)|set(many)))
        for changes,chosen in cases:
            value=dict(self.code);value.update(changes);before=copy.deepcopy(value)
            with self.subTest(changes=list(changes)[:2]),self.assertRaises(Exception):mapper(owner,value,chosen)
            self.assertEqual(value,before)
        extra=dict(self.code);extra['src/unselected/data.txt']=b'opaque'
        self.assertEqual(mapper(owner,extra,set(names)|{'src/unselected/data.txt'}),(mapped,digest))

    def test_stale_129_file_D207_manifest_is_rejected_before_mapping(self):
        provider=private_oracle()
        for path,expected in (
            ('state/analysis/P7_motor_const_compile_raw/inputs_static.json','1b847d96bb21fa72ed19138cb93f803b56b74224dffd7019dd930d99ff7bac95'),
            ('state/analysis/P7_motor_settle_compile_raw/inputs_static.json','aa314548521968fd3b1b7b1ef415da3c72c90a6bc914d0a9204ff707bcd7d282')):
            raw=(ROOT/path).read_bytes();self.assertEqual(hashlib.sha256(raw).hexdigest(),expected)
            self.assertEqual(len(json.loads(raw)['files']),129)
            owner=self.subject.InertRun(self.oracle.HEAD,root=ROOT)
            owner.fixed_bytes={provider.MANIFEST:raw};owner.expected_identity={'boot_id':self.manifest['boot_id']}
            before=copy.deepcopy(owner.fixed_bytes)
            with mock.patch.object(self.subject.diagnostic.CompileDiagnostic,'source_mapping') as mapping:
                with self.assertRaises(Exception):owner.load_source()
                mapping.assert_not_called()
            self.assertEqual(owner.fixed_bytes,before)

    @unittest.skipUnless(sys.platform.startswith('linux'),'Owned /dev/shm admission fixture required')
    def test_D207_artifacts_ABI_entry_source_and_consumed_owner_fail_real_admission(self):
        cls=self.oracle.CallerContract;cls.setUpClass()
        paths=('native_static01/artifacts.json','native_abi_static01/abi.json','native_entry_static01/entry.json')
        for relative in (*paths,'scope-source','scope-owner'):
            case=cls('test_preparation_manifest_and_source_drift_are_rejected');case.setUp()
            try:
                if relative in paths:
                    current=private_oracle().COMPILED+relative
                    raw=(ROOT/'state/analysis/P7_motor_const_compile_raw'/relative).read_bytes()
                    self.assertNotEqual(hashlib.sha256(raw).hexdigest(),case.preparation['files'][current]['sha256'])
                    case.drift[current]=raw
                else:
                    key,value=('source_sha256','4bc3a2e6ebb497d43a433aa887ab8388dd3dab075a4f44918ed614db30034cd2') if relative=='scope-source' else ('run_id','app-motor-const-4bc3a2e6-run01')
                    case.scope[key]=value;case.save_scope()
                with self.subTest(relative=relative):
                    case.rejected();case.transport.assert_not_called();case.process.assert_not_called()
            finally:case.doCleanups()

    def test_exact_scope_provenance_bindings_absences_and_current_owner(self):
        support=load_support().load_support();spec=support.specification()
        preparation=json.loads(support.checked(ROOT/spec['preparation']['path'],spec['preparation']))
        self.assertEqual(set(preparation),{'schema','run_id','source_sha256','bindings','files'})
        self.assertEqual(preparation['schema'],'ordinary-app-run-preparation-v1')
        self.assertEqual((preparation['run_id'],preparation['source_sha256']),(spec['run'],spec['source']))
        self.assertEqual(preparation['bindings'],spec['bindings'])
        self.assertEqual(len(preparation['files']),12)
        self.assertEqual(set(preparation['files']),set(self.subject.PROVENANCE))
        self.assertEqual(len(self.subject.SCOPE_FILES),11)
        self.assertEqual(set(self.subject.SCOPE_FILES),set(self.oracle.SCOPE_FILES))
        self.assertEqual(len(self.subject.PROVENANCE),12)
        self.assertEqual(set(self.subject.PROVENANCE),set(self.oracle.PROVENANCE))
        self.assertEqual((self.subject.RUN_ID,self.subject.SOURCE),(spec['run'],spec['source']))
        self.assertEqual(set(spec['bindings']),{'upload','capture'})
        self.assertEqual(len(spec['bindings']['upload']['absent']),14)
        self.assertIn(spec['contract']['path'],self.subject.SCOPE_FILES)
        self.assertIn(spec['derivation']['path'],self.subject.SCOPE_FILES)
        self.assertEqual(self.subject.OUTPUT,'state/analysis/P7_ordinary_app_run_raw/native_inert_run01')
        self.assertNotEqual(self.subject.OUTPUT,'state/analysis/P7_motor_const_run_raw/native_inert_run01')


def load_tests(loader,tests,pattern):
    provider=private_oracle();inherited=provider.caller_oracle()
    suite=unittest.TestSuite()
    for cls in (inherited.CallerContract,provider.ObserverEvidence,OrdinaryCaller):
        cls.__module__=__name__;suite.addTests(loader.loadTestsFromTestCase(cls))
    if suite.countTestCases()!=30:raise AssertionError('25 inherited and5 ordinary caller cases required')
    return suite


if __name__=='__main__':
    unittest.main(verbosity=2)

