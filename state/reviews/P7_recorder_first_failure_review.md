# D233 fresh recorder diagnostic review

FINAL PASS for the fixed source/data projection and focused host evidence.
No open material finding. Reviewed 2026-09-27 in the isolated fresh-diagnosis
worktree. The reviewer changed only this report; no tests, native query or MCU
capture ran during review. Actual run, ABI and capture results remain separate.

## Exact reviewed identity

Historical compile HEAD:
`ce4e69390d21d9a91231581a186be4a63213135e`.
Attempt: `07f19e32c483cebadecaa63f4d6d720f`.
Session: `572412568535289530`.
Source: `29cb1e76193e4b7c562d1fd842039f61367a82c2651a2303c09518d35a0c7ce9`.
Package: 55376 bytes / SHA-256
`b13a32b5e92993a49f165b907d5d6036fa933e1680bb23ff2738620b294fd584`.

Independently compared all 145 input files byte-for-byte with their historical
Git blobs and current files, and reconciled each recorded SHA-256. The four
compile records match both plan pins and the closed main-checkout copies.
Their staged inventory contains 110 files; the real host composition test also
recomputes that complete staging projection, including the session header.
These compile facts do not by themselves establish the loaded MCU image.

| Component | Bytes | SHA-256 |
| --- | ---: | --- |
| `tools/recorder_first_failure_abi.py` | 24804 | `0a2c745275e47d5c89ff0bb5e711d140268bc0d35f78cb0b36e717bbdf75cefb` |
| `tools/recorder_first_failure_capture.py` | 11772 | `576efd496802c5d789ce1a6c183144dadb6d309487709d3a0a4fdd4fcb8a1b96` |
| `tools/run_recorder_first_failure_capture.py` | 19614 | `c5ea40f9583beee040395030a0f73f0f5c50701e0885267fa17205b1319f047a` |

Contracts are pinned at
`4a5ff1648887f606bf16c2f19ca5c648e20381aa2239c8f94636cc51082d678e`
and `86b92d029c56b097cbb69a99532607889bf36b13dc677c8f85e1a5201e67062e`.
Flat preparation manifest: 28098 bytes / SHA-256
`0d0a344ebac99fc5c53d49ad00c0b0ae3262257e52135aedf3c94e4db1ca736d`.
All 180 manifest entries independently rehash exactly.

## Delta findings

Inspected all three source diffs and independently reversed their 14/7/4
counted substitutions to the accepted D230 sources. Changes are fixed
attempt/HEAD/session/source/artifact/path/inventory bindings, scope names,
the new type/window/field/enum tables and corresponding helper pins. No
descriptor, transport, child/reap, deadline, closure or capture lifecycle body
changed. Executable identity literals, not just reversal metadata, were checked
against the fresh attempt. Both flash-plan sketch spans are now 55376 bytes;
the complete 263680-byte loader remains bracketed before and after SRAM.

The new first_failure window derives from this image's private member and
FailureRecord type. Its eight fields match the accepted D231 declaration:
reason, site, cleanup, cleanup_ownership, packet_offset, packet_size,
payload_size and ownership_evaluated. Scalar widths are one byte. FailureSite
and CleanupDisposition names/order match the uint8_t source enums; their exact
widths and values are queried and checked. Current inventories are nine types
including bool, eleven windows, 64 fields and nine enum types, with 533 query
lines in the same four bounded offline children.

Every new member offset/extent and type layout is queried anew. Existing checks
bind object size/section to current ELF .data copy or bss-zero intervals, enforce
object/window/field bounds and nonoverlap, and reject incompatible scalar or
enum answers. No previous recorder address supplies a missing field. Alignment
padding and merged bounded read ranges derive mechanically from the accepted
fresh ABI. Invalid enum/bool observations retain raw evidence and prevent a
successful collection; coherence remains UNPROVEN.

The complete caller still checks the ABI's actual commands, twelve remote file
identities, board/local closure and recomputed summary before binding a spec.
It retains the /recorder source mapping, fixed adapter/source capabilities,
read-only retrieval and local export recomputation. Full current flash equality
must precede SRAM, with final comparisons afterward. Session equality remains
an observation rather than an acceptance shortcut.

## Host evidence and concrete continuation

Saved tests01 has seven methods PASS, no failures or skips. Inspected fixtures
cover the new exact enum/query inventory, malformed first-record extent,
offset/overlap/width rejection, every new enum value, progress decoding and
invalid bool/enum bytes. The valid/malformed layouts are synthetic, not target
addresses. The real file-only owner validates the historical input/staging
closure and composes four commands/twelve file pins without transport; only
the future collector clean-HEAD check is stubbed for this source fixture.
The real capture caller constructs the adapter and projected action plan with
the complete new flash spans. Accepted unchanged D230 lifecycle evidence is
reused; no broad suite or native action is claimed here.

After the active D233 run closes, root may commit this exact isolated package,
use its clean collector HEAD for one file-only --check-only and --execute, and
retain all native_abi01 evidence. Historical compile HEAD and collector HEAD
remain distinct. On successful strict reconciliation of the fresh ABI, root
may use its exact abi.json hash with --prepare-bindings, which exclusively
writes the three specified capture files. Commit that mechanical binding and
use the new clean same collector HEAD for one capture --check-only/--execute.
The contracts' literal commands and absent-only local/remote owners apply.

No second source-review chain is needed for those exact mechanical bindings.
Actual ABI results must supply the new addresses and layout; actual capture
must independently prove the image and reconcile raw results/closure. Failure
consumes an owner with no retry, cleanup, reset or upload branch. MAIN and the
loaded firmware are not changed by this diagnostic workflow.

Acceptance establishes preparation only. The original native reason remains
unknown until a valid observation. First-failure fields are non-atomic;
NOT_ATTEMPTED or an unevaluated ownership sentinel does not prove cleanup was
attempted. Packet offset does not prove shifted or received bytes. No UART
delivery, target timing, physical qualification, motor authority or phase gate
is inferred.
