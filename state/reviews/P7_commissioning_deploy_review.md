# D227 independent commissioning deployment review

Final disposition (2026-09-27): PASS for source and focused host acceptance.
F1 and F2 are closed on FINAL03; no material blocker remains in this scope.
This is a source/host review only. No upload, board command, motor permission,
physical qualification or phase acceptance follows.

Reviewed frozen inputs:

- tools/deploy_commissioning_app.py FINAL03: 28479 bytes,
  SHA256 d5f6e5f9e7cae19b74294422b29cb83111de722fd4e6f8b5a828f67d21033213.
- tools/commissioning_app_upload.py: 13772 bytes,
  SHA256 6fe131d2d7dbffa1af54bebaf080a0deababee5e08a2286f1abed943ddede765.
- state/analysis/P7_commissioning_deploy_contract.md: 10696 bytes,
  SHA256 9a8c36c7d62b321230ae9f6c7a135f79e11853c054dafeecc00c331b26190220.

The original FINAL02 caller remains retained at
state/analysis/P7_commissioning_deploy_raw/source_final02_deploy_commissioning_app.py,
26059 bytes, SHA256
28f5c7444c5f9e875406a3d695797b1e70e91170dd808c0f1b50d4b64cccd75c.
The following original findings describe that version and preserve the repair trace.

## F1, closed: disabled literal can mask an enabled C++ grant

`config_literals` at deploy_commissioning_app.py:202 counts only declarations
matching its supported literal regex. It neither accounts for conditional
preprocessing nor rejects another declaration with unsupported expression syntax.
A read-only, in-memory reproduction against the FINAL02 caller replaced the
single APP_GRANT_OPPONENTS declaration with:

```cpp
#if 0
inline constexpr std::uint32_t APP_GRANT_OPPONENTS = 0U;
#endif
inline constexpr std::uint32_t APP_GRANT_OPPONENTS = (1U);
```

`config_literals` returned APP_GRANT_OPPONENTS=0 and
`checked_qualification(None, None, {'motors_allowed': 0, 'qualification': None}, config)`
returned successfully. C++ selects the live value 1. No file was changed and no
C++/board/native child was executed for this reproduction. The same mechanism
can hide an enabled optional M1 grant from its required evidence check.

Minimal repair: accept a conservative, unambiguous declaration grammar; reject
conditional protection of these declarations and any additional/unsupported
protected declaration, instead of counting only successful regex matches. Keep
the existing actual Git-blob/config hash bindings. A C++ evaluator or a new
review chain is unnecessary. Add the decoy-plus-live-expression counterexample
with a valid baseline so rejection cannot come from unrelated fixture failure.

## F2, closed: configured flag does not exclude default button windows

`checked_qualification` at deploy_commissioning_app.py:234 checks only
BUTTON_WINDOWS_CONFIGURED==1. `config_literals` never reads BUTTON_LOW_RAW or
BUTTON_HIGH_RAW. Thus otherwise qualified M1 config can flip the configured flag
while retaining both four-element all-zero arrays. This contradicts the contract
requirement that zero defaults do not qualify. The unchanged src/hal/ui.cpp
classifies every raw input as UNKNOWN or AMBIGUOUS for that configuration.

Minimal repair: parse the exact four literal low/high windows and reject default,
out-of-range, reversed or overlapping windows for operational admission. Preserve
the existing config hash and physical buttons evidence requirement. The current
positive M1 fixture already supplies distinct valid windows; add the negative
zero-default case and focused boundary cases for the implemented checks.

## Repair verification and test closure

Compared the actual retained, hash-verified FINAL02 bytes with FINAL03. The diff
is limited to config_text, config_literals, checked_button_windows and invoking
the latter for M1. Adapter, contract and the previously reviewed deployment and
native lifecycle paths are unchanged.

F1 repair masks comments and ordinary string/character literals; refuses raw
strings and line splices; rejects protected preprocessor references and protected
names inside conditionals; requires exactly one supported literal declaration;
then refuses protected references left outside those declarations and assertions.
The independent counterexample run retains the original conditional/string
decoy failures. Both now reject, while the valid all-14-profile baseline passes.
F2 repair parses both exact four-element arrays, requires at least one nonzero
window endpoint for M1, requires ordered endpoints within 0..16383, and rejects
pairwise overlap including shared inclusive endpoints. The five independently
defined invalid-window cases now reject. M0's disabled defaults remain admitted.

Independently verified all five final source/contract/test pins and all 36 raw
attempt artifact pins indexed by validation_receipt.json: 41 matches. Reconciled
raw stderr method identities against the 29 declared methods. Linux first_linux01
passes all 29 together on FINAL03. Windows supplies the nine original adapter
passes, all 18 corrected original deployment passes, and the two new regression
passes; FINAL03 also repeats the valid 14-tuple method. The Windows reconstruction
excludes original invalid-baseline deployment passes. All three FINAL03 attempt
input sets equal the final pins, and completed attempts report unchanged inputs.
No test was rerun by this reviewer.

Accepted closure:

- state/analysis/P7_commissioning_deploy_validation.md: 9026 bytes,
  SHA256 b4692bbceec7728b68c3b587c45cb908d51bf2a5860870aa9fd0f2c8985e2abc.
- state/analysis/P7_commissioning_deploy_raw/validation_receipt.json: 10812 bytes,
  SHA256 05f307ae36573bde7d0d5a415adfd3313320649c70fee08b6c9714ad33108214.
- tests/tooling/test_commissioning_deploy.py: 30152 bytes,
  SHA256 ceec69cac41352d2c14a5271fe2a5ec5f0f1d0904f9adc5f49b46fe1661046d4.
- tests/tooling/test_commissioning_app_upload.py: 11197 bytes,
  SHA256 fd358fb3300f07eef2a82898e100682289289a6a2c61fe85d8de047308e1d59a.

The initial nonexistent D222 result-field requirement, invalid inherited metadata
fixture, original seven counterexample admissions and intermittent Windows
read-identity setup refusals remain retained and adjudicated. The latter occurred
before D227 admission; unchanged focused reruns passed. Their exact cause remains
unproven, and this acceptance does not claim they cannot recur. They fail closed.

## Review coverage and limits

Inspected both new tools, both test files, and the reused compiler/MATCH binding,
native initializer, uploader admission/finalization and byte serialization paths.
The caller binds current compiled inputs to actual source_commit Git blobs and
the complete D222 input manifest, and deployment code to reviewed HEAD. Artifact
and metadata validators are reused. The projected adapter retains exact frozen
legacy helper bytes, bounded canonical compressed payloads, the Windows command
bound, controlled isolated Python, and the original descriptor-bound uploader.
The original scratch-absence/process checks, consumed owner, bounded one-upload
lifecycle and independent host closing checks remain intact by source inspection.
No additional material finding was identified in that scope.

Only this review file was written. Main checkout, source, tests and native state
were untouched. Source/host acceptance does not admit an actual upload. A real
execution must use the exact committed reviewed HEAD, complete current scope and
receipts, a fresh run owner, and all unchanged local/native admission checks.
M0 remains an inhibited diagnostic with every setup grant disabled. No additional
recursive review chain is introduced by this report. M1 requires real physical source
facts, the applicable human phase gate and specific STAND OK/RING OK permission,
none of which this review or synthetic fixtures provide.
