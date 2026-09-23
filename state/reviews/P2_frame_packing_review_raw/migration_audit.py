"""List every existing predicate migration and protect historical/source scopes."""
from pathlib import Path
import ast
import collections
import difflib
import hashlib
import json
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
RAW = Path(__file__).resolve().parent
BASE = '0b1013b'
def old(path):
    return subprocess.check_output(['git', 'show', f'{BASE}:{path}'], cwd=ROOT)
def current(path):
    return (ROOT / path).read_bytes()
def macros(text):
    found = []
    for match in re.finditer(r'\b(?:CHECK(?:_FALSE)?|REQUIRE(?:_FALSE)?|static_assert|TEST_CASE)\s*\(', text):
        start = match.start(); index = match.end(); depth = 1; quote = None
        while depth:
            ch = text[index]; index += 1
            if quote:
                if ch == '\\': index += 1
                elif ch == quote: quote = None
            elif ch in ('"', "'"): quote = ch
            elif ch == '(': depth += 1
            elif ch == ')': depth -= 1
        found.append(re.sub(r'\s+', ' ', text[start:index]))
    return found
paths = ['tests/test_recorder_frames.cpp', 'tests/test_attempt_recorder.cpp',
         'tests/test_recorder_csv.cpp', 'tests/test_recorder_rate.cpp', 'tests/test_tick_timing.cpp',
         'tests/fixtures/app_dump/roundtrip.cc', 'tests/tooling/recorder_bench_cases.cc']
records = {}
for path in paths:
    before = old(path).decode(); after = current(path).decode()
    before_macros = macros(before); after_macros = macros(after)
    before_cases = [m for m in before_macros if m.startswith('TEST_CASE')]
    after_cases = [m for m in after_macros if m.startswith('TEST_CASE')]
    normalized_cases = [m.replace('and expanded 26 byte records', 'and 26 byte records') for m in after_cases]
    assert before_cases == normalized_cases, path
    records[path] = dict(before_assertions=len(before_macros)-len(before_cases),
                         after_assertions=len(after_macros)-len(after_cases),
                         test_case_names_preserved_except_expanded_DTO_label=len(before_cases),
                         predicates_diff=list(difflib.unified_diff(before_macros, after_macros)),
                         complete_diff=list(difflib.unified_diff(before.splitlines(), after.splitlines())))
protected = subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', BASE,
    'src/config.h', 'src/core', 'tests/locked', 'tests/candidates/recorder25.cc',
    'src/hal/recorder_csv.cpp', 'src/hal/recorder_csv.h', 'src/hal/recorder.cpp',
    'src/hal/recorder.h', 'src/hal/dump_uart_unoq.cpp', 'src/hal/dump_uart_unoq.h'], cwd=ROOT).decode().splitlines()
for path in protected:
    assert old(path).replace(b'\r\n', b'\n') == current(path).replace(b'\r\n', b'\n'), ('Protected source changed', path)
assert not subprocess.check_output(['git', 'diff', '--name-only', BASE, '--', *protected], cwd=ROOT)
py_path = 'tests/tooling/test_recorder_memory.py'
before = ast.parse(old(py_path)); after = ast.parse(current(py_path))
methods = lambda tree: {node.name: ast.dump(node, include_attributes=False)
                        for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)}
assert methods(before) == methods(after)
result = dict(baseline=BASE, protected_git_unchanged_files=len(protected),
              protected_crlf_worktree_files=[p for p in protected if old(p) != current(p)],
              protected_hashes={p: hashlib.sha256(current(p)).hexdigest() for p in protected},
              unchanged_python_function_asts=len(methods(before)), migrations=records)
label = sys.argv[1] if len(sys.argv) > 1 else 'initial'
assert label.isidentifier()
target = RAW / ('migration_audit.json' if label == 'initial' else 'migration_audit_' + label + '.json')
assert not target.exists()
target.write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps({p: {k: v for k, v in r.items() if k != 'complete_diff'} for p, r in records.items()}, indent=2))
