"""Reproduce D107 passive-state regression and prove its correction in private WSL copies."""
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import time

ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent
def sha(data):return hashlib.sha256(data).hexdigest()
current=(ROOT/'bench/opp_view/src/opp_view.cpp').read_bytes()
assert sha(current)=='1be9bc511d0b1af5d1a95f664f20e93e0779c0cd617596cd272fe615ea1c55e3'
newline=b'\r\n' if b'\r\n' in current else b'\n'
prefix=newline.join((b'bool Runner::poll() {',b'    report_.fresh = false;',
                    b'    if (report_.phase != Phase::RUNNING) return false;'))
assert current.count(prefix)==1
interim=current.replace(prefix,b'bool Runner::poll() {')
marker=newline.join((b'    } else {',b'        std::uint32_t started = 0U;'))
replacement=newline.join((b'    } else {',b'        report_.fresh = false;',
    b'        if (report_.phase != Phase::RUNNING) return false;',b'        std::uint32_t started = 0U;'))
assert interim.count(marker)==1
interim=interim.replace(marker,replacement)
assert sha(interim)=='23a24bb0a740876b41cc823e1ff4299758dbedc188f161870d993d2497c964b8'
(OUT/'interim_23a24bb0.cpp').write_bytes(interim)
record={'scope':'Synthetic public-state regression; no board or private state',
        'interim_provenance':'Exact reconstruction by reversing admission movement; SHA matches independently observed interim bytes',
        'source_sha256':{'interim':sha(interim),'fixed':sha(current)},'results':[]}
receipt=OUT/('passive_'+str(time.time_ns())+'.json')
with tempfile.TemporaryDirectory(prefix='d107-passive-review-') as temporary:
    copied=Path(temporary)
    shutil.copytree(ROOT/'src',copied/'src')
    shutil.copytree(ROOT/'bench/opp_view',copied/'bench')
    config=copied/'src/config.h'
    text,count=re.subn(r'(\bTICK_US\s*=\s*)[^;]+;',r'\g<1>0U;',config.read_text())
    assert count==1;config.write_text(text)
    record['zero_config_sha256']=sha(config.read_bytes())
    record['test_sha256']=sha((OUT/'passive_zero.cc').read_bytes())
    source=copied/'bench/src/opp_view.cpp'
    for label,data in [('interim',interim),('fixed',current)]:
        source.write_bytes(data)
        binary=copied/label
        command=['g++','-std=c++17','-O1','-Wall','-Wextra','-Wpedantic','-Werror',
                 '-fno-exceptions','-fno-rtti','-I',copied/'src','-I',copied/'bench/src',
                 '-include','initializer_list',source,OUT/'passive_zero.cc','-o',binary]
        for argv in (command,[binary]):
            result=subprocess.run(list(map(str,argv)),capture_output=True,text=True,timeout=120)
            record['results'].append(dict(profile=label,argv=list(map(str,argv)),returncode=result.returncode,
                                         stdout=result.stdout,stderr=result.stderr))
            receipt.write_text(json.dumps(record,indent=2)+'\n')
            print(label,result.returncode,result.stdout,result.stderr,flush=True)
            if argv==command:assert result.returncode==0
            elif label=='interim':assert result.returncode==1 and 'failures: 8' in result.stdout
            else:assert result.returncode==0 and 'failures: 0' in result.stdout
print(receipt)
