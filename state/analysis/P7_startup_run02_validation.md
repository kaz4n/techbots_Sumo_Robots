# D158 explicit ownership validation

IMPLEMENTED / HOST-TESTED / scoped review PASS; no run02 board attempt yet.
Existing wrappers now accept explicit per-instance binding/run selection. The
closed run02 launcher uses distinct claims and upload_loader; legacy defaults,
old dependency pins and consumed run01 evidence remain unchanged.

First source bcf623dc passed 197 unchanged regression cases, while the old private
launcher suite passed8/10. Two default-call/fixture compatibility differences were
repaired without editing those tests: default binding decode and native-entry
call shapes retain old behavior; run02 still uses strict projection and explicit
expected identity. The first independent ownership suite passed19/20 methods;
four subcase errors came from a missing json_bytes API in its harmless support
sentinel. Only that pure serializer was added; every assertion remains unchanged.
Original source, oracle and all first failures are preserved in1854bb8e/bcf623dc.

Final evidence totals227 passing methods (207 existing +20 new). The three affected
suites reran after repair: ownership20/20 in0.623s, public launcher30/30 in0.046s,
private launcher10/10 in0.079s; exit0 and all18 frozen pins unchanged. Unmodified
remote sources retain their passing55/59/46/3/4-method receipts. No locked test was
edited. Sources c9588835/23661c8a/ab0bb320 and companion84503c31 are frozen in
P7_static_startup_raw/run02_repair1_freeze.json; exact commands/results are adjacent.

Local composition passed16 profile/receipt pins plus17 runner pins and the
existing working/stage verification, with six fixed command forms and zero
native dispatches. Upload28751 and capture25436 UTF16 units are below30000.
Its optional source_manifest field is null, not a full manifest/count observation.
RAM fixtures were removed; a root find observed zero sumox_* directories.

Separate same-model review reusing design context: reviews/P7_startup_run02_review.md,
SHA bda4208e5491fbf33017961b00d4a747b68a92f74bbb56f2f9bfd77fc8657cb7.
No material finding remains. This is not a human/phase gate or cross-model review.

D159 separately removed the exact known temporary fragment after fresh checks;
its failure history remains. Run02 still requires fresh temporary-path absence,
committed reviewed scope/HEAD, unchanged source/packet and installed prerequisites.
No new firmware, source/config/locked-test change, native startup evidence or
physical acceptance follows from these host tests.
