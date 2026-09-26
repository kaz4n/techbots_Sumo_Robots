# Verifies the concrete passive caller using exact accepted ABI and synthetic reads.
# No fixture invokes a board transport, uploader or MCU operation.
# Runs a small serial composition and refusal suite on Windows and Linux.
import base64
import ast
import copy
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

ROOT = Path(__file__).absolute().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import run_recorder_failure_capture as r

ABI_SHA = 'de0cb0ecb558937a9ad251fd81168fe340bf2440aa9ebd3108a60d7758b89ee9'


def fixture():
    spec, unused = r.verified_abi(ROOT, ABI_SHA)
    legacy = r.old_caller(ROOT)
    source = r.adapter_source(spec, (ROOT / 'tools/recorder_failure_capture.py').read_bytes())
    pin = dict(path=r.capture.bindings()['output'] + '-adapter/remote.py', bytes=len(source), sha256=r.sha(source))
    plan, counts = r.project_actions(legacy.actions, spec, pin)
    samples = [(name, address, bytes(size)) for name, address, size in plan[6:-6]]
    analysis = r.capture.analysis(spec, samples, dict.fromkeys(r.capture.FLASH_KEYS, True))
    reads = [dict(name=name, address=address, bytes=size, sha256=r.sha(bytes(size)), file='{:02d}-{}.bin'.format(i, name))
             for i, (name, address, size) in enumerate(plan)]
    report = dict(schema='recorder-failure-capture-result-v1', run_id=r.capture.RUN_ID, source_sha256=r.abi.SOURCE,
        status='COLLECTED', counts=counts, started_utc='2026-09-26T20:00:00+00:00', finished_utc='2026-09-26T20:00:04+00:00',
        started_monotonic=10.0, finished_monotonic=14.0, wait=dict(requested_seconds=2, before=11.0, after=13.0),
        reads=reads, first_error=None, postcheck_errors=[], analysis=analysis)
    raw = r.canonical(report)
    reply = dict(schema='recorder-failure-action-v1', action='capture', run_id=r.capture.RUN_ID, source_sha256=r.abi.SOURCE,
        report=report, report_origin='returned', remote_result_path=r.capture.bindings()['output']+'/capture_result.json',
        full_result_bytes=len(raw), full_result_sha256=r.sha(raw), first_error=None, postcheck_errors=[])
    files = [('capture_result.json', raw)] + [(reads[i]['file'], bytes(plan[i][2])) for i in range(6, len(plan)-6)]
    packet = dict(status='FILE_ONLY_RESULTS_VERIFIED', identity_before=legacy.actions.EXPECTED_IDENTITY,
        identity_after=legacy.actions.EXPECTED_IDENTITY, closing_file_checks=len(files),
        files=[dict(path=legacy.actions.OUTPUT+'/'+name, bytes=len(body), sha256=r.sha(body),
                    data_base64=base64.b64encode(body).decode()) for name, body in files])
    return spec, legacy, source, plan, counts, reply, packet


class CallerTests(unittest.TestCase):
    def test_actual_abi_recomputes_and_tiny_status_plan(self):
        spec, legacy, source, plan, counts, reply, packet = fixture()
        self.assertEqual(len(spec['ranges']), 6)
        self.assertEqual(sum(row['bytes'] for row in spec['ranges']), 684)
        self.assertEqual(counts, dict(commands=24, reads=24, requested_bytes=638936))
        self.assertLess(len(source), 1048576)
        r.validate_reply(reply, legacy, plan, counts)

    def test_actual_abi_bad_hash_refuses(self):
        with self.assertRaises(ValueError): r.verified_abi(ROOT, '0'*64)

    def test_fixed_command_composition(self):
        spec, legacy, source, plan, counts, reply, packet = fixture()
        actions = legacy.actions
        commands = [actions.build_capture_command({'helper':(ROOT/r.HELPER).read_bytes(),
                    'support':(ROOT/r.SUPPORT).read_bytes()},r.capture.bindings()),
                    actions.build_retrieval_command((ROOT/r.HELPER).read_bytes(),actions.EXPECTED_IDENTITY)]
        self.assertTrue(all(actions._command_units(c) <= 30000 for c in commands))
        self.assertNotIn('537113200', actions._RETRIEVAL_SOURCE)
        self.assertNotIn('b4-recorder-capture-result-v1', actions._RETRIEVAL_SOURCE)
        self.assertIn("range(6,18)", actions._RETRIEVAL_SOURCE)
        self.assertIn("'closing_file_checks':13", actions._RETRIEVAL_SOURCE)
        self.assertNotIn('adapter.collect(dependencies,bindings=bindings)', source.decode())

    def test_envelope_timing_flash_and_count_refusals(self):
        spec, legacy, source, plan, counts, original, packet = fixture()
        changes = [('wait', dict(requested_seconds=2,before=12.0,after=13.0)),
                   ('counts', dict(commands=True, reads=24, requested_bytes=638936)),
                   ('source_sha256', '0'*64)]
        for field, value in changes:
            reply = copy.deepcopy(original); reply['report'][field] = value
            raw=r.canonical(reply['report']);reply['full_result_bytes']=len(raw);reply['full_result_sha256']=r.sha(raw)
            with self.assertRaises(ValueError): r.validate_reply(reply,legacy,plan,counts)
        reply=copy.deepcopy(original);reply['report']['reads'][0]['sha256']='0'*64
        raw=r.canonical(reply['report']);reply['full_result_bytes']=len(raw);reply['full_result_sha256']=r.sha(raw)
        with self.assertRaises(ValueError):r.validate_reply(reply,legacy,plan,counts)

    def test_raw_bundle_recomputation_and_refusals(self):
        spec, legacy, source, plan, counts, reply, packet = fixture()
        written={};owner=SimpleNamespace(write_bytes=lambda n,b:written.update({n:b}),write=lambda n,b:written.update({n:b}),local=lambda:None)
        value=r.export_packet(owner,packet,reply,legacy,spec,plan)
        self.assertEqual(value['bundle_status'],'PASS');self.assertEqual(value['coherence'],'UNPROVEN')
        self.assertEqual(len(value['files']),13)
        for field, value in [('path','/tmp/arbitrary'),('sha256','0'*64),('data_base64','!!!!')]:
            bad=copy.deepcopy(packet);bad['files'][1][field]=value
            with self.assertRaises((ValueError,TypeError)):r.export_packet(owner,bad,reply,legacy,spec,plan)

    def test_adapter_only_literal_data_wrapper(self):
        spec, legacy, source, plan, counts, reply, packet=fixture()
        module=r.module_from(source,Path('/synthetic/remote.py'))
        self.assertEqual(module._FIXED_SPEC_SHA,r.sha(r.capture.canonical(spec)))
        calls=[];module._fixed_collect=lambda *a,**k:calls.append(k)
        module.collect(SimpleNamespace(),bindings=r.capture.bindings())
        self.assertEqual(calls[0]['spec'],spec)

    def test_projected_retrieval_independent_closing_reads(self):
        spec, legacy, source, plan, counts, reply, expected=fixture()
        # Execute the exact projected read body; only its descriptor transport is fake.
        tree=ast.parse(legacy.actions._RETRIEVAL_SOURCE)
        keep=[node for node in tree.body if isinstance(node,(ast.Import,ast.ImportFrom,ast.FunctionDef)) or
              isinstance(node,ast.Assign) and all(isinstance(t,ast.Name) and t.id.isupper() for t in node.targets)]
        namespace={};exec(compile(ast.Module(body=keep,type_ignores=[]),'<projected-retrieval>','exec'),namespace)
        files={row['path']:base64.b64decode(row['data_base64']) for row in expected['files']}
        reads=[];identities=[]
        def read(fd,path,limit):
            self.assertEqual(fd,71);self.assertLessEqual(len(files[path]),limit)
            reads.append(path);return files[path]
        helper=SimpleNamespace(logical_read=read,identity=lambda fd:identities.append(fd) or legacy.actions.EXPECTED_IDENTITY)
        observed=namespace['read_bundle'](helper,71)
        self.assertEqual(observed,expected);self.assertEqual(identities,[71,71])
        ordered=[row['path'] for row in expected['files']]
        self.assertEqual(reads,[ordered[0]]+ordered+ordered)
        calls=[]
        def changed(fd,path,limit):
            calls.append(path)
            return b'changed' if len(calls)==15 else read(fd,path,limit)
        helper.logical_read=changed
        with self.assertRaisesRegex(ValueError,'Closing result pin mismatch'):
            namespace['read_bundle'](helper,71)

    def test_projected_bootstrap_request_and_descriptor_closure(self):
        spec, legacy, source, plan, counts, reply, packet=fixture()
        actions=legacy.actions
        command=actions.build_capture_command({'helper':(ROOT/r.HELPER).read_bytes(),
                    'support':(ROOT/r.SUPPORT).read_bytes()},r.capture.bindings())
        tree=ast.parse(actions._BOOTSTRAP_SOURCE);tree.body=tree.body[:-1]
        namespace={};exec(compile(tree,'<projected-bootstrap>','exec'),namespace)
        with patch.object(sys,'argv',['fixture']+command[-3:]):
            action,sources,bindings,pin=namespace['request']()
        self.assertEqual(action,'capture');self.assertEqual(pin,actions.ADAPTER_PIN)
        parser=(ROOT/'tools/p0_capture.py').read_bytes();reads=[];closed=[];collected=[]
        parser_path=namespace['INSTALLED']+'p0_capture.py'
        files={pin['path']:source,parser_path:parser}
        helper=SimpleNamespace(logical_read=lambda fd,path,limit:reads.append(path) or files[path])
        adapter=r.module_from(source,Path('/synthetic/remote.py'))
        def dependencies(values):
            # Linux-only modules are replaced at the explicit dependency seam on Windows.
            self.assertEqual(set(values),set(adapter.DEPENDENCIES))
            self.assertTrue(all((len(body),r.sha(body))==adapter.DEPENDENCIES[name]
                                for name,body in values.items()))
            return SimpleNamespace()
        adapter.load_dependencies=dependencies
        adapter._fixed_collect=lambda dependencies,**kwargs:collected.append(kwargs) or reply['report']
        namespace['load']=lambda name,body,path:helper if name.endswith('_helper') else adapter
        namespace['os']=SimpleNamespace(O_RDONLY=1,O_DIRECTORY=2,O_NOFOLLOW=4,O_CLOEXEC=8,
                                       open=lambda *a:71,close=lambda fd:closed.append(fd))
        envelope=copy.deepcopy(reply);envelope.update(report=None,report_origin=None)
        namespace['perform'](sources,bindings,pin,envelope)
        self.assertIsNone(envelope['first_error'],envelope)
        self.assertEqual(envelope['report'],reply['report']);self.assertEqual(envelope['postcheck_errors'],[])
        self.assertEqual(reads,[pin['path'],parser_path,pin['path'],parser_path]);self.assertEqual(closed,[71])
        self.assertEqual(collected[0]['spec'],spec)

    def test_failed_capture_refuses_retrieval_and_preserves_closure(self):
        spec,legacy,source,plan,counts,reply,packet=fixture()
        legacy.actions.validate_capture_reply=lambda value:r.validate_reply(value,legacy,plan,counts)
        reply['first_error']={'type':'ValueError','message':'synthetic failed capture'}
        owner=legacy.CaptureRun.__new__(legacy.CaptureRun);owner.run_started=False
        events=[];finished=[]
        for name in ('admit','claim','stage','intent','retrieval_intent','retrieve','export_bundle'):
            setattr(owner,name,lambda *a,_name=name:events.append(_name))
        local_calls=[]
        def local():
            local_calls.append(1)
            if len(local_calls)==2:raise ValueError('synthetic closing local')
        owner.local=local;prerequisite_calls=[]
        def prerequisites():
            prerequisite_calls.append(1)
            if len(prerequisite_calls)==2:raise ValueError('synthetic closing prerequisites')
        owner.prerequisites=prerequisites;owner.action=lambda name:reply;owner.finish=finished.append
        result=owner.run()
        self.assertEqual(result['status'],'FAILED');self.assertEqual(result['capture_attempts'],1)
        self.assertEqual(result['retrieval_attempts'],0);self.assertIsNone(result['export'])
        self.assertEqual(result['first_error']['message'],'Capture envelope differs')
        self.assertEqual([row['check'] for row in result['postcheck_errors']],['local','prerequisites'])
        self.assertEqual(events,['admit','claim','stage','intent']);self.assertEqual(finished,[result])

    def test_full_offline_owner_composition_and_binding_one_use(self):
        legacy=r.old_caller(ROOT)
        names=set(legacy.PINS)|set(r.SELECTED)|set(r.abi.PINS)|{r.OLD,r.ACTION}
        manifest=json.loads((ROOT/r.abi.COMPILE_RAW/'inputs.json').read_bytes())
        names.update(manifest['files'])
        with tempfile.TemporaryDirectory(prefix='sumox-capture-caller-') as folder:
            root=Path(folder)
            for name in names:
                target=root/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes((ROOT/name).read_bytes())
            prepared=r.prepare_bindings(root,ABI_SHA)
            self.assertEqual(prepared['status'],'BINDINGS_PREPARED_OFFLINE')
            with self.assertRaises(ValueError):r.prepare_bindings(root,ABI_SHA)
            gitdir=os.environ.get('GIT_DIR')
            if not gitdir:
                gitdir=subprocess.run(['git','-C',str(ROOT),'rev-parse','--absolute-git-dir'],capture_output=True,check=True).stdout.decode().strip()
            with patch.dict(os.environ,GIT_DIR=gitdir,GIT_WORK_TREE=str(root)):
                owner=r.owner_type(root)('1'*40,root=root)
                owner.local=lambda:None
                owner.admit()
                self.assertEqual(len(owner.allowed),7)
                self.assertEqual(set(owner.commands),{'capture','retrieve'})
                self.assertTrue(all(row.get('command_utf16_units',0)<=30000 for row in owner.command_records.values()))
                cap=owner.all_commands['capabilities'][-1]
                self.assertIn("+SOURCE+'/recorder'",cap)
                self.assertNotIn("+SOURCE+'/app'",cap)
                self.assertEqual(owner.push_arguments[1],str(root/r.STAGED))
                owner.check_state()
                owner.source_hashes=dict(owner.source_hashes,forged='0'*64)
                with self.assertRaises(ValueError):owner.check_state()


if __name__=='__main__':unittest.main()
