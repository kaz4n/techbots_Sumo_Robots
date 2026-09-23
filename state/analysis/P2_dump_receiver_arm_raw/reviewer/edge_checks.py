"""Controlled CLI edge reproduction; never launches a real transport."""
import contextlib
import hashlib
import importlib
import io
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
from unittest import mock

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
record = {'source_sha256': hashlib.sha256((ROOT/'tools/dump_match.py').read_bytes()).hexdigest(), 'cases': []}
with tempfile.TemporaryDirectory(prefix='d113-review-edge-') as temporary:
    copied = Path(temporary)
    shutil.copytree(ROOT/'tools', copied/'tools', ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
    sys.path.insert(0, str(copied/'tools'))
    module = importlib.import_module('dump_match')
    for name, env in (
        ('missing-transport', {'SUMO_SSH_TARGET':'fixture@board.invalid'}),
        ('missing-executable', {'SUMO_TRANSPORT':'ssh','SUMO_SSH_TARGET':'fixture@board.invalid'}),
    ):
        for option in ('--observe-connection','--connection-ticket'):
            argv = [option,'0123456789abcdef0123456789abcdef']
            if option == '--connection-ticket':
                argv += ['--output-dir',str(copied/name)]
            stdout,stderr=io.StringIO(),io.StringIO()
            with mock.patch.dict(os.environ,env,clear=True), mock.patch.object(module.board,'remote',side_effect=FileNotFoundError('synthetic missing executable')) as remote:
                with contextlib.redirect_stdout(stdout),contextlib.redirect_stderr(stderr):
                    try: result=module.main(argv)
                    except SystemExit as error: result=error.code
            item={'profile':name,'mode':option,'returncode':result,'remote_calls':remote.call_count,
                  'stdout':stdout.getvalue(),'stderr':stderr.getvalue()}
            if option == '--connection-ticket' and (copied/name).exists():
                item['error_metadata']=[json.loads(p.read_text()) for p in (copied/name).rglob('error.json')]
            record['cases'].append(item)
    for transport in ('ssh','adb'):
        environment={'SUMO_TRANSPORT':transport,
                     'SUMO_SSH_TARGET':'fixture@board.invalid','SUMO_ADB_SERIAL':'fixture-serial'}
        for option in ('--observe-connection','--connection-ticket'):
            argv=[option,'0123456789abcdef0123456789abcdef']
            folder=copied/('real-remote-'+transport)
            if option == '--connection-ticket': argv += ['--output-dir',str(folder)]
            stdout,stderr=io.StringIO(),io.StringIO()
            with mock.patch.dict(os.environ,environment,clear=True), \
                 mock.patch.object(module.board.shutil,'which',return_value=None), \
                 mock.patch.object(module.board.subprocess,'run',side_effect=FileNotFoundError('synthetic launch refusal')) as launch, \
                 mock.patch.object(module.board,'remote',wraps=module.board.remote) as remote:
                with contextlib.redirect_stdout(stdout),contextlib.redirect_stderr(stderr):
                    result=module.main(argv)
            item={'profile':'actual-board-remote-missing-executable','transport':transport,'mode':option,
                  'returncode':result,'remote_calls':remote.call_count,'launch_calls':launch.call_count,
                  'stdout':stdout.getvalue(),'stderr':stderr.getvalue()}
            if folder.exists(): item['error_metadata']=[json.loads(p.read_text()) for p in folder.rglob('error.json')]
            assert result == 1
            if option == '--observe-connection':
                envelope=json.loads(item['stdout'])
                assert envelope['error']['code']=='CONNECTION_TRANSPORT' and envelope['observed_utc'] is None
            else:
                assert item['error_metadata'][0]['code']=='TRANSPORT'
                assert item['error_metadata'][0]['connection_evidence']['error']['code']=='CONNECTION_TRANSPORT'
            assert launch.call_count == (remote.call_count if transport=='ssh' else 0)
            record['cases'].append(item)
path=OUT/('edge_'+record['source_sha256'][:8]+'.json')
path.write_text(json.dumps(record,indent=2)+'\n')
print(path)
for item in record['cases']:
    print(item['profile'],item['mode'],item['returncode'],item['remote_calls'])
