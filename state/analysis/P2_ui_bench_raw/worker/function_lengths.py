"""Review physical function lengths in the three owned implementation files."""
from pathlib import Path
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[4]
RAW = Path(__file__).resolve().parent
files = ['bench/ui/src/ui_bench.cpp', 'bench/ui/src/ui_bench_native.cpp', 'bench/ui/ui.ino']
rows = []
for name in files:
    lines = (ROOT / name).read_text().splitlines()
    active = None
    depth = 0
    for number, line in enumerate(lines, 1):
        if active is None and not line.startswith((' ', '\t', '//', '#', 'namespace', 'static_assert')):
            if '(' in line and '{' in line:
                active = {'file': name, 'signature': line.split('{')[0].strip(), 'first_line': number}
                depth = 0
        if active is not None:
            # These owned functions contain no braces in strings/comments.
            body = line.split('//')[0]
            depth += body.count('{') - body.count('}')
            if depth == 0:
                active['last_line'] = number
                active['lines'] = number - active['first_line'] + 1
                rows.append(active)
                active = None
    assert active is None, name
report = {'scope': 'Source review of every top-level function in the three owned TUs',
    'function_count': len(rows), 'maximum_lines': max(row['lines'] for row in rows),
    'all_under_60': all(row['lines'] < 60 for row in rows), 'functions': rows,
    'source_hashes': {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in files}}
destination = RAW / 'first_function_lengths.json'
assert not destination.exists(), 'Retain prior function review.'
destination.write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps({key: report[key] for key in ('function_count', 'maximum_lines', 'all_under_60')}))
raise SystemExit(not report['all_under_60'])
