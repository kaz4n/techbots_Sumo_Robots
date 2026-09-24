"""Account the checked unchanged current default M0 ELF with the retained pristine-pool loader model."""
from pathlib import Path
import hashlib
import importlib.util
import json

out = Path(__file__).resolve().parent
root = out.parents[2]
folder = out / 'app'
model_path = root / 'state/reviews/P2_bridge_dependency_review_raw/elf_review.py'
spec = importlib.util.spec_from_file_location('loader_model', model_path)
model = importlib.util.module_from_spec(spec)
spec.loader.exec_module(model)
image = model.Elf(folder / 'app.ino.elf')
receipt = json.loads((folder / 'receipt/verified.json').read_text())
account = image.account()
expected = [v for k, v in receipt['file_sha256'].items() if k.endswith('/build/app.ino.elf')]
assert expected == [account['sha256']]
account['model_sha256'] = hashlib.sha256(model_path.read_bytes()).hexdigest()
account['conditional_pristine_fit'] = account['conditional_pristine_peak_free_span'] >= 0
account['static_objects'] = [s for s in image.symbols if s['type'] == 1 and s['size'] >= 100]
account['relocation_used_imports'] = sorted({r['name'] for r in image.relocations if not r['symbol_section']})
names = {s['name'] for s in image.symbols}
account['opener_symbols'] = sorted(n for n in names if 'startOpener' in n or 'runOpener' in n)
account['abort_trace_symbols'] = sorted(n for n in names if 'OpenerTiming' in n or 'OpenerAbort' in n)
assert account['opener_symbols'] and not account['abort_trace_symbols']
baselines = {
    'D134_default': root / 'state/analysis/P5_native_compile_raw/app/loader_account.json',
    'D138_MATCH': root / 'state/analysis/P7_readiness_native_raw/app/loader_account.json',
}
account['baseline_comparisons'] = {}
for label, path in baselines.items():
    prior = json.loads(path.read_text())
    account['baseline_comparisons'][label] = {
        key: {'current': account[key], 'baseline': prior[key], 'delta': account[key] - prior[key]}
        for key in ('bytes', 'compiler_payload', 'global_func_object_count',
                    'conditional_pristine_peak_consumption', 'conditional_pristine_peak_free_span')}
(folder / 'loader_account.json').write_text(json.dumps(account, indent=2) + '\n')
print(json.dumps({k: account[k] for k in ('sha256', 'bytes', 'compiler_payload', 'conditional_pristine_peak_consumption', 'conditional_pristine_peak_free_span', 'conditional_pristine_fit')}, indent=2))
