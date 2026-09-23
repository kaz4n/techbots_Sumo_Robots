# D110 independent test-author preflight

2026-09-24 Asia/Dubai. Bounded review of `P2_vbat_contract_draft.md`, proposed
`P2_vbat_headers/vbat.h` and `vbat_native.h`, actual public `src/hal/power.h`,
existing config, D078/D086/D093 contracts and the voltage-bench design. No power
or new Runner implementation body was read. This reuses a separate D104-D109
author context; it is not fresh whole-repository or cross-model review. Only
this preflight document is authored; no tests, implementation or ledger edited.

## Conclusion and recommended prefreeze clarifications

The draft is substantially testable as written. No public API change, extra
callback, shutdown mechanism, timer or hardware assumption is needed. Recommend
two narrow clarifications before freezing independent expectations:

1. **Use explicit float endpoints for configuration admission.** State reference
   validation as finite and `reference > 2.4F && reference <= 3.6F`, and divider
   as finite and `divider >= 1.0F`. The nominal float value `2.4F` is slightly
   above mathematical2.4. Thus a comparison promoted against the double literal
   2.4 could admit the nominal lower endpoint even though a strict comparison
   against 2.4F rejects it. Recommend rejecting exactly2.4F and accepting the
   next representable float above it, consistent with the high-supply profile's
   intended open lower bound. This is an oracle clarification, not a proposed
   change to the existing native implementation.

2. **Execute publicly reachable missed-release saturation.** With the explicitly
   supported config `period=conversion=1`, equal source start/completion and
   equal S/A/C are valid. After one initial accepted sample, the following four
   accepted reads reach and overflow the diagnostic counter without private
   state or billions of calls:

   | Age at S from preceding accepted start | Local missed_before | Cumulative missed_releases | counter_saturated |
   |---:|---:|---:|---|
   | 2^31-1 | 2,147,483,646 | 2,147,483,646 | false |
   | 2^31-1 | 2,147,483,646 | 4,294,967,292 | false |
   | 4 | 3 | 4,294,967,295 | false |
   | 2 | 1 | 4,294,967,295 | true |

   Every wrapper delta remains below half-range; each accepted C reanchors source
   age to zero. The long deltas cross natural uint32 time wrap without reviving
   an old source. The source interval is0, strictly below the1us conversion bound.
   Recommend authorizing this valid test-only config profile and replacing the
   blanket source-review-only saturation statement with executed missed-release
   saturation plus source review of otherwise impractical counters. This profile
   makes no physical conversion-rate claim and changes no production default.

## Already determinate outcomes for the independent oracle

- Missing callbacks precede invalid config; default-false grant precedes both.
  Null context is permitted for stateless callbacks. One-attempt begin retains
  every field on repeat. The first clock establishes a baseline, since no prior
  wrapper observation exists against which to reject its absolute uint32 value.
- Healthy begin uses exactly S/begin/A/C. A setup result fault precedes bad A;
  unknown status/shutdown gives CONTRACT, otherwise known non-OK gives SETUP
  regardless of ready. OK requires ready and NOT_ATTEMPTED. Valid C is required
  for RUNNING. Known non-OK plus unknown shutdown remains CONTRACT.
- The first healthy poll is due. Every later RUNNING poll observes one S; early
  polls clear only fresh and poll last_valid, increment poll calls/not_due and
  advance internal age, preserving historical read timing/sample/acceptance.
  Equality at P is due. A due poll makes exactly one read, never a catch-up burst.
- Misses are computed once at S from the old committed source: floor(age/P)-1.
  They count at actual invocation even if the result/A/C subsequently fails.
  No invocation after bad S means no new misses. Extra time between S and C does
  not retroactively increase that call's local count.
- The prior source-era accumulator remains live through A and C. A newer valid
  sample cannot rescue old-source age reaching half-range before its C commits.
  On valid C, age becomes C-new_start, including callback and closing work. A
  sufficiently delayed C can make the next poll immediately due and late.
- A is always the immediate post-read observation. Unknown enums or contradictory
  known non-OK/valid results take CONTRACT; known non-OK/invalid takes ADC without
  success-only raw/voltage/source restrictions. Preserve actual shutdown and all
  failure fields. Independent bad chronology still sets clock_fault.
- Successful sample source timestamps satisfy the common S-relative inequalities.
  Zero span is admitted; exact conversion deadline is rejected. Bad successful
  source brackets are SOURCE_ORDER only after accepted A. Raw0/16383 are valid;
  exact float scaling is used without filtering or healthy-voltage clipping.
  Ordinary float equality admits negative zero for raw0; unchanged sample storage
  should preserve that actual value rather than canonicalizing it.
- Accepted A measures read S..A even if semantics/source subsequently reject.
  A bad C does not erase a valid read measurement, but prevents poll measurement
  and publication. Nonclock failures still observe C and measure the failed
  setup/due-poll bracket. Any rejected clock suppresses all remaining callbacks.
- Slots are inaccessible until C commits. Final publication returns true/fresh
  while entering COMPLETE, and later polls clear only fresh. Repeated numeric
  samples are accepted from new bracketed calls. Failed C retains the actual
  attempted sample, sample_seen=true, last_read_accepted=false and prior count.
  A later bad S with no read preserves the preceding historical acceptance flag.
- There is no stop API or wrapper cleanup. COMPLETE and FAULT mean no more
  callbacks, not ADC shutdown. Preserve actual NOT_ATTEMPTED/DISABLED/UNCONFIRMED;
  never manufacture disabled hardware or issue a deliberately failing read.
- Native tests can define counted public Reader begin/read methods and separately
  detect or fail linkage for beginWithButtons/readButtons. Execute the actual new
  binding and actual default sketch's setup plus10000loops, checking constructor,
  factory and destruction passivity. These are binding tests, not ADC evidence.

## Proposed execution boundary after adoption

Freeze the adopted contract/public declarations and independent tests before
first execution. Use isolated normal/ASan/UBSan copies, capacities128/1/0,
configuration boundary/refusal profiles, and the valid1us saturation profile if
adopted. Compare every public Capture member and every published slot throughout
the finite capture; include exact S/A/C and read/source/poll durations, local and
cumulative skips, hidden tentative slots and terminal callback counts. Distinguish
the wrapper's age accumulator from measured operation brackets in test stimuli.

No test may seed Runner private counters, invent power Sample sequence numbers,
equate sampled voltage with a qualified physical battery, or weaken existing
D078/D086/native-pins assertions. No deployment, ADC electrical permission,
0.05V accuracy, native runtime latency, full-app WCET or human gate follows.

Next action: coordinator decides the two narrow clarifications and adopts the
contract/public interface. This preflight does not authorize writing tests or
implementation before that adoption notice.
