# D117 independent public-oracle preflight

PASS for independently testable software preparation against final draft SHA256
`00a6c36c92c6b9f9eb5fd4b453de1ebe9a9e3a58fc28ab1907ca8328550f11f8`.
Root adoption and executable expectation freeze still precede implementation
execution. This reused author context read the proposal, public native/CSV/
recorder headers, D073/D090 contracts and existing native fixture interfaces;
it did not read native production bodies. No D117 executable tests, production
edits or board actions occurred in this preflight.

The proposed Buffering enum and passive constructors are sufficient. Separate
additive native subprocesses can observe all register accesses, DMB, privilege/
IRQ changes, readiness, clock callbacks and packets through the existing four-byte
Reg substitute and public owner methods. A fresh subprocess gives a new lifetime
owner without mutating production singleton or private state. Existing D090
default-constructor tests and D101 factory definitions/assertions stay unchanged.
Counted public-header substitution can verify the two real sketches explicitly
construct FIFO8 while their disabled/default setup remains passive; no getter,
mode setter or production test hook is necessary.

The final draft resolved these material oracle choices before adoption:

- Invalid mode precedes missing grants on first begin; neither causes native I/O.
  Existing earlier/legacy/live checks retain their prior behavior. New FIFO-only
  guards define CONTEXT, lifetime OWNERSHIP, DEVICE, other ownership facts, then
  REGISTER; pre-init metadata and the old post-init combined gate remain distinct.
- Successful new CR1 writes are exactly 0, TE|FIFOEN, UE|TE|FIFOEN. Each has an
  immediate DMB/readback verification; required additional read-only ownership
  checks may also read CR1. Tests must not confuse that requirement with exactly
  one total CR1 read in the entire operation.
- Missing immediate final TEACK and immediate readback mismatch are REGISTER.
  Immediately queried status() retains the first failed-begin return cause;
  later active/reentry calls follow existing poison behavior.
- After any direct setup mutation, the defined owned cleanup is mandatory once.
  It may accept only the immediately last verified or just attempted CR1 state
  and all required non-mode ownership facts, while omitting TEACK. Loss of those
  facts or an unrecognized CR1 means no cleanup write. A failed cleanup readback
  is an observed unverified result, not permission for retry or another write.
  The private cleanup flag itself need not be exposed or asserted.

Failure injection can occur on observed fixture boundaries after each write/DMB
or before its next readback/guard. Thus each branch has a real external cause:
retained preceding state, accepted just-attempted state, unrecognized CR1, missing
TEACK, changed AUTOCR, context, device, clock, pad or IRQ. Assertions can require
the precise primary result, exact permitted CR1 trace, no TDR/RX/AUTOCR writes,
PRIMASK restoration and future refusal. No private owner state need be seeded.

The independent FIFO fixture will model eight **queued** entries plus a separate
in-flight shifting byte. At nominal 115200 8N1, a byte occupies exactly 3125/36 us;
integer rational accounting avoids cumulative rounding. FIFO-room bit7 depends
on actual queue occupancy; TC becomes true only after the last stop bit has
finished and the queue and shift register are empty. Advancing the external
fixture clock advances serialization independently of native calls. The model
records completed emitted bytes separately from queued/in-flight bytes discarded
on inhibition. This is an explicit software reference model, not a measurement
of the board, setup ACK reliability, scheduling cost or guaranteed minimum rate.

This permits finite, additive checks of full FIFO, partial packets, exact1..64
payload framing, TC-only completion, unchanged8-store/80-us/100-ms boundaries,
wrap, current ready/ownership before stores, cancellation and no foreign repair.
Neither an always-high TXFNF value nor forcing FIFO contents to achieve a selected
rate is an acceptable throughput fixture. The conservative six-effective-store
model remains separate from execution of the actual native owner.

## Corrected unrestricted raw formatter bound

The original166-byte FR bound assumed valid state/mode/line-mask widths. D073
instead requires frameRow to preserve arbitrary raw codes, INT32_MIN, INT16_MIN
and duty -128, without enum/mask repair. A general formatter bound is170 bytes.
Root adopted this stronger bound; the earlier semantic-valid model is historical.

For schema, ordinal, status, t_ms, state, mode, line, opponent, heading, gyro,
acceleration X/Y, duties L/R, voltage, flags and tick maximum respectively, the
17 decimal widths are:

`[1,4,1,10,3,3,3,3,11,6,6,6,4,4,5,3,5]`, sum78.

The following literal row has a20-digit session, ordinal5000, known INVALID2
status and exact25-byte raw payload. It ends with one LF:

```text
FR,18446744073709551615,1,5000,2,4294967295,255,255,255,255,-2147483648,-32768,-32768,-32768,-128,-128,65535,255,65535,ffffffffffffffff000000800080008000808080ffffffffff
```

Length is24 prefix +78 decimal +17 commas +50 raw hex +1 LF =170.
The CSV row alone is146. These are independently derived from the public layout;
the actual formatter has not yet been executed. Its later test must verify this
exact row and all capacity ordinals. ER remains73 under the unrestricted event
layout. This deliberately invalid-raw width fixture is serialization/transport
stress evidence, not a semantically valid Robot attempt or strict-receiver success
claim. The complete actual D116 recording supplies that separate receiver case.

For line length L, split into payload lengths p<=64 and independently calculate
`C_b(L) = sum(ceil((p+15)/b)+1)`, reserving a separate completion observation for
each packet. All lengths include LF and exclude NUL. The six remaining lines
use the declared conservative1151-byte bound.

| Effective stores/call | FR170 | ER73 | Other1151 | Total:5001 FR +4096 ER +6 other |
|---:|---:|---:|---:|---:|
| 8 | 31 | 15 | 198 | 217659 |
| 6 | 41 | 20 | 269 | 288575 |
| 5 | 47 | 23 | 306 | 331091 |

FR partitions64/64/42; ER64/9; each1151-byte line has17 full64-byte chunks plus63.
Total packet count is5001*3 +4096*2 +6*18 =23303. Payload bytes are
5001*170 +4096*73 +6*1151 =1156084. Adding15*23303 packet overhead gives
**1,505,629 wire bytes**. These sums were recomputed with standalone public-data
arithmetic, without loading or executing any production module. Six-store
modeled completion is below300000 calls; five-store modeled completion exceeds
it. Neither establishes the native owner's physical lower throughput bound.

The actual D116 full positive stream is532562 bytes with5001 frames/eight events;
its preserved SHA256 is `420b4657c0a13d813ca66e29d6217c406de4d13befd8f7584b625724e9dfdfef`.
Replaying it through the real selected native owner, independently decoding every
MessagePack packet and then the unchanged strict receiver can verify byte identity.
D116's full lifecycle/source comparison and slow-progress TOTAL case remain
unchanged; the synthetic full-capacity formatter/model exercise is additional.

No remaining material public seam or oracle gap is identified in this final draft.
Target size/ABI/constructors/ownership paths, strong empty __loopHook and loader fit still
require actual compile artifacts; inherited empty initVariant may remain weak.
Physical FIFO/ACK/baud/drain/framing, receiver
attachment, effective service rate, whole-tick WCET and run permission remain
separate from host tests and this preflight.
