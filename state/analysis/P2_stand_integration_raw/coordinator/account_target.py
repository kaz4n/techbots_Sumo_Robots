"""Apply the retained loader model to checked final ELFs; no board access."""
from pathlib import Path
import hashlib
import importlib.util
import json
import sys
root = Path(__file__).resolve().parents[4]
out = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('loader_model', root/'state/reviews/P2_bridge_dependency_review_raw/elf_review.py')
model = importlib.util.module_from_spec(spec)
spec.loader.exec_module(model)
profile = sys.argv[1]
folder = out/profile
image = model.Elf(folder/(profile+'.ino.elf'))
account = image.account()
receipt = json.loads((folder/'receipt/verified.json').read_text())
prior = json.loads((root/'state/analysis/P2_stand_sequence_raw/coordinator/app_build_receipt/verified.json').read_text())
def one(mapping, suffix):
    values = [value for key,value in mapping.items() if key.endswith(suffix)]
    assert len(values) == 1
    return values[0]
assert account['sha256'] == one(receipt['file_sha256'], '/build/'+profile+'.ino.elf')
if profile == 'app':
    account['comparison_to_D119'] = {suffix: one(receipt['file_sha256'], suffix) == one(prior['file_sha256'], suffix)
        for suffix in ('/build/app.ino.elf', '/artifacts/app.ino.elf-zsk.bin', '/firmwares/zephyr-arduino_uno_q_stm32u585xx.elf')}
    assert all(account['comparison_to_D119'].values()), account['comparison_to_D119']
else:
    names = {symbol['name'] for symbol in image.symbols}
    account['stand_symbols'] = sorted(n for n in names if 'routeStand' in n or 'stand_sequence' in n)
    account['ordinary_route_symbols'] = sorted(n for n in names if 'routeNormal' in n or 'checkStall' in n)
    assert account['stand_symbols'] and not account['ordinary_route_symbols']
    account['loop_hook'] = [s for s in image.symbols if s['name'] == '_Z10__loopHookv']
    assert len(account['loop_hook']) == 1 and account['loop_hook'][0]['bind'] == 1
(folder/'loader_account.json').write_text(json.dumps(account, indent=2)+'\n')
print(json.dumps({key:value for key,value in account.items() if key not in ('sections','copied_regions','undefined','init','fini')}, indent=2))
assert account['conditional_pristine_peak_free_span'] >= 0, 'Loader model does not fit'
