# Retains 24 action framing/lifecycle cases and five ordinary expectations.
# Independently checks exact geometry, full Windows argv and stale refusals.
# All subprocess, descriptor and clock operations remain controlled.
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import shlex
import types
import unittest

ROOT = Path(__file__).resolve().parents[2]
SUPPORT = 'tests/tooling/test_ordinary_app_remote.py'
SUPPORT_SHA = '427489e5efed6a28e10cf16f2c23d69544d95735edf57910e641163f26f8557b'
_SUPPORT = _PROVIDER = None


def load_support():
    global _SUPPORT
    if _SUPPORT is None:
        raw = (ROOT/SUPPORT).read_bytes()
        if hashlib.sha256(raw).hexdigest()!=SUPPORT_SHA:
            raise AssertionError('Frozen remote oracle differs')
        module=types.ModuleType('_d212_actions_support'); module.__file__=str(ROOT/SUPPORT)
        exec(compile(raw,module.__file__,'exec'),module.__dict__); _SUPPORT=module
    return _SUPPORT


def private_oracle():
    global _PROVIDER
    if _PROVIDER is None:
        _PROVIDER=load_support().make_provider('actions',{'D212_REMOTE_ORACLE_SHA':SUPPORT_SHA})
    return _PROVIDER


def private_oracles():
    return private_oracle().private_oracles()


class OrdinaryActions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        provider=private_oracle(); provider.WaitValidation.setUpClass()
        cls.case_type=provider.WaitValidation
        cls.subject,cls.fixture,cls.remote=cls.case_type.subject,cls.case_type.fixture,cls.case_type.remote

    def setUp(self):
        case=self.case_type('test_valid_wait_receipt_and_inclusive_boundaries')
        case.setUp(); self.addCleanup(case.doCleanups)

    def test_exact_eleven_recipe_steps_and_fixed_adapter_identity(self):
        support=load_support(); support.assert_recipe(self,'actions',11)
        record=support.specification()['expected_subjects_data_only']['remote.py']
        self.assertEqual((self.subject.ADAPTER_BYTES,self.subject.ADAPTER_SHA),(record['bytes'],record['sha256']))
        self.assertEqual(self.fixture.ADAPTER_PIN['path'],self.subject.ADAPTER)

    def test_plan_framing_and_actual_full_windows_argv_bounds(self):
        support=load_support(); spec=support.specification()
        windows=tuple(tuple(x) for x in spec['windows'])
        self.assertEqual(tuple(self.subject.WINDOWS),windows)
        self.assertEqual(tuple(self.subject._plan()),tuple(self.remote.PLAN))
        self.assertEqual((len(self.remote.PLAN),sum(x[2] for x in self.remote.PLAN)),(28,715858))
        for action in ('upload','capture'):
            command=self.subject.build_command(action,self.fixture.sources(),self.remote.bindings(action),self.fixture.ADAPTER_PIN)
            raw,value=self.fixture.decode_command(command)
            self.assertEqual((value['source_sha256'],value['run_id']),(spec['source'],spec['run']))
            self.assertEqual(value['adapter_pin'],self.fixture.ADAPTER_PIN)
            self.assertLessEqual(len(raw),self.subject.legacy.PAYLOAD_LIMIT)
            self.assertLessEqual(self.subject.legacy._command_units(command)+1,self.subject.legacy.COMMAND_LIMIT)
            argv=[self.fixture.ADB,'-s','2629958581','shell','-T',shlex.join(command)]
            units=len(subprocess.list2cmdline(argv).encode('utf-16-le'))//2+1
            self.assertLessEqual(units,30000)
            print(json.dumps({'D212_actual_windows_argv':action,'utf16_units_including_nul':units},sort_keys=True))

    def test_each_stale_diagnostic_window_and_malformed_receipt_refuses_without_mutation(self):
        old=(('trace',536951180,2128),('report',537119696,1168),('runtime',537117984,600),
             ('transaction',537115448,504),('settle',537121768,28),('gate',536953520,88))
        for i in range(7):
            value=self.fixture.envelope('capture'); name,address,size=old[i%6]
            replacement={'name':'first.'+name,'address':address,'bytes':size}
            self.assertNotEqual(tuple(replacement.values()),tuple(value['report']['reads'][7+i][k] for k in ('name','address','bytes')))
            value['report']['reads'][7+i].update(replacement)
            value['report']['analysis']['snapshots'][i].update(replacement)
            self.fixture.refresh(value); before=copy.deepcopy(value)
            with self.subTest(window=i),self.assertRaises(Exception):self.subject.validate_reply('capture',value)
            self.assertEqual(value,before)
        for change in ({'counts':{'commands':26,'reads':26,'requested_bytes':727128}},
                       {'analysis':None}):
            value=self.fixture.envelope('capture');value['report'].update(change)
            self.fixture.refresh(value);before=copy.deepcopy(value)
            with self.assertRaises(Exception):self.subject.validate_reply('capture',value)
            self.assertEqual(value,before)

    def test_D207_source_consumed_owner_and_unattributed_receipts_are_refused(self):
        for key,stale in (('source_sha256','4bc3a2e6ebb497d43a433aa887ab8388dd3dab075a4f44918ed614db30034cd2'),
                          ('run_id','app-motor-const-4bc3a2e6-run01')):
            value=self.fixture.envelope('capture');self.assertNotEqual(value['report'][key],stale)
            value['report'][key]=stale;self.fixture.refresh(value);before=copy.deepcopy(value)
            with self.subTest(key=key),self.assertRaises(Exception):self.subject.validate_reply('capture',value)
            self.assertEqual(value,before)
        value=self.fixture.envelope('capture');value['report_origin']='durable_unattributed';before=copy.deepcopy(value)
        with self.assertRaises(Exception):self.subject.validate_reply('capture',value)
        self.assertEqual(value,before)

    def test_private_projection_installed_pins_and_scope_roles(self):
        support=load_support();spec=support.specification()
        data=json.loads(support.checked(ROOT/spec['derivation']['path'],spec['derivation']))
        record=data['private_actions_projection'];raw=support.checked(ROOT/record['input']['path'],record['input'])
        for row in record['steps']:
            self.assertEqual(raw.count(row['old'].encode()),row['count'])
            raw=raw.replace(row['old'].encode(),row['new'].encode())
        self.assertEqual(support.identity(raw),record['expected'])
        self.assertEqual((self.subject.legacy.RUN_ID,self.subject.legacy.SOURCE),(spec['run'],spec['source']))
        self.assertEqual(private_oracle().PINS[spec['contract']['path']],spec['contract']['sha256'])
        self.assertEqual(private_oracle().PINS[spec['derivation']['path']],spec['derivation']['sha256'])


def load_tests(loader,tests,pattern):
    provider=private_oracle();remote,actions=provider.private_oracles()
    suite=unittest.TestSuite()
    for cls in (actions.ActionsContract,provider.WaitValidation,OrdinaryActions):
        cls.__module__=__name__;suite.addTests(loader.loadTestsFromTestCase(cls))
    if suite.countTestCases()!=29:raise AssertionError('24 inherited and5 ordinary action cases required')
    return suite


if __name__=='__main__':
    unittest.main(verbosity=2)

