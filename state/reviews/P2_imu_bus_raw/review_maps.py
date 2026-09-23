"""Reproduces inert maps from bytes without staging or changing any upload policy."""
from pathlib import Path
import hashlib,json,subprocess
ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent
SKETCHES=('bench/p0_matrix','bench/p0_timing','bench/p0_adc','bench/p0_gpio','bench/p0_qtr')
def mapping(sketch):
    folder=ROOT/sketch
    files={p.relative_to(folder).as_posix():p.read_bytes() for p in folder.rglob('*')
           if p.is_file() and not(p.parent==folder and p.name=='.gitkeep')}
    files['src/config.h']=(ROOT/'src/config.h').read_bytes()
    for module in ('core','hal'):
        files.update({p.relative_to(ROOT).as_posix():p.read_bytes() for p in (ROOT/'src'/module).rglob('*') if p.is_file()})
    digest=hashlib.sha256()
    for name,raw in sorted(files.items()):
        digest.update(name.encode()+b'\0');digest.update(raw)
    return dict(hash=digest.hexdigest(),files={name:hashlib.sha256(raw).hexdigest() for name,raw in sorted(files.items())})
manifest=json.loads((ROOT/'tools/p0_inert_sources.json').read_text())
result=dict(baseline='6911b25',sketches={sketch:mapping(sketch) for sketch in SKETCHES},
    protected_diff=subprocess.check_output(['git','diff','6911b25','--','src/core','src/app','tests/locked','tools/board_tool.py'],cwd=ROOT).decode(),
    manifest_has_exact_original_five=set(manifest)==set(SKETCHES))
result['manifest_matches_current_source']=all(manifest[k]==v['hash'] for k,v in result['sketches'].items())
(OUT/'inert_maps.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(dict(maps={k:v['hash'] for k,v in result['sketches'].items()},
    protected_unchanged=result['protected_diff']=='',manifest_has_exact_original_five=result['manifest_has_exact_original_five'],
    manifest_matches_current_source=result['manifest_matches_current_source']),indent=2))
