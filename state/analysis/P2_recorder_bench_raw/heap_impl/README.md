# Offline heap decoder implementation evidence

2026-09-23. Scope: implement `tools/recorder_heap.py` for the D091 pinned allocator
API. No capture, CLI, network, board, MCU, build, flash, commit or state-ledger
operation belongs to this subtask.

Source authority was the cached primary Zephyr
`1743741760ee5d2d58da50d504855d43f9f8e826` heap.h/heap.c and the installed runtime
audit referenced by the frozen contract. The decoder validates the exact fixed
pool, normal chain, metadata chunk, footer and all free bucket lists before any
capacity result. Canonical metadata bytes and their encoding are documented in
the module; comparison checks the canonical bytes themselves, not only hashes.

Root clarified that the unused small-layout `chunk0_hdr` second word is reserved
and excluded from logical metadata. The final encoding uses initial spans
`[0,4)` and `[8,76)`, followed by each normal chunk's active fields and the active
end marker. Thus offsets 4..7, 76..79 and 262140..262143 are excluded along with
normal used payload and stale free payload. Earlier successful smoke/26-test
receipts are retained as `*_pre_padding_clarification.json`; they cover the
earlier encoding, not this final source.

Final source SHA-256:
`d661024975925a7d8a83f4b772199bbf59911adb5adb8ea69a2082b69eed4b92`.

- `python -B state/analysis/P2_recorder_bench_raw/heap_impl/selfcheck.py`: PASS;
  six acceptance/accounting scenarios and twelve malformed-input rejections.
  Exact source hash and output are in `selfcheck.json`.
- `python -B -m unittest tests.tooling.test_recorder_heap -v`: PASS;
  28 independently authored methods, including reserved/padding mutations and
  valid circular-head rotation. Full command/stdout/stderr/source identity are
  in `independent_tests.json`. The implementation agent did not modify tests.
- Python AST/compile check: PASS; longest decoder function 32 source lines.

All snapshots in these checks are synthetic source-derived fixtures. They prove
offline parser behavior only, not deployed identity, actual free memory, atomic
capture, minimum runtime capacity, stack high-water, hardware acceptance or WCET.
Next action: fresh independent source review and integration by the root agent.
