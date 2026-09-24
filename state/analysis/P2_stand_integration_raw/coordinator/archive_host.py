"""Preserve CTest evidence before WSL's transient memory filesystem is lost."""
from pathlib import Path
import shutil
import sys
import time
profile = sys.argv[1]
assert profile in ('normal', 'sanitize')
base = Path('/dev/shm/sumox_d120_'+profile)
out = Path(__file__).resolve().parent/(profile+'_build')
out.mkdir(exist_ok=True)
for name in ('sumox26_tests.dir','motor_gate_enabled_tests.dir',
             'stand_integration_m0_tests.dir','stand_integration_m1_tests.dir'):
    for file in ('flags.make','link.txt'):
        shutil.copy2(base/'CMakeFiles'/name/file, out/(name+'.'+file))
shutil.copy2(base/'CMakeCache.txt', out/'CMakeCache.txt')
log = base/'Testing/Temporary/LastTest.log'
for _ in range(900):
    if log.is_file() and 'End testing:' in log.read_text():
        shutil.copy2(log, out/'LastTest.log')
        print(log.read_text(), flush=True)
        break
    time.sleep(1)
else:
    raise RuntimeError('Timed out awaiting completed CTest log')
