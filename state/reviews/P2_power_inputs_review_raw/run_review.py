"""Run isolated normal/sanitized reviewer cases and retain exact command receipts."""
from pathlib import Path
import hashlib,json,subprocess,time
root=Path.cwd(); out=root/'state/reviews/P2_power_inputs_review_raw'
linux='/mnt/c/Users/narut/OneDrive/Desktop/Project/techbots_Sumo_Robots'
records=[]
for profile,flags in [('normal','-O2'),('sanitizer','-O1 -g -fsanitize=address,undefined -fno-omit-frame-pointer -fno-pie -no-pie')]:
    binary=f'/tmp/sumo-d093-review-{profile}'
    command=f'g++ -std=c++17 {flags} -Wall -Wextra -Wpedantic -Werror -fno-exceptions -fno-rtti -DDOCTEST_CONFIG_NO_EXCEPTIONS_BUT_WITH_ALL_ASSERTS -Isrc -isystem host/third_party src/hal/power_inputs.cpp src/hal/ui.cpp state/reviews/P2_power_inputs_review_raw/adversarial.cpp -o {binary}'
    for action,args in [('compile',['bash','-lc',command]),('test',[binary])]:
        argv=['wsl.exe','--cd',linux]+args
        start=time.monotonic(); result=subprocess.run(argv,capture_output=True)
        (out/f'{profile}_{action}.txt').write_bytes(result.stdout+result.stderr)
        records.append(dict(profile=profile,action=action,argv=argv,returncode=result.returncode,seconds=time.monotonic()-start))
        print(profile,action,result.returncode,result.stdout.decode(errors='replace'),flush=True)
        if result.returncode: break
    if result.returncode: break
paths=['src/hal/power_inputs.cpp','src/hal/power_inputs.h','src/hal/power_inputs_unoq.cpp','src/hal/ui.cpp','src/config.h','state/reviews/P2_power_inputs_review_raw/adversarial.cpp']
receipt=dict(source_hashes={p:hashlib.sha256((root/p).read_bytes()).hexdigest() for p in paths},records=records)
(out/'adversarial_runs.json').write_text(json.dumps(receipt,indent=2)+'\n')
raise SystemExit(any(r['returncode'] for r in records))
