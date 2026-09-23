"""Bind the completed D114 capture review to exact tested source and receipts."""
import ast
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[4]
OUT=Path(__file__).resolve().parent
sha=lambda data:hashlib.sha256(data).hexdigest()
pins={
    'tools/ui_adc_capture.py':'f4b3db265bdf2d5a5fdada19ed9f51a44304d9ba5da8be78e598365afa2c4444',
    'tools/p0_capture.py':'885c4e4206aea4ac9e03c4e92e48258db2a0ae302ff83a86430e6913afeeb57c',
    'tools/p0_mem_read.cfg':'89d16a28a1489c23ec743be55ade39824f9ca5213b02b20ef4785079122e4339',
    'tests/tooling/test_ui_adc_capture.py':'02b14721b6cf7805a3b854759bbf49c39b761031a22a20de0fbfad59e720b17d',
    'state/analysis/P2_ui_adc_capture_contract.md':'0e8ead402ac3ddd247a986790d793d4126141d7d283e38665e6fce411c51b689',
}
for name,expected in pins.items(): assert sha((ROOT/name).read_bytes())==expected,name
private=OUT/'private_1790201890768352679.json'
record=json.loads(private.read_text())
assert record['returncode']==0 and 'Ran 42 tests' in record['stderr'] and record['stderr'].endswith('OK\n')
for name in ('tools/ui_adc_capture.py','tools/p0_capture.py','tools/p0_mem_read.cfg','tests/tooling/test_ui_adc_capture.py'):
    assert record['copied_sha256'][name]==pins[name]
tree=ast.parse((ROOT/'tools/ui_adc_capture.py').read_text())
functions=[node for node in ast.walk(tree) if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef))]
assert max(node.end_lineno-node.lineno+1 for node in functions)<60
result=dict(verdict='PASS_SCOPED_D114_PINNED_CAPTURE_SOURCE_AND_TESTS',pins=pins,
    reviewer='Reused separate same-model context; did not author capture source or test oracles',
    source_sha256='396bcc45fbaf30d38b170bf0c0063c555d5e88cdad512829b86a52ffede18642',
    elf_sha256='76e23fe03631d5cc2144578d35ca78b9bafd44158e0d18b2ab026922e4c9d05b',
    zsk_sha256='567fb90da6965cf74efc5ac2221e543d6d2150e3bf70ddae3e2346e6646c7fb9',
    artifact_dir='/home/arduino/sumox26-capture-input/ui_adc_probe_396bcc45fbaf30d38b170bf0c0063c555d5e88cdad512829b86a52ffede18642',
    maximum_read_plan=dict(reads=22,bytes=588016,commands=26,extension_nodes=3),
    private_tests=dict(methods=42,failures=0,errors=0,skips=0,receipt=private.name,sha256=sha(private.read_bytes())),
    source_findings=[],fixture_corrections='Reviewed exact amendments; original frozen tests and failed runs preserved; no capture production edits',
    limits=['No actual board/MCU/readout operation by reviewer','Separate upload guard/run record/final bound approval remain required',
            'Measured collection and native admission are unproved until actual guarded run',
            'No physical acceptance, calibrated time, SC-AJ closure or human phase-gate claim'])
(OUT/'final_review.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'verdict':result['verdict'],'final_review_sha256':sha((OUT/'final_review.json').read_bytes())}))
