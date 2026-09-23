# Retrieves three primary timing documents without device access.
# Preserves transport failures rather than treating them as source statements.
# Successful PDF bodies are validated, hashed, and retained as local evidence.
from pathlib import Path
import urllib.request,hashlib,json,concurrent.futures
root=Path(__file__).parent
items=[
 ('AN4235.pdf','https://www.st.com/resource/en/application_note/an4235-i2c-timing-configuration-tool-for-stm32f3xxxx-and-stm32f0xxxx-microcontrollers-stmicroelectronics.pdf'),
 ('MPU6000_6050.pdf','https://invensense.tdk.com/wp-content/uploads/2015/02/MPU-6000-Datasheet.pdf'),
 ('DS13086.pdf','https://www.st.com/resource/en/datasheet/stm32u585ri.pdf'),
]
def get(x):
 name,url=x
 try:
  with urllib.request.urlopen(url,timeout=12) as r:
   b=r.read(); final=r.url; status=r.status;content=r.headers.get('Content-Type')
  if not b.startswith(b'%PDF'):return {'name':name,'url':url,'final_url':final,'status':status,'content_type':content,'error':'not PDF; not retained as PDF'}
  (root/name).write_bytes(b)
  return {'name':name,'url':url,'final_url':final,'status':status,'content_type':content,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
 except Exception as e:return {'name':name,'url':url,'error':str(e)}
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:results=list(ex.map(get,items))
(root/'retrieval.json').write_text(json.dumps(results,indent=2)+'\n')
print(json.dumps(results))
