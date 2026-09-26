# Exercises exact receive-only command construction and bounded child ownership.
# Controlled process substitutes write actual evidence files but never execute ADB.
# Latch races, multiple cleanup errors and timeout/output failures remain observable.
import hashlib
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
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT),str(ROOT/'tools')]
from tests.tooling.test_recorder_delivery import load,ATTEMPT,SESSION,HEAD,SOURCE,BOOT
from tests.tooling.test_recorder_delivery_run import Owner,Worker


class Child:
    def __init__(self,argv,stdout=None,stderr=None,done=True):
        self.args=argv;self.returncode=0 if done else None;self.kills=0;self.waits=[]
        self.kill_error=self.wait_error=None
        if stdout is not None:stdout.write(b'controlled stdout');stdout.flush()
        if stderr is not None:stderr.write(b'controlled stderr');stderr.flush()
    def poll(self):return self.returncode
    def kill(self):
        self.kills+=1
        if self.kill_error:raise self.kill_error
        self.returncode=-9
    def wait(self,timeout):
        self.waits.append(timeout)
        if timeout!=15:raise AssertionError('Child wait bound changed')
        if self.wait_error:raise self.wait_error
        return self.returncode


class ReceiverOwnershipTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.subject=load(ROOT/'tools/run_recorder_delivery.py','_d225_receiver')
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='d225-receiver-');self.addCleanup(self.temp.cleanup)
        self.owner=Owner(self.temp.name);(self.owner.output/'run').mkdir()
        adb=Path(self.temp.name)/'never-executed-adb';adb.write_bytes(b'controlled identity')
        self.owner.base.ADB=str(adb);self.owner.base.ADB_SHA=hashlib.sha256(adb.read_bytes()).hexdigest()
        for name in ('tools/dump_match.py','tools/validate_csv_bundle.py'):
            self.owner.code[name]=(ROOT/name).read_bytes()
        self.commands=self.subject.ReceiverCommands(self.owner)
        self.dump=self.subject.receiver_modules(self.owner,self.commands)
    def command(self,index=0):return self.commands.allowed[index]
    def test_real_receiver_modules_allow_only_exact_ticket_deadline_and_observer_commands(self):
        receiver,bound=self.command(0);observer,obound=self.command(1)
        self.assertEqual((bound,obound),(915,5))
        self.assertEqual(receiver[:3],['python3','-u','-c'])
        self.assertEqual(receiver[-4:],['900',ATTEMPT,'adb','2629958581'])
        self.assertEqual(observer[-3:],[ATTEMPT,'adb','2629958581'])
        self.assertNotEqual(receiver[3],observer[3])
        for args,timeout in ((receiver,915),(observer,5)):
            argv=[self.owner.base.ADB,'-s','2629958581','shell','-T',self.subject.shlex.join(args)]
            self.assertLessEqual(len(subprocess.list2cmdline(argv).encode('utf-16-le'))//2+1,30000)
        self.assertIs(self.dump.board.remote.__self__,self.commands)
        self.assertIsNot(self.dump.csv,sys.modules.get('validate_csv_bundle'))
    def test_unknown_wrong_target_timeout_or_changed_adb_refuses_before_launch(self):
        args,bound=self.command()
        bad=[('other',args,True,bound),('2629958581',args,False,bound),
             ('2629958581',args,True,916),('2629958581',args,True,True),
             ('2629958581',args+['extra'],True,bound),('2629958581',['sh','-c','id'],True,5)]
        with mock.patch.object(subprocess,'Popen',side_effect=AssertionError('Forbidden spawn')) as spawn:
            for target,argv,capture,timeout in bad:
                with self.subTest(target=target,timeout=timeout),self.assertRaises(ValueError):
                    self.commands.remote(target,argv,capture=capture,timeout=timeout)
            Path(self.owner.base.ADB).write_bytes(b'changed')
            with self.assertRaises(ValueError):self.commands.remote('2629958581',args,capture=True,timeout=bound)
            spawn.assert_not_called()
        self.assertEqual(list((self.owner.output/'run').iterdir()),[])
    def test_real_remote_saves_exact_outputs_and_reaps_once_without_communicate(self):
        args,bound=self.command(1);children=[]
        def start(argv,**kwargs):
            self.assertEqual(kwargs['stdin'],subprocess.DEVNULL)
            self.assertNotEqual(kwargs['stdout'],subprocess.PIPE)
            child=Child(argv,kwargs['stdout'],kwargs['stderr']);children.append(child);return child
        with mock.patch.object(subprocess,'Popen',side_effect=start) as spawn:
            result=self.commands.remote('2629958581',args,capture=True,timeout=bound)
        self.assertEqual((result.stdout,result.stderr),(b'controlled stdout',b'controlled stderr'))
        spawn.assert_called_once();self.assertEqual(children[0].waits,[15]);self.assertFalse(self.commands.children)
        folder=self.owner.output/'run/receive_1'
        self.assertEqual((folder/'stdout').read_bytes(),result.stdout)
        outcome=json.loads((folder/'outcome.json').read_bytes())
        self.assertTrue(outcome['reaped']);self.assertIsNone(outcome['first_error'])
        self.assertEqual(outcome['stdout_bytes'],len(result.stdout))
    def test_timeout_kills_reaps_and_retains_original_bytes(self):
        args,bound=self.command(1);child=Child([],done=False)
        def start(argv,**kwargs):
            child.args=argv;kwargs['stdout'].write(b'prefix');kwargs['stdout'].flush();return child
        with mock.patch.object(subprocess,'Popen',side_effect=start), \
             mock.patch.object(self.subject.time,'monotonic',side_effect=[0,5]), \
             self.assertRaises(subprocess.TimeoutExpired) as caught:
            self.commands.remote('2629958581',args,capture=True,timeout=bound)
        self.assertEqual(child.kills,1);self.assertEqual(child.waits,[15])
        self.assertEqual(caught.exception.output,b'prefix')
        evidence=json.loads((self.owner.output/'run/receive_1/outcome.json').read_bytes())
        self.assertEqual(evidence['first_error']['type'],'TimeoutExpired');self.assertTrue(evidence['reaped'])
    def test_timeout_keeps_first_failure_and_partial_bytes_when_kill_or_reap_also_fails(self):
        for fault in ('kill','wait'):
            with self.subTest(fault=fault):
                child=Child([],done=False)
                setattr(child,fault+'_error',OSError('secondary '+fault+' failure'))
                def start(argv,**kwargs):
                    child.args=argv
                    kwargs['stdout'].write(b'partial stdout');kwargs['stdout'].flush()
                    kwargs['stderr'].write(b'partial stderr');kwargs['stderr'].flush()
                    return child
                args,bound=self.command(1)
                with mock.patch.object(subprocess,'Popen',side_effect=start), \
                     mock.patch.object(self.subject.time,'monotonic',side_effect=[0,5]), \
                     self.assertRaises(subprocess.TimeoutExpired) as caught:
                    self.commands.remote('2629958581',args,capture=True,timeout=bound)
                self.assertEqual(caught.exception.output,b'partial stdout')
                self.assertEqual(caught.exception.stderr,b'partial stderr')
                self.assertEqual(child.kills,1);self.assertEqual(child.waits,[15])
                folder=self.owner.output/'run'/('receive_'+str(self.commands.counter))
                outcome=json.loads((folder/'outcome.json').read_bytes())
                self.assertEqual(outcome['first_error']['type'],'TimeoutExpired')
                self.assertTrue(any(row['operation']==fault and row['message']=='secondary '+fault+' failure'
                                    for row in self.commands.cleanup_errors))

    def test_output_limit_remains_primary_with_partial_bytes_when_reaping_fails(self):
        args,bound=self.command(1)
        child=Child([],done=False);child.wait_error=OSError('secondary reap failure')
        def start(argv,**kwargs):
            child.args=argv
            kwargs['stdout'].write(b'available prefix');kwargs['stdout'].flush()
            kwargs['stderr'].truncate(1048577);kwargs['stderr'].flush()
            return child
        with mock.patch.object(subprocess,'Popen',side_effect=start), \
             self.assertRaises(subprocess.CalledProcessError) as caught:
            self.commands.remote('2629958581',args,capture=True,timeout=bound)
        self.assertIsInstance(caught.exception.__cause__,ValueError)
        self.assertIn('output bound',str(caught.exception.__cause__))
        self.assertEqual(caught.exception.output,b'available prefix')
        self.assertEqual(len(caught.exception.stderr),1048576)
        self.assertEqual(child.kills,1);self.assertEqual(child.waits,[15])
        outcome=json.loads((self.owner.output/'run/receive_1/outcome.json').read_bytes())
        self.assertEqual(outcome['first_error']['type'],'ValueError')

    def test_original_timeout_survives_one_output_read_failure_and_other_stream_is_read(self):
        args,bound=self.command(1);child=Child([],done=False)
        original=Path.open
        def start(argv,**kwargs):
            child.args=argv
            kwargs['stdout'].write(b'available stdout');kwargs['stdout'].flush()
            kwargs['stderr'].write(b'available stderr');kwargs['stderr'].flush()
            return child
        def opened(path,*arguments,**options):
            mode=arguments[0] if arguments else options.get('mode','r')
            if path.name=='stdout' and mode=='rb':raise OSError('secondary stdout read failure')
            return original(path,*arguments,**options)
        with mock.patch.object(subprocess,'Popen',side_effect=start), \
             mock.patch.object(self.subject.time,'monotonic',side_effect=[0,5]), \
             mock.patch.object(Path,'open',opened),self.assertRaises(subprocess.TimeoutExpired) as caught:
            self.commands.remote('2629958581',args,capture=True,timeout=bound)
        self.assertEqual(caught.exception.output,b'')
        self.assertEqual(caught.exception.stderr,b'available stderr')
        folder=self.owner.output/'run/receive_1'
        self.assertEqual((folder/'stdout').read_bytes(),b'available stdout')
        outcome=json.loads((folder/'outcome.json').read_bytes())
        self.assertEqual(outcome['first_error']['type'],'TimeoutExpired')
        self.assertIn('secondary stdout read failure',json.dumps(outcome))

    def test_oversized_stdout_and_stderr_refuse_even_if_child_already_exited(self):
        for role,limit in (('stdout',33554432),('stderr',1048576)):
            with self.subTest(role=role):
                def start(argv,**kwargs):
                    stream=kwargs[role];stream.truncate(limit+1);stream.flush();return Child(argv)
                args,bound=self.command(1)
                with mock.patch.object(subprocess,'Popen',side_effect=start),self.assertRaises(subprocess.CalledProcessError):
                    self.commands.remote('2629958581',args,capture=True,timeout=bound)
                folder=self.owner.output/'run'/('receive_'+str(self.commands.counter))
                self.assertGreater((folder/role).stat().st_size,limit)
                result=json.loads((folder/'outcome.json').read_bytes())
                self.assertIsNotNone(result['first_error']);self.assertTrue(result['reaped'])
    def test_closed_latch_prevents_new_launch_and_race_after_evidence_claim(self):
        args,bound=self.command(1)
        original=self.commands.evidence_owner
        def stop_between_claim_and_launch(*arguments):
            result=original(*arguments);self.commands.stop();return result
        with mock.patch.object(self.commands,'evidence_owner',side_effect=stop_between_claim_and_launch), \
             mock.patch.object(subprocess,'Popen',side_effect=AssertionError('Launch crossed close latch')) as spawn:
            with self.assertRaises(subprocess.CalledProcessError) as raised:
                self.commands.remote('2629958581',args,capture=True,timeout=bound)
            self.assertIsInstance(raised.exception.primary_error,ValueError)
            self.assertIn('closed',str(raised.exception.primary_error).lower())
            with self.assertRaises(ValueError):self.commands.remote('2629958581',args,capture=True,timeout=bound)
            spawn.assert_not_called()
        self.assertTrue(self.commands.closed)
        report=json.loads((self.owner.output/'run/receive_1/outcome.json').read_bytes())
        self.assertFalse(report['reaped']);self.assertEqual(report['first_error']['type'],'ValueError')
    def test_stop_attempts_every_child_after_first_kill_or_wait_failure(self):
        for fault in ('kill','wait'):
            with self.subTest(fault=fault):
                commands=self.subject.ReceiverCommands(self.owner)
                commands.allowed=self.commands.allowed
                commands.children={Child(['first'],done=False),Child(['second'],done=False)}
                first,second=tuple(commands.children)
                failure=OSError('first '+fault+' failure')
                setattr(first,fault+'_error',failure)
                with self.assertRaises(OSError) as caught:commands.stop()
                self.assertIs(caught.exception,failure)
                self.assertTrue(commands.closed)
                self.assertEqual((first.kills,second.kills),(1,1))
                self.assertEqual((first.waits,second.waits),([15],[15]))
                self.assertEqual(caught.exception.receiver_cleanup_errors[0]['operation'],fault)
                self.assertEqual(commands.cleanup_errors,caught.exception.receiver_cleanup_errors)
                with mock.patch.object(subprocess,'Popen',side_effect=AssertionError('Late spawn')):
                    with self.assertRaises(ValueError):commands.remote('2629958581',self.command(1)[0],capture=True,timeout=5)
    def test_arm_receiver_passes_expected_identity_and_bounded_remote_deadline(self):
        calls=[]
        class Thread:
            def __init__(self,target,**kwargs):self.target=target;calls.append(('thread',kwargs))
            def start(self):self.target()
        def capture(target,timeout,**kwargs):calls.append(('capture',target,timeout,kwargs));return 'capture object'
        def save(value,path,**kwargs):calls.append(('save',value,path,kwargs));return path/'complete'
        dump=types.SimpleNamespace(LiveCapture=capture,save_capture=save)
        with mock.patch.dict(os.environ,{'SUMO_TRANSPORT':'adb'}),mock.patch.object(self.subject.threading,'Thread',Thread):
            worker,state=self.subject.arm_receiver(self.owner,self.owner.output/'run',dump)
        self.assertIsNone(state['error']);self.assertEqual(Path(state['destination']).parts[-2:],('capture','complete'))
        self.assertEqual(calls[0],('capture','2629958581',900,{'connection_ticket':ATTEMPT}))
        self.assertTrue(calls[1][1]['daemon'])
        self.assertEqual(calls[2][3]['expected_session'],SESSION)
        self.assertEqual(calls[2][3]['source_sha256'],SOURCE)
        self.assertEqual(calls[2][3]['firmware_revision'],HEAD)
        self.assertEqual(calls[2][3]['config_sha256'],hashlib.sha256(self.owner.code['src/config.h']).hexdigest())
    def test_connection_pending_unknown_then_fresh_boot_connected_precedes_upload(self):
        worker=Worker([]);state={'destination':None,'error':None}
        replies=[{'state':'PENDING'},{'state':'UNKNOWN'},{'state':'CONNECTED','claim':{'boot_id':BOOT}}]
        dump=types.SimpleNamespace(observe_connection=mock.Mock(side_effect=replies))
        with mock.patch.object(self.subject.time,'sleep') as sleep:
            result=self.subject.await_connection(self.owner,dump,worker,state)
        self.assertEqual(result,replies[-1]);self.assertEqual(sleep.call_count,2)
        self.assertEqual(dump.observe_connection.call_count,3)
        dump.observe_connection.assert_called_with('2629958581',ATTEMPT)
        for reply in ({'state':'CONNECTED','claim':{'boot_id':'wrong'}},{'state':'TERMINAL'}):
            dump.observe_connection=mock.Mock(return_value=reply)
            with self.assertRaises(ValueError):self.subject.await_connection(self.owner,dump,worker,state)
    def test_no_upload_after_receiver_ends_or_connection_bound_expires(self):
        worker=Worker([]);worker.alive=False;state={'destination':None,'error':None}
        dump=types.SimpleNamespace(observe_connection=mock.Mock(return_value={'state':'PENDING'}))
        with self.assertRaises(ValueError):self.subject.await_connection(self.owner,dump,worker,state)
        dump.observe_connection.assert_not_called()
        worker.alive=True
        with mock.patch.object(self.subject.time,'sleep'),self.assertRaises(ValueError):
            self.subject.await_connection(self.owner,dump,worker,state)
        self.assertEqual(dump.observe_connection.call_count,20)


if __name__=='__main__':unittest.main()
