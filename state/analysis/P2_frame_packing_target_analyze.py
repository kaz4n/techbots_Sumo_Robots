# Audit D102 target layout and loader fit against preserved D101 source evidence.
# Reuse the D101 pure audit routines without executing or editing its entry script.
# Compare actual ELF sections, retained paths, target DWARF and complete allocations.
import ast
import hashlib
import json
from pathlib import Path
import re
import struct
import sys

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'state/analysis/P2_frame_packing_raw'
REVIEW = ROOT / 'state/reviews/P2_bridge_dependency_review_raw'
sys.path.insert(0, str(REVIEW))
from elf_review import Elf

prior_path = ROOT / 'state/analysis/P2_app_dump_raw/target_analyze.py'
tree = ast.parse(prior_path.read_text())
functions = [node for node in tree.body if isinstance(node, ast.FunctionDef)]
scope = dict(ROOT=ROOT, OUT=OUT, REVIEW=REVIEW, Path=Path, json=json, ast=ast,
             hashlib=hashlib, re=re, struct=struct, Elf=Elf)
exec(compile(ast.Module(body=functions, type_ignores=[]), str(prior_path), 'exec'), scope)
scope['prior_function'] = scope['load_function']('verify_elfs.py', 'function')
scope['relocations'] = scope['load_function']('compare_objects.py', 'relocations')
old_base = ROOT / 'state/analysis/P2_app_acceptance_raw/bench-default'
scope['baseline'] = json.loads((old_base / 'audit.json').read_text())
scope['baseline_elf'] = Elf(old_base / 'app.ino.elf')

old = ROOT / 'state/analysis/P2_app_dump_raw/target_83600858_match-immediate'
old_elf = Elf(old / 'app.ino.elf')
old_audit = json.loads((old / 'audit.json').read_text())
old_account = old_elf.account()


def allocation_order(account):
    regions = {row['name']: row for row in account['copied_regions']}
    meta = account['metadata_chunks']
    requests = [('heap bookkeeping', meta['initial_bookkeeping']),
                ('extension', meta['extension']), ('section map', meta['section_map'])]
    # Pinned llext_mem enum/copy order; omitted regions are empty or flash-peeked.
    requests.extend((name, regions[name]['retained_chunk']) for name in
                    ('.text', '.data', '.rodata', '.bss', '.exported_sym', '.init_array', '.fini_array')
                    if name in regions)
    requests.extend([('temporary symbols', meta['global_symbols']), ('export copy', meta['export_copy'])])
    used = 0
    rows = []
    for name, amount in requests:
        before = 262144-used
        assert amount <= before, name
        used += amount
        rows.append(dict(name=name, chunk=amount, preceding_free_span=before,
                         remaining_free_span=262144-used))
    assert used == account['conditional_pristine_peak_consumption']
    return rows


builds = {}
for folder in sorted(OUT.glob('target_3bf0da00_*')):
    if not folder.is_dir() or not (folder / 'audit.json').exists():
        continue
    result = scope['audit_folder'](folder)
    audit = json.loads((folder / 'audit.json').read_text())
    changed_sources = [name for name, digest in audit['source_files'].items()
                       if old_audit['source_files'].get(name) != digest]
    assert changed_sources == ['src/hal/recorder_dump.cpp', 'src/hal/recorder_frames.cpp',
                              'src/hal/recorder_frames.h']
    current = Elf(folder / 'app.ino.elf')
    current_names = {s['name'] for s in current.symbols if s['section_index']}
    frame_read = '_ZNK8recorder11FrameBuffer4readEjRNS_11StoredFrameE'
    assert frame_read in current_names
    assert '_ZNK8recorder11FrameBuffer2atEj' not in current_names
    result['retained_frame_read'] = scope['function'](current, frame_read)
    assert result['owners']['_ZN12_GLOBAL__N_17runtimeE'] == 166216
    source_report = dict(changed_sources_from_d101=changed_sources,
                         actual_framebuffer_bytes=126300, actual_framebuffer_alignment=4)
    result['d102'] = source_report
    result['allocation_order'] = allocation_order(result['memory']['account'])
    if result['mode'] == 'match-immediate':
        current_account = result['memory']['account']
        result['d101_comparison'] = dict(
            source='836008588522b81c0f94435725a9b93cbd3cf826b871caf960285797b17b9db0',
            previous_elf_sha256=old_account['sha256'],
            compiler_payload_saved=old_account['compiler_payload']-current_account['compiler_payload'],
            conditional_peak_saved=old_account['conditional_pristine_peak_consumption']-
                                   current_account['conditional_pristine_peak_consumption'],
            previous_regions=old_account['copied_regions'], current_regions=current_account['copied_regions'],
            previous_metadata=old_account['metadata_chunks'], current_metadata=current_account['metadata_chunks'])
        # This comparison isolates D102 because both builds are MATCH Immediate.
        scope['baseline'] = old_audit
        result['d101_same_mode_objects'] = scope['compare_objects'](audit)
        scope['baseline'] = json.loads((old_base / 'audit.json').read_text())
    assert result['memory']['temporary_symbols_fit']
    assert result['memory']['complete_peak_deficit'] == 0
    builds[folder.name] = result

abi_dir = OUT / 'target_abi_retry'
abi_run = json.loads((abi_dir / 'receipt.json').read_text())
assert abi_run['returncode'] == 0 and not (abi_dir / 'stderr.txt').read_text()
abi_text = (abi_dir / 'stdout.txt').read_text()
values = [int(value) for value in re.findall(r'^\$\d+ = (\d+)$', abi_text, re.M)]
assert values == [126300, 4, 26, 1, 159200, 8, 166216, 8]
abi = dict(FrameBuffer=dict(size=values[0], alignment=values[1]),
           StoredFrame=dict(size=values[2], alignment=values[3]),
           AttemptRecorder=dict(size=values[4], alignment=values[5]),
           Runtime=dict(size=values[6], alignment=values[7]),
           evidence='Actual completed-target debug ELF, offline GDB type expressions; no new compilation',
           receipt_sha256=hashlib.sha256((abi_dir / 'receipt.json').read_bytes()).hexdigest())
sources = json.loads((ROOT / 'state/analysis/P2_memory_validation_raw/source_receipt.json').read_text())
for source in sources:
    assert hashlib.sha256((ROOT / source['path']).read_bytes()).hexdigest() == source['sha256']
report = dict(scope='Frozen source/ELF/target ABI and conditional loader fit only; not actual load/RAM/WCET',
              reused_analyzer_sha256=hashlib.sha256(prior_path.read_bytes()).hexdigest(),
              pinned_source_receipts=sources, target_abi=abi, builds=builds)
(OUT / 'target_summary.json').write_text(json.dumps(report, indent=2)+'\n')
print(json.dumps({name: dict(payload=r['memory']['account']['compiler_payload'],
    peak=r['memory']['account']['conditional_pristine_peak_consumption'],
    largest=r['memory']['conditional_largest_after_peak'],
    runtime=r['owners']['_ZN12_GLOBAL__N_17runtimeE']) for name, r in builds.items()}, indent=2))
