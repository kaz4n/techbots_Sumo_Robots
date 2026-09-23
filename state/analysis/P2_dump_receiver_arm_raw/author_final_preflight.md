# D113 final public-contract test preflight

2026-09-24. Initial candidate reviewed in full:
`state/analysis/P2_dump_receiver_arm_contract.md`, SHA-256
`92b647a136b17af44d792d50a7fd07777b83c2f97c63b609ceea518e9a50e805`.
Final candidate with the selected remote error branch:
`524c030033cf845c65256b357ce104b3a16020f9eed2d5158a6fec4ad7c44194`.
This review uses the reused independent author context, not a fresh repository
context or another model. No production implementation bodies were read, no
executable tests were authored/executed, and no hardware was accessed.

## Result

PASS for public-contract testability against final candidate 524c0300. The
coordinator added the strict alternate remote error branch, 512-character message
bound, diagnostic exit 0 / host CaptureError / observer CLI exit 1, and explicit
transport-error distinction. The author read that final section and verified the
candidate hash. No material independent-oracle gap remains. The original narrow
finding and recommendation below remain as the review history, now resolved.

The candidate resolves the prior public END predicate, receive/deadline priority,
exact schemas, immutable-file publication, before/after identity checks, bounded
process inspection, failure-prefix preservation, and final-success evidence gaps.
All are independently reachable through public CLI/API and controlled execution
of actual generated remote scripts after executable expectations are frozen.

The initial candidate had one narrow protocol seam requiring a literal decision:
how a remote
metadata validation failure reaches the host as CONNECTION_METADATA. Currently
the remote stdout schema describes only a six-key successful observation, while
all nonzero/timeout/launch outcomes map to CONNECTION_TRANSPORT. There is no
declared remote error payload that can communicate unsafe/malformed receipt
failure without relying on an unfrozen stderr convention.

## Minimal recommended clarification

Keep the successful remote stdout object unchanged. Permit one alternative strict
error object, within the same 16384-byte limit, with exactly:

```
error: {code: "CONNECTION_METADATA", message: string}
observed_utc: board UTC string | null
observed_monotonic_ns: board integer | null
claim: validated claim object | null
connection: validated connected object | null
terminal: validated terminal object | null
```

A completely emitted diagnostic uses remote exit 0: that means the query delivered
an error report, never that a connection exists. The host validates this branch,
then raises CaptureError(CONNECTION_METADATA) with the already-defined public
connection_evidence envelope (state null, actual command outcome, original error,
only verified records). A nonzero/timeout/launch failure remains
CONNECTION_TRANSPORT, and malformed/oversized diagnostic JSON is
CONNECTION_METADATA. No success state is synthesized and no new mode, public
function, retry, or transport framework is added. Human-readable diagnostics are
not a machine protocol. The coordinator may instead choose another literal error
branch before independent tests freeze; the requirement is determinism.

## Confirmed independently testable expectations

- Construction is passive. Invalid ticket/timeout/target/options fail before
  transport. Existing no-ticket and offline behavior is retained.
- Claim collision never connects; fresh claim publication precedes connect;
  connected publication precedes recv. No application send/probe/RPC occurs.
- Receive bytes are emitted before post-return deadline, total-byte, line and
  END checks; deadline equality wins. EOF and thrown socket timeout are distinct.
  A MAX+1 returned byte is observable remotely, while local wire retention is
  bounded. END_OBSERVED is not Parser/CRC acceptance.
- Record schemas, nested identity, strict JSON/byte bounds, file ownership/mode/
  link/inode stability, current boot/UID, and monotonic ordering have fixed oracles.
- Missing unpublished claim is PENDING; invalid records are errors. Terminal then
  expiry have priority without requiring live process metadata. Before deadline,
  process/socket loss or reuse is UNKNOWN, never a sticky CONNECTED. A changing
  ticket directory cannot preserve current attachment evidence.
- Query inspection is bounded to the claimed PID/fd and one capped IPv4 snapshot;
  malformed/unavailable/excessive live metadata is UNKNOWN. Before/after identity
  checks expose replacements without private state mutation.
- Final retrieval runs once before buffered fragments are yielded. Valid wire
  plus failed transport remains failure; valid wire plus absent/invalid terminal
  evidence remains failure. Existing primary errors and both command outcomes
  remain visible. Prefix retention does not depend on metadata availability.
- Successful final publication requires all three matching records with a
  TERMINAL/END_OBSERVED result and all unchanged parser/bundle checks. No claim,
  connection, terminal record or close time is invented when creation/close fails.

Fresh caller UUID binding remains an explicit caller obligation: observing an
old live ticket reports its original identity and cannot prove it belongs to a
new invocation. Sampled TCP connection, UNKNOWN router registration, no MCU
permission, no UART framing/exclusivity claim, and no physical acceptance remain
accurate limits. No further architecture expansion is recommended.

## Qualification after separate reviewer findings

2026-09-24. The separate reviewer found two literal contradictions that this
author's 524c0300 preflight did not catch. That earlier PASS and its hash remain
historical evidence, not a claim that the earlier candidate was contradiction-free.
The coordinator corrected them in candidate
`09d67ef3b64b9ec9e20f6068a6877dd111aa132bdc59bf41cd6b82e9f48c573f`.
The author verified the exact current hash and both corrected passages:

- Opt-in target is now at most **128 ASCII characters**, matching the existing
  manifest limit identified by the reviewer; the earlier 255-character statement
  no longer appears in this candidate. Timeout and no-ticket semantics are unchanged.
- The `<= observed` condition now explicitly covers only retained
  **started/claimed/connected/closed event times**. Deadline is expressly excluded;
  its derivation/range and expiry checks still apply, permitting a future deadline
  for live PENDING/CONNECTED evidence.

These literal corrections resolve both reported contradictions and give
deterministic target-boundary and live-future-deadline test expectations. This
bounded follow-up did not re-audit implementation or execute tests. No adoption
or hardware acceptance follows; executable authoring remains pending adoption.
