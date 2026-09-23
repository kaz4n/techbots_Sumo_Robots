# D091 recorder capture implementation handoff

Objective: implement tools/recorder_capture.py as a new independently bounded,
read-only diagnostic/allocator capture helper. Ownership is now returned to the
coordinator for exact reviewed artifact pinning and final review. No commands
against the board, MCU reads, uploads, resets, attach/halt, or daemon actions ran.

Only production file modified: tools/recorder_capture.py. The existing p0_capture
and its guards remain unchanged. New helper reuses its pure validation, loader
image comparison and bounded four-node LLEXT traversal through the NEW Capture
read boundary. No new independent tests or bench source were read or changed.

Implemented:
- Exact296B/74word diagnostics with sequence/schema/reserved/enums/boolean/capacity
  checks, valid-stack bounds and FROZEN=>SEALED/all-retained-rows-checksummed.
  FAILED preattempt may use mode0; actual failure/loss fields are preserved.
- Local reviewed hash checks including the coordinator-supplied readelf hash;
  exact deployed loader/sketch comparison before any private RAM interpretation.
- New48read/2MiB total/16KiB RAM/64command/600s total/30s command guards. Admitted
  attempts are charged before commands and each fixed read purpose is attempted
  at most once, including failure. No arbitrary command/address/size CLI input.
- Exact296B external-C BSS symbol validation, fixed24B descriptor, two16block
  pool snapshots, checked heap comparison, unchanged descriptor and diagnostic.
- Raw read fragments, full raw command stdout/stderr files, both raw pools,
  UTC/monotonic brackets, failure records and CAPTURED evidence-only semantics.

Self-checks: py_compile PASS; quiet import/literal decoder PASS; pure synthetic
capture_values consumes36fixed reads and returns CONSISTENT_SAMPLED with both
262144B pool files. No subprocess or physical read occurs in that smoke.
AST check:21functions, longest31lines. Receipts: initial_validation.json,
pure_capture_values.json, function_sizes.json, source_sha256.json.

Independent author reported27methodsPASS before extending negative coverage;
their final receipt is separately owned and must determine final test status.

ARTIFACT_DIR/ELF_HASH/BINARY_HASH remain intentionallyNone in this version;
unset pins fail before memory reads. Coordinator now owns pinning the exact
1502e948 reviewed recorder_inert build and its supplied ELF/ZSK hashes. Capture
does not authorize upload/run or imply a physical, timing, memory, or human gate.
