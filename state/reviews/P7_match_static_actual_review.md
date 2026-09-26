# D241 current production static MATCH compile: actual review

27 September 2026, Dubai. Separate Codex reviewer with reused project context.
Read-only saved-source, receipt and artifact-report reconciliation; no reviewer
test suite, native command, upload, reset or MCU observation. This report is the
only reviewer edit for the actual compile scope.

**PASS: current production static/Immediate/MATCH1/M1 compile-only evidence.
No open material finding.** This establishes the checked target build and static
layout/package result. It supplies no motor-run permission or runtime acceptance.

## Exact execution and evidence

Native HEAD `6306c88e54353e7864a86656614402631a5a3b9c`, attempt
`native_match01`, source
`9337c580d3451de6f2cfe02ebcaa19abf75b147cf7e35bca34defcc562ed1c3e`.
The frozen execution worktree was sumox-match-static-native-20260927. Durable
MAIN owner is
`state/analysis/P7_match_static_raw/match-static-match-m1-1d657ca567ed`.
All 993 original native-owner files, 1748556 bytes, independently compare exactly
with the MAIN copies; the separate outer streams are retained by root.

| Owner file | Bytes | SHA256 |
|---|---:|---|
| inputs.json | 14176 | `641691b75bbfd26508dfe959b2a9fcde18a85a52bb45ebcaf9338c6fd7fc8846` |
| intent.json | 1146 | `12741b0877d8b3c1109635bf2135f182eceffd77be1dca44f5c8ebe18c68da7c` |
| staged_files.json | 10074 | `2aee7687433513a0bbcd648dc77d7d47630831c7e59a13e82f393f6b1c7b1c75` |
| result.json | 1973 | `ca9dc58f111964462d3a4549271dc09f7547e173b905410c261271026df44ee7` |
| artifacts.json | 9732 | `66d970fbe6de60e3a0a1601d0c8437005ec144366292bc97c47be262e30b1146` |

Independently rehashed all 135 current native input files against their manifest
and exact historical Git blobs. All 105 staged files match, totaling774215 source
bytes. Recomputing the ordered staged-path/content digest gives the source above.
The accepted D241 source/host review remains
`P7_match_static_review.md`, SHA01851b69; no later firmware substitution occurs.

## Actual tuple and lifecycle

The target returned the exact canonical FQBN
`arduino:zephyr:unoq:link_mode=static,wait_linux_boot=no`, ordinary app.ino,
static link mode and Immediate boot. MATCH=1/MOTORS_ALLOWED=1 and all eight
commissioning/probe macros=0 agree in intent, both C/C++ properties and artifact
identity. Both package recipes contain `-prelinked -immediate`. Independently
applied the pinned D241 read-only policies to the complete query and compile
responses: all controlled metadata and recipes pass. Their only differing
returned properties are the expected query/compile time stamps.

Exactly one expanded-properties query and one compiler ran. Actual child argv
matches the saved canonical command plus the inherited explicit executable,
empty CLI configuration and `--jobs 1`; it contains no upload operation. Query
took1.651079 seconds within60, compiler222.474646 seconds within720, both reaped
with exit0/no timeout and the five-second reap bound. The overall execution
closed0 in the recorded413.746 seconds. Coordinator result spans
22:54:24.882985 through23:01:17.643770 UTC on26 September.

All235 transport receipts exit0 with empty stderr; maximum command length is
29368 UTF-16 units below30000. All nine checked child receipts are COMPLETED,
reaped/exit0/not timed out, with consistent decoded stream lengths and empty
stderr. The retained child stdout is the original base64-encoded LF JSON;
compile/properties convenience JSON copies use Windows physical CRLF. Removing
only that physical line-ending conversion yields exact equality; JSON content
is identical and neither original stream was discarded or rewritten.

The final result is COMPILE_CHECKED, query_calls=compiler_calls=1,
first_error=null. All nine local/identity/initialization/builtins/source/installed
pin/override/artifact/artifact-source closing checks pass. Admission and closing
remote source maps agree. The29649-byte artifact-source packet has the same
descriptor identity and SHA256
`6aafef6c2d0850ade3b91218bd5ae222d3b07f3f8cd2d88afd4a0250ed8c39d3`
after construction and at closing.

## Native artifact and static memory result

Initial, final and saved artifact reports agree exactly. The complete file set,
layout and nested artifact hashes reconcile; loader, TLS source and file closing
checks all pass. Status is STATIC_MATCH_APP_LAYOUT_PACKAGE_PASS with nested
STATIC_NATIVE_TLS_LAYOUT_PACKAGE_PASS, six exact inherited TLS symbols and no
weak undefined symbols. The pinned native validator enforces the full ELF/load
body and both exact Immediate/prelinked flag0x06 package forms; acceptance does
not rely solely on command text, header presence or reported size.

| Artifact | Bytes | SHA256 |
|---|---:|---|
| Flat package and identical export | 92092 | `7895a4d8991bd2158e63c69cb37ebcdc4f39632311a1dbf47401c3a34f664c86` |
| Raw binary | 92076 | `b3191e0c6d1ec5ed188f2438efd37b4c8ee6082104bab33ce4e428f7cb202679` |
| Final ELF | 165836 | `ba9766a8a207564fa0d2bd25dd6472a16f176f09740eda4689e167e81536a666` |
| Debug/temp ELF, identical bytes | 1700052 each | `6e09b5fa48739aa32564de4379a48686dd9ccfc545e7d6e34764a560514677d5` |
| ELF package | 165836 | `92828459482ab1e98a7775583030bf7205dafe9010c057f2bfa00e73608f9a30` |

The target validator reports216 copied data bytes,170456 bytes in the BSS zeroing
span and170648 bytes in the complete BSS section. Its structural RAM range ends
at537121792 and leaves91280 bytes before its bound. The independent Arduino size
summary reports170868 bytes of globals and91276 remaining; the four-byte
accounting difference is retained explicitly. Structural flash remaining is
694340 bytes. These are file-derived layout results, not live free RAM, stack
high-water, startup correctness or WCET measurements.

Artifact hashes/layout are observed by the source-bound target validator; this
review did not newly download or locally inspect binary artifacts. No image was
uploaded, no motor permission was supplied, and no human phase gate or physical
qualification follows. The production static compile/tooling gap is now closed
for this exact current source and tuple; qualified deployment and physical
operation remain separate.
