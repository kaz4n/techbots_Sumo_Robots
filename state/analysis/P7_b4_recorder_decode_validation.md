# B4 retained-recorder decoder

`tools/decode_b4_recorder.py` is a pure offline decoder for the exact D214/D215
B4 motor-disabled image. Its fixed map comes from the observed target layout:
159,200 owner bytes, three packed arrays and 35 interpreted scalar fields.
It preserves the original bytes, chronological frame order, event insertion
order, all codec statuses and all 22 loss indicators. It emits the existing
three CSV schemas, including every summary field.

The decoder refuses an altered map, wrong owner size, invalid interpreted bool,
out-of-range index or retained unsupported status. It publishes all three CSV
byte strings together, or none. Valid CSV can still have inconsistent owner
metadata; format, consistency, lifecycle and provenance remain separate.
Unknown payload values and signed duty -128 are preserved. Unused native bytes
remain raw-only. The decoder never establishes hardware origin or coherence.

Public API:

```python
from tools.decode_b4_recorder import decode_recorder

report = decode_recorder(owner_bytes, layout_raw=checked_layout_bytes)
```

The caller supplies bytes from an independently qualified capture and the exact
`P7_b4_recorder_decode_raw/layout01.json`. The function does no file, process,
clock or network I/O. This module has no CLI, memory reader or file exporter.
The current ordinary firmware is a different image: its RAM must not be
interpreted with this B4 map.

First independent focused host runs passed 20 tests on Linux and 20 on Windows,
with no skips, failures or repairs. Cases include full capacities, ring wrap,
packed status lanes, literal D073 CSV goldens, every scalar width, all loss
terms, lifecycle values, malformed bools and unsupported retained statuses.
All 26 frozen files remained unchanged. Tests used synthetic owner bytes
against the observed map; no actual B4 recording was captured.

Independent review is FINAL PASS: `state/reviews/P7_b4_recorder_decode_review.md`,
6,196 bytes, hash `e817e6914a102333298b3904ccc5e84fffc28296a3b2b23e10e33589e05edd66`.
Root closure `decode_host_closing01.json` is 6,062 bytes,
`3fab6436bf85a176611c318cd20b0d341b372f30aa7dce10d21f60d8a6cd2038`.
It reconciles all 40 outcomes, eight saved invocation files and the input pins.

The decoder source is 11,743 bytes,
`43347b569098b78cbdbf32a1e4b06ebbbef245c4c57b91609fa38d8bb3cca8a3`;
the exact map is 4,443 bytes,
`f9b4b1531b9f714fb2b424d9613787449b2172fcc7a0e96292dd51d37d8c0b2d`.
The existing validator and firmware were unchanged. Bounded live capture,
native UART delivery, physical commissioning and human gates remain separate.
