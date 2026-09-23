# Derives D114 single-attempt upload expectations from the public run contract.
# Synthetic receipts and board calls never contact a board or execute an upload.
# Reused reviewer context saw old board_tool, but not the new guard implementation.
from contextlib import ExitStack, redirect_stderr, redirect_stdout
import copy
import hashlib
import importlib
import io
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
RUN = 'd114-ui-adc-01'
TARGET = '2629958581'
SOURCE = '396bcc45fbaf30d38b170bf0c0063c555d5e88cdad512829b86a52ffede18642'
ELF = '76e23fe03631d5cc2144578d35ca78b9bafd44158e0d18b2ab026922e4c9d05b'
ZSK = '567fb90da6965cf74efc5ac2221e543d6d2150e3bf70ddae3e2346e6646c7fb9'
REMOTE_ROOT = '/fixture/root'
BUILD_ROOT = REMOTE_ROOT + '/_app_builds/native-app-v1/' + SOURCE + '/bench-default/' + 'a'*32
ARTIFACTS = BUILD_ROOT + '/artifacts'
BOARD_FOLDER = REMOTE_ROOT + '/' + SOURCE + '/ui_adc_probe'
FQBN = 'arduino:zephyr:unoq'
PINS = ('tools/board_tool.py', 'tools/app_build_policy.py', 'tools/app_build_pins.json',
        'tools/app_build_commands.json', 'tools/ui_adc_run.py', 'tools/ui_adc_capture.py',
        'tools/p0_capture.py', 'tools/p0_mem_read.cfg', 'tools/p0_inert_sources.json',
        'state/analysis/P2_ui_adc_capture_contract.md', 'state/analysis/P2_ui_adc_run_contract.md')
OLD_KEYS = {
    'bench/p0_adc':'5ecab8cd5dd2166a640effa1bf5689dbd20cc41886870c8813eca969117e3303',
    'bench/p0_gpio':'0b143f2bc5f4fed94a93b7a80f98b2c1f6243c0d50c058b0c89251a9cbc719cb',
    'bench/p0_matrix':'2d6a5cc49c30e59af0d1b96ac160e85a358490837165ca97833cbad8e8794c70',
    'bench/p0_qtr':'b034b93123d5be6947abe29cf3be1b562104af7219186668493130958a873512',
    'bench/p0_timing':'8df06a48afb4f91a663f4f89b22acf0391331a82858e6de11619784321e900b9',
    'bench/recorder_inert':'0ffb40cde8a4eeab1eaa50f927fcad7abfc182ba3662b19b4b5677891898363d',
    'bench/runtime_inert':'2bd817c4e535324964a031cdd44720f26fd145a3cd317ab7b3ced089f35db7e5',
    'bench/ui_matrix':'c24e0a510b39f9b3ac2eee18a712b2f0f223d3635b890868e88bb5b1f575d2d1',
}
sha = lambda data: hashlib.sha256(data).hexdigest()


def request(**changes):
    values = dict(sketch='bench/ui_adc_probe', startup=None, match=False,
                  compile_only=False, run_ui_adc_probe=RUN)
    values.update(changes)
    return SimpleNamespace(**values)


class Fixture:
    def __enter__(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='d114-guard-author-')
        self.root = Path(self.temporary.name)
        for name in PINS:
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(('SYNTHETIC FIXTURE ONLY: ' + name + '\n').encode())
        (self.root / 'tools/p0_inert_sources.json').write_text(json.dumps({**OLD_KEYS, 'bench/ui_adc_probe':SOURCE}))
        self.record = self.root / 'state/analysis/P2_ui_adc_probe_run01.json'
        self.approval = self.root / 'state/analysis/P2_ui_adc_probe_raw/reviewer/run01_approval.json'
        self.approval.parent.mkdir(parents=True)
        self.attempt = self.approval.parent.parent / 'run01_upload_attempt.json'
        self.outcome = self.approval.parent.parent / 'run01_upload_outcome.json'
        self.approved = dict(schema_version=1, run_id=RUN,
            verdict='PASS_EXACT_INERT_ADC_SOURCE_TARGET_CAPTURE_GUARD', source_sha256=SOURCE,
            elf_sha256=ELF, binary_sha256=ZSK,
            file_sha256={name:sha((self.root/name).read_bytes()) for name in PINS})
        self.run = dict(schema_version=1, run_id=RUN, target=TARGET, transport='adb',
            source_sha256=SOURCE, elf_sha256=ELF, binary_sha256=ZSK, review_sha256='',
            software_commit='b'*40, setup='human-reported bare UNO Q',
            scope='one inert ADC diagnostic upload; no motors; passive readout separately')
        self.save()
        return self

    def save(self):
        self.approval.write_text(json.dumps(self.approved, indent=2)+'\n')
        self.run['review_sha256'] = sha(self.approval.read_bytes())
        self.record.write_text(json.dumps(self.run, indent=2)+'\n')

    def __exit__(self, *args):
        self.temporary.cleanup()


class FakeBoard:
    def __init__(self, fixture, outcome=None):
        self.ROOT = fixture.root
        self.fixture, self.outcome = fixture, outcome
        self.calls = []
        self.hashes = [ELF, ZSK]
        self.before_upload = None
        self.after_hash = None

    def transport(self): return 'adb'
    def target(self): return TARGET
    def setting(self, name, pattern):
        if name != 'SUMO_REMOTE_ROOT': raise AssertionError('unexpected setting '+name)
        return REMOTE_ROOT

    def remote(self, target, argv, capture=False, timeout=None):
        self.calls.append(dict(target=target, argv=list(argv), capture=capture, timeout=timeout))
        if target != TARGET: raise AssertionError('wrong board')
        if argv[0] == 'sha256sum':
            expected = ['sha256sum','--',BUILD_ROOT+'/build/ui_adc_probe.ino.elf',
                        ARTIFACTS+'/ui_adc_probe.ino.elf-zsk.bin']
            if argv != expected: raise AssertionError('wrong hash command '+repr(argv))
            if self.after_hash: self.after_hash()
            return SimpleNamespace(returncode=0, stdout=''.join(h+'  '+p+'\n' for h,p in zip(self.hashes,argv[2:])), stderr='')
        if argv[:2] == ['arduino-cli','upload']:
            if not self.fixture.attempt.is_file(): raise AssertionError('upload before durable attempt')
            if self.before_upload: self.before_upload()
            if isinstance(self.outcome, BaseException): raise self.outcome
            return self.outcome or SimpleNamespace(returncode=0, stdout='uploaded\n', stderr='')
        raise AssertionError('unexpected remote operation '+repr(argv))


class GuardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.guard = importlib.import_module('ui_adc_run')
        cls.board = importlib.import_module('board_tool')

    def setUp(self):
        self.stack = ExitStack()
        self.addCleanup(self.stack.close)
        for target in ('subprocess.run','subprocess.Popen','socket.create_connection'):
            self.stack.enter_context(mock.patch(target, side_effect=AssertionError('real external operation forbidden')))

    def load(self, fixture):
        return self.guard.load_scope(fixture.root, TARGET, 'adb')

    def fail_load(self, fixture):
        with self.assertRaises(ValueError): self.load(fixture)

    def uploads(self, board):
        return [c for c in board.calls if c['argv'][:2] == ['arduino-cli','upload']]

    def test_import_and_request_validation_are_passive(self):
        with (mock.patch.object(Path,'read_bytes',side_effect=AssertionError('file read')),
              mock.patch.object(Path,'read_text',side_effect=AssertionError('file read'))):
            importlib.reload(self.guard)
            self.assertIs(self.guard.validate_request(request(),'default'), True)

    def test_absent_request_and_exact_valid_request(self):
        absent=request(); del absent.run_ui_adc_probe
        self.assertIs(self.guard.validate_request(absent,'default'),False)
        self.assertIs(self.guard.validate_request(request(run_ui_adc_probe=None),'default'),False)
        for startup in (None,'default'):
            self.assertIs(self.guard.validate_request(request(startup=startup),'default'),True)

    def test_each_wrong_identifier_sketch_profile_and_compile_only_refuses(self):
        cases=[dict(run_ui_adc_probe=v) for v in ('','other',RUN+'\n',True,False,0,[],{})]
        cases += [dict(sketch=v) for v in ('app','bench/ui','bench/runtime_inert','bench/ui_adc_probe/')]
        cases += [dict(match=True),dict(compile_only=True),dict(startup='immediate')]
        for changes in cases:
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                self.guard.validate_request(request(**changes),changes.get('startup') or 'default')
        with self.assertRaises(ValueError): self.guard.validate_request(request(),'immediate')

    def test_exact_scope_shape_and_original_bytes_are_bound(self):
        with Fixture() as f:
            result=self.load(f)
            self.assertEqual(set(result),{'root','run_record','approval','run_record_sha256','approval_sha256'})
            self.assertEqual(result['root'],f.root.absolute())
            self.assertEqual(result['run_record'],f.run); self.assertEqual(result['approval'],f.approved)
            self.assertEqual(result['run_record_sha256'],sha(f.record.read_bytes()))
            self.assertEqual(result['approval_sha256'],sha(f.approval.read_bytes()))
            self.assertFalse(f.attempt.exists()); self.assertFalse(f.outcome.exists())

    def test_target_transport_and_each_record_identity_are_exact(self):
        with Fixture() as f:
            for target,transport in (('other','adb'),(TARGET,'ssh'),('', 'adb')):
                with self.subTest(target=target,transport=transport),self.assertRaises(ValueError):
                    self.guard.load_scope(f.root,target,transport)
        for name in ('schema_version','run_id','target','transport','source_sha256','elf_sha256',
                     'binary_sha256','review_sha256','software_commit','setup','scope'):
            for bad in (None, True, 'wrong'):
                with self.subTest(name=name,bad=bad),Fixture() as f:
                    f.run[name]=bad; f.record.write_text(json.dumps(f.run)); self.fail_load(f)
        for value in ('A'*40,'b'*39,'b'*41):
            with Fixture() as f:
                f.run['software_commit']=value; f.save(); self.fail_load(f)

    def test_approval_schema_verdict_identities_and_exact_file_key_set(self):
        for name in ('schema_version','run_id','verdict','source_sha256','elf_sha256','binary_sha256'):
            for bad in (None,True,'wrong'):
                with self.subTest(name=name,bad=bad),Fixture() as f:
                    f.approved[name]=bad; f.save(); self.fail_load(f)
        for which in ('record','approval'):
            for alteration in ('extra','missing'):
                with Fixture() as f:
                    obj=f.run if which=='record' else f.approved
                    if alteration=='extra': obj['unreviewed']=1
                    else: del obj['run_id']
                    f.save(); self.fail_load(f)
        for name in PINS:
            with self.subTest(missing_pin=name),Fixture() as f:
                del f.approved['file_sha256'][name]; f.save(); self.fail_load(f)
        with Fixture() as f:
            f.approved['file_sha256']['tools/other.py']='0'*64; f.save(); self.fail_load(f)

    def test_each_actual_file_hash_and_unset_hash_is_checked(self):
        for name in PINS:
            with self.subTest(name=name),Fixture() as f:
                (f.root/name).write_bytes(b'changed'); self.fail_load(f)
        for bad in (None,'','0'*63,'A'*64,False,'0'*64):
            with self.subTest(hash=bad),Fixture() as f:
                f.approved['file_sha256'][PINS[0]]=bad; f.save(); self.fail_load(f)

    def test_json_duplicate_nonfinite_malformed_and_size_are_refused(self):
        for which in ('record','approval'):
            for bad in ('{','[]','null','{"x":NaN}','{"x":Infinity}',
                        '{"schema_version":1,"schema_version":1}', ' '*65537):
                with self.subTest(which=which,bad=bad[:60]),Fixture() as f:
                    path=f.record if which=='record' else f.approval
                    path.write_text(bad)
                    if which=='approval':
                        f.run['review_sha256']=sha(path.read_bytes()); f.record.write_text(json.dumps(f.run))
                    self.fail_load(f)

    def test_json_exact_65536_byte_boundary_is_accepted(self):
        with Fixture() as f:
            for path in (f.approval,f.record):
                data=path.read_bytes(); path.write_bytes(data+b' '*(65536-len(data)))
                if path==f.approval:
                    f.run['review_sha256']=sha(path.read_bytes()); f.record.write_text(json.dumps(f.run))
            self.assertEqual(f.approval.stat().st_size,65536)
            self.assertEqual(f.record.stat().st_size,65536)
            self.load(f)
        for which in ('record','approval'):
            with self.subTest(oversized=which),Fixture() as f:
                path=f.record if which=='record' else f.approval
                data=path.read_bytes(); path.write_bytes(data+b' '*(65537-len(data)))
                if which=='approval':
                    f.run['review_sha256']=sha(path.read_bytes()); f.record.write_text(json.dumps(f.run))
                self.fail_load(f)

    def test_missing_directory_symlink_ancestry_and_nonregular_files_refuse(self):
        for name in PINS+('state/analysis/P2_ui_adc_probe_run01.json',
                         'state/analysis/P2_ui_adc_probe_raw/reviewer/run01_approval.json'):
            for kind in ('missing','directory','symlink','dangling'):
                with self.subTest(name=name,kind=kind),Fixture() as f:
                    path=f.root/name; old=path.read_bytes(); path.unlink()
                    if kind=='directory': path.mkdir()
                    if kind in ('symlink','dangling'):
                        other=f.root/'fixture-other'
                        if kind=='symlink': other.write_bytes(old)
                        path.symlink_to(other)
                    with self.assertRaises((ValueError,OSError)): self.load(f)
        for directory in ('tools','state/analysis/P2_ui_adc_probe_raw/reviewer'):
            with Fixture() as f:
                path=f.root/directory; moved=path.with_name(path.name+'-real')
                path.rename(moved); path.symlink_to(moved,target_is_directory=True); self.fail_load(f)
        with Fixture() as f:
            link=f.root/'root-link'; link.symlink_to(f.root,target_is_directory=True)
            with self.assertRaises(ValueError): self.guard.load_scope(link,TARGET,'adb')
            with self.assertRaises((ValueError,OSError)): self.guard.load_scope(f.root/'absent',TARGET,'adb')

    def test_existing_attempt_and_outcome_never_allow_launch(self):
        for which in ('attempt','outcome'):
            for kind in ('file','directory','dangling'):
                with self.subTest(which=which,kind=kind),Fixture() as f:
                    scope=self.load(f); path=getattr(f,which)
                    if kind=='file': path.write_text('original evidence')
                    elif kind=='directory': path.mkdir()
                    else: path.symlink_to(f.root/'missing')
                    board=FakeBoard(f)
                    with self.assertRaises(ValueError): self.guard.upload_once(board,TARGET,ARTIFACTS,BOARD_FOLDER,scope)
                    self.assertEqual(self.uploads(board),[])
                    if which=='attempt': self.assertEqual(board.calls,[])

    def test_success_checks_sibling_elf_and_zsk_before_one_durable_attempt(self):
        with Fixture() as f:
            scope=self.load(f); board=FakeBoard(f)
            original_fsync=os.fsync
            with mock.patch('os.fsync',wraps=original_fsync) as fsync:
                board.before_upload=lambda: self.assertGreaterEqual(fsync.call_count,1)
                self.guard.upload_once(board,TARGET,ARTIFACTS,BOARD_FOLDER,scope)
            self.assertEqual(len(board.calls),2)
            self.assertEqual(board.calls[0]['argv'][0],'sha256sum')
            expected=['arduino-cli','upload','--fqbn',FQBN,'--input-dir',ARTIFACTS,BOARD_FOLDER]
            self.assertEqual(self.uploads(board),[dict(target=TARGET,argv=expected,capture=True,timeout=120)])
            intent=json.loads(f.attempt.read_text()); outcome=json.loads(f.outcome.read_text())
            self.assertEqual(set(intent),{'schema_version','run_id','target','source_sha256','elf_sha256',
                'binary_sha256','approval_sha256','started_utc','argv'})
            self.assertEqual(intent['argv'],expected); self.assertEqual(intent['approval_sha256'],scope['approval_sha256'])
            self.assertEqual(intent['source_sha256'],SOURCE); self.assertEqual(intent['elf_sha256'],ELF)
            self.assertEqual(intent['binary_sha256'],ZSK); self.assertEqual(intent['run_id'],RUN)
            self.assertEqual(intent['target'],TARGET); self.assertEqual(intent['schema_version'],1)
            self.assertTrue(intent['started_utc'])
            self.assertEqual(set(outcome),{'schema_version','run_id','finished_utc','returncode','stdout','stderr','timed_out','error'})
            self.assertEqual(outcome['returncode'],0); self.assertEqual(outcome['stdout'],'uploaded\n')
            self.assertEqual(outcome['stderr'],''); self.assertIs(outcome['timed_out'],False)
            self.assertIsNone(outcome['error']); self.assertEqual(outcome['run_id'],RUN)
            before=f.attempt.read_bytes(); calls=len(board.calls)
            with self.assertRaises(ValueError): self.guard.upload_once(board,TARGET,ARTIFACTS,BOARD_FOLDER,scope)
            self.assertEqual(len(board.calls),calls); self.assertEqual(f.attempt.read_bytes(),before)

    def test_wrong_artifact_paths_board_folder_or_target_refuse_before_remote(self):
        paths=('/cached/artifacts',ARTIFACTS+'/',ARTIFACTS+'/other',ARTIFACTS.replace('a'*32,'a'*31),
               ARTIFACTS.replace('a'*32,'A'*32),ARTIFACTS.replace(SOURCE,'0'*64),
               ARTIFACTS.replace('bench-default','bench-immediate'),ARTIFACTS.replace('native-app-v1','other'),
               ARTIFACTS.replace(REMOTE_ROOT,'/other/root'))
        for artifact in paths:
            with self.subTest(path=artifact),Fixture() as f:
                board=FakeBoard(f)
                with self.assertRaises(ValueError): self.guard.upload_once(board,TARGET,artifact,BOARD_FOLDER,self.load(f))
                self.assertEqual(board.calls,[]); self.assertFalse(f.attempt.exists())
        for target,folder in (('wrong',BOARD_FOLDER),(TARGET,BOARD_FOLDER+'/'),(TARGET,'/cached/ui_adc_probe')):
            with Fixture() as f:
                board=FakeBoard(f)
                with self.assertRaises(ValueError): self.guard.upload_once(board,target,ARTIFACTS,folder,self.load(f))
                self.assertEqual(board.calls,[])

    def test_each_binary_mismatch_or_hash_command_failure_prevents_attempt(self):
        for index in (0,1):
            with Fixture() as f:
                board=FakeBoard(f); board.hashes[index]='0'*64
                with self.assertRaises(ValueError): self.guard.upload_once(board,TARGET,ARTIFACTS,BOARD_FOLDER,self.load(f))
                self.assertEqual(len(board.calls),1); self.assertFalse(f.attempt.exists())
        with Fixture() as f:
            board=FakeBoard(f)
            board.remote=mock.Mock(side_effect=subprocess.CalledProcessError(1,['sha256sum'],output='bad',stderr='failed'))
            with self.assertRaises(subprocess.CalledProcessError):
                self.guard.upload_once(board,TARGET,ARTIFACTS,BOARD_FOLDER,self.load(f))
            self.assertEqual(board.remote.call_count,1); self.assertFalse(f.attempt.exists())

    def test_revalidation_rejects_changed_scope_before_and_after_hashes(self):
        for when in ('before','after'):
            for changed in ('pinned','record','approval','scope'):
                with self.subTest(when=when,changed=changed),Fixture() as f:
                    scope=self.load(f); board=FakeBoard(f)
                    def mutate():
                        if changed=='pinned': (f.root/PINS[0]).write_text('changed')
                        elif changed=='record': f.record.write_bytes(f.record.read_bytes()+b' ')
                        elif changed=='approval': f.approval.write_bytes(f.approval.read_bytes()+b' ')
                        else: scope['run_record_sha256']='0'*64
                    if when=='before': mutate()
                    else: board.after_hash=mutate
                    with self.assertRaises(ValueError): self.guard.upload_once(board,TARGET,ARTIFACTS,BOARD_FOLDER,scope)
                    self.assertEqual(self.uploads(board),[]); self.assertFalse(f.attempt.exists())

    def test_attempt_race_or_fsync_failure_cannot_launch(self):
        with Fixture() as f:
            board=FakeBoard(f); board.after_hash=lambda: f.attempt.write_text('other attempt')
            with self.assertRaises((ValueError,FileExistsError)):
                self.guard.upload_once(board,TARGET,ARTIFACTS,BOARD_FOLDER,self.load(f))
            self.assertEqual(self.uploads(board),[]); self.assertEqual(f.attempt.read_text(),'other attempt')
        with Fixture() as f:
            board=FakeBoard(f)
            with mock.patch('os.fsync',side_effect=OSError('disk sync failed')),self.assertRaises(OSError):
                self.guard.upload_once(board,TARGET,ARTIFACTS,BOARD_FOLDER,self.load(f))
            self.assertEqual(self.uploads(board),[]); self.assertTrue(f.attempt.exists())

    def test_nonzero_oserror_timeout_and_unknown_launch_consume_attempt(self):
        errors=[subprocess.CalledProcessError(7,['upload'],output='partial',stderr='failed'),
                OSError('executable absent'),subprocess.TimeoutExpired(['upload'],120,output=b'prefix\xff',stderr=b'err\xfe'),
                SimpleNamespace(returncode=9,stdout='nonzero',stderr='bad')]
        for error in errors:
            with self.subTest(error=type(error).__name__),Fixture() as f:
                board=FakeBoard(f,error); scope=self.load(f)
                with self.assertRaises((ValueError,OSError,subprocess.SubprocessError)):
                    self.guard.upload_once(board,TARGET,ARTIFACTS,BOARD_FOLDER,scope)
                self.assertEqual(len(self.uploads(board)),1); self.assertTrue(f.attempt.is_file())
                outcome=json.loads(f.outcome.read_text())
                self.assertIsInstance(outcome['stdout'],str); self.assertIsInstance(outcome['stderr'],str)
                self.assertIsInstance(outcome['error'],str); self.assertTrue(outcome['error'])
                if isinstance(error,subprocess.TimeoutExpired):
                    self.assertIs(outcome['timed_out'],True)
                    self.assertEqual(outcome['stdout'],'prefix\ufffd'); self.assertEqual(outcome['stderr'],'err\ufffd')
                elif isinstance(error,subprocess.CalledProcessError):
                    self.assertEqual(outcome['returncode'],7); self.assertEqual(outcome['stdout'],'partial')
                elif isinstance(error,OSError):
                    self.assertIsNone(outcome['returncode']); self.assertEqual(outcome['stdout'],'')
                else: self.assertEqual(outcome['returncode'],9)
                calls=len(board.calls)
                with self.assertRaises(ValueError): self.guard.upload_once(board,TARGET,ARTIFACTS,BOARD_FOLDER,scope)
                self.assertEqual(len(board.calls),calls)

    def test_outcome_collision_during_upload_retains_attempt_and_does_not_retry(self):
        with Fixture() as f:
            board=FakeBoard(f); board.before_upload=lambda: f.outcome.write_text('other evidence')
            with self.assertRaises((ValueError,OSError)):
                self.guard.upload_once(board,TARGET,ARTIFACTS,BOARD_FOLDER,self.load(f))
            self.assertEqual(len(self.uploads(board)),1)
            self.assertTrue(f.attempt.exists()); self.assertEqual(f.outcome.read_text(),'other evidence')

    def test_cli_parses_exact_option_without_executing_flash(self):
        argv=['board_tool.py','flash','bench/ui_adc_probe','--run-ui-adc-probe',RUN]
        with mock.patch.object(sys,'argv',argv),mock.patch.object(self.board,'flash') as flash:
            self.assertEqual(self.board.main(),0)
            self.assertEqual(flash.call_args.args[0].run_ui_adc_probe,RUN)
        with mock.patch.object(sys,'argv',argv[:-1]),redirect_stderr(io.StringIO()),self.assertRaises(SystemExit) as error:
            self.board.main()
        self.assertEqual(error.exception.code,2)

    def test_flash_refuses_bad_requests_and_generic_upload_before_target(self):
        cases=[request(run_ui_adc_probe=None),request(run_ui_adc_probe='wrong'),request(sketch='app'),
               request(sketch='bench/ui'),request(match=True),request(startup='immediate'),request(compile_only=True)]
        absent=request(); del absent.run_ui_adc_probe; cases.append(absent)
        for args in cases:
            with (self.subTest(args=args),mock.patch.object(self.board,'target') as target,
                  mock.patch.object(self.board,'stage') as stage, mock.patch.object(self.board,'remote') as remote):
                with self.assertRaises(ValueError): self.board.flash(args)
                target.assert_not_called(); stage.assert_not_called(); remote.assert_not_called()

    def test_flash_success_uses_checked_return_and_never_falls_back_after_failure(self):
        for failure in (None,'verify_inert_source','sync_sources','compile_app','upload_once'):
            with self.subTest(failure=failure),Fixture() as f,ExitStack() as stack:
                board=self.board; scope=self.load(f)
                stack.enter_context(mock.patch.object(board,'ROOT',f.root))
                values={'target':TARGET,'transport':'adb','setting':REMOTE_ROOT,'stage':f.root/'stage',
                        'source_hash':SOURCE,'compile_app':ARTIFACTS}
                calls={name:stack.enter_context(mock.patch.object(board,name,return_value=value)) for name,value in values.items()}
                for name in ('require_transport','verify_core','sync_sources','remote','verify_inert_source'):
                    calls[name]=stack.enter_context(mock.patch.object(board,name))
                loader=stack.enter_context(mock.patch.object(self.guard,'load_scope',return_value=scope))
                uploader=stack.enter_context(mock.patch.object(self.guard,'upload_once'))
                if failure:
                    (uploader if failure=='upload_once' else calls[failure]).side_effect=ValueError('controlled failure')
                    with redirect_stdout(io.StringIO()),self.assertRaises(ValueError): board.flash(request())
                else:
                    with redirect_stdout(io.StringIO()): board.flash(request())
                    calls['verify_inert_source'].assert_called_once_with('bench/ui_adc_probe',SOURCE)
                    calls['compile_app'].assert_called_once_with(TARGET,SOURCE,BOARD_FOLDER,REMOTE_ROOT,
                        FQBN,'-DMATCH=0 -DMOTORS_ALLOWED=0','default',project='ui_adc_probe.ino')
                    uploader.assert_called_once_with(board,TARGET,ARTIFACTS,BOARD_FOLDER,scope)
                    loader.assert_called_once_with(f.root,TARGET,'adb')
                if failure and failure!='upload_once': uploader.assert_not_called()
                self.assertFalse(any(c.args[1][:2]==['arduino-cli','upload'] for c in calls['remote'].call_args_list))

    def test_manifest_old_eight_values_and_only_exact_optional_new_key(self):
        actual=json.loads((ROOT/'tools/p0_inert_sources.json').read_text())
        self.assertEqual({k:actual[k] for k in OLD_KEYS},OLD_KEYS)
        self.assertLessEqual(set(actual)-set(OLD_KEYS),{'bench/ui_adc_probe'})
        if 'bench/ui_adc_probe' in actual: self.assertEqual(actual['bench/ui_adc_probe'],SOURCE)


if __name__ == '__main__':
    unittest.main(verbosity=2)
