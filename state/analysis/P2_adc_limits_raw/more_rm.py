from pypdf import PdfReader
from pathlib import Path
import re,json
out=Path('state/analysis/P2_adc_limits_raw')
s=(out/'stjp_detail.body').read_text(encoding='utf-8')
print(json.dumps(re.findall(r'https?[^\s\"<>]+\.pdf',s)))
r=PdfReader('build/cache/RM0456_Rev6_52152e41.pdf')
for n in [1344,1345,1346]: (out/f'RM0456_p{n}.txt').write_text(r.pages[n-1].extract_text(),encoding='utf-8')
for n in range(3,30):
    t=r.pages[n-1].extract_text()
    if 'SYSCFG' in t or 'Power control' in t: print(n,t.encode('ascii','replace').decode())
