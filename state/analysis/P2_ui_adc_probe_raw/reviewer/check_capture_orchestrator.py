"""Review-authored controlled checks for three outer-runner fixes; no board calls."""
from contextlib import redirect_stdout
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from types import SimpleNamespace
from unittest import mock

ROOT=Path(__file__).resolve().parents[4]
OUT=Path(__file__).resolve().parent
PATH=ROOT/'state/analysis/P2_ui_adc_probe_capture_run01.py'
PIN='46a1fe34ef2e6ab88c1843cae0201781b6e659e474992c77bd16a8b91e61fa6b'
assert hashlib.sha256(PATH.read_bytes()).hexdigest()==PIN
spec=importlib.util.spec_from_file_location('reviewed_outer_capture',PATH)
module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
checks=[]
for error in (None,subprocess.TimeoutExpired(['fixture'],90,output=b'part\xff',stderr=b'bad\xfe'),OSError('missing')):
    with tempfile.TemporaryDirectory(prefix='d114-pull-review-') as name:
        folder=Path(name)
        def launch(argv,**kwargs):
            assert kwargs['timeout']==90 and argv==['fixture-adb','-s','2629958581','pull',module.FOLDER,str(folder/'local')]
            assert (folder/'run01_capture_pull_attempt.json').is_file()
            if error: raise error
            return SimpleNamespace(returncode=0,stdout='pulled',stderr='')
        with mock.patch.object(module,'RAW',folder),mock.patch.object(module.board,'adb_executable',return_value='fixture-adb'),mock.patch.object(module.board,'target',return_value='2629958581'),mock.patch.object(module.subprocess,'run',side_effect=launch) as run:
            try: module.pull_evidence(folder/'local')
            except AssertionError:
                assert error is not None
            else: assert error is None
            assert run.call_count==1
        outcome=json.loads((folder/'run01_capture_pull.json').read_text())
        assert outcome['finished_utc'] and outcome['started_utc']
        if isinstance(error,subprocess.TimeoutExpired):
            assert outcome['stdout']=='part\ufffd' and outcome['stderr']=='bad\ufffd'
        if isinstance(error,OSError): assert outcome['stdout']==outcome['stderr']==''
        checks.append({'case':'pull '+('success' if error is None else type(error).__name__),'retained':outcome})
for error in (None,subprocess.TimeoutExpired(['fixture'],30,output=b'part',stderr=b'err')):
    with tempfile.TemporaryDirectory(prefix='d114-hash-review-') as name:
        folder=Path(name)
        def remote(target,argv,**kwargs):
            assert target=='2629958581' and kwargs=={'capture':True,'timeout':30}
            if error: raise error
            return SimpleNamespace(returncode=0,stdout='hashes',stderr='')
        with mock.patch.object(module,'RAW',folder),mock.patch.object(module.board,'target',return_value='2629958581'),mock.patch.object(module.board,'remote',side_effect=remote) as run:
            try: result=module.hash_remote('2629958581',['sha256sum','--','fixture'])
            except RuntimeError: assert error is not None
            else: assert error is None and result.stdout=='hashes'
            assert run.call_count==1
        record=json.loads((folder/'run01_capture_tool_hash_command.json').read_text())
        checks.append({'case':'hash '+('success' if error is None else 'timeout'),'retained':record})

class File:
    name='blob'
    def __init__(self,size,data): self.size,self.data,self.requested=size,data,[]
    def lstat(self): return SimpleNamespace(st_mode=0o100600,st_size=self.size)
    def open(self,mode):
        assert mode=='rb'
        owner=self
        class Stream(io.BytesIO):
            def read(self,size=-1): owner.requested.append(size); return super().read(size)
        return Stream(self.data)

class Folder:
    parents=[]
    def __init__(self,entries): self.entries,self.visited=entries,0
    def is_dir(self): return True
    def is_symlink(self): return False
    def iterdir(self):
        for entry in self.entries: self.visited+=1; yield entry

for label,folder,valid in (
    ('101st entry stops enumeration',Folder([File(1,b'x') for _ in range(200)]),False),
    ('bounded healthy file',Folder([File(3,b'abc')]),True),
    ('growing file refuses after size plus one',Folder([File(3,b'abcdef')]),False),
    ('oversize file refuses before read',Folder([File(2097153,b'')]),False)):
    with mock.patch('pathlib.Path',return_value=folder),redirect_stdout(io.StringIO()):
        try: exec(compile(module.MANIFEST_PROGRAM,'<reviewed fixed manifest>','exec'),{})
        except AssertionError: assert not valid
        else: assert valid
    if len(folder.entries)>100:
        assert folder.visited==101 and not any(f.requested for f in folder.entries)
    elif folder.entries[0].size>2097152: assert not folder.entries[0].requested
    else: assert folder.entries[0].requested==[4]
    checks.append({'case':label,'pass':True,'visited':folder.visited})
record={'verdict':'PASS_SCOPED_OUTER_CAPTURE_FIXES','script_sha256':PIN,'checks':checks,
        'independence':'Review-authored after source inspection; not an independently frozen contract suite',
        'board_actions':False}
(OUT/'capture_orchestrator_checks.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps({'verdict':record['verdict'],'checks':len(checks)}))
