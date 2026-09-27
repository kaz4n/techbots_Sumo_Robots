# D244 B7 native compile review

Date: 2026-09-27. Reviewer: independent `b7_reviewer` subagent.
Verdict: **PASS_NATIVE_COMPILE_ONLY**. No open material finding in the three
closed compile operations reviewed here.

The reviewer read admission/provenance records, copied raw evidence and artifact
reports, independently checked retained file hashes, and compared production
artifact identities. The reviewer executed no compiler, tests, board transport,
upload, reset or motor action. Only this review report was written for this
scope. The accepted source/host report remains unchanged at SHA256
`f00d39fea72d8fd6b14f91d732982f9d513ce714a3cfaa647ddd1994401c5a70`.
The separately accepted D245 deployment preparation review remains unchanged at
`2fd710ec4e82e0246a8bd966b13762906c272107ac1b0dc9a3760f6806cd92a7`.

## Admission and source identity

All three builds bind frozen HEAD
`97e32fded4f36bdb759fd273965ee8ce72301753` and common application source SHA256
`85b320de79f0fe26602bd6b714d77136718f4a6ab32ba989ea8322b7b92a481a`.
The saved local check-only results passed with `board_observed=false` before
the separate compile execution. They used the checked callers in dedicated
clean sparse worktrees and the exact closed profile/flag grammar.

| Selection | Attempt | Input files | `inputs.json` SHA256 |
| --- | --- | ---: | --- |
| B7 M0 | `native01` | 143 | `e004a99ed4236340338ff5854fd194560303b1da415d62265a10546cf702b409` |
| B7 M1 | `native01` | 143 | `15e3bc502305543e66d6e36e0f6e8af857a5826a66259313c0a1302f65f9485d` |
| Production MATCH M1 | `b7_match01` | 139 | `df9f9de01dfda6ee338732de1ccd614f4a51d4b99775a40cc0767167b63a2fec` |

All three stage manifests contain the same 109 file/hash mappings and have
SHA256 `2c5635f27df73cb1b16de5c75b8457554a0d335cf4391dae0f7db37707fc7c20`.
The 147-path sparse-checkout union is a separate count. The B7 and production
input counts differ because their checked compiler adapters/contracts differ;
their common application source and staged files agree. B7 M0/M1 input file
hashes agree, and all reviewed input file hashes match the retained/current
source bytes. M0 sparse-file and staged-byte hashes were also checked during
its admission review.

B7 flags are MATCH=0, the selected MOTORS_ALLOWED value, all eight existing
diagnostic macros=0 and SUMOX_B7_BROWNOUT=1. Their FQBN is
`arduino:zephyr:unoq:link_mode=static`, with default Linux startup. Production
uses MATCH=1, MOTORS_ALLOWED=1, the existing eight diagnostic macros=0 and
B7's source default 0, with FQBN
`arduino:zephyr:unoq:link_mode=static,wait_linux_boot=no`.

Saved board identity remains UID 1000/user `arduino`, boot
`55c386b9-fe6d-4388-a7f4-1d91e0bb49d8`, CLI SHA256
`b878632298958d61fd1eb19e70ac5d2e803d83db8930bc72dc6915eee6e8f433` and no
conflicting processes. M0 created the checked common source directory; M1 and
production record `reused=true` for that source directory and each performed
its own new compilation in a distinct owner.

## Closed operations and retained evidence

| Selection | Owner under `state/analysis/` | Outer exit / elapsed | Transports | Retained owner files / bytes |
| --- | --- | --- | ---: | ---: |
| B7 M0 | `P2_b7_build_raw/commission-b7_brownout-m0-4adb205ea983` | 0 / 433.208 s | 243 | 1025 / 1,780,354 |
| B7 M1 | `P2_b7_build_raw/commission-b7_brownout-m1-4adb205ea983` | 0 / 265.829 s | 25 | 153 / 1,041,368 |
| Production MATCH M1 | `P7_match_static_raw/match-static-match-m1-9fceb7202abf` | 0 / 265.126 s | 25 | 153 / 1,039,256 |

The corresponding outer evidence owners are
`P2_b7_build_raw/native_m0_01`, `native_m1_01` and `native_match_01`.
Each retains check/compile command, output, exit/time receipts and a
`copy_closure.json`. The reviewer independently hashed all 1,331 copied owner
files, totalling 3,860,978 bytes, against those copy closures: zero mismatches
and exact file counts. Raw owner evidence was retained in commits `3baf77b5`,
`3aca4532` and `990a4749`, respectively.

Each operation reports `COMPILE_CHECKED`, one properties query, one compiler
invocation and no first error. Actual query/compiler argv include `--jobs 1`.
All recorded transports returned 0. Each operation's nine checked children
are `COMPLETED`, return 0, reaped and not timed out. Their saved argv contain
no upload, reset or monitor operation.

All nine final checks passed: local, identity, initialization, builtins,
remote_sources, installed_pins, overrides, artifacts and artifact_sources.
Opening/closing source-set observations are byte-identical within each build;
the common source-set SHA256 is
`da9d27707656cb9ae8b473e53584c4dadb121b35e6d401eed049eb5324de77f8`.
Initial/final artifact observations also match within each owner. Artifact
postchecks for loader, TLS source and files pass with no error.

## Artifact results

| Selection | Packaged/exported bytes | Package SHA256 | Structural RAM remaining |
| --- | ---: | --- | ---: |
| B7 M0 | 84,284 | `e370976cc89cf36dd70226c48813cddf3d53d298d4db9831b7b4ba7449cced0d` | 90,256 bytes |
| B7 M1 | 84,656 | `b7e2f20b8e286d5baf9488f3b8350886e6f6162ca13ee508de76a861b0191ae9` | 90,256 bytes |
| Production MATCH M1 | 92,092 | `7895a4d8991bd2158e63c69cb37ebcdc4f39632311a1dbf47401c3a34f664c86` | 91,280 bytes |

All artifact reports are `ARTIFACTS_CHECKED`. Both B7 layout reports are
`STATIC_COMMISSIONING_APP_LAYOUT_PACKAGE_PASS`; production is
`STATIC_MATCH_APP_LAYOUT_PACKAGE_PASS`. All three underlying ELF/TLS/package
reports are `STATIC_NATIVE_TLS_LAYOUT_PACKAGE_PASS`, with no weak undefined
symbols. Build and exported package hashes/lengths agree in every owner.
Raw binary, final ELF, ELF package, map and debug/temp identities are separately
bound in the retained artifact reports.

Production's 165,836-byte final ELF has SHA256
`ba9766a8a207564fa0d2bd25dd6472a16f176f09740eda4689e167e81536a666`.
Both that ELF and its 92,092-byte package exactly match the earlier saved
production reports in `match-static-match-m1-c1c267697b5d` and
`match-static-match-m1-1d657ca567ed`. This supports B7 feature isolation in the
compiled production image. Debug/map equality is not asserted.

The associated `P2_b7_brownout_actual_validation.md` was checked against these
saved results; its counts, artifact identities and evidence boundary agree.

## Limits and next action

This verdict establishes target compilation and package/layout/provenance
checks only. The RAM figures are structural linker accounting, not runtime
free RAM, stack usage or tick WCET. Setup grants remain absent, including in
the M1 compile artifact; M1 is not thereby an operationally qualified image.
No upload, MCU execution or motor operation is evidenced by these compiles.

Physical B7 remains pending: accepted wiring/setup and source qualification,
fresh specific `STAND OK`, a half-charged pack, twenty actual full forward/full
reverse cycles, and independently observed uninterrupted uptime. The D245
host-tested deployment route grants none of those facts or permissions.
Human phase gates remain separate. Preserve the checked artifacts and raw
receipts for a future specifically authorized, qualified operation.
