# D-071 recorder memory experiment — 2026-09-23

IMPLEMENTED / HOST-TESTED / SCRIPT-TESTED / TARGET-COMPILED(candidate25) /
REVIEWED. P0/P1 human gates and physical P2 B8 remain pending.

Contract390b7cc preceded implementation and separate spec/header-only test author.
The experiment keeps production50Hz, all43 protected source/locked files and the
five existing upload guards byte-identical. No upload/reset/MCU execution or
motor action occurred. Linux on the connected UNO Q performed builds via the
verified ADB fallback; no password or secret was needed or recorded.

## Actual target outcomes

| Snapshot | Exit/result | Compiler RAM | Pool difference | ELF bytes |
|---|---|---:|---:|---:|
| Initial50,990b5b80 | 1, preprocessing failure | unavailable | unavailable | unavailable |
| Repaired50,9d82fea5 | 1, EXPECTED_OVERSIZE |356608| -94464|424956|
| Candidate25,a060474c | 0, TARGET-COMPILED |226584|35560|294932|

CLI1.5.1/core1.0.0, default FQBN arduino:zephyr:unoq, MATCH0/MOTORS_ALLOWED0.
Installed target GCC version and library inventory are retained in raw ELF
receipts. All build commands, statuses and exact sources are in
P2_memory_validation_raw/compile_*.json and candidate_provenance.json. The50Hz
failed size check did not export output-dir artifacts; its ELF was read from
the cache identified by build.options.json and exact sketchLocation. That ELF
does not turn the failed compile command into a success.

Initial failure: Arduino auto-includes a Zephyr EMPTY macro, colliding with the
pure recorder enum. A bench-only push/undef/pop include boundary repairs it;
production interface bytes remain unchanged. Independent defined/undefined
macro restoration fixtures pass. Future app integration must address this
boundary explicitly. Original failure stays in compile_50.json/console; the
first repair reaches the expected50Hz size failure. No weakened test.

## Actual validation

- Independent18 focused tooling tests pass2.547s; fresh reviewer reproduced18.
  setup plus10000 loops causes zero counted API/probe/heap work. ABI/address,
  literal/provenance, invalid arguments, symlink/path, failure restoration and
  six upload-refusal combinations are checked without board action.
- Six candidate-specific cases plus unchanged locked tests:245cases and8451027
  assertions, no fail/skip; normal run0.420s, ASan/UBSan5.594s. Full command/source
  receipts in candidate_host.json; compiler exits0. Fresh reviewer separately
  rebuilt/reproduced245/8451027. Candidate .cc stays outside production CMake's
  recursive .cpp glob. Synthetic application receipts are not robot measurements.
- Full controlled tooling suite335 passes136.757s (wrapper wall140.825s), exit0.
  Existing969 production50Hz cases were not rerun: their source/config/locked
  inputs remain unchanged; their earlier verified result remains in D-070.
- Source maps, remote/local ELF hashes, ABI, section sums, single-owner census,
  retained calls and constructor paths separately reviewed. No new upload entry.

## ABI and image limits

Final ELF hashes:50Hz197ae66ad5a1852df5d28192e6476b02dc087b9d0df86b8def9b0bfe2f7d6581;
25Hzb1fd86780b5d2a3a91c7c41031a2329484226991f5a198309bc8515d60a3df76.
Both have exactly one Robot2352B and one AttemptRecorder in .data (292952B at50,
162952B at25). StoredFrame26B; EventBuffer32780B; Summary96B; Input112B;
Result352B. ABI has32-bit pointers/size_t, capacities10001/5001. The large owners
are initialized .data, not assumed BSS. elf_account.json contains full sizes,
alignments, sections and large-object census. A first offline parser mistakenly
subtracted section addresses from ET_REL values; elf_parser_failure.json retains
that analysis defect and its first correction. Reviewer independently corrected
the same ad-hoc extraction mistake before checking the final numbers.

Seven setup pointer stores and an empty loop are confirmed. Four inherited
platform initializers remain; the one named after robot_owner initializes HCI
state. ZephyrSerial initialization includes semaphore setup. The linked Arduino
loop hook has an indefinite mutex wait and conditional Bridge.update_safe.
Therefore this whole image is not certified Bridge-free or runtime-bounded.
Robot::reset uses2392B of stack including saved registers before its callees.
No complete stack/WCET/constructor allocation measurement was made.

P2_memory_loader_budget.md distinguishes the compiler35560B difference from a
conditional pristine-heap model:230072B load peak and32068B largest allocatable
payload. This is not measured free memory. Future HAL/transport growth, actual
loader state/fragmentation, other arenas and full-tick behavior remain unknown.

Verdict: candidate25 clears this image's size check. It is not production rate
adoption, complete firmware fit, loadability,200s/no-gap/dump evidence, R4/B8 or
a human gate. SC-AH remains open for deployment; SC-I inherited runtime paths
remain a separate blocker. Last known uploaded MCU image is still earlier inert
QTR61d7a2d0/default from03:00:13.327+04; no new hardware connection is requested.

Fresh-context same-model review: ../reviews/P2_memory_compile_codex.md, PASS
within this scope, no open findings. Not cross-model review or gate approval.
