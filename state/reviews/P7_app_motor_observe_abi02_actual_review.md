# D194 ABI02 actual file-only observation review

26 September 2026, Asia/Dubai. **PASS for actual file-only ABI collection and
saved-summary consistency; no material finding.** Reviewer `/root/fresh_review`
is a separate same-model reused context. This review independently read local
receipts/source and decoded their data; it did not import subjects, run tests,
invoke native tools or contact the board. Only this review file was written.

The checked HEAD is `efadbe5c9e920114919e016b5af6952cda9efb6c`. Actual check-only
and execution returned 0. The checked command uses 5565 UTF16 units, four file
children and the exclusive `native_abi_static02` owner. Invocation output agrees
with the saved inputs and local closure. Attempt01 remains FAILED and consumed;
its raw result `e83afc5f...` and closure `589b78d1...` remain unchanged.

## Receipt bindings

All paths below are under `state/analysis/P7_app_motor_observe_compile_raw`.

| Receipt | Bytes | SHA-256 |
|---|---:|---|
| native_abi_static02/inputs.json | 27138 | `a43d40bf2ff526c9247fef3f48da3355d43cbe728fb00e5dc81bc4a22cf7d1fe` |
| native_abi_static02/result.json | 893020 | `a5e67635f43b96b813885687fbafe743cfc3ec6a93d089a66453ca574c0676da` |
| native_abi_static02/abi.json | 3704 | `dfc34596b65d3a82e21e28c3acf9fb1535bec2eb3b489d270c593c9fe3eab3a7` |
| native_abi_static02/local_result.json | 275 | `3f17b83efc79026b46d519646798f70d9cf898b0c4a0bef2e06e6da4da0e84a7` |
| native_abi_static02_invocation.json | 1336 | `62cec19c01ffb45aa2ea28029c44892e9b38df5555b790170bf9aedabd947c7d` |

The reviewer independently hashed all 140 actual local input pins and all 142
coordinator freeze pins: all match. Wrapper `a0a5aef1...`, supplementary contract
`772615cd...`, original wrapper `497f756e...`, source tree `3a08ddeb...`, D193
manifest `aa350c65...` and successful compile/artifact receipts retain their
reviewed bindings. The 12 remote pins are unchanged from attempt01 and agree
with the D193 artifact records, including ELF `2fd70da8...`, debug ELF
`33e3b34d...`, package `85b05c56...`, loader/TLS and the two pinned file tools.

## Actual commands and closure

The reviewer independently composed the expected four argv lists from the
preserved type/window definitions and ABI02 contract; all equal the actual
receipts and saved intent. The GDB argv contains 297 entries, uses the pinned
debug ELF with `-nx -nh -batch`, disables autoload and function calls, and has
only the prescribed file queries. The polls ALIGN query is exactly
`p/d alignof(unsigned int)`; SIZE and LAYOUT still query the actual member.

All four children exited 0, were reaped, did not time out and retained the
60-second child / 5-second reap bounds. Canonical Base64 and exact byte counts
match all eight streams. Stdout sizes are 283, 281, 158577 and 500150 bytes,
each below 1 MiB; every stderr is empty. Remote scope is
`D194_STATIC_FILE_ONLY_ABI02`, status OBSERVED, first_error null. The closure has
exactly the 12 expected file checks plus board identity, all PASS. Identity is
arduino/UID1000 with no conflicts and the expected boot
`55c386b9-fe6d-4388-a7f4-1d91e0bb49d8`. Local closure reports one transport,
STATIC_ABI_OBSERVED, null first_error and local PASS.

## Independent numeric interpretation

The reviewer independently parsed the raw text, without calling the project
decoder. Every one of the 20 SIZE/ALIGN/LAYOUT groups and 11 OFFSET windows
matches the saved summary. All numeric tags are unique; all sizes, power-of-two
alignment bounds, window addresses and containment checks pass.

| Observed item | Result |
|---|---|
| Diagnostic symbol | Unique LOCAL OBJECT `_ZN12_GLOBAL__N_110diagnosticE` in ET_EXEC section 5, writable NOBITS .bss |
| Runner | Address `0x20013960`, size 169736 bytes, alignment 8 |
| Runner interval | `[0x20013960, 0x2003d068)` |
| D193 initialized BSS interval | `[0x20013960, 0x2003d3e8)`; Runner wholly contained |
| Polls member | Current type `unsigned int`, size 4, observed alignment 4, offset 168572, address `0x2003cbdc` |

The raw .bss address/size agree with the D193 structural artifact report. All
11 selected windows fit inside Runner and satisfy their observed alignments.
The polls type block is uniquely contiguous and exact, confirming the type
again in this successful attempt. Its recorded provenance still points to the
preserved failed-attempt member observation.

The raw readelf symbol size is `0x29708`. Independently converting it gives
169736, agreeing with GDB Runner size. Replacing only that size token reproduces
every normalization metadata field: original 158577 bytes / `b3542b0d...`,
private projection 158576 bytes / `c908abee...`, with the original receipt
unchanged. No hex/decimal ambiguity or stale address remains in this summary.

This establishes the compiled files' observed layout and its evidence bindings.
It does not show MCU contents, execution of initialization, firmware runtime
behavior, fault reproduction or repair, live RAM/stack/WCET, motor permission,
physical acceptance or a human phase gate. Any subsequent run needs its own
scoped preparation and admission; neither consumed ABI owner may be reused.
