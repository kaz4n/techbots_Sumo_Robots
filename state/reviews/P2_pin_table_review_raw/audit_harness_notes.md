# D106 reviewer harness corrections

The first preliminary-target audit stopped at the new COUNT value check. The
reviewer helper subtracted section sh_addr from ET_REL st_value, which is
section-relative. COUNT lives at offset0 of .llext.rodata.noreloc, whose layout
hint sh_addr is2124; subtracting it selected unrelated bytes. All symbol-data
reads now use the actual section-relative st_value. The raw final bytes are
46000000 (70), matching the intermediate constant section. This is an auditor
addressing correction, not a production edit or a relaxed count assertion.
Prior table/function checks used sections with sh_addr0 and were unaffected.

The first MATCH audit compared actually referenced imports against the D105
motors-disabled artifact and stopped on __real___aeabi_d2uiz. This helper was
already referenced in the reviewed D103 MATCH artifact e3d539a2. D105 has no
MATCH target. The audit now pins that D103 MATCH artifact as the actual-import
baseline for MATCH only; complete declared import sets are also required equal.
The current MATCH referenced-import set matches it exactly. Table bytes still
compare against final D105 c059, and initializer instructions/references match
both prior profiles. No new import was whitelisted or source change made.
