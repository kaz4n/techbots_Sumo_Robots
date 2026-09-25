# D178 first repair findings

The frozen original oracle 90471804 runs 13 methods against source cb4c0d73:
11 pass, two fail, no errors/skips. Full original output is retained in
P7_dump_error_retention_repair1.json. Reviewer and independent test author
adjudicated the two distinct findings before corrective edits.

1. Source formatting: the journal-failure message prepends its error code,
   violating the intended preserved primary-message prefix. Move the code after
   the original message and before the partial path. Keep the error code visible
   in CLI diagnostics, secondary details, cause and all existing precedence.
2. New oracle fixture: its serialization test patches json.dumps, while the
   unchanged writer uses streaming json.dump. The injected TypeError is never
   reached; requiring no open attempt/no journal additionally assumes an
   unspecified serialization order. The spec-only author independently confirms
   the fixture defect without reading the subject implementation.

Approve only this new test's injection change: intercept json.dump for error.json,
write/flush a fixed prefix, then raise the existing TypeError. Preserve original
primary/code/message/cause/path/raw bytes/secondary/no-publication assertions and
single serialization count; replace no-open/no-file expectations with exactly one
open of the intended journal and exact retained partial-prefix bytes. This tests
D178's required preservation instead of changing production serialization to fit
an unsupported fixture. No established or locked test is changed. Original draft
90471804 and original failures b11f8d6e remain; all other new assertions stay.

This is the first source repair outcome; next source change is its bounded
formatting correction. No device, firmware, motor permission or gate is involved.
