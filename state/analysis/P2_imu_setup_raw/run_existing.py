"""Run existing tooling, excluding only separately validated D080 setup tests."""
from pathlib import Path
import unittest
loader=unittest.TestLoader()
suite=unittest.TestSuite()
for path in sorted(Path('tests/tooling').glob('test_*.py')):
    if path.name != 'test_imu_setup.py':
        suite.addTests(loader.discover('tests/tooling', pattern=path.name))
result=unittest.TextTestRunner(verbosity=2).run(suite)
raise SystemExit(0 if result.wasSuccessful() else 1)
