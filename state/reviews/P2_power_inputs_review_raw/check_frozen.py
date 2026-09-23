"""Record the reviewed snapshot and prove established tests/source unchanged."""
from pathlib import Path
import hashlib,json,subprocess
root=Path.cwd(); out=root/'state/reviews/P2_power_inputs_review_raw'
paths=subprocess.check_output(['git','ls-tree','-r','--name-only','8e4544a','tests','src','tools']).decode().splitlines()
allowed={'src/config.h','tools/p0_inert_sources.json'}
checked=[]
checkout_crlf=[]
for path in paths:
    if path in allowed: continue
    before=subprocess.check_output(['git','show','8e4544a:'+path])
    current=(root/path).read_bytes()
    if before!=current:
        # core.autocrlf=true has pre-existing checked-out CRLF in legacy fixtures.
        assert before.replace(b'\r\n',b'\n')==current.replace(b'\r\n',b'\n'),('established file changed beyond checkout CRLF',path)
        checkout_crlf.append(path)
    checked.append(path)
current_paths=['src/config.h','src/hal/power_inputs.h','src/hal/power_inputs.cpp','src/hal/power_inputs_unoq.cpp','host/CMakeLists.txt']
current_paths += [p.relative_to(root).as_posix() for p in (root/'bench/p2_power_inputs_compile').rglob('*') if p.is_file()]
result=dict(baseline='8e4544a',unchanged_count=len(checked),unchanged=checked,checkout_crlf=checkout_crlf,
            snapshot={p:hashlib.sha256((root/p).read_bytes()).hexdigest() for p in sorted(current_paths)})
(out/'frozen_source.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(dict(unchanged_count=len(checked),snapshot=result['snapshot']),indent=2))
