import hashlib,json,subprocess,time
from pathlib import Path
root=Path.cwd();out=root/'state/reviews/P2_tick_timing_review_raw'
linux='/mnt/c/Users/narut/OneDrive/Desktop/Project/techbots_Sumo_Robots'
sources=['tests/test_tick_timing.cpp','tests/fixtures/tick_timing_fixture.h','src/core/fsm.h','src/core/fsm_robot.cpp']
checks=[]
for active in [0,1]:
    command=f'g++ -std=c++17 -O0 -g -Wall -Wextra -Wpedantic -Werror -fno-exceptions -fno-rtti -DDOCTEST_CONFIG_NO_EXCEPTIONS -DMOTORS_ALLOWED={active} -Itests -Isrc -isystem host/third_party src/core/*.cpp src/hal/motors.cpp src/hal/recorder.cpp src/hal/recorder_frames.cpp tests/test_tick_timing.cpp state/reviews/P2_tick_timing_review_raw/adversarial.cpp host/motor_gate_main.cpp -o /tmp/sumo-d092-review-{active}'
    argv=['wsl.exe','--cd',linux,'bash','-lc',command]
    start=time.monotonic();result=subprocess.run(argv,capture_output=True)
    (out/f'compile_{active}.txt').write_bytes(result.stdout+result.stderr)
    checks.append(dict(action='compile',active=active,argv=argv,returncode=result.returncode,seconds=time.monotonic()-start))
    if result.returncode: break
    argv=['wsl.exe','--cd',linux,f'/tmp/sumo-d092-review-{active}']
    start=time.monotonic();result=subprocess.run(argv,capture_output=True)
    (out/f'tests_{active}.txt').write_bytes(result.stdout+result.stderr)
    checks.append(dict(action='run',active=active,argv=argv,returncode=result.returncode,seconds=time.monotonic()-start))
    print(result.stdout.decode(errors='replace'),flush=True)
    if result.returncode: break
receipt=dict(source_hashes={p:hashlib.sha256((root/p).read_bytes()).hexdigest() for p in sources},checks=checks)
(out/'test_runs.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(checks,indent=2));raise SystemExit(any(c['returncode']!=0 for c in checks))
