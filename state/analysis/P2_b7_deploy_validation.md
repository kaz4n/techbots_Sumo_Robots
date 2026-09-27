# D245 B7 guarded deployment validation

27 September 2026. **PASS_SOURCE_AND_HOST**, accepted independent review
`state/reviews/P2_b7_deploy_review.md` (SHA256
2fd710ec4e82e0246a8bd966b13762906c272107ac1b0dc9a3760f6806cd92a7).
This is software preparation only. No real deployment scope, upload, MCU action,
hardware qualification or human gate was created or exercised.

Source and independent oracle froze in commit98b13db0 before the first execution.
The two new tools preserve the frozen D227 implementation through exact source
pins and bounded private substitutions. The adapter changes only its header and
closed B7 profile list. The caller selects the checked B7 compiler/policy, keeps
complete Git/source/artifact closure, requires P1 qualification and specifically
fresh STAND OK for M1, and rejects identified-delivery use. M0 retains absent
grants and null qualification/authorization. Existing tools remain unchanged.

- `tools/b7_app_upload.py`: 13680 bytes,
  SHA256567966d5dfcb7abe7ccddbfc8c2d2b2d7f9f84056ea031bb54b94aeca3a17f22.
- `tools/deploy_b7_app.py`: 6367 bytes,
  SHA25681b5585535dc074a2bf0150e7971fee1e3eae3184c2f6ee8771205edd252f95c.
- Independent oracle `tests/tooling/test_b7_deploy.py`:
  SHA2560f9edc64b798d105dc23d4c4f384971e07fdb7adc22b5c46e36816304a392b68.

Both first runs passed all12 methods, with exit0 and unchanged before/after/live
source, contract and oracle hashes. Linux elapsed27.114s; Windows101.156s. Raw
commands, original stdout/stderr and pin receipts are retained under
`P2_b7_deploy_raw/host01` and `host02`. Tests use temporary Git repositories and
explicitly synthetic qualification records. Board calls are refused or replaced
by controlled callbacks; their successful fake upload is not an actual upload.

Coverage includes both motor modes, exact B7-only identity, private module
isolation, source-commit blob mismatch, complete compiler receipt/metadata checks,
all eight physical checks and required source grants, nonoverlapping button
windows, P1/stand/STAND-only selection, RING rejection, expired/future/mismatched
authorization, unavailable identified delivery, one controlled upload, consumed
owner refusal, timeout, independent closing failure and evidence-write failure.
The original failure takes precedence, UNKNOWN cannot become success, and no
retry, cleanup or rollback was added. All inherited descriptor/process/child
guards remain unchanged and were inspected by the independent reviewer.

The current board is UNO Q only; its compiled M1 source has absent setup grants.
It is not an operationally qualified B7 image. A later physical test needs a
new qualified source/build scope, verified half-charge and wiring, fresh specific
STAND OK and continuous independent uptime evidence. Upload success alone cannot
establish any of those facts or a completed twenty-cycle test.
