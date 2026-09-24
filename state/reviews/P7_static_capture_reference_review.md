# Static capture loader-reference correction

25 September 2026, Asia/Dubai. Reused-context same-model follow-up review.
**MAJOR in the original caller-reference prose; proposed correction PASS.**
The original contract/review remain preserved in commit `6d45e3b5`; this finding
corrects the earlier review's incomplete reference-identity assessment.

The original [contract](../analysis/P7_static_capture_contract.md), SHA256
`ee1bb8d4acd969fa16330f2e7a55bf26daac71a6dbe4f6922c730f46bcb96fc3`,
directs the caller to loader BIN hash `6b2ffd3a`. That is the wrong full-byte
reference for this ELF-based upload route and would reject the correct image.
Retained installed [boards.txt:92](../analysis/P2_bridge_dependency_raw/installed/core/boards.txt:92)
selects the loader ELF; [platform.txt:197](../analysis/P2_bridge_dependency_raw/installed/core/platform.txt:197)
and its upload recipe at line 323 pass that ELF to remoteocd.

Independent local verification used Python `-B`, with only the exact AST-selected
pure `loader_image`, `require`, `uint32`, `in_range` definitions and their two
constants from [p0_capture.py](../../tools/p0_capture.py:75), SHA256
`885c4e4206aea4ac9e03c4e92e48258db2a0ae302ff83a86430e6913afeeb57c`.
The collector module itself was not imported or executed. All checks passed:

- Retained ELF SHA256
  `39d4a4fd47241663323f6e04f94dd8f5a9f9ad6582cf1df37f9709b74026adcd`
  derives exactly 263680 physical flash bytes with SHA256
  `e9322826c422fb234ac8c2e79ea38a050d0dd8dc32b2a89f6930e0a0ff7ebab2`.
- Packaged BIN SHA256
  `6b2ffd3a24aa77ca40bac1a8c61460c5cdd3292a2ff38cb377b938a6ac939713`
  has equal length but differs at exactly offset 260287: ELF byte 0, BIN byte 255.
- Reassembled retained D118 before/after five-block loader captures each equal
  the ELF-derived image byte for byte. This corroborates the existing
  [capture receipt](../analysis/P2_app_default_probe_raw/actual_capture/capture.json)
  SHA256 `6ab8d82f23e6ccf5fc9a737e8b04e123defb50c661719a9ecf59dc06dbd898b3`
  and [original identity analysis](../analysis/P0_loader_identity_analysis.md).

Required correction: bind the loader ELF and pinned pure helper above, derive
the complete reference and require the 263680-byte/e932 hash before passing it
to the comparator. Preserve the BIN hash as package provenance and its explicit
mismatch; never ignore the differing byte. Static sketch reference `5f08afe0`
does not change.

This alters caller-reference preparation only. The pure comparator signature,
18-read plan, lengths, strict comparison, decoding, priorities and synthetic
test oracles remain unchanged. The coordinator owns the prose correction;
the original paragraph must not govern a real capture. Existing D118 bytes are
historical evidence, not proof of the currently loaded image. No board call,
build, upload, new capture or hardware acceptance occurred. Only this small
review was written; derivation and comparisons stayed in memory, with no cache.
