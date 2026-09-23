"""Run the stable existing tooling suite while independent B3 tests finalize."""
import sys
import unittest
from pathlib import Path

root = Path(__file__).resolve().parents[3]
folder = root / 'tests/tooling'
sys.path.insert(0, str(folder))
suite = unittest.TestSuite()
for path in sorted(folder.glob('test_*.py')):
    if path.name != 'test_imu_bus_unoq.py':
        suite.addTests(unittest.defaultTestLoader.loadTestsFromName(path.stem))
print('Separate suite: new test_imu_bus_unoq is run independently, not waived.', flush=True)
result = unittest.TextTestRunner(verbosity=2).run(suite)
raise SystemExit(0 if result.wasSuccessful() else 1)
