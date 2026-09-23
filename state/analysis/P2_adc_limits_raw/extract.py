from pypdf import PdfReader
from pathlib import Path
import hashlib,json
out=Path('state/analysis/P2_adc_limits_raw'); pdf=Path('build/cache/RM0456_Rev6_52152e41.pdf'); r=PdfReader(pdf)
records=[]
for n in list(range(1267,1285))+[1339,1340,1341,1342,1343]:
    page=r.pages[n-1]; text=page.extract_text(); p=out/f'RM0456_p{n}.txt'; p.write_text(text,encoding='utf-8'); records.append({'printed_page':n,'text_sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
(out/'rm_pages.json').write_text(json.dumps({'pdf':str(pdf),'sha256':hashlib.sha256(pdf.read_bytes()).hexdigest(),'pages':len(r.pages),'selected_pages':records},indent=2)+'\n',encoding='utf-8')
