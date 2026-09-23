"""D107 independent local reproduction and isolated host/author-suite execution."""
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import time

ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent
receipt=OUT/('host_'+str(time.time_ns())+'.json')
record={'scope':'Private WSL source copy; no board, network or hardware', 'results':[]}
def run(command,cwd):
    result=subprocess.run(list(map(str,command)),cwd=cwd,capture_output=True,text=True,timeout=600)
    record['results'].append(dict(argv=list(map(str,command)),returncode=result.returncode,
                                 stdout=result.stdout,stderr=result.stderr))
    receipt.write_text(json.dumps(record,indent=2)+'\n')
    print(result.stdout[-4000:],result.stderr[-5000:],flush=True)
    return result
with tempfile.TemporaryDirectory(prefix='d107-review-') as temporary:
    copied=Path(temporary)
    for name in ('src','tests','host','tools','bench'):
        shutil.copytree(ROOT/name,copied/name,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
    if '--second' in sys.argv:
        shutil.copytree(ROOT/'state/analysis/P2_opp_view_raw/worker/second_sources',
                        copied/'bench/opp_view',dirs_exist_ok=True)
    contract=Path('state/analysis/P2_opp_view_contract.md')
    (copied/contract).parent.mkdir(parents=True)
    shutil.copy2(ROOT/contract,copied/contract)
    record['source_hashes']={p.relative_to(copied).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
                             for p in copied.rglob('*') if p.is_file()}
    receipt.write_text(json.dumps(record,indent=2)+'\n')
    if '--zero' in sys.argv:
        config=copied/'src/config.h'
        original_config=config.read_bytes()
        data,count=re.subn(r'(\bTICK_US\s*=\s*)[^;]+;',r'\g<1>0U;',config.read_text())
        assert count==1;config.write_text(data)
        record['zero_config_sha256']=hashlib.sha256(config.read_bytes()).hexdigest()
        result=run(['g++','-std=c++17','-O1','-Wall','-Wextra','-Wpedantic','-Werror',
                    '-fno-exceptions','-fno-rtti','-I',copied/'src','-I',copied/'bench/opp_view/src',
                    '-c',copied/'bench/opp_view/src/opp_view.cpp','-o',copied/'zero.o'],copied)
        if '--second' in sys.argv:
            assert result.returncode!=0 and 'division by zero' in result.stderr
            record['verdict']='REPRODUCED_D107_R1_ZERO_PERIOD_COMPILE_FAILURE'
        else:
            assert result.returncode==0
            record['verdict']='PASS_ZERO_PERIOD_COMPILE'
        config.write_bytes(original_config)
        assert hashlib.sha256(config.read_bytes()).hexdigest()==record['source_hashes']['src/config.h']
        receipt.write_text(json.dumps(record,indent=2)+'\n')
    if '--host' in sys.argv:
        assert run(['bash','tools/test_host.sh'],copied).returncode==0
        log=copied/'build/host/Testing/Temporary/LastTest.log'
        if log.exists():shutil.copy2(log,OUT/(receipt.stem+'_LastTest.log'))
    if '--author' in sys.argv:
        result=run(['python3','-m','unittest','tests.tooling.test_opp_view','-v'],copied)
        generated=copied/'state/analysis/P2_opp_view_raw/author'
        if generated.exists():shutil.copytree(generated,OUT/(receipt.stem+'_cases'))
        assert result.returncode==0
print(receipt)
