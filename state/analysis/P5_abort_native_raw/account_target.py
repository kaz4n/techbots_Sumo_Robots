"""Account one checked D135 ELF with the retained pristine-pool loader model."""
from pathlib import Path
import hashlib
import importlib.util
import json

out = Path(__file__).resolve().parent
root = out.parents[2]
folder = out / 'opener_timing'
model_path = root / 'state/reviews/P2_bridge_dependency_review_raw/elf_review.py'
spec = importlib.util.spec_from_file_location('loader_model', model_path)
model = importlib.util.module_from_spec(spec)
spec.loader.exec_module(model)
image = model.Elf(folder / 'opener_timing.ino.elf')
receipt = json.loads((folder / 'receipt/verified.json').read_text())
account = image.account()
expected = [v for k, v in receipt['file_sha256'].items() if k.endswith('/build/opener_timing.ino.elf')]
assert expected == [account['sha256']]
account['model_sha256'] = hashlib.sha256(model_path.read_bytes()).hexdigest()
account['conditional_pristine_fit'] = account['conditional_pristine_peak_free_span'] >= 0
account['static_objects'] = [s for s in image.symbols if s['type'] == 1 and s['size'] >= 100]
account['relocation_used_imports'] = sorted({r['name'] for r in image.relocations if not r['symbol_section']})
names = {s['name'] for s in image.symbols}
account['opener_symbols'] = sorted(n for n in names if 'startOpener' in n or 'runOpener' in n)
account['abort_trace_symbols'] = sorted(n for n in names if 'OpenerTiming' in n or 'OpenerAbort' in n)
assert account['opener_symbols'] and account['abort_trace_symbols']
prior = json.loads((root / 'state/analysis/P5_native_compile_raw/app/loader_account.json').read_text())
account['D134_default_comparison'] = {key: {'current': account[key], 'D134_default': prior[key],
    'delta': account[key] - prior[key]} for key in ('bytes', 'compiler_payload',
    'global_func_object_count', 'conditional_pristine_peak_consumption', 'conditional_pristine_peak_free_span')}
(folder / 'loader_account.json').write_text(json.dumps(account, indent=2) + '\n')
print(json.dumps({k: v for k, v in account.items() if k not in
    ('sections', 'copied_regions', 'undefined', 'init', 'fini', 'static_objects')}, indent=2))
