# Exercises independent safety failure probes for the exact default-app guard.
# All board, Git and subprocess effects are controlled host-only substitutes.
# Stores an exclusive evidence folder without editing production or public tests.
from contextlib import ExitStack, redirect_stderr, redirect_stdout
from datetime import datetime, timezone
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace
import unittest
from unittest import mock

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[4]
spec = importlib.util.spec_from_file_location('public_guard_oracle', ROOT/'tests/tooling/test_app_default_run.py')
public = importlib.util.module_from_spec(spec)
spec.loader.exec_module(public)


class PrivateProbes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import app_default_run
        cls.guard = app_default_run

    def setUp(self):
        self.stack = ExitStack()
        self.addCleanup(self.stack.close)
        self.stack.enter_context(mock.patch.dict(os.environ, public.ENV, clear=True))
        self.stack.enter_context(mock.patch('subprocess.run', side_effect=self.git))
        for name in ('subprocess.Popen', 'socket.create_connection'):
            self.stack.enter_context(mock.patch(name, side_effect=AssertionError('real external operation denied')))

    def git(self, argv, **kwargs):
        self.assertEqual(argv[0:2], ['git','-C'])
        self.assertEqual(argv[3:], ['rev-parse','HEAD'])
        self.assertEqual(kwargs['timeout'], 10)
        return SimpleNamespace(returncode=0, stdout=public.HEAD+'\n', stderr='')

    def uploads(self, board):
        return [entry for entry in board.calls if entry[0]=='upload']

    def receipt(self, fixture):
        paths=list((fixture.root/public.RAW/'preparations').glob('*.json'))
        self.assertEqual(len(paths),1)
        return json.loads(paths[0].read_text())

    def test_interrupted_preparations_never_launch_and_record_interruption(self):
        for phase in ('verify_core','sync_sources','compile_app','hash'):
            with self.subTest(phase=phase),public.Fixture() as f:
                board=public.Board(f)
                def stop(): raise KeyboardInterrupt('private preparation interruption')
                board.hooks[phase]=stop
                with self.assertRaises(KeyboardInterrupt): self.guard.run_once(board,public.request())
                self.assertEqual(self.uploads(board),[])
                self.assertFalse((f.root/public.ATTEMPT).exists())
                self.assertEqual(self.receipt(f)['error']['type'],'KeyboardInterrupt')

    def test_staged_content_or_added_file_during_hash_refuses_before_claim(self):
        for name in ('app.ino','extra.bin'):
            with self.subTest(name=name),public.Fixture() as f:
                board=public.Board(f)
                board.hooks['hash']=lambda:f.put('build/stage/app/'+name,b'private mutation')
                with self.assertRaises(ValueError): self.guard.run_once(board,public.request())
                self.assertEqual(self.uploads(board),[])
                self.assertFalse((f.root/public.ATTEMPT).exists())

    def test_self_consistent_reviewer_record_replacement_still_refuses(self):
        with public.Fixture() as f:
            board=public.Board(f)
            def mutate():
                f.put(public.REVIEW,b'changed private review bytes')
                f.approval['review_sha256']=public.digest((f.root/public.REVIEW).read_bytes())
                f.save()
            board.hooks['hash']=mutate
            with self.assertRaises(ValueError): self.guard.run_once(board,public.request())
            self.assertEqual(self.uploads(board),[])
            self.assertFalse((f.root/public.ATTEMPT).exists())

    def test_outcome_specific_fsync_failure_retains_consumed_attempt(self):
        with public.Fixture() as f:
            board=public.Board(f)
            original=os.fsync
            seen=[]
            def fsync(fd):
                path=f.root/public.OUTCOME
                if path.exists() and os.fstat(fd).st_ino==path.stat().st_ino:
                    seen.append(True)
                    raise OSError('private outcome fsync failure')
                return original(fd)
            with mock.patch('os.fsync',side_effect=fsync),self.assertRaises(OSError):
                self.guard.run_once(board,public.request())
            self.assertEqual(seen,[True])
            self.assertEqual(len(self.uploads(board)),1)
            self.assertTrue((f.root/public.ATTEMPT).exists())
            with self.assertRaises(ValueError): self.guard.run_once(board,public.request())
            self.assertEqual(len(self.uploads(board)),1)

    def test_git_nonzero_original_status_and_output_retained(self):
        with public.Fixture() as f:
            board=public.Board(f)
            result=SimpleNamespace(returncode=37,stdout='private stdout',stderr='private stderr')
            with mock.patch('subprocess.run',return_value=result),self.assertRaises(ValueError):
                self.guard.run_once(board,public.request())
            self.assertEqual(board.calls,[])
            check=self.receipt(f)['local_git_checks'][0]
            self.assertEqual((check['returncode'],check['stdout'],check['stderr']),(37,'private stdout','private stderr'))
            self.assertEqual(check['argv'],['git','-C',str(f.root),'rev-parse','HEAD'])

    def test_root_symlink_and_special_staged_file_refuse(self):
        with public.Fixture() as f:
            alias=f.root/'alias'
            alias.symlink_to(f.root,target_is_directory=True)
            with self.assertRaises(ValueError): self.guard.load_scope(alias,public.TARGET,'adb')
        with public.Fixture() as f:
            os.mkfifo(f.stage/'private.fifo')
            board=public.Board(f)
            with self.assertRaises(ValueError): self.guard.run_once(board,public.request())
            self.assertEqual(self.uploads(board),[])
            self.assertFalse((f.root/public.ATTEMPT).exists())


if __name__=='__main__':
    label=sys.argv[1]
    if not label.isalnum(): raise ValueError('unique alphanumeric label required')
    output=Path(__file__).parent/label
    output.mkdir(exist_ok=False)
    receipt=dict(started_utc=datetime.now(timezone.utc).isoformat(),scope='SYNTHETIC_HOST_ONLY_NO_BOARD',python=sys.version,
        implementation_sha256=public.digest((ROOT/'tools/app_default_run.py').read_bytes()),
        public_test_sha256=public.digest((ROOT/'tests/tooling/test_app_default_run.py').read_bytes()),
        private_probes_sha256=public.digest(Path(__file__).read_bytes()))
    log=io.StringIO()
    with ExitStack() as stack,redirect_stdout(log),redirect_stderr(log):
        for name in ('subprocess.run','subprocess.Popen','socket.create_connection'):
            stack.enter_context(mock.patch(name,side_effect=AssertionError('real external operation denied')))
        result=unittest.TextTestRunner(stream=log,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(PrivateProbes))
    receipt.update(finished_utc=datetime.now(timezone.utc).isoformat(),tests=result.testsRun,failures=len(result.failures),errors=len(result.errors),skipped=len(result.skipped),successful=result.wasSuccessful())
    (output/'unittest.txt').write_text(log.getvalue())
    (output/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt,indent=2))
    raise SystemExit(0 if result.wasSuccessful() else 1)
