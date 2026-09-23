"""Compare final target source bytes with physical files and staged Git blobs."""
import hashlib,json,subprocess
from pathlib import Path
root=Path(__file__).resolve().parents[2]
raw=root/'state/analysis/P2_qtr_cal_raw'
data=json.loads((raw/'target_cc4819aa_bench-default.json').read_text())
rows=[]
for relative,wanted in data['source_files'].items():
    if relative.startswith('src/core/') or relative.startswith('src/hal/') or relative=='src/config.h':
        path=relative
    else:
        path='bench/p2_qtr_cal_compile/'+relative
    actual=hashlib.sha256((root/path).read_bytes()).hexdigest()
    process=subprocess.run(['git','show',':'+path],cwd=root,capture_output=True,check=True)
    staged=hashlib.sha256(process.stdout).hexdigest()
    assert actual==staged==wanted,(path,actual,staged,wanted)
    rows.append(dict(path=path,sha256=wanted))
assert len(rows)==67 and len(data['records'])==3 and not data['math_missing']
elf=next(x for x in data['records'] if x['path'].endswith('.ino.elf'))
required=['qtr_cal_probe::exercise','Calibration::step','applyRawSnapshot','formatConfig',
          'applyCalibration','prepareCalibrationLine','prepareLineStart']
assert all(any(name in symbol for symbol in elf['nm']) for name in required)
receipt=dict(status='PASS',source=data['source_sha256'],files=rows,
    artifacts=[dict(path=x['path'],bytes=x['bytes'],sha256=x['sha256']) for x in data['records']],
    native_imports=len(data['native_names']),math_imports=len(data['math_aliases']),
    scope='Physical files and staged Git blobs equal board Linux source; no MCU or physical claim')
(raw/'source_integrity.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(status='PASS',files=len(rows),elf=elf['sha256'])))
