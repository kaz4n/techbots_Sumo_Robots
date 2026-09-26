# Tests one-use recorder run ordering, result acceptance and receiver containment.
# The transport boundary is deterministic; saved full wire is parsed by real validators.
# All cases run offline and preserve first failure without retrying native operations.
import copy
from contextlib import ExitStack
import hashlib
import importlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import types
import unittest
from unittest import mock
import zlib

ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT),str(ROOT/'tools')]
from tests.tooling.test_recorder_delivery import load,request,identity,compiled,ATTEMPT,SESSION,HEAD,SOURCE,BOOT
from tests.tooling.test_dump_match import wire,rechecksum

REFERENCE='state/analysis/P2_recorder_transport_raw/author/run1_commands/normal_exports_1790205416118983952/positive.wire'
REFERENCE_SHA='420b4657c0a13d813ca66e29d6217c406de4d13befd8f7584b625724e9dfdfef'


def full_wire():
    reference=Path(os.environ.get('SUMOX_TEST_REFERENCE_ROOT',ROOT))/REFERENCE
    data=reference.read_bytes()
    if hashlib.sha256(data).hexdigest()!=REFERENCE_SHA:raise AssertionError('Reference wire changed')
    lines=data.splitlines(keepends=True)
    for i,line in enumerate(lines):
        fields=line.rstrip(b'\n').split(b',')
        fields[2 if i==0 else 1]=str(SESSION).encode()
        lines[i]=b','.join(fields)+b'\n'
    return rechecksum(b''.join(lines))


class Owner:
    def __init__(self,root):
        self.root=Path(root);self.attempt=ATTEMPT;self.session=SESSION
        self.source_sha256=SOURCE;self.reviewed_head=HEAD
        self.output=self.root/'state/analysis/P7_recorder_delivery_raw'/('recorder-'+ATTEMPT[:16])
        self.output.mkdir(parents=True)
        self.remote='/home/arduino/sumox26_codex_build/recorder-'+ATTEMPT[:16]
        self.code={'src/config.h':(ROOT/'src/config.h').read_bytes()}
        self.base=types.SimpleNamespace(decode=json.loads)
        self.board=types.SimpleNamespace(target=lambda:'2629958581')
        self.calls=[];self.failure=None;self.late=None
        self.reply=dict(status='UPLOADED',attempts=1,first_error=None,postcheck_errors=[],
            run_id=ATTEMPT,source_sha256=SOURCE,subprocess=dict(returncode=0,timed_out=False,reaped=True))
    def identity(self,schema):return dict(identity(),schema=schema)
    def hit(self,name):
        self.calls.append(name)
        if self.failure==name:raise ValueError('first:'+name)
    def inventory(self):self.hit('inventory')
    def prerequisites(self):self.hit('prerequisites')
    def sources(self):self.hit('sources')
    def observe_artifacts(self,final):
        if final is not True:raise AssertionError('Missing final artifact check')
        self.hit('artifacts')
    def local(self):self.hit('local')
    def preamble(self):return '# controlled preamble\n'
    def direct(self,program,label,timeout):
        if label!='delivery-upload' or timeout!=240:raise AssertionError('Unexpected upload operation')
        self.hit('upload')
        return types.SimpleNamespace(stdout=json.dumps(self.reply),stderr=''),None
    def closing(self,report,first):
        self.calls.append('closing')
        report['final_checks']=[dict(name='local',status='FAIL' if self.late else 'PASS',error=self.late)]
        return first or (ValueError('late:'+self.late) if self.late else None)


class Worker:
    def __init__(self,calls,stuck=False):self.calls=calls;self.alive=True;self.stuck=stuck;self.joins=[]
    def join(self,timeout):
        if timeout is None or timeout<0 or timeout>960:raise AssertionError('Unbounded thread wait')
        self.joins.append(timeout);self.calls.append('join')
        if not self.stuck:self.alive=False
    def is_alive(self):return self.alive


class RunOrderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.subject=load(ROOT/'tools/run_recorder_delivery.py','_d225_run')
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='d225-run-');self.addCleanup(self.temp.cleanup)
        self.owner=Owner(self.temp.name);self.worker=Worker(self.owner.calls)
        self.state={'destination':str(self.owner.output/'run/capture/good'),'error':None}
        self.commands=types.SimpleNamespace(stop=lambda:self.owner.calls.append('stop'),cleanup_errors=[])
        self.accepted=dict(status='FULL_SYNTHETIC_PASS',frames=5001,events=8,session=SESSION,
                           loss='NONE_REPORTED',lifecycle='SEALED',hardware_acceptance=False)
    def invoke(self):
        owner=self.owner;s=self.subject
        def admission(*unused):owner.hit('admit');return b'controlled upload packet'
        def arm(*unused):owner.hit('arm');return self.worker,self.state
        def connection(*unused):
            owner.hit('connected');return dict(state='CONNECTED',claim={'boot_id':BOOT})
        def acceptance(*unused):owner.hit('accept');return self.accepted
        with ExitStack() as stack:
            patches={'restored_owner':lambda *a,**k:(owner,*compiled()),
                'prepare_upload':admission,'receiver_modules':lambda *a:object(),
                'arm_receiver':arm,'await_connection':connection,'accept_capture':acceptance,
                'ReceiverCommands':lambda *a:self.commands}
            for name,value in patches.items():stack.enter_context(mock.patch.object(s,name,value))
            stack.enter_context(mock.patch.object(subprocess,'Popen',side_effect=AssertionError('Run spawned native process')))
            return s.run_delivery(request(),root=self.owner.root)
    def test_happy_path_requires_readonly_admission_before_receiver_and_one_upload(self):
        result=self.invoke()
        self.assertEqual(result['status'],'DELIVERED')
        self.assertEqual(result['upload_attempts'],1)
        self.assertEqual(result['capture_acceptance'],self.accepted)
        self.assertIsNone(result['first_error']);self.assertEqual(result['closing_errors'],[])
        self.assertEqual(self.owner.calls,['inventory','prerequisites','sources','artifacts','admit',
            'arm','connected','local','upload','join','stop','accept','closing'])
        self.assertEqual(len(self.worker.joins),1)
        self.assertGreater(self.worker.joins[0],900)
        self.assertEqual(json.loads((self.owner.output/'run/result.json').read_bytes()),result)
        with self.assertRaises(FileExistsError):self.invoke()
        self.assertEqual(self.owner.calls.count('upload'),1)
    def test_each_early_failure_stops_before_arming_and_preserves_consumed_run(self):
        for name in ('inventory','prerequisites','sources','artifacts','admit','arm'):
            with self.subTest(stage=name),tempfile.TemporaryDirectory(prefix='d225-early-') as temp:
                self.owner=Owner(temp);self.owner.failure=name;self.worker=Worker(self.owner.calls)
                with self.assertRaises(ValueError) as caught:self.invoke()
                report=caught.exception.delivery_outcome
                self.assertEqual(report['first_error']['message'],'first:'+name)
                self.assertEqual(report['upload_attempts'],0)
                self.assertNotIn('upload',self.owner.calls)
                if name!='arm':self.assertNotIn('arm',self.owner.calls)
                self.assertTrue((self.owner.output/'run/attempt.json').exists())
                self.assertTrue((self.owner.output/'run/result.json').exists())
    def test_connection_local_or_upload_failure_waits_once_retains_first_error_and_never_retries(self):
        for name in ('connected','local','upload'):
            with self.subTest(stage=name),tempfile.TemporaryDirectory(prefix='d225-after-arm-') as temp:
                self.owner=Owner(temp);self.owner.failure=name;self.owner.late='independent close failure'
                self.worker=Worker(self.owner.calls)
                self.state['error']=ValueError('later receive failure')
                with self.assertRaises(ValueError) as caught:self.invoke()
                report=caught.exception.delivery_outcome
                self.assertEqual(str(caught.exception),'first:'+name)
                self.assertEqual(report['first_error']['message'],'first:'+name)
                self.assertEqual(report['status'],'FAILED')
                self.assertEqual(len(self.worker.joins),1)
                self.assertEqual(self.owner.calls.count('upload'),int(name=='upload'))
                self.assertEqual(len(report['closing_errors']),1)
    def test_upload_profile_subprocess_or_postcheck_failure_cannot_report_delivered(self):
        bad=[('attempts',True),('attempts',2),('first_error',{}),('postcheck_errors',['late']),
             ('run_id','f'*32),('source_sha256','f'*64),('status','COMPILE_CHECKED'),
             ('subprocess',dict(returncode=1,timed_out=False,reaped=True)),
             ('subprocess',dict(returncode=0,timed_out=False,reaped=False))]
        for key,value in bad:
            with self.subTest(key=key,value=value),tempfile.TemporaryDirectory(prefix='d225-upload-refusal-') as temp:
                self.owner=Owner(temp);self.owner.reply[key]=value;self.worker=Worker(self.owner.calls)
                with self.assertRaises(ValueError) as caught:self.invoke()
                self.assertEqual(caught.exception.delivery_outcome['status'],'FAILED')
                self.assertEqual(self.owner.calls.count('upload'),1)
                self.assertEqual(len(self.worker.joins),1)
    def test_receive_acceptance_and_late_failures_never_become_delivery(self):
        for name in ('receive','accept','late'):
            with self.subTest(name=name),tempfile.TemporaryDirectory(prefix='d225-close-failure-') as temp:
                self.owner=Owner(temp);self.worker=Worker(self.owner.calls)
                self.state={'destination':str(self.owner.output/'run/capture/good'),'error':None}
                if name=='receive':self.state['error']=ValueError('receive failed')
                if name=='accept':self.owner.failure='accept'
                if name=='late':self.owner.late='local changed'
                with self.assertRaises(ValueError) as caught:self.invoke()
                self.assertEqual(caught.exception.delivery_outcome['status'],'FAILED')
                self.assertEqual(self.owner.calls.count('upload'),1)
    def test_stuck_receiver_has_only_bounded_joins_and_indeterminate_failure(self):
        self.worker.stuck=True
        with self.assertRaises(TimeoutError) as caught:self.invoke()
        report=caught.exception.delivery_outcome
        self.assertEqual(report['status'],'FAILED')
        self.assertEqual(len(self.worker.joins),2)
        self.assertEqual(self.worker.joins[-1],25)
        self.assertIn(dict(check='receiver_thread',status='INDETERMINATE'),report['closing_errors'])
        self.assertGreaterEqual(self.owner.calls.count('stop'),1)
        self.assertEqual(self.owner.calls.count('upload'),1)


class RestorationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.subject=load(ROOT/'tools/run_recorder_delivery.py','_d225_restore')
    def fixture(self,root):
        owner=Owner(root)
        outcome,artifacts=compiled()
        owner.inputs_path=owner.output/'inputs.json';owner.inputs_raw=b'closed source snapshot\n'
        owner.inputs_path.write_bytes(owner.inputs_raw)
        owner.expected_stage={'recorder.ino':'a'*64,'src/recorder_run_identity.h':'b'*64}
        owner.base.read=lambda path:path.read_bytes()
        owner.prepare=lambda:owner.calls.append('prepare')
        def artifact_check(text):
            owner.calls.append('artifact_validation')
            if json.loads(text)!=artifacts:raise ValueError('checked artifact packet differs')
        owner.validate_artifact_reply=artifact_check
        (owner.output/'result.json').write_text(json.dumps(outcome))
        (owner.output/'artifacts.json').write_text(json.dumps(artifacts))
        (owner.output/'staged_files.json').write_text(json.dumps(owner.expected_stage))
        return owner
    def test_actual_restore_checks_compile_sources_artifacts_and_counter_before_run(self):
        with tempfile.TemporaryDirectory(prefix='d225-restore-') as temp:
            owner=self.fixture(temp)
            with mock.patch.object(self.subject,'make_owner',return_value=owner), \
                 mock.patch.object(subprocess,'Popen',side_effect=AssertionError('Restore spawned process')):
                result=self.subject.restored_owner(request(),root=owner.root)
            self.assertIs(result[0],owner)
            self.assertEqual(owner.calls,['local','artifact_validation','prepare','local'])
            self.assertEqual(owner.counter,8)
            self.assertTrue(owner.manifest_saved)
            self.assertFalse((owner.output/'run').exists())
    def test_changed_compile_artifact_stage_snapshot_or_late_source_refuses_before_claim(self):
        for damage in ('compile','artifact','stage','snapshot','counter','late'):
            with self.subTest(damage=damage),tempfile.TemporaryDirectory(prefix='d225-restore-bad-') as temp:
                owner=self.fixture(temp)
                if damage=='compile':
                    path=owner.output/'result.json';value=json.loads(path.read_text());value['flags']='-DMATCH=1 -DMOTORS_ALLOWED=0';path.write_text(json.dumps(value))
                if damage=='artifact':
                    path=owner.output/'artifacts.json';value=json.loads(path.read_text());value['unknown_artifact']='unbound';path.write_text(json.dumps(value))
                if damage=='stage':(owner.output/'staged_files.json').write_text('{}')
                if damage=='snapshot':owner.inputs_path.write_bytes(b'changed')
                if damage=='counter':
                    path=owner.output/'result.json';value=json.loads(path.read_text());value['transport_calls']=True;path.write_text(json.dumps(value))
                if damage=='late':
                    def local():
                        owner.calls.append('local')
                        if owner.calls.count('local')==2:raise ValueError('late source change')
                    owner.local=local
                with mock.patch.object(self.subject,'make_owner',return_value=owner),self.assertRaises(ValueError):
                    self.subject.restored_owner(request(),root=owner.root)
                self.assertFalse((owner.output/'run').exists())


class FullCaptureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.subject=load(ROOT/'tools/run_recorder_delivery.py','_d225_capture')
        cls.dump=importlib.import_module('dump_match')
        cls.reference=full_wire()
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='d225-full-capture-');self.addCleanup(self.temp.cleanup)
        self.owner=Owner(self.temp.name)
        (self.owner.output/'run').mkdir()
    def save(self,data=None,**changes):
        arguments=dict(receive_mode='adb',target='2629958581',expected_session=SESSION,
            firmware_revision=HEAD,source_sha256=SOURCE,
            config_sha256=hashlib.sha256(self.owner.code['src/config.h']).hexdigest())
        arguments.update(changes)
        return self.dump.save_capture([self.reference if data is None else data],
                                      self.owner.output/'run/capture',**arguments)
    def test_real_full_synthetic_wire_is_reparsed_and_independently_validated(self):
        destination=self.save()
        result=self.subject.accept_capture(self.owner,destination,self.dump)
        self.assertEqual(result,dict(status='FULL_SYNTHETIC_PASS',frames=5001,events=8,
                                    session=SESSION,loss='NONE_REPORTED',lifecycle='SEALED',hardware_acceptance=False))
        self.assertEqual((destination/'wire.txt').read_bytes(),self.reference)
    def test_valid_but_short_or_lossy_or_wrong_origin_captures_are_refused(self):
        full=self.reference.splitlines(keepends=True)
        lossy=list(full)
        summary_header=full[1].rstrip(b'\n').split(b',')[2:]
        fields=lossy[2].rstrip(b'\n').split(b',')
        for field in (b'missing_results',b'incomplete'):fields[2+summary_header.index(field)]=b'1'
        lossy[2]=b','.join(fields)+b'\n'
        wrong_origin=list(full);header=wrong_origin[0].rstrip(b'\n').split(b',');header[4]=b'2'
        wrong_origin[0]=b','.join(header)+b'\n'
        for data in (wire(session=SESSION),rechecksum(b''.join(lossy)),rechecksum(b''.join(wrong_origin))):
            with self.subTest(bytes=len(data)):
                destination=self.save(data)
                metadata=json.loads((destination/'capture.json').read_bytes())
                self.assertEqual(metadata['transport_integrity'],'PASS')
                with self.assertRaises(ValueError):self.subject.accept_capture(self.owner,destination,self.dump)
    def test_current_source_config_revision_session_and_csv_wire_bindings_cannot_drift(self):
        for key,value in (('firmware_revision','f'*40),('source_sha256','f'*64),('config_sha256','f'*64)):
            with self.subTest(field=key):
                destination=self.save(**{key:value})
                with self.assertRaises(ValueError):self.subject.accept_capture(self.owner,destination,self.dump)
        destination=self.save();metadata=json.loads((destination/'capture.json').read_bytes())
        for key,value in (('expected_session',SESSION-1),('observed_session',SESSION-1),('session',True),('rejected_session',5)):
            changed=dict(metadata,**{key:value});(destination/'capture.json').write_text(json.dumps(changed))
            with self.subTest(field=key),self.assertRaises(ValueError):self.subject.accept_capture(self.owner,destination,self.dump)
        (destination/'capture.json').write_text(json.dumps(metadata))
        frame=next(destination.glob('*_frames.csv'));frame.write_bytes(frame.read_bytes()+b'changed')
        with self.assertRaises(ValueError):self.subject.accept_capture(self.owner,destination,self.dump)
    def test_capture_path_outside_session_owner_is_refused(self):
        destination=self.dump.save_capture([self.reference],Path(self.temp.name)/'outside',expected_session=SESSION)
        with self.assertRaises(ValueError):self.subject.accept_capture(self.owner,destination,self.dump)


if __name__=='__main__':unittest.main()
