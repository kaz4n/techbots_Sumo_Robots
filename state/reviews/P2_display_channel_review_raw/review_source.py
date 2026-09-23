"""Bind D108's authorized literal change and unchanged frozen test evidence."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
RAW = ROOT / 'state/analysis/P2_display_channel_raw/author'
def sha(data): return hashlib.sha256(data).hexdigest()
before = (RAW / 'red_ui_display.cpp').read_bytes()
after = (ROOT / 'src/hal/ui_display.cpp').read_bytes()
old = b'{{4,1},{2,1},{6,1},{0,3},{8,3},{2,5},{6,5}}'
new = b'{{2,1},{4,1},{6,1},{0,3},{8,3},{2,5},{6,5}}'
assert before.count(old) == 1 and before.replace(old, new) == after
assert sha(before) == '4b03f677e27f839ae7a0a77ed0a88635f7a2d33c759c3c80c26ea6cb2e55728b'
assert sha(after) == '9e9d5d9a44d8b0d637f2301d042f7021df890a270995e1806d4d4456dd58c535'
test_before = (RAW / 'test_ui_display_before.cpp').read_bytes()
test_after = (ROOT / 'tests/test_ui_display.cpp').read_bytes()
assert test_before.replace(b'    constexpr unsigned OPP[] = {17,15,19,39,47,67,71};',
    b'    // D108 corrects FL15/FC positions; all other D088 pixels and assertions stay.\n'
    b'    constexpr unsigned OPP[] = {15,17,19,39,47,67,71};') == test_after
freeze = json.loads((RAW / 'freeze.json').read_text())
for row in freeze['files']:
    if row['path'] == 'src/hal/ui_display.cpp': continue
    assert sha((ROOT / row['path']).read_bytes()) == row['sha256'], row['path']
host = json.loads((RAW / 'full_host_source.json').read_text())
for name in ('src/hal/ui_display.cpp', 'tests/test_ui_display.cpp', 'tests/test_display_channels.cpp'):
    assert sha((ROOT / name).read_bytes()) == host[name]
for profile in ('normal', 'san'):
    command = json.loads((RAW / ('full_' + profile + '_test.json')).read_text())
    assert command['returncode'] == 0 and command['stderr'] == ''
    assert '1446 |     1446 passed | 0 failed | 0 skipped' in command['stdout']
    assert '187 |     187 passed | 0 failed | 0 skipped' in command['stdout']
    green = json.loads((RAW / ('green_' + profile + '_run.json')).read_text())
    red = json.loads((RAW / ('red_' + profile + '_run.json')).read_text())
    assert green['returncode'] == 0 and red['returncode'] == 1
    assert green['stderr'] == red['stderr'] == ''
    assert '4104 failed' in red['stdout']
result = dict(verdict='PASS_EXACT_D108_LITERAL_SOURCE_AND_FROZEN_TEST_EVIDENCE',
    renderer_before_sha256=sha(before), renderer_after_sha256=sha(after),
    old_test_before_sha256=sha(test_before), old_test_after_sha256=sha(test_after),
    new_test_sha256=sha((ROOT / 'tests/test_display_channels.cpp').read_bytes()),
    source_change='Only first two coordinate pairs; no mask projection or other production byte change',
    test_change='Only corresponding two positions and comment; all old other bytes identical',
    author_evidence_sha256={p.name: sha(p.read_bytes()) for p in RAW.glob('*.json')},
    limits='Reused same-model context, no physical optical orientation or hardware acceptance. Target/own host review separate.')
(OUT / 'source_review.json').write_text(json.dumps(result, indent=2) + '\n')
print(result['verdict'])
