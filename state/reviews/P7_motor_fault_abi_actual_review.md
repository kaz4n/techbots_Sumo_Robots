# D173 actual ABI evidence review
Reviewer: separate same-model agent, reused source-review context; 2026-09-25.
Scope: local receipt/source parsing only; no board action or implementation edit.
Execution HEAD089de986; invocation exit0/empty stderr, elapsed1.1971205s.
Raw transport stdout SHA256: 338c198c20c54583007adf73b272e571137a0e97bc08507b5f79efec15392eb0.
Saved observation SHA256: 0e540e0c50dc17af292b751c05742e86f8cb84f672a8bdf6ecbcc95a753c558a.
Compact ABI SHA256: 822c917d32d5bbbcb209ebfad88fd347b516141f85351b84058b3a5ac4ab77a4.

BLOCKER: none. MAJOR: none. MINOR: none in the bounded actual-evidence scope.
PASS - One transport/6009 command units; five children each exit0/reaped/no timeout,
empty stderr; decoded byte counts exact. Raw JSON equals the saved observation.
PASS - Decoded transmitted program c5f4793a matches reviewed composition; its pins
and commands match inputs.json and actual child argv. Reader50c07402, metadata45ec0da9,
manifestb91cf39c and all117 current local source hashes match retained bindings.
PASS - Exact25 remote file checks plus identity and exact120 local checks all PASS;
both final statuses OBSERVED, first errors null; UID1000/boot6d4aca1b recorded.
PASS - ARM32 little-endian REL final ELF symbol diagnostic is2592B at section7
.bss offset0; section2632B/alignment8. Debug Runner2592/alignment8 agrees;
trace report/calls offset44, report2312, applied2336. All10 compact type sizes,
alignments and direct member offsets independently reconcile with recorded GDB.
PASS - Loader llext_list0x200017bc/list8; llext196/alignment4, BSS index3,
base-pointer offset32 and size offset92 agree with recorded loader GDB.
PASS - Compact recipe equals D1720116 compile JSON: dynamic motor_fault.ino,
remoteocd, wait startup, exact loader/build export paths. Build and artifacts
export copies both hash b4416792; recipe inspection did not execute an upload.

PASS for file-only ABI collection. Scope is consumed; no retry is implied.
No MCU memory, relocated runtime BSS address, atomic snapshot, callback-fault cause,
startup/RAM/WCET/physical acceptance or human gate is established. Later actions
must recheck their own source/artifact/board identities and preserve run authority.
