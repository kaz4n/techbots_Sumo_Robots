import json,pathlib,hashlib,datetime
out=pathlib.Path('state/analysis/P2_adc_limits_raw')
d=json.loads(pathlib.Path('state/analysis/P2_adc_native_raw/installed_source_01.json').read_text(encoding='utf-8-sig'))
print([(type(x).__name__,list(x)[:5] if isinstance(x,dict) else '') for x in d])
for x in d:
 if isinstance(x,dict) and str(x.get('path','')).endswith('stm32u5xx_ll_adc.h'):
  for k,v in x.items():
   if isinstance(v,list):
    selected=[row for row in v if isinstance(row,list) and isinstance(row[0],int) and (1954<=row[0]<=1960 or 7918<=row[0]<=7931)]
    if selected:(out/'installed_ll_timing_excerpt.json').write_text(json.dumps({'input_receipt':'../P2_adc_native_raw/installed_source_01.json','selected':selected},indent=2)+'\n',encoding='utf-8')
meta={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'source only; no board, errata or NVIC action','datasheet':{'revision':'DS13086 Rev10','date':'2024-07-05','pages':350,'urls':['https://www.st.com/resource/en/datasheet/dm00639779.pdf','https://www.st.com/resource/en/datasheet/stm32u585ai.pdf'],'source_original_pdf_sha256':None,'evidence':'web extraction; direct download failures preserved'},'rm':{'revision':'RM0456 Rev6','path':'build/cache/RM0456_Rev6_52152e41.pdf','sha256':'52152e414e2ac329cfd9038481b97e8ff70592f9892d171dcb63b7d283722616','rendered_visually_checked_pages':[654,1297]},'tool_failures':['Initial rg PowerShell wildcard path invalid; corrected using directory -g filter.','Initial console print of Japanese HTML failed cp1252; corrected using ASCII-escaped JSON.','Inline Python regex PowerShell quoting failed before execution; corrected via literal here-string script.','Additional web request produced no numbered DS lines; next response preserved verbatim in ds_timing_web.txt.']}
(out/'provenance.json').write_text(json.dumps(meta,indent=2)+'\n',encoding='utf-8')
files=[{'path':str(p.relative_to(out)).replace('\\','/'),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(out.iterdir()) if p.is_file() and p.name!='manifest.json']
(out/'manifest.json').write_text(json.dumps({'files':files},indent=2)+'\n',encoding='utf-8')
print('Manifest files',len(files),'bytes',sum(x['bytes'] for x in files))
for x in files:
 assert hashlib.sha256((out/x['path']).read_bytes()).hexdigest()==x['sha256']
print('All manifest entries verified')
