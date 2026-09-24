"""Apply the retained loader model to checked final ELFs; no board access."""
from pathlib import Path
import hashlib
import importlib.util
import json
import sys
root = Path(__file__).resolve().parents[3]
out = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('loader_model', root/'state/reviews/P2_bridge_dependency_review_raw/elf_review.py')
model = importlib.util.module_from_spec(spec)
spec.loader.exec_module(model)
profile = sys.argv[1]
folder = out/profile
project = 'reactive_timing' if profile == 'reactive_timing_configured' else profile
image = model.Elf(folder/(project+'.ino.elf'))
account = image.account()
receipt = json.loads((folder/'receipt/verified.json').read_text())
prior = json.loads((root/'state/analysis/P4_reactive_profile_raw/app/receipt/verified.json').read_text())
def one(mapping, suffix):
    values = [value for key,value in mapping.items() if key.endswith(suffix)]
    assert len(values) == 1
    return values[0]
assert account['sha256'] == one(receipt['file_sha256'], '/build/'+project+'.ino.elf')
if profile == 'app':
    account['comparison_to_D128'] = {suffix: one(receipt['file_sha256'], suffix) == one(prior['file_sha256'], suffix)
        for suffix in ('/build/app.ino.elf', '/artifacts/app.ino.elf-zsk.bin', '/firmwares/zephyr-arduino_uno_q_stm32u585xx.elf')}
    account['byte_identical_to_D128'] = all(account['comparison_to_D128'].values())
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
    if project == 'reactive_timing':
        assert account['trace_symbols']
    else:
        assert not account['trace_symbols']
        old = json.loads((root/'state/analysis/P4_reactive_profile_raw/reactive_test/receipt/verified.json').read_text())
        suffixes = ('/build/reactive_test.ino.elf', '/artifacts/reactive_test.ino.elf-zsk.bin',
                    '/firmwares/zephyr-arduino_uno_q_stm32u585xx.elf')
        account['comparison_to_D128'] = {s: one(receipt['file_sha256'],s)==one(old['file_sha256'],s) for s in suffixes}
        account['byte_identical_to_D128'] = all(account['comparison_to_D128'].values())
(folder/'loader_account.json').write_text(json.dumps(account, indent=2)+'\n')
print(json.dumps({key:value for key,value in account.items() if key not in ('sections','copied_regions','undefined','init','fini')}, indent=2))
assert account['conditional_pristine_peak_free_span'] >= 0, 'Loader model does not fit'
