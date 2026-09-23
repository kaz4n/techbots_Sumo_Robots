from pathlib import Path
import importlib, unittest, sys, json, hashlib, datetime
root=Path.cwd(); raw=root/'state/reviews/P2_dump_review_raw'
sys.path[:0]=[str(root),str(root/'tests/tooling')]
modules=[importlib.import_module('test_dump_match'),importlib.import_module('test_dump_uart_unoq')]
modules[1].RAW=raw/'native_final'
paths=[root/'tools/dump_match.py',root/'src/hal/dump_uart_unoq.cpp',root/'src/hal/dump_uart_unoq.h',root/'src/hal/loop_hook.cpp',root/'tests/tooling/test_dump_match.py',root/'tests/tooling/test_dump_uart_unoq.py']
paths+=sorted(p for p in (root/'tests/fixtures/dump_uart_native').rglob('*') if p.is_file())
with (raw/'tooling_final_freeze.json').open('x') as f: json.dump({str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},f,indent=2)
suite=unittest.TestSuite(unittest.defaultTestLoader.loadTestsFromModule(module) for module in modules)
started=datetime.datetime.now(datetime.timezone.utc).isoformat()
with (raw/'tooling_final.txt').open('x') as log: result=unittest.TextTestRunner(stream=log,verbosity=2).run(suite)
receipt=dict(start_utc=started,end_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),tests=result.testsRun,errors=len(result.errors),failures=len(result.failures),skipped=len(result.skipped),passed=result.wasSuccessful())
with (raw/'tooling_final.json').open('x') as f:json.dump(receipt,f,indent=2)
print(json.dumps(receipt));sys.exit(not result.wasSuccessful())
