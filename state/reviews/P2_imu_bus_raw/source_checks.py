"""Records bounded production functions and protected-source scope checks."""
from pathlib import Path
import hashlib,json,re,subprocess
ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent
paths=[ROOT/'src/hal/imu_bus_unoq.cpp',ROOT/'src/hal/imu_bus_unoq.h',
       ROOT/'bench/p2_imu_bus_compile/p2_imu_bus_compile.ino',
       ROOT/'bench/p2_imu_bus_compile/src/imu_bus_probe.cpp',
       ROOT/'bench/p2_imu_bus_compile/src/imu_bus_probe.h']
functions=[]
for path in paths:
    text=path.read_text()
    for match in re.finditer(r'^\w[\w :<>*&]*\b([A-Za-z_]\w*(?:::\w+)*)\([^;{}]*\)\s*\{',text,re.M):
        end,depth=match.end(),1
        while depth:
            depth+=(text[end]=='{')-(text[end]=='}');end+=1
        functions.append(dict(path=path.relative_to(ROOT).as_posix(),name=match.group(1),
            line=text[:match.start()].count('\n')+1,lines=text[match.start():end].count('\n')+1))
protected=subprocess.check_output(['git','diff','6911b25','--','src/core','src/app','tests/locked','tools/board_tool.py'],cwd=ROOT).decode()
report=dict(functions=functions,all_functions_under_60=all(f['lines']<60 for f in functions),
    files={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},
    protected_unchanged=protected=='',protected_diff=protected,
    manual_observations=['No motor EN or PWM access, motion command acceptance or app integration',
      'Native clock dispatch audited finite; no Wire semaphore transfer or IRQ mutation',
      'Static boot claim and Bus constructors initialize memory only; no new allocator, blocking API or unbounded loop',
      'Every polling loop bounded; one Operation.polls shared across transfer phases and bytes',
      'Private staging only publishes after checked complete request; terminal returns zero bytes',
      'Per-pin lock guards; no clock reset, GPIO pulse recovery, retry, STOP synthesis or cleanup reenable',
      'Observation timestamps and counters are software evidence, not physical time or clock lock'])
(OUT/'source_checks.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(dict(functions=len(functions),maximum_lines=max(f['lines'] for f in functions),
    all_functions_under_60=report['all_functions_under_60'],protected_unchanged=report['protected_unchanged'])))
assert report['all_functions_under_60'] and report['protected_unchanged']
