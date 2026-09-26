# D202 expected motor metadata review

Date: 26 September 2026, Asia/Dubai. Separate fresh-context reviewer; local
source, contract, frozen oracle and saved-receipt inspection only. No compiler,
test, subject import or device invocation by this reviewer. Only this review
file is owned and written by the reviewer.

**PASS for the bounded D202 host implementation and evidence. No open material
finding remains.** The historical D197 symbol test remains FAIL, with its exact
three-symbol difference explicitly adjudicated below. No target benefit or
runtime repair is established.

## Scope and source findings

The adopted contract is `state/analysis/P7_motor_expected_metadata_contract.md`,
6222 bytes, SHA256
`2abaae2995e1938e4c7f0dcef2522c9334d9550bd77d9da37727b47a7940a846`,
adopted by D202 at `8eec4cc4`. Current production was first inspected only after
the coordinator notified the independent oracle's final freeze. The predecessor
was independently retrieved from `ff35c83e6d21d299dac14eb6fc5570d173a7772d`.

| Source | Bytes | SHA256 |
|---|---:|---|
| Predecessor `src/hal/motor_port_unoq.cpp` | 19185 | `f1ee755a7bddec38e86545f4c5e5457b3ed5e5f1bdd7f5cf368cc77f91664f5e` |
| D202 implementation, commit `37139e83` | 19906 | `fdbc27d972a59a9c955b67b88072a03df3b90a4629e22fd7833ff5f09e0c8f8b` |

No material source defect found. Independent raw-byte inspection confirms the
3918-byte prefix and 13833-byte suffix remain exact. Only the former
candidateRate/candidatePeriod region changes, from 1434 to 2155 bytes. The
original calculation bytes match after precisely the permitted constexpr
declaration/function-name substitutions and the expectedPeriod call rename.

Each preserved runtime signature selects three automatic constexpr scalars
derived with literal indices 0, 1 and 2, then returns zero for any other index.
No new table, persistent state, guard, constructor, device observation, allocation
or replacement numeric rate/period is introduced. Constant-expression initializers
require constant evaluation; target instruction emission is not established by
that source property.

The original widths, casts, short-circuit ordering, zero checks, APB domain and
selector checks, exact divisibility, HCLK interpretation, 64-bit PSC+1 and
period range 1..65536 remain exact. PRESCALERS/DOMAINS/SELECTORS declarations are
unchanged. Every native call site and direct MMIO expression is in the protected
prefix/suffix. Whole-Port zeroing, live PWM-rate observations, ownership,
readiness, EN LOW, activation checks and unsigned SETTLE timing remain unchanged,
including the strict 150-us/4096-poll limits and the diagnostic publication.
The source diff contains no other production, header, config or locked-test edit.

## Initial oracle and evidence inspection

The oracle author froze before seeing or hashing the new implementation.
Initial freeze `independent_freeze01.json` is 31325 bytes /
`0ff509960451c8e183ed636b5d60242a8175dd5fa7afc7623a8cf68bbbcd246d`;
initial Python oracle is 22081 bytes /
`2b8f66e344319542661239b03abb46a5c48333bb472cd338480728b15fbf206c`.
All 79 independent pins and all 148 initial coordinator pins were independently
rehashed with no mismatch.

The seven-method oracle checks exact scoped source, forced constant evaluation,
21 full native/clock/final-fixture transcripts in four variants, 45 explicit
numeric metadata rows, whole-Port rejection, layout, no allocation/native calls
from metadata queries, independent probe exclusion/storage and inert guards.
The new unlocked shim overrides only isolated fixture metadata after including
the unchanged DT header. Carrier changes are exact recorded temporary config
projections; predecessor/current receive identical inputs. Invalid indices 3 and
UINT32_MAX, isolated invalid timers, both APB buses, endpoint periods and 64-bit
values are covered. Runtime helper queries use volatile input indices in the
same translation unit, without a production test seam.

Saved first-run transcript receipts independently establish all 21 groups of
four equal stdout lengths/hashes, zero exits and empty stderr: 84 executions.
The underlying unchanged scenario fixture rejects trace truncation, compares
ordered native and clock calls plus final fixture state, and validates report
bytes separately. Direct MMIO protection additionally comes from source equality.

## Preserved initial finding and required disposition

- **Initial host validation FAIL, fixture-admission issue:**
  `metadata_first_linux01/commands/0382-matrix-carrier_zero-previous-0-build.json`
  records exit 1, `-Werror=div-by-zero` in the pinned predecessor's
  `candidatePeriod`, line 119. Literal carrier zero triggers the compiler warning
  at `rate / carrier`, despite the immediately preceding carrier-zero return.
  This failed before the new implementation's carrier-zero build; it is not
  evidence of a D202 runtime defect. The other six methods passed; the first 36
  numeric rows completed all four variants. The remaining nine rows were not
  established by that run.

The first outer result is exit 1, 163.507941 seconds, unchanged inputs; unittest
reports seven methods/one failure in 144.178 seconds. Original stdout, stderr,
oracle and freeze must remain preserved. The narrow acceptable fixture repair
is `-Wno-error=div-by-zero` only for the explicit carrier-zero row, identically
in all four variants. Keep the warning visible and saved, retain -Werror for all
other warnings/rows, retain UBSan and every numeric/zero/Port assertion, and
retain exact production and historical-test bytes. The independent oracle
author must own/refreeze that fixture-only change. No production rewrite,
warning suppression or skipped zero case is acceptable.

## Historical symbol finding and explicit adjudication

The unchanged D197 suite `probe_first_linux01` remains **FAIL**: four methods
passed, while its complete probe0 symbol equality failed. All 21 original /
current-probe0 / current-probe1 transcript comparisons, preprocessed SETTLE
body, public exclusion/inert guards and protected-byte checks passed. Its
symbol assertion executes before its diagnostic-symbol assertions, so that
method's later checks were not reached. The separate new oracle's method 05
reached and passed those checks for predecessor/current in both probe modes.

The first D197 failure truncated its 1599-character list diff. A fresh bounded
auxiliary owner, `symbols_audit_linux01`, reran only that unchanged symbol
method with `unittest.TestCase.maxDiff=None`. The exact saved argv changes only
diagnostic display; it preserves comparison, normalization, flags, inputs and
the nonzero verdict. Original first failure remains intact. Full stderr SHA256:
`b38675846e94ae531c181c6398f9054b2ddf7a08e0252a251b874abd786a52cf`.

Independent inspection of the complete diff establishes exactly three removed
defined symbols and no additions:

- `r motors::(anonymous namespace)::DOMAINS`
- `r motors::(anonymous namespace)::SELECTORS`
- `t motors::(anonymous namespace)::candidateRate(unsigned int)`

**Disposition: accepted for the explicit D202 source scope; historical test
verdict remains FAIL.** DOMAINS/SELECTORS declarations remain byte-exact and
their only uses are now constant evaluation. Their standalone readonly objects
are consequently not needed in this observed host object. The internal
candidateRate selector also has no standalone text symbol, consistent with
inlining/elimination. The actual source definition/signature remains present,
and unchanged liveRateValid still makes the live PWM-rate observation and
compares it against that selector. No assumption that live state is constant
is introduced. PRESCALERS remains emitted and the unchanged live timer check
still compares regs->PSC against it; candidatePeriod is also retained.

This is neither a filtered symbol assertion nor a manufactured emitted symbol.
There is no added storage or initializer symbol. Independently reached new
oracle assertions establish probe0 report absence, exactly one 28-byte probe1
zero-BSS report, one text accessor and no dynamic-initializer symbol in each
predecessor/current host object. Complete report-byte/layout assertions and
byte-exact publication code remain independently covered. Actual target
emission, section sizes and ABI remain separate pending observations.

The two selected unchanged locked native methods in `locked_first_linux01`
passed: 38 disabled cases/108417 assertions and 38 host-only-enabled cases/
108603 assertions, totaling **76 cases and 217020 assertions**, no skips.
This does not claim every metadata variation in that historical driver ran.
All first-run, historical, locked and auxiliary result receipts report unchanged
148 coordinator pins. All runs were serial; the reviewer executed none.

## Corrected oracle review

Independent author correction `correction01.json`, 4802 bytes /
`0ba239f9d4183206d5326f3df98e097c4b6a8c6b272acb82b5bff6f48bfdb154`,
records preserved original oracle commit `2b7449b2` and first-failure commit
`4d7b92a9`. Revised Python oracle is 22611 bytes /
`7378ed6a1f13e32a8ac6477c39d115dc34efb2217caf7ec75f0bac25d81a2db1`;
`independent_freeze02.json` is 32996 bytes /
`68a539d9ff61227df87233023d15a66083b96a3c4053295425b02eb4ac06cd87`.
All 84 revised independent pins were independently rehashed and match.

The inspected diff contains only the revised freeze pointer and the approved
carrier-zero warning admission. It additionally requires metadata carrier zero,
exactly one `warning: division by zero [-Wdiv-by-zero]`, no other warning, and
diagnostic length within the retained 8000-byte receipt. No original assertion
is removed. This is an accepted fixture correction; the real config and
production source remain unchanged. It does not establish a warning-free
zero-carrier compilation.

## Completed corrected execution and final verdict

`metadata_corrected_linux02/result.json` records exit 0, no changed inputs,
145.4370766 seconds outer elapsed; unittest reports all seven methods passed,
no skips, in 135.077 seconds. Result SHA256:
`7249f9bf767fb42a54eaf34ebaf712ec7e182c9962e6a088341eb08ff7f98af5`.
Saved stdout is 5632 bytes /
`295e16728374501bcb67e3c5661ee05a74170effe9c8121c7d27aa37d7bd2a5e`;
stderr is 1293 bytes /
`ff8062315b0a5414b457d43678dc7c7cd1667579be4369f95f4a0b04b6a65db6`.
These hashes were independently recomputed against the outer receipt.

Independent receipt inspection confirms 465 commands, with only the four
intended negative interface/inert-guard compilations exiting nonzero. All 45
numeric rows completed four variants: 180 executions, zero exits, empty runtime
stderr and four equal output lengths/hashes in every row. All 21 native
transcript scenarios likewise completed four equal variants: 84 executions.
All four carrier-zero builds exited zero and retain exactly one complete
expected warning each: 477-byte predecessor diagnostics and 484-byte current
diagnostics. Their warnings remain evidence; all runtime zero assertions and
UBSan checks passed. No row or assertion was skipped to obtain the result.

Final independent rehashing confirms all 154 coordinator-freeze02 pins match,
including unchanged production `fdbc27d9`. The saved oracle closing receipt
records stable inputs and its owned scratch cleanup. The successful direct-argv
read-only `scratch_closing03.json` observation reports no matching owned fixture
directories remaining. The earlier shell-interpretation observation error is
preserved separately; it did not change source, tests or execution outcomes.

**Verdict: PASS for D202 source and host validation.** The initial carrier-zero
fixture failure and full historical symbol failure remain preserved, with the
bounded repair and explicit dispositions recorded above. No production change
followed the reviewed implementation. The next allowed work is preparation
and review of a new fixed compile-only scope; this verdict does not authorize
using an old owner or performing a target operation.

## Evidence boundary

D201 separately observed SETUP_FAILED with lifetime first FINAL_DEADLINE at
154 us/poll5/fresh7, then successful setup cleanup at 132 us, with zero epochs.
That localizes a rejection predicate; it does not prove its physical cause or
a timing benefit from D202. D195's earlier application failure remains separate.
Host equality cannot establish target division removal, storage/code-size
changes, timing, WCET, reliability, electrical outputs, physical acceptance or
a human phase gate. A new fixed compile-only workflow, new artifacts and actual
ABI/entry observation must precede any separately reviewed inhibited attempt.
No target compilation, upload or motor run is authorized by this review.
