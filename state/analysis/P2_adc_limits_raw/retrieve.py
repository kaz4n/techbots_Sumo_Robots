import requests,json,hashlib,datetime,pathlib,concurrent.futures
out=pathlib.Path('state/analysis/P2_adc_limits_raw')
urls=[('st_ai','https://www.st.com/resource/en/datasheet/stm32u585ai.pdf'),('stcn_ai','https://www.st.com.cn/resource/en/datasheet/stm32u585ai.pdf'),('stjp_index','https://www.stmcu.jp/design/document/datasheet/')]
def get(item):
    key,url=item; row={'key':key,'url':url,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
    try:
        r=requests.get(url,timeout=(10,22)); data=r.content
        row.update(status=r.status_code,final_url=r.url,headers=dict(r.headers),length=len(data),sha256=hashlib.sha256(data).hexdigest(),pdf=data.startswith(b'%PDF-'))
        file=out/(key+('.pdf' if row['pdf'] else '.body'));file.write_bytes(data);row['file']=str(file)
    except Exception as e:row['error']=repr(e)
    (out/(key+'_receipt.json')).write_text(json.dumps(row,indent=2)+'\n',encoding='utf-8')
    return row
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:
    for row in ex.map(get,urls): print(json.dumps(row))
