# Current timing firmware: UNO Q compile-only result

The updated p4_timing application compiled and passed its static package/layout
checks on the connected UNO Q. Independent review
[P7_epoch_timing_compile_review.md](../reviews/P7_epoch_timing_compile_review.md)
is FINAL PASS. No firmware upload or reset occurred.

One query and one compiler process (`--jobs 1`) ran at source commit
`ac8be0c7c72141c9507fb74e93beb5f734778d7a`, with MATCH=0 and MOTORS_ALLOWED=0.
The entire staged source digest is
`13e34a041cbc57db64bec6a51bf3ace2e7527799d3a4d72c1df6c39ce35c8fe1`.
All 135 input pins and 105 staged files reconcile; 235 transports returned 0,
nine checked children were reaped, and all nine closing checks passed. The
complete operation took 462.907 seconds, including source staging.

The checked package is 91,128 bytes, SHA-256
`557bc714513df7a4dc181fff50fa8cd76744cd0519b135d4d7988cc52a6b74ae`.
The ELF is 164,832 bytes with SHA-256
`e5a998d8bb65eb10316b2eac937930ca363c5274d6a68c0c44bbec472dd251b4`.
The static layout reports 91,280 remaining RAM bytes. This is structural
space beyond the linked image, not a live free-RAM, stack-margin, timing or
five-minute all-sensor measurement. No p99 value was measured on the MCU.

Evidence and root closure are under
[P7_commissioning_build_raw/commission-p4_timing-m0-6337767d5597](P7_commissioning_build_raw/commission-p4_timing-m0-6337767d5597).
The original local precheck refusal is retained: sparse checkout converted
app_build_commands.json to CRLF. Exact committed LF bytes and the unchanged
index entry were restored; the final clean check passed. No source, test or
guard was weakened, and no native call preceded successful admission.

This validates the current common timing code in one selected profile. The
earlier fourteen-profile matrix remains evidence for its own earlier source.
The loaded MCU still contains D228's inhibited recorder, pending its separate
passive failure diagnosis. Source integration follows that capture.
