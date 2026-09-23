# Next offline B8 task audit - 2026-09-23

Read-only audit by /root/csv_implementation after implementation ownership ended;
this is planning input, not independent safety review or implementation approval.

Smallest next task: contract-first host-only validator for existing CSV evidence
files, potentially one local-file Python CLI with independent fixtures. A new
scoped decision under D-051 must precede implementation; D-073 authorizes only
formatting. Do not label it dump_match.sh, a live recorder or a transport framework.

Define exact-schema/numeric-range/raw-hex agreement and retained-count checks.
Preserve INVALID/CLAMPED data, unknown raw codes, insertion order and wrapped/equal
timestamps. Report file integrity, known recording loss and attempt completion
separately. Require supplied firmware/config/rate/target provenance; never infer
historical rate from the current checkout. Hashes show local file integrity only.

Rows contain caller ordinals but no session/epoch identity. Separate files cannot
prove common attempt provenance. epoch_token is not globally unique. Accepted
lifetime status counts may include overwritten records, so equality with retained
row status totals would be incorrect. Missing manifest/closure metadata is unknown,
not inferred success. SEALED is not live IDLE; loss=false is not a complete dump.

References: P2_csv_contract.md metadata/deferred envelope; P2_attempt_recorder_contract.md
rules12/13; tools/README.md receive-only/runtime restrictions and deferred tools;
P2_hal_bench.md B8/integration; BEHAVIOR.md B15 IDLE-only dump. Runtime cursor/owner
integration, Bridge paths, authentic deployed identity, full RAM/WCET and physical
200s/no-gap B8 acceptance remain pending. No further files or hardware were changed
by the auditor. Coordinator selects the next exact contract at resume.
