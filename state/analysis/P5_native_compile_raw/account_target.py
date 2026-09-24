"""Apply retained loader model and compare D128 without assuming identity or fit."""
from pathlib import Path
import hashlib
import importlib.util
import json
import sys

root = Path(__file__).resolve().parents[3]
out = Path(__file__).resolve().parent
model_path = root / 'state/reviews/P2_bridge_dependency_review_raw/elf_review.py'
spec = importlib.util.spec_from_file_location('loader_model', model_path)
model = importlib.util.module_from_spec(spec)
spec.loader.exec_module(model)
profile = sys.argv[1]
assert profile in ('app', 'reactive_timing')
folder = out / profile
image = model.Elf(folder / (profile + '.ino.elf'))
account = image.account()
receipt = json.loads((folder / 'receipt/verified.json').read_text())


def one(mapping, suffix):
    values = [value for key, value in mapping.items() if key.endswith(suffix)]
    assert len(values) == 1
    return values[0]


assert account['sha256'] == one(receipt['file_sha256'], '/build/' + profile + '.ino.elf')
account['model_sha256'] = hashlib.sha256(model_path.read_bytes()).hexdigest()
account['conditional_pristine_fit'] = account['conditional_pristine_peak_free_span'] >= 0
account['native_storage_symbols'] = [s for s in image.symbols
    if s['type'] == 1 and ('runtime' in s['name'].lower() or 'native' in s['name'].lower())]
if profile == 'app':
    prior_folder = root / 'state/analysis/P4_reactive_profile_raw/app'
    prior = json.loads((prior_folder / 'receipt/verified.json').read_text())
    old_image = model.Elf(prior_folder / 'app.ino.elf')
    old_account = old_image.account()
    assert old_account['sha256'] == one(prior['file_sha256'], '/build/app.ino.elf')
    account['comparison_to_D128'] = {
        suffix: {'current': one(receipt['file_sha256'], suffix),
                 'prior': one(prior['file_sha256'], suffix),
                 'byte_identical': one(receipt['file_sha256'], suffix) == one(prior['file_sha256'], suffix)}
        for suffix in ('/build/app.ino.elf', '/artifacts/app.ino.elf-zsk.bin',
                       '/firmwares/zephyr-arduino_uno_q_stm32u585xx.elf')}
    account['byte_identical_to_D128'] = all(row['byte_identical']
                                         for row in account['comparison_to_D128'].values())
    account['D128_delta'] = {key: account[key] - old_account[key]
        for key in ('bytes', 'compiler_payload', 'global_func_object_count',
                    'conditional_pristine_peak_consumption', 'conditional_pristine_peak_free_span')}
    current_regions = {row['name']: row for row in account['copied_regions']}
    old_regions = {row['name']: row for row in old_account['copied_regions']}
    account['D128_region_changes'] = {name: {'current': current_regions.get(name), 'prior': old_regions.get(name)}
        for name in sorted(current_regions.keys() | old_regions.keys())
        if current_regions.get(name) != old_regions.get(name)}
    functions, old_functions = image.functions(), old_image.functions()
    account['D128_function_byte_changes'] = [name for name in sorted(functions.keys() | old_functions.keys())
                                           if functions.get(name) != old_functions.get(name)]
else:
    names = {symbol['name'] for symbol in image.symbols}
    account['reactive_symbols'] = sorted(n for n in names if 'routeNormal' in n or 'checkStall' in n)
    account['opener_symbols'] = sorted(n for n in names if 'startOpener' in n or 'runOpener' in n)
    assert any('routeNormal' in n for n in account['reactive_symbols'])
    assert any('checkStall' in n for n in account['reactive_symbols'])
    assert not account['opener_symbols']
    account['loop_hook'] = [s for s in image.symbols if s['name'] == '_Z10__loopHookv']
    assert len(account['loop_hook']) == 1 and account['loop_hook'][0]['bind'] == 1
    account['trace_symbols'] = sorted(n for n in names if 'TimingTrace' in n or 'TimingCandidate' in n)
    assert account['trace_symbols']
(folder / 'loader_account.json').write_text(json.dumps(account, indent=2) + '\n')
print(json.dumps({key: value for key, value in account.items()
    if key not in ('sections', 'copied_regions', 'undefined', 'init', 'fini',
                   'D128_function_byte_changes', 'trace_symbols')}, indent=2))
