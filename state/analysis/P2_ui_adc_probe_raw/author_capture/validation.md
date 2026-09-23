# D114 independent readout author validation

Final PASS: 42 unittest methods (21 pure decoder, 21 collector), zero failures,
errors or skips; 4.830 seconds in an isolated Linux copy. Production remained
unchanged throughout all three executions.

- Capture source: `f4b3db265bdf2d5a5fdada19ed9f51a44304d9ba5da8be78e598365afa2c4444`.
- Final tests: `02b14721b6cf7805a3b854759bbf49c39b761031a22a20de0fbfad59e720b17d`.
- Harness: `f9f54f60f905060863cd1be490e3703d7dd604b84b135f626c349e69ab87009a`.
- Final contract: `0e8ead402ac3ddd247a986790d793d4126141d7d283e38665e6fce411c51b689`.

The 21 pure expectations froze before implementation execution; all 42 methods
then froze before the first run. `pure_frozen`, `full_frozen`, `amended_frozen`
and `final_frozen` retain the successive exact files. Two fixture corrections
were proposed as exact diffs and approved by the coordinator/reviewer before
application. The original run1 (8 failures,47 subtest errors) and run2 (1 failure,
1 error) remain intact. Their triage and later qualification identify fixture
causes; no production defect or source change followed. The COUNT correction
preserves rejection of nonzero counts in NOT_STARTED/DISABLED. The final hash
helper substitute preserves actual delegated symlink/regular-file checks.
Invalid caller requests are independently tested without assuming later recovery.
Metadata commands are ordered once; repeated version calls are not admitted.

Decoder cases cover the literal enabled 9892-byte ABI, every public field, full128
and truthful failed/nonterminal records, historical samples/decoders/flags, enum
and boolean domains, count/timing/source/decoder consistency, natural wrap,
99/100us and half-range boundaries, raw0/16383, cadence/misses, saturated counter
history, and strict full-byte identity including otherwise ignored padding,
private state and unused records. Pure decoding is checked without process,
file or clock calls. Collection integrity remains separate from terminal meaning.

Collector cases execute the actual new Capture/check_identities/read_layout/
collect methods against controlled filesystem/process/clock replies. Exact one-
and three-node plans pass18/22 reads,587232/588016 bytes,22/26 commands. Cases
cover pins, artifact sizes and symlinks, all layout identities, both flash
brackets, invalid list/node/BSS ranges, cycles/duplicate sketch/fourth node,
post-read descriptor changes, partial files and consumed failed purposes,
wrong command/range/region/label/replay refusal, admitted deadline boundaries,
and CLI result/report persistence. Import is guarded against process/network
calls. CLI reporting uses the separately approved public collect/constructor
substitutes; collector behavior is tested independently through actual collect.

Actual pinned installed loader ELF/package and enabled ELF/ZSK bytes are local
fixture inputs. The immutable p0 loader helper executes; a separate literal
ELF32 PT_LOAD reader constructs the expected flash bytes. Other installed tool
identities use approved public hash substitutions, so this is host software
validation, not installed-binary or deployed-flash verification. The fixed plan
cannot reach48 reads,2MiB or64 commands without violating admission; no private
state was seeded and those unreachable ceiling branches remain source-reviewed.
No hardware, upload, wiring, calibrated timing or phase-gate claim is made.

The author is a reused separate test-author context, not a fresh repository or
cross-model reviewer. No capture implementation body was read. No old/locked
test, production file, shared ledger or hardware setting was changed.
`validation.json`, `run3_source_copy.json`, `run3_command.json` and full receipts
bind the command, dependencies and result. Final test line endings are UTF-8 LF;
this normalizes the prior CRLF amendment, explicitly recorded in final_freeze.

Next action: independent private rerun/source review and coordinator acceptance.
Any actual capture or ADC operation remains separately authorized work.
