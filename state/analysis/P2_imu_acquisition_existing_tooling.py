"""Run every existing tooling method, leaving D081's seven to its separate run."""
import os
from pathlib import Path
import sys
import unittest

root = Path(__file__).resolve().parents[2]
os.chdir(root)
raw = root / 'state/analysis/P2_imu_acquisition_raw'
os.environ['SUMO_NATIVE_RECEIPT_DIR'] = str(raw / 'existing_native_bus')
os.environ['SUMO_IMU_SETUP_RECEIPT_DIR'] = str(raw / 'existing_imu_setup')
suite = unittest.defaultTestLoader.discover(str(root / 'tests/tooling'), pattern='test_*.py')

def cases(group):
    for test in group:
        if isinstance(test, unittest.TestSuite):
            yield from cases(test)
        else:
            yield test

existing = unittest.TestSuite(t for t in cases(suite)
                             if not t.id().startswith('test_imu_acquisition.'))
print('Existing tooling methods:', existing.countTestCases(), flush=True)
result = unittest.TextTestRunner(verbosity=2).run(existing)
sys.exit(0 if result.wasSuccessful() else 1)
