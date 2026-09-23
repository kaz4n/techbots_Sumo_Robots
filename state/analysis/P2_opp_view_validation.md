# D107 opponent-view software validation

2026-09-24 Asia/Dubai. Contract cd5d784, subsequent pre-test clarifications and
explicit build correction in P2_opp_view_contract.md. Implementation Runner
1be9bc511d0b1af5d1a95f664f20e93e0779c0cd617596cd272fe615ea1c55e3.
Status: IMPLEMENTED/HOST-TESTED/TARGET-COMPILED/independent scoped review PASS.

One actual sensor and matrix owner, literal seven-channel strip, full raw status
and timestamp retention, invalid/unknown indication, bounded polling and visible
missed/error counters. Default grants are false; no motor, UART, Robot or Runtime
owner. No upload or hardware input grant was introduced.

## Independent host evidence

Independent author used the contract/public headers without implementation-body
reads. The same-model context had prior D104 work; this is separate-context
spec-derived testing, not cross-model review. Frozen tests remained unchanged.
See P2_opp_view_raw/author/validation.md, coverage.md and run2_summary.json.

| Check | Actual result |
|---|---|
| Pure runner normal and ASan/UBSan | 24 cases /40,087 assertions each PASS |
| Real new native binding/default sketch with substituted existing owners | 2/51 each normal/sanitizer PASS |
| Six invalid-config profiles | 1/29 each PASS |
| Alternate all-high/all-low polarity, all128 masks | 16,002 assertions each PASS |
| Forbidden MATCH/motor flag combinations | Three expected compile refusals |
| New checked-policy tests, WSL with real dangling symlinks | 15 methods PASS unchanged |
| Existing app policy/override/runtime-inert policy | 85 methods PASS unchanged |

The original zero-TICK compile failure is retained. Explicit constexpr division
guards fixed it without changing assertions or warning flags. An interim fix
changed passive state; the reviewer reconstructed its known exact hash with that
provenance disclosed, reproduced eight failed assertions and verified the same
regression passes final1be9bc51. Original and corrected evidence remain separate.

Root's first invocation of the85 methods omitted tests/tooling from PYTHONPATH,
causing19 import errors; the recorded corrected invocation passes. No production
or test change was made to resolve that invocation error. Command receipts are
P2_app_build_raw/d107_policy_existing*.{json,txt}. New author policy receipts are
P2_opp_view_raw/policy_author; reviewer receipts are separate.

## Target source lineage and rejected artifacts

All target commands were compile-only on board Linux through ADB. No MCU reset,
upload or new run occurred; the MCU remains frozen in exact D1042bd817c4.

| Source | Scope |
|---|---|
| 9fb6f9bf00e5abe5095e7e079eaad118a2aa8ec6efb6390994a983d092d72d22 | Initial generic95-file build, before zero-period fix |
| 367814a050f0d2f2482303d39406f2622d8cb546f147200c91df8e4b87725a8e | Final runner, generic95-file build |
| 332787f09d3cb35a96f4cc1e3caad535ac24103372f4894ab56bf7329e3d0451 | Checked96-file build; adds bench README and D108's separate two-coordinate UI correction |

Both generic builds compiled but are **TARGET-REJECTED D107-R3**:14 initializers
and retained Bridge/Serial owners/allocating imports are outside the intended
bench scope. All-false Runner grants cannot suppress pre-setup constructors.
Retained imports are not proof that every imported operation executed. No rejected
artifact was uploaded. Frozen sources and all three ELFs/packages are retained.

The literal opp_view build now uses existing native-app-v1 checks: exact CLI/core,
installed dependency hashes, preflight effective commands, no selected libraries,
actual compiler result and artifact hashes. Only inert default/Immediate profiles
are eligible. MATCH, profile files/symlinks and uploads fail before transport.
Other existing routes/constraints remain unchanged. Tool source hashes and mocked
route/failure tests are in policy_author and the separate review.

Checked target receipts and final source/ELF/startup/import/conditional-memory
review are recorded in P2_opp_view_raw/target_332787f0_*_checked and
state/reviews/P2_opp_view_review.md. The collector initially expected95 files and
correctly refused the newly included README; its explicit95+README count correction
and successful retry are recorded, without weakening the exact source hash check.

Physical polarity/ranges/sixty-second false-hit acceptance, optical confirmation,
clock calibration, full-app loaded RAM/800us WCET and human gates remain pending.
Simulated callback duration verifies accounting only; the closing C excludes
report publication/return instructions. No physical measurement is invented.

## Final checked artifact acceptance

Separate same-model reviewer closed R1/R2 (zero-period/passive guards) and R3
only for checked332787f0 default/Immediate. Default receipt798ea29ae9454bb8aa3d7a1ebc0fa93a;
Immediate86bea3bf10b54dd984387fa72369b603. Both retain ELF SHA256
2a20fbc108befc40b681cbb6d2f6450b05370201f8048157158519f7e4c462af.
Each has14,572 ELF bytes,3,733-byte compiler payload and conditional ordered
loader peak4,496 in262,144 bytes; remaining span257,648/largest payload257,644.
Packages differ by the recorded startup option. This is a loader model, not a
new loaded-RAM or timing measurement.

Actual startup has one passive Native.port/Runner initializer, all-false setup
and empty thread bounds. No Bridge/Serial/MotorGate/Runtime owner is retained.
The retained core thread-start helper has empty bounds; its import alone does
not establish an actual created thread. The exception allocator is an abort
stub, not a success path. Exact disassembly/relocations/imports/ABI are reviewed.

Source identity uses the Windows producer's existing Path ordering. Addition
of uppercase README makes POSIX string ordering yield a different aggregate;
review explicitly checks producer ordering and every individual file hash.
This artifact claim does not promise cross-platform aggregate-hash equivalence.
Both generic rejected artifacts remain rejected and preserved.
