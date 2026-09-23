# Retrieves the already identified pinned Arduino Zephyr sources for citation.
# Saves exact bytes and hashes; does not install or execute the drivers.
# Network failures remain recorded independently for each source.
from pathlib import Path
import urllib.request,hashlib,json
root=Path(__file__).parent
rev='1743741760ee5d2d58da50d504855d43f9f8e826'
out=[]
for name in ['i2c_stm32.c','i2c_stm32_v2.c','i2c-priv.h']:
 url=f'https://raw.githubusercontent.com/arduino/zephyr/{rev}/drivers/i2c/{name}'
 try:
  with urllib.request.urlopen(url,timeout=15) as r:b=r.read()
  (root/name).write_bytes(b);out.append({'url':url,'name':name,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()})
 except Exception as e:out.append({'url':url,'name':name,'error':str(e)})
(root/'downloads.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out))
