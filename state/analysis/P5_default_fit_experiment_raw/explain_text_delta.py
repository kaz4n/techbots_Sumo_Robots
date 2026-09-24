"""Separate named function extent from unclaimed text bytes without assuming causality."""
from pathlib import Path
import importlib.util
import json

out = Path(__file__).resolve().parent
root = out.parents[2]
spec = importlib.util.spec_from_file_location('elf_model',
    root / 'state/reviews/P2_bridge_dependency_review_raw/elf_review.py')
model = importlib.util.module_from_spec(spec)
spec.loader.exec_module(model)
report = {}
for label, path in (
    ('candidate1', out / 'app_attempt02/app.ino.elf'),
    ('D134', root / 'state/analysis/P5_native_compile_raw/app/app.ino.elf'),
):
    elf = model.Elf(path)
    section = next(s for s in elf.sections if s['name'] == '.text')
    data = elf.section_bytes(section)
    ranges = sorted((s['value'] & ~1, (s['value'] & ~1) + s['size'], s['name'])
                    for s in elf.symbols if s['type'] == 2 and s['size'] and s['section'] == '.text')
    covered = bytearray(len(data))
    for start, end, name in ranges:
        assert 0 <= start <= end <= len(data)
        covered[start:end] = b'\1' * (end - start)
    gaps = []
    start = 0
    while start < len(data):
        if covered[start]:
            start += 1
            continue
        end = start + 1
        while end < len(data) and not covered[end]:
            end += 1
        gaps.append({'offset': start, 'bytes': end - start, 'hex': data[start:end].hex()})
        start = end
    report[label] = {'text_bytes': len(data), 'function_extent_union_bytes': sum(covered),
                     'nonfunction_text_bytes': len(data) - sum(covered), 'nonfunction_text': gaps}
report['note'] = 'Named function size deltas total zero; this separates remaining text extent, not a new compile control'
(out / 'text_extent_comparison.json').write_text(json.dumps(report, indent=2) + '\n')
for label in ('candidate1', 'D134'):
    print(label, {k: v for k, v in report[label].items() if k != 'nonfunction_text'})
