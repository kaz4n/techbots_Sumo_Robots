from pathlib import Path
import re
base=Path('tests/native_power')
for name in ('cases.cc','ownership_cases.cc','takeover_cases.cc','metadata_cases.cc','config_cases.cc'):
 p=base/name;s=p.read_text(encoding='utf-8-sig');masked=re.sub(r'"(?:\\.|[^"\\])*"|//[^\n]*|/\*.*?\*/',lambda m:' '*len(m.group()),s,flags=re.S)
 stack=[];pairs={};owners={}
 for i,c in enumerate(masked):
  if c=='{':stack.append(i)
  if masked.startswith('fixture::reset();',i):owners[stack[-1]]=True
  if c=='}':pairs[stack.pop()]=i
 changes=[]
 for start in owners:
  changes.extend([(start+1,'fixture::isolated([&] {'),(pairs[start],'\n});')])
 for at,text in sorted(changes,reverse=True):s=s[:at]+text+s[at:]
 s=s.replace('#include "native_fixture.h"','#include "native_fixture.h"\n#include "isolation.h"')
 p.write_text(s)
p=base/'native_fixture.cc';s=p.read_text();s=s.replace('PWR->VOSR.value=PWR_VOSR_VOS|PWR_VOSR_VOSRDY;','PWR->VOSR.value=PWR_VOSR_VOS|PWR_VOSR_VOSRDY|PWR_VOSR_BOOSTEN|PWR_VOSR_BOOSTRDY;');p.write_text(s)
p=Path('tests/tooling/test_power_unoq.py');s=p.read_text();s=s.replace("str(FIXTURE / 'native_fixture.cc'), str(source", "str(FIXTURE / 'native_fixture.cc'), str(FIXTURE / 'isolation.cc'), str(source")
s=s.replace('    def test_b5_partial_claim_is_reset_only(self):','    def test_b5_all_ownership_guards(self):\n        self.execute(self.variant(case="ownership_cases.cc"))\n\n    def test_b5_partial_claim_is_reset_only(self):')
p.write_text(s)
