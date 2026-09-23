from pypdf import PdfReader
from pathlib import Path
r=PdfReader('build/cache/RM0456_Rev6_52152e41.pdf');out=Path('state/analysis/P2_adc_limits_raw')
for n in range(1266,1378):
 t=r.pages[n-1].extract_text()
 if 'LFTRIG' in t or 'idle time' in t or 'Tidle' in t:
  (out/f'RM0456_p{n}.txt').write_text(t,encoding='utf-8'); print(t.encode('ascii','replace').decode())
