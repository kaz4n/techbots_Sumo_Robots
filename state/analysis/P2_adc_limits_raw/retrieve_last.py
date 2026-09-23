exec(compile(open('state/analysis/P2_adc_limits_raw/retrieve_aliases.py',encoding='utf-8-sig').read().split('with concurrent.futures')[0],'<helpers>','exec'))
urls=[('stjp_rev10_guess','https://www.stmcu.jp/wp/wp-content/uploads/2021/10/DS13086_Rev10.pdf'),('st_vi','https://www.st.com/resource/en/datasheet/stm32u585vi.pdf'),('stcn_dm','https://www.st.com.cn/resource/en/datasheet/dm00639779.pdf')]
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:
    for row in ex.map(get,urls): print(json.dumps(row))
