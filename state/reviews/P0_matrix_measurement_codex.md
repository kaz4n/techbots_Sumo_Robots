# P0 matrix run1: scoped measurement review

Date: 2026-09-22, Asia/Dubai. Reused separate reviewer context; no hardware operation, source edit or new test.
Disposition: PASS for independent reproduction of this default-startup bare-board counter observation. No open BLOCKER, MAJOR or MINOR in this evidence scope; not a full REVIEW_GATE or phase pass.

Inspected the saved capture JSON, invocation receipt and every file in `state/analysis/P0_matrix_run1_raw`. Independent Python byte decoding and ELF parsing did not import the production capture/analyzer functions.
Saved record SHA-256: `8cecd18ab51b27d120449cc60227b0619e33f5b63d6b53826f6c21bc3e90c6ef`.
Raw capture.json SHA-256: `c9740a06efae24c2fffb080d6cec529b33e925bc8d81b93b3d27dc3ea4594f1c`; parsed records are exactly equal despite different formatting.
All 36 raw files, totaling 526300 bytes, are accounted for. All nine memory reads match their recorded byte lengths and SHA-256s; all 13 commands exited 0 with no timeout. The invocation receipt also records exit_status=0.
Saved command output matches each raw stdout/stderr file and its truncation flag. Only the long symbol-table stdout is truncated in JSON; the complete 87971-byte output is preserved as cmd-03.out. Recorded OpenOCD deprecation/speed-support messages are not capture failures.

The complete 263680-byte loader read hashes to `e9322826c422fb234ac8c2e79ea38a050d0dd8dc32b2a89f6930e0a0ff7ebab2`, matching the reviewed ELF-derived reference. The original packaged-BIN one-byte padding difference remains explicit in the record.
The complete 74444-byte sketch read hashes to `74dcf3e03f0122c6d0df7158c48d09aabf3a9b1ca6f9d7eebbc063f570d7fe48`, the pinned matrix/default binary. Recorded executable/helper/configuration and ELF/binary identities agree with the prior scoped review.
Both flash reads completed before the first RAM read. Every recorded memory command matches its fixed configuration, address, size and raw output filename; no reset, halt or target-memory-write command appears.

Raw LLEXT head=tail=0x200138e4; next=0; the complete fixed name is sketch plus zero padding. All three eight-byte list dumps are byte-identical, and both complete 196-byte node dumps are byte-identical before and after counter observation.
Decoded BSS base=0x20019228 and size=7716 (0x1e24). Independent section/symbol parsing of the deployed normalized ELF confirms one p0Seconds GLOBAL OBJECT, section 9, offset 0x78 and size 4. Its aligned runtime address is therefore 0x200192a0, fully within that BSS.
Raw first counter bytes b9010000 decode to 441; raw second bytes bc010000 decode to 444. The ordinary and modulo-2^32 differences both equal 3, exactly matching the saved result.
Counter-file hashes are `0f4bcf022ff8f6cefd9fc6afebc05e08229dd2e94606e624eb43b0474c04ff99` and `9a23b74af8162eda5c1fb95f514b30564e4dead6dd9f55556f4794a378d4f269` respectively.

Recomputed monotonic read-separation bounds are 3.000219096 to 3.078028672 seconds, consistent with waiting at least the requested three seconds. Counter read windows on the board host were 23:41:55.028004-23:41:55.067516 and 23:41:58.067801-23:41:58.105839 +04.
Total capture duration was 104.838049471 seconds; first attachment command to final command completion was 104.562342 seconds, below 120. Per-read remaining time decreased throughout; the final read started with 15.555243725 seconds remaining.
The post-counter mapping checks completed before COUNTER-ADVANCED was reported. Host and board wall clocks are not assumed synchronized; the observation bounds and deadline conclusion use the board-host record and monotonic values.

Limits: this establishes counter advancement through the reviewed running matrix workload. It does not establish optical correctness, exact 1 Hz accuracy, uninterrupted operation outside these observations, unobserved boot timing, loaded Robot WCET or any hardware/phase gate. MEM-AP activity may perturb the workload; prior source-versus-binary and cache-coherency limits remain.
Next action: preserve this evidence and record bounded matrix software progress; keep visual qualification and remaining P0 acceptance separate.
