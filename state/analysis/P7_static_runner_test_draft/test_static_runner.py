# Tests the frozen runner protocol through independent exact command responses.
# Retains real fixed local pin/stage checks and never invokes actual transport.
# Execute only after freeze_runner.json is frozen and the coordinator gives GO.
import base64
import builtins
import contextlib
import copy
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import shlex
import subprocess
import sys
import tempfile
import types
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[3]
DRAFT = Path(__file__).resolve().parent
RAW = ROOT / 'state/analysis/P7_static_link_probe_raw'


def load(path, name):
    module = types.ModuleType(name)
    module.__file__ = str(path)
    sys.modules[name] = module
    exec(compile(path.read_bytes(), str(path), 'exec'), module.__dict__)
    return module


class Protocol:
    def __init__(self, case, receipt, mutations=None, omit=()):
        self.case, self.receipt = case, receipt
        self.f = case.f
        self.calls, self.protocol_errors = [], []
        self.mutations = mutations or {}
        self.rows = [row for row in self.build_rows() if row[0] not in omit]

    def helper(self, action, arguments, data):
        argv = ['python3', '-I', '-B', '-c', self.case.boot, self.case.hz,
                action, self.f.RUN, *arguments]
        phase = 'remote_postcheck' if action == 'postcheck' else action
        return phase, argv, self.f.TIMEOUTS[action], json.dumps(self.f.envelope(action, data)) + '\n'

    def build_rows(self):
        f = self.f
        c, files = f.claim(), self.case.files
        handle = f.canonical(c)
        u, b, a = f.paths()
        inv = self.helper('inventory', [], dict(identity=f.identity(), resources=f.resources(), compiler_candidates=[]))
        source = self.helper('source', [self.case.m], self.case.source_report)
        override = ('overrides', f.override_argv(), 60, '')
        pins = ('installed_pins', ['sha256sum', '--', *self.case.pins], 60,
                ''.join(value+'  '+name+'\n' for name,value in self.case.pins.items()))
        claim = self.helper('claim', [], dict(claim=c, created=[u, b, a]))
        absent = self.helper('absent', [handle], dict(claim=c, outputs={key:'absent' for key in files}))
        query = ('query', f.compiler_argv(query=True), 300, json.dumps(f.compiler_result()))
        compile_ = ('compile', f.compiler_argv(), 1800, json.dumps(f.compiler_result()))
        post = self.helper('postcheck', [handle, self.case.m], dict(
            claim=c, identity=f.identity(), resources=f.resources(), compiler_candidates=[],
            source=self.case.source_report, files=files))
        artifacts = self.helper('artifacts', [handle], dict(claim=c, files=files))
        layout = self.helper('layout', [handle, self.case.v], dict(
            claim=c, validator_sha256=f.VALIDATOR_SHA, files=files, report=self.case.report))
        elf = self.case.packet['app.ino.elf']
        read = self.helper('read', [handle, 'app.ino.elf', '0', str(len(elf)), f.digest(elf)], dict(
            claim=c, name='app.ino.elf', file=files['build/app.ino.elf'], offset=0, length=len(elf),
            chunk_sha256=f.digest(elf), base64=base64.b64encode(elf).decode()))
        return [inv, ('cli_version', ['arduino-cli','version'],60,'arduino-cli  Version: 1.5.1 Commit: 01f3d4f2b Date: synthetic\n'),
                ('cli_core', ['arduino-cli','core','list'],60,'ID Installed Latest Name\narduino:zephyr 1.0.0 1.0.0 Zephyr\n'),
                ('cli_data', ['arduino-cli','config','get','directories.data','--json'],60,json.dumps(f.D)),
                ('cli_user', ['arduino-cli','config','get','directories.user','--json'],60,json.dumps(f.USER)),
                source,override,pins,claim,absent,query,source,override,pins,inv,absent,compile_,
                post,pins,override,artifacts,layout,read,post,pins,override]

    def __call__(self, board, argv, *, capture, timeout):
        number = len(self.calls) + 1
        try:
            self.case.assertLessEqual(number, len(self.rows), 'Unexpected extra transport')
            phase, expected, limit, output = self.rows[number-1]
            self.case.assertEqual((board, argv, capture, timeout), (self.f.BOARD, expected, True, limit))
            planned = json.loads((self.receipt / f'{number:04}.json').read_text())
            self.case.assertEqual(set(planned), {'sequence','phase','board','argv','timeout','start_utc'})
            self.case.assertEqual((planned['sequence'],planned['board'],planned['argv'],planned['timeout']),
                                  (number,board,argv,timeout))
            self.case.assertIsInstance(planned['phase'], str)
            self.case.assertIsInstance(planned['start_utc'], str)
            command_line = subprocess.list2cmdline([self.f.ADB,'-s',board,'shell','-T',shlex.join(argv)])
            self.case.assertLessEqual(len(command_line.encode('utf-16-le'))//2+1,30000)
        except AssertionError as error:
            self.protocol_errors.append(str(error))
            raise
        self.calls.append((phase, list(argv)))
        response = subprocess.CompletedProcess(argv, 0, output, '')
        effect = self.mutations.get(number, self.mutations.get(phase))
        if isinstance(effect, BaseException):
            raise effect
        return effect(response) if effect else response


def mutate_json(change):
    def alter(response):
        data = json.loads(response.stdout)
        change(data)
        return subprocess.CompletedProcess(response.args,response.returncode,json.dumps(data),response.stderr)
    return alter


class StaticRunnerContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        freeze = json.loads((DRAFT/'freeze_runner.json').read_text())
        if freeze.get('status') != 'FROZEN_FOR_AUTHORIZED_HOST_TEST':
            raise RuntimeError('Runner tests are not frozen')
        for relative, expected in freeze['inputs_sha256'].items():
            if hashlib.sha256((ROOT/relative).read_bytes()).hexdigest() != expected:
                raise RuntimeError('Frozen input changed: '+relative)
        cls.f = load(DRAFT/'public_fixtures.py','independent_runner_public_fixtures')
        cls.module = load(RAW/'run_static_probe.py','independent_static_runner_under_test')
        cls.packet, cls.report = cls.f.artifact_packet()
        cls.files = cls.f.file_records(cls.packet)
        manifest, _, cls.source_report = cls.f.source_packet()
        cls.m = cls.f.packed(manifest)
        validator = (RAW/'static_artifacts.py').read_bytes()
        if cls.f.digest(validator) != cls.f.VALIDATOR_SHA:
            raise RuntimeError('Pinned validator changed')
        cls.v = cls.f.packed(validator)
        helper = (RAW/'static_remote.py').read_bytes()
        helper_sha = cls.f.digest(helper)
        cls.hz = cls.f.packed(helper)
        cls.boot = (RAW/'static_bootstrap.txt').read_text().replace('@HELPER_SHA256@',helper_sha)
        cls.pins = cls.f.installed_pins()

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='sumox_runner_')
        self.addCleanup(self.temporary.cleanup)
        self.parent = Path(self.temporary.name).resolve()
        self.receipt = self.parent/'new-run'

    def run_probe(self, protocol, **options):
        arguments = dict(compile_only=True,run_id=self.f.RUN,receipt_dir=self.receipt,command=protocol)
        arguments.update(options)
        with mock.patch.object(subprocess,'Popen',side_effect=AssertionError('Real process forbidden')):
            try:
                return self.module.run_probe(**arguments)
            finally:
                self.assertEqual(protocol.protocol_errors,[])

    def result(self):
        return json.loads((self.receipt/'result.json').read_text())

    def test_success_exact_protocol_receipts_and_checked_final_only(self):
        protocol = Protocol(self,self.receipt)
        result = self.run_probe(protocol)
        self.assertEqual(len(protocol.calls),26)
        self.assertEqual(result,self.result())
        self.assertEqual(set(result),{'status','source_sha256','run_id','receipt_dir','remote_root',
                                     'build_path','artifact_path','query_attempts','compile_attempts',
                                     'layout','artifacts','final_elf'})
        self.assertEqual(result['status'],'STATIC_COMPILE_COLLECTED')
        self.assertEqual(result['source_sha256'],self.f.SOURCE)
        self.assertEqual((result['query_attempts'],result['compile_attempts']),(1,1))
        self.assertEqual(result['layout'],self.report)
        self.assertEqual(result['artifacts'],self.report['artifacts'])
        self.assertEqual((result['remote_root'],result['build_path'],result['artifact_path']),self.f.paths())
        self.assertEqual((self.receipt/'app.ino.elf').read_bytes(),self.packet['app.ino.elf'])
        self.assertEqual(result['final_elf'],dict(path=str(self.receipt/'app.ino.elf'),**self.report['artifacts']['app.ino.elf']))
        self.assertEqual({path.name for path in self.receipt.iterdir()},
                         {'result.json','app.ino.elf',*[f'{i:04}.json' for i in range(1,27)]})
        for index in range(1,27):
            record = json.loads((self.receipt/f'{index:04}.json').read_text())
            self.assertEqual(set(record),{'sequence','phase','board','argv','timeout','start_utc',
                                          'end_utc','returncode','stdout','stderr','error'})
            self.assertEqual((record['returncode'],record['error']),(0,None))

    def test_request_admission_rejects_before_claim_or_transport(self):
        cases = [('compile_only',v) for v in (False,1,'true',None)]
        cases += [('run_id',v) for v in ('','a'*31,'A'*32,'../'+'a'*29,None,12)]
        cases += [('receipt_dir',v) for v in ('/tmp/string',Path('relative'),None,12)]
        cases += [('command',v) for v in (None,1,'remote')]
        for key,value in cases:
            protocol = Protocol(self,self.receipt)
            with self.subTest(key=key,value=str(value)), self.assertRaises(ValueError):
                self.run_probe(protocol,**{key:value})
            self.assertFalse(self.receipt.exists())
            self.assertEqual(protocol.calls,[])

    def test_cli_only_exact_three_tokens_and_help(self):
        valid = self.module.parse_request(['--compile-only','--run-id',self.f.RUN])
        self.assertIs(valid.compile_only,True)
        self.assertEqual(valid.run_id,self.f.RUN)
        bad = [[],['--compile-only'],['--run-id',self.f.RUN,'--compile-only'],
               ['--compile-only','--run-id','A'*32],['--compile','--run-id',self.f.RUN],
               ['--compile-only','--run-id',self.f.RUN,'--compile-only'],
               ['--compile-only','--run-id='+self.f.RUN],['--help','--compile-only']]
        with contextlib.redirect_stdout(io.StringIO()),contextlib.redirect_stderr(io.StringIO()):
            for argv in bad:
                with self.subTest(argv=argv),self.assertRaises(SystemExit) as failure:
                    self.module.parse_request(argv)
                self.assertEqual(failure.exception.code,2)
            for argv in (['--help'],['-h']):
                with self.assertRaises(SystemExit) as helped:
                    self.module.parse_request(argv)
                self.assertEqual(helped.exception.code,0)

    def test_main_configuration_failure_returns_one_without_transport(self):
        output=io.StringIO()
        values={'SUMO_TRANSPORT':'ssh','SUMO_ADB_SERIAL':self.f.BOARD,
                'SUMO_ADB_EXECUTABLE':self.f.ADB}
        with mock.patch.dict(os.environ,values),contextlib.redirect_stderr(output), \
             mock.patch.object(subprocess,'Popen',side_effect=AssertionError('Transport before configuration')):
            code=self.module.main(['--compile-only','--run-id',self.f.RUN])
        self.assertEqual(code,1)
        self.assertTrue(output.getvalue().strip())

    def test_existing_missing_parent_and_symlink_receipt_paths_rejected(self):
        self.receipt.mkdir()
        for target in (self.receipt,self.parent/'missing'/'run'):
            protocol = Protocol(self,target)
            with self.assertRaises(ValueError):
                self.run_probe(protocol,receipt_dir=target)
            self.assertEqual(protocol.calls,[])
        if os.name=='posix':
            (self.parent/'link').symlink_to(self.receipt,target_is_directory=True)
            protocol=Protocol(self,self.parent/'link'/'new')
            with self.assertRaises(ValueError):
                self.run_probe(protocol,receipt_dir=self.parent/'link'/'new')
            self.assertEqual(protocol.calls,[])

    def test_precompile_failures_never_compile_or_run_terminal_postchecks(self):
        for index in (1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16):
            receipt=self.parent/f'failure-{index}'
            protocol=Protocol(self,receipt,{index:OSError('injected precompile failure')})
            with self.subTest(index=index),self.assertRaises(OSError):
                self.run_probe(protocol,receipt_dir=receipt)
            self.assertEqual(len(protocol.calls),index)
            result=json.loads((receipt/'result.json').read_text())
            self.assertEqual(result['compile_attempts'],0)
            self.assertEqual(result['query_attempts'],int(index>=11))

    def test_core_required_row_unique_exact_version(self):
        for text in ('ID Installed Latest Name\nother:core 1.0.0 1.0.0 Other\n',
                     'arduino:zephyr 1.0.1 1.0.1 Zephyr\n',
                     'arduino:zephyr 1.0.0 1.0.0 Zephyr\narduino:zephyr 1.0.0 1.0.0 Duplicate\n',
                     'arduino:zephyr 1.0.0 1.0.0 Zephyr\narduino:zephyr 2.0.0 2.0.0 Duplicate\n'):
            receipt=self.parent/f'core-{len(list(self.parent.iterdir()))}'
            protocol=Protocol(self,receipt,{'cli_core':lambda r,t=text:subprocess.CompletedProcess(r.args,0,t,'')})
            with self.assertRaises(ValueError):self.run_probe(protocol,receipt_dir=receipt)
            self.assertEqual(len(protocol.calls),3)

    def test_inventory_identity_resources_and_extra_fields(self):
        changes = [lambda x:x['data']['identity'].update(machine='x86_64'),
                   lambda x:x['data']['identity'].update(uid=True),
                   lambda x:x['data']['resources'].update(available_ram_bytes=536870911),
                   lambda x:x['data']['resources'].update(root_available_bytes=1073741823),
                   lambda x:x['data']['resources'].update(tmp_available_bytes=1073741823),
                   lambda x:x.update(extra=1)]
        for index,change in enumerate(changes):
            receipt=self.parent/f'inventory-{index}'
            protocol=Protocol(self,receipt,{1:mutate_json(change)})
            with self.assertRaises(ValueError):self.run_probe(protocol,receipt_dir=receipt)
            self.assertEqual(len(protocol.calls),1)

    def test_source_and_claim_response_binding(self):
        for index,change in ((6,lambda x:x['data'].update(total_bytes=x['data']['total_bytes']+1)),
                             (6,lambda x:x['data'].update(file_count=101)),
                             (9,lambda x:x['data']['claim'].update(run_id='f'*32)),
                             (9,lambda x:x['data']['claim'].update(boot_id='aaaaaaaa-bbbb-4ccc-8ddd-eeeeeeeeeeee')),
                             (10,lambda x:x['data']['outputs'].update({'build/app.ino.elf':'present'}))):
            receipt=self.parent/f'bound-{len(list(self.parent.iterdir()))}'
            protocol=Protocol(self,receipt,{index:mutate_json(change)})
            with self.assertRaises(ValueError):self.run_probe(protocol,receipt_dir=receipt)
            self.assertEqual(len(protocol.calls),index)

    def test_query_properties_drift_and_stale_after_query_stop_before_compile(self):
        changes = [(11,lambda x:x['builder_result']['build_properties'].append('recipe.unreviewed=true')),
                   (16,lambda x:x['data']['outputs'].update({'build/app.ino.bin-zsk.bin':'present'}))]
        for index,change in changes:
            receipt=self.parent/f'precompile-{index}'
            protocol=Protocol(self,receipt,{index:mutate_json(change)})
            with self.assertRaises(ValueError):self.run_probe(protocol,receipt_dir=receipt)
            self.assertEqual(len(protocol.calls),index)
            result=json.loads((receipt/'result.json').read_text())
            self.assertEqual((result['query_attempts'],result['compile_attempts']),(1,0))

    def test_compile_nonzero_transport_exceptions_and_malformed_status_are_unknown(self):
        errors = [subprocess.TimeoutExpired('compile',1800,output=b'partial\xff',stderr=b'err\x00'),
                  OSError('launch uncertain'),subprocess.CalledProcessError(7,'compile',output=b'bad\xff',stderr=b'error'),
                  RuntimeError('callback uncertainty')]
        effects = errors + [lambda r:subprocess.CompletedProcess(r.args,3,'failed','diagnostic'),
                            lambda r:subprocess.CompletedProcess(r.args,True,'',''),lambda r:None,
                            lambda r:subprocess.CompletedProcess(r.args,0,{},''),
                            lambda r:subprocess.CompletedProcess(r.args,float('nan'),'','')]
        for index,effect in enumerate(effects):
            receipt=self.parent/f'unknown-{index}'
            protocol=Protocol(self,receipt,{'compile':effect})
            with self.assertRaises(Exception) as failure:self.run_probe(protocol,receipt_dir=receipt)
            if isinstance(effect,BaseException):self.assertIs(failure.exception,effect)
            if index>=5:self.assertIsInstance(failure.exception,ValueError)
            self.assertEqual(len(protocol.calls),17)
            result=json.loads((receipt/'result.json').read_text())
            self.assertEqual(result['status'],'COMPILE_OUTCOME_UNKNOWN')
            self.assertEqual((result['query_attempts'],result['compile_attempts']),(1,1))
            self.assertFalse((receipt/'app.ino.elf').exists())
            record=json.loads((receipt/'0017.json').read_text())
            if isinstance(effect,(subprocess.TimeoutExpired,subprocess.CalledProcessError)):
                self.assertEqual(record['stdout'],{'encoding':'base64','data':base64.b64encode(effect.output).decode()})
            if isinstance(effect,(subprocess.TimeoutExpired,OSError,RuntimeError)):
                self.assertIsNone(record['returncode'])

    def test_zero_exit_invalid_compile_policy_preserves_failure_and_runs_postchecks(self):
        protocol=Protocol(self,self.receipt,{'compile':mutate_json(lambda x:x.update(success=False))})
        with self.assertRaises(ValueError):self.run_probe(protocol)
        self.assertEqual(len(protocol.calls),20)
        self.assertEqual(self.result()['status'],'FAILED')
        self.assertEqual(self.result()['phase'],'compile')
        self.assertEqual(self.result()['postcheck_errors'],[])

    def test_first_failure_survives_independent_remote_postcheck_failures(self):
        effects={'compile':mutate_json(lambda x:x.update(success=False)),
                 18:OSError('postcheck one'),19:OSError('postcheck two'),20:OSError('postcheck three')}
        protocol=Protocol(self,self.receipt,effects)
        with self.assertRaises(ValueError) as first:self.run_probe(protocol)
        self.assertEqual(len(protocol.calls),20)
        result=self.result()
        self.assertEqual(result['error'],{'class':'ValueError','message':str(first.exception)})
        self.assertEqual([x['check'] for x in result['postcheck_errors']],
                         ['remote_postcheck','installed_pins','overrides'])

    def test_compile_success_first_postcheck_failure_becomes_primary(self):
        original=OSError('postcheck rejected')
        protocol=Protocol(self,self.receipt,{18:original})
        with self.assertRaises(OSError) as failure:self.run_probe(protocol)
        self.assertIs(failure.exception,original)
        self.assertEqual(len(protocol.calls),20)
        self.assertEqual(self.result()['postcheck_errors'][0]['check'],'remote_postcheck')

    def test_collection_identity_and_report_failures_still_run_final_postchecks(self):
        cases=[('artifacts',lambda x:x['data']['files']['build/app.ino.elf']['identity'].update(inode=999),('layout','read'),24),
               ('layout',lambda x:x['data']['report'].update(status='STATIC_ARTIFACT_PROBE_PASS'),('read',),25),
               ('layout',lambda x:x['data']['report']['flash'].update(remaining=1),('read',),25),
               ('layout',lambda x:x['data']['report']['sections'][0].update(alignment=3),('read',),25),
               ('layout',lambda x:x['data']['report']['artifacts']['app.ino.elf'].update(sha256='0'*64),('read',),25),
               ('read',lambda x:x['data'].update(offset=262144),(),26),
               ('read',lambda x:x['data'].update(base64=x['data']['base64']+'\n'),(),26)]
        for index,(phase,change,omit,count) in enumerate(cases):
            receipt=self.parent/f'collect-{index}'
            protocol=Protocol(self,receipt,{phase:mutate_json(change)},omit)
            with self.assertRaises(ValueError):self.run_probe(protocol,receipt_dir=receipt)
            self.assertEqual(len(protocol.calls),count)
            self.assertFalse((receipt/'app.ino.elf').exists())

    def test_final_postcheck_drift_blocks_saved_elf(self):
        protocol=Protocol(self,self.receipt,{24:mutate_json(
            lambda x:x['data']['files']['build/app.ino.elf']['identity'].update(ctime_ns=125))})
        with self.assertRaises(ValueError):self.run_probe(protocol)
        self.assertEqual(len(protocol.calls),26)
        self.assertFalse((self.receipt/'app.ino.elf').exists())

    def test_duplicate_nonfinite_and_wrong_envelope_types_fail_closed(self):
        texts=['{"schema":"x","schema":"static-remote-v1"}', '{"unused":NaN}',
               '{"unused":1e999}', '[]', 'null', '{} garbage']
        for index,text in enumerate(texts):
            receipt=self.parent/f'json-{index}'
            protocol=Protocol(self,receipt,{1:lambda r,t=text:subprocess.CompletedProcess(r.args,0,t,'')})
            with self.assertRaises(ValueError):self.run_probe(protocol,receipt_dir=receipt)
            self.assertEqual(len(protocol.calls),1)

    def test_planned_receipt_write_failure_prevents_dispatch(self):
        protocol=Protocol(self,self.receipt)
        real_open=io.open
        def fail_receipt(file,*args,**kwargs):
            if os.fspath(file)==os.fspath(self.receipt/'0001.json'):
                raise OSError('planned receipt failure')
            return real_open(file,*args,**kwargs)
        with mock.patch.object(io,'open',fail_receipt),self.assertRaises(OSError):
            self.run_probe(protocol)
        self.assertEqual(protocol.calls,[])

    def test_local_pin_read_drift_rejects_without_editing_pinned_file(self):
        target=ROOT/'tools/app_build_commands.json'
        before=target.read_bytes()
        original=Path.read_bytes
        def drift(path):
            data=original(path)
            return data+b'\n' if path==target else data
        protocol=Protocol(self,self.receipt)
        with mock.patch.object(Path,'read_bytes',drift),self.assertRaises(ValueError):
            self.run_probe(protocol)
        self.assertEqual(protocol.calls,[])
        self.assertEqual(target.read_bytes(),before)

    def test_local_postcompile_pin_and_stage_read_failures_are_independent(self):
        protocol=Protocol(self,self.receipt)
        targets={ROOT/'tools/app_build_commands.json',ROOT/'src/config.h'}
        original=Path.read_bytes
        def drift(path):
            data=original(path)
            return data+b'\n' if path in targets and len(protocol.calls)>=17 else data
        with mock.patch.object(Path,'read_bytes',drift),self.assertRaises(Exception):
            self.run_probe(protocol)
        self.assertEqual(len(protocol.calls),20)
        errors=[item['check'] for item in self.result()['postcheck_errors']]
        self.assertIn('local_pins',errors)
        self.assertIn('local_stage',errors)

    def test_current_interpreter_common_policy_cache_blocks_before_or_after_import(self):
        target=os.path.normcase(importlib.util.cache_from_source(str(ROOT/'tools/app_build_policy.py')))
        original=os.path.lexists
        for threshold in (1,2):
            observed=[0]
            def cache_present(path):
                if os.path.normcase(os.fspath(path))==target:
                    observed[0]+=1
                    if observed[0]>=threshold:return True
                return original(path)
            receipt=self.parent/f'cache-{threshold}'
            protocol=Protocol(self,receipt)
            with mock.patch.object(os.path,'lexists',cache_present),self.assertRaises(ValueError):
                self.run_probe(protocol,receipt_dir=receipt)
            self.assertEqual(protocol.calls,[])
            self.assertGreaterEqual(observed[0],threshold)

    def test_late_common_policy_read_drift_never_executes_unverified_bytes(self):
        target=ROOT/'tools/app_build_policy.py'
        original=Path.read_bytes
        count=[0]
        def drift(path):
            if path==target:
                count[0]+=1
                if count[0]>1:return b'raise AssertionError("UNVERIFIED_SOURCE_EXECUTED")\n'
            return original(path)
        protocol=Protocol(self,self.receipt)
        with mock.patch.object(Path,'read_bytes',drift),self.assertRaises(ValueError):
            self.run_probe(protocol)
        self.assertEqual(protocol.calls,[])


if __name__=='__main__':unittest.main(verbosity=2)
