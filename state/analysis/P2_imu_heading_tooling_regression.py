"""Run affected staging/config/upload safeguards after adding the pure D082 HAL."""
import json
import os
from pathlib import Path
import sys
import unittest

root = Path(__file__).resolve().parents[2]
os.chdir(root)
suite = unittest.defaultTestLoader.discover(str(root / 'tests/tooling'), pattern='test_*.py')
modules = {'test_tools', 'test_adb_transport', 'test_preflight',
           'test_staged_core', 'test_motor_gate_probe'}

def cases(group):
    for test in group:
        if isinstance(test, unittest.TestSuite):
            yield from cases(test)
        else:
            yield test

selected = [t for t in cases(suite)
            if t.id().split('.')[0] in modules or t.id().startswith('test_p0_')]
receipt = root / 'state/analysis/P2_imu_heading_raw/tooling_selection.json'
receipt.write_text(json.dumps({
    'scope': 'Existing staging/config/inert-probe/upload/preflight safeguards affected by new project sources. New D082 numerical/probe methods run separately. Existing native drivers, recorder and transport implementations are unchanged and passed the prior D081 complete regression.',
    'count': len(selected), 'methods': [t.id() for t in selected]
}, indent=2) + '\n')
print('Selected existing tooling methods:', len(selected), flush=True)
result = unittest.TextTestRunner(verbosity=2).run(unittest.TestSuite(selected))
sys.exit(0 if result.wasSuccessful() else 1)
