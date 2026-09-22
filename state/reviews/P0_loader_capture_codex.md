# P0 loader capture retry: scoped Codex review

Date: 2026-09-22, Asia/Dubai. Reviewer: reused separate read-only implementation-review context.
Scope: frozen `tools/p0_capture.py`, unchanged `tools/p0_mem_read.cfg`, loader mismatch evidence and independent pure tests.
This is not a fresh-context/cross-model review, a full REVIEW_GATE, or a P0 phase pass.

Disposition: PASS for the bounded read-only retry. No open BLOCKER, MAJOR or MINOR finding in this scope.

Reviewed capture SHA-256: `885c4e4206aea4ac9e03c4e92e48258db2a0ae302ff83a86430e6913afeeb57c`.
Unchanged MEM-AP config SHA-256: `89d16a28a1489c23ec743be55ade39824f9ca5213b02b20ef4785079122e4339`.
Pinned loader ELF SHA-256: `39d4a4fd47241663323f6e04f94dd8f5a9f9ad6582cf1df37f9709b74026adcd`.

Run1 correctly failed after one complete loader read, before sketch/RAM decoding. Its single difference was flash `0x0803f8bf`: captured/ELF `00`, packaged BIN `FF`.
Installed upload recipes select the ELF. The correction derives all nonempty PT_LOAD file bytes in physical-address order, validating ELF32LE ARM ET_EXEC, header/table/file bounds and exact contiguous nonoverlapping coverage of `[0x08000000,0x08040600)`.
It neither ignores the differing byte nor fills gaps. Full loader and sketch comparisons still precede RAM interpretation; original BIN identity and differences remain recorded.
Read commands, pinned helper/config, address bounds, traversal limits, command/read limits and shared 120-second deadline are unchanged. No reset, halt, flash-write or MCU-memory-write command was added.

Independently reproduced under WSL Ubuntu:

- `python3 -m unittest discover -s tests/tooling -p test_p0_loader_image.py -v`: 16 tests, 0.037 s, OK, exit 0.
- `python3 -m unittest discover -s tests/tooling -p test_p0_capture.py -v`: 17 tests, 0.015 s, OK, exit 0.

Evidence inspected: `state/analysis/P0_timing_capture_20260922.json`, `P0_loader_difference_20260922.json`, `P0_loader_elf_byte_20260922.json`, `P0_loader_identity_analysis.md`, actual source diff and both independent test suites.
Format corroboration: [OpenOCD ELF image reader](https://openocd.org/doc-release/doxygen/image_8c.html). Installed artifact selection and captured bytes remain the direct evidence.

Limitations: reviewer performed no hardware operation and changed only this review file. Pure tests do not prove target identity or timing. Preserve run1 failure and upload-to-first-SWD timestamps; the later samples-first check alone cannot prove completion before first SWD traffic. A retry timeout or mismatch must remain a failed capture. Next action: coordinator executes the unchanged bounded readout and records its actual result.
