# D233 independent actual recorder delivery review

Reviewed 2026-09-27. Verdict: **ACCEPTED FAILED-ATTEMPT EVIDENCE; DELIVERY FAILED**.
No open evidence-reconciliation blocker. This accepts the closed compile and
failed delivery records, not successful recorder delivery, physical evidence,
motor authority or a phase gate. The reviewer inspected retained local evidence
and wrote only this report; no native command or test ran during review.

## Historical native identity

Native HEAD: `ce4e69390d21d9a91231581a186be4a63213135e`.
Attempt: `07f19e32c483cebadecaa63f4d6d720f`.
Session: `572412568535289530`.
Source: `29cb1e76193e4b7c562d1fd842039f61367a82c2651a2303c09518d35a0c7ce9`.
Owner: `state/analysis/P7_recorder_delivery_raw/recorder-07f19e32c483ceba`.
Target: ADB serial2629958581, boot55c386b9-fe6d-4388-a7f4-1d91e0bb49d8,
UID1000, static/default recorder.ino, MATCH0/MOTORS_ALLOWED0.

All145 recorded input hashes independently match their native-HEAD Git blobs.
Using those exact historical bytes, the source mapping and staged-only603-byte
positive-session header reproduce all110 staged hashes and the complete source
digest. All four saved source-set observations match that inventory. Subsequent
integration changed current configured_setup.h, runtime_dump.cpp and config.h;
this review deliberately binds the historical native inputs, not that later
application source or current HEAD. Saved local closing checks passed while
the native attempt owned the frozen source.

## Compile and upload

The compile outcome is COMPILE_CHECKED with one query and one compiler,28
transports, no first error and all nine closing checks PASS. Actual checked
query/compiler argv retain --jobs1, static FQBN and MATCH0/MOTORS_ALLOWED0.
Both child receipts are COMPLETED, reaped, returncode0, not timed out, with
empty stderr. Their decoded raw output reproduces the saved parsed CLI JSON.
The compile interval is21:12:25.166530 to21:16:51.163240 UTC on2026-09-26.

Native TLS/layout/package validation passes. The55376-byte exported package is
SHA-256 `b13a32b5e92993a49f165b907d5d6036fa933e1680bb23ff2738620b294fd584`;
the101908-byte ELF is
`d6578af6fb2994501cbf024b5488a4b641da4bb87f30403b4bdb79366cd31bca`.
The packet records the216-byte .data copy,164196-byte initialized BSS interval
and97424 bytes of structural RAM remainder. That is a link-layout fact, not
measured free RAM or timing. Loader, TLS-source and artifact postchecks pass.
The final artifact packet exactly equals the original; final artifact-source
identity/hash also matches compile closure.

Original uploader admission succeeded before receiver use in the reviewed
sequence. The fresh ticket was initially absent/pending, then its matching
loopback socket was recorded TCP_CONNECTED. Board connection time
120789.128240637 precedes upload start120792.333779087 and completion
120802.541314020. Uploader output exactly matches the run's upload object:
UPLOADED, one attempt, reaped child/returncode0/no timeout, no first error and
no postcheck errors. It establishes uploader completion, not execution of the
expected MCU path or UART/router readiness. No synchronized host/board clock
assumption is needed for this ordering.

## Terminal receive failure and closure

The receiver claim starts at120789093242013ns with deadline121689093242013ns:
exactly900 seconds. Its terminal closes at121689148803278ns,900.055561265
seconds after start, with reasonTIMEOUT and observed_byte_count0. The terminal
and connected claim retain the same ticket, boot, target, process and directory
identity. The native stderr preserves TimeoutError from socket.recv. The host
receive child reports reaped/returncode1/CalledProcessError, not a host915-second
timeout. The original failure is retained with no secondary errors.

Receive stdout and partial wire.txt are empty. Partial error.json records
TRANSPORT/partial, expected session572412568535289530, observed/rejected session
null and the exact terminal evidence. Its CONNECTION_METADATA error preserves
the absence of verified END_OBSERVED. The run records CaptureError, capture and
capture_acceptance null, statusFAILED and framing_cleanUNKNOWN. There is no
BEGIN, frame, event, END or accepted capture evidence.

All45 main transport intent/result pairs match and return0. The four separate
receiver children are reaped; only the receive child returns1, while the other
three return0. Raw stdout/stderr sizes match their outcomes. Every secondary
error list is empty; run closing_errors and receiver_cleanup_errors are empty.
The compile root closure pins and totals independently reconcile. This owner
is consumed; the evidence supplies no retry or new-upload authority.

Principal retained SHA-256 pins:

- Inputs: `79adabdcb74bea6537a759fce7d18036895ebdabf72e78885f0ab6015abbcbde`.
- Staged inventory: `f7edb520e389a3e2129a1d7a71f92f045a922a21bade78e257ec2575b44b6cfb`.
- Compile result: `aac76518e1900667cf4319e14422ace824ef58e6d719726db3e250d2f9ef387a`.
- Artifacts: `2b5725d09c53590a07d6e1325cc6a4773211bc519f2b3c43d991a51021be23f5`.
- Run result22203B: `4a58ba4e6f79d8290f299e8d98bdfb3e1577ade6068849cbb7979bed19e1f7f6`.
- Partial error41769B: `e4b0d048f001d6b1069a8d0fd112d975872d9bfa6ef6b12170e8f7578a3caa87`.
- Receive stderr584B: `0c29dd39584457b842dfc6b5a8b9633e0c43558d4a9dc305b91250acbc6388bc`.
- Receive outcome20319B: `e6e363534f27669be24305cf87ba9cbf2a94183a613828a9744ca40cb02b5387`.
- Terminal query1834B: `c05a772f124897d9c4598f86f393dd89212ddec614742a067f45ede519b19a99`.

The receiver timeout is established; the original MCU/native failure cause is
not. Empty receive data and TCP connection do not identify that cause or prove
that no UART prefix shifted. The separately accepted fresh file-only ABI and
bounded passive first-failure capture are the next diagnostic evidence. Their
actual dynamic observations remain separate from this delivery review. No
reset, new upload, grant/ready-pin change, physical qualification or gate follows.
