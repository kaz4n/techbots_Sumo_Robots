# P0 capture tooling validation, 2026-09-22

Coordinator evidence; Asia/Dubai. Hardware target is the human-reported bare
UNO Q USB2629958581 under D-052. No motor-capable build or extra hardware.

The first readout correctly stopped with exit1 before sketch/RAM interpretation:
`P0_timing_capture_20260922.json`, invocation timestamps in
`P0_capture_invocation_20260922.txt`. Exactly one byte differed from the packaged
BIN. Installed upload uses the ELF; its file-backed alignment byte matches the
captured board. See `P0_loader_identity_analysis.md`, `P0_loader_difference_20260922.json`
and `P0_loader_elf_byte_20260922.json`. This was a reference-format bug, not evidence
of corrupted firmware. No byte is now ignored or replaced.

Frozen correction SHA256885c4e4206aea4ac9e03c4e92e48258db2a0ae302ff83a86430e6913afeeb57c
derives the entire loader image from checked ELF physical PT_LOAD ranges. The
offline board-file comparison (no MCU operation) matched all263680 bytes,
SHA256e9322826c422fb234ac8c2e79ea38a050d0dd8dc32b2a89f6930e0a0ff7ebab2,
exit0: `P0_loader_offline_verification_20260922.json`.

Validation commands actually executed:
- Native `python -m unittest discover -s tests/tooling -p test_p0_*.py -v`:
  41 executed cases passed, but overall exit1 because diagnostic setUpClass
  requires g++ and explicitly directs this suite to WSL. No test was skipped or
  changed to accommodate the missing native compiler.
- `wsl -e bash -lc 'python3 -m unittest discover -s tests/tooling -p "test_*.py"'`:
  all107 tests passed in38.655s, exit0. Includes74 prior script/config/diagnostic
  cases,17 histogram cases and16 new independent ELF parser cases.
- Separate reused read-only reviewer independently reproduced16+17 passes;
  `../reviews/P0_loader_capture_codex.md` has exact scope/limitations. This is
  not a fresh whole-phase review.
- `git diff --check`: exit0.

New helper/config copied to `/home/arduino/sumox26-tools/885c4e42/`; board sha256sum
confirmed the frozen helper and unchanged config89d16a28... before retry. Run1
and its older helper directory are retained. Retry is a fresh run2 directory;
its actual outcome and measurements must be recorded separately.

Immediate timing compile-only also succeeded with MOTORS_ALLOWED0, exit0:
`P0_timing_immediate_compile_20260922.txt`. It did not upload/reset/start the MCU.
The default-startup timing image remains running until explicitly replaced by
another reviewed inert upload. Compilation does not measure cold-boot time.
