"""Seal the bounded D114 source/staging/target review without board actions."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
TARGET = OUT.parent / 'target_396bcc45_bench-default_checked'
sha = lambda data: hashlib.sha256(data).hexdigest()
pins = {
    'tools/board_tool.py': 'e0444bc4c8922a53469d232dcab72bb91b6a59f8be50a80f4eb8e8badbad44d6',
    'tools/app_build_policy.py': '744d7d411e9ed68fb724d3ac2fc4081ea35ebca7c8e5414be54ee7feb1a1e161',
    'bench/ui_adc_probe/ui_adc_probe.ino': '87e305fe7c3eb4d606224065fea2a2a1ef2dce93351c195ea9bf43748eaf0a60',
    'tests/tooling/test_ui_adc_probe_policy.py': 'f88ff324c23f6c0b3d0b91498874498910fa19eb0c9529dec84360990a73f297',
    'state/analysis/P2_ui_adc_probe_contract.md': '1250e761bc46b517816ca012b45c7ecc89ce665847e7f04e06b4e99a7c1dab0e',
}
for path, expected in pins.items():
    assert sha((ROOT / path).read_bytes()) == expected, path
elf = (TARGET / 'ui_adc_probe.ino.elf').read_bytes()
zsk = (TARGET / 'ui_adc_probe.ino.elf-zsk.bin').read_bytes()
assert len(elf) == len(zsk) == 19840 and elf[:7] == zsk[:7] and elf[16:] == zsk[16:]
assert sha(elf) == '76e23fe03631d5cc2144578d35ca78b9bafd44158e0d18b2ab026922e4c9d05b'
assert sha(zsk) == '567fb90da6965cf74efc5ac2221e543d6d2150e3bf70ddae3e2346e6646c7fb9'
evidence = {}
for name in ('target_396bcc45_bench-default.json', 'policy_1790200987897358667.json'):
    evidence[name] = sha((OUT / name).read_bytes())
result = {
    'verdict': 'PASS_SCOPED_D114_FIRMWARE_STAGING_AND_EXACT_TARGET',
    'reviewer': 'Reused separate same-model source-aware context; not a human gate or cross-model review',
    'source_sha256': '396bcc45fbaf30d38b170bf0c0063c555d5e88cdad512829b86a52ffede18642',
    'receipt_id': '73d13df1e7244ddc8a71d1a7e52c0ed8',
    'pins': pins,
    'elf_sha256': sha(elf), 'zsk_sha256': sha(zsk),
    'package_identity': {'bytes': len(elf), 'identical_from_offset': 16,
                         'different_offsets': [i for i in range(len(elf)) if elf[i] != zsk[i]]},
    'private_tests': {'methods': 24, 'failures': 0, 'errors': 0, 'skips': 0},
    'evidence_sha256': evidence,
    'target': {'payload_bytes': 16245, 'conditional_peak_bytes': 17128,
               'conditional_free_span_bytes': 245016, 'conditional_largest_payload_bytes': 245012,
               'runner_size': 9892, 'runner_bss_offset': 0, 'bss_section_vma': 5776,
               'shared_sources_unchanged_from_D112': 94},
    'findings': [],
    'closed_draft_issue': 'nm VMA 0x1690 is not raw st_value. ET_REL Runner st_value 0 is already BSS-relative; installed loader adds it without subtracting sh_addr.',
    'limits': ['No capture-tool, upload route/key, readout or run approval.',
               'Conditional pristine-loader-pool fit, not measured live RAM or WCET.',
               'Stock ADC/RCC/PWR/DAC startup is not a competing post-admission producer; actual Reader guards must still admit the board.',
               'No physical A1 ladder, buttons, STOP, accuracy, SC-AJ closure or phase-gate claim.',
               'Existing full host evidence reused for unchanged source; no redundant full suite rerun.'],
}
(OUT / 'final_review.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps({'verdict': result['verdict'], 'receipt': str(OUT / 'final_review.json')}))
