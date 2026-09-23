"""Independently compare fixture LL bodies against retained installed originals."""
from pathlib import Path
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
SOURCE = ROOT / "state/analysis/P2_adc_ownership_raw/headers"
FIXTURE = ROOT / "tests/native_power"

def functions(text):
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    found = {}
    for match in re.finditer(r"(?:__STATIC_INLINE|inline)\s+[^\n]*\b(LL_\w+)\([^{}]*\)\s*\{", text):
        end, depth = match.end(), 1
        while depth:
            if text[end] == "{": depth += 1
            if text[end] == "}": depth -= 1
            end += 1
        body = text[match.start():end].replace("__STATIC_INLINE", "inline")
        found[match.group(1)] = re.sub(r"\s+", " ", body).strip()
    return found

reports = []
for name in ("stm32u5xx_ll_adc.h", "stm32u5xx_ll_gpio.h", "stm32u5xx_ll_rcc.h"):
    original = functions((SOURCE / name).read_text())
    copied = functions((FIXTURE / name).read_text())
    checks = {key: value == original.get(key) for key, value in copied.items()}
    reports.append(dict(name=name, functions=checks,
        fixture_sha256=hashlib.sha256((FIXTURE / name).read_bytes()).hexdigest()))
result = dict(kind="offline-source-body-comparison", all_match=all(all(x["functions"].values()) for x in reports), reports=reports)
(OUT / "native_header_comparison.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(dict(all_match=result["all_match"], functions=sum(len(x["functions"]) for x in reports))))
assert result["all_match"]
