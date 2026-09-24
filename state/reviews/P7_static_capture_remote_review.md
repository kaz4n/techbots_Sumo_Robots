# D153 passive collector code and host-receipt review

25 September 2026, Asia/Dubai. Separate fresh-context, same-model reviewer;
read-only implementation review plus four supplemental controlled host tests.
This is neither cross-model review nor a human phase gate.

## Findings and disposition

PASS for the D153 host collector scope. No open BLOCKER, MAJOR or MINOR finding.
No native invocation is approved by this review.

Reviewed [contract](../analysis/P7_static_capture_remote_contract.md) SHA256
`0371739e93920fa24a18ed95eeb8eb6b117e4cf4e3f3b87f04ed38bc16ba227e`,
[implementation](../analysis/P7_static_startup_raw/capture_remote.py) SHA256
`1aa602d03745b6d5654c7c7dca9c6f76ca99af6109b58b5c5c591cdf561a4983`, and
[bindings](../analysis/P7_static_startup_raw/capture_bindings.json) SHA256
`c2c87df6165556602a5a79472caedf0755c070b2e2f3e0b834f17ab0de5c0d32`.
The earlier [design review](P7_static_startup_design_review.md) remains scoped to
its earlier contract. The current pre-execution clarifications specify literal
Tcl path braces/eight-digit addresses, the actual pre-Popen deadline check,
retained-descriptor failure receipts, and clock-error evidence retention.

Inspection identified stale timeout calculation before stream-file setup and
possible loss of the first claim error when context exit also fails. Both were
repaired before first implementation execution. Source b099e4d9 remains in
commit d5c8d6d6; the repaired first-executed source is 1aa602d0. Draft test
expectations were reconciled with the public contract before freeze. There was
no failing execution followed by a rewritten oracle or source repair.

The fixed bindings and descriptor helper provide bounded admission and owned
file creation; the durable claim precedes launch and existing output is never
reused. The only process command is the exact eighteen-read plan. Both complete
before-flash images must match before RAM sampling. Partial collection cannot
reach decoding. Timeout handling targets the owned process group and records
unknown/unreaped completion; it makes no MCU-quiescence claim. All five file
postchecks, board identity and directory identity are attempted independently.
Fault, no-progress and late flash mismatch remain interpretation outcomes of a
complete collection, not successful startup claims.

## Test evidence

The independent spec-only author's test source is SHA256
`2d9fe1697ebd0603508b1a36a08132ed3e000d3770e34e16df7e4854aff277dd`.
The [public freeze](../analysis/P7_static_startup_raw/remote_freeze.json)
predates the [first receipt](../analysis/P7_static_startup_raw/remote_first.json)
(SHA256 `6ca375980310ca4589e55e119394bd1f9873475a73acc11a4769f28b87fdee6f`).
All 46 methods passed on their first run in 2.569 seconds, exit 0, with all eight
frozen pins unchanged. This reviewer read that actual receipt and checked its
current input hashes rather than rerunning the entire suite.

The reviewer-authored [supplemental suite](../analysis/P7_static_startup_raw/capture_remote_private.py)
is SHA256 `a529fbb1387bcfb4595708762ee83cd2f1ae767e6b8af6bdaa0abb9908dfaa72`.
Its [freeze](../analysis/P7_static_startup_raw/remote_private_freeze.json)
preceded execution. The [first supplemental receipt](../analysis/P7_static_startup_raw/remote_private_first.json)
(SHA256 `e589b823a575b43e9dbfdceae661895a1d655cebbb0ebf20c7bc9f8f999c0ee9`)
records four methods passing in 0.153 seconds, exit 0, with all seven pins
unchanged. These prove in controlled fixtures that 4096 numeric process entries
are admitted, entry 4097 refuses before claim/launch, stream setup can reduce the
actual wait to the remaining 20 seconds, and a parent-fsync failure remains first
when context exit adds another error. The process-bound cases use lazy synthetic
entries and do not create thousands of files. These supplemental tests were
authored after source inspection and are not claimed as independent spec-only
tests.

Both runs used WSL Python -B and small /dev/shm fixtures. Popen/killpg were guarded
or replaced by controlled substitutes. A final read-only check found zero
remaining sumox_capture_contract_* fixture directories; current public/private
freeze hashes all match. Only the supplemental source, compact freeze/result
receipts and this review were added by the reviewer. No binary/source snapshots,
bytecode, firmware edits, compiler, upload, reset or MCU read were produced.

## Limits and next action

The filesystem/process checks are sampled; OpenOCD still accepts a pathname and
there is no kernel-wide exclusive lock. The process tests establish wrapper
behavior with substitutes, not native RLIMIT enforcement or live process-group
behavior. The shallow decoder check inherits the frozen D152 decoder's semantics.
No current image provenance, startup progress, RAM/stack/WCET, physical acceptance
or human gate is established.

The next native composition must separately bind reviewed source/HEAD and the
D144 packet, obtain a known clean new upload outcome, and durably consume a fresh
source-bound capture authorization. This host PASS supplies no upload or capture
grant and does not change production static admission.
