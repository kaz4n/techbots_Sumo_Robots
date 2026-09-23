from pathlib import Path
base=Path('tests/native_power')
for name in ('native_cmsis.h','native_fixture.cc'):
 p=base/name;s=p.read_text(encoding='utf-8-sig').replace('0x40010000UL','0x46000000UL').replace('0x40011000UL','0x46001000UL')
 if name=='native_cmsis.h':s=s.replace('SYSCFG_TypeDef*>(0x46000000UL)','SYSCFG_TypeDef*>(0x46000400UL)')
 p.write_text(s)
p=base/'extract_bits.py';s=p.read_text();s=s.replace("intro='// Copies source-verified", "license_notice='/* Copyright (c) 2021 STMicroelectronics. All rights reserved.\\n * This software is licensed under terms that can be found in the LICENSE file\\n * in the root directory of this software component.\\n * If no LICENSE file comes with this software, it is provided AS-IS.\\n * Extracted from the exact installed headers retained with hashes in\\n * state/analysis/P2_adc_ownership_raw/headers/manifest.json.\\n */\\n'\nintro='// Copies source-verified")
s=s.replace("// Independent B5 tests supply hardware side effects and fault injection.\\n#pragma once\\n'", "// Independent B5 tests supply hardware side effects and fault injection.\\n#pragma once\\n'+license_notice")
p.write_text(s)
p=Path('tests/tooling/test_power_unoq.py');s=p.read_text();s=s.replace("        cls.stage = Path(cls.temp.name)","        cls.stage = Path(cls.temp.name)\n        cls.binary_manifests = {}")
s=s.replace("        payload = {'argv':", "        native_source = next((Path(x) for x in argv if str(x).endswith('/hal/power.cpp')), None)\n        manifest = cls.binary_manifests.get(str(argv[0]))\n        if native_source is not None:\n            manifest = {name: hashlib.sha256(p.read_bytes()).hexdigest() for name, p in {\n                'production': native_source, 'header': native_source.with_suffix('.h'),\n                'config': native_source.parent.parent / 'config.h'}.items()}\n        payload = {'staged_source_manifest': manifest, 'argv':")
s=s.replace("        cls.command([*argv, '-o', str(binary)])\n        return binary", "        cls.command([*argv, '-o', str(binary)])\n        cls.binary_manifests[str(binary)] = {name: hashlib.sha256(p.read_bytes()).hexdigest()\n            for name, p in {'production': source / 'hal/power.cpp',\n                            'header': source / 'hal/power.h', 'config': source / 'config.h'}.items()}\n        return binary")
p.write_text(s)
