# D-073 offline recorder CSV validation - 2026-09-23

IMPLEMENTED / HOST-TESTED / SCRIPT-TESTED / REVIEWED; hardware and phase acceptance
remain pending. Contract c32b47c preceded separate implementation and test work.
The formatter adds no live dump command, application integration or transport.

## Result

src/hal/recorder_csv.h/.cpp formats one complete header or row into caller storage.
Frames retain exact scaled integers, supplied PackStatus and all25 raw bytes as
hex; events retain all8 raw bytes. The36-column summary exports every owner field
and loss counter. captureSummary copies bounded metadata without payload arrays
or owner mutation. Neither phase nor absence of known loss authorizes a dump.

Functions have bounded work: at most20 decimal digits,25 raw bytes and1023 copied
characters. Row scratch storage is1024 bytes plus a20-byte decimal temporary and
small scalar state. This is source-level accounting, not target stack or WCET.
No heap, clock, I/O, floating-point/locale formatting or global constructor added.
Known invalid records remain evidence; no byte repair, timestamp sorting or
completeness inference. Failure changes only writable destination[0] to NUL,
reports size0 and never publishes a partial line. All functions are under60 lines.

## Independent checks

The test author read only the frozen contract/public headers/prior tests, never
implementation .cpp files.18 new cases cover literal18/7/36-column schemas,
signed extrema including raw duty-128, uint64 maxima, all253 unknown status codes,
all short capacities/exact fit/null/zero guards, every summary field,10 one-hot
booleans, five actual owner phases and frame/event loss,1000 repeated reads and
4096 fixed-seed independent scalar/hex round trips. Existing tests are unchanged.

- Full normal build retry1 exit0;993cases/16989315assertions pass, zero fail/skip,
 5.574s wrapper elapsed. The initial doctest predicate-syntax failure is retained
 and repaired without changing assertions; see P2_csv_failure_analysis.md.
- Full ASan/UBSan build exit0; same993/16989315 pass with zero fail/skip,21.952s.
 Build23.088s; normal retry build12.960s. Exact argv/status/output are retained.
- Controlled tooling340 pass183.058s (wrapper199.727s), exit0. These are script
 tests, not board builds or uploads.
- Separate fresh same-model reviewer reproduced18CSVcases/1321502assertions,
 exit0. The975 unrelated cases are intentionally filtered only in that focused
 review run; both full root runs execute all993 with zero skips.

All43 previous source/config/locked files remain byte-identical. New header SHA
0be2bebf0d8cc80376fcd4ca259a258e028647f4103dab5934bc7b972f12d8e2;
new implementation SHA779b1e2609ddb4aadfd1624dabf7c0607039e99a395a3b2abc2c1aa4558318c2.
Independent test SHA5e89f574c06a1afc0ac13c001152efc814227020abc494f53c43559c31282d8c.

Reviewer recomputed the five inert source maps/hashes independently without
staging/tool imports or board calls. Removing just the two new source files
reproduces all old hashes. Approved replacements: matrixd8ac13fc, timing9b2096c5,
ADC652f235d, GPIO0ce623cf, QTRa29cff03. Full hashes/maps are in
P2_csv_inert_manifest_proposal.json. Key set and upload authority are unchanged.

## Limits and next work

No target build, upload/reset, MCU execution, peripheral operation or motor run
occurred for D-073. Earlier D-072226584B target result is tied to revision9acc0cc
and its memory probe; it is not a target-size result for this changed source tree.
Last known uploaded image remains inertQTR61d7a2d0/default from03:00:13.327+04.
FullHAL/app/loader/freeRAM/200s/no-gap/WCET and original human gates remain open.
F-091 inherited Bridge mutex/initializers and reset-stack limits are unchanged.

The row schema is not a complete transported evidence envelope. Firmware/rate/
target provenance, dump-session completeness, live IDLE enforcement and a bounded
transport still require their own contracts. tools/dump_match.sh remains absent,
not a successful stub. Subsequent offline work must not imply live integration.
Raw receipts, including first failure and generated-executable disk cleanup,
are byte-preserved in P2_csv_validation_raw/ with SHA256.json.
