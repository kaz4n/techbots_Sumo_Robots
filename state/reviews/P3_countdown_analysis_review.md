# D127 offline countdown analysis scoped review

Date: 2026-09-24. Reviewer: separate same-model reviewer, independent of the
analyzer implementation and public test author. Earlier read-only exploration
and D125/D126 reviews are disclosed; the reviewer authored no D127 production
code or public oracle. All earlier evidence remains immutable.

Status: PASS for the bounded D127 offline analysis slice. No open BLOCKER or
material production finding. The public fixture finding below is resolved;
original failures remain preserved. Production SHA-256 prefix `1a91b857` is
unchanged, and the corrected new oracle `ec9167bd` is accepted. This concerns
offline arithmetic and evidence handling, not physical acceptance or GATE P3.

Scope: adopted `P3_countdown_analysis_contract.md`, P3.1, D073 wire semantics,
D074 validator interface, `tools/analyze_countdown.py` and its documentation.
Reviewer edits are confined to this report and its raw directory. No firmware,
configuration, established tests, board operations or evidence input is changed.

## Contract and static source trace

- The supported historical hold is explicitly declared as 5000 + 100 ms.
  Current firmware configuration is not read to infer older run settings.
- The tool loads the exact sibling D074 validator and retains its report
  unchanged. Failed format, consistency or manifest validation rejects an
  attempt without upgrading provenance or making a physical-origin claim.
- Cohort input and reopened event/summary files use bounded reads, regular-file
  checks and before/after descriptor/path identity checks. Reopened bytes, byte
  counts and row counts must match the validator's accepted snapshot. The
  accepted manifest is not reread; no atomic cross-file snapshot is claimed.
- All event ordinals must strictly increase. Only START_RELEASE, GO and
  receipt-derived FIRST_NONZERO_DUTY are timing markers. Modes, release identity
  and FIRST wheel-byte payloads receive their specified checks; other event
  payloads retain only existing format validation.
- A valid interval remains diagnostic when GO, closure or complete recording
  evidence is missing. Half-range or backward chronology cannot publish an
  apparent early interval. Normal wrap and equal timestamps are supported.
- SEALED state, positive epoch, observed GO, no loss and declared closure are
  separate qualification requirements. Every reused three-file hash triple
  is invalidated, including its first occurrence. All attempts remain reported.
- Cohort statistics use qualified intervals only. Exactly 50 are required;
  hold is inclusive at 5,100,000 us and spread is strict below 5,000 us. CLI
  success follows timing PASS only. All verification/acceptance flags stay false.
- No production shell, subprocess, network, board or file-write path is present.
  The original CSV validator remains outside the change scope.

## Independent probes and initial public finding

`P3_countdown_analysis_review_raw/private_freeze.json` binds seven test methods
derived from the adopted contract and established D073 fixture definitions.
They cover partial early intervals versus ambiguous chronology; loss/closure
diagnostics; 108 FIRST payload combinations including signed-byte boundaries and
quantization to zero; repeated-bundle group invalidation; 50 unique synthetic
bundles at hold/spread boundaries; post-validation replacements with unchanged
size and restored mtime; and owner/ordinal/marker contradictions.

The snapshot probes also require one read each of frames and manifest. All
seven methods pass on their first Linux execution after the public freeze and
also pass natively on Windows, using the identical frozen oracle. Separate
receipts are retained as `private_linux.*` and `private_windows.*`. Generated
evidence is synthetic, temporary and independent of hardware. Source review
found no material production issue.

The initial public Linux run reports four failures among 71 methods (33 new,
38 established validator methods). The Windows run reports five among 33 new
methods. Original logs and frozen source are retained. The four common failures
are an inactive injection hook in `tests/tooling/test_countdown_analysis.py:120`:
the helper patches an independently imported validator module, while the
analyzer loads its exact sibling as a separate module instance. The hook never
runs. This also leaves the apparently passing manifest-read-once case without
its intended mutation. The supported correction is confined to the new,
unaccepted oracle: wrap the actual loaded analyzer instance's public validator
boundary and assert the injection ran exactly once, retaining every assertion.
Changing the production loader to fit an import assumption is unwarranted.

Resolved: the separate test author changed only the new helper and its ModuleType
import. It loads one analyzer instance, identifies exactly one module dependency
whose path is the exact sibling validator and whose public validate_bundle API
is callable, wraps that API, analyzes through the same instance, and requires
one hook invocation. Every existing test assertion remains. The corrected full
Linux run passes all 71 methods without skipping, including actual symlink and
descriptor checks and the previously vacuous no-reopen mutation. No production
change was made. All original seven frozen files are archived under the root's
raw `original/`; only the new oracle changes between the two public freezes.

Windows separately cannot create real symlinks (`WinError 1314`). Real-symlink
coverage must remain mandatory on Linux; no full Windows PASS is claimed from
the failed first run. The independent private probes use ordinary file-open
interception and exercise actual post-validation rereads on both platforms.

## Final evidence binding

`P3_countdown_analysis_review_raw/evidence_bindings.json` records PASS for 74
checks: current seven-file public freeze, private oracle and contract bindings,
all seven archived initial files, the sole approved oracle correction, all 38
established locked files, both private outcomes and retained public receipts.
The two pre-execution contract clarifications concern main's integer return and
descriptor identity checks; only that contract hash changed in the private
freeze, whose original version remains retained. Private test code is unchanged.

| Verification | Result |
|---|---|
| Corrected full Linux tooling | 71 methods PASS: 33 D127 and 38 unchanged D074 validator methods |
| Independent Linux private probes | 7 methods PASS |
| Independent Windows private probes | Same 7 methods PASS |
| Established locked files | All 38 exact |
| Existing CSV validator and its tests | Exact original bytes |
| Initial public failures | Linux four; Windows same four plus unavailable symlink privilege; retained |

Root receipts supply the public runs; this reviewer independently executed the
private probes, reviewed the fixture correction and bound current file hashes
to the receipts. No full public Windows PASS is claimed. No firmware, board or
physical test was required or performed for this offline slice.

## Limits

Arithmetic PASS may come from synthetic data. Declared origin, hashes and closure
do not prove hardware provenance, a common physical attempt, independent runs,
transport delivery, calibrated timing, wheel movement or a human phase gate.
One ordinary timestamp wrap is supported; multiple unseen wraps cannot be
established. No tuning or production configuration change follows.

Next action: root may record and commit this scoped acceptance. Real P3.1
observations, identified evidence and the human phase gate remain separate.
