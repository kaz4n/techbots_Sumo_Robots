# D147 native TLS extension code review

25 September 2026, Asia/Dubai. Separate fresh-context, same-model read-only
review; not cross-model review or a human gate. Only this review file is owned
by the reviewer. Reviewer performed no implementation execution, board action,
build or download; coordinator test receipts were inspected read-only.

## Scope and identity

- Contract: `588e1ad8e25be604e9b048477dd7f67e716ea206ab88b8485de5d54e99437859`.
- New source in `2d39b8f9`, `P7_static_link_probe_raw/static_native_artifacts.py`:
  `cd52a29a32b8ae1da4bea51dd55d9011386dd4be0ca537195bb124d13031d6c0`.
- Frozen base: `d30372dd4b8fb8c2661d00affc4a215cc88e3f62511995ff6303827bed4b7368`.
  Rehashed both implementation files; inspected the complete base and extension,
  D147 design review, D142 contract and D146 provenance validation/assembly.

## Findings

No BLOCKER, MAJOR or MINOR source findings.

At extension lines14-26, both supplied sources require exact bytes, positive
bounded sizes and the fixed hashes before compilation/execution. Only the frozen
Python bytes execute in a new dictionary. The assembly never executes. No caller
objects or existing module/class definitions are changed; the extension creates
a private subclass of the freshly loaded base.

At lines32-48, every reserved name or type6 symbol must match the complete fixed
value/size/binding/type/visibility/ABS tuple and nonlocal partition. The frozen
base calls this dispatch for every table entry (base lines255-261), so wrong-type
shadows and additional/anonymous TLS entries cannot avoid it. Each of six names
must appear exactly once. All three images run the same checks (lines63-69).
The repeated offset8 belongs to two different required names and is permitted.

All other symbols use the original check unchanged. Inherited construction
retains ELF/table/name bounds, section/program/TLS/relocation restrictions,
layout/segment permissions, essential-symbol and initialization checks. The
wrapper retains exact input bounds, normalized allocations including empty
records, entry identity and initialization equality, then invokes the original
BIN/both-ZSK checks and report directly on the unmodified artifacts (lines57-71).

At lines72-74, the distinct `STATIC_NATIVE_TLS_LAYOUT_PACKAGE_PASS` status and
exact native_tls fields provide sorted, fully checked symbol records. No
consumer is changed; `run_static_probe.py:287-290` still requires the old exact
schema/status and rejects this result. The code performs no filesystem, device, subprocess,
clock, environment or network operation and makes no source freshness, native
ABI, runtime, physical or gate claim. D146 provenance supports the fixed metadata
exception; it does not establish later caller/source/artifact binding.

## Verification and verdict

**PASS for D147 pure host implementation and test evidence; no open findings.**
Reviewed the independent frozen 19-method suite, synthetic fixture and plan
without executing them. Coverage includes all six names in all three forms, every tuple field,
cardinality/shadows, source admission before exec, input/result/module isolation,
base structural/package negatives and allowed diagnostic differences. The
freeze manifest records implementation-independent authorship and exact inputs;
SHA256 `e1cd0763877276c279718003deced702d8f6e902958b5db7382eb798b167a8e4`,
committed in `3462c6f8` before first execution.

Inspected actual JSON/terminal output under
`../analysis/P7_static_link_probe_raw/native_tls_host/`:

- `native_first`: exit0, all19 methods PASS in7.421s on unchanged `cd52a29a`.
  Independently rehashed all10 pinned inputs: match recorded before/after values.
- `legacy_public`: exit0,39 methods PASS; `legacy_consistency`: exit0,6 PASS.
- `legacy_private`: exit2 because the invocation omitted required `--source-ref`;
  argument parsing stopped before tests. Original usage error is retained.
- `legacy_private_working`: adds only `--source-ref working`; exit0,6 PASS with
  unchanged private oracle `2b2e4f4c`. No implementation/oracle repair occurred.

Total:19 new and51 existing methods PASS. These are the coordinator's observed
synthetic host runs, not a separate reviewer rerun. Git comparison confirms no
changes to either implementation or the original public/private suites since
`2d39b8f9`. No actual native artifact validation, consumer integration, runtime
qualification, upload/reset, physical evidence or human gate follows from this
review. Preserve the original D144 rejection and separately scope any next step.
