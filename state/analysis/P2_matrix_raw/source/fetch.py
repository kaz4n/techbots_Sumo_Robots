# Retrieves the exact tagged Arduino matrix and loader source from primary URLs.
# Preserves bytes and hashes separately from installed binary evidence.
# Tested by successful HTTP retrieval and local/installed header equality.
from pathlib import Path
import hashlib,json,urllib.request
here=Path(__file__).parent
rev='79b3f1afdad455f55e4a25030953617152c0227c'
records=[]
for path in ['loader/matrix.inc','loader/main.c','libraries/Arduino_LED_Matrix/src/Arduino_LED_Matrix.h']:
 url=f'https://raw.githubusercontent.com/arduino/ArduinoCore-zephyr/{rev}/{path}'
 with urllib.request.urlopen(url,timeout=20) as r:b=r.read()
 name='official_'+Path(path).name
 (here/name).write_bytes(b)
 records.append({'url':url,'local':name,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()})
(here/'official_receipt.json').write_text(json.dumps(records,indent=2)+'\n',encoding='utf-8')
print(json.dumps(records))
