"""D117 read-only source/collector checks; does not import production modules."""
import ast
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
BASE = '993afdd0'
sha = lambda b: hashlib.sha256(b).hexdigest()


def old(path):
    return subprocess.run(['git', 'show', BASE + ':' + path], cwd=ROOT,
                          capture_output=True, check=True).stdout.decode()


def body(source, signature):
    start = source.index('{', source.index(signature))
    depth = 1
    end = start + 1
    while depth:
        depth += (source[end] == '{') - (source[end] == '}')
        end += 1
    return source[start + 1:end - 1]


def tokens(source):
    source = re.sub(r'//[^\n]*|/\*.*?\*/', '', source, flags=re.S)
    return re.findall(r'\w+|[^\s\w]', source)


freeze = json.loads((ROOT / 'state/analysis/P2_dump_fifo_raw/implementer/first_source_freeze.json').read_text())
identities = {}
for name, declared in freeze['files'].items():
    raw = (ROOT / name).read_bytes()
    identities[name] = {'sha256': sha(raw), 'bytes': len(raw), 'frozen_match': sha(raw) == declared['sha256']}
    assert identities[name]['frozen_match']
changed = subprocess.run(['git', 'diff', '--name-only', BASE, '--', 'src', 'bench', 'host', 'tools'],
                         cwd=ROOT, capture_output=True, check=True).stdout.decode().splitlines()
assert set(changed) == set(identities)
path = 'src/hal/dump_uart_unoq.cpp'
prior, current = old(path), (ROOT / path).read_text()
unchanged = {}
for name in ('sampleReady', 'ready', 'port', 'write', 'cancel', 'prepare', 'withinDeadline', 'advance', 'transmit', 'fail'):
    marker = 'UnoQDumpPort::' + name + '('
    unchanged[name] = tokens(body(prior, marker)) == tokens(body(current, marker))
    assert unchanged[name]
for name in ('deviceMetadata', 'metadata', 'clocksAvailable', 'nominalClock', 'clockRegister', 'padsOwned', 'irqIdle'):
    marker = name + '('
    unchanged[name] = tokens(body(prior, marker)) == tokens(body(current, marker))
    assert unchanged[name]
expanded_abort = body(current, 'UnoQDumpPort::abort(').replace('poison();', body(current, 'UnoQDumpPort::poison('))
abort_equal = tokens(expanded_abort) == tokens(body(prior, 'UnoQDumpPort::abort('))
assert abort_equal
sketches = {}
for path, owner in (('src/app/app.ino', 'dump_port'), ('bench/recorder/recorder.ino', 'native_dump')):
    current_sketch = (ROOT / path).read_text()
    restored = current_sketch.replace(owner + '{recorder::dump::Buffering::FIFO8};', owner + ';')
    sketches[path] = tokens(restored) == tokens(old(path))
    assert sketches[path]
collector = ROOT / 'state/analysis/P2_dump_fifo_target_collect.py'
tree = ast.parse(collector.read_text())
embedded = next(ast.literal_eval(n.value) for n in tree.body if isinstance(n, ast.Assign)
                and any(isinstance(t, ast.Name) and t.id == 'ABI_PROGRAM' for t in n.targets))
ast.parse(embedded)
compile(embedded, '<D117 offline ABI literal>', 'exec')
result = dict(utc=datetime.now(timezone.utc).isoformat(), verdict='PASS_STATIC_ONLY_TESTS_AND_TARGETS_PENDING',
              scope='Read-only source and AST checks; no implementation/test execution, import or board access',
              baseline=BASE, files=identities, changed_production_paths=changed,
              identical_function_tokens=unchanged, abort_after_poison_inline_identical=abort_equal,
              sketches_only_explicit_constructor=sketches,
              collector_sha256=sha(collector.read_bytes()), collector_and_literal_syntax='PASS',
              contract_sha256=sha((ROOT / freeze['contract']['path']).read_bytes()))
(OUT / 'source_static.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
