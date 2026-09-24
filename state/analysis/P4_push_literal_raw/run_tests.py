"""Run source-bound D132 tooling checks with small receipts and no board access."""
from pathlib import Path
from datetime import datetime, timezone
import contextlib
import hashlib
import json
import sys
import unittest

root = Path(__file__).resolve().parents[3]
out = Path(__file__).resolve().parent
sys.path[:0] = [str(root), str(root / 'tests/tooling')]
group = sys.argv[1]
assert group in ('admission', 'regression')
assert not (out / (group + '.json')).exists(), 'Preserve prior results'
freeze = json.loads((out / 'freeze.json').read_text())
for name, expected in freeze.items():
    assert hashlib.sha256((root / name).read_bytes()).hexdigest() == expected, name
names = ['test_push_literal_admission']
if group == 'regression':
    names = ['test_tools', 'test_adb_transport', 'test_ui_adc_probe_policy',
             'test_reactive_timing', 'test_reactive_profile_policy',
             'test_stop_trial_profile', 'test_turn_trial_profile',
             'test_drive_test_profile', 'test_motor_direction_policy',
             'test_app_build_policy', 'test_opp_view_policy',
             'test_runtime_inert_policy', 'test_motor_stand_inhibit_policy',
             'test_recorder_transport_policy', 'test_qtr_raw_policy',
             'test_imu_heading_bench_policy', 'test_ui_bench_policy',
             'test_vbat_policy', 'test_recorder_upload', 'test_ui_adc_run',
             'test_app_default_run', 'test_staged_core', 'test_runtime_config_registry']
    from tests.tooling import test_runtime_config_registry
    test_runtime_config_registry.RAW = out
record = {'group': group, 'modules': names,
          'start_utc': datetime.now(timezone.utc).isoformat(),
          'freeze_sha256': hashlib.sha256((out / 'freeze.json').read_bytes()).hexdigest()}
with (out / (group + '.txt')).open('w') as log:
    with contextlib.redirect_stdout(log), contextlib.redirect_stderr(log):
        suite = unittest.defaultTestLoader.loadTestsFromNames(
            ['tests.tooling.' + name for name in names])
        result = unittest.TextTestRunner(stream=log, verbosity=2).run(suite)
code = 0 if result.wasSuccessful() else 1
record.update(returncode=code, tests_run=result.testsRun,
              failures=len(result.failures), errors=len(result.errors),
              skipped=len(result.skipped), end_utc=datetime.now(timezone.utc).isoformat())
(out / (group + '.json')).write_text(json.dumps(record, indent=2) + '\n')
print((out / (group + '.txt')).read_text()[-4500:])
sys.exit(code)
