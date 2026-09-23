"""Run the independent native suite with all receipts owned by the reviewer."""
from pathlib import Path
import importlib.util
import sys
import unittest

sys.dont_write_bytecode = True
OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[3]
spec = importlib.util.spec_from_file_location('matrix_native_review_suite',
                                            ROOT/'tests/tooling/test_ui_matrix_native.py')
suite = importlib.util.module_from_spec(spec)
spec.loader.exec_module(suite)
suite.RAW = OUT/'native'
result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromModule(suite))
raise SystemExit(not result.wasSuccessful())
