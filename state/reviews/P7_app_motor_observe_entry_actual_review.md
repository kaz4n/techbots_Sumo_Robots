# D194 observer actual entry review

26 September 2026, Asia/Dubai. **PASS for this file-only collection and the
bounded instruction review below; no open material finding.** Reviewer
`/root/fresh_review` is a separate same-model reused context. Review comprised
local receipt/source reads, hashes and independent static/data comparisons;
no subject imports, test execution, native tools or board calls. Only this
review was written. The machine summary's conservative "semantic review
pending" text is preserved; this document records the additional human-readable
instruction audit without altering that receipt.

## Actual provenance and closure

The invocation names clean reviewed HEAD
`41bea2603bffd199c1d57180062950ef0d3013eb`. Check-only and execution both return
0. Parsed check stdout agrees on the source, boot, four file commands and 4925
command units; execution stdout equals the saved local result. The one actual
transport ran from 04:55:56.018578 to 04:55:57.473921 UTC.

| File under P7_app_motor_observe_compile_raw | Bytes | SHA-256 |
|---|---:|---|
| native_entry_static01/inputs.json | 22218 | `261b10a07a1668d26bed6a00144eccf6a028cc42aac8ab38606f57f695f4e094` |
| native_entry_static01/result.json | 357824 | `61c7b0907c70132e7b19f2b2aa1a2d6d4168322ead329337f85f0f7268f96757` |
| native_entry_static01/entry.json | 9251 | `e195fdeb0262687fc8541beb207874e393edfcdd5a3a1c36606daf67d8f32653` |
| native_entry_static01/local_result.json | 277 | `fd86da1f5fd920d9e707bbeb051e51c1c2007d13e9948b8014af51e42ef5b759` |
| native_entry_static01_invocation.json | 1351 | `0df6a650b4ec32e83d8496dd6c954640337a8a63aabbd16b57f3e831cacd0018` |

Independently hashed all 146 admitted local pins and all 150 coordinator-freeze
pins: every current file matches. Wrapper `0c3a3dd1...`, contract `437f8cb8...`,
D193 source `3a08ddeb...`, and the accepted ABI02 receipts remain exact. The
12 remote pins agree with ABI02 and all eight relevant D193 artifact files.
In particular ELF `2fd70da8...`, debug ELF `33e3b34d...` and package
`85b05c56...` are the same static observer build, with MATCH=0,
MOTORS_ALLOWED=0 and SUMOX_MOTOR_FAULT_PROBE=1. No historical owner was reused.

The raw result has scope D194_STATIC_FILE_ONLY_ENTRY, status OBSERVED and no
first error. All four file children were reaped, returned 0, did not time out
and produced empty stderr. Their stdout lengths are 283, 281, 158668 and
103279 bytes. All eight stream encodings/counts satisfy their bounds. All
13 remote final checks, including identity, and the local final check PASS.
Observed identity remains arduino/UID1000, boot
`55c386b9-fe6d-4388-a7f4-1d91e0bb49d8`, with no conflicting process reported.

Independently reconstructed all four argv from the fixed projections and
matched both intent and actual commands. GDB retains -nx/-nh/-batch, disabled
autoload and may-call-functions off; it queries the existing debug file with
27 fixed disassembly ranges. No target connection or execution command occurs.
All exact function tuples/constructor aliases, Thumb bits, section bounds,
markers, headers, opcode widths, contiguous coverage and raw block hashes
agree with the summary: 27 groups, 945 rows, 2686 bytes. Literal pools sometimes
appear as decoded instructions in GDB; their words were treated as data, so
the row count is not a count of executed instructions.

## Instructions actually inspected

**Entry and initialization.** The current entry copies 208 bytes from
`0x081173b0` into `[0x20013890,0x20013960)` and zeroes 170632 bytes at
`[0x20013960,0x2003d3e8)`. This uses the current source address, not the older
diagnostic's data image. The memcpy/memset stubs tail-jump to the pinned loader;
their loader bodies were not included. Entry also contains three inherited
printk calls before these operations, so this review does not claim absence of
startup logging. Preinit bounds are equal. The actual .init_array bytes
`05011008` decode to the sole Thumb pointer `0x08100105`, the current
`_GLOBAL__sub_I_setup`. Entry iterates that array then hands off to main.

The global initializer directly initializes native source/default fields,
obtains the real motor, ADC, source and dump ports, and calls Runner's constructor
at `0x08103985` with this=`0x20013960`. The source context is `0x2003d090`, motor
context `0x2003d068`, and initialized dump storage `0x20013890`. The inspected
port factories assemble current context/function pointers without invoking
the hardware callbacks. The motor factory additionally computes its candidate
periods and invalidates all periods if any is invalid. Its inspected rate/period
helpers enforce the channel/prescaler/divisibility constraints and a 1..65536
period at 10000 Hz. The unsigned-divide stub targets the pinned loader.
Referenced configuration-table contents were not separately dumped; physical
PWM routing/rate is not established by these instructions.

Trace construction copies the 44-byte native motor port, clears the call
storage and initializes its report/context fields. Trace.port copies that
port and substitutes each non-null callback with its matching trace thunk,
preserving period data. Runner construction calls this Trace constructor and
factory, then calls Runtime's constructor at `0x08100511` on Runner+2184 with
the same ADC/source/dump ports. It initializes report state including polls at
offset 168572 and the one-attempt flag at 169728. The current RuntimeReport
constructor call is also identified. Runtime/RuntimeReport constructor bodies
were not selected: their internals are supported by the bound source and
inherited reviews, not newly disassembled here.

**Setup and polling.** main calls initVariant, start_static_threads and setup,
then loop/loopHook repeatedly. initVariant and loopHook return immediately.
The sketch static-thread list has equal bounds, so this initializer creates no
sketch static threads; this says nothing about the underlying RTOS threads.
setup supplies the single true exclusive diagnostic grant to Runner.begin.
That grant is distinct from application peripheral grants or motor permission.
Runner.begin checks/sets its one-attempt flag, establishes SETUP trace context,
zeroes all 21 bytes of SetupGrants and calls Runtime.begin. Thus the call uses
empty application grants. Missing exclusive permission selects DISABLED;
setup failure freezes as SETUP_FAILED. The successful path evaluates stopReason
before reporting RUNNING. Runtime.begin's body was not among the queried ranges.

loop and Runner.poll both check RUNNING. poll increments the stored poll count
before establishing APPLY context for the next epoch and making one call to
Runtime.step. It stores the returned boolean, evaluates stopReason and freezes
if needed. Terminal calls return before these effects. These bounds govern
returning polls; they do not prove preemption of a blocking callback or WCET.

**Stop priority and feedback.** applicationValid accepts the no-decision case;
otherwise it requires consumed/applied-valid feedback, an equal 64-bit decision
token, motors disabled and both applied duties equal to zero. The actual
stopReason branches are, in order: callback failure, trace timing fault,
invalid application feedback, Runtime STOPPED/FAULT, epoch limit, poll limit.
The epoch comparison is unsigned greater-than 9999 (10000 or more); the poll
literal is `0x00989680` (10000000), compared unsigned greater-or-equal. No
trace-full stop precedes these checks. Reading trace flags is visible, but the
trace callback/report helper internals are outside these 27 ranges.

**Snapshot, halt and passivity.** freeze first rejects a non-RUNNING phase,
sets FINALIZING/reason, then copies the pre-abort RuntimeReport (600 bytes),
TransactionReport fields (497 bytes) and PreviousTick fields (44 bytes). Current
ABI02 ptype confirms TransactionReport is 504 bytes with seven trailing padding
bytes, and PreviousTick is 48 bytes with four trailing padding bytes. The
copies preserve all declared fields; they are not full-object padding copies.
Only after copying does freeze set before_abort_valid, establish HALT context,
set abort_called and call Runtime.abort at `0x08101331`. After that call returns,
it sets abort_returned and FROZEN. Combined with the poll/loop phase checks and
one-attempt begin flag, the inspected code supports terminal passivity and
snapshot-before-abort ordering. Runtime.abort and lower MotorGate/HAL bodies
were not disassembled; actual pin transitions or successful physical halt do
not follow from observing the call site.

The source comparison used the current bench/app_motor_observe sketch and
its Runner implementation, plus bound app/runtime, transaction and feedback
definitions. All 27 selected ranges were examined, including factories,
constructors, arithmetic/memory stubs and startup helpers; conclusions about
unselected callees remain explicitly limited above. This PASS closes the
requested file and instruction audit only. It establishes no MCU execution,
live report contents, RAM headroom, timing acceptance, physical acceptance,
motor-run authorization or phase gate. Any later upload/capture remains a
separate admitted scope using this exact compiled artifact.
