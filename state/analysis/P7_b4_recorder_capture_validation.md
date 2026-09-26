# Fixed B4 retained capture and CSV completion

The native component `tools/b4_recorder_capture.py` adds four hooks to the
unchanged, checked MEM-AP capture implementation. Its fixed plan has 26 reads
and 852,624 requested bytes. Full loader and B4 sketch comparisons must pass
before any SRAM read. Ten chunks preserve the 159,200-byte recorder; two
120-byte lifecycle brackets remain separate observations. No reset, halt,
upload, MCU write, polling or motor permission is introduced.

The pure host component `tools/decode_b4_capture.py` requires a successfully
returned capture envelope, successful closing checks and exactly 13 saved
files. It verifies their identities, lengths, ordering and contents before
passing the complete owner to the unchanged D216 recorder decoder. Raw inputs
are retained on bounded refusals. Origin, coherence and hardware acceptance
remain unproven; equal lifecycle fields do not establish an atomic snapshot.

Independent review caught an owner-retention issue before tests: a failed final
lifecycle read discarded the assembled `raw_owner` field even when all ten
chunks had passed. The bounded repair publishes that field immediately after
the tenth validated chunk, while still refusing CSV. The exact original source
is reproducible from the three counted reverse substitutions and its saved
hash; the original derivation is retained.

The first Linux run passed 14 of 15 methods. Two assertions in the remaining
JSON fixture assumed a parser depth failure and used stale durable-report
identity. Both installed Python versions parsed the 2,048-deep array, after
which the product correctly refused its schema. The fixture was corrected to
exercise the reachable boundaries, and a deterministic RecursionError fixture
retains the strict parser-exception check. All other 14 methods are unchanged.
The original test, oracle, streams and failures remain available.

Corrected runs passed all 15 tests on Linux and all 15 on Windows, without
skips. All 36 frozen inputs remained unchanged. Root closure is
`P7_b4_recorder_capture_raw/capture_host_closing01.json`, 8,096 bytes,
`321ab6747d7167b45f55cbfd389c51dfd6b9a7ff2e2402f9cf6b647c9f3237c8`.
The independent synthetic fixture is 5,393 report bytes, 5,870 envelope bytes
and 164,833 retrieved bytes, within the unchanged caps.

Native source: 9,769 bytes,
`e28d01312742389737c0ca0d6914ab8593d59f93b1a67ac302029749f11b4189`.
Host source: 10,061 bytes,
`1c0f75c001b8f66e9b3f5f4ed2be8472c8aaf1991265cfb6f91e4372043f6109`.
Contract `c6eba89a`; fixed plan `14137f10`; corrected oracle `bf14d974`.

These tests use synthetic captures. No B4 RAM capture has run, and D212's
ordinary image remains loaded. That image is incompatible with the B4 map.
The complete qualified caller, staging, transport and retrieval integration
is the separate D219 task. Full initialized timing, sensor/motor commissioning,
native UART delivery, physical trials and human gates remain open.

Independent source/host review is FINAL PASS:
`state/reviews/P7_b4_recorder_capture_review.md`, 7,924 bytes,
`e598b25b5707c9456cdda4e6d0143b9d3f2a4df66e567770b00926b64826c5e6`.
It reconciles all 32 inherited function spans, the fixed bindings, both bounded
repairs and all 30 accepted outcomes. No open material finding remains in this
component scope.
