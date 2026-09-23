"""Static-only D115 diff and identity proof; imports no production modules."""
from pathlib import Path
import ast
import hashlib
import json
import subprocess
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[4]
RAW = ROOT / 'state/analysis/P2_motor_stand_inhibit_raw/reviewer'


def sha(blob):
    return hashlib.sha256(blob).hexdigest()


def original(name):
    return subprocess.check_output(['git', 'show', 'HEAD:' + name], cwd=ROOT)


freeze = json.loads((RAW.parent / 'coordinator/first_source_freeze.json').read_bytes())
for name, expected in freeze['files'].items():
    assert sha((ROOT / name).read_bytes()) == expected
comparisons = {}
for name in ['tools/board_tool.py', 'tools/app_build_policy.py', 'host/CMakeLists.txt']:
    old, new = original(name), (ROOT / name).read_bytes()
    before, after = old.decode().replace('\r\n', '\n'), new.decode().replace('\r\n', '\n')
    if name.endswith('board_tool.py'):
        restored = after.replace("'bench/ui', 'bench/ui_adc_probe', 'bench/motor_stand')", "'bench/ui', 'bench/ui_adc_probe')")
        restored = restored.replace("(probe or args.sketch in ('bench/ui_adc_probe', 'bench/motor_stand'))", "(probe or args.sketch == 'bench/ui_adc_probe')")
        restored = restored.replace("'bench/ui': 'ui.ino', 'bench/ui_adc_probe': 'ui_adc_probe.ino',\n                   'bench/motor_stand': 'motor_stand.ino'}", "'bench/ui': 'ui.ino', 'bench/ui_adc_probe': 'ui_adc_probe.ino'}")
    elif name.endswith('app_build_policy.py'):
        restored = after.replace(", 'motor_stand.ino'", '')
    else:
        restored = after.replace('  "${CMAKE_CURRENT_SOURCE_DIR}/../bench/motor_stand/src/motor_stand.cpp"\n', '')
    assert restored == before, name
    comparisons[name] = dict(exact_scoped_reversal_with_newlines_normalized=True,
        prior_sha256=sha(old), current_sha256=sha(new), prior_crlf=old.count(b'\r\n'), current_crlf=new.count(b'\r\n'))
    if name.endswith('.py'):
        ast.parse(after)
manifest = (ROOT / 'tools/p0_inert_sources.json').read_bytes()
assert sha(manifest) == 'a1587931afa5f817bf8b93054f384918dc8cd36d4fb71c8f7b083d76e6128802'
assert json.loads(manifest) == json.loads(original('tools/p0_inert_sources.json'))
assert 'bench/motor_stand' not in json.loads(manifest)
implementation = json.loads((RAW.parent / 'implementer/first_source_freeze.json').read_bytes())
for name, meta in implementation['files'].items():
    assert sha((ROOT / name).read_bytes()) == meta['sha256']
collector = ROOT / 'state/analysis/P2_motor_stand_inhibit_target_collect.py'
ast.parse(collector.read_text())
result = dict(verdict='PASS_SCOPED_STATIC_D115_TOOLING_AND_HOST_LINK_REVIEW',
    utc=datetime.now(timezone.utc).isoformat(),
    baseline_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT).decode().strip(),
    files=freeze['files'], comparisons=comparisons,
    manifest_sha256=sha(manifest), manifest_unchanged_from_reviewed_D114_bytes=True,
    manifest_git_comparison='Parsed entries equal; committed LF and existing working CRLF are explicitly distinguished.',
    five_implementation_files_still_first_freeze=True, collector_sha256=sha(collector.read_bytes()),
    collector_source_review='Linux source/artifact reads and offline readelf/nm/objdump/GDB only; no upload/reset/MCU attachment. Exact95 source files and receipt binding; execution pending.',
    tests_executed=False, production_modules_imported=False, board_actions=False, findings=[],
    initial_static_harness_failure=dict(error='AssertionError', check='Working manifest raw bytes equal git HEAD bytes',
        cause='Existing CRLF working manifest versus LF git blob; both parse identically. Current manifest is byte-identical to actual D114 approved a1587931.',
        disposition='No production change. Final static proof uses exact previously reviewed byte hash plus original parsed entries.'),
    pending=['Independent executable test freeze and results', 'Exact default target retained-path/import/startup/ABI and ordered loader-fit audit'])
(RAW / 'tooling_preflight.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps({key: result[key] for key in ('verdict', 'collector_sha256', 'tests_executed', 'findings')}, indent=2))
