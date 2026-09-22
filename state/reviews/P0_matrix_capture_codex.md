# P0 matrix counter readout: scoped review

Date: 2026-09-22, Asia/Dubai. Reused separate reviewer context; no hardware operation or implementation/test edit.
Disposition: PASS for the bounded default-startup bare-board readout under D-052. No open BLOCKER, MAJOR or MINOR in this scope; not a fresh-context full REVIEW_GATE or phase pass.

Reviewed wrapper SHA-256: `ace4cda492de13610a2ca24ba4a5ccd3453a073c3e2b13b4b388bdc8726c9d31`.
Unchanged helper SHA-256: `885c4e4206aea4ac9e03c4e92e48258db2a0ae302ff83a86430e6913afeeb57c`.
Unchanged MEM-AP configuration SHA-256: `89d16a28a1489c23ec743be55ade39824f9ca5213b02b20ef4785079122e4339`.
Independent test snapshot SHA-256: `dfa372a77c52ab1bc122e0a94d17d7954acec03543986cf76dfe659f7db7714a`.

Independent `wsl -d Ubuntu -- python3 -m unittest discover -s tests/tooling -p test_p0_matrix_capture.py -v`: 9 tests PASS, exit 0. These test quiet import and exact uint32/modular arithmetic, not hardware capture mechanics.
Static review covers the final wrapper, unchanged helper/configuration and `P0_matrix_readout_plan.md`, including the exact linked startup audit and retained default/inert scope.
All pinned files, exact matrix ELF layout and complete deployed loader/sketch images are checked before RAM interpretation. The reviewed source manifest remains `72214f8aa1b6d84e21d2dc8a568ea01adb5fe0295f3f3d0f362e8696d2543e8f`.
The matrix ELF and uploaded binary are fixed at 74444 bytes, with hashes `1fbb189bba0a52f2d23040522560aee66d8c1d0629e80e6476459cf05c43ec5d` and `74dcf3e03f0122c6d0df7158c48d09aabf3a9b1ca6f9d7eebbc063f570d7fe48` respectively.
Bounded LLEXT traversal requires a unique sketch, stable head/tail and exact BSS size 0x1e24. The unique global p0Seconds symbol has aligned offset 0x78 and size 4; both reads must fit that verified runtime BSS.

Closed MINOR: initial code did not reconfirm the selected runtime mapping after counter observation. Final code validates the original raw list/node files against metadata and hashes, rereads list and selected node, and compares head/tail, next, complete name and BSS base/size before success.
Worst case is 12 memory reads, within the unchanged 16-read and 32-command caps. The three-second wait consumes the original 120-second attachment budget; every subsequent read receives only remaining time. Any identity, timeout, range or delta failure returns nonzero without extending or retrying.
The wrapper adds no reset, halt, flash or target-memory write command. It retains the fixed MEM-AP-only configuration and private bounded output paths.
Counter success requires exact uint32 observations and 1 <= (second-first) modulo 2^32 <= 0x7fffffff; raw values and host read-time bounds remain in evidence.

Transfer-width corroboration: Arduino OpenOCD commit e6a2c12f4 dispatches a four-byte aligned dump through target_read_buffer_default to one size=4/count=1 read; mem_ap forwards that size/count to mem_ap_read_buf. Sources: [target.c](https://github.com/arduino/openocd/blob/e6a2c12f4/src/target/target.c#L2256), [mem_ap.c](https://github.com/arduino/openocd/blob/e6a2c12f4/src/target/mem_ap.c#L221).
This is source-at-reported-commit corroboration, not independent installed-binary disassembly, a bus trace, or cache-coherency qualification. The installed executable remains hash-pinned by the wrapper.
Limits: counter advancement is software progress through the reviewed matrix workload. It does not establish optical correctness, precise 1 Hz timing, uninterrupted operation outside the observations, loaded control timing or a passed hardware/phase gate. Read activity may perturb the running workload.
Next action: execute only this reviewed bounded readout, preserve all raw files, and independently check the returned identities and counter evidence before recording a measurement result.
