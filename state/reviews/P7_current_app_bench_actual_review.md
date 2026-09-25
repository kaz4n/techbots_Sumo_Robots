# D185 actual bench compile-only review

25 September 2026, Asia/Dubai. Separate same-model Codex reviewer with reused
context; not a fresh-context, cross-model or phase-gate review. Read-only source
and actual-receipt inspection; no reviewer test, compiler, transport or device
execution. This new review is the only owned edit.

**PASS for checked target compilation and receipt consistency. No material
finding within this compile-only scope. The modeled default RAM deficit remains.**

Reviewed execution HEAD `34eb56ba3ee0204a2e11a16b0806a909454ac047`, caller
`aed3fbf4`, source
`37a2099f6938baf6430cfed2b5a002793d9748820fe0876e9cd039fd94330c29`,
ADB `2629958581`, boot `55c386b9-fe6d-4388-a7f4-1d91e0bb49d8`.
The profile is bench/default, FQBN `arduino:zephyr:unoq`, with both C/C++ flags
`-DMATCH=0 -DMOTORS_ALLOWED=0`. Intent, actual compiler argv, canonical command
and returned artifact/receipt UUID `6d9e48f8b648469787bc8623ae05d163` agree.

Evidence: `state/analysis/P7_current_app_compile_raw/native_bench01/result.json`
SHA-256 `5e9fbf08cc3816b9887ace00367c2e8cf1246fb94b6deda796995259510d9359`;
`build/app-receipts/6d9e48f8b648469787bc8623ae05d163/verified.json`
SHA-256 `0ca4bf40e9bfb977c5915c1b6c124390c5de1a007a96ab65ccc810acdb008e86`.

The reviewer independently checked all 227 transport results: exit zero, empty
transport stderr, maximum 16,154 command units within 30,000. All ten child
receipts report COMPLETED/exit zero/reaped/no timeout; encoded stdout/stderr
match their retained local bytes and lengths. Exactly one property query and
one compiler ran, with respective 60/720-second deadlines, five-second reap
bound and jobs=1. The terminal result is COMPILE_CHECKED with all seven closing
checks PASS and no first error.

Both F166 inventories match their pinned baselines after the admitted boot
replacement and timestamp-only projection; closing inventories match admission.
Closing identity preserves UID1000/arduino, boot and CLI hash, no conflicting
processes, and 14,033,997,824 bytes available on the board. All 115 input pins
remain exact: 104 source files plus 11 caller/dependency inputs. The 103-file
staged mapping, local staged bytes, and before/after remote source maps agree;
the source was newly admitted, not reused. The source/stage count difference
comes from the existing staging mapping, which omits `src/app/.gitkeep`.
The 18 installed hashes agree before/after compilation and with the receipt;
all 22 installed/artifact hashes agree with the actual postcompile hash output.

Artifact comparison against D139's
`state/analysis/P7_default_qualification_raw/final_verification.json` and
`retained_artifacts_after_cleanup.json` confirms exact equality of:

- Final ELF: `72a8bfcd320e8bfff7e5bcc6ef8607a98f9033866f3fa3d2be2cb95433e42f1d`.
- Exported package: `5b40026825ed851e27f185cb0a62d5f091c02122d620a6b68dad43201bd48f96`.

Current debug ELF `ccc8990a...` differs from D139 `e68ed750...`; current temporary
ELF `a552d742...` also differs from D139 `55222b07...`. No fresh debug/ABI query
was performed. Equality supports reusing the final-file byte model and import
requirements under the same pinned loader assumptions, not a fresh ABI finding
or successful runtime allocation. D139's ordered peak remains 262,736 bytes
against a 262,144-byte modeled pool: a 592-byte deficit; its first failing
allocation remains `global_symbols` (4,400 requested, 3,824 available).

No upload/reset, MCU startup, physical output measurement, free-RAM/stack/WCET
qualification, motor-run permission or human gate follows. The earlier static
full-app I/O fault remains unresolved. The bench owner is consumed; preserve it
and its original receipts. The separate MATCH profile requires its own fresh
admission and reviewed committed invocation.
