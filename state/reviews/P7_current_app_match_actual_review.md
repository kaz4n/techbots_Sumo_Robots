# D185 actual MATCH compile-only review

25 September 2026, Asia/Dubai. Separate same-model Codex reviewer with reused
context; not a fresh-context, cross-model or phase-gate review. Read-only actual
receipt and artifact-binding inspection; no reviewer test, compiler, transport
or device execution. This new review is the only owned edit.

**PASS for checked target compilation and receipt consistency. No material
finding within this compile-only scope. Memory fit remains conditional.**

Reviewed execution HEAD `80c059f7a3b2e173198f484e3cf7a24d2af44fee`, caller
`aed3fbf4`, source
`37a2099f6938baf6430cfed2b5a002793d9748820fe0876e9cd039fd94330c29`,
ADB `2629958581`, boot `55c386b9-fe6d-4388-a7f4-1d91e0bb49d8`.
Profile MATCH/Immediate uses FQBN `arduino:zephyr:unoq:wait_linux_boot=no` and
both C/C++ flags `-DMATCH=1 -DMOTORS_ALLOWED=1`. Intent, actual compiler argv,
canonical command and returned artifact/receipt UUID
`1fcc7d57d66848cd9ea604297538e125` agree.

Evidence: `state/analysis/P7_current_app_compile_raw/native_match01/result.json`
SHA-256 `43b6113b0d3ef58c582db378283cd521062a7415704a47307dc5f9faea813a68`;
`build/app-receipts/1fcc7d57d66848cd9ea604297538e125/verified.json`
SHA-256 `35ec6c34aae2882af536e4455280597f15929f1352edc30d1a4ac9d9dd8666f9`.

The reviewer independently checked all 21 transport results: exit zero, empty
transport stderr, maximum 16,154 command units within 30,000. All ten child
receipts report COMPLETED/exit zero/reaped/no timeout; encoded stdout/stderr
match their retained local bytes and lengths. Exactly one property query and
one compiler ran, with respective 60/720-second deadlines, five-second reap
bound and jobs=1. The terminal result is COMPILE_CHECKED with all seven closing
checks PASS and no first error.

Both F166 inventories match their pinned baselines after the admitted boot
replacement and timestamp-only projection; closing inventories match admission.
Closing identity preserves UID1000/arduino, boot and CLI hash, no conflicting
processes, and 14,004,715,520 bytes available on the board. All 115 input pins
remain exact: 104 source files plus 11 caller/dependency inputs. The 103-file
staged mapping, local staged bytes and before/after remote source maps agree.
The existing canonical source was verified and reused; no source push occurred.
The stage omits `src/app/.gitkeep` under the existing mapping. All 18 installed
hashes agree before/after compilation and with the receipt; all 22 installed/
artifact hashes agree with actual postcompile hash output.

Comparison against D138's `state/analysis/P7_readiness_native_raw/`
`retained_artifacts_after_cleanup.json` confirms exact equality of:

- Final ELF: `cb5fbb53ce4089ef682977a66fd5337491f150f17ca2cfdcd150a0dd6bca07d4`.
- Exported package: `004d51bffd3b04803e55cadf44087b9e1faae884690a9f46ec56232def5c724f`.

Current debug ELF `2245bacd...` differs from D138 `85db9e56...`; current temporary
ELF `1517b2ea...` also differs from D138 `d783147b...`. No fresh debug/ABI query
was performed. Current installed loader SHA-256 remains
`39d4a4fd47241663323f6e04f94dd8f5a9f9ad6582cf1df37f9709b74026adcd`.
Final-file equality and that loader pin support reuse of D138's byte model and
62 resolved import requirements, not a fresh ABI result or actual allocation.
Its `account_validation_stdout.txt` retains only conditional pristine-pool fit:
261,280-byte ordered peak in 262,144 bytes, 864-byte span and 860-byte largest
payload under aligned persistent flash-peek assumptions at `0x08100010`.

This is not measured live RAM, stack or WCET. The default profile's modeled
592-byte deficit and earlier static full-app I/O fault remain unresolved. No
upload/reset, MCU startup, physical acceptance, motor-run permission or human
gate follows from compiling MATCH. The MATCH owner is consumed; retain it and
its original receipts. Any later deployment requires its own qualified scope
and authorization.
