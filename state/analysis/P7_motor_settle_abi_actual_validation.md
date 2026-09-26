# D199 actual SETTLE report file layout

The fixed file-only inspection succeeded at clean reviewed HEAD
`23f0aeba788c19607a76ee20e0e43834e163ac77`. Check-only and execute returned zero.
One transport ran four file commands, all returning zero with empty stderr and
no timeout. All thirteen remote closing checks and the independent local closure
passed. It did not upload firmware, reset the board or inspect live MCU memory.

## Retained evidence

- Raw result: 905,572 bytes, SHA256
  `230ef847f74e84d032a87336f74a4817d4cd8317a0ea5abc72c54fdd0d03eb6e`.
- ABI summary: 5,410 bytes, SHA256
  `069ed01bee9fba11159a4d93d156b8ada35ea5c11414b77870d80b6182d59941`.
- Local closure: 275 bytes, SHA256
  `eb68ef2e125445ad94fc5c0dc251c2a411d55120ab1299e205a1674b572576f9`.

These files are under P7_motor_settle_compile_raw/native_abi_static01; the adjacent
invocation receipt records the exact check and execution outcomes. The attempt
started 2026-09-26 06:33:42.852687 UTC and finished 06:33:44.920691 UTC.
The local owner is consumed. Original readelf/GDB bytes remain preserved; the
existing decimal/hex symbol-size normalization operates only on a copy.

## Observed target layout

The separate `_ZN6motors12_GLOBAL__N_119settle_probe_reportE` is one LOCAL OBJECT,
28 bytes at **0x2003d3e8**, alignment four, in section five. Its whole range lies
inside the checked initialized-BSS interval and is disjoint from the Runner.
Runner remains 169,736 bytes at 0x20013960, alignment eight. All 23 type groups
and eleven Runner windows were validated from the new image's own output.

| Type | Member | Offset | Width |
|---|---|---:|---:|
| Sample | elapsed_us | 0 | 4 |
| Sample | poll_index | 4 | 4 |
| Sample | reason | 8 | 1 |
| Sample | fresh_mask | 9 | 1 |
| Sample | valid | 10 | 1 |
| Sample | reserved | 11 | 1 |
| Report | current | 0 | 12 |
| Report | first_failure | 12 | 12 |
| Report | has_current | 24 | 1 |
| Report | has_failure | 25 | 1 |
| Report | reserved | 26 | 2 |

Sample size/alignment is 12/4, Report 28/4 and Reason 1/1. All nine reason values
were observed: NONE0, SUCCESS1, NULL_CONTEXT2, PRECONDITION3, INITIAL_BANK4,
POLL_DEADLINE5, POLL_BANK6, FINAL_DEADLINE7 and POLL_LIMIT8. Validity masks1/2/4
remain pinned-header semantics; no unused-constant debug query or inferred target
answer was used.

The raw symbol table also emits publishSettle as a local function at Thumb
address0x08110d61, size60, and UnoQPort::settle at0x081115bd, size292. No separate
storeSettleSample row was observed in this table. These are file symbol facts,
not yet proof of the emitted store order or first-failure guard. A new entry
binding must use this image's actual complete function ranges.

## Limits and next action

The retained owner contains eight files totaling 1,858,490 logical bytes. They
support reproduction and instruction/capture preparation; no ELF/debug binary
was downloaded. Independent actual review is recorded in
[P7_motor_settle_abi_actual_review.md](../reviews/P7_motor_settle_abi_actual_review.md).

Next inspect the emitted startup and publication instructions using newly bound
ranges. A later, separately checked inhibited capture may read the new report.
This operation provides no current RAM contents, executed publication, runtime
failure reason, repair, live free RAM, stack or WCET measurement. D195 remains
flashed, with its observed SETTLE failure and unconfirmed final halt inhibition.
Physical acceptance, motor-run permission and human phase gates remain open.
