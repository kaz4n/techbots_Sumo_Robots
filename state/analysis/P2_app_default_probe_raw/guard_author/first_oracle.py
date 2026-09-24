# Derives D118 exact-app upload expectations from its public run contract.
# Controlled filesystem, Git and board substitutes never operate hardware.
# Coordinator-authored expectations precede the separate guard implementation.
from contextlib import ExitStack, redirect_stderr, redirect_stdout
import copy
import hashlib
import importlib
import io
import json
import os
from pathlib import Path
import shutil
import socket
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
RUN = 'app-default-e820c0e1-run01'
TARGET = '2629958581'
SOURCE = 'e820c0e16c29cfd289889273f02721a995e5336b14397f64d6093cffd42b8b69'
ELF = '8379f152554649fd1b96165f29fda1f165c2b5cfc51d8dca430a37e19f693257'
ZSK = 'c60443cd8d90c26a85591153dfa38d5f9233bd686b413b2ab7daa3e1457f6df5'
HEAD = 'b' * 40
REMOTE = '/home/arduino/sumox26_codex_build'
BUILD = REMOTE + '/_app_builds/native-app-v1/' + SOURCE + '/bench-default/' + 'a' * 32
ARTIFACT = BUILD + '/artifacts'
FOLDER = REMOTE + '/' + SOURCE + '/app'
RAW = 'state/analysis/P2_app_default_probe_raw'
RECORD = 'state/analysis/P2_app_default_probe_run01.json'
APPROVAL = RAW + '/reviewer/run01_approval.json'
REVIEW = 'state/reviews/P2_app_default_run01_review.md'
ATTEMPT = RAW + '/run01_upload_attempt.json'
OUTCOME = RAW + '/run01_upload_outcome.json'
FILES = ('tools/board_tool.py', 'tools/app_build_policy.py', 'tools/app_build_pins.json',
         'tools/app_build_commands.json', 'tools/app_default_run.py',
         'tools/app_default_capture.py', 'tools/p0_capture.py', 'tools/recorder_heap.py',
         'tools/p0_mem_read.cfg', 'tools/p0_inert_sources.json',
         'state/analysis/P2_app_default_probe_contract.md',
         'state/analysis/P2_app_default_run_contract.md')
ENV = dict(SUMO_TRANSPORT='adb', SUMO_ADB_SERIAL=TARGET, SUMO_REMOTE_ROOT=REMOTE)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def request(**changes):
    args = dict(run_id=RUN, sketch='app', match=False, compile_only=False, startup=None)
    args.update(changes)
    return SimpleNamespace(**args)


class Fixture:
    def __enter__(self):
        self.temp = tempfile.TemporaryDirectory(prefix='d118-guard-test-')
        self.root = Path(self.temp.name)
        self.stage = self.root / 'build/stage/app'
        self.source_map = json.loads((ROOT / (RAW + '/preflight/guard_route/source_pin_proposal.json')).read_text())['staged_relative_sha256']
        check = hashlib.sha256()
        for name in sorted(self.source_map):
            local = 'src/app/app.ino' if name == 'app.ino' else name
            data = (ROOT / local).read_bytes()
            if digest(data) != self.source_map[name]:
                raise AssertionError('Public source fixture changed: ' + name)
            check.update(name.encode() + b'\0'); check.update(data)
            self.put(local, data); self.put('build/stage/app/' + name, data)
        if len(self.source_map) != 91 or check.hexdigest() != SOURCE:
            raise AssertionError('Exact public firmware fixture does not match D118')
        for name in FILES:
            data = (ROOT / name).read_bytes() if name == 'tools/p0_inert_sources.json' else ('SYNTHETIC TOOL ' + name).encode()
            self.put(name, data)
        self.put(REVIEW, b'SYNTHETIC independent review fixture only\n')
        self.approval = dict(schema_version=1, run_id=RUN,
            verdict='PASS_EXACT_DEFAULT_APP_SOURCE_TARGET_CAPTURE_GUARD',
            source_sha256=SOURCE, elf_sha256=ELF, binary_sha256=ZSK, software_commit=HEAD,
            review_sha256=digest((self.root / REVIEW).read_bytes()),
            file_sha256={name:digest((self.root / name).read_bytes()) for name in FILES},
            source_file_sha256=copy.deepcopy(self.source_map))
        self.record = dict(schema_version=1, run_id=RUN, target=TARGET, transport='adb',
            source_sha256=SOURCE, elf_sha256=ELF, binary_sha256=ZSK, software_commit=HEAD,
            approval_sha256='', remote_root=REMOTE, setup='human-reported bare UNO Q',
            scope='one unchanged default app upload with inhibited native GPIO/PWM setup; optional grants false; passive readout separately')
        self.save()
        return self

    def put(self, name, data):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)

    def save(self):
        self.put(APPROVAL, (json.dumps(self.approval, indent=2) + '\n').encode())
        self.record['approval_sha256'] = digest((self.root / APPROVAL).read_bytes())
        self.put(RECORD, (json.dumps(self.record, indent=2) + '\n').encode())

    def __exit__(self, *unused):
        self.temp.cleanup()


class Board:
    def __init__(self, fixture):
        self.ROOT, self.fixture = fixture.root, fixture
        self.calls, self.hooks = [], {}
        self.artifact, self.hashes = ARTIFACT, [ELF, ZSK]
        self.result = SimpleNamespace(returncode=0, stdout='fixture uploaded\n', stderr='')
        self.error = None

    def call(self, name, *args):
        self.calls.append((name, args))
        if name in self.hooks:
            self.hooks[name]()

    def transport(self): return os.environ.get('SUMO_TRANSPORT')
    def target(self): return os.environ.get('SUMO_ADB_SERIAL')
    def setting(self, name, pattern): return os.environ.get(name, '')
    def require_transport(self, sync=False): self.call('require_transport', sync)
    def check_source(self, folder): self.call('check_source', folder)
    def stage(self, name):
        self.call('stage', name)
        return self.fixture.stage
    def source_hash(self, folder):
        self.call('source_hash', folder)
        result = hashlib.sha256()
        for path in sorted(p for p in Path(folder).rglob('*') if p.is_file()):
            result.update(path.relative_to(folder).as_posix().encode() + b'\0')
            result.update(path.read_bytes())
        return result.hexdigest()
    def verify_core(self, target): self.call('verify_core', target)
    def sync_sources(self, *args): self.call('sync_sources', *args)
    def compile_app(self, *args):
        self.call('compile_app', *args)
        return self.artifact
    def remote(self, target, argv, capture=False, timeout=None):
        if target != TARGET:
            raise AssertionError('Unexpected board target')
        argv = list(argv)
        name = 'hash' if argv[:1] == ['sha256sum'] else 'upload' if argv[:2] == ['arduino-cli', 'upload'] else 'mkdir'
        self.call(name, target, argv, capture, timeout)
        if name == 'mkdir':
            if argv != ['mkdir', '-p', FOLDER]: raise AssertionError('Unexpected remote operation')
            return SimpleNamespace(returncode=0, stdout='', stderr='')
        if name == 'hash':
            expected = ['sha256sum', '--', BUILD + '/build/app.ino.elf', ARTIFACT + '/app.ino.elf-zsk.bin']
            if argv != expected: raise AssertionError('Unexpected artifact hash command')
            return SimpleNamespace(returncode=0, stdout=''.join(h + '  ' + p + '\n' for h,p in zip(self.hashes, argv[2:])), stderr='')
        if not (self.ROOT / ATTEMPT).is_file(): raise AssertionError('Upload before claim')
        if self.error: raise self.error
        return self.result


class GuardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.guard = importlib.import_module('app_default_run')

    def setUp(self):
        self.stack = ExitStack(); self.addCleanup(self.stack.close)
        self.stack.enter_context(mock.patch.dict(os.environ, ENV, clear=True))
        self.git_calls, self.git_value, self.git_error = [], HEAD, None
        self.stack.enter_context(mock.patch('subprocess.run', side_effect=self.git))
        for name in ('subprocess.Popen', 'socket.create_connection'):
            self.stack.enter_context(mock.patch(name, side_effect=AssertionError('Unexpected external operation')))

    def git(self, argv, **kwargs):
        self.git_calls.append((list(argv), kwargs))
        self.assertEqual(argv[0], 'git'); self.assertEqual(argv[1], '-C')
        self.assertEqual(argv[3:], ['rev-parse', 'HEAD'])
        self.assertEqual(kwargs.get('timeout'), 10)
        self.assertTrue(kwargs.get('capture_output'))
        if self.git_error: raise self.git_error
        return SimpleNamespace(returncode=0, stdout=self.git_value + '\n', stderr='')

    def scope(self, f): return self.guard.load_scope(f.root, TARGET, 'adb')
    def uploads(self, b): return [c for c in b.calls if c[0] == 'upload']

    def test_import_and_exact_request_are_passive(self):
        with mock.patch.object(Path, 'read_bytes', side_effect=AssertionError('import read')):
            importlib.reload(self.guard)
            self.assertIs(self.guard.validate_request(request(), 'default'), True)
        self.assertEqual(self.git_calls, [])

    def test_request_bool_types_and_all_overrides_refuse(self):
        changes = [dict(run_id=v) for v in (None, '', RUN+'\n', 1, True)]
        changes += [dict(sketch=v) for v in ('bench/ui', 'app/', None)]
        changes += [{key:v} for key in ('match','compile_only') for v in (True, 0, None, 'false')]
        changes += [dict(startup='immediate')]
        for change in changes:
            with self.subTest(change=change), self.assertRaises(ValueError):
                self.guard.validate_request(request(**change), 'default')
        args=request(); del args.run_id
        with self.assertRaises(ValueError): self.guard.validate_request(args, 'default')
        with self.assertRaises(ValueError): self.guard.validate_request(request(), 'immediate')

    def test_scope_exact_schema_original_bytes_current_git_and_no_claim(self):
        with Fixture() as f:
            scope=self.scope(f)
            self.assertEqual(set(scope), {'root','run_record','approval','run_record_sha256','approval_sha256','review_sha256','head_commit'})
            self.assertEqual(scope['root'], f.root)
            self.assertEqual(scope['head_commit'], HEAD)
            for key,name in [('run_record_sha256',RECORD),('approval_sha256',APPROVAL),('review_sha256',REVIEW)]:
                self.assertEqual(scope[key], digest((f.root/name).read_bytes()))
            self.assertEqual(scope['run_record'], f.record); self.assertEqual(scope['approval'], f.approval)
            self.assertFalse((f.root/ATTEMPT).exists()); self.assertFalse((f.root/OUTCOME).exists())
            self.assertTrue(self.git_calls)

    def test_environment_and_target_are_explicit(self):
        with Fixture() as f:
            for key in ENV:
                for bad in (None, '', 'wrong'):
                    with self.subTest(key=key,bad=bad), mock.patch.dict(os.environ, {}, clear=False):
                        if bad is None: os.environ.pop(key)
                        else: os.environ[key]=bad
                        with self.assertRaises(ValueError): self.scope(f)
            for target,transport in [('other','adb'),(TARGET,'ssh')]:
                with self.assertRaises(ValueError): self.guard.load_scope(f.root,target,transport)

    def test_run_and_approval_fields_schema_and_types(self):
        for which in ('record','approval'):
            with Fixture() as original:
                names=list(getattr(original,which))
            for key in names:
                for bad in (None, True, 'wrong'):
                    with self.subTest(which=which,key=key,bad=bad), Fixture() as f:
                        getattr(f,which)[key]=bad
                        f.save()
                        if which=='record' and key=='approval_sha256':
                            f.record[key]=bad; f.put(RECORD,json.dumps(f.record).encode())
                        with self.assertRaises(ValueError): self.scope(f)
            for mode in ('missing','extra'):
                with Fixture() as f:
                    obj=getattr(f,which)
                    if mode=='missing': del obj['run_id']
                    else: obj['extra']=1
                    f.save()
                    with self.assertRaises(ValueError): self.scope(f)

    def test_duplicate_nonfinite_oversize_and_unreadable_records(self):
        for name in (RECORD,APPROVAL):
            for data in (b'{"schema_version":1,"schema_version":1}', b'{"bad":NaN}', b'[]', b'X'*65537):
                with Fixture() as f:
                    f.put(name,data)
                    with self.assertRaises(ValueError): self.scope(f)
            with Fixture() as f:
                (f.root/name).unlink()
                with self.assertRaises(OSError): self.scope(f)
        with Fixture() as f:
            f.put(REVIEW,b'R'*65537)
            f.approval['review_sha256']=digest((f.root/REVIEW).read_bytes()); f.save()
            with self.assertRaises(ValueError): self.scope(f)

    def test_file_pin_set_and_each_file_bytes_are_bound(self):
        for name in FILES:
            with self.subTest(name=name), Fixture() as f:
                f.put(name,b'changed')
                with self.assertRaises(ValueError): self.scope(f)
        for change in ('missing','extra','upper'):
            with Fixture() as f:
                pins=f.approval['file_sha256']
                if change=='missing': pins.pop(FILES[0])
                elif change=='extra': pins['extra']='f'*64
                else: pins[FILES[0]]='A'*64
                f.save()
                with self.assertRaises(ValueError): self.scope(f)

    def test_source_map_names_counts_digest_and_local_content(self):
        for change in ('missing','extra','dot','parent','absolute','backslash','content','self_consistent_change'):
            with self.subTest(change=change), Fixture() as f:
                pins=f.approval['source_file_sha256']
                if change=='missing': pins.pop('app.ino')
                elif change=='extra': pins['src/extra.h']='f'*64
                elif change in ('dot','parent','absolute','backslash'):
                    value=pins.pop('app.ino')
                    pins[{'dot':'./app.ino','parent':'src/../app.ino','absolute':'/app.ino','backslash':'src\\app.ino'}[change]]=value
                else:
                    f.put('src/app/app.ino',b'changed')
                    if change=='self_consistent_change': pins['app.ino']=digest(b'changed')
                f.save()
                with self.assertRaises(ValueError): self.scope(f)

    def test_current_head_mismatch_bad_output_and_command_failure(self):
        with Fixture() as f:
            for value in ('a'*40,HEAD+'\n'+HEAD,'B'*40,'b'*39,''):
                with self.subTest(value=value):
                    self.git_value=value
                    with self.assertRaises(ValueError): self.scope(f)
            self.git_value=HEAD
            for error in (OSError('no git'),subprocess.TimeoutExpired('git',10),subprocess.CalledProcessError(7,'git',output='bad',stderr='oops')):
                self.git_error=error
                with self.assertRaises(type(error)): self.scope(f)

    def test_existing_attempt_outcome_and_symlink_ancestry_refuse(self):
        for name in (ATTEMPT,OUTCOME):
            for kind in ('file','dangling'):
                with self.subTest(name=name,kind=kind),Fixture() as f:
                    if kind=='file': f.put(name,b'claimed')
                    else: (f.root/name).symlink_to(f.root/'missing')
                    b=Board(f)
                    with self.assertRaises(ValueError): self.guard.run_once(b,request())
                    self.assertEqual(b.calls,[])
        for name in (RECORD,REVIEW,'tools/p0_capture.py','src/core/types.h'):
            with Fixture() as f:
                path=f.root/name; data=path.read_bytes(); path.unlink()
                dest=f.root/'fixture-link-target'; dest.write_bytes(data); path.symlink_to(dest)
                with self.assertRaises(ValueError): self.scope(f)
        with Fixture() as f:
            src=f.root/'src'; src.rename(f.root/'src-real'); src.symlink_to(f.root/'src-real',target_is_directory=True)
            with self.assertRaises(ValueError): self.scope(f)

    def test_success_exact_build_order_artifact_scope_durable_claim_and_outcome(self):
        with Fixture() as f:
            b=Board(f)
            synced=[]
            real_fsync=os.fsync
            def fsync(fd): synced.append(fd); return real_fsync(fd)
            def launch_check(): self.assertTrue(synced)
            b.hooks['upload']=launch_check
            with mock.patch('os.fsync',side_effect=fsync): result=self.guard.run_once(b,request())
            names=[name for name,args in b.calls]
            for name in ('stage','verify_core','sync_sources','compile_app','upload'): self.assertEqual(names.count(name),1)
            self.assertLess(names.index('stage'),names.index('verify_core'))
            self.assertLess(names.index('verify_core'),names.index('sync_sources'))
            self.assertLess(names.index('sync_sources'),names.index('compile_app'))
            self.assertLess(names.index('compile_app'),names.index('hash'))
            compile_args=next(args for name,args in b.calls if name=='compile_app')
            self.assertEqual(compile_args,(TARGET,SOURCE,FOLDER,REMOTE,'arduino:zephyr:unoq','-DMATCH=0 -DMOTORS_ALLOWED=0','default'))
            self.assertEqual(set(result),{'run_id','source_sha256','artifact_folder','board_folder','attempt_file','outcome_file'})
            self.assertEqual(result['artifact_folder'],ARTIFACT); self.assertEqual(result['board_folder'],FOLDER)
            upload=self.uploads(b)[0][1]
            self.assertEqual(upload,(TARGET,['arduino-cli','upload','--fqbn','arduino:zephyr:unoq','--input-dir',ARTIFACT,FOLDER],True,120))
            claim=json.loads((f.root/ATTEMPT).read_text()); outcome=json.loads((f.root/OUTCOME).read_text())
            for key,value in dict(run_id=RUN,target=TARGET,transport='adb',source_sha256=SOURCE,elf_sha256=ELF,binary_sha256=ZSK,software_commit=HEAD,artifact_folder=ARTIFACT,board_folder=FOLDER).items(): self.assertEqual(claim[key],value)
            self.assertEqual(claim['argv'],upload[1]); self.assertEqual(outcome['returncode'],0)
            self.assertFalse(outcome['timed_out']); self.assertIsNone(outcome['error'])
            receipts=list((f.root/RAW/'preparations').glob('*.json')); self.assertEqual(len(receipts),1)
            receipt=json.loads(receipts[0].read_text()); self.assertTrue(receipt['local_git_checks'])
            self.assertEqual(receipt['artifact_folder'],ARTIFACT)
            self.assertIn('a'*32,str(receipt['checked_receipt']))
            with self.assertRaises(ValueError): self.guard.run_once(b,request())
            self.assertEqual(len(self.uploads(b)),1)

    def test_each_preparation_failure_prevents_upload(self):
        for phase in ('check_source','require_transport','stage','verify_core','mkdir','sync_sources','compile_app','hash'):
            with self.subTest(phase=phase),Fixture() as f:
                b=Board(f)
                def fail(): raise OSError('fixture failure '+phase)
                b.hooks[phase]=fail
                with self.assertRaises(OSError): self.guard.run_once(b,request())
                self.assertEqual(self.uploads(b),[]); self.assertFalse((f.root/ATTEMPT).exists())
                receipts=list((f.root/RAW/'preparations').glob('*.json')); self.assertEqual(len(receipts),1)
                self.assertIn('fixture failure',str(json.loads(receipts[0].read_text())['error']))

    def test_profiles_staged_extras_and_bad_stage_refuse(self):
        for name in ('sketch.yaml','sketch.yml'):
            with Fixture() as f:
                f.put('src/app/'+name,b'profile')
                b=Board(f)
                with self.assertRaises(ValueError): self.guard.run_once(b,request())
                self.assertEqual(b.calls,[])
        for mode in ('extra','content','folder'):
            with Fixture() as f:
                b=Board(f)
                if mode=='extra': f.put('build/stage/app/extra.h',b'new')
                elif mode=='content': f.put('build/stage/app/app.ino',b'new')
                else: f.stage=f.root/'build/stage/other'
                with self.assertRaises(ValueError): self.guard.run_once(b,request())
                self.assertFalse(any(name in ('verify_core','sync_sources','compile_app','upload','hash') for name,args in b.calls))

    def test_changes_during_prepare_or_hash_are_not_uploaded(self):
        for phase in ('stage','sync_sources','compile_app','hash'):
            for mutation in ('head','tool','source','record','environment'):
                with self.subTest(phase=phase,mutation=mutation),Fixture() as f:
                    b=Board(f)
                    def mutate():
                        if mutation=='head': self.git_value='a'*40
                        elif mutation=='tool': f.put('tools/p0_capture.py',b'changed')
                        elif mutation=='source': f.put('src/app/app.ino',b'changed')
                        elif mutation=='record': f.put(RECORD,b'{}')
                        else: os.environ['SUMO_REMOTE_ROOT']='/wrong'
                    b.hooks[phase]=mutate
                    try:
                        with self.assertRaises(ValueError): self.guard.run_once(b,request())
                        self.assertEqual(self.uploads(b),[])
                    finally:
                        self.git_value=HEAD; os.environ.update(ENV)

    def test_artifact_path_and_hash_refuse_before_claim(self):
        paths=[REMOTE+'/'+SOURCE+'/app/artifacts',ARTIFACT+'/extra',ARTIFACT.replace('bench-default','match-default'),ARTIFACT.replace('a'*32,'A'*32),ARTIFACT.replace(SOURCE,'0'*64),'/home/arduino/sumox26-capture-input/app']
        for path in paths:
            with Fixture() as f:
                b=Board(f); b.artifact=path
                with self.assertRaises(ValueError): self.guard.run_once(b,request())
                self.assertEqual(self.uploads(b),[]); self.assertFalse((f.root/ATTEMPT).exists())
        for index in (0,1):
            with Fixture() as f:
                b=Board(f); b.hashes[index]='0'*64
                with self.assertRaises(ValueError): self.guard.run_once(b,request())
                self.assertEqual(self.uploads(b),[])

    def test_upload_public_scope_root_and_folder_are_revalidated(self):
        for change in ('extra','root','approval','folder'):
            with Fixture() as f:
                scope=self.scope(f); b=Board(f); folder=FOLDER
                if change=='extra': scope['extra']=1
                elif change=='root': b.ROOT=f.root/'other'
                elif change=='approval': scope['approval_sha256']='0'*64
                else: folder=FOLDER+'/extra'
                with self.assertRaises((ValueError,OSError)): self.guard.upload_once(b,TARGET,ARTIFACT,folder,scope)
                self.assertEqual(self.uploads(b),[])

    def test_upload_failures_are_consumed_and_exact_status_retained(self):
        errors=[OSError('launch refused'),subprocess.CalledProcessError(9,'upload',output='out',stderr='err'),subprocess.TimeoutExpired('upload',120,output=b'partial\xff',stderr=b'slow')]
        for error in errors:
            with self.subTest(error=type(error).__name__),Fixture() as f:
                b=Board(f); b.error=error
                with self.assertRaises(type(error)): self.guard.run_once(b,request())
                self.assertEqual(len(self.uploads(b)),1)
                value=json.loads((f.root/OUTCOME).read_text())
                self.assertEqual(value['returncode'],getattr(error,'returncode',None))
                self.assertEqual(value['timed_out'],isinstance(error,subprocess.TimeoutExpired))
                self.assertIsInstance(value['stdout'],str); self.assertIsInstance(value['stderr'],str)
                if isinstance(error,subprocess.TimeoutExpired): self.assertEqual(value['stdout'],'partial\ufffd')
                with self.assertRaises(ValueError): self.guard.run_once(b,request())
                self.assertEqual(len(self.uploads(b)),1)
        with Fixture() as f:
            b=Board(f); b.result=SimpleNamespace(returncode=7,stdout='returned',stderr='bad')
            with self.assertRaises(subprocess.CalledProcessError) as result: self.guard.run_once(b,request())
            self.assertEqual(result.exception.returncode,7); self.assertEqual(result.exception.stdout,'returned')
            self.assertEqual(json.loads((f.root/OUTCOME).read_text())['stderr'],'bad')

    def test_exclusive_claim_fsync_and_outcome_failure_never_relaunch(self):
        for mode in ('race','fsync','outcome'):
            with self.subTest(mode=mode),Fixture() as f:
                b=Board(f)
                if mode=='race': b.hooks['hash']=lambda:f.put(ATTEMPT,b'other claim')
                if mode=='outcome': b.hooks['upload']=lambda:f.put(OUTCOME,b'other outcome')
                context=mock.patch('os.fsync',side_effect=OSError('fsync failed')) if mode=='fsync' else ExitStack()
                with context,self.assertRaises((ValueError,OSError)): self.guard.run_once(b,request())
                self.assertEqual(len(self.uploads(b)),1 if mode=='outcome' else 0)
                if mode!='fsync':
                    with self.assertRaises(ValueError): self.guard.run_once(b,request())
                    self.assertEqual(len(self.uploads(b)),1 if mode=='outcome' else 0)

    def test_cli_rejects_every_override_before_transport(self):
        for argv in ([],['--run-id','wrong'],['--run-id',RUN,'--match'],['--run-id',RUN,'--compile-only'],['--run-id',RUN,'app'],['--run-id',RUN,'--startup','default'],['--run-id',RUN,'--artifact',ARTIFACT]):
            with self.subTest(argv=argv),redirect_stderr(io.StringIO()),redirect_stdout(io.StringIO()):
                try: code=self.guard.main(argv)
                except SystemExit as error: code=error.code
                self.assertIn(code,(1,2)); self.assertNotEqual(code,0)
        self.assertEqual(self.git_calls,[])

    def test_unchanged_manifest_exact_nine_keys(self):
        data=(ROOT/'tools/p0_inert_sources.json').read_bytes()
        self.assertEqual(digest(data),'a1587931afa5f817bf8b93054f384918dc8cd36d4fb71c8f7b083d76e6128802')
        self.assertEqual(len(json.loads(data)),9)
        self.assertNotIn('app',json.loads(data))


if __name__ == '__main__':
    unittest.main()
