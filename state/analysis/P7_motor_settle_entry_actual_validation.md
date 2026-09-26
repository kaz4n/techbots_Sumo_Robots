# D199 actual SETTLE instruction observation

The single fixed file-only attempt at clean reviewed HEAD
`5adbd784f80ba7347b9437811266bd2b6cefd175` completed successfully on26 September2026,
07:00:45.131832â€“07:00:46.704941UTC. Check-only and execute both returned0. One
transport ran exactly four bounded file commands; all returned0, were reaped,
had empty stderr and did not time out. All13 remote closing checks and the
independent local closing check passed. No MCU operation or upload occurred.

| Retained output | Bytes | SHA256 |
|---|---:|---|
| native_entry_static01/result.json | 378557 | 10d8a184598b587ff820cb3342586a61a22106a087788a7be756486e22a824ad |
| native_entry_static01/entry.json | 9919 | 8332f7974cdcb39ec5e65cd262b2c22623bb51412f07fc04ec329d5b0d685485 |
| native_entry_static01/local_result.json | 277 | ec4c45e92b7cdb4e6191293c77777182d7a90f49e1594d3421c61f24bf171fe7 |

The raw result preserves the original readelf and118,292-byte GDB output. The
summary accepts all29 fixed ranges and31 function aliases. At0x081162d8 the
four initializer bytes are05011008, the little-endian pointer0x08100105. The
eight owner files total798,606 logical bytes; no ELF/debug binary was downloaded.
All204 host input pins remain exact after observation. The owner is consumed.

The publication block loads the observed report address0x2003d3e8 from its literal
pool. It stores current fields at offsets0,4,8,9,10,11 before has_current at24.
SUCCESS skips the failure stores. For other reasons, nonzero has_failure at25
prevents replacement; otherwise fields at12,16,20,21,22,23 precede has_failure.
The literal pool is data, despite the disassembler displaying opcode mnemonics
for those words. These instructions do not establish atomic snapshot reads.

The SETTLE block retains the initial guards, existing clock/bank checks, three
update-flag clears and bounded polling sequence. Unsigned comparisons against149
implement the unchanged150-us boundary. The loop retains4096 iterations and
reports last index4095 on exhaustion. Early failures pass zero validity; later
outcomes pass mask7 with the existing sampled elapsed/poll/fresh values. This
is emitted file behavior, not observed execution of any particular branch.

Separate actual review20f54afa is PASS with no open findings; it independently
checks151 admitted local pins and204 frozen host inputs. It also assesses startup, constructors,
inert grants, observer stopping and terminal passivity against the accepted
source and ABI. Its final disposition is recorded separately in
[P7_motor_settle_entry_actual_review.md](../reviews/P7_motor_settle_entry_actual_review.md).

Next prepare and review one new inhibited upload/capture using the current
artifacts and actual ABI. The proposed six windows replace only the final live
PreviousTick window with this28-byte report; nested pre-abort PreviousTick and
final Runtime/Transaction/Gate remain. A decoder must preserve the raw values,
loss fields, original errors and coherence=UNPROVEN. No live report value,
failure cause, repair, production timing, physical acceptance, motor permission
or phase gate follows from this file observation. D195 remains flashed.
