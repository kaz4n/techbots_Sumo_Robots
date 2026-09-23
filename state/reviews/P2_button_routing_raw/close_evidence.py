"""Close D087 reviewer source/test/registry identity without hardware access."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
read = lambda p: json.loads(p.read_text())
hash_file = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
initial = read(OUT / 'target_identity_audit.json')
final = read(OUT / 'target_identity_final_audit.json')
approved = read(OUT / 'inert_approval_final.json')
registry = read(ROOT / 'tools/p0_inert_sources.json')
assert approved['approved_existing_keys'] == registry == final['existing_five_candidate_identities']
assert len(registry) == 5
initial_elfs = {Path(r['path']).name: r['sha256'] for r in initial['elfs']}
final_elfs = {Path(r['path']).name: r['sha256'] for r in final['elfs']}
assert initial_elfs['p2_button_compile.ino.elf'] == final_elfs['p2_button_compile.ino.elf']
focused = read(OUT / 'final_focused_v2/receipt.json')
assert not focused['drift']
assert all(c['returncode'] == 0 and not c['binary_drift'] for c in focused['commands'])
drift = [name for name, digest in focused['frozen_files'].items()
         if hash_file(ROOT / name) != digest]
assert not drift, drift
tooling = read(OUT / 'final_tooling/receipt.json')
assert tooling['status'] == 0 and not tooling['live_drift']
scoped_changes = []
for name, digest in tooling['frozen_files'].items():
    if not name.startswith(('src/', 'tests/', 'host/', 'bench/p2_button_compile/')):
        continue
    current = ROOT / name
    if hash_file(current) == digest:
        continue
    assert name == 'src/core/logframe.h', name
    assert hashlib.sha256(current.read_bytes().replace(b'\n', b'\r\n')).hexdigest() == digest
    scoped_changes.append(name)
assert scoped_changes == ['src/core/logframe.h']
native = [read(p) for p in (OUT / 'final_tooling/tooling_native').glob('command_*.json')]
assert len(native) == 24 and all(r['returncode'] == 0 for r in native)
refusals = [read(p) for p in (OUT / 'final_tooling/tooling_native').glob('upload_refusal_*.json')]
assert len(refusals) == 8
assert all(r['target_calls'] == r['remote_calls'] == r['require_calls'] == 0 for r in refusals)
data = dict(status='PASS_SOFTWARE_SCOPE', current_source_sha256=final['source_sha256'],
            source_files=len(final['source_files']), upload_elf_identical_across_LF_normalization=True,
            initial_elf_hashes=initial_elfs, final_elf_hashes=final_elfs,
            native_exports=final['native_exports'], aeabi_exports=final['math_exports'],
            additional_math_exports=2, all5_registry_approved_and_current=True,
            focused_current_source_drift=drift, earlier_decoder_only_drift=scoped_changes,
            earlier_decoder_drift_verified_exact_CRLF_to_LF=True,
            native_compile_execution_receipts=len(native), native_returncodes_all_zero=True,
            pretransport_upload_refusals=len(refusals),
            scope='Independent source and execution review only; reused separate same-model context; no hardware, MCU, upload or gate')
(OUT / 'final_evidence_audit.json').write_text(json.dumps(data, indent=2) + '\n')
print(json.dumps(data))
