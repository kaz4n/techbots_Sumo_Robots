# D188 actual entry instruction review

Reviewer /root/app_trace_abi_scope, separate read-only reused same-model context.
PASS, no material finding. Coordinator transcribed actual review; no gate verdict.
All4children/12filepins+identity/localclosure PASS,1transport,27ranges2654B.
No target connection, MCUread, compiler/upload/reset or firmware execution.

Entry0x08100010 implements208B memcpy from0x08117390 to0x20013890 and170632B
BSS clear through0x2003d3e8 before sole initializer. The inherited three early
printk calls through0x080173d5 remain. Actual initword05011008 points to
_GLOBAL__sub_I_setup0x08100105. Empty preinit/staticthread spans and main's
initVariant/setup/loop handoff match source; this does not imply no RTOS threads.
memcpy/memset/divide trampolines bind unchanged loader targets0x0801b2d3,
0x0801b31f,0x08001365 respectively; full loader semantics are inherited facts.

Global initializer defaults sources0x2003d090, takes motor0x2003d068 and
FIFO8dump0x20013890 factories, constructs Runner0x20013960. Trace copies44B
nativePort. Its wrapper preserves periods, replaces six non-null callbacks
and context with ownTrace. Runtime receives wrapper atRunner+2184. Factories
store callbacks without invoking them. Setup passes diagnostic admission1;
Runner zeroes21B SetupGrants, begins Runtime once. Loop/poll guardRUNNING,
call one step, and preserve source stop priority: firstcallbackfailure,
traceinvalid, invalidapplication, runtime terminal, fourcompletedepochs.

Freeze copies RuntimeReport600B, TransactionReport497meaningfulB and
PreviousTick44meaningfulB; trailing7/4ABI padding is not copied. Decode fields
rather than requiring pre/post whole-object byte equality. before_abort validity
follows copies; HALT context/Runtimeabort precede abort_returned/FROZEN.

No concrete unknown unsafe initializer or hardware/API effect was found.
Unchanged Runtime/Transaction/MotorGate cpp+headers, NativeSources cpp+header
and motor_port.cpp hash-match constructor-audited D139 source. New compiler-
emitted RuntimeReport default constructor0x08103868..0x08103984 is a value-only
struct in unchanged runtime.h (b2524602...), passed before_abort.runtime at
Runner+168576. These are source-backed constructor interpretations, not newly
claimed instruction audits of every callee. No recursive query is required
before the scoped inhibited experiment; full runtime qualification stays open.

Receipt hashes are retained in native_entry_static01_invocation.json.
