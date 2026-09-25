# D189 inhibited diagnostic caller source review

Reviewer: /root/app_trace_abi_scope, separate reused read-only same-model context.
This is a scoped source review, not a fresh phase-gate review.

Initial MAJOR: actions.py draft62f07d50 inherited self-consistent inline hashes,
but executed the helper before the staged adapter checked the three fixed hashes.
A recomputed substituted helper/payload could therefore cross the bootstrap's
required validation boundary. Normal immutable caller argv reduced exposure but
did not satisfy the explicit contract. Fix required before execution.

Final source PASS: actions509b15a3e65fa0fee8b215dc55dbad14bf9770f7af30c314d7b2bfc25b83db62
and run332a30e917178dc41a42164912c50c7bf39277763e062fbb9ff35fd84a78dac2.
At actions.py:131 the count-checked insertion verifies all three expected hashes
inside request before any dependency execution or filesystem root open.
The original finding is resolved; no open BLOCKER or MAJOR.

Verified exact 12 provenance records, 127 D188 input pins/source projection,
11 scope files, committed clean HEAD/scope, seven immutable commands and at most
13 transports. Durable staging intent precedes dispatch; push requires the
verified exclusive claim; each staging label is consumed before transport.
Capture requires the strictly successful actual uploaded predecessor hash.
Outward errors and durable_unattributed results cannot become success. Independent
closing checks and original error evidence remain preserved.

The inherited descriptor-close MINOR keeps its prior disposition: frozen remote
lifecycle; process exit releases remaining descriptors; new envelope preserves
outward failure plus explicitly unattributed durable report, and refuses capture.
No tests, module imports, edits or native execution performed by the reviewer.
Host result review and actual fresh scope/admission remain separate.

## First host-run finding and bounded repair

Independent caller oracle83c5fea6 exposed a real local-admission defect:
run_test01.json preserves 19/20 PASS and the changed-package-hash subcase failure.
The test author and reviewer separately agree the test should remain unchanged.
Local admission must reject it before claim/staging; later remote rejection is
insufficient. Original source/failure is retained at ef7f91d7.

Repair source PASS: run.py
d0f0e0d0d1cd1de38932eb84d75330cdeafe4986fd38bf28e42edc3b7f82b0f8, 24802 bytes.
Lines 53-54 pin both unchanged historical binding files; lines178-197 privately
project the exact new schema/run/source/boot/owners/raw/flat and three sketch
absence paths. Complete canonical comparison preserves nested types/keys and
all unchanged tool/config/loader/directory pins. Line173 invokes it before
command composition, successful admission, claim or staging. Bool versus integer
fields differ under canonical JSON. No helper/test/historical source changes.
No open BLOCKER/MAJOR; unchanged independent rerun remains required.

## Final controlled host result

PASS: run_test02.json53f239ee records exit0, all20methods PASS/no skips,
177.507seconds, all141frozenpins unchanged. Original failure52bb346f and source
remain separately preserved. The original bad-package-hash method now passes
under unchanged independent oracle83c5fea6. Actions13/13 and remote26/26 remain
valid with unchanged source/oracles; no redundant rerun. Actual Windows command
construction measures29667/28705UTF16units includingNUL, no dispatch. Separate
reused-context same-model source/host review complete; no phase-gate inference.
