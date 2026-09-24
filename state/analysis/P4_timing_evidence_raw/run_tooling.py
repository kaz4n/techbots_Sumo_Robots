"""Record D129 controlled tooling tests; never touch actual board transport."""
from pathlib import Path
from datetime import datetime, timezone
import json
import os
import subprocess
import sys
root = Path(__file__).resolve().parents[3]
out = Path(__file__).resolve().parent
names = ['test_reactive_timing', 'test_reactive_profile_policy',
         'test_stop_trial_profile', 'test_turn_trial_profile', 'test_drive_test_profile',
         'test_motor_direction_policy', 'test_app_build_policy', 'test_opp_view_policy',
         'test_runtime_inert_policy', 'test_motor_stand_inhibit_policy',
         'test_recorder_transport_policy']
argv = [sys.executable, '-m', 'unittest', '-v'] + ['tests.tooling.' + n for n in names]
env = os.environ.copy()
env['PYTHONPATH'] = str(root/'tests/tooling')
record = {'argv': argv, 'start_utc': datetime.now(timezone.utc).isoformat()}
with (out/'tooling.txt').open('wb') as log:
    result = subprocess.run(argv, cwd=root, env=env, stdout=log, stderr=subprocess.STDOUT)
record.update(returncode=result.returncode, end_utc=datetime.now(timezone.utc).isoformat())
(out/'tooling.json').write_text(json.dumps(record, indent=2)+'\n')
print((out/'tooling.txt').read_text(errors='replace')[-2200:])
sys.exit(result.returncode)
