# Future static native invocation review

25 September 2026. Separate reused-context same-model review, not a fresh-context,
cross-model or human gate review. Read-only plan/source/hash inspection; the
launcher, runner, helper, ADB and compiler were not executed for this review.

Reviewed plan `state/analysis/P7_static_native_invocation.md`, 8,628 bytes,
SHA256 `20a85e16cb58512d46cec64ddca0500ab155a85f17280d2620f92341ed6283f2`.
Its four literal input identities match current files:

- Runner: `983e86d7eb68f437c50b4b790e96ca4520e092abe53e4d29e8ffe1a97502b208`.
- Helper: `8ba9b190c38e728013a383348c60c287b0366607f65f703161cf7f2e142d36f8`.
- Runner contract: `35473ed0eb59b9d7fd097cb25554b591ec6bd470703504e1a525219b2fdba7e7`.
- Remote contract: `a4be3733d40632b4ae79e3bbbab3300f720b8f7f13f3337d35d96dfc90373b39`.

## Findings

**MINOR, open — post-run source-read failure can discard launcher completion
evidence.** Plan lines100-103 evaluate both Get-FileHash calls inside the
completed.json hashtable while ErrorActionPreference is Stop. A missing or
unreadable runner/helper after the invocation throws from finally before that
receipt is written, replacing the launcher failure and omitting the already
observed exit code. This contradicts the planned retained completion evidence
at108-110. Smallest fix: catch each post-hash observation independently, record
null plus an explicit error for an unavailable hash, then attempt completed.json
using the original exitCode and launchError. Treat hash-read errors or mismatches
as failure. This needs no runner/helper, contract or admission change.

The pending-supplement wording at3-5 is an acknowledged editorial update: the
coordinator reports all80 host methods and both scoped reviews complete. It is
not a native authorization and need not change this plan's safety boundary.

## Other scoped checks

The launcher verifies exact runner/helper bytes before invoking the unchanged
script main with `-B --compile-only --run-id <fresh GUID>`. Main retains exact
ADB environment/path/hash admission and the unchanged transport. The three SUMO
variables are process-local and their original values/absence are restored in
finally; the native command preference is restored too.

The fixed runs parent is a coordinator prerequisite, including ancestry checks
before any launcher write. The launcher sibling is newly created without Force;
the runner's separate run directory remains absent for its exclusive claim.
The runner repeats its canonical ancestry checks before transport. Planned,
stdout/stderr and completion captures remain inside the new sibling, so the
literal plan does not overwrite old captures. No precreation of the runner's
directory, automatic parent-tree creation or cleanup is proposed.

One main invocation retains the reviewed maximum of one properties query and
one compiler dispatch. It inserts no independent board inventory, retry,
compiler wrapper, alternate policy, validator callback, upload or reset. The
plan preserves unknown nonzero/malformed/timeout completion and its local-only
checks, and distinguishes that from a known terminal failure's required
postchecks. Session yielding cannot authorize a second process. Source hash
checks expressly detect ordinary drift without claiming adversarial race proof.

Close the minor receipt finding and update the stale host-status prose before
binding a later coordinator GO to the final plan bytes. This review itself is
not that GO. Successful collection would still require the retained result and
identities to agree, then the parent contract's separate entry/initialization,
binding and ABI audits. Static fit/runtime/release/human gates and D139's592-byte
dynamic deficit remain separate; no native evidence was produced here.

## Bounded revision closure

Re-read final plan SHA256
`e2834aa0c57525566261922e0028c3dec14b7f83bc6a920f9caaaddc6303bb68`
(9,091 bytes). Lines98-106 now catch each post-run source-hash observation
independently and preserve null plus an explicit per-source error when absent or
unreadable. Lines107-112 write the original launcher exit code/error alongside
those observations. Lines114-116 fail on launcher failure, hash-read errors or
hash drift. The minor evidence-loss finding is **closed by inspection**. The
opening host-status text is updated to80 passing methods (24runner,33helper,
23bootstrap), with no native authorization inferred.

**Disposition: no open material invocation-plan finding; suitable for a later
coordinator GO bound to these exact plan and implementation bytes.** This review
did not execute the snippet or issue that GO. Existing parent-ancestry, resource,
exclusive-run and separate native-audit prerequisites remain in force.
