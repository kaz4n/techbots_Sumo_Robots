# D148: existing static packet, read-only structural validation

Active P7; D147 host extension is complete in16d95b4e. This scope applies that
tested interface to the existing D144 packet, never recompiles or reuses an old
experiment. D144's rejection and production consumers remain unchanged.

After separate source review and coordinator selection under D051, execute the
fixed `P7_static_link_probe_raw/validate_native_actual.py` once, using captured
hash-checked bytes with Windows Python `-B`. It invokes the new fixed
`read_native_actual.py` composition through the unchanged D143 bootstrap/helper.
Record the final source hashes in the decision before execution. Neither script
is a production tool or a general-purpose retry mechanism.

Reuse17 literal local pins, the103-file source and102-file existing stage,
26 installed pins, three original D144 receipts, exact ADB executable/serial,
original boot/directory Claim and eight exact artifact FileRecords. A fresh
exclusive `native_actual/` directory retains compact command/result receipts.
Before any dispatch, verify the combined Windows command is at most30000 UTF16
units. The intended five read-only commands are installed-file hashes, current
stage observation, one pure native validation, installed-file hashes, stage
observation. Final installed/stage/local checks run independently after failure;
preserve the first failure and do not repeat the native validation.

The one native validation reads seven existing build artifacts plus the exported
flat package using the reviewed descriptor checks. Its captured validator is
exact D147cd52a29a, frozen base d30372dd and helper8ba9b190. It checks installed
TLS source68bb1476 and loader39d4a4fd, runs the pure validator in memory, then
rechecks installed-file identity, all eight artifacts, board identity and Claim.
Only a compact report is transferred; no duplicate binaries are downloaded.
Return validation/postcheck errors explicitly; preserve unsuccessful receipts.

Host response checking requires the distinct extended status and all six exact
TLS tuples. A temporary copy of the common report fields is checked with the
frozen original schema/bounds checker; that copy is never saved or sent to a
production consumer. The actual result retains its distinct new status.

No remote writes, compiler, properties query, upload/reset, MCU execution, source
change, static adoption or old-test change. A pass proves structure and packaging
of this fixed packet only. Entry/constructors/native-binding/ABI audit, live
stack/RAM/WCET, physical acceptance and human gates remain separate. Use existing
local debug ELF/map for the next audit and retain only compact new evidence.
