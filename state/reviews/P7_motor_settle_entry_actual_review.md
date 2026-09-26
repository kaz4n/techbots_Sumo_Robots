# D199 SETTLE actual entry and publication review

26 September 2026, Asia/Dubai. Separate same-model reviewer, reusing its review
context. Review consisted of saved receipt/source reads, hashes and independent
static/data checks. No subject import, test, native tool, transport or board
operation was invoked. Only this report was written.

## Findings

No open BLOCKER, MAJOR or MINOR finding in the exact file collection and selected
instruction review below. The original machine summary remains unchanged,
including its conservative semantic-review-pending limitation.

## Actual identity and evidence closure

The recorded invocation uses reviewed HEAD
`5adbd784f80ba7347b9437811266bd2b6cefd175`. Check-only and execution returned zero.
Parsed check stdout agrees with the saved inputs on source, boot, four file
commands, owner and 4969 UTF16 command units. Parsed execution stdout equals the
saved local closure. Its one transport ran from 07:00:45.131832 to
07:00:46.704941 UTC. Child timestamps come from the remote clock and are not
used to infer cross-machine timing.

| File under state/analysis/P7_motor_settle_compile_raw | Bytes | SHA256 |
|---|---:|---|
| native_entry_static01/inputs.json | 22998 | fcb79bd4cfc3d8a1067a149b382c7bb001b7291ee9e171cda64c7e9be5ee0f84 |
| native_entry_static01/result.json | 378557 | 10d8a184598b587ff820cb3342586a61a22106a087788a7be756486e22a824ad |
| native_entry_static01/entry.json | 9919 | 8332f7974cdcb39ec5e65cd262b2c22623bb51412f07fc04ec329d5b0d685485 |
| native_entry_static01/local_result.json | 277 | ec4c45e92b7cdb4e6191293c77777182d7a90f49e1594d3421c61f24bf171fe7 |
| native_entry_static01_invocation.json | 1267 | b66f3a5a3318704f431014abe042fed676c25d2fe2f52abb11142f3e08857c87 |

All 151 admitted local pin hashes and all 204 coordinator-frozen input hashes
and lengths were independently checked against current files. The exact
wrapper c9e8f023, contract af8ce726, binding 62346762, accepted ABI evidence and
reviews remain unchanged. D198 source is
`117cc0e777341c893f4e618a97e3f196fd0bbf2427cb2a4b02543eb37d6522da`.

The 12 remote pins equal the accepted ABI attempt's pins and the eight D198
artifact identities plus installed GDB/readelf, loader and TLS source. The
observed ELF is 6091f27d, debug ELF dc610650 and package e4000781, all from the
fixed app-motor-settle-static01 owner. Raw status is OBSERVED under
D199_STATIC_FILE_ONLY_ENTRY with no first error. All four file children exited
zero, were reaped, did not time out and produced empty stderr. All eight stream
encodings/counts fit their bounds. Stdout lengths are 283, 281, 159047 and
118292 bytes; readelf stdout SHA256 is
`0f489796fce4408065fb65b5815558613ea20770a9fc5fa293fd8b4b5c2b6d89`, and GDB stdout
SHA256 is `c43df2bcacfcf84cd65e9c803b13cd53fa0484e7211651d2a08e99df529d6c9b`.

All 13 remote closing checks pass in the producer's exact order: eight artifact
files, GDB, readelf, loader, TLS source, then board identity. The local final
check also passes. Identity is arduino/UID1000, boot
`55c386b9-fe6d-4388-a7f4-1d91e0bb49d8`, with no conflicts reported. A first
reviewer-only data check incorrectly used sorted serialized pin-key order for
the closing list and stopped; the corrected read-only audit reconstructs the
unchanged producer order. No receipt, implementation, assertion or native
operation was changed or repeated.

All four exact argv were independently checked, including -nx/-nh/-batch,
disabled autoload, C++ language and may-call-functions off. The fixed ELF/debug
paths, 59 expressions, literal backslash-n markers and 29 ranges match the
binding. There is no target connection/run/call in these commands. The native
entry owner is now consumed; do not retry it.

## Actual structure and initializer

Independent parsing verifies all 31 unique function alias tuples, both
constructor aliases, Thumb bits, sizes, bindings, section numbers and six
initialization-bound tuples. The .text section is address 0x08100010, size
0x162c8, AX/alignment8. .init_array is section2 at 0x081162d8, four bytes,
WA/alignment4. Its actual dump is `05011008`, little-endian Thumb pointer
0x08100105, the observed global initializer. Preinit and static-thread bounds
are equal; the init-array end is 0x081162dc.

All marker sequences, range headers/end markers, opcode widths, contiguous
coverage and raw block hashes agree with entry.json: 29 groups, 1099 displayed
rows, 3038 bytes. Literal-pool words appear as GDB-decoded instructions in some
rows. They were treated as data reached by literal loads, not executed opcodes;
1099 is therefore not a count of executed instructions.

## SETTLE publication instructions

The entire selected publishSettle range is [0x08110d60,0x08110d9c), with raw block
SHA256 `1cb72d84e76f723ba0c941e27c67f76515ec7f68fcdaa5e3ee6206a9fcaa9bec`.
The literal at 0x08110d98 is 0x2003d3e8, matching the separate 28-byte LOCAL
report in accepted ABI 069ed01b. It is not a second diagnostic object or a
Runner field. The fifth argument is loaded from the caller's stack after the
20-byte register push, matching the valid byte.

At 0x08110d6a through 0x08110d74, stores to report offsets 0,4,8,9,10,11 publish
elapsed_us, poll_index, reason, fresh_mask, valid and reserved zero, respectively.
The word/byte widths agree with all accepted sample field widths. The store at
0x08110d7a sets has_current at offset24 to one only after those six stores.

Reason is compared with SUCCESS=1. That path branches directly to the return,
without touching the first failure. Other reasons load has_failure at offset25
and return if it is nonzero. Only the zero-flag path stores the corresponding
six sample fields at offsets12,16,20,21,22,23, then sets has_failure=1 at
0x08110d94. For the offset23 reserved store, r12 holds the masked flag value
that was just required to be zero. Thus it stores zero, even though GDB does
not show an immediate-zero instruction at that site. There is no clearing or
replacement of an existing first failure in this routine. Report reserved
bytes26..27 are untouched and lie in the initialized zero-BSS interval.

These instructions and the bound sole-writer source support current replacement
on each completed call and retention of the first failure across subsequent
successes/failures, including later cleanup calls. They do not provide atomic
publication: individual stores and flags can be observed partway through an
update. No coherent-live-read, locking, interrupt-exclusion or memory-barrier
claim is made.

## Native SETTLE paths and ordering

The complete selected range [0x081115bc,0x081116e0) has raw block SHA256
`250a64b8ff2d95be3b2103ef0fb40797c5ed2aa12e3838c07a8ad06c639097d6`.
Literal call targets resolve through the current symbol table:

| Literal location | Thumb target | Function |
|---|---|---|
| 0x081116cc | 0x08110d61 | publishSettle |
| 0x081116d0 | 0x08111205 | UnoQPort::enableLow |
| 0x081116d4 | 0x081161a1 | micros |
| 0x081116d8 | 0x08111579 | UnoQPort::bankValid |
| 0x081116dc | 0x08110c69 | timerRegisters |

For non-null context, settled_ is cleared at object offset18. The configured
mask at offset19 is checked against15, then written_mask at20 against15, then
enableLow is called; failure short-circuits before the settle-start clock.
After that clock, bankValid is called. Only a successful initial bank check
allows timer0,1,2 update clears, in that order, by stores of 0xfffffffe to each
returned timer base+16. These are the existing update-flag clears.

The loop holds poll in r5 and accumulated fresh mask in r6, both initially zero.
Its top clock sample subtracts the saved start in 32 bits. The unsigned
comparison with149 permits only values <=149 to reach flag reads. Timer indices
0,1,2 are read at base+16; bit0 sets the corresponding accumulated mask bit.
bankValid follows all three reads. A final clock is taken only when fresh==7.
There is no extra diagnostic clock, GPIO/PWM call or timer observation in the
publication routine.

| Completed reason | Observed branch and payload |
|---|---|
| NULL_CONTEXT=2 | Null branch sets elapsed/poll/fresh/valid to zero, publishes and returns false; no clock or hardware callback. |
| PRECONDITION=3 | Either mask check or enableLow rejection publishes the same invalid-zero numeric payload; no settle-start clock. |
| INITIAL_BANK=4 | The start clock is read once, bankValid fails, and invalid-zero numeric payload is published without another clock. |
| POLL_DEADLINE=5 | Unsigned loop-top elapsed >=150 publishes that elapsed, current zero-based poll and previously accumulated fresh mask with valid=7, before this poll's flag reads. |
| POLL_BANK=6 | Failure after three flag reads publishes the retained loop-top elapsed, same poll and updated accumulated fresh mask with valid=7; no new clock. |
| SUCCESS=1 | fresh==7 and final unsigned elapsed <=149 set settled_=true; publish final elapsed/poll/fresh7/valid7 and return the stored true value. |
| FINAL_DEADLINE=7 | The same final sample >=150 sets settled_=false; reason7 comes from r6, already constrained to7. It publishes the final sample and returns false. |
| POLL_LIMIT=8 | After unsuccessful freshness, poll increments and compares with4096. Exhaustion publishes explicit poll4095, retained last loop-top elapsed and final accumulated mask, valid7, then returns false. |

All seven false outcomes and success reach publication only after their decision.
NONE=0 is not emitted by a completed path. Early/loop failures share the
publisher call at 0x081115d2 and false-return epilogue; the final-clock paths call
at 0x081116ae and return settled_. Both 150-us boundaries and the 4096-poll bound
are retained. Clock subtraction remains unsigned wrap arithmetic. A bounded
number of returning poll iterations is not a WCET guarantee or preemption of a
blocking callee. The bodies of enableLow, bankValid, timerRegisters and micros
were not selected; their identities and call ordering are observed here, while
their internals rely on bound source and prior validation.

## Existing entry, wiring and terminal behavior

All other 27 selected ranges were inspected against the current bound source
and ABI, not treated as valid merely because an earlier image was reviewed.

Entry copies 208 bytes from 0x08117450 into [0x20013890,0x20013960) and zeroes
170664 bytes at [0x20013960,0x2003d408). This zero interval contains the report
through 0x2003d404 and establishes its intended zero/NONE initialization when
entry executes. It does not establish that entry has executed on the MCU.
The memcpy/memset stubs target the pinned loader symbols; their loader bodies
are not included. Three inherited printk calls precede copying/zeroing, so no
absence-of-startup-logging claim is made. The empty preinit interval is skipped,
the one initializer pointer is called, and entry hands off to main.

The global initializer uses source context 0x2003d090, native motor context
0x2003d068, dump storage 0x20013890 and Runner 0x20013960. It builds the motor, ADC,
source and dump ports and passes them to Runner's constructor at 0x08103985.
The port factories store current callback/context pointers without invoking
their hardware callbacks. The motor factory binds settle to 0x081115bd and
computes all four candidate periods, zeroing all if any is invalid. Selected
candidateRate/candidatePeriod instructions preserve their constant-table,
divisibility and 1..65536 period checks at 10000 Hz. The arithmetic stub targets
the pinned loader. Referenced table contents were not newly dumped here; these
instructions do not verify physical PWM mapping or rate.

Trace construction copies the 44-byte motor port, clears its call storage and
initializes report/context fields. Trace.port preserves period data and replaces
each non-null callback with its trace thunk. Runner constructs Trace and obtains
that wrapped port, then calls Runtime's constructor on Runner+2184 with the same
ADC/source/dump ports. The selected constructor initializes report fields,
polls at 168572 and attempted_ at 169728. Runtime/RuntimeReport constructor bodies
are outside the selected ranges; their call targets are observed, not their
entire implementation.

main calls the immediate-return initVariant, start_static_threads and setup,
then repeats loop/loopHook. The inspected static-thread bounds are equal, so
this helper adds no sketch static threads; existing RTOS activity is outside
that conclusion. loopHook immediately returns. setup passes the single true
exclusive diagnostic grant to Runner.begin. This is separate from application
peripheral grants and motor-run permission. begin checks and sets attempted_,
selects DISABLED without exclusive grant, and otherwise records SETUP context,
zeroes all 21 bytes of the application SetupGrants, and calls Runtime.begin.
Setup failure freezes with SETUP_FAILED; successful setup checks stopReason
before returning whether still RUNNING.

loop and Runner.poll both guard RUNNING. poll increments its counter, records
APPLY context at runtime epoch+1, calls Runtime.step exactly once, records its
boolean return and evaluates stopReason. applicationValid accepts no-decision;
otherwise it checks consumed and applied_valid, an equal 64-bit token, motors
disabled and both applied duties zero. Current field offsets match accepted
ABI. stopReason preserves priority: callback failure, trace timing fault,
application feedback invalid, Runtime STOPPED/FAULT, epochs>=10000, then
polls>=10000000. The epoch instruction compares unsigned greater-than9999;
the poll literal 0x00989680 is compared unsigned greater-or-equal. There is no
earlier trace-full stop.

freeze rejects non-RUNNING, stores FINALIZING/reason and snapshots before abort:
600 RuntimeReport bytes, 497 TransactionReport bytes and 44 PreviousTick bytes.
The current ABI ptype ends TransactionReport's last field at 497 with 7 trailing
padding bytes, and PreviousTick's last field at 44 with 4 trailing padding bytes.
Thus the copies cover all declared fields, not all object padding. freeze then
sets before_abort_valid, establishes HALT context, sets abort_called and calls
Runtime.abort at 0x08101331. After return it sets abort_returned and FROZEN.
The phase guards and one-attempt flag support terminal passivity: later loop/
poll/begin calls do not restart the application. Runtime.step/begin/abort,
Trace callback bodies and MotorGate internals were not newly disassembled here;
their call sites do not establish electrical pin transitions or successful halt.

## Verdict and remaining boundaries

PASS for this exact file-only attempt and the bounded actual instruction review.
It establishes the observed initializer, fixed report address and emitted
publication/SETTLE control flow, together with the selected inhibited entry and
Runner behavior. It does not establish current report bytes, which reason will
occur, root cause of D195's earlier failure, atomic capture, loaded execution,
electrical inhibition, live RAM/stack/WCET, physical acceptance or a human gate.

D195 remains flashed. No guard, 150-us limit, 4096-poll bound, configuration, pin,
locked test or production behavior was changed by this collection/review. A
later inhibited upload/capture needs its separate source/artifact/ABI binding,
review and fresh scope; this consumed owner supplies no retry or broader grant.
